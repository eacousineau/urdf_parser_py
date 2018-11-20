"""
Python implementation of the URDF parser.
"""

import functools
import warnings


class _NowPrivateDescriptor(object):
    def __init__(self, private):
        self._private = private
        self.__doc__ = "Deprecated propery"

    def _warn(self):
        non_private = self._private.lstrip('_')
        warnings.warn(
            "{} is now private; please do not use.".format(non_private),
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
