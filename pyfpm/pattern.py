"""
This module holds the actual pattern implementations.

End users should not normally have to deal with it, except for constructing
patterns programatically without making use of the pattern syntax parser.

"""

import re

try:
    # python 2.x base string
    _basestring = basestring
except NameError:
    # python 3.x base string
    _basestring = str

class Match(object):
    """
    Represents the result of matching successfully a pattern against an
    object. The `ctx` attribute is a :class:`dict` that contains the value for
    each bound name in the pattern, if any.

    """
    def __init__(self, ctx=None, value=None):
        if ctx is None:
            ctx = {}
        self.ctx = ctx
        self.value = value

    def __eq__(self, other):
        return (isinstance(other, Match) and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return 'Match(%s)' % self.ctx

class Pattern(object):
    """
    Base Pattern class. Abstracts the behavior common to all pattern types,
    such as name bindings, conditionals and operator overloading for combining
    several patterns.

    """

    def __init__(self):
        self.bound_name = None
        self.condition = None

    def match(self, other, ctx=None):
        """
        Match this pattern against an object. Operator: `<<`.

        :param other: the object this pattern should be matched against.
        :param ctx: optional context. If none, an empty one will be
            automatically created.
        :type ctx: dict
        :returns: a :class:`Match` if successful, `None` otherwise.

        """
        match = self._does_match(other, ctx)
        if match:
            ctx = match.ctx
            value = match.value or other
            if self.bound_name:
                if ctx is None:
                    ctx = {}
                try:
                    previous = ctx[self.bound_name]
                    if previous != value:
                        return None
                except KeyError:
                    ctx[self.bound_name] = value
            if self.condition is None or self.condition(**ctx):
                return Match(ctx)
        return None
    def __lshift__(self, other):
        return self.match(other)

    def bind(self, name):
        """Bind this pattern to the given name. Operator: `%`."""
        self.bound_name = name
        return self
    def __mod__(self, name):
        return self.bind(name)

    def if_(self, condition):
        """
        Add a boolean condition to this pattern. Operator: `/`.

        :param condition: must accept the match context as keyword
            arguments and return a boolean-ish value.
        :type condition: callable

        """
        self.condition = condition
        return self
    def __div__(self, condition):
        return self.if_(condition)
    def __truediv__(self, condition):
        return self.if_(condition)

    def multiply(self, n):
        """
        Build a :class:`ListPattern` that matches `n` instances of this pattern.
        Operator: `*`.

        Example:

            >>> p = EqualsPattern(1).multiply(3)
            >>> p.match((1, 1, 1))
            Match({})

        """
        return build(*([self]*n))
    def __mul__(self, length):
        return self.multiply(length)
    def __rmul__(self, length):
        return self.multiply(length)

    def or_with(self, other):
        """
        Build a new :class:`OrPattern` with this or the other pattern.
        Operator: `|`.

        Example:

            >>> p = EqualsPattern(1).or_with(InstanceOfPattern(str))
            >>> p.match('hello')
            Match({})
            >>> p.match(1)
            Match({})
            >>> p.match(2)

        """
        patterns = []
        for pattern in (self, other):
            if isinstance(pattern, OrPattern):
                patterns.extend(pattern.patterns)
            else:
                patterns.append(pattern)
        return OrPattern(*patterns)
    def __or__(self, other):
        return self.or_with(other)

    def head_tail_with(self, other):
        """
        Head-tail concatenate this pattern with the other. The lhs pattern will
        be the head and the other will be the tail. Operator: `+`.

        Example:

            >>> p = InstanceOfPattern(int).head_tail_with(ListPattern())
            >>> p.match([1])
            Match({})
            >>> p.match([1, 2])

        """
        return ListPattern(self, other)
    def __add__(self, other):
        return self.head_tail_with(other)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                ', '.join('='.join((str(k), repr(v))) for (k, v) in
                    self.__dict__.items() if v))

class AnyPattern(Pattern):
    """Pattern that matches anything."""
    def _does_match(self, other, ctx):
        return Match(ctx)

class EqualsPattern(Pattern):
    """Pattern that only matches objects that equal the given object."""
    def __init__(self, obj):
        super(EqualsPattern, self).__init__()
        self.obj = obj

    def _does_match(self, other, ctx):
        if self.obj == other:
            return Match(ctx)
        else:
            return None

class InstanceOfPattern(Pattern):
    """Pattern that only matches instances of the given class."""
    def __init__(self, cls):
        super(InstanceOfPattern, self).__init__()
        self.cls = cls

    def _does_match(self, other, ctx):
        if isinstance(other, self.cls):
            return Match(ctx)
        else:
            return None

