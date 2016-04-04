# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

import asyncio
import asyncio.streams
import collections
import ctypes
import struct

from . import aioutils

Event = collections.namedtuple('Event', ['flags', 'cookie', 'name', 'alias'])


_libc = ctypes.cdll.LoadLibrary('libc.so.6')


class LibC:
    """Proxy to C functions for inotify"""
    @classmethod
    def inotify_init(cls):
        return _libc.inotify_init()

    @classmethod
    def inotify_add_watch(cls, fd, path, flags):
        return _libc.inotify_add_watch(fd, path.encode('utf-8'), flags)

    @classmethod
    def inotify_rm_watch(cls, fd, wd):
        return _libc.inotify_rm_watch(fd, wd)


PREFIX = struct.Struct('iIII')


class Watcher:

    def __init__(self):
        self.requests = {}
        self._reset()

    def _reset(self):
        self.descriptors = {}
        self.aliases = {}
        self._stream = None
        self._transport = None
        self._fd = None
        self._loop = None

    def watch(self, path, flags, *, alias=None):
        """Add a new watching rule."""
        if alias is None:
            alias = path
        if alias in self.requests:
            raise ValueError("A watch request is already scheduled for alias %s" % alias)
        self.requests[alias] = (path, flags)
        if self._fd is not None:
            # We've started, register the watch immediately.
            self._setup_watch(alias, path, flags)

    def unwatch(self, alias):
        """Stop watching a given rule."""
        if alias not in self.descriptors:
            raise ValueError("Unknown watch alias %s; current set is %r" % (alias, list(self.descriptors.keys())))
        wd = self.descriptors[alias]
        errno = LibC.inotify_rm_watch(self._fd, wd)
        if errno != 0:
            raise IOError("Failed to close watcher %d: errno=%d" % (wd, errno))
        del self.descriptors[alias]
        del self.requests[alias]
        del self.aliases[wd]

    def _setup_watch(self, alias, path, flags):
        """Actual rule setup."""
        assert alias not in self.descriptors, "Registering alias %s twice!" % alias
        wd = LibC.inotify_add_watch(self._fd, path, flags)
        if wd < 0:
            raise IOError("Error setting up watch on %s with flags %s: wd=%s" % (
                path, flags, wd))
        self.descriptors[alias] = wd
        self.aliases[wd] = alias

    @asyncio.coroutine
    def setup(self, loop):
        """Start the watcher, registering new watches if any."""
        self._loop = loop

        self._fd = LibC.inotify_init()
        for alias, (path, flags) in self.requests.items():
            self._setup_watch(alias, path, flags)

        # We pass ownership of the fd to the transport; it will close it.
        self._stream, self._transport = yield from aioutils.stream_from_fd(self._fd, loop)

    def close(self):
        """Schedule closure.

        This will close the transport and all related resources.
        """
        self._transport.close()
        self._reset()

    @property
    def closed(self):
        """Are we closed?"""
        return self._transport is None

    @asyncio.coroutine
    def get_event(self):
        """Fetch an event.

        This coroutine will swallow events for removed watches.
        """
        while True:
            prefix = yield from self._stream.readexactly(PREFIX.size)
            if prefix == b'':
                # We got closed, return None.
                return
            wd, flags, cookie, length = PREFIX.unpack(prefix)
            path = yield from self._stream.readexactly(length)

            # All async performed, time to look at the event's content.
            if wd not in self.aliases:
                # Event for a removed watch, skip it.
                continue

            decoded_path = struct.unpack('%ds' % length, path)[0].rstrip(b'\x00').decode('utf-8')
            return Event(
                flags=flags,
                cookie=cookie,
                name=decoded_path,
                alias=self.aliases[wd],
            )
