"""
UILAAT RangeIndexedList class Tests

"""
# Copyright © 2020 Moses Chong
#
# This file is part of the UILAAT: The Unicode Interlingual Aesthetic
# Appropriation Toolkit
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from unittest import TestCase
from uilaat import RangeIndexedList

class RangeIndexedListLookupTests(TestCase):
    """
    Tests to verify correctness of RangeIndexedList

    """
    def setUp(self):
        self.range_keys = (5,10,15,20,25,30)
        self.range_keys_b2b = (2,4,5,7,8,10) # back-to-back
        self.range_keys_s = (2,3,6,7,9,10) # short ranges
        self.range_keys_s_b2b = (2,3,4,5,6,7) # short ranges, back-to-back
        self.range_keys_one = (18,35) # single range
        self.range_zero_start_one = (0,10)
        self.range_zero_start_one_s = (0,1)

    def test_getitem(self):
        """
        Lookups on spaced-out ('normal') ranges

        """
        vals = [i for i in range(len(self.range_keys)//2)]
        ril = RangeIndexedList(self.range_keys, vals)

        # NOTE: Please leave this test as it is, as it serves as a
        # transparent reference test.
        self.assertEqual(ril[5], vals[0])
        self.assertEqual(ril[6], vals[0])
        self.assertEqual(ril[9], vals[0])
        self.assertEqual(ril[10], vals[0])
        self.assertEqual(ril[15], vals[1])
        self.assertEqual(ril[16], vals[1])
        self.assertEqual(ril[19], vals[1])
        self.assertEqual(ril[20], vals[1])
        self.assertEqual(ril[25], vals[2])
        self.assertEqual(ril[26], vals[2])
        self.assertEqual(ril[29], vals[2])
        self.assertEqual(ril[30], vals[2])

    def test_getitem_copykey(self):
        """
        Lookup with copy key to output option
        
        """
        ks = self.range_keys_one
        SAY_YES = '\u2713'
        vals = ('\ufffc' + SAY_YES,)
        ril = RangeIndexedList(ks, vals, copy_key=True)

        k = self.range_keys_one[0]
        out_exp = chr(k) + SAY_YES
        self.assertEqual(ril[k], out_exp)

    def test_getitem_lookuperror(self):
        """
        Out-of-range index handling for spaced-out ('normal') ranges

        """
        ks = self.range_keys
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)
        # past small side of ranges
        for i in range(0, len(ks), 2):
            k = ks[i] - 1
            with self.subTest(k=k):
                with self.assertRaises(LookupError):
                    ril[k]
        # past large side of ranges
        for i in range(1, len(ks), 2):
            k = ks[i] + 1
            with self.subTest(k=k):
                with self.assertRaises(LookupError):
                    ril[k]

    def test_getitem_s_b2b(self):
        """
        Lookups on short, back-to-back ranges

        """
        ks = self.range_keys_s_b2b
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        for i in range(len(ks)):
            k = ks[i]
            with self.subTest(k=k):
                self.assertEqual(ril[k], vals[i//2])

    def test_getitem_s_b2b_lookuperror(self):
        """
        Out-of-range index handling for short, back-to-back ranges

        """
        ks = self.range_keys_s_b2b
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(LookupError):
            k = ks[0] - 1
            ril[k]
        with self.assertRaises(LookupError):
            k = ks[-1] + 1
            ril[k]

