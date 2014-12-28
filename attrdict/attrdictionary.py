"""
A subclass of MutableAttr that works as a drop-in replacement of dict
"""
from collections import Mapping
import copy
from sys import version_info

from attrdict.mutableattr import MutableAttr
from attrdict.two_three import PYTHON_2


class AttrDict(MutableAttr):
    """
    A subclass of MutableAttr that works as a drop-in replacement of
    dict.

    NOTE: AttrDict does not subclass dict. This is not a stylistic
        decision, CPython's dict implementation makes this functionally
        impossible. The CPython function `PyDict_Merge` (found in
        Objects/dictobject.c) uses the macro `PyDict_Check` (found in
        Include/dictobject.h) to see whether it can do some
        optimizations during merge. If you subclass dict, The merge
        won't actually iterate over the items in AttrDict. This means
        operations such as **attrdict will not actually work.

        This shouldn't matter though, as code that is doing type checks
        against dict is wrong (e.g., defaultdict, OrderedDict, etc.
        don't subclass dict). If you need to typecheck, you should be
        checking against collections.Mapping or
        collections.MutableMapping. In the worst-case scenario, remember
        that isinstance can take a tuple of types.
    """
    def __init__(self, items=None, **kwargs):
        if items is None:
            items = ()

        # items may be an iterable of two-tuples, or a mapping.
        if isinstance(items, Mapping):
            mapping = items
        else:
            mapping = dict(items)

        for key in kwargs:
            mapping[key] = kwargs[key]

        super(AttrDict, self).__init__(mapping)

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        items, sequence_type = state
        self.__init__(items)
        self.__setattr__('_sequence_type', sequence_type, force=True)

    def copy(self):
        """
        Make a (shallow) copy of the AttrDict
        """
        return copy.copy(self)

    if PYTHON_2:
        def has_key(self, key):
            """
            Test for the presence of key in the dictionary.
            has_key() is deprecated in favor of key in d.
            """
            return key in self

        def iteritems(self):
            """
            Iterate over items in the mapping.
            """
            for key in self:
                yield key, self[key]

        def iterkeys(self):
            """
            Iterate over keys in the mapping.
            """
            for key in self:
                yield key

        def itervalues(self):
            """
            Iterate over values in the mapping.
            """
            for key in self:
                yield self[key]

        if version_info >= (2, 7):
            def viewitems(self):
                """
                Get a view of the items.
                """
                if hasattr(self._mapping, 'viewitems'):
                    return self._mapping.viewitems()
                else:
                    return dict(self._mapping).viewitems()

            def viewkeys(self):
                """
                Get a view of the keys.
                """
                if hasattr(self._mapping, 'viewkeys'):
                    return self._mapping.viewkeys()
                else:
                    return dict(self._mapping).viewkeys()

            def viewvalues(self):
                """
                Get a view of the values.
                """
                if hasattr(self._mapping, 'viewvalues'):
                    return self._mapping.viewvalues()
                else:
                    return dict(self._mapping).viewvalues()

    @classmethod
    def fromkeys(cls, seq, value=None):
        """
        Create a new dictionary with keys from seq and values set to
        value.
        """
        return cls((key, value) for key in seq)

    @classmethod
    def _constructor(cls, items=None, sequence_type=tuple):
        """
        A constructor for AttrDict that respects sequence_type
        """
        mapping = cls(items)
        mapping.__setattr__('_sequence_type', sequence_type, force=True)

        return mapping
