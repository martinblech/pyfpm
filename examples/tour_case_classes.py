#!/usr/bin/env python
"""
Loose port of the examples at `A Tour of Scala: Case Classes <http://www.scala-lang.org/node/107>`_
"""
from __future__ import print_function

from pyfpm import MatchFunction, handler
from pyfpm import Case

class Term(Case): pass
class Var(Term):
    def __init__(self, name):
        self.name = name
class Fun(Term):
    def __init__(self, arg, body):
        self.arg = arg
        self.body = body
class App(Term):
    def __init__(self, f, v):
        self.f = f
        self.v = v

print('-'*80)
example = Fun('x', Fun('y', App(Var('x'), Var('y'))))
print(example)

print('-'*80)
x = Var('x')
print(x.name)

print('-'*80)
class printTerm(MatchFunction):
    @handler('Var(n:str)')
    def var(n):
        print(n, end='')

    @handler('Fun(x:str, b:Term)')
    def fun(x, b):
        print('^' + x + '.', end='')
        printTerm(b)

    @handler('App(f:Term, v:Term)')
    def app(f, v):
        print('(', end='')
        printTerm(f)
        print(' ', end='')
        printTerm(v)
        print(')', end='')

class isIdentityFun(MatchFunction):
    @handler('Fun(x, Var(y)) if x==y')
    def identity(x, y):
        return True

    @handler('_')
    def other():
        return False

id = Fun('x', Var('x'))
t = Fun('x', Fun('y', App(Var('x'), Var('y'))))
printTerm(t)
print()
print(isIdentityFun(id))
print(isIdentityFun(t))
