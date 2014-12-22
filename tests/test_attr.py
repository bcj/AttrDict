# encoding: UTF-8
"""
Tests for the Attr class.
"""
from collections import defaultdict
from copy import copy, deepcopy
import pickle
from sys import version_info

from nose.tools import (assert_equals, assert_not_equals,
                        assert_true, assert_false, assert_raises)


PYTHON_2 = version_info < (3,)


def test_attr_access():
    """
    Test that Attr can be accessed
    """
    from attrdict.attr import Attr

    mapping = Attr({
        'foo': 'bar',
        '_lorem': 'ipsum',
        u'👻': 'boo',
        3: 'three',
        'get': 'not the function',
        'sub': {'alpha': 'bravo'},
        'bytes': b'bytes',
        'tuple': ({'a': 'b'}, 'c'),
        'list': [{'a': 'b'}, {'c': 'd'}],
    })

    # key that can be an attribute
    assert_equals(mapping['foo'], 'bar')
    assert_equals(mapping.foo, 'bar')
    assert_equals(mapping('foo'), 'bar')
    assert_equals(mapping.get('foo'), 'bar')

    # key that cannot be an attribute
    assert_equals(mapping[3], 'three')
    assert_raises(TypeError, getattr, mapping, 3)
    assert_equals(mapping(3), 'three')
    assert_equals(mapping.get(3), 'three')

    # key that cannot be an attribute (sadly)
    assert_equals(mapping[u'👻'], 'boo')
    if PYTHON_2:
        assert_raises(UnicodeEncodeError, getattr, mapping, u'👻')
    else:
        assert_raises(AttributeError, getattr, mapping, u'👻')
    assert_equals(mapping(u'👻'), 'boo')
    assert_equals(mapping.get(u'👻'), 'boo')

    # key that represents a hidden attribute
    assert_equals(mapping['_lorem'], 'ipsum')
    assert_raises(AttributeError, lambda: mapping._lorem)
    assert_equals(mapping('_lorem'), 'ipsum')
    assert_equals(mapping.get('_lorem'), 'ipsum')

    # key that represents an attribute that already exists
    assert_equals(mapping['get'], 'not the function')
    assert_not_equals(mapping.get, 'not the function')
    assert_equals(mapping('get'), 'not the function')
    assert_equals(mapping.get('get'), 'not the function')

    # does recursion work
    assert_raises(AttributeError, lambda: mapping['sub'].alpha)
    assert_equals(mapping.sub.alpha, 'bravo')
    assert_equals(mapping('sub').alpha, 'bravo')
    assert_raises(AttributeError, lambda: mapping.get('sub').alpha)

    # bytes
    assert_equals(mapping['bytes'], b'bytes')
    assert_equals(mapping.bytes, b'bytes')
    assert_equals(mapping('bytes'), b'bytes')
    assert_equals(mapping.get('bytes'), b'bytes')

    # tuple
    assert_equals(mapping['tuple'], ({'a': 'b'}, 'c'))
    assert_equals(mapping.tuple, ({'a': 'b'}, 'c'))
    assert_equals(mapping('tuple'), ({'a': 'b'}, 'c'))
    assert_equals(mapping.get('tuple'), ({'a': 'b'}, 'c'))

    assert_raises(AttributeError, lambda: mapping['tuple'][0].a)
    assert_equals(mapping.tuple[0].a, 'b')
    assert_equals(mapping('tuple')[0].a, 'b')
    assert_raises(AttributeError, lambda: mapping.get('tuple')[0].a)

    assert_true(isinstance(mapping['tuple'], tuple))
    assert_true(isinstance(mapping.tuple, tuple))
    assert_true(isinstance(mapping('tuple'), tuple))
    assert_true(isinstance(mapping.get('tuple'), tuple))

    assert_true(isinstance(mapping['tuple'][0], dict))
    assert_true(isinstance(mapping.tuple[0], Attr))
    assert_true(isinstance(mapping('tuple')[0], Attr))
    assert_true(isinstance(mapping.get('tuple')[0], dict))

    assert_true(isinstance(mapping['tuple'][1], str))
    assert_true(isinstance(mapping.tuple[1], str))
    assert_true(isinstance(mapping('tuple')[1], str))
    assert_true(isinstance(mapping.get('tuple')[1], str))

    # list
    assert_equals(mapping['list'], [{'a': 'b'}, {'c': 'd'}])
    assert_equals(mapping.list, ({'a': 'b'}, {'c': 'd'}))
    assert_equals(mapping('list'), ({'a': 'b'}, {'c': 'd'}))
    assert_equals(mapping.get('list'), [{'a': 'b'}, {'c': 'd'}])

    assert_raises(AttributeError, lambda: mapping['list'][0].a)
    assert_equals(mapping.list[0].a, 'b')
    assert_equals(mapping('list')[0].a, 'b')
    assert_raises(AttributeError, lambda: mapping.get('list')[0].a)

    assert_true(isinstance(mapping['list'], list))
    assert_true(isinstance(mapping.list, tuple))
    assert_true(isinstance(mapping('list'), tuple))
    assert_true(isinstance(mapping.get('list'), list))

    assert_true(isinstance(mapping['list'][0], dict))
    assert_true(isinstance(mapping.list[0], Attr))
    assert_true(isinstance(mapping('list')[0], Attr))
    assert_true(isinstance(mapping.get('list')[0], dict))

    assert_true(isinstance(mapping['list'][1], dict))
    assert_true(isinstance(mapping.list[1], Attr))
    assert_true(isinstance(mapping('list')[1], Attr))
    assert_true(isinstance(mapping.get('list')[1], dict))

    # Nonexistent key
    assert_raises(KeyError, lambda: mapping['fake'])
    assert_raises(AttributeError, lambda: mapping.fake)
    assert_raises(AttributeError, lambda: mapping('fake'))
    assert_equals(mapping.get('fake'), None)
    assert_equals(mapping.get('fake', 'bake'), 'bake')


