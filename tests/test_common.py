# encoding: UTF-8
"""
Common tests that apply to multiple Attr-derived classes.
"""
import copy
from collections import namedtuple, Mapping, ItemsView, KeysView, ValuesView
from itertools import chain
import pickle
from sys import version_info

from nose.tools import (assert_equals, assert_not_equals,
                        assert_true, assert_false, assert_raises)
import six

from attrdict.mixins import Attr


Options = namedtuple(
    'Options',
    ('cls', 'constructor', 'mutable', 'iter_methods', 'view_methods',
     'recursive')
)


class AttrImpl(Attr):
    """
    An implementation of Attr.
    """
    def __init__(self, items=None, sequence_type=tuple):
        if items is None:
            items = {}
        elif not isinstance(items, Mapping):
            items = dict(items)

        self._mapping = items
        self._sequence_type = sequence_type

    def _configuration(self):
        """
        The configuration for an attrmap instance.
        """
        return self._sequence_type

    def __getitem__(self, key):
        """
        Access a value associated with a key.
        """
        return self._mapping[key]

    def __len__(self):
        """
        Check the length of the mapping.
        """
        return len(self._mapping)

    def __iter__(self):
        """
        Iterated through the keys.
        """
        return iter(self._mapping)

    def __getstate__(self):
        """
        Serialize the object.
        """
        return (self._mapping, self._sequence_type)

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        mapping, sequence_type = state
        self._mapping = mapping
        self._sequence_type = sequence_type

    @classmethod
    def _constructor(cls, mapping, configuration):
        """
        A standardized constructor.
        """
        return cls(mapping, sequence_type=configuration)


def test_attr():
    """
    Tests for an class that implements Attr.
    """
    for test in common(AttrImpl, mutable=False):
        yield test


def test_attrmap():
    """
    Run AttrMap against the common tests.
    """
    from attrdict.mapping import AttrMap

    for test in common(AttrMap, mutable=True):
        yield test


def test_attrdict():
    """
    Run AttrDict against the common tests.
    """
    from attrdict.dictionary import AttrDict

    view_methods = (2, 7) <= version_info < (3,)

    def constructor(items=None, sequence_type=tuple):
        """
        Build a new AttrDict.
        """
        if items is None:
            items = {}

        return AttrDict._constructor(items, sequence_type)

    for test in common(AttrDict, constructor=constructor,
                       mutable=True, iter_methods=True,
                       view_methods=view_methods, recursive=False):
        yield test


def test_attrdefault():
    """
    Run AttrDefault against the common tests.
    """
    from attrdict.default import AttrDefault

    def constructor(items=None, sequence_type=tuple):
        """
        Build a new AttrDefault.
        """
        if items is None:
            items = {}

        return AttrDefault(None, items, sequence_type)

    for test in common(AttrDefault, constructor=constructor, mutable=True):
        yield test


def common(cls, constructor=None, mutable=False, iter_methods=False,
           view_methods=False, recursive=True):
    """
    Iterates over tests common to multiple Attr-derived classes

    cls: The class that is being tested.
    mutable: (optional, False) Whether the object is supposed to be
        mutable.
    iter_methods: (optional, False) Whether the class implements
        iter<keys,values,items> under Python 2.
    view_methods: (optional, False) Whether the class implements
        view<keys,values,items> under Python 2.
    recursive: (optional, True) Whether recursive assignment works.
    """
    tests = (
        item_access, iteration, containment, length, equality,
        item_creation, item_deletion, sequence_typing, addition,
        to_kwargs, pickling,
    )

    mutable_tests = (
        pop, popitem, clear, update, setdefault, copying, deepcopying,
    )

    if constructor is None:
        constructor = cls

    options = Options(cls, constructor, mutable, iter_methods, view_methods,
                      recursive)

    if mutable:
        tests = chain(tests, mutable_tests)

    for test in tests:
        test.description = test.__doc__.format(cls=cls.__name__)

        yield test, options


