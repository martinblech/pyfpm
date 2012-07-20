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
        def _reg(f):
            self.register(pattern, f)
            return f
        return _reg

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.bindings == other.bindings and
                self.parser.context == other.parser.context)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                ','.join('='.join((str(k), repr(v)))
                    for (k, v) in self.__dict__.items()))

def handler(pattern):
    def wrapper(function):
        function.pattern = pattern
        return function
    return wrapper

if sys.version_info < (3, 0):
    def _function_sort_key(function):
        return function.func_code.co_firstlineno
else:
    def _function_sort_key(function):
        return function.__code__.co_firstlineno

class _static_matcher_metacls(type):
    def __new__(mcs, name, bases, dict_):
        bindings = map(lambda f: (f.pattern, f),
                sorted((f for f in dict_.values() if hasattr(f, 'pattern')),
                    key=_function_sort_key))
        context = _get_caller_globals()
        matcher = Matcher(bindings=bindings, context=context)
        dict_['_matcher'] = matcher
        return type.__new__(mcs, name, bases, dict_)

def match_args(pattern):
    if isinstance(pattern, _basestring):
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
