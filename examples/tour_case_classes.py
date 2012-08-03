#!/usr/bin/env python
"""
Loose port of the examples at `A Tour of Scala: Case Classes <http://www.scala-lang.org/node/107>`_
"""
from __future__ import print_function
from collections import namedtuple

from pyfpm.matcher import Matcher

Var = namedtuple('Var', 'name')
Fun = namedtuple('Fun', 'arg, body')
App = namedtuple('Term', 'f, v')

print('-'*80)
example = Fun('x', Fun('y', App(Var('x'), Var('y'))))
print(example)

print('-'*80)
x = Var('x')
print(x.name)

print('-'*80)
printTerm = Matcher()
@printTerm.handler('Var(n:str)')
def _var(n):
    print(n, end='')
@printTerm.handler('Fun(x:str, b)')
def _fun(x, b):
    print('^' + x + '.', end='')
    printTerm(b)
@printTerm.handler('App(f, v)')
def _app(f, v):
    print('(', end='')
    printTerm(f)
    print(' ', end='')
    printTerm(v)
    print(')', end='')

isIdentityFun = Matcher()
@isIdentityFun.handler('Fun(x, Var(y)) if x==y')
def _identity(x, y):
    return True
@isIdentityFun.handler('_')
def _other():
    return False

id = Fun('x', Var('x'))
t = Fun('x', Fun('y', App(Var('x'), Var('y'))))
printTerm(t)
print()
print(isIdentityFun(id))
print(isIdentityFun(t))
