#!/usr/bin/env python

import os
import sys

import skosprovider

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'skosprovider',
]

requires = [
    'language-tags',
    'rfc3987',
    'pyld',
    'html5lib'
]

setup(
    name='skosprovider',
    version='0.8.0',
    description='Abstraction layer for SKOS vocabularies.',
    long_description=open('README.rst').read(),
    author='Koen Van Daele',
    author_email='koen_van_daele@telenet.be',
    url='http://github.com/koenedaele/skosprovider',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'skosprovider': 'skosprovider'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='nose.collector'
)
