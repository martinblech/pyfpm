#!/usr/bin/env python
"""
Loose port of the examples at `A Tour of Scala: Pattern Matching <http://www.scala-lang.org/node/120>`_
"""
from __future__ import print_function

from pyfpm import Matcher as M

print('-'*80)
matchTest = M([
        ('1', lambda: 'one'),
        ('2', lambda: 'two'),
        ('_', lambda: 'many')
        ])
print(matchTest(1))
print(matchTest(2))
print(matchTest(3))

print('-'*80)
matchTest = M([
        ('1', lambda: 'one'),
        ('"two"', lambda: 2),
        ('y:int', lambda y: 'scala.Int')
        ])
print(matchTest(1))
print(matchTest("two"))
print(matchTest(3))
