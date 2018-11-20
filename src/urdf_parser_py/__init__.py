"""
Python implementation of the URDF parser.
"""

import functools
import warnings


class _NowPrivateDescriptor(object):
    # Implements the descriptor interface to warn about deprecated access.
    def __init__(self, private):
        self._private = private
        self._old_public = self._private.lstrip('_')
        self.__doc__ = "Deprecated propery '{}'".format(self._old_public)

    def _warn(self):
        warnings.warn(
            "'{}' is deprecated, and will be removed in future releases."
                .format(self._old_public),
            category=DeprecationWarning, stacklevel=2)

    def __get__(self, obj, objtype):
        self._warn()
        if obj is None:
            return getattr(objtype, self._private)
        else:
            return getattr(obj, self._private)

    def __set__(self, obj, value):
        self._warn()
        setattr(obj, self._private, value)

    def __del__(self, obj):
        self._warn()
        delattr(obj, self._private)


def _now_private_property(private):
    # Indicates that a property (or method) is now private.
    return _NowPrivateDescriptor(private)
