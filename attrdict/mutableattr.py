"""
A subclass of Attr that implements MutableMapping.
"""
from collections import MutableMapping

from attrdict.attr import Attr


class MutableAttr(Attr, MutableMapping):
    """
    A subclass of Attr that implements MutableMapping.
    """
    # def pop(self, key, default=None):
    #     value = default

    #     if key in self._mapping:
    #         value = self._mapping[key]
    #         del self[key]

    #     return value

    def __setattr__(self, key, value, force=False):
        """
        Add an attribute to the instance. The attribute will only be
        added if force is set to True.
        """
        if force:
            super(MutableAttr, self).__setattr__(key, value, force=force)
        else:
            if not self._valid_name(key):
                raise TypeError("Invalid key: {0}".format(repr(key)))

            self._set(key, value)

    def __delattr__(self, key):
        """
        Delete an attribute.
        """
        if not self._valid_name(key) or key not in self._mapping:
            raise TypeError("Invalid key: {0}".format(repr(key)))

        self._delete(key)

    def __setitem__(self, key, value):
        """
        Add a key-value pair to the instance.
        """
        self._set(key, value)

    def __getitem__(self, key):
        """
        Get a value associated with a key.
        """
        return self._mapping[key]

    def __delitem__(self, key):
        """
        Delete a key-value pair
        """
        self._delete(key)

    def _delete(self, key):
        """
        Delete an item from the MutableAttr.

        key: The key to delete.
        """
        del self._mapping[key]

        if self._valid_name(key):
            super(MutableAttr, self).__delattr__(key, True)
