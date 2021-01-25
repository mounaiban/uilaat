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
from uilaat import JSONRepo, TextProcessor
from timeit import timeit
from warnings import filterwarnings, warn

# Ready-to-play demo objects
#
jr = JSONRepo('trans')

jr_invalid = JSONRepo('trans')
jr_invalid._repo_dir = 'asdf_notfound_404'

demo = TextProcessor({'trans':jr, 'asdf_notfound_404': jr_invalid})

# REPL Setup Routine
#
if __name__ == 'main':
    filterwarnings('always')

