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

# TODO: these tests are done with integer keys

from unittest import TestCase
from uilaat import RangeIndexedList

class DoIndexTests(TestCase):
    """
    Tests to verify range key index lookups
    Please see RangeIndexedList._do_index() for details

    """
    def test_doindex(self):
        ks = (18,35,60,120)
        ril = RangeIndexedList(ks)

        i = ril._do_index(18)
        self.assertEqual(i, (0,True,))
        ii = ril._do_index(35)
        self.assertEqual(ii, (1,True,))
        iii = ril._do_index(60)
        self.assertEqual(iii, (2,True,))
        iiii = ril._do_index(120)
        self.assertEqual(iiii, (3,True,))

    def test_doindex_not_found(self):
        ks = (18,35,60,120)
        ril = RangeIndexedList(ks)

        i = ril._do_index(17)
        self.assertEqual(i, (0,False,))
        ii = ril._do_index(34)
        self.assertEqual(ii, (1,False,))
        iii = ril._do_index(59)
        self.assertEqual(iii, (2,False,))
        iiii = ril._do_index(119)
        self.assertEqual(iiii, (3,False,))
        v = ril._do_index(121)
        self.assertEqual(v, (4,False,))

class EqTests(TestCase):
    """
    Tests to verify correctness of the equality operator

    """
    def test_eq(self):
        """
        Equality between RILs with default options

        """
        ks = (18,35,60,120)
        vals = ('c1','c2')
        ril_a = RangeIndexedList(ks, vals)
        ril_b = RangeIndexedList(ks, vals)

        self.assertEqual(ril_a, ril_b)

    def test_eq_kwargs(self):
        """
        Equality between RILs with options set

        """
        ks = (18,35,60,120)
        vals = ('c1','c2')
        ril_a = RangeIndexedList(ks, vals, copy_key=True,)
        ril_b = RangeIndexedList(ks, vals, copy_key=True,)

        self.assertEqual(ril_a, ril_b)

    def test_eq_not_equal_keys(self):
        """
        Equality between RILs with mismatched keys

        """
        ks_a = (18,35,60,120)
        ks_b = (2,3,4,5)
        vals = ('c1','c2')
        ril_a = RangeIndexedList(ks_a, vals)
        ril_b = RangeIndexedList(ks_b, vals)

        self.assertNotEqual(ril_a, ril_b)

    def test_eq_not_equal_vals(self):
        """
        Equality between RILs with mismatched values

        """
        ks = (18,35,60,120)
        vals_a = ('c1','c2')
        vals_b = ('ad1','ad2')
        ril_a = RangeIndexedList(ks, vals_a)
        ril_b = RangeIndexedList(ks, vals_b)

        self.assertNotEqual(ril_a, ril_b)

