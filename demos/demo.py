"""
UILAAT Introductory Demos Module

A small collection of tools for interactive use of the library

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

import pdb
import uilaat
from timeit import timeit
from warnings import filterwarnings

def dump_page(plane, page):
    """
    Naively dumps an area of 256 Unicode code points as a string,
    without regard for a code point's status as a reserved or
    non-character pursuant to the Section 3.4.D10a of the Unicode
    Standard. Returns None if requested code points are out of range.

    Arguments
    ---------
    * plane - (int) index of the 65536-code point block, corresponding
        to the highest 16 bits of the code point value. See Section 2.8
        of the Standard. Range allowed: 0 <= plane <= 10
    
    * page - (int) the value of the page, corresponding to the 9th to
        the 16th bit of the code point's value.

    Use for testing generators or substitution functions.
    """
    if plane < 0 or page < 0:
        return None
    if plane > 10 or page > 0xFF:
        return None
    out = '' 
    if plane == 0 and page == 0:
        # Special Dumping Procedure for Plane 0 Page 0 (the ASCII page):
        # Avoid dumping the code points that are identical to ASCII
        # control codes to avoid messing up terminal emulators when
        # used with print()
        for i in range(32, 127):
            out = ''.join((out, chr(i),))
        for i in range(174, 256):
            out = ''.join((out, chr(i),))
    else:
        start = (plane << 16) +  (page << 8)
        end = start | 0xFF
        for i in range(start, end+1):
            out = ''.join((out, chr(i),))
    return out

class DemoTextGenerator:
    """
    Decorative text generator object which serves as an object-oriented
    interface to the rather functional core module.

    This allows users who are prefer an object-oriented programming
    approach to experiment with the library in an interactive environment,
    or even in an actual application.
    """
    # TODO: If possible, implement an acutal Python generator that yields
    # chars for improved memory efficiency.
    def __init__(self):
        self._args = ()
        self._raw = (lambda s:s, None,)
    
    def __add__(self, other):
        """
        These decorative text generators can be combined into a chain
        using the addition operator '+'. The result is a single text
        generator that applies decorations from each of the separate
        generators.
        
        Notes
        -----
        Please be aware that combinations are not commutative; combining
        generators in a different order often yields different results.
        Order of processing takes place in the order which the constituent
        generators were combined.

        Generators down the chain may be rendered ineffective, if other
        generators up the chain cause intermediate results to fall
        completely out of the target range of a subsequent generator.
        """

        if isinstance(other, self.__class__) is False:
            raise TypeError('cannot add with other object types')
        if isinstance(self._args[0], (tuple, list,)) is False:
            ar_self = ((self._args),)
        else:
            ar_self = self._args
        if isinstance(other._args[0], (tuple, list,)) is False:
            ar_other = ((other._args),)
        else:
            ar_other = other._args
        ar = ar_self + ar_other 
        return self.from_args_multi(ar)

    def __repr__(self):
        fmt = '{}{}'
        rs = fmt.format(self.__class__.__name__, self._args)
        return rs

    @classmethod
    def from_args(self, *args):
        """
        Create a decorative text generator object, guessing the
        substitution function to use from the arguments.
        """
        raw = self._get_raw(*args)
        out = self.from_raw(raw)
        out._args = args
        return out

    @classmethod
    def from_args_multi(self, reqs):
        """
        Create a Multi-Substitution text generator object from a
        list of argument tuples.
        """
        raws = []
        for r in reqs:
            raws.append(self._get_raw(*r))
        out = self()
        out._raw = uilaat.sfunc_from_list(raws)
        out._args = reqs
        return out

    @classmethod
    def from_raw(self, raw):
        """
        Create a decorative text generator object from the raw
        call of a substitution function creator.
        """
        out = self()
        if raw[1] == uilaat.SCOPE_CHAR:
            out._raw = uilaat.sfunc_from_list((raw,))
        elif raw[1] == uilaat.SCOPE_STR:
            out._raw = raw
        else:
            raise RuntimeError("unknown substitution scope")
        out._args = (None, None, {'direct_from_raw':True})
        return out
    
    def get_text(self, orig_text):
        """
        Return the mangled text string. Note that strings are not
        yet ready to be copypasted as when strings are viewed
        unprocessed invisible characters show up as escape codes.
        """
        if isinstance(orig_text, str) is False:
            raise TypeError('only str-like input supported')
        return self._raw[0](orig_text)

    def print(self, orig_text):
        """
        Return the mangled text in ready-to-copypaste form :)
        """
        print(self.get_text(orig_text))

    @classmethod
    def _get_raw(self, *args):
        """
        Orders a substitution function from the main module with
        metadata intact, guessing the substitution function type
        from the arguments
        """
        raw = None
        if len(args) == 3:
            if isinstance(args[2], dict) is True:
                raw = uilaat.sfunc_from_dict(*args) 
            elif isinstance(args[2], int) is True:
                raw = uilaat.sfunc_from_covar(*args)
        elif isinstance(args, (list, tuple,)) is True:
            raw = uilaat.sfunc_from_re(*args)
        else:
            fmt = 'could not determine function type from args: {}'
            msg = fmt.format(args)
            raise TypeError(msg)
        return raw


# Ready-to-Use Demo Objects
#
# aesthetic - outputs wide monospaced text, as seen on Shift-JIS
aesthetic = DemoTextGenerator.from_args(33, 127, 65248)
#
# black_cat - add a Phaistos Disc cat before instances of phrase 'black cat'
black_cat = DemoTextGenerator.from_args(r'black cat', '𐇬\uf820')
#
# bubbles - circled text, limited version of the Lunicode.js original
bubbles_dict = {'0':'🄋', '.':'\u00a0⚬', ' ':'\u2003', '\n':'\n'}
bubbles_lite_config = (
    (32, 48, bubbles_dict), # zero, period and whitespace exceptions
    (49, 57, 9412),      # numbers 1-9
    (65, 90, 9333),      # uppercase
    (97, 122, 9327),     # lowercase
)
bubbles_lite = DemoTextGenerator.from_args_multi(bubbles_lite_config)
#
# bubble_black_cat_aesthetic - combined text generator demo
black_cat_aesthetic = black_cat + aesthetic
#
# squares - lazy port of Lunicode.js original
squares_config = (
    32,
    127,
    {
        '':'\uf820\u20de\u00a0',
        ' ':' ',   # another way of excluding characters
        '\n':'\n', # from substitution
    },
)
squares = DemoTextGenerator.from_args(*squares_config)
#
# witch - noisy Witch House-esque text effect
witch_config = (
    None,
    None,
    {
        '':'\uf820\u0353\u034f\u036f',
        'A':'🜂',
        'a':'🜂',
        ' ':' \u1dd1',
        '*':'⛧',
    },
)
witch = DemoTextGenerator.from_args(*witch_config)

# REPL Setup Routine
#
filterwarnings('always')