def test_iteration():
    """
    Test the various iteration functions.
    """
    from attrdict.attr import Attr

    raw = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'bravo'}

    mapping = Attr(raw)

    for expected, actual in zip(raw, mapping):
        assert_equals(expected, actual)

    for expected, actual in zip(raw.keys(), mapping.keys()):
        assert_equals(expected, actual)

    for expected, actual in zip(raw.values(), mapping.values()):
        assert_equals(expected, actual)

    for expected, actual in zip(raw.items(), mapping.items()):
        assert_equals(expected, actual)

    assert_equals(list(Attr().items()), [])


def test_contains():
    """
    Test that contains works.
    """
    from attrdict.attr import Attr

    mapping = Attr({'foo': 'bar', frozenset((1, 2, 3)): 'abc', 1: 2})
    empty = Attr()

    assert_true('foo' in mapping)
    assert_false('foo' in empty)
    assert_true(frozenset((1, 2, 3)) in mapping)
    assert_false(frozenset((1, 2, 3)) in empty)
    assert_true(1 in mapping)
    assert_false(1 in empty)
    assert_false('banana' in mapping)
    assert_false('banana' in empty)


def test_len():
    """
    Test that length works.
    """
    from attrdict.attr import Attr

    assert_equals(len(Attr()), 0)
    assert_equals(len(Attr({'foo': 'bar'})), 1)
    assert_equals(len(Attr({'foo': 'bar', 'lorem': 'ipsum'})), 2)


