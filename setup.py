#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

setup(
    name='python-cas-gateway',
    version=open('VERSION').read().strip(),
    author='Adam Charnock',
    author_email='adam@adamcharnock.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/adamcharnock/python-cas-gateway',
    license='MIT',
    description='Asyncio cas gateway/proxy',
    long_description=open('README.rst').read() if exists("README.rst") else "",
    install_requires=[
        'aiohttp>=3,<3.2',
        'aiohttp-cas>=0.1,<1',
        'aioredis>=1.0.0<2',
        'aiohttp-remotes==0.0.5',
        'boto3>=1.7.66,<1.8',
        'async-timeout<3',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cas_gateway=python_cas_gateway.gateway:main',
        ]
    }
)
