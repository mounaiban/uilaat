"""
UILAAT TranslationDict class Tests

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
from uilaat import TranslationDict, SUBPOINT

# Test Resources
FANCY_A = '\u1555'
FANCY_Bm = '\u18b5\u15ff'
DEFAULT_OUT = SUBPOINT + '\u20e0'  # put circle-slash over chars
dict_plain = {'a':FANCY_A, 'b':FANCY_Bm,}
dict_with_default = { 'a':FANCY_A, 'b':FANCY_Bm, '':DEFAULT_OUT,}
dict_with_none_default = { 'a':FANCY_A, 'b':FANCY_Bm, '':None,}

class GetitemTests(TestCase):
    """
    Tests to verify correctness of lookup output of TranslationDict
    """
    clsc = TranslationDict      # clsc => candidate class

    def test_getitem(self):
        """
        Look up chars found in dict
        """
        tdict_a = self.clsc.from_dict(dict_plain)   # tdict => test dict
        out_single = tdict_a[ord('a')]
        out_multi = tdict_a[ord('b')]

        self.assertEqual(out_single, FANCY_A)
        self.assertEqual(out_multi, FANCY_Bm)

    def test_getitem_not_found(self):
        """
        Look up chars _not found in dict
        """
        tdict_a = self.clsc.from_dict(dict_plain)
        out_nf = tdict_a[ord('\uffff')]
        self.assertEqual(out_nf, '\uffff')
        # PROTIP: Unicode non-characters can be used for testing

    def test_getitem_default(self):
        """
        Look up chars found in dict with default output
        """
        tdict_d = self.clsc.from_dict(dict_with_default)
        out_single = tdict_d[ord('a')]
        out_multi = tdict_d[ord('b')]

        self.assertEqual(out_single, FANCY_A)
        self.assertEqual(out_multi, FANCY_Bm)

    def test_getitem_not_found_default(self):
        """
        Look up chars _not found in dict, but with default output
        """
        test_char = '\uffff'
        tdict_d = self.clsc.from_dict(dict_with_default)
        out_nf = tdict_d[ord(test_char)]
        out_expected = DEFAULT_OUT.replace(SUBPOINT, test_char)

        self.assertEqual(out_nf, out_expected)

    def test_getitem_none_default(self):
        """
        Look up chars _not found in dict, but with None as default output
        """
        test_char = '\uffff'
        tdict_d = self.clsc.from_dict(dict_with_none_default)
        out_nf = tdict_d[ord(test_char)]

        self.assertEqual(out_nf, None)

    def test_setitem_default(self):
        """
        Change default output by setting value of empty string key
        """
        test_lookup = '\uffff'
        test_newdef = '\u0280\u20df' # small capital R in enclosing diamond
        tdict_d = self.clsc.from_dict(dict_with_default)
        tdict_d[''] = test_newdef
        out_nf = tdict_d[ord(test_lookup)]

        self.assertEqual(tdict_d.out_default, out_nf)
        self.assertEqual(out_nf, test_newdef)

    def test_setitem_multi_codepoint(self):
        """
        Handle insertion of multi-code point string to dictionary
        """
        test_newval = FANCY_Bm
        test_newkey = 'multi'
        tdict_d = self.clsc.from_dict(dict_with_default)
        tdict_d[test_newkey] = test_newval

        out_lu = tdict_d[test_newkey]

        self.assertEqual(out_lu, test_newval)

    def test_getdict(self):
        """
        Conversion to plain dict; retain str.translate()-ready format
        """
        tdict_d = self.clsc.from_dict(dict_plain)
        out_expected = {ord('a'):FANCY_A, ord('b'):FANCY_Bm,}

        self.assertEqual(tdict_d.get_dict(), out_expected)

    def test_getdict_default(self):
        """
        Handle conversion to plain dict when default output set
        """
        tdict_d = self.clsc.from_dict(dict_with_default)
        out_expected = {ord('a'): FANCY_A, ord('b'): FANCY_Bm, '': DEFAULT_OUT}

        self.assertEquals(tdict_d, out_expected)