def test_equality():
    """
    Test that equality works.
    """
    from attrdict.attr import Attr

    empty = {}
    dict_a = {'foo': 'bar'}
    dict_b = {'lorem': 'ipsum'}

    assert_true(Attr(empty) == empty)
    assert_false(Attr(empty) != empty)
    assert_false(Attr(empty) == dict_a)
    assert_true(Attr(empty) != dict_a)
    assert_false(Attr(empty) == dict_b)
    assert_true(Attr(empty) != dict_b)

    assert_false(Attr(dict_a) == empty)
    assert_true(Attr(dict_a) != empty)
    assert_true(Attr(dict_a) == dict_a)
    assert_false(Attr(dict_a) != dict_a)
    assert_false(Attr(dict_a) == dict_b)
    assert_true(Attr(dict_a) != dict_b)

    assert_false(Attr(dict_b) == empty)
    assert_true(Attr(dict_b) != empty)
    assert_false(Attr(dict_b) == dict_a)
    assert_true(Attr(dict_b) != dict_a)
    assert_true(Attr(dict_b) == dict_b)
    assert_false(Attr(dict_b) != dict_b)

    assert_true(Attr(empty) == Attr(empty))
    assert_false(Attr(empty) != Attr(empty))
    assert_false(Attr(empty) == Attr(dict_a))
    assert_true(Attr(empty) != Attr(dict_a))
    assert_false(Attr(empty) == Attr(dict_b))
    assert_true(Attr(empty) != Attr(dict_b))

    assert_false(Attr(dict_a) == Attr(empty))
    assert_true(Attr(dict_a) != Attr(empty))
    assert_true(Attr(dict_a) == Attr(dict_a))
    assert_false(Attr(dict_a) != Attr(dict_a))
    assert_false(Attr(dict_a) == Attr(dict_b))
    assert_true(Attr(dict_a) != Attr(dict_b))

    assert_false(Attr(dict_b) == Attr(empty))
    assert_true(Attr(dict_b) != Attr(empty))
    assert_false(Attr(dict_b) == Attr(dict_a))
    assert_true(Attr(dict_b) != Attr(dict_a))
    assert_true(Attr(dict_b) == Attr(dict_b))
    assert_false(Attr(dict_b) != Attr(dict_b))

    assert_true(Attr((('foo', 'bar'),)) == {'foo': 'bar'})


def test_set():
    """
    Test that attributes can't be set.
    """
    from attrdict.attr import Attr

    def attribute():
        "Attempt to add an attribute"
        Attr().foo = 'bar'

    def item():
        "Attempt to add an item"
        Attr()['foo'] = 'bar'

    assert_raises(TypeError, attribute)
    assert_raises(TypeError, item)


def test_del():
    """
    Test that attributes can't be deleted.
    """
    from attrdict.attr import Attr

    attr = Attr({'foo': 'bar'})

    def attribute(attr):
        "Attempt to del an attribute"
        del attr.foo

    def item(attr):
        "Attempt to del an item"
        del attr['foo']

    assert_raises(TypeError, attribute, attr)
    assert_raises(TypeError, item, attr)

    assert_equals(attr, {'foo': 'bar'})
    assert_equals(attr.foo, 'bar')
    assert_equals(attr['foo'], 'bar')


def test_sequence_type():
    """
    Test that sequence_type is respected.
    """
    from attrdict.attr import Attr

    mapping = {'list': [{'foo': 'bar'}], 'tuple': ({'foo': 'bar'},)}

    tuple_attr = Attr(mapping)

    assert_true(isinstance(tuple_attr.list, tuple))
    assert_equals(tuple_attr.list[0].foo, 'bar')

    assert_true(isinstance(tuple_attr.tuple, tuple))
    assert_equals(tuple_attr.tuple[0].foo, 'bar')

    list_attr = Attr(mapping, sequence_type=list)

    assert_true(isinstance(list_attr.list, list))
    assert_equals(list_attr.list[0].foo, 'bar')

    assert_true(isinstance(list_attr.tuple, list))
    assert_equals(list_attr.tuple[0].foo, 'bar')

    none_attr = Attr(mapping, sequence_type=None)

    assert_true(isinstance(none_attr.list, list))
    assert_raises(AttributeError, lambda: none_attr.list[0].foo)

    assert_true(isinstance(none_attr.tuple, tuple))
    assert_raises(AttributeError, lambda: none_attr.tuple[0].foo)


