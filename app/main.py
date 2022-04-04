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
@click.option('-q', '--quiet', is_flag=True, default=False, type=bool, help='Do not print any output.')
@click.option('-v', '--verbose', is_flag=True, default=False, type=bool,
              help='Print a detailed output for blocked packages.')
@click.option('-r', 'requirements', default="requirements.txt", type=str,
              help='Indicate the requirements file to be used.')
@click.option('-A', '--all', 'all_requirements', is_flag=True, default=False, type=str,
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
def cli(ctx, check, blocked, permitted, quiet, verbose, requirements, all_requirements, mode, format_to):
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

    found_blocked = len(packages.check_blocked_licenses(verbose=verbose)) > 0
    if not quiet and found_blocked:
        click.echo('Found Blocked:')
        format_output(content_list=packages.check_blocked_licenses(verbose=verbose), verbose=verbose, format_to=format_to)
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
