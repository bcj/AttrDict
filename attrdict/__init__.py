"""
AttrDict is a mapping object that allows access to its values both as
keys, and as attributes (whenever the key can be used as an attribute
name).
"""
from collections import Mapping
import re
from sys import version_info


__all__ = ['AttrDict', 'merge']


if version_info < (3,):  # Python 2
    PY2 = True

    STRING = basestring
else:
    PY2 = False

    STRING = str


class AttrDict(Mapping):
    """
    A mapping object that allows access to its values both as keys, and
    as attributes (as long as the attribute name is valid).
    """
    def __init__(self, mapping=None):
        """
        mapping: (optional, None) The mapping object to use for the
            instance. Note that the mapping object itself is used, not a
            copy. This means that you cannot clone an AttrDict using:
            adict = AttrDict(adict)
        """
        if mapping is None:
            mapping = {}

        self._mapping = mapping

        for key, value in mapping.iteritems() if PY2 else mapping.items():
            if self._valid_name(key):
                setattr(self, key, self._build(value))

    def get(self, key, default=None):
        """
        Get a value associated with a key.

        key: The key associated with the desired value.
        default: (optional, None) The value to return if the key is not
            found.
        """
        return self._mapping.get(key, default)

    def items(self):
        """
        In python 2.X returns a list of (key, value) pairs as 2-tuples.
        In python 3.X returns an iterator over the (key, value) pairs.
        """
        return self._mapping.items()

    def keys(self):
        """
        In python 2.X returns a list of keys in the mapping.
        In python 3.X returns an iterator over the mapping's keys.
        """
        return self._mapping.keys()

    def values(self):
        """
        In python 2.X returns a list of values in the mapping.
        In python 3.X returns an iterator over the mapping's values.
        """
        return self._mapping.values()

    def _set(self, key, value):
        """
        Respoinsible for actually adding/changing a key-value pair. This
        needs to be separated otu so that setattr and setitem don't
        clash.
        """
        self._mapping[key] = value

        if self._valid_name(key):
            super(AttrDict, self).__setattr__(
                key, self._build(value))

    def _delete(self, key):
        """
        Responsible for actually deleting a key-value pair. This needs
        to be separated out so that delattr and delitem don't clash.
        """
        del self._mapping[key]

        if self._valid_name(key):
            super(AttrDict, self).__delattr__(key)

    def __call__(self, key):
        """
        Access a value in the mapping as an attribute. This differs from
        dict-style key access because it returns a new instance of an
        AttrDict (if the value is a mapping object), not the underlying
        type. This allows for dynamic attribute-style access.

        key: The key associated with the value being accessed.
        """
        if key not in self._mapping:
            raise AttributeError(
                "'{0}' instance has no attribute '{1}'".format(
                    self.__class__.__name__, key))

        return self._build(self._mapping[key])

    def __setattr__(self, key, value):
        """
        adict.key = value

        Add a key-value pair as an attribute
        """
        if not hasattr(self, '_mapping'):
            super(AttrDict, self).__setattr__(key, value)
        else:
            if not self._valid_name(key):
                raise TypeError("Invalid key: {0}".format(repr(key)))

            self._set(key, value)

    def __delattr__(self, key):
        """
        del adict.key

        Remove a key-value pair as an attribute.
        """
        if not self._valid_name(key) or key not in self._mapping:
            raise TypeError("Invalid key: {0}".format(repr(key)))

        self._delete(key)

    def __setitem__(self, key, value):
        """
        adict[key] = value

        Add a key-value pair to the instance.
        """
        self._set(key, value)

    def __getitem__(self, key):
        """
        value = adict[key]

        Access a value associated with a key in the instance.
        """
        return self._mapping[key]

    def __delitem__(self, key):
        """
        del adict[key]

        Delete a key-value pair in the instance.
        """
        self._delete(key)

    def __contains__(self, key):
        """
        key in adict

        Check if a key is in the instance.
        """
        return key in self._mapping

    def __len__(self):
        """
        len(adict)

        Check the length of the instance.
        """
        return len(self._mapping)

    def __iter__(self):
        """
        (key for key in adict)

        iterate through all the keys.
        """
        return self._mapping.__iter__()

    def __add__(self, other):
        """
        adict + other

        Add a mapping to this AttrDict object.

        NOTE: AttrDict is not idempotent. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        return merge(self, other)

    def __radd__(self, other):
        """
        other + adict

        Add this AttrDict to a mapping object.

        NOTE: AttrDict is not idempotent. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        return merge(other, self)

    def __repr__(self):
        """
        Create a string representation of the AttrDict.
        """
        return u"a{0}".format(repr(self._mapping))

    @classmethod
    def _build(cls, obj):
        """
        Wrap an object in an AttrDict as necessary. Mappings are
        wrapped, but all other objects are returned as is.

        obj: The object to (possibly) wrap.
        """
        return cls(obj) if isinstance(obj, Mapping) else obj

    @classmethod
    def _valid_name(cls, name):
        """
        Check whether a key name is a valid attribute name. A valid
        name must start with an alphabetic character, and must only
        contain alphanumeric characters and underscores. The name also
        must not be an attribute of this class.

        NOTE: Names with leading underscores are considered invalid for
        stylistic reasons. While this package is fairly un-Pythonic, I'm
        going to stand strong on the fact that leading underscores
        represent private attributes. Further, magic methods absolutely
        need to be prevented so that crazy things don't happen.
        """
        return (isinstance(name, STRING) and
                re.match('^[A-Za-z][A-Za-z0-9_]*$', name) and
                not hasattr(cls, name))

    # Add missing iter methods in 2.X
    if PY2:
        def iteritems(self):
            """
            Iterate over (key, value) 2-tuples in the mapping
            """
            return self._mapping.iteritems()

        def iterkeys(self):
            """
            Iterate over keys in the mapping
            """
            return self._mapping.iterkeys()

        def itervalues(self):
            """
            Iterate over values in the mapping
            """
            return self._mapping.itervalues()


def merge(left, right):
    """
    merge to mappings objects into a new AttrDict.

    left: The left mapping object.
    right: The right mapping object.

    NOTE: This is not idempotent. merge(a, b) != merge(b, a).
    """
    merged = AttrDict()

    left_keys = set(left)
    right_keys = set(right)

    # Items only in the left object
    for key in (left_keys - right_keys):
        merged[key] = left[key]

    # Items only in the right object
    for key in (right_keys - left_keys):
        merged[key] = right[key]

    # In both
    for key in left_keys.intersection(right_keys):
        if isinstance(left[key], Mapping) and isinstance(right[key], Mapping):
            merged[key] = merge(left[key], right[key])
        else:  # different types, overwrite with the right value
            merged[key] = right[key]

    return merged
