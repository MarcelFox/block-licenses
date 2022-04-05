import os
import sys
import click
import json
import subprocess
from itertools import chain, compress
from pkg_resources import get_distribution, DistributionNotFound
from app.core.package_class import PackageList

from os.path import exists
from configparser import ConfigParser
from typing import Tuple, Dict, List, Optional, Union

config = ConfigParser()
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--check', is_flag=True, type=bool, help='Check licenses from the requirements.txt file.')
@click.option('-b', '--blocked', is_flag=True, default=False, type=bool, help='Print blocked list.')
@click.option('-p', '--permitted', is_flag=True, default=False, type=bool, help='Print permitted list.')
@click.option('-i', '--interactive', is_flag=True, default=False, type=bool,
              help='Block packages interactively by analysing their licenses.')
@click.option('-q', '--quiet', is_flag=True, default=False, type=bool, help='Do not print any output.')
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool,
              help='Print a detailed output for blocked packages.')
@click.option('-r', 'requirements', default="requirements.txt", type=str,
              help='Indicate the requirements file to be used.')
@click.option('-a', '--all', 'all_requirements', is_flag=True, default=False, type=str,
              help='Print all available licenses based on the requirements file.')
@click.option(
    '--mode', type=click.Choice(['permitted', 'blocked'],
                                case_sensitive=False), default='blocked',
    help='Mode which will be used to check packages, either from the permitted list or blocked list perspective.')
@click.option(
    '--format', 'format_to', type=click.Choice(['text', 'json', 'column'],
                                               case_sensitive=False), default='json',
    help='Format output.')
@click.pass_context
def cli(ctx, check, blocked, permitted, interactive, quiet, verbose, requirements, all_requirements, mode, format_to):
    """
    Tool that checks if all licenses from a project requirements are complient with FOSS.
    """
    packages = PackageList(requirements=requirements)

    if all_requirements:
        format_output(content_list=packages.detailed_list, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if permitted:
        format_output(content_list=packages.permitted_licenses, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if blocked:
        format_output(content_list=packages.blocked_licenses, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if interactive:
        build_interactively(packages.detailed_list)
        sys.exit(0)

    blocked_licenses = packages.check_blocked_licenses(verbose=verbose, mode=mode)
    if len(blocked_licenses) > 0:
        if not quiet:
            click.echo(f"Found Blocked on '{mode}' mode:")
            format_output(blocked_licenses, verbose=verbose, format_to=format_to)
            sys.exit(1)
        sys.exit(1)


def format_output(content_list: List, verbose: bool = False, format_to: str = 'json'):
    has_package_details = type(content_list[0]) == dict

    if format_to == 'json':
        click.echo(json.dumps(content_list, indent=2))

    if format_to == 'text':
        for item in content_list:
            if has_package_details:
                if verbose:
                    click.echo(f'{item.get("package")} - {item.get("licenses")}')
                else:
                    click.echo(f'{item.get("package")}')
            else:
                click.echo(f' - {item}' if verbose else f'{item}')

    if format_to == 'column':
        for item in content_list:
            if has_package_details:
                if verbose:
                    click.echo(f'| {item.get("package")} | {item.get("licenses")} |')
                else:
                    click.echo(f'| {item.get("package")} |')
            else:
                click.echo(f' - {item}' if verbose else f'{item}')


def build_interactively(detailed_list):
    build_list = list()
    for index, package in enumerate(detailed_list):
        click.echo(json.dumps(package, indent=2))
        if click.confirm(
                f"The '{package.get('package')}' package should be blocked? ({index + 1}/{len(detailed_list)})"):
            build_list.append(package)
        if click.confirm(f"  Remove packages on the list that have '{package['licenses'][0]}'?"):
            detailed_list = sanatize_licenses(detailed_list, package['licenses'])

    if len(build_list) > 0:
        permitted_list = [item for item in detailed_list if item not in build_list]
        with open('licenses.ini', 'w') as file:
            file.write('[licenses]\npermitted:\n')
            write_lines_to_file(file, permitted_list)
            
            file.write('\nblocked:\n')
            write_lines_to_file(file, build_list)


def write_lines_to_file(file, content_list):
    for package in content_list:
        for index, value in enumerate(package['licenses']):
            if index == 0:
                file.write(f"    {value}")
            else:
                file.write(f" {value}")
        file.write(f"\n")

def sanatize_licenses(detailed_list, license_name):
    for index, package in enumerate(detailed_list):
        if license_name[0] in package['licenses']:
            del detailed_list[index]
    return detailed_list
