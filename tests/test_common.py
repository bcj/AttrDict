# encoding: UTF-8
"""
Common tests that apply to multiple Attr-derived classes.
"""
from collections import namedtuple, ItemsView, KeysView, ValuesView
import pickle
from sys import version_info

from nose.tools import (assert_equals, assert_not_equals,
                        assert_true, assert_false, assert_raises)

PYTHON_2 = version_info < (3,)

Options = namedtuple(
    'Options',
    ('cls', 'constructor', 'mutable', 'method_missing', 'iter_methods')
)


def test_attr():
    """
    Run Attr against the common tests.
    """
    from attrdict.attr import Attr

    for test in common(Attr):
        yield test


def test_mutable_attr():
    """
    Run MutableAttr against the common tests.
    """
    from attrdict.mutableattr import MutableAttr

    for test in common(MutableAttr, mutable=True):
        yield test


def common(cls, constructor=None, mutable=False, method_missing=False,
           iter_methods=False):
    """
    Iterates over tests common to multiple Attr-derived classes

    cls: The class that is being tested.
    constructor: (optional, None) A special constructor that supports
        0-1 positional arguments representing a mapping, and the named
        argument 'sequence_type'. If not given, cls will be called
    mutable: (optional, False) Whether the object is supposed to be
        mutable.
    method_missing: (optional, False) Whether the class supports dynamic
        creation of methods (e.g., defaultdict).
    iter_methods: (optional, False) Whether the class implements
        iter<keys,values,items> under Python 2.
    """
    tests = (
        item_access, iteration, containment, length, equality,
        item_creation, item_deletion, sequence_type, addition,
        to_kwargs, pickleing, pop, popitem, clear, update, setdefault
    )

    require_mutable = lambda options: options.mutable

    requirements = {
        pop: require_mutable,
        popitem: require_mutable,
        clear: require_mutable,
        update: require_mutable,
        setdefault: require_mutable,
    }

    if constructor is None:
        constructor = cls

    options = Options(cls, constructor, mutable, method_missing, iter_methods)

    for test in tests:
        if (test not in requirements) or requirements[test](options):
            test.description = test.__doc__.format(cls=cls.__name__)

            yield test, options


def item_access(options):
    "Access items in {cls}."
    mapping = options.constructor(
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
    if not options.method_missing:
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

    if PYTHON_2:
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
                assert_true(hasattr(iterable, '__next__'))
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
        def attribute():
            "Attempt to add an attribute"
            options.constructor().foo = 'bar'

        def item():
            "Attempt to add an item"
            options.constructor()['foo'] = 'bar'

        assert_raises(TypeError, attribute)
        assert_raises(TypeError, item)
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


def item_deletion(options):
    "Remove a key-value from to an {cls}"

    if not options.mutable:
        mapping = options.constructor({'foo': 'bar'})

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


def sequence_type(options):
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


def pickleing(options):
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

    mapping = options.constructor(expected)

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