def item_access(options):
    """Access items in {cls}."""
    mapping = options.constructor(
        {
            'foo': 'bar',
            '_lorem': 'ipsum',
            six.u('👻'): 'boo',
            3: 'three',
            'get': 'not the function',
            'sub': {'alpha': 'bravo'},
            'bytes': b'bytes',
            'tuple': ({'a': 'b'}, 'c'),
            'list': [{'a': 'b'}, {'c': 'd'}],
        }
    )

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
    assert_equals(mapping[six.u('👻')], 'boo')
    if six.PY2:
        assert_raises(UnicodeEncodeError, getattr, mapping, six.u('👻'))
    else:
        assert_raises(AttributeError, getattr, mapping, six.u('👻'))
    assert_equals(mapping(six.u('👻')), 'boo')
    assert_equals(mapping.get(six.u('👻')), 'boo')

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
    assert_true(isinstance(mapping.tuple[0], options.cls))
    assert_true(isinstance(mapping('tuple')[0], options.cls))
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
    assert_true(isinstance(mapping.list[0], options.cls))
    assert_true(isinstance(mapping('list')[0], options.cls))
    assert_true(isinstance(mapping.get('list')[0], dict))

    assert_true(isinstance(mapping['list'][1], dict))
    assert_true(isinstance(mapping.list[1], options.cls))
    assert_true(isinstance(mapping('list')[1], options.cls))
    assert_true(isinstance(mapping.get('list')[1], dict))

    # Nonexistent key
    assert_raises(KeyError, lambda: mapping['fake'])
    assert_raises(AttributeError, lambda: mapping.fake)
    assert_raises(AttributeError, lambda: mapping('fake'))
    assert_equals(mapping.get('fake'), None)
    assert_equals(mapping.get('fake', 'bake'), 'bake')


def iteration(options):
    "Iterate over keys/values/items in {cls}"
    raw = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'bravo'}

    mapping = options.constructor(raw)

    expected_keys = frozenset(('foo', 'lorem', 'alpha'))
    expected_values = frozenset(('bar', 'ipsum', 'bravo'))
    expected_items = frozenset(
        (('foo', 'bar'), ('lorem', 'ipsum'), ('alpha', 'bravo'))
    )

    assert_equals(set(iter(mapping)), expected_keys)

    actual_keys = mapping.keys()
    actual_values = mapping.values()
    actual_items = mapping.items()

    if six.PY2:
        for collection in (actual_keys, actual_values, actual_items):
            assert_true(isinstance(collection, list))

        assert_equals(frozenset(actual_keys), expected_keys)
        assert_equals(frozenset(actual_values), expected_values)
        assert_equals(frozenset(actual_items), expected_items)

        if options.iter_methods:
            actual_keys = mapping.iterkeys()
            actual_values = mapping.itervalues()
            actual_items = mapping.iteritems()

            for iterable in (actual_keys, actual_values, actual_items):
                assert_false(isinstance(iterable, list))

            assert_equals(frozenset(actual_keys), expected_keys)
            assert_equals(frozenset(actual_values), expected_values)
            assert_equals(frozenset(actual_items), expected_items)

        if options.view_methods:
            actual_keys = mapping.viewkeys()
            actual_values = mapping.viewvalues()
            actual_items = mapping.viewitems()

            # These views don't actually extend from collections.*View
            for iterable in (actual_keys, actual_values, actual_items):
                assert_false(isinstance(iterable, list))

            assert_equals(frozenset(actual_keys), expected_keys)
            assert_equals(frozenset(actual_values), expected_values)
            assert_equals(frozenset(actual_items), expected_items)

            # What happens if mapping isn't a dict
            from attrdict.mapping import AttrMap

            mapping = options.constructor(AttrMap(raw))

            actual_keys = mapping.viewkeys()
            actual_values = mapping.viewvalues()
            actual_items = mapping.viewitems()

            # These views don't actually extend from collections.*View
            for iterable in (actual_keys, actual_values, actual_items):
                assert_false(isinstance(iterable, list))

            assert_equals(frozenset(actual_keys), expected_keys)
            assert_equals(frozenset(actual_values), expected_values)
            assert_equals(frozenset(actual_items), expected_items)

    else:  # methods are actually views
        assert_true(isinstance(actual_keys, KeysView))
        assert_equals(frozenset(actual_keys), expected_keys)

        assert_true(isinstance(actual_values, ValuesView))
        assert_equals(frozenset(actual_values), expected_values)

        assert_true(isinstance(actual_items, ItemsView))
        assert_equals(frozenset(actual_items), expected_items)

    # make sure empty iteration works
    assert_equals(tuple(options.constructor().items()), ())


