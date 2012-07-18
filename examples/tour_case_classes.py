#!/usr/bin/env python
"""
Loose port of the examples at `A Tour of Scala: Case Classes <http://www.scala-lang.org/node/107>`_
"""
from __future__ import print_function

from pyfpm import Matcher as M
from pyfpm import build as _
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
printTerm = M(
        (_(Var(_(str)%'n')), lambda n: (
            print(n, end='')
            )),
        (_(Fun(_(str)%'x', _(Term)%'b')), lambda x, b: (
            print('^' + x + '.', end=''),
            printTerm(b)
            )),
        (_(App(_(Term)%'f', _(Term)%'v')), lambda f, v: (
            print('(', end=''),
            printTerm(f),
            print(' ', end=''),
            printTerm(v),
            print(')', end='')
            )),
        )
isIdentityFun = M(
        (_(Fun(_()%'x', Var(_()%'y'))), lambda x, y: x==y),
        (_(), lambda: False),
        )
id = Fun('x', Var('x'))
t = Fun('x', Fun('y', App(Var('x'), Var('y'))))
printTerm(t)
print()
print(isIdentityFun(id))
print(isIdentityFun(t))
