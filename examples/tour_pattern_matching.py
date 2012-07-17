"""
Loose port of the examples at `A Tour of Scala: Pattern Matching <http://www.scala-lang.org/node/120>`_
"""
from __future__ import print_function

from pyfpm.matcher import DynamicMatcher as M
from pyfpm.pattern import build as _

print('-'*80)
matchTest = lambda x: M(
        (_(1), lambda: 'one'),
        (_(2), lambda: 'two'),
        (_(), lambda: 'many')
        ).match(x)
print(matchTest(1))
print(matchTest(2))
print(matchTest(3))

print('-'*80)
matchTest = lambda x: M(
        (_(1), lambda: 'one'),
        (_("two"), lambda: 2),
        (_(int)%'y', lambda y: 'scala.Int')
        ).match(x)
print(matchTest(1))
print(matchTest("two"))
print(matchTest(3))
