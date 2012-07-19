from pyfpm import pattern

class NoMatch(Exception): pass

class Matcher(object):
    def __init__(self, *bindings):
        self.bindings = list(bindings)

    def register(self, pattern, handler):
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
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return '%s(bindings=%s)' % (self.__class__.__name__, self.bindings)

def handler(pattern):
    def wrapper(function):
        function.pattern = pattern
        return function
    return wrapper

def _function_sort_key(function):
    return function.func_code.co_firstlineno

class _static_matcher_metacls(type):
    def __new__(mcs, name, bases, dict_):
        bindings = map(lambda f: (f.pattern, f),
                sorted((f for f in dict_.values() if hasattr(f, 'pattern')),
                    key=_function_sort_key))
        matcher = Matcher(*bindings)
        dict_['_matcher'] = matcher
        return type.__new__(mcs, name, bases, dict_)
