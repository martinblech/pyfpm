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
        if self._does_match(other):
            if self.bound_name:
                if ctx is None:
                    ctx = {}
                if self.bound_name in ctx:
                    raise AttributeError('pattern bound to duplicate name: %s'
                            % self.bound_name)
                ctx[self.bound_name] = other
            return Match(ctx)
        return None
    def __eq__(self, other):
        return self.match(other)

    def bind(self, name):
        self.bound_name = name
        return self
    def __mod__(self, name):
        return self.bind(name)

    def length(self):
        return 1

    def set_length(self, length):
        return RangePattern(self, length)
    def __mul__(self, length):
        return self.set_length(length)

class AnyPattern(Pattern):
    def _does_match(self, other):
        return True

class EqualsPattern(Pattern):
    def __init__(self, obj):
        super(EqualsPattern, self).__init__()
        self.obj = obj

    def _does_match(self, other):
        return self.obj == other

class InstanceOfPattern(Pattern):
    def __init__(self, cls):
        super(InstanceOfPattern, self).__init__()
        self.cls = cls

    def _does_match(self, other):
        return isinstance(other, self.cls)

class RangePattern(Pattern):
    def __init__(self, pattern=AnyPattern(), length=None):
        super(RangePattern, self).__init__()
        self.pattern = pattern
        self._length = length

    def set_length(self, length):
        self._length = length
        return self

    def length(self):
        return self._length

    def set_infinite(self):
        return self.set_length(-1)
    def __pos__(self):
        return self.set_infinite()

    def _does_match(self, other):
        if self.pattern.bound_name:
            raise ValueError("inner pattern in a range can't be bound")
        l = self.length()
        if l is None:
            raise ValueError('range length unset')
        if l == 1:
            raise ValueError('range length must be higher than 1')
        if l != -1 and len(other) != l:
            return None
        for item in other:
            if not self.pattern._does_match(item):
                return None
        return True

class ListPattern(Pattern):
    def __init__(self, *patterns):
        super(ListPattern, self).__init__()
        self.patterns = patterns

    def match(self, other, ctx=None):
        remaining = other
        for pattern in self.patterns:
            l = pattern.length()
            if len(remaining) < l:
                return None
            if l == 1:
                match = pattern.match(remaining[0], ctx)
            elif l == -1:
                match = pattern.match(remaining, ctx)
            else:
                match = pattern.match(remaining[:l], ctx)
            if not match:
                return None
            if ctx is None:
                ctx = match.ctx
            if l != -1:
                remaining = remaining[l:]
            else:
                remaining = tuple()
        if len(remaining):
            return None
        return Match(ctx)
