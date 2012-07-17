from pyfpm import pattern

class NoMatch(Exception): pass

class DynamicMatcher(object):
    def __init__(self, *bindings):
        self.bindings = list(bindings)

    def register(self, pattern, handler):
        self.bindings.append((pattern, handler))

    def match(self, obj):
        for pattern, handler in self.bindings:
            match = pattern << obj
            if match:
                return handler(**match.ctx)
        raise NoMatch('no registered pattern could match %s' % obj)
    def __call__(self, obj):
        return self.match(obj)

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

def statichandler(pattern):
    def wrapper(function):
        function.pattern = pattern
        return function
    return wrapper

class _static_matcher_metacls(type):
    def __new__(mcs, name, bases, dict_):
        bindings = map(lambda f: (f.pattern, f),
                sorted(f for f in dict_.values() if hasattr(f, 'pattern')))
        matcher = DynamicMatcher(*bindings)
        dict_['_matcher'] = matcher
        return type.__new__(mcs, name, bases, dict_)

class StaticMatcher(object):
    __metaclass__ = _static_matcher_metacls

    def __new__(cls, obj):
        return cls._matcher.match(obj)

    @classmethod
    def match(cls, obj):
        return cls(obj)
