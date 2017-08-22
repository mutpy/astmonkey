# -*- coding: utf-8 -*-
from setuptools import setup

import astmonkey

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='astmonkey',
    version=astmonkey.__version__,
    description='astmonkey is a set of tools to play with Python AST.',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    url='https://github.com/mutpy/astmonkey',
    packages=['astmonkey'],
    install_requires=['pydot'],
    long_description=long_description,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License'
    ]
)
