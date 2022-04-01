from setuptools import setup, find_packages

setup(
    name='require-foss',
    version='0.1.2',
    description='Tool that checks if all licenses from a project requirements are complient with FOSS.',
    url='https://github.com/marcelfox/require-foss',
    author='Marcel Fox',
    author_email='marcelfox@live.com',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click'
    ],
    entry_points={
        'console_scripts': [
            'require-foss = app.main:cli',
        ],
    },
)
