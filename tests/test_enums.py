# Copyright (c) 2016 The aionotify project
# This code is distributed under the two-clause BSD License.

import unittest

import aionotify


class EnumsTests(unittest.TestCase):
    def test_parsing(self):
        Flags = aionotify.Flags

        flags = Flags.ACCESS | Flags.MODIFY | Flags.ATTRIB

        parsed = Flags.parse(flags)
        self.assertEqual([Flags.ACCESS, Flags.MODIFY, Flags.ATTRIB], parsed)
