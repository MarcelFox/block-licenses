import click
import json
import subprocess
from os.path import exists
from configparser import ConfigParser
from app.core.custom_exceptions import BlockedLicenses

config = ConfigParser()

@click.command()
@click.option('-c', '--check', is_flag=True, type=bool, help='Check licenses from the requirements.txt file.')
@click.option('-b', '--blocked', is_flag=True, default=False, type=bool, help='Print blocked list.')
@click.option('-p', '--permitted', is_flag=True, default=False, type=bool, help='Print permitted list.')
@click.pass_context
def cli(ctx, check, blocked, permitted):
    """
    Main command related to the license scope.
    """
    config.read('./default.ini')
    if exists("licenses.ini"):
        config.read('./licenses.ini')

    permitted_licenses_list = [value for value in config.get('licenses', 'permitted').split('\n') if value]    
    blocked_licenses_list = [value for value in config.get('licenses', 'blocked').split('\n') if value]

    if blocked:
        click.echo('Blocked List:')
        for i in blocked_licenses_list:
            click.echo(f' - {i}')
        
    
    if permitted:
        click.echo('Permitted List:')
        for i in permitted_licenses_list:
            click.echo(f' - {i}')


    packages_details_list = json.loads(subprocess.check_output(["pip-licenses", "-f", "json"]))

    blocked_list = list()
    for package in packages_details_list:
        if str(package.get('License')).lower() in blocked_licenses_list:
            blocked_list.append(package)
    
    if len(blocked_list) > 0:
        click.echo('blocked packages')
        click.echo(json.dumps(blocked_list, indent=2))
        raise BlockedLicenses