def containment(options):
    "Check whether {cls} contains keys"
    mapping = options.constructor(
        {'foo': 'bar', frozenset((1, 2, 3)): 'abc', 1: 2}
    )
    empty = options.constructor()

    assert_true('foo' in mapping)
    assert_false('foo' in empty)

    assert_true(frozenset((1, 2, 3)) in mapping)
    assert_false(frozenset((1, 2, 3)) in empty)

    assert_true(1 in mapping)
    assert_false(1 in empty)

    assert_false('banana' in mapping)
    assert_false('banana' in empty)


def length(options):
    "Get the length of an {cls} instance"
    assert_equals(len(options.constructor()), 0)
    assert_equals(len(options.constructor({'foo': 'bar'})), 1)
    assert_equals(len(options.constructor({'foo': 'bar', 'baz': 'qux'})), 2)


def equality(options):
    "Equality checks for {cls}"
    empty = {}
    mapping_a = {'foo': 'bar'}
    mapping_b = {'lorem': 'ipsum'}

    constructor = options.constructor

    assert_true(constructor(empty) == empty)
    assert_false(constructor(empty) != empty)
    assert_false(constructor(empty) == mapping_a)
    assert_true(constructor(empty) != mapping_a)
    assert_false(constructor(empty) == mapping_b)
    assert_true(constructor(empty) != mapping_b)

    assert_false(constructor(mapping_a) == empty)
    assert_true(constructor(mapping_a) != empty)
    assert_true(constructor(mapping_a) == mapping_a)
    assert_false(constructor(mapping_a) != mapping_a)
    assert_false(constructor(mapping_a) == mapping_b)
    assert_true(constructor(mapping_a) != mapping_b)

    assert_false(constructor(mapping_b) == empty)
    assert_true(constructor(mapping_b) != empty)
    assert_false(constructor(mapping_b) == mapping_a)
    assert_true(constructor(mapping_b) != mapping_a)
    assert_true(constructor(mapping_b) == mapping_b)
    assert_false(constructor(mapping_b) != mapping_b)

    assert_true(constructor(empty) == constructor(empty))
    assert_false(constructor(empty) != constructor(empty))
    assert_false(constructor(empty) == constructor(mapping_a))
    assert_true(constructor(empty) != constructor(mapping_a))
    assert_false(constructor(empty) == constructor(mapping_b))
    assert_true(constructor(empty) != constructor(mapping_b))

    assert_false(constructor(mapping_a) == constructor(empty))
    assert_true(constructor(mapping_a) != constructor(empty))
    assert_true(constructor(mapping_a) == constructor(mapping_a))
    assert_false(constructor(mapping_a) != constructor(mapping_a))
    assert_false(constructor(mapping_a) == constructor(mapping_b))
    assert_true(constructor(mapping_a) != constructor(mapping_b))

    assert_false(constructor(mapping_b) == constructor(empty))
    assert_true(constructor(mapping_b) != constructor(empty))
    assert_false(constructor(mapping_b) == constructor(mapping_a))
    assert_true(constructor(mapping_b) != constructor(mapping_a))
    assert_true(constructor(mapping_b) == constructor(mapping_b))
    assert_false(constructor(mapping_b) != constructor(mapping_b))

    assert_true(constructor((('foo', 'bar'),)) == {'foo': 'bar'})


