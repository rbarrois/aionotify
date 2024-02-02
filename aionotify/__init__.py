# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

from importlib.metadata import version

from .enums import Flags
from .base import Watcher

__all__ = ['Flags', 'Watcher']


__version__ = version("aionotify")
__author__ = 'Raphaël Barrois <raphael.barrois+aionotify@polytechnique.org>'
