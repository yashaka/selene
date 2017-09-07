#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from selene import version

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = [
    'selenium',
    'webdriver_manager',
    'future',
    'backports.functools_lru_cache',
    'six'
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='selene',
    version=version.VERSION,
    description='Concise API for selenium in Python + Ajax support + PageObjects (Selenide port from Java to Python)',
    long_description=readme + '\n\n' + history,
    author='Iakiv Kramarenko',
    author_email='yashaka@gmail.com',
    url='http://github.com/yashaka/selene/',
    packages=find_packages(include=[
        'selene',
        'selene.api',
        'selene.abctypes',
        'selene.common',
        'selene.support',
        'selene.support.conditions'
    ]),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=['testing', 'selenium', 'selenide', 'browser', 'pageobject', 'widget', 'wrapper'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Software Development :: Testing'
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
