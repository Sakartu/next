#!/usr/bin/env python

from setuptools import setup

packages = ['next', 'next.db', 'next.show', 'next.tui', 'next.tvr', 'next.util']

setup(name='next',
      version='1.1.1',
      description="tool to remember which tv serie season and ep you're at and play the next one for you",
      author='Peter Wagenaar',
      author_email='sakartu@gmail.com',
      url='https://github.com/Sakartu/next',
      packages=packages,
      scripts=['next.py'],
      install_requires=[
          'python-tvrage',
          'pyxdg',
          ],
     )
