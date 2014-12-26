# encoding: UTF-8
"""
Tests for the Attr class.
"""
from collections import defaultdict

from nose.tools import assert_equals, assert_true


def test_repr():
    """
    Create a text representation of Attr.
    """
    from attrdict.attr import Attr

    assert_equals(repr(Attr()), 'a{}')
    assert_equals(repr(Attr({'foo': 'bar'})), "a{'foo': 'bar'}")
    assert_equals(repr(Attr({'foo': {1: 2}})), "a{'foo': {1: 2}}")
    assert_equals(repr(Attr({'foo': Attr({1: 2})})), "a{'foo': a{1: 2}}")


def test_subclassability():
    """
    Ensure Attr is sub-classable
    """
    from attrdict.attr import Attr

    class DefaultAttr(Attr):
        """
        A subclassed version of Attr that uses an defaultdict.
        """
        def __init__(self, items=None, sequence_type=tuple):
            self.__setattr__('_mapping', defaultdict(lambda: 0), force=True)

            super(DefaultAttr, self).__init__(items, sequence_type)

        @property
        def mapping(self):
            "Access to the internal mapping"
            return self._mapping

    default = DefaultAttr({'foo': 'bar', 'mapping': 'not overwritten'})

    assert_true(isinstance(default.mapping, defaultdict))

    assert_equals(default.foo, 'bar')
    assert_equals(default('mapping'), 'not overwritten')