def item_creation(options):
    "Add a key-value pair to an {cls}"

    if not options.mutable:
        # Assignment shouldn't add to the dict
        mapping = options.constructor()

        try:
            mapping.foo = 'bar'
        except TypeError:
            pass  # may fail if setattr modified
        else:
            pass  # may assign, but shouldn't assign to dict

        def item():
            """
            Attempt to add an item.
            """
            mapping['foo'] = 'bar'

        assert_raises(TypeError, item)

        assert_false('foo' in mapping)
    else:
        mapping = options.constructor()

        # key that can be an attribute
        mapping.foo = 'bar'

        assert_equals(mapping.foo, 'bar')
        assert_equals(mapping['foo'], 'bar')
        assert_equals(mapping('foo'), 'bar')
        assert_equals(mapping.get('foo'), 'bar')

        mapping['baz'] = 'qux'

        assert_equals(mapping.baz, 'qux')
        assert_equals(mapping['baz'], 'qux')
        assert_equals(mapping('baz'), 'qux')
        assert_equals(mapping.get('baz'), 'qux')

        # key that cannot be an attribute
        assert_raises(TypeError, setattr, mapping, 1, 'one')

        assert_true(1 not in mapping)

        mapping[2] = 'two'

        assert_equals(mapping[2], 'two')
        assert_equals(mapping(2), 'two')
        assert_equals(mapping.get(2), 'two')

        # key that represents a hidden attribute
        def add_foo():
            "add _foo to mapping"
            mapping._foo = '_bar'

        assert_raises(TypeError, add_foo)
        assert_false('_foo' in mapping)

        mapping['_baz'] = 'qux'

        def get_baz():
            "get the _foo attribute"
            return mapping._baz

        assert_raises(AttributeError, get_baz)
        assert_equals(mapping['_baz'], 'qux')
        assert_equals(mapping('_baz'), 'qux')
        assert_equals(mapping.get('_baz'), 'qux')

        # key that represents an attribute that already exists
        def add_get():
            "add get to mapping"
            mapping.get = 'attribute'

        assert_raises(TypeError, add_get)
        assert_false('get' in mapping)

        mapping['get'] = 'value'

        assert_not_equals(mapping.get, 'value')
        assert_equals(mapping['get'], 'value')
        assert_equals(mapping('get'), 'value')
        assert_equals(mapping.get('get'), 'value')

        # rewrite a value
        mapping.foo = 'manchu'

        assert_equals(mapping.foo, 'manchu')
        assert_equals(mapping['foo'], 'manchu')
        assert_equals(mapping('foo'), 'manchu')
        assert_equals(mapping.get('foo'), 'manchu')

        mapping['bar'] = 'bell'

        assert_equals(mapping.bar, 'bell')
        assert_equals(mapping['bar'], 'bell')
        assert_equals(mapping('bar'), 'bell')
        assert_equals(mapping.get('bar'), 'bell')

        if options.recursive:
            recursed = options.constructor({'foo': {'bar': 'baz'}})

            recursed.foo.bar = 'qux'
            recursed.foo.alpha = 'bravo'

            assert_equals(recursed, {'foo': {'bar': 'qux', 'alpha': 'bravo'}})


def item_deletion(options):
    "Remove a key-value from to an {cls}"
    if not options.mutable:
        mapping = options.constructor({'foo': 'bar'})

        # could be a TypeError or an AttributeError
        try:
            del mapping.foo
        except TypeError:
            pass
        except AttributeError:
            pass
        else:
            raise AssertionError('deletion should fail')

        def item(mapping):
            """
            Attempt to del an item
            """
            del mapping['foo']

        assert_raises(TypeError, item, mapping)

        assert_equals(mapping, {'foo': 'bar'})
        assert_equals(mapping.foo, 'bar')
        assert_equals(mapping['foo'], 'bar')
    else:
        mapping = options.constructor(
            {'foo': 'bar', 'lorem': 'ipsum', '_hidden': True, 'get': 'value'}
        )

        del mapping.foo
        assert_false('foo' in mapping)

        del mapping['lorem']
        assert_false('lorem' in mapping)

        def del_hidden():
            "delete _hidden"
            del mapping._hidden

        try:
            del_hidden()
        except KeyError:
            pass
        except TypeError:
            pass
        else:
            assert_false("Test raised the appropriate exception")
        # assert_raises(TypeError, del_hidden)
        assert_true('_hidden' in mapping)

        del mapping['_hidden']
        assert_false('hidden' in mapping)

        def del_get():
            "delete get"
            del mapping.get

        assert_raises(TypeError, del_get)
        assert_true('get' in mapping)
        assert_true(mapping.get('get'), 'value')

        del mapping['get']
        assert_false('get' in mapping)
        assert_true(mapping.get('get', 'banana'), 'banana')


