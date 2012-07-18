#!/usr/bin/env python

from __future__ import print_function
import sys
import random
import time

from pyfpm import Matcher as M, MatchFunction as MF, handler as h
from pyfpm import build as _
from pyfpm import Case

(iterations,) = map(int, sys.argv[1:])

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

dynamic = M(
        (_(1)%'x', lambda x: x),
        (_('abc')%'x', lambda x: x),
        (_(int)%'x', lambda x: x),
        (_(str)%'x', lambda x: x),
        (_(Var(_(str)%'n')), lambda n: n),
        (_(Fun(_(str)%'x', _(Term)%'b')), lambda x, b: (x, b)),
        (_(App(_(Term)%'f', _(Term)%'v')), lambda f, v: (f, v)),
        )

class static(MF):
    @h(_(1)%'x')
    def one(x): return x
    @h(_('abc')%'x')
    def abc(x): return x
    @h(_(int)%'x')
    def int(x): return x
    @h(_(str)%'x')
    def string(x): return x
    @h(_(Var(_(str)%'n')))
    def var(n): return n
    @h(_(Fun(_(str)%'x', _(Term)%'b')))
    def fun(x, b): return x, b
    @h(_(App(_(Term)%'f', _(Term)%'v')))
    def app(f, v): return f, v

objects = (1, 'abc', 2, 'def', Fun('x', Var('x')),
        Fun('x', Fun('y', App(Var('x'), Var('y')))),
        App(App(Var('x'), Var('x')), Fun('y', Var('z'))),
        )

matchers = dict(dynamic=dynamic, static=static)

for name, matcher in matchers.items():
    # warmup
    for i in range(iterations/10):
        obj = random.choice(objects)
        matcher(obj)
    # actual timing
    t = time.time()
    for i in range(iterations):
        obj = random.choice(objects)
        matcher(obj)
    t = time.time() - t
    print('%s: %s' % (name, t))
