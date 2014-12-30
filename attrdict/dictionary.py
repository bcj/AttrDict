"""
A dict that implements MutableAttr.
"""
from attrdict.mixins import MutableAttr


class AttrDict(dict, MutableAttr):
    """
    A dict that implements MutableAttr.
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)

        self.__setattr__('_sequence_type', tuple, force=True)
        self.__setattr__('_allow_invalid_attributes', False, force=True)

    def _configuration(self):
        """
        The configuration for an attrmap instance.
        """
        return self._sequence_type

    def __getstate__(self):
        """
        Serialize the object.
        """
        return (
            self.copy(),
            self._sequence_type,
            self._allow_invalid_attributes
        )

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        mapping, sequence_type, allow_invalid_attributes = state
        self.update(mapping)
        self.__setattr__('_sequence_type', sequence_type, force=True)
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
        attr = cls(mapping)
        attr.__setattr__('_sequence_type', configuration, force=True)

        return attr