def sequence_typing(options):
    "Does {cls} respect sequence type?"
    data = {'list': [{'foo': 'bar'}], 'tuple': ({'foo': 'bar'},)}

    tuple_mapping = options.constructor(data)

    assert_true(isinstance(tuple_mapping.list, tuple))
    assert_equals(tuple_mapping.list[0].foo, 'bar')

    assert_true(isinstance(tuple_mapping.tuple, tuple))
    assert_equals(tuple_mapping.tuple[0].foo, 'bar')

    list_mapping = options.constructor(data, sequence_type=list)

    assert_true(isinstance(list_mapping.list, list))
    assert_equals(list_mapping.list[0].foo, 'bar')

    assert_true(isinstance(list_mapping.tuple, list))
    assert_equals(list_mapping.tuple[0].foo, 'bar')

    none_mapping = options.constructor(data, sequence_type=None)

    assert_true(isinstance(none_mapping.list, list))
    assert_raises(AttributeError, lambda: none_mapping.list[0].foo)

    assert_true(isinstance(none_mapping.tuple, tuple))
    assert_raises(AttributeError, lambda: none_mapping.tuple[0].foo)


def addition(options):
    "Adding {cls} to other mappings."
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

    constructor = options.constructor

    assert_raises(TypeError, lambda: constructor() + 1)
    assert_raises(TypeError, lambda: 1 + constructor())

    assert_equals(constructor() + constructor(), {})
    assert_equals(constructor() + {}, {})
    assert_equals({} + constructor(), {})

    assert_equals(constructor(left) + constructor(), left)
    assert_equals(constructor(left) + {}, left)
    assert_equals({} + constructor(left), left)

    assert_equals(constructor() + constructor(left), left)
    assert_equals(constructor() + left, left)
    assert_equals(left + constructor(), left)

    assert_equals(constructor(left) + constructor(right), merged)
    assert_equals(constructor(left) + right, merged)
    assert_equals(left + constructor(right), merged)

    assert_equals(constructor(right) + constructor(left), opposite)
    assert_equals(constructor(right) + left, opposite)
    assert_equals(right + constructor(left), opposite)

    # test sequence type changes
    data = {'sequence': [{'foo': 'bar'}]}

    assert_true(isinstance((constructor(data) + {}).sequence, tuple))
    assert_true(
        isinstance((constructor(data) + constructor()).sequence, tuple)
    )

    assert_true(isinstance((constructor(data, list) + {}).sequence, list))
    # assert_true(
    #     isinstance((constructor(data, list) + constructor()).sequence, tuple)
    # )

    assert_true(isinstance((constructor(data, list) + {}).sequence, list))
    assert_true(
        isinstance(
            (constructor(data, list) + constructor({}, list)).sequence,
            list
        )
    )


def to_kwargs(options):
    "**{cls}"
    def return_results(**kwargs):
        "Return result passed into a function"
        return kwargs

    expected = {'foo': 1, 'bar': 2}

    assert_equals(return_results(**options.constructor()), {})
    assert_equals(return_results(**options.constructor(expected)), expected)


def check_pickle_roundtrip(source, options, **kwargs):
    """
    serialize then deserialize a mapping, ensuring the result and initial
    objects are equivalent.
    """
    source = options.constructor(source, **kwargs)
    data = pickle.dumps(source)
    loaded = pickle.loads(data)

    assert_true(isinstance(loaded, options.cls))

    assert_equals(source, loaded)

    return loaded


def pickling(options):
    "Pickle {cls}"

    empty = check_pickle_roundtrip(None, options)
    assert_equals(empty, {})

    mapping = check_pickle_roundtrip({'foo': 'bar'}, options)
    assert_equals(mapping, {'foo': 'bar'})

    # make sure sequence_type is preserved
    raw = {'list': [{'a': 'b'}], 'tuple': ({'a': 'b'},)}

    as_tuple = check_pickle_roundtrip(raw, options)
    assert_true(isinstance(as_tuple['list'], list))
    assert_true(isinstance(as_tuple['tuple'], tuple))
    assert_true(isinstance(as_tuple.list, tuple))
    assert_true(isinstance(as_tuple.tuple, tuple))

    as_list = check_pickle_roundtrip(raw, options, sequence_type=list)
    assert_true(isinstance(as_list['list'], list))
    assert_true(isinstance(as_list['tuple'], tuple))
    assert_true(isinstance(as_list.list, list))
    assert_true(isinstance(as_list.tuple, list))

    as_raw = check_pickle_roundtrip(raw, options, sequence_type=None)
    assert_true(isinstance(as_raw['list'], list))
    assert_true(isinstance(as_raw['tuple'], tuple))
    assert_true(isinstance(as_raw.list, list))
    assert_true(isinstance(as_raw.tuple, tuple))


