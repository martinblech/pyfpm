"""Scala-like case classes.
"""
from pyfpm.caseclass_common import case_metacls
try:
    from pyfpm.caseclass_3x import _Case
except SyntaxError:
    from pyfpm.caseclass_2x import _Case

class Case(_Case):
    """ Base case class. You can either inherit from this or use the
    case_metacls metaclass directly.
    This won't be enforced, but case instances should be immutable. Matchers
    will only look at init-time values and won't check the current state.
    """
    def __init__(self): pass
    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self._case_args)
    def __eq__(self, other):
        return (other.__class__ == self.__class__ and 
                other._case_args == self._case_args)
