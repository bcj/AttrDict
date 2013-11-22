"""
A collection of unit tests for the AttrDict class.
"""
from sys import version_info
import unittest


PY2 = version_info < (3,)


class TestAttrDict(unittest.TestCase):
    """
    A collection of unit tests for the AttrDict class.
    """
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
        adict._set
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


if __name__ == '__main__':
    unittest.main()
