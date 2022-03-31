"""Module that stores custom exceptions."""

class BlockedLicenses(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return ("Found blocked licenses.")