"""Module stores PackageList Class."""

import os
import sys
import click
from os.path import exists
from itertools import chain, compress
from configparser import ConfigParser
from pkg_resources import get_distribution, DistributionNotFound
from typing import Tuple, Dict, List, Optional, Union


class PackageList:
    def __init__(self, requirements: str = "requirements.txt"):
        # Getting the configuration file to check for licenses:
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), '../config/default.ini')
        config.read(config_path)
        if exists("licenses.ini"):
            config.read('./licenses.ini')

        self.permitted_licenses = [value for value in config.get(
                'licenses', 'permitted').split('\n') if value]
        self.blocked_licenses = [value for value in config.get(
                'licenses', 'blocked').split('\n') if value]
        self.requirements = requirements
        self.detailed_list = self.get_package_list_from_requirements()

    def get_package_list_from_requirements(self) -> List:
        packages_list = list()
        with open(file=self.requirements) as file:
            for line in file:
                package = line.split('==')[0]
                if package[0] != "-":
                    packages_list.append(package)

        package_details = list()
        for package in packages_list:
            package_details.append(self.get_licenses_from_package(package))
        return package_details

    def get_licenses_from_package(self, pkg_name: str):
        try:
            distribution = get_distribution(pkg_name)
        except DistributionNotFound:
            click.echo(f"Package '{pkg_name}' not found.\n \
                Have you installed all packages from the '{self.requirements}' file?")
            sys.exit(1)

        try:
            lines = distribution.get_metadata_lines('METADATA')
        except OSError:
            lines = distribution.get_metadata_lines('PKG-INFO')

        return {'package': distribution.project_name, "version": distribution.version,
                'licenses': list(chain.from_iterable(map(self.__filters, lines)))}

    def check_blocked_licenses(self, verbose: bool = False, mode: str = 'blocked') -> List:
        blocked_list = list()
        for index, package in enumerate(self.detailed_list):
            package_licenses = package.get('licenses')
            for license_name in package_licenses:
                if not license_name or license_name == 'UNKNOWN':
                    break
                if mode == 'permitted':
                    if license_name.lower() not in self.permitted_licenses:
                        blocked_list.append(self.detailed_list[index])
                        break
                else:
                    if license_name.lower() in self.blocked_licenses:
                        blocked_list.append(self.detailed_list[index])
                        break
        return blocked_list

    @staticmethod
    def __filters(line):
        return compress(
                (line[9:], line[39:]),
                (line.startswith('License:'), line.startswith('Classifier: License')),
        )