def test_add():
    """
    Test that adding works.
    """
    from attrdict.attr import Attr

    left = {
        'foo': 'bar',
        'mismatch': False,
        'sub': {'alpha': 'beta', 'a': 'b'},
    }

    right = {
        'lorem': 'ipsum',
        'mismatch': True,
        'sub': {'alpha': 'bravo', 'c': 'd'},
    }

    merged = {
        'foo': 'bar',
        'lorem': 'ipsum',
        'mismatch': True,
        'sub': {'alpha': 'bravo', 'a': 'b', 'c': 'd'}
    }

    opposite = {
        'foo': 'bar',
        'lorem': 'ipsum',
        'mismatch': False,
        'sub': {'alpha': 'beta', 'a': 'b', 'c': 'd'}
    }

    assert_raises(TypeError, lambda: Attr() + 1)

    assert_equals(Attr() + Attr(), {})
    assert_equals(Attr() + {}, {})
    assert_equals({} + Attr(), {})

    assert_equals(Attr(left) + Attr(), left)
    assert_equals(Attr(left) + {}, left)
    assert_equals({} + Attr(left), left)

    assert_equals(Attr() + Attr(left), left)
    assert_equals(Attr() + left, left)
    assert_equals(left + Attr(), left)

    assert_equals(Attr(left) + Attr(right), merged)
    assert_equals(Attr(left) + right, merged)
    assert_equals(left + Attr(right), merged)

    assert_equals(Attr(right) + Attr(left), opposite)
    assert_equals(Attr(right) + left, opposite)
    assert_equals(right + Attr(left), opposite)

    # test sequence type changes
    data = {'sequence': [{'foo': 'bar'}]}

    assert_true(isinstance((Attr(data) + {}).sequence, tuple))
    assert_true(isinstance((Attr(data) + Attr()).sequence, tuple))

    assert_true(isinstance((Attr(data, list) + {}).sequence, list))
    assert_true(isinstance((Attr(data, list) + Attr()).sequence, tuple))

    assert_true(isinstance((Attr(data, list) + {}).sequence, list))
    assert_true(isinstance((Attr(data, list) + Attr({}, list)).sequence, list))


def test_kwargs():
    """
    Test that ** works
    """
    from attrdict.attr import Attr

    def return_results(**kwargs):
        """Return result passed into a function"""
        return kwargs

    expected = {'foo': 1, 'bar': 2}

    assert_equals(return_results(**Attr()), {})
    assert_equals(return_results(**Attr(expected)), expected)


def test_repr():
    """
    Test that repr works appropriately.
    """
    from attrdict.attr import Attr

    assert_equals(repr(Attr()), 'a{}')
    assert_equals(repr(Attr({'foo': 'bar'})), "a{'foo': 'bar'}")
    assert_equals(repr(Attr({'foo': {1: 2}})), "a{'foo': {1: 2}}")
    assert_equals(repr(Attr({'foo': Attr({1: 2})})), "a{'foo': a{1: 2}}")


def test_subclassability():
    """
    Test that attr doesn't break subclassing.
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


def _check_pickle_roundtrip(source, **kwargs):
    """
    serialize then deserialize an Attr, ensuring the result and initial
    objects are equivalent.
    """
    from attrdict.attr import Attr

    source = Attr(source, **kwargs)
    data = pickle.dumps(source)
    loaded = pickle.loads(data)

    assert_true(isinstance(loaded, Attr))

    assert_equals(source, loaded)

    return loaded


def test_pickle():
    """
    Test that Attr can be pickled
    """
    empty = _check_pickle_roundtrip(None)
    assert_equals(empty, {})

    mapping = _check_pickle_roundtrip({'foo': 'bar'})
    assert_equals(mapping, {'foo': 'bar'})

    # make sure sequence_type is preserved
    raw = {'list': [{'a': 'b'}], 'tuple': ({'a': 'b'},)}

    as_tuple = _check_pickle_roundtrip(raw)
    assert_true(isinstance(as_tuple['list'], list))
    assert_true(isinstance(as_tuple['tuple'], tuple))
    assert_true(isinstance(as_tuple.list, tuple))
    assert_true(isinstance(as_tuple.tuple, tuple))

    as_list = _check_pickle_roundtrip(raw, sequence_type=list)
    assert_true(isinstance(as_list['list'], list))
    assert_true(isinstance(as_list['tuple'], tuple))
    assert_true(isinstance(as_list.list, list))
    assert_true(isinstance(as_list.tuple, list))

    as_raw = _check_pickle_roundtrip(raw, sequence_type=None)
    assert_true(isinstance(as_raw['list'], list))
    assert_true(isinstance(as_raw['tuple'], tuple))
    assert_true(isinstance(as_raw.list, list))
    assert_true(isinstance(as_raw.tuple, tuple))
