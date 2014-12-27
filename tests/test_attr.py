# encoding: UTF-8
"""
Tests for the Attr class.
"""
from nose.tools import assert_equals


def test_repr():
    """
    Create a text representation of Attr.
    """
    from attrdict.attr import Attr

    assert_equals(repr(Attr()), 'a{}')
    assert_equals(repr(Attr({'foo': 'bar'})), "a{'foo': 'bar'}")
    assert_equals(repr(Attr({'foo': {1: 2}})), "a{'foo': {1: 2}}")
    assert_equals(repr(Attr({'foo': Attr({1: 2})})), "a{'foo': a{1: 2}}")
