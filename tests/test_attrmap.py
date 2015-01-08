"""
Tests for the AttrMap class.
"""
from nose.tools import assert_equals


def test_repr():
    """
    repr(AttrMap)
    """
    from attrdict.mapping import AttrMap

    assert_equals(repr(AttrMap()), "a{}")
    assert_equals(repr(AttrMap({'foo': 'bar'})), "a{'foo': 'bar'}")
    assert_equals(repr(AttrMap({1: {'foo': 'bar'}})), "a{1: {'foo': 'bar'}}")
    assert_equals(
        repr(AttrMap({1: AttrMap({'foo': 'bar'})})),
        "a{1: a{'foo': 'bar'}}"
    )
