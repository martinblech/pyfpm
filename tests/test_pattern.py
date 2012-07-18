try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyfpm import pattern
from pyfpm import Case

_m = pattern.Match

_any = pattern.AnyPattern
class TestAny(unittest.TestCase):
    def test_match_unbound(self):
        self.assertEquals(_any()<<1, _m())

    def test_match_int(self):
        self.assertEquals(_any()%'x'<<1, _m({'x': 1}))

_eq = pattern.EqualsPattern
class TestEquals(unittest.TestCase):
    def test_match_unbound(self):
        self.assertEquals(_eq(1)<<1, _m())

    def test_match_int(self):
        self.assertEquals(_eq(1)%'x'<<1, _m({'x': 1}))

    def test_not_match_different_int(self):
        self.assertFalse(_eq(1)%'x'<<2)

    def test_not_match_different_type(self):
        self.assertFalse(_eq(1)%'x'<<'abc')

_iof = pattern.InstanceOfPattern
class TestInstance(unittest.TestCase):
    def test_match_int(self):
        self.assertEquals(_iof(int)%'x'<<1, _m({'x': 1}))

    def test_match_different_int(self):
        self.assertEquals(_iof(int)%'x'<<2, _m({'x': 2}))

    def test_not_match_different_type(self):
        self.assertFalse(_iof(int)%'x'<<'abc')

_l = pattern.ListPattern
class TestList(unittest.TestCase):
    def test_match_empty_list(self):
        self.assertEquals(_l()%'x'<<[], _m({'x': []}))

    def test_match_single_item(self):
        self.assertEquals(_l(_eq(1)%'x')<<[1], _m({'x': 1}))

    def test_match_multiple_items(self):
        self.assertEquals(_l(_eq(1)%'x', _l(_iof(str)%'y'))<<(1, 'a'),
                _m({'x': 1, 'y': 'a'}))

    def test_match_head_tail(self):
        self.assertEquals(_l(_any()%'head', _any()%'tail')<<(1, 2, 3),
                _m({'head': 1, 'tail': (2, 3)}))

    def test_not_match_scalar(self):
        scalars = (1, 'abc', .5, 'd', lambda: None)
        for x in scalars:
            self.assertFalse(_l() << x)
            self.assertFalse(_l(_any()) << x)

    # TODO: more tests

_c = pattern.CasePattern
class MyCase(Case):
    def __init__(self, *args): pass

class TestCasePattern(unittest.TestCase):
    def test_match_single_arg(self):
        self.assertEquals(_c(MyCase, _eq(1)%'x')<<MyCase(1), _m({'x': 1}))

    def test_match_multiple_args(self):
        self.assertEquals(_c(MyCase, _eq(1)%'x', _iof(str)*3%'y')<<
                                                MyCase(1, 'a', 'b', 'c'),
                _m({'x': 1, 'y': ('a', 'b', 'c')}))

    def test_match_head_tail(self):
        self.assertEquals(_c(MyCase, _any()%'head', _any()%'tail')%'x'<<
                                                MyCase(1, 2, 3),
                        _m({'head': 1, 'tail': (2, 3), 'x': MyCase(1, 2, 3)}))

    # TODO: more tests

_or = pattern.OrPattern
class TestOr(unittest.TestCase):
    def test_simple_or(self):
        p = _or(_l()%'x', _l(_any()%'y'))
        self.assertEquals(p << [], _m({'x': []}))
        self.assertEquals(p << [1], _m({'y': 1}))

    def test_bind(self):
        p = _or(_l()%'a', _any()%'b')%'x'
        self.assertEquals(p<<[], _m({'a': [], 'x':[]}))
        self.assertEquals(p<<1, _m({'b': 1, 'x':1}))

_ = pattern.build
class TestPBuilder(unittest.TestCase):
    def test_int(self):
        self.assertEquals(_(1), _eq(1))

    def test_str(self):
        self.assertEquals(_('abc'), _eq('abc'))

    def test_class(self):
        self.assertEquals(_(str), _iof(str))

    def test_case(self):
        class MyCase(Case): pass
        self.assertEquals(_(MyCase()), _c(MyCase))

    def test_pattern(self):
        self.assertEquals(_(_()), _())

    def test_any(self):
        self.assertEquals(_(), _any())

    def test_nil(self):
        self.assertEquals(_([]), _l())

    def test_list(self):
        self.assertEquals(_(1, str), _l(_(1), _l(_(str))))

class TestOperators(unittest.TestCase):
    def test_mul(self):
        self.assertEquals(_()*2, _l(_any(), _l(_any())))
    def test_rmul(self):
        self.assertEquals(2*_(1), _(1)*2)

    def test_mod(self):
        self.assertEquals(_(1)%'x', _(1).bind('x'))

    def test_or(self):
        self.assertEquals(_(1) | _(), _or(_(1), _()))
        self.assertEquals(_or(_(1), _(2)) | _(3), _or(_(1), _(2), _(3)))
        self.assertEquals(_(1) | _or(_(2), _(3)), _or(_(1), _(2), _(3)))

    def test_add(self):
        self.assertEquals(_(1) + _(), _l(_(1), _()))

class TestMultibind(unittest.TestCase):
    pattern = _(_()%'x', _()%'x', _()%'y')
    def test_sameok(self):
        self.assertEquals(TestMultibind.pattern << (1, 1, 2),
                _m({'x': 1, 'y': 2}))

    def test_differentfail(self):
        print TestMultibind.pattern
        self.assertFalse(TestMultibind.pattern << (1, 2, 3))
