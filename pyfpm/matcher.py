import sys
from functools import wraps

from pyfpm.parser import Parser, _get_caller_globals

try:
    _basestring = basestring
except NameError:
    _basestring = str

class NoMatch(Exception): pass

class Matcher(object):
    def __init__(self, bindings=[], context=None):
        self.bindings = []
        if context is None:
            context = _get_caller_globals()
        self.parser = Parser(context)
        for pattern, handler in bindings:
            self.register(pattern, handler)

    def register(self, pattern, handler):
        if isinstance(pattern, _basestring):
            pattern = self.parser(pattern)
        self.bindings.append((pattern, handler))

    def match(self, obj, *args):
        for pattern, handler in self.bindings:
            match = pattern << obj
            if match:
                return handler(*args, **match.ctx)
        raise NoMatch('no registered pattern could match %s' % repr(obj))
    def __call__(self, obj, *args):
        return self.match(obj, *args)

    def handler(self, pattern):
        def _reg(function):
            self.register(pattern, function)
            return function
        return _reg

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.bindings == other.bindings and
                self.parser.context == other.parser.context)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                ','.join('='.join((str(k), repr(v)))
                    for (k, v) in self.__dict__.items()))

def match_args(pattern, context=None):
    if isinstance(pattern, _basestring):
        if context is None:
            context = _get_caller_globals()
        pattern = Parser(context)(pattern)
    def wrapper(function):
        @wraps(function)
        def f(*args):
            match = pattern.match(args)
            if not match:
                raise NoMatch("%s doesn't match %s" % (pattern, args))
            return function(**match.ctx)
        return f
    return wrapper

class _UnpackerHelper(object):
    def __init__(self, vars, pattern):
        self.vars = vars
        self.pattern = pattern

    def _do(self, other):
        match = self.pattern.match(other)
        if not match:
            raise NoMatch("%s doesn't match %s" % (self.pattern, other))
        self.vars.update(match.ctx)

    def __lshift__(self, other):
        return self._do(other)

class Unpacker(object):
    def __call__(self, pattern, context=None):
        if isinstance(pattern, _basestring):
            if context is None:
                context = _get_caller_globals()
            pattern = Parser(context)(pattern)
        return _UnpackerHelper(self.__dict__, pattern)
