# encoding: UTF-8
"""
Tests for the two_three submodule.
"""
from sys import version_info

from nose.tools import assert_equals, assert_true


PYTHON_2 = version_info < (3,)


def test_python_2_flag():
    """
    PYTHON_2 flag.
    """
    from attrdict import two_three

    assert_equals(two_three.PYTHON_2, PYTHON_2)


def test_string_type():
    """
    StringType type.
    """
    from attrdict.two_three import StringType

    assert_true(isinstance('string', StringType))
    assert_true(isinstance(u'👻', StringType))
