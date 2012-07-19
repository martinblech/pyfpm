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
        try:
            original_init = original_init._original_init
        except AttributeError:
            pass
        if (hasattr(inspect, 'getargspec') and
                hasattr(inspect, 'getcallargs') and
                inspect.isfunction(original_init)):
            # try introspection for Python __init__
            argnames, varargs, keywords, _ = inspect.getargspec(original_init)
            if keywords:
                raise AttributeError(
                        'case class __init__ is picky with kwargs')
            def __init__(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                callargs = inspect.getcallargs(original_init, self, *args,
                        **kwargs)
                self._case_args = tuple(callargs[x] for x in argnames[1:])
                if varargs:
                    self._case_args += callargs[varargs]
            functools.update_wrapper(__init__, original_init)
            __init__._original_init = original_init
        else:
            # no introspection (python<2.7 or non-python function)
            def __init__(self, *args, **kwargs):
                if kwargs:
                    raise AttributeError(
                            'case class __init__ is picky with kwargs')
                if original_init:
                    original_init(self, *args)
                self._case_args = args
        dict_['__init__'] = __init__
        return type.__new__(mcs, name, bases, dict_)


