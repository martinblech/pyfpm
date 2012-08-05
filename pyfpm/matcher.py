"""
Matchers are the main user-facing API for `pyfpm`.

This module lets you unpack objects:

    >>> unpacker = Unpacker()
    >>> unpacker('head :: tail') << (1, 2, 3)
    >>> unpacker.head
    1
    >>> unpacker.tail
    (2, 3)

or function parameters:

    >>> @match_args('[x:str, [y:int, z:int]]')
    ... def match(x, y, z):
    ...     return (x, y, z)

    >>> match('abc', (1, 2))
    ('abc', 1, 2)

You can also create simple matchers with lambda expressions:

    >>> what_is_it = Matcher([
    ...     ('_:int', lambda: 'an int'),
    ...     ('_:str', lambda: 'a string'),
    ...     ('x', lambda x: 'something else: %s' % x),
    ...     ])

    >>> what_is_it(10)
    'an int'
    >>> what_is_it('abc')
    'a string'
    >>> what_is_it({})
    'something else: {}'

or more complex ones using a decorator:

    >>> parse_options = Matcher()
    >>> @parse_options.handler("['-h'|'--help', None]")
    ... def help():
    ...     return 'help'
    >>> @parse_options.handler("['-o'|'--optim', level:int] if 1<=level<=5")
    ... def set_optimization(level):
    ...     return 'optimization level set to %d' % level
    >>> @parse_options.handler("['-o'|'--optim', bad_level]")
    ... def bad_optimization(bad_level):
    ...     return 'bad optimization level: %s' % bad_level
    >>> @parse_options.handler('x')
    ... def unknown_options(x):
    ...     return 'unknown options: %s' % repr(x)

    >>> parse_options(('-h', None))
    'help'
    >>> parse_options(('--help', None))
    'help'
    >>> parse_options(('-o', 3))
    'optimization level set to 3'
    >>> parse_options(('-o', 0))
    'bad optimization level: 0'
    >>> parse_options(('-v', 'x'))
    "unknown options: ('-v', 'x')"

"""
from functools import wraps

from pyfpm.parser import Parser, _get_caller_globals
from pyfpm.pattern import _basestring

class NoMatch(Exception):
    """
    Thrown by matchers when no registered pattern could match the given object.

    """

class Matcher(object):
    """
    Maps patterns to handler functions.

    :param bindings: an optional list of pattern-handler pairs.
        String patterns are automatically parsed.
    :type bindings: iterable
    :param context: an optional context for the :class:`Parser`.
        If absent, it uses the caller's `globals()`
    :type context: dict

    """
    def __init__(self, bindings=[], context=None):
        self.bindings = []
        if context is None:
            context = _get_caller_globals()
        self.parser = Parser(context)
        for pattern, handler in bindings:
            self.register(pattern, handler)

    def register(self, pattern, handler):
        """
        Register a new pattern-handler pair. If the pattern is a string, it will
        be parsed automatically.

        :param pattern: Pattern or str -- the pattern
        :param handler: callable -- the handler function for the pattern

        """
        if isinstance(pattern, _basestring):
            pattern = self.parser(pattern)
        self.bindings.append((pattern, handler))

    def match(self, obj, *args):
        """
        Match the given object against the registerd patterns until the first
        match. The corresponding handler gets called with `args` as
        positional arguments and the match context as keyword arguments.

        :param obj: the object to match the patterns with
        :param args: the extra positional arguments that the handler function
            will get called with
        :raises: NoMatch -- if none of the patterns can match de object

        Example:

            >>> m = Matcher([
            ... ('head :: tail', lambda extra, head, tail: (extra, head, tail)),
            ... ('x', lambda extra, x: (extra, 'got something! %s' % x)),
            ... ])
            >>> m.match('hello', 'yo!')
            ('yo!', 'got something! hello')
            >>> m.match((1, 2, 3), 'numbers')
            ('numbers', 1, (2, 3))

        """
        for pattern, handler in self.bindings:
            match = pattern << obj
            if match:
                return handler(*args, **match.ctx)
        raise NoMatch('no registered pattern could match %s' % repr(obj))

    def __call__(self, obj, *args):
        """
        Same as :func:`match`. Matcher instances can be called directly:

            >>> m = Matcher([('_', lambda: 'yes')])
            >>> m(0) == m.match(0)
            True

        """
        return self.match(obj, *args)

    def handler(self, pattern):
        """
        Decorator for registering handlers. It's an alternate syntax with the
        same effect as :func:`register`:

            >>> m = Matcher()
            >>> @m.handler('x:int')
            ... def int_(x):
            ...     return 'an int: %d' % x
            >>> @m.handler('_')
            ... def any():
            ...     return 'any'
            >>> m(1)
            'an int: 1'
            >>> m(None)
            'any'

        """
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
    """
    Decorator for matching a function's arglist.

    :param pattern: Pattern or str -- the pattern
    :param context: dict -- an optional context for the pattern parser. If
        absent, it defaults to the caller's `globals()`.

    Usage:

        >>> @match_args('head::tail')
        ... def do_something(head, tail):
        ...     return (head, tail)
        >>> do_something(1, 2, 3, 4)
        (1, (2, 3, 4))

    """
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
    """
    Inline object unpacker. Usage:

        >>> unpacker = Unpacker()
        >>> unpacker('[x, [y, z]]') << (1, (2, 3))
        >>> unpacker.x
        1
        >>> unpacker.y
        2
        >>> unpacker.z
        3

    """
    def __call__(self, pattern, context=None):
        if isinstance(pattern, _basestring):
            if context is None:
                context = _get_caller_globals()
            pattern = Parser(context)(pattern)
        return _UnpackerHelper(self.__dict__, pattern)
