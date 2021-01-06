"""
Functional Demos: Functions to Supplement unicodedata Module

"""
# Copyright © 2021 Moses Chong
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

import re
import functools
from uilaat import RangeIndexedList

def blocks_txt_iter(path):
    """
    Import data records from a copy of the Unicode Character Database
    Blocks list (published as a text database named Blocks.txt).

    Returns an iter which yields records from the Blocks file.

    A copy of this file may be obtained at:
    <https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt>

    """
    tmp = ''
    with open(path, mode='r') as fh:
        tmp = fh.read()
    rx = re.compile(r"^[^#]+?$", flags=re.MULTILINE)
    return (i.group() for i in rx.finditer(tmp))

def blocks_rec_to_range(rec):
    """
    Convert a record from Blocks.txt (see blocks_txt_iter() above)
    into a 2-tuple with the format:

    ([rs, rend], BLOCK_NAME)

    where rs is the start of a code point value range ending with rend.

    """
    recs = rec.split(';')
    r = [int(i, base=16) for i in recs[0].split('..')]
    d = recs[1].strip()
    return (r, d,)

def blocks_txt_to_ril(path):
    """
    Read a copy of Blocks.txt (see block_txt_iter() above) into a
    RangeIndexedList.

    The returned RIL will be a decimal code point value-to-block
    name lookup.

    """
    data = blocks_txt_iter(path)
    # TODO: Can these lists be replaced with immutables while
    # maintaining efficiency?
    bounds = [] 
    values = []
    brs = (blocks_rec_to_range(d) for d in data)
    for i in brs:
        bounds.extend(i[0])
        values.append(i[1])
    return RangeIndexedList(bounds, values=values, default=False)

