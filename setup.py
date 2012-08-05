#!/usr/bin/env python

from distutils.core import setup
import pyfpm

setup(name='pyfpm',
      version=pyfpm.__version__,
      description='Scala-like functional pattern matching in Python.',
      author=pyfpm.__author__,
      url='https://github.com/martinblech/pyfpm',
      packages=['pyfpm'],
      requires=['pyparsing'],
     )
