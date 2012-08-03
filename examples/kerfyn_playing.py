#!/usr/bin/env python
"""Loose port of the examples in `Kerflyn's Blog / Playing with Scala's 
pattern matching
<http://kerflyn.wordpress.com/2011/02/14/playing-with-scalas-pattern-matching/>`_
"""
from __future__ import print_function

from pyfpm.matcher import Matcher

# Traditional approach
print('-'*80)
toYesOrNo = Matcher([
        ('1', lambda: 'yes'),
        ('0', lambda: 'no'),
        ('_', lambda: 'error'),
        ])
for x in (0, 1, 2):
    print(toYesOrNo(x))

print('-'*80)
toYesOrNo = Matcher([
        ('1 | 2 | 3', lambda: 'yes'),
        ('0', lambda: 'no'),
        ('_', lambda: 'error'),
        ])
for x in (0, 1, 2, 3, 4):
    print(toYesOrNo(x))

print('-'*80)
def displayHelp():
    print('HELP')
def displayVersion():
    print('V1.0')
def unknownArgument(whatever):
    print('unknown argument: %s' % whatever)
parseArgument = Matcher([
        ('"-h" | "--help"', displayHelp),
        ('"-v" | "--version"', displayVersion),
        ('whatever', unknownArgument),
        ])
for x in ('-h', '--help', '-v', '--version', '-f', '--fdsa'):
    parseArgument(x)

# Typed Pattern
print('-'*80)
f = Matcher([
        ('i:int', lambda i: 'integer: %s' % i),
        ('_:float', lambda: 'a float'),
        ('s:str', lambda s: 'I want to say ' + s),
        ])
for x in (1, 1.0, 'hello'):
    print(f(x))

# Functional approach to pattern matching
print('-'*80)
fact = Matcher([
        ('0', lambda: 1),
        ('n:int', lambda n: n * fact(n - 1)),
        ])
for x in range(10):
    print(fact(x))

# Pattern matching and collection: the look-alike approach
print('-'*80)
length = Matcher([
        ('_ :: tail', lambda tail: 1 + length(tail)),
        ('[]', lambda: 0)
        ])
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
parseArgument = Matcher([
        ('["-l", lang]', setLanguageTo),
        ('["-o" | "--optim", n:int] if 0 < n <= 5', setOptimizationLevel),
        ('["-o" | "--optim", badLevel]', badOptimizationLevel),
        ('["-h" | "--help", None]', displayHelp),
        ('bad', badArgument),
        ])
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
from collections import namedtuple
X = namedtuple('X', [])
Const = namedtuple('Const', 'value')
Add = namedtuple('Add', 'left, right')
Mult = namedtuple('Mult', 'left, right')
Neg = namedtuple('Neg', 'expression')

eval = Matcher([
        ('X()',
            lambda xValue: xValue),
        ('Const(cst)',
            lambda xValue, cst: cst),
        ('Add(left, right)',
            lambda xValue, left, right: eval(left, xValue)+eval(right, xValue)),
        ('Mult(left, right)',
            lambda xValue, left, right: eval(left, xValue)*eval(right, xValue)),
        ('Neg(expr)',
            lambda xValue, expr: -eval(expr, xValue)),
        ])

expr = Add(Const(1), Mult(Const(2), Mult(X(), X()))) # 1 + 2 * X*X
print('expression:', expr)
result = eval(expr, 3)
print('f(3):', result)
assert result == 19

deriv = Matcher([
        ('X()', lambda: Const(1)),
        ('Const(_)', lambda: Const(0)),
        ('Add(left, right)',
            lambda left, right: Add(deriv(left), deriv(right))),
        ('Mult(left, right)',
            lambda left, right: Add(Mult(deriv(left), right),
                                    Mult(left, deriv(right)))),
        ('Neg(expr)', lambda: Neg(deriv(expr))),
        ])

df = deriv(expr)
print('df:', df)
result = eval(df, 3)
print('df(3):', result)
assert result == 12

_simplify = Matcher()
@_simplify.handler('Mult(Const(x), Const(y))')
def _mult_consts(x, y):
    return Const(x * y)
@_simplify.handler('Add(Const(x), Const(y))')
def _add_consts(x, y):
    return Const(x + y)
@_simplify.handler('Mult(Const(0), _)')
def _mult_zero_left():
    return Const(0)
@_simplify.handler('Mult(_, Const(0))')
def _mult_zero_right():
    return Const(0)
@_simplify.handler('Mult(Const(1), expr)')
def _mult_one_left(expr):
    return simplify(expr)
@_simplify.handler('Mult(expr, Const(1))')
def _mult_one_right(expr):
    return simplify(expr)
@_simplify.handler('Add(Const(0), expr)')
def _add_zero_left(expr):
    return simplify(expr)
@_simplify.handler('Add(expr, Const(0))')
def _add_zero_right(expr):
    return simplify(expr)
@_simplify.handler('Neg(Neg(expr))')
def _double_negation(expr):
    return simplify(expr)
@_simplify.handler('Add(left, right)')
def _normal_add(left, right):
    return Add(simplify(left), simplify(right))
@_simplify.handler('Mult(left, right)')
def _normal_mult(left, right):
    return Mult(simplify(left), simplify(right))
@_simplify.handler('Neg(expr)')
def _normal_negation(expr):
    return simplify(expr)
@_simplify.handler('expr')
def _no_can_do(expr):
    return expr

def simplify(expr):
    while True:
        simplified = _simplify(expr)
        if simplified == expr:
            return simplified
        expr = simplified

df_simplified = simplify(df)
print('df_simplified:', df_simplified)
result = eval(df_simplified, 3)
print('df_simplified(3)', result)
assert result == 12

for expr in (
        Add(Const(5), Const(10)),
        Mult(Mult(Mult(Const(5), Add(Const(1), Const(0))), Const(.2)), X()),
        ):
    print('expr:', expr)
    print('simplified:', simplify(expr))
