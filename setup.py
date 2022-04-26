from setuptools import setup, find_packages

setup(
    name='block-licenses',
    version='0.0.3',
    description='CLI tool that helps us easily define which licenses are not good based on the requirements.txt file. \
        It uses pkg_resources to get details from the packages, given us the licenses listed byt the package owner and \
        returns exit 1 if found a package that contains a blocked license.',
    url='https://github.com/MarcelFox/block-licenses',
    author='Marcel Fox',
    author_email='marcelfox@live.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.ini and *.xml files, include them
        '': ['*.ini'],
        'licenses': ['core/license-list-XML/src/*.xml']
    },
    install_requires=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'block-licenses = app.main:cli',
        ],
    },
)
