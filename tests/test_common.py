# encoding: UTF-8
"""
Common tests that apply to multiple Attr-derived classes.
"""
import pickle
from sys import version_info

from nose.tools import (assert_equals, assert_not_equals,
                        assert_true, assert_false, assert_raises)

PYTHON_2 = version_info < (3,)


def test_attr():
    """
    Run Attr against the common tests.
    """
    from attrdict.attr import Attr

    options = {
        'class': Attr,
        'mutable': False,
        'method_missing': False,
        'iter_methods': False
    }

    for test, description in common():
        test.description = description.format(cls='Attr')
        yield test, Attr, options


def test_mutableattr():
    """
    Run MutableAttr against the common tests.
    """
    from attrdict.mutableattr import MutableAttr

    options = {
        'class': MutableAttr,
        'mutable': True,
        'method_missing': False,
        'iter_methods': False
    }

    for test, description in common():
        test.description = description.format(cls='MutableAttr')
        yield test, MutableAttr, options


def common():
    """
    Iterates over tests common to multiple Attr-derived classes.

    To run the tests:
    for test, description in common()
        test.description = description.format(cls=YOUR_CLASS_NAME)
        yield test, constructor, options

    constructor should accept 0–1 positional parameters, as well as the
        named parameter sequence_type.

    options:
        cls: (optional, constructor) The actual class.
        mutable: (optional, False) Are constructed instances mutable
        method_missing: (optional, False) Is there defaultdict support?
        iter_methodsf: (optional, False) Under Python2, are
            iter<keys, values, items> methods defined?
    """
    tests = (
        item_access, iteration, containment, length, equality,
        item_creation, item_deletion, sequence_type, addition,
        to_kwargs, pickleing
    )

    for test in tests:
        yield test, test.__doc__


