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
@click.option('-P', '--paranoid', is_flag=True, default=False, type=bool,
              help='Paranoid mode for the interactive option, loop through each package even if a contains \
              a license that was already checked.')
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
def cli(ctx, check, blocked, permitted, interactive, quiet, 
        verbose, paranoid, requirements, all_requirements, mode, format_to):
    """
    Tool that checks if all licenses from a project requirements are complient with FOSS.
    """
    packages = PackageList(requirements=requirements)

    if all_requirements:
        # Print all packages found on requirements:
        format_output(content_list=packages.detailed_list, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if permitted:
        # Print Permitted list:
        format_output(content_list=packages.permitted_licenses, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if blocked:
        # Print Blocked list:
        format_output(content_list=packages.blocked_licenses, verbose=verbose, format_to=format_to)
        return sys.exit(0)

    if interactive:
        # Prompt interactively to build a licenses.ini:
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
    """
    Helper function to print the output of the content list as 'json', 'text' or 'column'.

    Args:
        content_list(list): Content list to be formatted and printed.
        verbose(bool): Either to print more detailed info or not.
        format_to(str): DEFAULT 'json' - format option to be printed.
    """
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
    """
    Function to build a licenses.ini file interactively.

    Args:
        detailed_list(list): List of the detailed packages generated by PackageList instance.
    """
    blocked_licenses = list()
    permitted_licenses = list()

    for index, package in enumerate(detailed_list):
        # PROMPT LICENSES:
        if len(package['licenses']) > 0:

            previous_package = None
            for license_name in package['licenses']:

                # Avoid List helps not repeat the same license:
                avoid_list = blocked_licenses + permitted_licenses + ['UNKNOW', '']
                if license_name.lower() not in avoid_list:
                    if previous_package != package:
                        click.echo('PACKAGE DETAILS:')
                        click.echo(json.dumps(package, indent=2))
                    if click.confirm(
                            f"Should the license '{license_name.upper()}' be blocked? ({index + 1}/{len(detailed_list)})"):
                        blocked_licenses.append(license_name.lower())
                    else:
                        permitted_licenses.append(license_name.lower())
                    previous_package = package
                
                if not paranoid:
                    sanitize_licenses(detailed_list, license_name)

    with open('licenses.ini', 'w') as file:
        file.write('[licenses]\npermitted:\n')
        write_lines_to_file(file, permitted_licenses)

        file.write('\nblocked:\n')
        write_lines_to_file(file, blocked_licenses)


def write_lines_to_file(file, content_list):
    """
    Helper function that will write lines to the given file.

    Args:
        file(IO Stream): File to be used.
        content_list(list): List of contents to be written in the file.
    """
    for index, license_name in enumerate(content_list):
        file.write(f"    {license_name}\n")


def sanitize_licenses(detailed_list, license_name) -> list:
    """
    This will remove any packages that contains a license that was already verified.

    Args:
        detailed_list(list): List of the detailed packages generated by PackageList instance.
        license_name(str): Name of the license to be checked.
    
    Returns:
        Sanitized detailed_list.
    """
    for package in detailed_list:
        if(len(package['licenses']) > 0):
            package['licenses'] = [value for value in package['licenses'] if value != license_name]
    return detailed_list
