"""
Tests for depricated methods.
"""
from sys import version_info

from nose.tools import assert_true, assert_false


PYTHON_2 = version_info < (3,)


if PYTHON_2:
    def test_has_key():
        """
        The now-depricated has_keys method
        """
        from attrdict.attrdictionary import AttrDict

        mapping = AttrDict(
            {'foo': 'bar', frozenset((1, 2, 3)): 'abc', 1: 2}
        )
        empty = AttrDict()

        assert_true(mapping.has_key('foo'))
        assert_false(empty.has_key('foo'))

        assert_true(mapping.has_key(frozenset((1, 2, 3))))
        assert_false(empty.has_key(frozenset((1, 2, 3))))

        assert_true(mapping.has_key(1))
        assert_false(empty.has_key(1))

        assert_false(mapping.has_key('banana'))
        assert_false(empty.has_key('banana'))