def item_access(constructor, options=None):
    "Access items in {cls}."

    if options is None:
        options = {}

    cls = options.get('class', constructor)
    method_missing = options.get('method_missing', False)

    mapping = constructor(
        {
            'foo': 'bar',
            '_lorem': 'ipsum',
            u'👻': 'boo',
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
    assert_true(isinstance(mapping.tuple[0], cls))
    assert_true(isinstance(mapping('tuple')[0], cls))
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
    assert_true(isinstance(mapping.list[0], cls))
    assert_true(isinstance(mapping('list')[0], cls))
    assert_true(isinstance(mapping.get('list')[0], dict))

    assert_true(isinstance(mapping['list'][1], dict))
    assert_true(isinstance(mapping.list[1], cls))
    assert_true(isinstance(mapping('list')[1], cls))
    assert_true(isinstance(mapping.get('list')[1], dict))

    # Nonexistent key
    if not method_missing:
        assert_raises(KeyError, lambda: mapping['fake'])
        assert_raises(AttributeError, lambda: mapping.fake)
        assert_raises(AttributeError, lambda: mapping('fake'))
        assert_equals(mapping.get('fake'), None)
        assert_equals(mapping.get('fake', 'bake'), 'bake')


def iteration(constructor, options=None):
    "Iterate over keys/values/items in {cls}"
    if options is None:
        options = {}

    iter_methods = options.get('iter_methods', False)

    raw = {'foo': 'bar', 'lorem': 'ipsum', 'alpha': 'bravo'}

    mapping = constructor(raw)

    expected_keys = frozenset(('foo', 'lorem', 'alpha'))
    expected_values = frozenset(('bar', 'ipsum', 'bravo'))
    expected_items = frozenset(
        (('foo', 'bar'), ('lorem', 'ipsum'), ('alpha', 'bravo'))
    )

    assert_equals(set(iter(mapping)), expected_keys)

    actual_keys = mapping.keys()
    actual_values = mapping.values()
    actual_items = mapping.items()

    if PYTHON_2:
        for collection in (actual_keys, actual_values, actual_items):
            assert_true(isinstance(collection, list))

        assert_equals(frozenset(actual_keys), expected_keys)
        assert_equals(frozenset(actual_values), expected_values)
        assert_equals(frozenset(actual_items), expected_items)

        if iter_methods:
            actual_keys = mapping.iterkeys()
            actual_values = mapping.itervalues()
            actual_items = mapping.iteritems()

            for iterable in (actual_keys, actual_values, actual_items):
                assert_false(isinstance(iterable, list))
                assert_true(hasattr(iterable, '__next__'))
    else:  # methods are actually views
        for iterable in (actual_keys, actual_values, actual_items):
            assert_false(isinstance(iterable, list))
            # is there a good way to check if something is a view?

        assert_equals(frozenset(actual_keys), expected_keys)
        assert_equals(frozenset(actual_values), expected_values)
        assert_equals(frozenset(actual_items), expected_items)

    # make sure empty iteration works
    assert_equals(tuple(constructor().items()), ())


def containment(constructor, _=None):
    "Check whether {cls} contains keys"
    mapping = constructor({'foo': 'bar', frozenset((1, 2, 3)): 'abc', 1: 2})
    empty = constructor()

    assert_true('foo' in mapping)
    assert_false('foo' in empty)

    assert_true(frozenset((1, 2, 3)) in mapping)
    assert_false(frozenset((1, 2, 3)) in empty)

    assert_true(1 in mapping)
    assert_false(1 in empty)

    assert_false('banana' in mapping)
    assert_false('banana' in empty)


def length(constructor, _=None):
    "Get the length of an {cls} instance"

    assert_equals(len(constructor()), 0)
    assert_equals(len(constructor({'foo': 'bar'})), 1)
    assert_equals(len(constructor({'foo': 'bar', 'lorem': 'ipsum'})), 2)


def equality(constructor, _=None):
    "Equality checks for {cls}"
    empty = {}
    mapping_a = {'foo': 'bar'}
    mapping_b = {'lorem': 'ipsum'}

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


def item_creation(constructor, options=None):
    "Add a key-value pair to an {cls}"
    if options is None:
        options = {}

    mutable = options.get('mutable', False)

    if not mutable:
        def attribute():
            "Attempt to add an attribute"
            constructor().foo = 'bar'

        def item():
            "Attempt to add an item"
            constructor()['foo'] = 'bar'

        assert_raises(TypeError, attribute)
        assert_raises(TypeError, item)
    else:
        mapping = constructor()

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

        assert_raises(TypeError, add_foo)
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


def item_deletion(constructor, options=None):
    "Remove a key-value from to an {cls}"
    if options is None:
        options = {}

    mutable = options.get('mutable', False)

    if not mutable:
        mapping = constructor({'foo': 'bar'})

        def attribute(mapping):
            "Attempt to del an attribute"
            del mapping.foo

        def item(mapping):
            "Attempt to del an item"
            del mapping['foo']

        assert_raises(TypeError, attribute, mapping)
        assert_raises(TypeError, item, mapping)

        assert_equals(mapping, {'foo': 'bar'})
        assert_equals(mapping.foo, 'bar')
        assert_equals(mapping['foo'], 'bar')
    else:
        mapping = constructor(
            {'foo': 'bar', 'lorem': 'ipsum', '_hidden': True, 'get': 'value'}
        )

        del mapping.foo
        assert_false('foo' in mapping)

        del mapping['lorem']
        assert_false('lorem' in mapping)

        def del_hidden():
            "delete _hidden"
            del mapping._hidden

        assert_raises(TypeError, del_hidden)
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


def sequence_type(constructor, _=None):
    "Does {cls} respect sequence type?"
    data = {'list': [{'foo': 'bar'}], 'tuple': ({'foo': 'bar'},)}

    tuple_mapping = constructor(data)

    assert_true(isinstance(tuple_mapping.list, tuple))
    assert_equals(tuple_mapping.list[0].foo, 'bar')

    assert_true(isinstance(tuple_mapping.tuple, tuple))
    assert_equals(tuple_mapping.tuple[0].foo, 'bar')

    list_mapping = constructor(data, sequence_type=list)

    assert_true(isinstance(list_mapping.list, list))
    assert_equals(list_mapping.list[0].foo, 'bar')

    assert_true(isinstance(list_mapping.tuple, list))
    assert_equals(list_mapping.tuple[0].foo, 'bar')

    none_mapping = constructor(data, sequence_type=None)

    assert_true(isinstance(none_mapping.list, list))
    assert_raises(AttributeError, lambda: none_mapping.list[0].foo)

    assert_true(isinstance(none_mapping.tuple, tuple))
    assert_raises(AttributeError, lambda: none_mapping.tuple[0].foo)


def addition(constructor, _=None):
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

    assert_raises(TypeError, lambda: constructor() + 1)

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
    assert_true(
        isinstance((constructor(data, list) + constructor()).sequence, tuple)
    )

    assert_true(isinstance((constructor(data, list) + {}).sequence, list))
    assert_true(
        isinstance(
            (constructor(data, list) + constructor({}, list)).sequence,
            list
        )
    )


def to_kwargs(constructor, _=None):
    "**{cls}"
    def return_results(**kwargs):
        "Return result passed into a function"
        return kwargs

    expected = {'foo': 1, 'bar': 2}

    assert_equals(return_results(**constructor()), {})
    assert_equals(return_results(**constructor(expected)), expected)


def check_pickle_roundtrip(source, constructor, cls=None, **kwargs):
    """
    serialize then deserialize a mapping, ensuring the result and initial
    objects are equivalent.
    """
    if cls is None:
        cls = constructor

    source = constructor(source, **kwargs)
    data = pickle.dumps(source)
    loaded = pickle.loads(data)

    assert_true(isinstance(loaded, cls))

    assert_equals(source, loaded)

    return loaded


def pickleing(constructor, options=None):
    "Pickle {cls}"
    if options is None:
        options = {}

    cls = options.get('class', constructor)

    empty = check_pickle_roundtrip(None, constructor, cls)
    assert_equals(empty, {})

    mapping = check_pickle_roundtrip({'foo': 'bar'}, constructor, cls)
    assert_equals(mapping, {'foo': 'bar'})

    # make sure sequence_type is preserved
    raw = {'list': [{'a': 'b'}], 'tuple': ({'a': 'b'},)}

    as_tuple = check_pickle_roundtrip(raw, constructor, cls)
    assert_true(isinstance(as_tuple['list'], list))
    assert_true(isinstance(as_tuple['tuple'], tuple))
    assert_true(isinstance(as_tuple.list, tuple))
    assert_true(isinstance(as_tuple.tuple, tuple))

    as_list = check_pickle_roundtrip(raw, constructor, cls, sequence_type=list)
    assert_true(isinstance(as_list['list'], list))
    assert_true(isinstance(as_list['tuple'], tuple))
    assert_true(isinstance(as_list.list, list))
    assert_true(isinstance(as_list.tuple, list))

    as_raw = check_pickle_roundtrip(raw, constructor, cls, sequence_type=None)
    assert_true(isinstance(as_raw['list'], list))
    assert_true(isinstance(as_raw['tuple'], tuple))
    assert_true(isinstance(as_raw.list, list))
    assert_true(isinstance(as_raw.tuple, tuple))
