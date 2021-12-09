#!/usr/bin/env python
# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

from typing import Optional, Any
import argparse
import asyncio
from asyncio import AbstractEventLoop, Task
import logging
import signal

import aionotify

from collections import abc


class aenumerate(abc.AsyncIterator):
    """enumerate for async for
    https://pythonwise.blogspot.com/2015/11/aenumerate-enumerate-for-async-for.html
    """

    def __init__(self, aiterable, start=0):
        self._aiterable = aiterable
        self._i = start - 1

    def __aiter__(self):
        self._ait = self._aiterable.__aiter__()
        return self

    async def __anext__(self):
        # self._ait will raise the apropriate AsyncStopIteration
        val = await self._ait.__anext__()
        self._i += 1
        return self._i, val


class Example:
    def __init__(self, path: str):
        self.loop: Optional[AbstractEventLoop] = None
        self.task: Optional[Task[Any]] = None
        self.watcher = aionotify.Watcher()
        self.watcher.watch(
            path,
            aionotify.Flags.MODIFY
            | aionotify.Flags.CREATE
            | aionotify.Flags.DELETE)

    async def _run(self, max_events: int):
        async for i, event in aenumerate(self.watcher, start=1):
            print(event.name, aionotify.Flags.parse(event.flags))
            if i == max_events:
                break
        self.shutdown()

    def run(self, max_events: int, loop: Optional[AbstractEventLoop] = None):
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self.task = self.loop.create_task(self._run(max_events))

    def shutdown(self):
        try:
            self.watcher.close()
        except Exception:
            pass
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

    example = Example(args.path)

    loop = asyncio.get_event_loop()
    if args.debug:
        loop.set_debug(True)

    setup_signal_handlers(loop, example)
    example.run(args.events, loop)

    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Path to watch")
    parser.add_argument('-c', '--events', default=10, type=int, help="Number of arguments before shutdown")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable asyncio debugging.")

    args = parser.parse_args()
    main(args)
