#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from setuptools import setup, find_packages

try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except IOError:
    long_description = ''


def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name="asva",
    version="0.3.1",
    url='https://github.com/adc21/asva',
    author='adc21',
    author_email='aseismic.device@gmail.com',
    maintainer='adc21',
    maintainer_email='aseismic.device@gmail.com',
    description='Vibration analysis program for multi degree of freedom model',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
