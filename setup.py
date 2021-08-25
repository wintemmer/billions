#!/user/bin/env python
# coding: utf-8

from setuptools import _install_setup_requires, setup, find_packages

setup(
    name='Shouzheng_billions',
    version = '0.1.8',
    author='Shouzheng-Hu',
    author_email='obobob32@gmail.com',
    url='https://github.com/wintemmer/billions',
    packages=find_packages(),
    setup_requires=['pandas', 'numpy', 'tqdm', 'plotly']
)
