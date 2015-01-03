# encoding: UTF-8
"""
Tests for the AttrDict class.
"""
from sys import version_info

from nose.tools import assert_equals, assert_false


PYTHON_2 = version_info < (3,)


def test_init():
    """
    Create a new AttrDict.
    """
    from attrdict.dictionary import AttrDict

    # empty
    assert_equals(AttrDict(), {})
    assert_equals(AttrDict(()), {})
    assert_equals(AttrDict({}), {})

    # with items
    assert_equals(AttrDict({'foo': 'bar'}), {'foo': 'bar'})
    assert_equals(AttrDict((('foo', 'bar'),)), {'foo': 'bar'})
    assert_equals(AttrDict(foo='bar'), {'foo': 'bar'})

    # non-overlapping
    assert_equals(AttrDict({}, foo='bar'), {'foo': 'bar'})
    assert_equals(AttrDict((), foo='bar'), {'foo': 'bar'})

    assert_equals(
        AttrDict({'alpha': 'bravo'}, foo='bar'),
        {'foo': 'bar', 'alpha': 'bravo'}
    )

    assert_equals(
        AttrDict((('alpha', 'bravo'),), foo='bar'),
        {'foo': 'bar', 'alpha': 'bravo'}
    )

    # updating
    assert_equals(
        AttrDict({'alpha': 'bravo'}, foo='bar', alpha='beta'),
        {'foo': 'bar', 'alpha': 'beta'}
    )

    assert_equals(
        AttrDict((('alpha', 'bravo'), ('alpha', 'beta')), foo='bar'),
        {'foo': 'bar', 'alpha': 'beta'}
    )

    assert_equals(
        AttrDict((('alpha', 'bravo'), ('alpha', 'beta')), alpha='bravo'),
        {'alpha': 'bravo'}
    )


def test_copy():
    """
    Make a dict copy of an AttrDict.
    """
    from attrdict.dictionary import AttrDict

    mapping_a = AttrDict({'foo': {'bar': 'baz'}})
    mapping_b = mapping_a.copy()
    mapping_c = mapping_b

    mapping_b['foo']['lorem'] = 'ipsum'

    assert_equals(mapping_a, mapping_b)
    assert_equals(mapping_b, mapping_c)


def test_fromkeys():
    """
    make a new sequence from a set of keys.
    """
    from attrdict.dictionary import AttrDict

    # default value
    assert_equals(AttrDict.fromkeys(()), {})
    assert_equals(
        AttrDict.fromkeys({'foo': 'bar', 'baz': 'qux'}),
        {'foo': None, 'baz': None}
    )
    assert_equals(
        AttrDict.fromkeys(('foo', 'baz')),
        {'foo': None, 'baz': None}
    )

    # custom value
    assert_equals(AttrDict.fromkeys((), 0), {})
    assert_equals(
        AttrDict.fromkeys({'foo': 'bar', 'baz': 'qux'}, 0),
        {'foo': 0, 'baz': 0}
    )
    assert_equals(
        AttrDict.fromkeys(('foo', 'baz'), 0),
        {'foo': 0, 'baz': 0}
    )


if not PYTHON_2:
    def test_has_key():
        """
        The now-depricated has_keys method
        """
        from attrdict.dictionary import AttrDict

        assert_false(hasattr(AttrDict(), 'has_key'))
