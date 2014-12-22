# encoding: UTF-8
"""
Tests for the two_three submodule.
"""
from sys import version_info

from nose.tools import assert_equals, assert_true


PYTHON_2 = version_info < (3,)


def test_python_2_flag():
    """
    Test the PYTHON_2 flag.
    """
    from attrdict import two_three

    assert_equals(two_three.PYTHON_2, PYTHON_2)


def test_string_type():
    """
    Test the StringType type.
    """
    from attrdict.two_three import StringType

    assert_true(isinstance('string', StringType))
    assert_true(isinstance(u'👻', StringType))


def test_iteritems():
    """
    Test the two_three.iteritems method.
    """
    from attrdict.two_three import iteritems

    mapping = {'foo': 'bar', '_lorem': '_ipsum'}

    # make sure it gives all the items
    actual = {}
    for key, value in iteritems(mapping):
        actual[key] = value

    assert_equals(actual, mapping)

    # make sure that iteritems is being used under Python 2
    if PYTHON_2:
        class MockMapping(object):
            "A mapping that doesn't implement items"
            def __init__(self, value):
                self.value = value

            def iteritems(self):
                "The only way to get items"
                return self.value

        assert_equals(
            iteritems(MockMapping({'test': 'passed'})), {'test': 'passed'}
        )
