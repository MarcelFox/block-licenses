from setuptools import setup, find_packages

setup(
    name='block-license',
    version='0.0.1',
    description='CLI tool to check and block licenses based on \
        packages installed and listed on the Requirements file.',
    url='https://github.com/marcelfox/require-foss',
    author='Marcel Fox',
    author_email='marcelfox@live.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains *.ini files, include them
        '': ['*.ini'],
    },
    install_requires=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'require-foss = app.main:cli',
        ],
    },
)
