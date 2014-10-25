"""
A collection of unit tests for the AttrDict class.
"""
from __future__ import print_function

import os
from sys import version_info
from tempfile import mkstemp
import unittest


PY2 = version_info < (3,)


class TestAttrDict(unittest.TestCase):
    """
    A collection of unit tests for the AttrDict class.
    """
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for tempfile in self.tempfiles:
            os.remove(tempfile)

    def test_init(self):
        """
        Make sure that keys are accessable both as keys and attributes
        at initialization.
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar', 'alpha': {'beta': 2, 'bravo': {}}})

        # as key
        self.assertEqual(adict['foo'], 'bar')

        # as attribute
        self.assertEqual(adict.foo, 'bar')

        # nested as key
        self.assertEqual(adict['alpha'], {'beta': 2, 'bravo': {}})

        # nested as attribute
        self.assertEqual(adict.alpha, {'beta': 2, 'bravo': {}})
        self.assertEqual(adict.alpha.beta, 2)
        self.assertEqual(adict.alpha.bravo, {})

    def test_get(self):
        """
        Test that attributes can be accessed (both as keys, and as
        attributes).
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar'})

        # found
        self.assertEqual(adict.get('foo'), 'bar')

        # found, default given
        self.assertEqual(adict.get('foo', 'baz'), 'bar')

        # not found
        self.assertEqual(adict.get('bar'), None)

        # not found, default given
        self.assertEqual(adict.get('bar', 'baz'), 'baz')

    def test_iteration_2(self):
        """
        Test the iteration methods (items, keys, values[, iteritems,
        iterkeys, itervalues]).
        """
        if not PY2:  # Python2.6 doesn't have skipif/skipunless
            return

        from attrdict import AttrDict

        empty = AttrDict()
        adict = AttrDict({'foo': 'bar', 'lorem': 'ipsum', 'alpha': {
            'beta': 1, 'bravo': empty}})

        self.assertEqual(empty.items(), [])
        self.assertEqual(empty.keys(), [])
        self.assertEqual(empty.values(), [])

        items = adict.items()
        self.assertEqual(len(items), 3)
        self.assertTrue(('foo', 'bar') in items)
        self.assertTrue(('lorem', 'ipsum') in items)
        self.assertTrue(('alpha', {'beta': 1, 'bravo': empty}) in items)

        self.assertEqual(set(adict.keys()), set(['foo', 'lorem', 'alpha']))

        values = adict.values()
        self.assertEqual(len(values), 3)
        self.assertTrue('bar' in values)
        self.assertTrue('ipsum' in values)
        self.assertTrue({'beta': 1, 'bravo': empty} in values)

        # Iterator methods
        iterator = empty.iteritems()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = empty.iterkeys()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = empty.itervalues()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = adict.iteritems()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), adict.items())

        iterator = adict.iterkeys()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), adict.keys())

        iterator = adict.itervalues()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), adict.values())

    def test_iteration_3(self):
        """
        Test the iteration methods (items, keys, values[, iteritems,
        iterkeys, itervalues]).
        """
        if PY2:  # Python2.6 doesn't have skipif/skipunless
            return

        from attrdict import AttrDict

        empty = AttrDict()
        adict = AttrDict({'foo': 'bar', 'lorem': 'ipsum', 'alpha': {
            'beta': 1, 'bravo': empty}})

        iterator = empty.items()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = empty.keys()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = empty.values()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(list(iterator), [])

        iterator = adict.items()
        self.assertFalse(isinstance(iterator, list))
        items = list(iterator)
        self.assertEqual(len(items), 3)
        self.assertTrue(('foo', 'bar') in items)
        self.assertTrue(('lorem', 'ipsum') in items)
        self.assertTrue(('alpha', {'beta': 1, 'bravo': empty}) in items)

        iterator = adict.keys()
        self.assertFalse(isinstance(iterator, list))
        self.assertEqual(set(iterator), set(['foo', 'lorem', 'alpha']))

        iterator = adict.values()
        self.assertFalse(isinstance(iterator, list))
        values = list(iterator)
        self.assertEqual(len(values), 3)
        self.assertTrue('bar' in values)
        self.assertTrue('ipsum' in values)
        self.assertTrue({'beta': 1, 'bravo': empty} in values)

        # make sure 'iter' methods don't exist
        self.assertFalse(hasattr(adict, 'iteritems'))
        self.assertFalse(hasattr(adict, 'iterkeys'))
        self.assertFalse(hasattr(adict, 'itervalues'))

    def test_call(self):
        """
        Ensure that attributes can be dynamically accessed
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar', 'alpha': {'beta': 2, 'bravo': {}}})

        self.assertEqual(adict('foo'), 'bar')
        self.assertEqual(adict('alpha'), {'beta': 2, 'bravo': {}})
        self.assertEqual(adict('alpha').beta, 2)
        self.assertEqual(adict('alpha').bravo, {})

        # Make sure call failes correctly
        # with self.assertRaises(AttributeError)
        try:
            adict('fake')
        except AttributeError:
            pass  # this is what we want
        else:
            raise AssertionError("AttributeError not raised")

    def test_setattr(self):
        """
        Test that key-value pairs can be added/changes as attributes
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar'})

        adict.foo = 'baz'
        self.assertEqual(adict.foo, 'baz')
        self.assertEqual(adict['foo'], 'baz')

        adict.lorem = 'ipsum'
        self.assertEqual(adict.lorem, 'ipsum')
        self.assertEqual(adict['lorem'], 'ipsum')

        adict.alpha = {'beta': 1, 'bravo': 2}
        self.assertEqual(adict.alpha, {'beta': 1, 'bravo': 2})
        self.assertEqual(adict.alpha.beta, 1)
        self.assertEqual(adict['alpha'], {'beta': 1, 'bravo': 2})

        # with self.assertRaises(TypeError):
        try:
            adict._no = "Won't work"
        except TypeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

    def test_delattr(self):
        """
        Test that key-value pairs can be deleted as attributes.
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar', '_set': 'shadows', 'get': 'shadows'})

        del adict.foo

        # with self.assertRaises(AttributeError):
        try:
            adict.foo
        except AttributeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(KeyError):
        try:
            adict['foo']
        except KeyError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(TypeError):
        try:
            del adict.lorem
        except TypeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(TypeError):
        try:
            del adict._set
        except TypeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(TypeError):
        try:
            del adict.get
        except TypeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # make sure things weren't deleted
        self.assertNotEqual(adict._set, 'shadows')
        self.assertEqual(adict.get('get'), 'shadows')
        self.assertEqual(adict, {'_set': 'shadows', 'get': 'shadows'})

    def test_setitem(self):
        """
        Test that key-value pairs can be added/changes as keys
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar'})

        adict['foo'] = 'baz'
        self.assertEqual(adict.foo, 'baz')
        self.assertEqual(adict['foo'], 'baz')

        adict['lorem'] = 'ipsum'
        self.assertEqual(adict.lorem, 'ipsum')
        self.assertEqual(adict['lorem'], 'ipsum')

        adict['alpha'] = {'beta': 1, 'bravo': 2}
        self.assertEqual(adict.alpha, {'beta': 1, 'bravo': 2})
        self.assertEqual(adict.alpha.beta, 1)
        self.assertEqual(adict['alpha'], {'beta': 1, 'bravo': 2})

    def test_delitem(self):
        """
        Test that key-value pairs can be deleted as keys.
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar', '_set': 'shadows', 'get': 'shadows'})

        del adict['foo']

        # with self.assertRaises(AttributeError):
        try:
            adict.foo
        except AttributeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(AttributeError):
        try:
            adict.foo
        except AttributeError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(KeyError):
        try:
            adict['foo']
        except KeyError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        # with self.assertRaises(KeyError):
        try:
            del adict['lorem']
        except KeyError:
            pass  # expected
        else:
            raise AssertionError("Exception not thrown")

        del adict['_set']
        del adict['get']

        # make sure things weren't deleted
        adict._set
        self.assertEqual(adict.get('get', 'deleted'), 'deleted')
        self.assertEqual(adict, {})

    def test_getitem(self):
        """
        Tests that getitem doesn't return an attrdict.
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': {'bar': {'baz': 'lorem'}}})

        self.assertEqual(adict.foo.bar, {'baz': 'lorem'})  # works
        self.assertRaises(AttributeError, lambda: adict['foo'].bar)

        self.assertEqual(adict.foo.bar.baz, 'lorem')  # works
        self.assertRaises(AttributeError, lambda: adict['foo']['bar'].baz)

        adict = AttrDict({'foo': [{'bar': 'baz'}]})

        self.assertEqual(adict.foo[0].bar, 'baz')  # works
        self.assertRaises(AttributeError, lambda: adict['foo'][0].bar)

    def test_contains(self):
        """
        Test that contains works properly.
        """
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar', '_set': 'shadows', 'get': 'shadows'})

        self.assertTrue('foo' in adict)
        self.assertTrue('_set' in adict)
        self.assertTrue('get' in adict)
        self.assertFalse('items' in adict)

    def test_has_key(self):
        """
        Test has_key behavior in regard to this python
        """
        import inspect
        from attrdict import AttrDict

        adict = AttrDict({'foo': 'bar'})
        masked = AttrDict({'has_key': 'foobar'})

        if PY2:
            self.assertTrue(inspect.ismethod(adict.has_key))
            self.assertTrue(inspect.ismethod(masked.has_key))
            self.assertFalse(adict.has_key('has_key'))
            self.assertTrue(masked.has_key('has_key'))
        else:  # Python3 dropped this method
            self.assertFalse(inspect.ismethod(masked.has_key))
            self.assertRaises(AttributeError, getattr, adict, 'has_key')
            self.assertEqual(masked.has_key, 'foobar')

    def test_len(self):
        """
        Test that len works properly.
        """
        from attrdict import AttrDict

        # empty
        adict = AttrDict()
        self.assertEqual(len(adict), 0)

        # added via key
        adict['key'] = 1
        self.assertEqual(len(adict), 1)

        adict['key'] = 2
        self.assertEqual(len(adict), 1)

        # added via attribute
        adict.attribute = 3
        self.assertEqual(len(adict), 2)

        adict.key = 3
        self.assertEqual(len(adict), 2)

        # deleted
        del adict.key
        self.assertEqual(len(adict), 1)

    def test_iter(self):
        """
        Test that iter works properly.
        """
        from attrdict import AttrDict

        # empty
        for key in AttrDict():
            raise AssertionError("Nothing should be run right now")

        # non-empty
        expected = {'alpha': 1, 'bravo': 2, 'charlie': 3}
        actual = set()

        adict = AttrDict(expected)

        for key in adict:
            actual.add(key)

        self.assertEqual(actual, set(expected.keys()))

    def test_add(self):
        """
        Test that adding works.
        """
        from attrdict import AttrDict

        a = {'alpha': {'beta': 1, 'a': 1}, 'lorem': 'ipsum'}
        b = {'alpha': {'bravo': 1, 'a': 0}, 'foo': 'bar'}

        ab = {
            'alpha': {
                'beta': 1,
                'bravo': 1,
                'a': 0
            },
            'lorem': 'ipsum',
            'foo': 'bar'
        }

        ba = {
            'alpha': {
                'beta': 1,
                'bravo': 1,
                'a': 1
            },
            'lorem': 'ipsum',
            'foo': 'bar'
        }

        # Both AttrDicts
        self.assertEqual(AttrDict(a) + AttrDict(b), ab)
        self.assertEqual(AttrDict(b) + AttrDict(a), ba)

        # Left AttrDict
        self.assertEqual(AttrDict(a) + b, ab)
        self.assertEqual(AttrDict(b) + a, ba)

        # Right AttrDict
        self.assertEqual(a + AttrDict(b), ab)
        self.assertEqual(b + AttrDict(a), ba)

        # Defer on non-mappings
        class NonMapping(object):
            """
            A non-mapping object to test NotImplemented
            """
            def __radd__(self, other):
                return 'success'

        self.assertEqual(AttrDict(a) + NonMapping(), 'success')

        # with self.assertRaises(NotImplementedError)
        try:
            NonMapping + AttrDict(b)
        except TypeError:
            pass  # what we want to happen
        else:
            raise AssertionError("NotImplementedError not thrown")

    def test_build(self):
        """
        Test that build works.
        """
        from attrdict import AttrDict

        self.assertTrue(isinstance(AttrDict._build({}), AttrDict))
        self.assertTrue(isinstance(AttrDict._build([]), list))
        self.assertTrue(isinstance(AttrDict._build(AttrDict()), AttrDict))
        self.assertTrue(isinstance(AttrDict._build(1), int))

    def test_valid_name(self):
        """
        Test that valid_name works.
        """
        from attrdict import AttrDict

        self.assertTrue(AttrDict._valid_name('valid'))
        self.assertFalse(AttrDict._valid_name('_invalid'))
        self.assertFalse(AttrDict._valid_name('get'))

    def test_kwargs(self):
        """
        Test that ** works
        """
        def return_results(**kwargs):
            """Return result passed into a function"""
            return kwargs

        expected = {'foo': 1, 'bar': 2}

        from attrdict import AttrDict

        self.assertEqual(return_results(**AttrDict()), {})
        self.assertEqual(return_results(**AttrDict(expected)), expected)

    def test_sequences(self):
        """
        Test that AttrDict handles Sequences properly.
        """
        from attrdict import AttrDict

        adict = AttrDict({'lists': [{'value': 1}, {'value': 2}],
                          'tuple': ({'value': 1}, {'value': 2})})

        # lists
        self.assertTrue(adict.lists, list)

        self.assertEqual(adict.lists[0].value, 1)
        self.assertEqual(adict.lists[1].value, 2)

        self.assertEqual(({} + adict).lists[0].value, 1)
        self.assertEqual((adict + {}).lists[1].value, 2)

        self.assertEqual((AttrDict(recursive=True) + adict).lists[0].value, 1)
        self.assertEqual((adict + AttrDict(recursive=True)).lists[1].value, 2)

        self.assertEqual([element.value for element in adict.lists], [1, 2])

        self.assertEqual(adict('lists')[0].value, 1)

        # tuple
        self.assertTrue(adict.tuple, tuple)

        self.assertEqual(adict.tuple[0].value, 1)
        self.assertEqual(adict.tuple[1].value, 2)

        self.assertTrue(adict.tuple, tuple)

        self.assertEqual(({} + adict).tuple[0].value, 1)
        self.assertEqual((adict + {}).tuple[1].value, 2)

        self.assertTrue(({} + adict).tuple, tuple)
        self.assertTrue((adict + {}).tuple, tuple)

        self.assertEqual((AttrDict(recursive=True) + adict).tuple[0].value, 1)
        self.assertEqual((adict + AttrDict(recursive=True)).tuple[1].value, 2)

        self.assertEqual([element.value for element in adict.tuple], [1, 2])

        # Not recursive
        adict = AttrDict({'lists': [{'value': 1}, {'value': 2}],
                          'tuple': ({'value': 1}, {'value': 2})},
                         recursive=False)

        self.assertFalse(isinstance(adict.lists[0], AttrDict))

        self.assertFalse(isinstance(({} + adict).lists[0], AttrDict))
        self.assertFalse(isinstance((adict + {}).lists[1], AttrDict))

        self.assertFalse(
            isinstance((AttrDict(recursive=True) + adict).lists[0], AttrDict))
        self.assertFalse(
            isinstance((adict + AttrDict(recursive=True)).lists[1], AttrDict))

        self.assertFalse(isinstance((adict + adict).lists[0], AttrDict))

        for element in adict.lists:
            self.assertFalse(isinstance(element, AttrDict))

        self.assertFalse(isinstance(adict('lists')[0], AttrDict))

        # Dict access shouldn't produce an attrdict
        self.assertFalse(isinstance(adict['lists'][0], AttrDict))

        self.assertFalse(isinstance(adict.tuple[0], AttrDict))

        self.assertFalse(isinstance(({} + adict).tuple[0], AttrDict))
        self.assertFalse(isinstance((adict + {}).tuple[1], AttrDict))

        self.assertFalse(
            isinstance((AttrDict(recursive=True) + adict).tuple[0], AttrDict))
        self.assertFalse(
            isinstance((adict + AttrDict(recursive=True)).tuple[1], AttrDict))

        self.assertFalse(isinstance((adict + adict).tuple[0], AttrDict))

        for element in adict.tuple:
            self.assertFalse(isinstance(element, AttrDict))

        self.assertFalse(isinstance(adict('tuple')[0], AttrDict))

        # Dict access shouldn't produce an attrdict
        self.assertFalse(isinstance(adict['tuple'][0], AttrDict))

    def test_repr(self):
        """
        Test that repr works appropriately.
        """
        from attrdict import AttrDict

        self.assertEqual(repr(AttrDict()), 'a{}')
        self.assertEqual(repr(AttrDict({'foo': 'bar'})), "a{'foo': 'bar'}")
        self.assertEqual(
            repr(AttrDict({'foo': {1: 2}})), "a{'foo': {1: 2}}")
        self.assertEqual(
            repr(AttrDict({'foo': AttrDict({1: 2})})), "a{'foo': a{1: 2}}")

    def test_copy(self):
        """
        test that attrdict supports copy.
        """
        from copy import copy

        from attrdict import AttrDict

        adict = AttrDict({'foo': {'bar': 'baz'}})
        bdict = copy(adict)
        cdict = bdict

        bdict.foo.lorem = 'ipsum'

        self.assertEqual(adict, bdict)
        self.assertEqual(bdict, cdict)

    def test_deepcopy(self):
        """
        test that attrdict supports deepcopy.
        """
        from copy import deepcopy

        from attrdict import AttrDict

        adict = AttrDict({'foo': {'bar': 'baz'}})
        bdict = deepcopy(adict)
        cdict = bdict

        bdict.foo.lorem = 'ipsum'

        self.assertNotEqual(adict, bdict)
        self.assertEqual(bdict, cdict)

    def test_default_dict(self):
        """
        test attrdict's defaultdict support.
        """
        from attrdict import AttrDict

        self.assertRaises(KeyError, lambda: AttrDict()['foo'])
        self.assertRaises(AttributeError, lambda: AttrDict().foo)

        adict = AttrDict(default_factory=lambda: ('foo', 'bar', 'baz'))

        self.assertEqual(adict['foo'], ('foo', 'bar', 'baz'))
        self.assertEqual(adict('bar'), ('foo', 'bar', 'baz'))
        self.assertEqual(adict.baz, ('foo', 'bar', 'baz'))
        self.assertEqual(adict.get('lorem'), None)
        self.assertEqual(adict.get('ipsum', 'alpha'), 'alpha')

        # make sure this doesn't break access
        adict.bravo = 'charlie'

        self.assertEqual(adict['bravo'], 'charlie')
        self.assertEqual(adict('bravo'), 'charlie')
        self.assertEqual(adict.bravo, 'charlie')
        self.assertEqual(adict.get('bravo'), 'charlie')
        self.assertEqual(adict.get('bravo', 'alpha'), 'charlie')

    def test_default_dict_pass_key(self):
        """
        test attrdict's defaultdict support.
        """
        from attrdict import AttrDict

        adict = AttrDict(default_factory=lambda foo: (foo, 'bar', 'baz'),
                         pass_key=True)

        self.assertEqual(adict['foo'], ('foo', 'bar', 'baz'))
        self.assertEqual(adict('bar'), ('bar', 'bar', 'baz'))
        self.assertEqual(adict.baz, ('baz', 'bar', 'baz'))
        self.assertEqual(adict.get('lorem'), None)
        self.assertEqual(adict.get('ipsum', 'alpha'), 'alpha')

        # make sure this doesn't break access
        adict.bravo = 'charlie'

        self.assertEqual(adict['bravo'], 'charlie')
        self.assertEqual(adict('bravo'), 'charlie')
        self.assertEqual(adict.bravo, 'charlie')
        self.assertEqual(adict.get('bravo'), 'charlie')
        self.assertEqual(adict.get('bravo', 'alpha'), 'charlie')

    def test_load_bad_kwarg(self):
        """
        Test that load TypeErrors on kwargs other than load_function
        """
        from attrdict import load

        self.assertRaises(TypeError, load, foo='bar')

    def test_load_empty(self):
        """
        Test that load TypeErrors on kwargs other than load_function
        """
        from attrdict import load, AttrDict

        adict = load()

        self.assertTrue(isinstance(adict, AttrDict))
        self.assertFalse(adict)

    def test_load_one(self):
        """
        test loading a single file
        """
        from attrdict import load

        self.tempfiles.append(mkstemp()[1])

        with open(self.tempfiles[0], 'w') as fileobj:
            fileobj.write('{"foo": "bar", "baz": 1}')

        adict = load(self.tempfiles[0])

        self.assertEqual(adict, {'foo': 'bar', 'baz': 1})

    def test_load_many(self):
        """
        test loading multiple files at once.
        """
        from attrdict import load

        self.tempfiles.append(mkstemp()[1])

        with open(self.tempfiles[0], 'w') as fileobj:
            fileobj.write('{"foo": "bar", "baz": {"lorem": "ipsum"}}')

        self.tempfiles.append(mkstemp()[1])

        with open(self.tempfiles[1], 'w') as fileobj:
            fileobj.write('{"alpha": "bravo", "baz": {"charlie": "delta"}}')

        self.tempfiles.append(mkstemp()[1])

        with open(self.tempfiles[2], 'w') as fileobj:
            fileobj.write('{"alpha": "a", "baz": {"charlie": "delta"}}')

        adict = load(*self.tempfiles)

        self.assertEqual(adict, {
            'foo': 'bar',
            'alpha': 'a',
            'baz': {'lorem': 'ipsum', 'charlie': 'delta'}})

    def test_load_load_function(self):
        """
        test that load works with a custom load_function provided.
        """
        from attrdict import load

        self.tempfiles.append(mkstemp()[1])

        with open(self.tempfiles[0], 'w') as fileobj:
            fileobj.write('{"foo": "bar", "baz": 1}')

        adict = load(self.tempfiles[0], load_function=lambda _: {'banana': 1})

        self.assertEqual(adict, {'banana': 1})

if __name__ == '__main__':
    unittest.main()
