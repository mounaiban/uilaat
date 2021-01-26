"""
Functional Demos: Translation Database Documentation Helpers

"""
# Copyright © 2021 Moses Chong
#
# This file is part of UILAAT: The Unicode Interlingual Aesthetic
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

from .unicodedata_extra import blocks_txt_to_ril
from itertools import chain

def req_block_names(d, blocks_txt_path):
    """
    Return a set of Required Block Names which contains the names of
    Unicode Code Blocks used by a particular translation dictionary d.

    A copy of Blocks.txt is required. Copies may be downloaded from 
    the Unicode Consortium at:
    <https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt>
    Please specify a path to Blocks.txt in blocks_txt_path.

    TypeError may be raised if the translation dictionary malformed.

    """

    bril = blocks_txt_to_ril(blocks_txt_path)
    va = chain.from_iterable([list(i) for i in d.values() if type(i) is str])
    vb = [bril[ord(i)] for i in va if type(i) is str]
    return set(vb)

