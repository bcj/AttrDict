"""
A subclass of MutableAttr that has defaultdict support.
"""
from collections import Mapping

from attrdict.mixins import MutableAttr


class AttrDefault(MutableAttr):
    """
    An implementation of MutableAttr with defaultdict support
    """
    def __init__(self, default_factory=None, items=None, sequence_type=tuple,
                 pass_key=False):
        if items is None:
            items = {}
        elif not isinstance(items, Mapping):
            items = dict(items)

        self.__setattr__('_default_factory', default_factory, force=True)
        self.__setattr__('_mapping', items, force=True)
        self.__setattr__('_sequence_type', sequence_type, force=True)
        self.__setattr__('_pass_key', pass_key, force=True)
        self.__setattr__('_allow_invalid_attributes', False, force=True)

    def _configuration(self):
        """
        The configuration for a AttrDefault instance
        """
        return self._sequence_type, self._default_factory, self._pass_key

    def __getitem__(self, key):
        """
        Access a value associated with a key.

        Note: values returned will not be wrapped, even if recursive
        is True.
        """
        if key in self._mapping:
            return self._mapping[key]
        elif self._default_factory:
            return self.__missing__(key)

        raise KeyError(key)

    def __setitem__(self, key, value):
        """
        Add a key-value pair to the instance.
        """
        self._mapping[key] = value

    def __delitem__(self, key):
        """
        Delete a key-value pair
        """
        del self._mapping[key]

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

    def __getattr__(self, key):
        """
        Access a key-value pair as an attribute.
        """
        if self._valid_name(key):
            if key in self:
                return self._build(self._mapping[key])
            elif self._default_factory:
                return self._build(self.__missing__(key))

        raise AttributeError(
            "'{cls}' instance has no attribute '{name}'".format(
                cls=self.__class__.__name__, name=key
            )
        )

    def __missing__(self, key):
        """
        Add a missing element.
        """
        if self._pass_key:
            self._mapping[key] = value = self._default_factory(key)
        else:
            self._mapping[key] = value = self._default_factory()

        return value

    def __getstate__(self):
        """
        Serialize the object.
        """
        return (
            self._default_factory,
            self._mapping,
            self._sequence_type,
            self._pass_key,
            self._allow_invalid_attributes,
        )

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        (default_factory, mapping, sequence_type, pass_key,
         allow_invalid_attributes) = state

        self.__setattr__('_default_factory', default_factory, force=True)
        self.__setattr__('_mapping', mapping, force=True)
        self.__setattr__('_sequence_type', sequence_type, force=True)
        self.__setattr__('_pass_key', pass_key, force=True)
        self.__setattr__(
            '_allow_invalid_attributes',
            allow_invalid_attributes,
            force=True
        )

    @classmethod
    def _constructor(cls, mapping, configuration):
        """
        A standardized constructor.
        """
        sequence_type, default_factory, pass_key = configuration
        return cls(default_factory, mapping, sequence_type=sequence_type,
                   pass_key=pass_key)
