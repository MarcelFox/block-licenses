"""Module stores PackageList Class."""

import os
import sys
from configparser import ConfigParser
from itertools import chain, compress
from os.path import exists
from typing import List

import click
from pkg_resources import DistributionNotFound, get_distribution


class PackageList:
    """Package List Class."""

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
        """Returns a detailed package list based on the packages on requirements.txt.

        Returns:
            List: Detailed packages list.
        """
        packages_list = []
        with open(file=self.requirements, encoding='UTF-8') as file:
            for line in file:
                package = line.split('==')[0]
                if package[0] != "-":
                    packages_list.append(package)

        package_details = []
        for package in packages_list:
            package_details.append(self.get_licenses_from_package(package))
        return package_details

    def get_licenses_from_package(self, pkg_name: str):
        """Retrieve a dict of packages.

        Args:
            pkg_name (str): Name of the package.

        Returns:
            dict: List of packages.
        """
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
        """Returns a list with possible blocked packages.

        Args:
            verbose (bool, optional): Verbose output. Defaults to False.
            mode (str, optional): Block mode. Defaults to 'blocked'.

        Returns:
            List: List containing blocked packages.
        """
        blocked_list = []
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
