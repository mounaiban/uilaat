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
from uilaat import JSONRepo
from timeit import timeit
from warnings import filterwarnings, warn

def dump_code_page(plane, page):
    """
    Naively dumps a code page of Unicode code points as a string, without
    regard for a code point's properties.

    A code page is defined as a series of 256 code points starting from
    U+0000, or any code point value that is a multiple of 256. Borrowing
    from 8-bit encoding conventions, the Unicode code space is herein
    regarded as an amalgamation of 256-point code pages.

    Use this function for testing translation operations.

    Notes
    -----
    Non-characters such as control, replacement, reserved and 0x*FFFF
    code points will be returned. However, the ASCII-compatible control
    characters in the first code page of plane 0, 0x0000 -> 0x00FF, will
    not be returned to avoid malfunctions in terminals.

    Arguments
    ---------
    All ints are shown in hexadecimal, but decimal equivalents are also
    accepted.

    * plane - (int) index of the 65536-code point block, corresponding
        to the highest four bits of the 21-bit code point value.
        See Section 2.8 of the Unicode Standard Core Specification.
        Range allowed: 0x0 <= plane <= 0x10

    * page - (int) the value of the code page, corresponding to bits
      8/9 to 15/16 of the code point value.

    Example: to dump U+3000 to U+30FF: plane=0x0, page=0x30; to dump
    U+21000 to U+210FF: plane=0x2, page=0x10

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

def dump_page(plane, page):
    # support use of deprecated function
    warn('dump_page() will be renamed to dump_code_page()', DeprecationWarning)
    return dump_code_page(plane, page)

class DemoTP:
    """
    Text processor object, for use as a core component of an interactive
    application.

    """
    FQ_SEP = ':'
    def __init__(self, repo_dict={}):
        """
        To create a DemoTP:
        DemoTP() => empty DemoTP
        DemoTP(dict) => DemoTP with preloaded repositories

        Format for dict: {REPO_NAME: REPO_OBJECT, ...}
        Only JSONRepo's are supported as repo objects at the moment.

        """
        self.repos = repo_dict
        self.trans_ops = {}
        self.meta = {}

    def add_repo(self, repo):
        """
        Add a single repository. Only JSONRepo's are supported at
        this time.

        """
        if not isinstance(repo, JSONRepo):
            err = {
                'msg': 'only JSONRepo\'s are currently supported',
                'repo-type': type(repo)
            }
            raise TypeError(err)
        self.repos[repo._repo_dir] = repo
            # TODO: implement non-private alternative to repo._repo_dir

    def add_trans(self, trans_name, n=0):
        """
        Add a translation to the operations list.

        If there are two or more repositories loaded, and there are
        translations that have the same name across the repositories,
        use a fully qualified name like: 'REPO:TRANS', where REPO is
        the name of the repository, and TRANS is the name of the
        translation.

        If alternate translations are available, those can be selected
        with different n-values.

        Please avoid the use of the colon ':' character in the names
        of any translation or database.

        Use translate() to generate text.

        """
        # attempt to detect and handle FQ translation name
        tname_tmp = trans_name
        repo = None
        if self.FQ_SEP in tname_tmp:
            alrepo = tname_tmp.split(self.FQ_SEP)[0]
            repo_names = tuple(self.repos.keys())
            if alrepo in repo_names:
                repo = self.repos[alrepo]
                len_sep = len(self.FQ_SEP)
                name_remn = tname_tmp[trans_name.index(self.FQ_SEP)+len_sep:]
                repo.load_db(name_remn)
        # if a non-FQ translation name is used, look through all
        # added repos and get the first translation found
        else:
            for name in self.list_repos(incl='valid'):
                try:
                    repo = self.repos[name]
                    repo.load_db(trans_name)
                        # load_db() raises FileNotFoundError if trans
                        # not found
                    tname_tmp = f"{name}{self.FQ_SEP}{trans_name}"
                    self.trans_ops[tname_tmp] = repo.get_trans(
                        n=n, one_dict=True
                    )
                except FileNotFoundError:
                    continue
        trans_tmp = repo.get_trans(n=n,one_dict=True)
        if trans_tmp is not None:
            self.trans_ops[tname_tmp] = trans_tmp
            self.meta[tname_tmp] = repo.get_meta()
        else:
            raise KeyError(f"translation {trans_name} not found in any repo")

    def list_repos(self, incl='valid'):
        """
        Gets a list of names of repositories. Valid options for get are:

        * 'valid': list names of valid repositories.

        * 'all': list names of all loaded repositories, valid repositories
          first, followed by invalid repositories in a nested list.
          Invalid repositories point to a non-existent or inaccessible
          directory.

        """
        if not isinstance(self.repos, dict):
            err = {
                'msg': 'repo dictionary is not of type dict',
                'repo-type': type(self.repos)
            }
            raise TypeError(err)
        out = []
        out_invalid = []
        keys = self.repos.keys()
        for k in keys:
            try:
                if self.repos[k].list_trans(incl='count') >= 0:
                    out.append(k)
            except NotADirectoryError:
                # invalid repository encountered
                out_invalid.append(k)
        if len(out_invalid) > 0 and incl == 'all':
            out.append(out_invalid)
        return out

    def list_trans(self):
        """
        Return a list of names of available translations from all valid
        repositories added to the text processor.

        """
        repo_names= self.list_repos(incl='valid')
        out = []
        for r in repo_names:
            repo = self.repos[r]
            trans_names = repo.list_trans(incl='names')
            for t in trans_names:
                out.append(f"{r}{self.FQ_SEP}{t}")
        return out

    def pop_trans(self, i):
        if len(demo.trans_ops) <= 0:
            raise ValueError("ops dict-list is empty")
        names = list(self.trans_ops.keys())
        if isinstance(i, int):
            if i > len(names):
                raise ValueError(f"last op has index {len(names)}")
            tn = names[i]
            return {tn: self.trans_ops.pop(tn)}
        elif isinstance(i, str):
            return self.trans_ops.pop(i)

    def sample(self, plane, page, order=[]):
        """
        Returns a string of consecutive code points for previewing the
        final effects of the selected translation operations.

        The definition of plane is specified in the Unicode Standard
        Core Specification (e.g. plane 0x0 is U+0000 to U+FFFF inclusive,
        plane 0x1 is U+10000 to U+1FFFF, and so on...)

        A page (short for code page) is a series of 256 code points
        starting at U+0000 or any other code point value that is a
        multiple of 256.

        """
        dump = dump_code_page(plane, page)
        return self.translate(dump, order)

    def translate(self, s, order=[]):
        """
        Make some fancy text!

        Returns a string with all selected translation operations applied

        """
        def do_trans(s):
            tmp = s
            for tn in order:
                trans_dict = self.trans_ops[tn][0]
                # TODO: pre-process strings with regexes according to
                # trans spec
                if self.meta[tn].get('reverse-out', False) is True:
                    # handle reversed output
                    tmp_rev = ''
                    for c in tmp:
                        tmp_rev = ''.join((trans_dict.get(ord(c), c), tmp_rev))
                        tmp = tmp_rev
                else:
                    tmp = tmp.translate(trans_dict)
            return tmp

        if len(order) == 0:
            order = list(self.trans_ops.keys())
        return do_trans(s)

# Ready-to-play demo objects
#
jr = JSONRepo('trans')

jr_invalid = JSONRepo('trans')
jr_invalid._repo_dir = 'asdf_notfound_404'

demo = DemoTP({'trans':jr, 'asdf_notfound_404': jr_invalid})

# REPL Setup Routine
#
if __name__ == 'main':
    filterwarnings('always')

