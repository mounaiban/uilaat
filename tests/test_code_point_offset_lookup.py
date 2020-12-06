"""
UILAAT CodePointOffsetLookup class Tests

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
from uilaat import CodePointOffsetLookup

class EqTests(TestCase):
    """
    Tests to verify correctness of equality operator

    """
    def test_eq(self):
        args = (33, 127, 65248)
        cpoff_a = CodePointOffsetLookup(*args)
        cpoff_b = CodePointOffsetLookup(*args)

        self.assertNotEqual(id(cpoff_a), id(cpoff_b))
        self.assertEqual(cpoff_a, cpoff_b)

    def test_eq_not_equal(self):
        args_a = (33, 127, 65248)
        args_b = (65, 90, 119473)
        cpoff_a = CodePointOffsetLookup(*args_a)
        cpoff_b = CodePointOffsetLookup(*args_b)

        # nearly-identical args as cpoff_b
        args_c = (65, 90, 119951)
        cpoff_c = CodePointOffsetLookup(*args_c)

        self.assertNotEqual(cpoff_a, cpoff_b)
        self.assertNotEqual(cpoff_b, cpoff_c)

