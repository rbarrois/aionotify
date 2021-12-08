#!/usr/bin/env python
# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

import codecs
import os
import re
import sys

from setuptools import setup

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    init_path = os.path.join(root_dir, *(package_components + ['__init__.py']))
    with codecs.open(init_path, 'r', 'utf-8') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'


PACKAGE = 'aionotify'


setup(
    name=PACKAGE,
    version=get_version(PACKAGE),
    description="Asyncio-powered inotify library",
    author="Raphaël Barrois",
    author_email="raphael.barrois+%s@polytechnique.org" % PACKAGE,
    url='https://github.com/rbarrois/%s' % PACKAGE,
    keywords=['asyncio', 'inotify'],
    packages=[PACKAGE],
    license='BSD',
    setup_requires=[
    ],
    tests_require=[
        'asynctest; python_version<"3.8"',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
    ],
    test_suite='tests',
)
