"""Scala-like case classes.
"""

import functools
import inspect

def _lookup(classes, attr):
    for cls in classes:
        try:
            return getattr(cls, attr)
        except AttributeError:
            pass

class case_metacls(type):
    def __new__(mcs, name, bases, dict_):
        original_init = (dict_.get('__init__', None) or
                _lookup(bases, '__init__'))
        if inspect.isfunction(original_init):
            # introspection for Python __init__
            argnames, varargs, keywords, _ = inspect.getargspec(original_init)
            if keywords:
                raise AttributeError(
                        "case class __init__ is picky with kwargs")
            def __init__(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                callargs = inspect.getcallargs(original_init, self, *args,
                        **kwargs)
                self._case_args = tuple(callargs[x] for x in argnames[1:])
                if varargs:
                    self._case_args += callargs[varargs]
            functools.update_wrapper(__init__, original_init)
        else:
            # no introspection for native built-in __init__
            def __init__(self, *args, **kwargs):
                if kwargs:
                    raise AttributeError(
                            "case class __init__ is picky with kwargs")
                original_init(self, *args)
                self._case_args = args
        dict_['__init__'] = __init__
        return type.__new__(mcs, name, bases, dict_)

class Case(object):
    """ Base case class. You can either inherit from this or use the
    case_metacls metaclass directly.
    This won't be enforced, but case instances should be immutable. Matchers
    will only look at init-time values and won't check the current state.
    """
    __metaclass__ = case_metacls
    def __init__(self): pass
    def __repr__(self):
        return '%s%s' % (self.__class__.__name__, self._case_args)
    def __eq__(self, other):
        return (other.__class__ == self.__class__ and 
                other._case_args == self._case_args)
