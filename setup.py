#!/usr/bin/env python
# -*- coding: utf-8 -*-

r'''
このpythonパッケージのsetup.pyです。
詳しくは以下を参照してください。

http://www.python.jp/doc/2.7/dist/dist.html

Copyright O. Sugiyama 2019. All rights reserved.
'''


__author__ = "Osamu Sugiyama"
__author_email__ = "sugiyama.o@gmail.com"
__date__ = "2019/7/20"
__version__ = "0.0.2"

import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

setup(
    name='fxtrade',
    version='0.0.1',
    description='python components to handle FX trade',
    author=__author__,
    author_email=__author_email__,
    url='',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    long_description=read('readme.md'),
    include_package_data=True,
    install_requires=[
        'setuptools',
        'google',
        'python_box',
    ],
    scripts=[],
    zip_safe=False
)
