# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='astmonkey',
    version='0.2.0',
    description='astmonkey is a set of tools to play with Python AST.',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    url='https://github.com/mutpy/astmonkey',
    packages=['astmonkey'],
    install_requires=['pydot'],
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

