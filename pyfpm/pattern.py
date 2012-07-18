import re

class Match(object):
    def __init__(self, ctx=None):
        if ctx is None:
            ctx = {}
        self.ctx = ctx
    def __eq__(self, other):
        return isinstance(other, Match) and other.ctx == self.ctx
    def __repr__(self):
        return 'Match(%s)' % self.ctx

class Pattern(object):
    def __init__(self):
        self.bound_name = None

    def match(self, other, ctx=None):
        match = self._does_match(other, ctx)
        if match:
            ctx = match.ctx
            # repeated code, TODO figure out something better
            if self.bound_name:
                if ctx is None:
                    ctx = {}
                try:
                    previous = ctx[self.bound_name]
                    if previous != other:
                        print '!!!!!!'
                        return None
                except KeyError:
                    ctx[self.bound_name] = other
            # end repeated code
            return Match(ctx)
        return None
    def __lshift__(self, other):
        return self.match(other)

    def bind(self, name):
        self.bound_name = name
        return self
    def __mod__(self, name):
        return self.bind(name)

    def length(self):
        return 1

    def set_length(self, length):
        return build(*([self]*length))
    def __mul__(self, length):
        return self.set_length(length)
    def __rmul__(self, length):
        return self.set_length(length)

    def or_with(self, other):
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
        return ListPattern(self, other)
    def __floordiv__(self, other):
        return self.head_tail_with(other)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                ', '.join('='.join(map(str, (k, v))) for (k, v) in
                    self.__dict__.items() if v))

class AnyPattern(Pattern):
    def _does_match(self, other, ctx):
        return Match(ctx)

class EqualsPattern(Pattern):
    def __init__(self, obj):
        super(EqualsPattern, self).__init__()
        self.obj = obj

    def _does_match(self, other, ctx):
        if self.obj == other:
            return Match(ctx)
        else:
            return None

class InstanceOfPattern(Pattern):
    def __init__(self, cls):
        super(InstanceOfPattern, self).__init__()
        self.cls = cls

    def _does_match(self, other, ctx):
        if isinstance(other, self.cls):
            return Match(ctx)
        else:
            return None

class RegexPattern(Pattern):
    def __init__(self, regex):
        raise ValueError('not ready yet')
        super(RegexPattern, self).__init__()
        if not isinstance(regex, re.RegexObject):
            regex = re.compile(regex)
        self.regex = regex
    # TODO: finish this, must improve Pattern._do_match

class ListPattern(Pattern):
    def __init__(self, head_pattern=None, tail_pattern=None):
        super(ListPattern, self).__init__()
        self.head_pattern = head_pattern
        self.tail_pattern = tail_pattern

    def _does_match(self, other, ctx):
        try:
            if (self.head_pattern is None and
                    self.tail_pattern is None and
                    len(other) == 0):
                return Match(ctx)
        except TypeError:
            return None
        try:
            head, tail = other[0], other[1:]
        except IndexError:
            return None
        if self.head_pattern is not None:
            match = self.head_pattern.match(head, ctx)
            if match:
                ctx = match.ctx
                if self.tail_pattern is not None:
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

    # def match(self, other, ctx=None):
    #     if not hasattr(other, '__iter__'):
    #         return None
    #     if self.head_pattern:
    #         match = self.head_pattern.match(other[0], ctx)
    #         if not match:
    #             return None
    #         ctx = match.ctx
    #         if self.tail_pattern:
    #             match = self.tail_pattern.match(other[1:], ctx)
    #             if not match:
    #                 return None
    #             ctx = match.ctx
    #     # repeated code, TODO figure out something better
    #     if self.bound_name:
    #         if ctx is None:
    #             ctx = {}
    #         try:
    #             previous = ctx[self.bound_name]
    #             if previous != other:
    #                 return None
    #         except KeyError:
    #             ctx[self.bound_name] = other
    #     # end repeated code
    #     return Match(ctx)

class CasePattern(Pattern):
    def __init__(self, casecls, *initpatterns):
        super(CasePattern, self).__init__()
        self.casecls_pattern = InstanceOfPattern(casecls)
        self.initargs_pattern = ListPattern(*initpatterns)

    def match(self, other, ctx=None):
        if not self.casecls_pattern.match(other, ctx):
            return None
        match = self.initargs_pattern.match(other._case_args, ctx)
        if not match:
            return None
        # repeated code, TODO figure out something better
        ctx = match.ctx
        if self.bound_name:
            if ctx is None:
                ctx = {}
            try:
                previous = ctx[self.bound_name]
                if previous != other:
                    return None
            except KeyError:
                ctx[self.bound_name] = other
        # end repeated code
        return Match(ctx)

class OrPattern(Pattern):
    def __init__(self, *patterns):
        if len(patterns) < 2:
            raise ValueError('need at least two patterns')
        super(OrPattern, self).__init__()
        self.patterns = patterns

    def match(self, other, ctx=None):
        for pattern in self.patterns:
            if ctx is not None:
                ctx_ = ctx.copy()
            else:
                ctx_ = None
            match = pattern.match(other, ctx_)
            if match:
                # repeated code, TODO figure out something better
                ctx = match.ctx
                if self.bound_name:
                    if ctx is None:
                        ctx = {}
                    try:
                        previous = ctx[self.bound_name]
                        if previous != other:
                            return None
                    except KeyError:
                        ctx[self.bound_name] = other
                # end repeated code
                return Match(ctx)
        return None

def build(*args, **kwargs):
    arglen = len(args)
    if arglen > 1:
        head, tail = args[0], args[1:]
        return ListPattern(build(head), build(*tail, is_list=True))
    if arglen == 0:
        return AnyPattern()
    (arg,) = args
    if kwargs.get('is_list', False):
        return ListPattern(build(arg))
    if isinstance(arg, Pattern):
        return arg
    if hasattr(arg, '_case_args'):
        return CasePattern(arg.__class__,
                *map(build, arg._case_args))
    if isinstance(arg, type):
        return InstanceOfPattern(arg)
    if isinstance(arg, (tuple, list)):
        if len(arg) == 0:
            return ListPattern()
        return build(*arg)
    return EqualsPattern(arg)
