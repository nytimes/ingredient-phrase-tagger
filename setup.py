#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import ingredient_phrase_tagger


requires, extra = ['Unidecode==0.04.14', 'pandas==0.17.1'], {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='ingredient_phrase_tagger',
    version='0.0.0.dev0',
    description='Extract structured data from ingredient phrases using conditional random fields',
    author='The New York Times Company',
    author_email='',
    license='Apache 2.0',
    install_requires=requires,
    packages=find_packages(),
    package_dir={'ingredient_phrase_tagger': 'ingredient_phrase_tagger'},
    **extra
)
