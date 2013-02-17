# -*- coding: utf-8 -*-
import sys
from setuptools import setup


setup(
    name='astmonkey',
    author='Konrad Hałas',
    author_email='halas.konrad@gmail.com',
    url='https://bitbucket.org/khalas/astmonkey',
    packages=['astmonkey'],
    test_suite='astmonkey.tests',
    install_requires=['pydot'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License'
    ]
)

