from pyfpm.matcher_common import *
try:
    from pyfpm.matcher_3x import _StaticMatcher
except SyntaxError:
    from pyfpm.matcher_2x import _StaticMatcher

class MatchFunction(_StaticMatcher):
    def __new__(cls, *args):
        return cls._matcher.match(args[-1], *args[:-1])