_CompiledRegex = type(re.compile(''))
class RegexPattern(Pattern):
    """Pattern that only matches strings that match the given regex."""
    def __init__(self, regex):
        super(RegexPattern, self).__init__()
        if not isinstance(regex, _CompiledRegex):
            regex = re.compile(regex)
        self.regex = regex

    def _does_match(self, other, ctx):
        re_match = self.regex.match(other)
        if re_match:
            return Match(ctx, re_match.groups())
        return None

class ListPattern(Pattern):
    """Pattern that only matches iterables whose head matches `head_pattern` and
    whose tail matches `tail_pattern`"""
    def __init__(self, head_pattern=None, tail_pattern=None):
        super(ListPattern, self).__init__()
        if head_pattern is not None and tail_pattern is None:
            tail_pattern = ListPattern()
        self.head_pattern = head_pattern
        self.tail_pattern = tail_pattern

    def head_tail_with(self, other):
        return ListPattern(self.head_pattern,
                self.tail_pattern.head_tail_with(other))

    def _does_match(self, other, ctx):
        try:
            if (self.head_pattern is None and
                    self.tail_pattern is None and
                    len(other) == 0):
                return Match(ctx)
        except TypeError:
            return None
        if isinstance(other, _basestring):
            return None
        try:
            head, tail = other[0], other[1:]
        except (IndexError, TypeError):
            return None
        if self.head_pattern is not None:
            match = self.head_pattern.match(head, ctx)
            if match:
                ctx = match.ctx
                match = self.tail_pattern.match(tail, ctx)
                if match:
                    ctx = match.ctx
                else:
                    return None
            else:
                return None
        else:
            if len(other):
                return None
        return Match(ctx)

class NamedTuplePattern(Pattern):
    """Pattern that only matches named tuples of the given class and whose
    contents match the given patterns."""
    def __init__(self, casecls, *initpatterns):
        super(NamedTuplePattern, self).__init__()
        self.casecls_pattern = InstanceOfPattern(casecls)
        if (len(initpatterns) == 1 and
                isinstance(initpatterns[0], ListPattern)):
            self.initargs_pattern = initpatterns[0]
        else:
            self.initargs_pattern = build(*initpatterns, **dict(is_list=True))

    def _does_match(self, other, ctx):
        match = self.casecls_pattern.match(other, ctx)
        if not match:
            return None
        ctx = match.ctx
        return self.initargs_pattern.match(other, ctx)

class OrPattern(Pattern):
    """Pattern that matches whenever any of the inner patterns match."""
    def __init__(self, *patterns):
        if len(patterns) < 2:
            raise ValueError('need at least two patterns')
        super(OrPattern, self).__init__()
        self.patterns = patterns

    def _does_match(self, other, ctx):
        for pattern in self.patterns:
            if ctx is not None:
                ctx_ = ctx.copy()
            else:
                ctx_ = None
            match = pattern.match(other, ctx_)
            if match:
                return match
        return None

def build(*args, **kwargs):
    """
    Shorthand pattern factory.

    Examples:

        >>> build() == AnyPattern()
        True
        >>> build(1) == EqualsPattern(1)
        True
        >>> build('abc') == EqualsPattern('abc')
        True
        >>> build(str) == InstanceOfPattern(str)
        True
        >>> build(re.compile('.*')) == RegexPattern('.*')
        True
        >>> build(()) == build([]) == ListPattern()
        True
        >>> build([1]) == build((1,)) == ListPattern(EqualsPattern(1),
        ...     ListPattern())
        True
        >>> build(int, str, 'a') == ListPattern(InstanceOfPattern(int),
        ...     ListPattern(InstanceOfPattern(str),
        ...         ListPattern(EqualsPattern('a'))))
        True
        >>> try:
        ...     from collections import namedtuple
        ...     MyTuple = namedtuple('MyTuple', 'a b c')
        ...     build(MyTuple(1, 2, 3)) == NamedTuplePattern(MyTuple, 1, 2, 3)
        ... except ImportError:
        ...     True
        True

    """
    arglen = len(args)
    if arglen > 1:
        head, tail = args[0], args[1:]
        return ListPattern(build(head), build(*tail, **(dict(is_list=True))))
    if arglen == 0:
        return AnyPattern()
    (arg,) = args
    if kwargs.get('is_list', False):
        return ListPattern(build(arg))
    if isinstance(arg, Pattern):
        return arg
    if isinstance(arg, _CompiledRegex):
        return RegexPattern(arg)
    if isinstance(arg, tuple) and hasattr(arg, '_fields'):
        return NamedTuplePattern(arg.__class__, *map(build, arg))
    if isinstance(arg, type):
        return InstanceOfPattern(arg)
    if isinstance(arg, (tuple, list)):
        if len(arg) == 0:
            return ListPattern()
        return build(*arg, **(dict(is_list=True)))
    return EqualsPattern(arg)
