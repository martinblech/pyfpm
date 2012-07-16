try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyfpm import pattern

_m = pattern.Match

_any = pattern.AnyPattern
class TestAny(unittest.TestCase):
    def test_match_unbound(self):
        self.assertEquals(_any()==1, _m())

    def test_match_int(self):
        self.assertEquals(_any()%'x'==1, _m({'x': 1}))

_eq = pattern.EqualsPattern
class TestEquals(unittest.TestCase):
    def test_match_unbound(self):
        self.assertEquals(_eq(1)==1, _m())

    def test_match_int(self):
        self.assertEquals(_eq(1)%'x'==1, _m({'x': 1}))

    def test_not_match_different_int(self):
        self.assertFalse(_eq(1)%'x'==2)

    def test_not_match_different_type(self):
        self.assertFalse(_eq(1)%'x'=='abc')

_iof = pattern.InstanceOfPattern
class TestInstance(unittest.TestCase):
    def test_match_int(self):
        self.assertEquals(_iof(int)%'x'==1, _m({'x': 1}))

    def test_match_different_int(self):
        self.assertEquals(_iof(int)%'x'==2, _m({'x': 2}))

    def test_not_match_different_type(self):
        self.assertFalse(_iof(int)%'x'=='abc')

_r = pattern.RangePattern
class TestRange(unittest.TestCase):
    def test_match_range_unbound(self):
        self.assertEquals(_iof(str)*2==('a', 'b'), _m())

    def test_match_range(self):
        self.assertEquals(_iof(int)*2%'x'==(1, 2), _m({'x': (1, 2)}))

_l = pattern.ListPattern
class TestList(unittest.TestCase):
    def test_match_single_item(self):
        self.assertEquals(_l(_eq(1)%'x')==[1], _m({'x': 1}))

    def test_match_multiple_items(self):
        self.assertEquals(_l(_eq(1)%'x', _iof(str)%'y')==(1, 'a'),
                _m({'x': 1, 'y': 'a'}))

    def test_match_head_tail(self):
        self.assertEquals(_l(_any()%'head', +_r()%'tail')==(1, 2, 3),
                _m({'head': 1, 'tail': (2, 3)}))
