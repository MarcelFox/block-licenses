import os
import sys
import click
import json
import subprocess
from itertools import chain, compress
from pkg_resources import get_distribution

from os.path import exists
from configparser import ConfigParser
from typing import Tuple, Dict, List, Optional, Union

config = ConfigParser()
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--check', is_flag=True, type=bool, help='Check licenses from the requirements.txt file.')
@click.option('-b', '--blocked', is_flag=True, default=False, type=bool, help='Print blocked list.')
@click.option('-p', '--permitted', is_flag=True, default=False, type=bool, help='Print permitted list.')
@click.option('-q', '--quiet', is_flag=True, default=False, type=bool, help='Do not print any output.')
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool, help='Print a detailed output for blocked packages.')
@click.option('-r', 'requirements', default="requirements.txt", type=str, help='Indicate the requirements file to be used.')
@click.option('-A', '--all', 'all_requirements', is_flag=True, default=False, type=str, help='Print all available licenses based on the requirements file.')
@click.pass_context
def cli(ctx, check, blocked, permitted, quiet, verbose, requirements, all_requirements):
    """
    Tool that checks if all licenses from a project requirements are complient with FOSS.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/default.ini')
    config.read(config_path)
    if exists("licenses.ini"):
        config.read('./licenses.ini')

    permitted_licenses_list = [value for value in config.get('licenses', 'permitted').split('\n') if value]
    blocked_licenses_list = [value for value in config.get('licenses', 'blocked').split('\n') if value]

    if blocked:
        click.echo('Blocked List:')
        for i in blocked_licenses_list:
            click.echo(f' - {i}')
        sys.exit(0)
    
    if permitted:
        click.echo('Permitted List:')
        for i in permitted_licenses_list:
            click.echo(f' - {i}')
        sys.exit(0)

    package_details = get_package_list_from_requirements(requirements)
    if all_requirements:
        print(json.dumps(package_details, indent=2))
        sys.exit(0)
    blocked_list = check_blocked_licenses(package_details, blocked_licenses_list, verbose)

    print()


    if len(blocked_list) > 0:
        if not quiet:
            click.echo('Found blocked packages:')
            click.echo(json.dumps(blocked_list, indent=2))
        sys.exit(1)


def filters(line):
    return compress(
        (line[9:], line[39:]),
        (line.startswith('License:'), line.startswith('Classifier: License')),
    )


def get_licenses_from_package(pkg_name: str):
    distribution = get_distribution(pkg_name)
    try:
        lines = distribution.get_metadata_lines('METADATA')
    except OSError:
        lines = distribution.get_metadata_lines('PKG-INFO')
    return list(chain.from_iterable(map(filters, lines)))


def check_blocked_licenses(packages_details_list, blocked_licenses_list, verbose: bool=False) -> List:
    blocked_list = list()
    for index, package in enumerate(packages_details_list):
        licenses_list = package.get('licenses')
        for license_name in licenses_list:
            if license_name.lower() in blocked_licenses_list:
                if verbose:
                    blocked_list.append(packages_details_list[index])
                else:
                    blocked_list.append(packages_details_list[index].pop('package'))
    return blocked_list


def get_package_list_from_requirements(requirements: str = "requirements.txt") -> List:
    if not exists(requirements):
        click.echo(f"Did not found a '{requirements}' file.")
        sys.exit(1)

    packages_list = list()
    with open(file=requirements) as file:
        for line in file:
            package = line.split('==')[0]
            if package[0] != "-":
                packages_list.append(package)

    package_details = list()
    for package in packages_list:
        package_details.append({'package': package, 'licenses': get_licenses_from_package(package)})
    return package_details
