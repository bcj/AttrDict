"""
Attr is an implementation of Mapping which also allows for
attribute-style access of values. Attr serves as the base class that all
other Attr* classes subclass from.
"""
from collections import Mapping, Sequence
import re

from attrdict.merge import merge
from attrdict.two_three import StringType


__all__ = ['Attr']


class Attr(Mapping):
    """
    An implementation of Mapping which also allows for attribute-style
    access of values. Attr serves as the base class that all other Attr*
    classes subclass from.

    A key may be used as an attribute if:
      *  It is a string.
      *  It matches /^[A-Za-z][A-Za-z0-9_]*$/ (i.e., public attribute).
      *  The key doesn't overlap with any class attributes (for Attr,
        those would be 'get', 'items', 'keys', 'values', 'mro', and
        'register').

    If a value which is accessed as an attribute is a Sequence type (and
    is not string/bytes), any Mappings within it will be converted to an
    Attr.

    items: (optional, None) An iterable or mapping representing the items
        in the object.
    sequence_type: (optional, tuple) If not None, the constructor for
        converted (i.e., not string or bytes) Sequences.

    NOTE: Attr isn't designed to be mutable, but it isn't actually
    immutable. By accessing hidden attributes, an untrusted source can
    mutate an Attr object. If you need to ensure an untrusted source
    can't modify a base object, you should pass a copy (using deepcopy
    if the Attr is nested).

    NOTE: If sequence_type is not None, then Sequence values will
    be different when accessed as a value then when accessed as an
    attribute. For mutable types like list, this may result in
    hard-to-track bugs
    """
    def __init__(self, items=None, sequence_type=tuple):
        if items is None:
            items = ()

        self.__setattr__('_sequence_type', sequence_type, force=True)

        # NOTE: we want to keep the original mapping if possible, that
        # way, subclasses that implement mutability can subassign e.g.:
        # attr.foo.bar = 'baz'

        # items may be an iterable of two-tuples, or a mapping.
        if isinstance(items, Mapping):
            mapping = items
        else:
            mapping = dict(items)

        self.__setattr__('_mapping', mapping, force=True)

    def __getitem__(self, key):
        """
        Access a value associated with a key.

        Note: values returned will not be wrapped, even if recursive
        is True.
        """
        return self._mapping[key]

    def __len__(self):
        """
        Check the length of the mapping.
        """
        return len(self._mapping)

    def __iter__(self):
        """
        iterate through the keys.
        """
        return self._mapping.__iter__()

    def __call__(self, key):
        """
        Dynamically access a key in the mapping.

        This differs from dict-style key access because it returns a new
        instance of an Attr (if the value is a Mapping object, and
        recursive is True).
        """
        if key not in self._mapping:
            raise AttributeError(
                "'{cls}' instance has no attribute '{name}'".format(
                    cls=self.__class__.__name__, name=key
                )
            )

        return self._build(
            self._mapping[key],
            sequence_type=self._sequence_type
        )

    def __getattr__(self, key):
        """
        Access a key-value pair as an attribute.
        """
        if key in self._mapping and self._valid_name(key):
            return self._build(
                self._mapping[key], sequence_type=self._sequence_type
            )

        raise AttributeError(
            "'{cls}' instance has no attribute '{name}'".format(
                cls=self.__class__.__name__, name=key
            )
        )

    def __setattr__(self, key, value, force=False):
        """
        Add an attribute to the instance. The attribute will only be
        added if force is set to True.
        """
        if force:
            super(Attr, self).__setattr__(key, value)
        else:
            raise TypeError("Can not add new attribute")

    def __delattr__(self, key, force=False):
        """
        Delete an attribute from the instance. But no, this is not
        allowered.
        """
        raise TypeError(
            "'{cls}' object does not support attribute deletion".format(
                cls=self.__class__.__name__
            )
        )

    def __add__(self, other):
        """
        Add a mapping to this Attr, creating a new, merged Attr.

        NOTE: Attr is not commutative. a + b != b + a.
        NOTE: If both objects are `Attr`s and have differing sequence
            types, the default value of tuple will be used
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        sequence_type = tuple
        other_sequence_type = getattr(
            other, '_sequence_type', self._sequence_type
        )

        if other_sequence_type == self._sequence_type:
            sequence_type = self._sequence_type

        return Attr(merge(self, other), sequence_type=sequence_type)

    def __radd__(self, other):
        """
        Add this Attr to a mapping, creating a new, merged Attr.

        NOTE: Attr is not commutative. a + b != b + a.
        NOTE: If both objects are `Attr`s and have differing sequence
            types, the default value of tuple will be used
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        sequence_type = tuple
        other_sequence_type = getattr(
            other, '_sequence_type', self._sequence_type
        )

        if other_sequence_type == self._sequence_type:
            sequence_type = self._sequence_type

        return Attr(merge(other, self), sequence_type=sequence_type)

    def __repr__(self):
        """
        Return a string representation of the object
        """
        return u"a{0}".format(repr(self._mapping))

    def __getstate__(self):
        """
        Serialize the object.

        NOTE: required to maintain sequence_type.
        """
        return (self._mapping, self._sequence_type)

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        items, sequence_type = state
        self.__init__(items, sequence_type=sequence_type)

    @classmethod
    def _valid_name(cls, name):
        """
        Check whether a key is a valid attribute.

        A key may be used as an attribute if:
          *  It is a string.
          *  It matches /^[A-Za-z][A-Za-z0-9_]*$/ (i.e., public
             attribute).
          *  The key doesn't overlap with any class attributes (for
             Attr, those would be 'get', 'items', 'keys', 'values',
             'mro', and 'register').
        """
        return (
            isinstance(name, StringType) and
            re.match('^[A-Za-z][A-Za-z0-9_]*$', name) and
            not hasattr(cls, name)
        )

    @classmethod
    def _build(cls, obj, sequence_type=tuple):
        """
        Create an Attr version of an object. Any Mapping object will be
        converted to an Attr, and if sequence_type is not None, any
        non-(string/bytes) object will be converted to sequence_type,
        with any contained Mappings being converted to Attr.
        """
        if isinstance(obj, Mapping):
            if hasattr(cls, '_constructor'):
                constructor = cls._constructor
            else:
                constructor = cls

            obj = constructor(obj, sequence_type=sequence_type)
        elif (isinstance(obj, Sequence) and
              not isinstance(obj, (StringType, bytes)) and
              sequence_type is not None):
            obj = sequence_type(
                cls._build(element, sequence_type=sequence_type)
                for element in obj
            )

        return obj
