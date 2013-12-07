# -*- coding: utf-8 -*-
import sys
from setuptools import setup

dependency_links = []
tests_require = []

if sys.version_info >= (3, 0):
    dependency_links.append('hg+https://bitbucket.org/prologic/pydot#egg=pydot')

if sys.version_info < (2, 7):
    tests_require.append('unittest2')

setup(
    name='astmonkey',
    version='0.1.1',
    description='astmonkey is a set of tools to play with Python AST.',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    url='https://github.com/konradhalas/astmonkey',
    packages=['astmonkey'],
    test_suite='astmonkey.tests',
    install_requires=['pydot'],
    dependency_links=dependency_links,
    tests_require=tests_require,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: Apache Software License'
    ]
)

