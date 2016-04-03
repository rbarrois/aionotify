import asyncio
import asyncio.streams
import collections
import ctypes
import enum
import struct
import os

Event = collections.namedtuple('Event', ['event_mask', 'cookie', 'name'])


_libc = ctypes.cdll.LoadLibrary('libc.so.6')

class INotifyProxy:
    """Proxy to C functions for inotify"""
    @classmethod
    def inotify_init(cls):
        return _libc.inotify_init()

    @classmethod
    def inotify_add_watch(cls, fd, path, flags):
        return _libc.inotify_add_watch(fd, path.encode('utf-8'), flags)


class FDProxy:
    SIZE = 1024
    def __init__(self, fd, stream_reader):
        self.fd = fd
        self.reader = stream_reader

    def read_ready(self):
        try:
            data = os.read(self.fd, self.SIZE)
        except OSError:
            asyncio.get_event_loop().remove_reader(self.fd)
            raise
        if data:
            self.reader.feed_data(data)
        else:
            self.reader.feed_eof()


class INotifyStream:

    PREFIX = struct.Struct('iIII')

    def __init__(self, path, events):
        self.path = path
        self.events = events
        self._stream = None
        self._disconnect = False
        self._fd = None
        self._wd = None

    def setup(self):
        self._fd = INotifyProxy.inotify_init()
        self._wd = INotifyProxy.inotify_add_watch(self._fd, self.path, self.events)
        if self._wd < 0:
            raise IOError("Got wd %s" % self._wd)
        self._stream = asyncio.streams.StreamReader()
        proxy = FDProxy(self._fd, self._stream)
        loop = asyncio.get_event_loop()
        loop.add_reader(self._fd, proxy.read_ready)

    def schedule_shutdown(self):
        self._disconnect = True

    @asyncio.coroutine
    def get_event(self):
        prefix = yield from self._stream.readexactly(self.PREFIX.size)
        if prefix == b'':
            return
        wd, event_mask, cookie, length = self.PREFIX.unpack(prefix)
        # assert wd == self._wd, "Received an event for another watch descriptor, %s"
        path = yield from self._stream.readexactly(length)
        if path == b'':
            return
        decoded_path = struct.unpack('%ds' % length, path)[0].rstrip(b'\x00').decode('utf-8')
        return Event(
            event_mask=event_mask,
            cookie=cookie,
            name=decoded_path,
        )


class flags(enum.IntEnum):
    ACCESS = 0x00000001  #: File was accessed
    MODIFY = 0x00000002  #: File was modified
    ATTRIB = 0x00000004  #: Metadata changed
    CLOSE_WRITE = 0x00000008  #: Writable file was closed
    CLOSE_NOWRITE = 0x00000010  #: Unwritable file closed
    OPEN = 0x00000020  #: File was opened
    MOVED_FROM = 0x00000040  #: File was moved from X
    MOVED_TO  = 0x00000080  #: File was moved to Y
    CREATE = 0x00000100  #: Subfile was created
    DELETE = 0x00000200  #: Subfile was deleted
    DELETE_SELF = 0x00000400  #: Self was deleted
    MOVE_SELF = 0x00000800  #: Self was moved

    UNMOUNT = 0x00002000  #: Backing fs was unmounted
    Q_OVERFLOW = 0x00004000  #: Event queue overflowed
    IGNORED = 0x00008000  #: File was ignored

    ONLYDIR = 0x01000000  #: only watch the path if it is a directory
    DONT_FOLLOW = 0x02000000  #: don't follow a sym link
    EXCL_UNLINK = 0x04000000  #: exclude events on unlinked objects
    MASK_ADD = 0x20000000  #: add to the mask of an already existing watch
    ISDIR = 0x40000000  #: event occurred against dir
    ONESHOT = 0x80000000  #: only send event once

    @classmethod
    def from_mask(cls, mask):
        return [flag for flag in cls.__members__.values() if flag & mask]

@asyncio.coroutine
def run():
    stream = INotifyStream('/tmp/inotify', flags.CREATE)
    stream.setup()

    for _i in range(10):
        event = yield from stream.get_event()
        print(event)
    stream.schedule_shutdown()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


main()
