# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

import asyncio
import logging
import os
import os.path
import tempfile
import unittest

import aionotify


AIODEBUG = bool(os.environ.get('PYTHONAIODEBUG') == '1')


if AIODEBUG:
    logger = logging.getLogger('asyncio')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


TESTDIR = os.environ.get('AIOTESTDIR') or os.path.join(os.path.dirname(__file__), 'testevents')


class AIONotifyTestCase(unittest.IsolatedAsyncioTestCase):
    timeout = 3

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        if AIODEBUG:
            self.loop.set_debug(True)
        self.watcher = aionotify.Watcher()
        self._testdir = tempfile.TemporaryDirectory(dir=TESTDIR)
        self.testdir = self._testdir.name

        # Schedule a loop shutdown
        self.loop.call_later(self.timeout, self.loop.stop)

    def tearDown(self):
        if not self.watcher.closed:
            self.watcher.close()
        self._testdir.cleanup()
        self.assertFalse(os.path.exists(self.testdir))

    # Utility functions
    # =================

    # Those allow for more readable tests.

    def _touch(self, filename, *, parent=None):
        path = os.path.join(parent or self.testdir, filename)
        with open(path, 'w') as f:
            f.write('')

    def _unlink(self, filename, *, parent=None):
        path = os.path.join(parent or self.testdir, filename)
        os.unlink(path)

    def _rename(self, source, target, *, parent=None):
        source_path = os.path.join(parent or self.testdir, source)
        target_path = os.path.join(parent or self.testdir, target)
        os.rename(source_path, target_path)

    def _assert_file_event(self, event, name, flags=aionotify.Flags.CREATE, alias=None):
        """Check for an expected file event.

        Allows for more readable tests.
        """
        if alias is None:
            alias = self.testdir

        self.assertEqual(name, event.name)
        self.assertEqual(flags, event.flags)
        self.assertEqual(alias, event.alias)

    async def _assert_no_events(self, timeout=0.1):
        """Ensure that no events are left in the queue."""
        task = self.watcher.get_event()
        try:
            result = await asyncio.wait_for(task, timeout)
        except asyncio.TimeoutError:
            # All fine: we didn't receive any event.
            pass
        else:
            raise AssertionError("Event %r occurred within timeout %s" % (result, timeout))


class SimpleUsageTests(AIONotifyTestCase):

    async def test_watch_before_start(self):
        """A watch call is valid before startup."""
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        await self.watcher.setup(self.loop)

        # Touch a file: we get the event.
        self._touch('a')
        event = await self.watcher.get_event()
        self._assert_file_event(event, 'a')

        # And it's over.
        await self._assert_no_events()

    async def test_watch_before_start_default_loop(self):
        """A watch call is valid before startup."""
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        await self.watcher.setup()

        # Touch a file: we get the event.
        self._touch('a')
        event = await self.watcher.get_event()
        self._assert_file_event(event, 'a')

        # And it's over.
        await self._assert_no_events()

    async def test_watch_after_start(self):
        """A watch call is valid after startup."""
        await self.watcher.setup(self.loop)
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)

        # Touch a file: we get the event.
        self._touch('a')
        event = await self.watcher.get_event()
        self._assert_file_event(event, 'a')

        # And it's over.
        await self._assert_no_events()

    async def test_event_ordering(self):
        """Events should arrive in the order files where created."""
        await self.watcher.setup(self.loop)
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)

        # Touch 2 files
        self._touch('a')
        self._touch('b')

        # Get the events
        event1 = await self.watcher.get_event()
        event2 = await self.watcher.get_event()
        self._assert_file_event(event1, 'a')
        self._assert_file_event(event2, 'b')

        # And it's over.
        await self._assert_no_events()

    async def test_filtering_events(self):
        """We only get targeted events."""
        await self.watcher.setup(self.loop)
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        self._touch('a')
        event = await self.watcher.get_event()
        self._assert_file_event(event, 'a')

        # Perform a filtered-out event; we shouldn't see anything
        self._unlink('a')
        await self._assert_no_events()

    async def test_watch_unwatch(self):
        """Watches can be removed."""
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        await self.watcher.setup(self.loop)

        self.watcher.unwatch(self.testdir)
        await asyncio.sleep(0.1)

        # Touch a file; we shouldn't see anything.
        self._touch('a')
        await self._assert_no_events()

    async def test_watch_unwatch_before_drain(self):
        """Watches can be removed, no events occur afterwards."""
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        await self.watcher.setup(self.loop)

        # Touch a file before unwatching
        self._touch('a')
        self.watcher.unwatch(self.testdir)

        # We shouldn't see anything.
        await self._assert_no_events()

    async def test_rename_detection(self):
        """A file rename can be detected through event cookies."""
        self.watcher.watch(self.testdir, aionotify.Flags.MOVED_FROM | aionotify.Flags.MOVED_TO)
        await self.watcher.setup(self.loop)
        self._touch('a')

        # Rename a file => two events
        self._rename('a', 'b')
        event1 = await self.watcher.get_event()
        event2 = await self.watcher.get_event()

        # We got moved_from then moved_to; they share the same cookie.
        self._assert_file_event(event1, 'a', aionotify.Flags.MOVED_FROM)
        self._assert_file_event(event2, 'b', aionotify.Flags.MOVED_TO)
        self.assertEqual(event1.cookie, event2.cookie)

        # And it's over.
        await self._assert_no_events()


class ErrorTests(AIONotifyTestCase):
    """Test error cases."""

    async def test_watch_nonexistent(self):
        """Watching a non-existent directory raises an OSError."""
        badpath = os.path.join(self.testdir, 'nonexistent')
        self.watcher.watch(badpath, aionotify.Flags.CREATE)
        with self.assertRaises(OSError):
            await self.watcher.setup(self.loop)

    async def test_unwatch_bad_alias(self):
        self.watcher.watch(self.testdir, aionotify.Flags.CREATE)
        await self.watcher.setup(self.loop)
        with self.assertRaises(ValueError):
            self.watcher.unwatch('blah')


class SanityTests(AIONotifyTestCase):
    timeout = 0.1

    @unittest.expectedFailure
    async def test_timeout_works(self):
        """A test cannot run longer than the defined timeout."""
        # This test should fail, since we're setting a global timeout of 0.1 yet ask to wait for 0.3 seconds.
        await asyncio.sleep(0.5)
