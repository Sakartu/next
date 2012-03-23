#!/usr/bin/env python

from setuptools import setup
import os

packages = ['next', 'next.db', 'next.show', 'next.tui', 'next.tvr', 'next.util']

setup(name = 'next',
      version = '1.1',
      description = "tool to remember which tv serie season and ep you're at and play the next one for you",
      author = 'Peter Wagenaar',
      author_email = 'sakartu@gmail.com',
      url = 'https://github.com/Sakartu/next',
      packages = packages,
      keywords = ['show', 'season', 'ep', 'next',],
      entry_points = '''
      [console_scripts]
      next = next.next:main
      ''',
      install_requires = [
          'python-tvrage',
          'pyxdg',
          ],
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
     )
