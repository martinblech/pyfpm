#!/usr/bin/env python
"""Loose port of the examples in `Kerflyn's Blog / Playing with Scala's 
pattern matching
<http://kerflyn.wordpress.com/2011/02/14/playing-with-scalas-pattern-matching/>`_
"""
from __future__ import print_function

from pyfpm import Matcher as M, NoMatch
from pyfpm import build as _
from pyfpm import Case

# Traditional approach
print('-'*80)
toYesOrNo = M(
        (_(1), lambda: 'yes'),
        (_(0), lambda: 'no'),
        (_(), lambda: 'error'),
        )
for x in (0, 1, 2):
    print(toYesOrNo(x))

print('-'*80)
toYesOrNo = M(
        (_(1) | _(2) | _(3), lambda: 'yes'),
        (_(0), lambda: 'no'),
        (_(), lambda: 'error'),
        )
for x in (0, 1, 2, 3, 4):
    print(toYesOrNo(x))

print('-'*80)
def displayHelp():
    print('HELP')
def displayVersion():
    print('V1.0')
def unknownArgument(whatever):
    print('unknown argument: %s' % whatever)
parseArgument = M(
        (_('-h') | _('--help'), displayHelp),
        (_('-v') | _('--version'), displayVersion),
        (_()%'whatever', unknownArgument),
        )
for x in ('-h', '--help', '-v', '--version', '-f', '--fdsa'):
    parseArgument(x)

# Typed Pattern
print('-'*80)
f = M(
        (_(int)%'i', lambda i: 'integer: %s' % i),
        (_(float), lambda: 'a float'),
        (_(str)%'s', lambda s: 'I want to say ' + s),
        )
for x in (1, 1.0, 'hello'):
    print(f(x))

# Functional approach to pattern matching
print('-'*80)
fact = M(
        (_(0), lambda: 1),
        (_(int)%'n', lambda n: n * fact(n - 1)),
        )
for x in range(10):
    print(fact(x))

# Pattern matching and collection: the look-alike approach
print('-'*80)
length = M(
        (_() + _()%'tail', lambda tail: 1 + length(tail)),
        (_([]), lambda: 0)
        )
for x in range(10):
    print(length([None]*x))

print('-'*80)
def setLanguageTo(lang):
    print('language set to:', lang)
def setOptimizationLevel(n):
    print('optimization level set to:', n)
def badOptimizationLevel(badLevel):
    print('bad optimization level:', badLevel)
def displayHelp():
    print('help!')
def badArgument(bad):
    print('bad argument:', bad)
parseArgument = M(
        (_('-l', _(str)%'lang'), setLanguageTo),
        (_(_('-o') | _('--optim'), _(int)%'n').if_(lambda n: 0 < n <= 5),
            setOptimizationLevel),
        (_(_('-o') | _('--optim'), _()%'badLevel'), badOptimizationLevel),
        (_(_('-h') | _('--help'), _(None)), displayHelp),
        (_()%'bad', badArgument),
        )
for x in (('-l', 'eng'),
        ('-o', 1), ('--optim', 5),
        ('-o', 0), ('--optim', 6),
        ('-h', None), ('--help', None),
        ('-h', 1), ('--help', 'abc'),
        None, 'blabla'
        ):
    parseArgument(x)

# Advanced pattern matching: case class

print('-'*80)
class Expression(Case): pass
class X(Expression): pass
class Const(Expression):
    def __init__(self, value): pass
class Add(Expression):
    def __init__(self, left, right): pass
class Mult(Expression):
    def __init__(self, left, right): pass
class Neg(Expression):
    def __init__(self, expr): pass

def eval(expression, xValue):
    return M(
            (_(X()),
                lambda: xValue),
            (_(Const(_()%'cst')),
                lambda cst: cst),
            (_(Add(_()%'left', _()%'right')),
                lambda left, right: eval(left, xValue) + eval(right, xValue)),
            (_(Mult(_()%'left', _()%'right')),
                lambda left, right: eval(left, xValue) * eval(right, xValue)),
            (_(Neg(_()%'expr')),
                lambda expr: -eval(expr, xValue)),
            )(expression)

expr = Add(Const(1), Mult(Const(2), Mult(X(), X()))) # 1 + 2 * X*X
print('expression:', expr)
result = eval(expr, 3)
print('f(3):', result)
assert result == 19

deriv = M(
        (_(X()), lambda: Const(1)),
        (_(Const(_())), lambda: Const(0)),
        (_(Add(_()%'left', _()%'right')),
            lambda left, right: Add(deriv(left), deriv(right))),
        (_(Mult(_()%'left', _()%'right')),
            lambda left, right: Add(Mult(deriv(left), right),
                                    Mult(left, deriv(right)))),
        (_(Neg(_()%'expr')), lambda: Neg(deriv(expr))),
        )

df = deriv(expr)
print('df:', df)
result = eval(df, 3)
print('df(3):', result)
assert result == 12
