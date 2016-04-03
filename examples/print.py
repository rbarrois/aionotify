#!/usr/bin/env python
# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.


import aionotify
import argparse
import asyncio
import logging
import signal


class Example:
    def __init__(self):
        self.loop = None
        self.watcher = None
        self.task = None

    def prepare(self, path):
        self.watcher = aionotify.Watcher()
        self.watcher.watch(path, aionotify.Flags.MODIFY | aionotify.Flags.CREATE | aionotify.Flags.DELETE)

    @asyncio.coroutine
    def _run(self, max_events):
        yield from self.watcher.setup(self.loop)
        for _i in range(max_events):
            event = yield from self.watcher.get_event()
            print(event.name, aionotify.Flags.parse(event.flags))
        self.shutdown()

    def run(self, loop, max_events):
        self.loop = loop
        self.task = loop.create_task(self._run(max_events))

    def shutdown(self):
        self.watcher.close()
        if self.task is not None:
            self.task.cancel()
        self.loop.stop()


def setup_signal_handlers(loop, example):
    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, example.shutdown)


def main(args):
    if args.debug:
        logger = logging.getLogger('asyncio')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    example = Example()
    example.prepare(args.path)

    loop = asyncio.get_event_loop()
    if args.debug:
        loop.set_debug(True)

    setup_signal_handlers(loop, example)
    example.run(loop, args.events)

    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Path to watch")
    parser.add_argument('--events', default=10, type=int, help="Number of arguments before shutdown")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable asyncio debugging.")

    args = parser.parse_args()
    main(args)
