#!/usr/bin/env python

from distutils.core import setup
import pyfpm

setup(name='pyfpm',
        version=pyfpm.__version__,
        author=pyfpm.__author__,
        author_email='martinblech@gmail.com',
        url='https://github.com/martinblech/pyfpm',
        description='Scala-like functional pattern matching in Python.',
        long_description="""`pyfpm` stands for PYthon Functional Pattern
        Matching. It's been heavily inspired by the Pattern Matching and Case
        Classes implementation in Scala.""",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development :: Libraries',
            ],
        packages=['pyfpm'],
        requires=['pyparsing'],
        )