class GetitemTests(TestCase):
    """
    Tests to verify correctness of value lookups

    """
    def setUp(self):
        self.bounds = (5,10,15,20,25,30)
        self.bounds_pt = (5,10,15,15,25,30) # with point
        self.bounds_b2b = (2,4,5,7,8,10) # back-to-back
        self.bounds_b2b_pt = (2,4,5,5,6,8) # back-to-back with point
        self.bounds_s = (2,3,6,7,9,10) # short ranges
        self.bounds_s_pt = (2,3,6,6,9,10) # short ranges with point
        self.bounds_s_b2b = (2,3,4,5,6,7) # short ranges, back-to-back
        self.bounds_s_b2b_pt = (2,3,4,4,6,7) # short ranges, b2b with point
        self.bounds_one = (18,35) # single range
        self.bounds_one_pt = (18,18) # single point
        self.range_zero_start_one = (0,10)
        self.range_zero_start_one_s = (0,1) # back-to-back from zero
        self.range_zero_start_one_pt = (0,0) # single point at zero

    def test_getitem(self):
        """
        Lookups on spaced-out ('normal') ranges

        """
        vals = [i for i in range(len(self.bounds)//2)]
        ril = RangeIndexedList(self.bounds, vals)

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

    def test_getitem_none_shared_copykey(self):
        """
        Lookup a shared None value when copy_key is enabled

        """
        vals = [None,]
        ril = RangeIndexedList(self.bounds, vals, copy_key=True)

        for i in range(0, len(self.bounds), 2):
            ks = self.bounds[i]
            ke = self.bounds[i+1]
            km = ks + (ke-ks)//2  # mid point between range start & end
            with self.subTest(ks=ks):
                self.assertEqual(ril[ks], None)
                self.assertEqual(ril[ke], None)
                self.assertEqual(ril[km], None)

    def test_getitem_copykey(self):
        """
        Lookup with copy key to output option

        """
        ks = self.bounds_one
        SAY_YES = '\u2713'
        vals = ('\ufffc' + SAY_YES,)
        ril = RangeIndexedList(ks, vals, copy_key=True)

        k = self.bounds_one[0]
        out_exp = chr(k) + SAY_YES
        self.assertEqual(ril[k], out_exp)

    def test_getitem_lookuperror(self):
        """
        Out-of-range index handling for spaced-out ('normal') ranges

        """
        ks = self.bounds
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

    def test_getitem_shared(self):
        """
        Lookups on multiple ranges with one value

        """
        ks = self.bounds
        vals = ('same',)
        ril = RangeIndexedList(ks, vals)

        ks_test = (5,6,9,10,15,16,19,20,25,26,29,30)
        for k in ks_test:
            with self.subTest(k=k):
                self.assertEqual(ril[k], vals[0])

    def test_getitem_short_b2b(self):
        """
        Lookups on short, back-to-back ranges

        """
        ks = self.bounds_s_b2b
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        for i in range(len(ks)):
            k = ks[i]
            with self.subTest(k=k):
                self.assertEqual(ril[k], vals[i//2])

    def test_getitem_short_b2b_pt(self):
        """
        Lookups on short, back-to-back ranges with point

        """
        ks = self.bounds_s_b2b_pt
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        for i in range(len(ks)):
            k = ks[i]
            with self.subTest(k=k):
                self.assertEqual(ril[k], vals[i//2])

    def test_getitem_short_b2b_lookuperror(self):
        """
        Out-of-range index handling for short, back-to-back ranges

        """
        ks = self.bounds_s_b2b
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(LookupError):
            k = ks[0] - 1
            ril[k]
        with self.assertRaises(LookupError):
            k = ks[-1] + 1
            ril[k]

    def test_getitem_one_pt(self):
        """
        Lookups on lone point

        """
        ks = self.bounds_one_pt
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        for i in range(len(ks)):
            k = ks[i]
            with self.subTest(k=k):
                self.assertEqual(ril[k], vals[i//2])

class InsertTests(TestCase):
    """
    Tests to verify correctness of range insertions

    """
    # TODO: Add more input validation tests
    def test_insert(self):
        """
        Insert new range between two ranges

        """
        ks = (5,10,30,35)
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        new_range = (15,25)
        ril.insert(new_range, (42,))

        rks_exp = [5,10,15,25,30,35]
        self.assertEqual(ril._bounds, rks_exp)
        rvals_exp = [0,42,1]
        self.assertEqual(ril._values, rvals_exp)

    def test_insert_large_side(self):
        """
        Insert new range after last range

        """
        ks = (5,10,30,35)
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        new_range = (36,48)
        ril.insert(new_range, (42,))

        rks_exp = [5,10,30,35,36,48]
        self.assertEqual(ril._bounds, rks_exp)
        rvals_exp = [0,1,42]
        self.assertEqual(ril._values, rvals_exp)

    def test_insert_small_side(self):
        """
        Insert new range before first range

        """
        ks = (5,10,30,35)
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        new_range = (0,3)
        ril.insert(new_range, (42,))

        rks_exp = [0,3,5,10,30,35]
        self.assertEqual(ril._bounds, rks_exp)
        rvals_exp = [42,0,1]
        self.assertEqual(ril._values, rvals_exp)

    def test_insert_overlap_bridge(self):
        """
        Handle attempt to insert overlapping range (start & end in other ranges)

        """
        ks = [5,10,30,35]   # keep as a list, assertion needs matched types
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (4,31)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)

    def test_insert_overlap_small_end(self):
        """
        Handle attempt to insert overlapping range (start in another range)

        """
        ks = [5,10,30,35]   # keep as a list, assertion needs matched types
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (6,28)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)

    def test_insert_overlap_large_end(self):
        """
        Handle attempt to insert overlapping range (end in another range)

        """
        ks = [5,10,30,35]
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (12,36)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)

    def test_insert_overlap_whole_range(self):
        """
        Handle attempt to insert range wholly overlapping another

        """
        ks = [5,10,30,35]
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (29,36)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)

    def test_insert_overlap_whole_range_one(self):
        """
        Handle attempt to insert range wholly overlapping lone range

        """
        ks = [5,10]
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (4,12)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)

    def test_insert_overlap_within_range(self):
        """
        Handle attempt to insert range within another

        """
        ks = [5,10]
        vals = [i for i in range(len(ks)//2)]
        ril = RangeIndexedList(ks, vals)

        with self.assertRaises(ValueError):
            new_range = (7,9)
            ril.insert(new_range)
        self.assertEqual(ril._bounds, ks)
        self.assertEqual(ril._values, vals)