def pop(options):
    "Popping from {cls}"

    mapping = options.constructor({'foo': 'bar', 'baz': 'qux'})

    assert_raises(KeyError, lambda: mapping.pop('lorem'))
    assert_equals(mapping.pop('lorem', 'ipsum'), 'ipsum')
    assert_equals(mapping, {'foo': 'bar', 'baz': 'qux'})

    assert_equals(mapping.pop('baz'), 'qux')
    assert_false('baz' in mapping)
    assert_equals(mapping, {'foo': 'bar'})

    assert_equals(mapping.pop('foo', 'qux'), 'bar')
    assert_false('foo' in mapping)
    assert_equals(mapping, {})


def popitem(options):
    "Popping items from {cls}"
    expected = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'beta'}
    actual = {}

    mapping = options.constructor(dict(expected))

    for _ in range(3):
        key, value = mapping.popitem()

        assert_equals(expected[key], value)
        actual[key] = value

    assert_equals(expected, actual)

    assert_raises(AttributeError, lambda: mapping.foo)
    assert_raises(AttributeError, lambda: mapping.lorem)
    assert_raises(AttributeError, lambda: mapping.alpha)
    assert_raises(KeyError, mapping.popitem)


def clear(options):
    "clear the {cls}"

    mapping = options.constructor(
        {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'beta'}
    )

    mapping.clear()

    assert_equals(mapping, {})

    assert_raises(AttributeError, lambda: mapping.foo)
    assert_raises(AttributeError, lambda: mapping.lorem)
    assert_raises(AttributeError, lambda: mapping.alpha)


def update(options):
    "update a {cls}"

    mapping = options.constructor({'foo': 'bar', 'alpha': 'bravo'})

    mapping.update(alpha='beta', lorem='ipsum')
    assert_equals(mapping, {'foo': 'bar', 'alpha': 'beta', 'lorem': 'ipsum'})

    mapping.update({'foo': 'baz', 1: 'one'})
    assert_equals(
        mapping,
        {'foo': 'baz', 'alpha': 'beta', 'lorem': 'ipsum', 1: 'one'}
    )

    assert_equals(mapping.foo, 'baz')
    assert_equals(mapping.alpha, 'beta')
    assert_equals(mapping.lorem, 'ipsum')
    assert_equals(mapping(1), 'one')


def setdefault(options):
    "{cls}.setdefault"

    mapping = options.constructor({'foo': 'bar'})

    assert_equals(mapping.setdefault('foo', 'baz'), 'bar')
    assert_equals(mapping.foo, 'bar')

    assert_equals(mapping.setdefault('lorem', 'ipsum'), 'ipsum')
    assert_equals(mapping.lorem, 'ipsum')

    assert_true(mapping.setdefault('return_none') is None)
    assert_true(mapping.return_none is None)

    assert_equals(mapping.setdefault(1, 'one'), 'one')
    assert_equals(mapping[1], 'one')

    assert_equals(mapping.setdefault('_hidden', 'yes'), 'yes')
    assert_raises(AttributeError, lambda: mapping._hidden)
    assert_equals(mapping['_hidden'], 'yes')

    assert_equals(mapping.setdefault('get', 'value'), 'value')
    assert_not_equals(mapping.get, 'value')
    assert_equals(mapping['get'], 'value')


def copying(options):
    "copying a {cls}"
    mapping_a = options.constructor({'foo': {'bar': 'baz'}})
    mapping_b = copy.copy(mapping_a)
    mapping_c = mapping_b

    mapping_b.foo.lorem = 'ipsum'

    assert_equals(mapping_a, mapping_b)
    assert_equals(mapping_b, mapping_c)

    mapping_c.alpha = 'bravo'


def deepcopying(options):
    "deepcopying a {cls}"
    mapping_a = options.constructor({'foo': {'bar': 'baz'}})
    mapping_b = copy.deepcopy(mapping_a)
    mapping_c = mapping_b

    mapping_b['foo']['lorem'] = 'ipsum'

    assert_not_equals(mapping_a, mapping_b)
    assert_equals(mapping_b, mapping_c)

    mapping_c.alpha = 'bravo'

    assert_not_equals(mapping_a, mapping_b)
    assert_equals(mapping_b, mapping_c)

    assert_false('lorem' in mapping_a.foo)
    assert_equals(mapping_a.setdefault('alpha', 'beta'), 'beta')
    assert_equals(mapping_c.alpha, 'bravo')
