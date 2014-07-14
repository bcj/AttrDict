"""
AttrDict is a mapping object that allows access to its values both as
keys, and as attributes (whenever the key can be used as an attribute
name).
"""
from collections import Mapping, MutableMapping, Sequence
from copy import deepcopy
import json
import re
from sys import version_info


__all__ = ['AttrDict', 'merge']


# Python 2
PY2, STRING = (True, basestring) if version_info < (3,) else (False, str)


class AttrDict(MutableMapping):
    """
    A mapping object that allows access to its values both as keys, and
    as attributes (as long as the attribute name is valid).
    """
    def __init__(self, mapping=None, recursive=True,
                 default_factory=None, pass_key=False):
        """
        mapping: (optional, None) The mapping object to use for the
            instance. Note that the mapping object itself is used, not a
            copy. This means that you cannot clone an AttrDict using:
            adict = AttrDict(adict)
        recursive: (optional, True) Recursively convert mappings into
            AttrDicts.
        default_factory: (optional, Not Passed) If passed make AttrDict
            behave like a default dict.
        pass_key: (optional, False) If True, and default_factory is
            given, then default_factory will be passed the key.
        """
        if mapping is None:
            mapping = {}

        if default_factory is None:
            self.__setattr__('_default_factory', None, force=True)
            self.__setattr__('_pass_key', False, force=True)
        else:
            self.__setattr__('_default_factory', default_factory, force=True)
            self.__setattr__('_pass_key', pass_key, force=True)

        self.__setattr__('_recursive', recursive, force=True)

        self.__setattr__('_mapping', mapping, force=True)

        for key, value in mapping.iteritems() if PY2 else mapping.items():
            if self._valid_name(key):
                setattr(self, key, value)

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
        Responsible for actually adding/changing a key-value pair. This
        needs to be separated out so that setattr and setitem don't
        clash.
        """
        self._mapping[key] = value

        if self._valid_name(key):
            super(AttrDict, self).__setattr__(
                key, self._build(value, recursive=self._recursive))

    def _delete(self, key):
        """
        Responsible for actually deleting a key-value pair. This needs
        to be separated out so that delattr and delitem don't clash.
        """
        del self._mapping[key]

        if self._valid_name(key):
            super(AttrDict, self).__delattr__(key)

    def __getattr__(self, key):
        """
        value = adict.key

        Access a value associated with a key in the instance.
        """
        if self._default_factory is None:
            raise AttributeError(key)

        return self.__missing__(key)

    def __call__(self, key):
        """
        Access a value in the mapping as an attribute. This differs from
        dict-style key access because it returns a new instance of an
        AttrDict (if the value is a mapping object), not the underlying
        type. This allows for dynamic attribute-style access.

        key: The key associated with the value being accessed.
        """
        if key not in self._mapping:
            if self._default_factory is not None:
                self.__missing__(key)
            else:
                raise AttributeError(
                    "'{0}' instance has no attribute '{1}'".format(
                        self.__class__.__name__, key))

        return self._build(self._mapping[key], recursive=self._recursive)

    def __setattr__(self, key, value, force=False):
        """
        adict.key = value

        Add a key-value pair as an attribute
        """
        if force:
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
        if key not in self._mapping and self._default_factory is not None:
            self[key] = self.__missing__(key)

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

        NOTE: AttrDict is not commutative. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        recursive = not hasattr(other, '_recursive') or other._recursive

        return merge(self, other, recursive=self._recursive and recursive)

    def __radd__(self, other):
        """
        other + adict

        Add this AttrDict to a mapping object.

        NOTE: AttrDict is not commutative. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        return merge(other, self, recursive=self._recursive)

    def __repr__(self):
        """
        Create a string representation of the AttrDict.
        """
        return u"a{0}".format(repr(self._mapping))

    def __missing__(self, key):
        """
        Add a missing element.
        """
        if self._pass_key:
            self._mapping[key] = value = self._default_factory(key)
        else:
            self._mapping[key] = value = self._default_factory()

        return value

    def __copy__(self):
        """
        Copy an attrdict.
        """
        return AttrDict(self._mapping, recursive=self._recursive,
                        default_factory=self._default_factory,
                        pass_key=self._pass_key)

    def __deepcopy__(self, memo):
        """
        Deep copy an attrdict.
        """
        return AttrDict(deepcopy(self._mapping), recursive=self._recursive,
                        default_factory=self._default_factory,
                        pass_key=self._pass_key)

    @classmethod
    def _build(cls, obj, recursive=True):
        """
        Wrap an object in an AttrDict as necessary. Mappings are
        wrapped, but all other objects are returned as is.

        obj: The object to (possibly) wrap.
        recursive: (optional, True) Whether Sequences should have their
            elements turned into attrdicts.
        """
        if isinstance(obj, Mapping):
            obj = cls(obj, recursive=recursive)
        elif recursive:
            if isinstance(obj, Sequence) and not isinstance(obj, STRING):
                new = [cls._build(element, recursive=True) for element in obj]

                # This has to have a __class__. Only old-style classes
                # don't, and none of them would subclass Sequence.
                obj = obj.__class__(new)

        return obj

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


def merge(left, right, recursive=True):
    """
    merge to mappings objects into a new AttrDict.

    left: The left mapping object.
    right: The right mapping object.
    recursive: (optional, True) Whether Sequences should have their
        elements turned into attrdicts.

    NOTE: This is not commutative. merge(a, b) != merge(b, a).
    """
    merged = AttrDict(recursive=recursive)

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
            merged[key] = merge(left[key], right[key], recursive=recursive)
        else:  # different types, overwrite with the right value
            merged[key] = right[key]

    return merged


# def load(*filenames, load_function=json.load)  # once Python3-only
def load(*filenames, **kwargs):
    """
    Returns a settings dict built from a list of settings files.

    filenames: The names of any number of settings files.
    load_function: (optional, json.load) The function used to load the
    settings into a Mapping object.
    """
    load_function = kwargs.pop('load_function', json.load)

    if kwargs:
        raise TypeError("unknown options: {0}".format(kwargs.keys()))

    settings = AttrDict()

    for filename in filenames:
        with open(filename, 'r') as fileobj:
            settings += load_function(fileobj)

    return settings
