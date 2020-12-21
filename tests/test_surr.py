"""
UILAAT Surrogate Helper Function Tests

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

from json import JSONDecoder, JSONEncoder
from unittest import TestCase

from uilaat import surr

je = JSONEncoder()
jd = JSONDecoder()

class SurrTests(TestCase):
    """
    Tests for surr() in the main module
    """
    
    def test_surr_smp1(self):
        """
        Correctness of surrogate generation for first 255 SMP code points
        """
        chars = [chr(i) for i in range(0x10000, 0x10100)]
        surrs = [surr(c) for c in chars]
        zt = zip(surrs, chars)
        for t in zt:
            with self.subTest(surr=t[0]):
                # Using the json library for verifying surrogate conversions
                # is a lazy but effective hack. In particular, JSONDecoder
                # automatically converts surrogates, making comparisons easy.
                self.assertEqual(t[1], jd.decode(je.encode(t[0])))

    def test_surr_smp2(self):
        """
        Correctness of surrogate generation for first 255 SIP code points
        """
        chars = [chr(i) for i in range(0x20000, 0x20100)]
        surrs = [surr(c) for c in chars]
        zt = zip(surrs, chars)
        for t in zt:
            with self.subTest(surr=t[0]):
                self.assertEqual(t[1], jd.decode(je.encode(t[0])))
    
    def test_surr_smp16(self):
        """
        Correctness of surrogate generation for last 255 SPU B code points
        """
        chars = [chr(i) for i in range(0x10FFFF, 0x10FF00, -1)]
        surrs = [surr(c) for c in chars]
        zt = zip(surrs, chars)
        for t in zt:
            with self.subTest(surr=t[0]):
                self.assertEqual(t[1], jd.decode(je.encode(t[0])))

