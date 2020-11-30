"""
UILAAT JSON File Database Repository

Supplement to support loading translations from JSON Repositories,
herein defined as directories containing a single collection of
databases encoded in JSON/ECMA-404 format.

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

from os import path
from json import JSONDecoder
from warnings import warn

SUFFIX_JSON = '.json'
KEY_DB_NAME = '_db_name'

class JSONRepo:
    """
    JSON Translation Database Repository

    Supports loading of translations from a directory containing a collection
    of translation files encoded in JSON format.

    """
    def __init__(self, repo_dir, **kwargs):
        """
        Examples on creating a JSON Repository:

        jr = JSONRepo('trans')  # relative path, relative to working directory
        jr = JSONRepo('/etc/uilaat/trans/')  # absolute path, Unix style
        jr = JSONRepo("J:\Translations")    # absolute path, Windows style

        Other arguments are not supported yet.
        """
        self.current_db_name = None
        # Private variables
        self._repo_dir = repo_dir
        self._current_trans = {}
        self._used_maketrans = False
        self._tmp = []
        self._filename_memo = []
        self._fh = None

    def __repr__(self):
        name = self.__class__.__name__
        return "{}('{}')".format(name, self._repo_dir)

    def get_meta(self, key):
        """
        Return a metadata item from the currently loaded database.
        """
        return (self._tmp[-1])['meta'].get(key)

    def get_trans(self, n=None, maketrans=False):
        """
        Return a translation dictionary from the currently selected
        repository. Remember to load a database using load_db() before
        attempting this.

        Given this translation loaded from a database:
        {'a': '4', 'b':['|3', '\ua7b4', '\U0001d7ab'], 'c':['<', '\U0001f30a']}

        The n parameter selects alternate translations where available
        
        get_trans(0) == {'a': '4', 'b': '|3', 'c': '<'}
        get_trans(1) == {'a': '4', 'b':'\ua7b4', 'c': '\U0001f30a'}
        get_trans(2) == {'a': '4', 'b':'\U0001d7ab', 'c': '<'}

        The maketrans option causes returned translation dictionaries to
        be ready for use with str.translate(), which requires translation
        dictionaries to use decimal codepoint values instead.

        get_trans(0, maketrans=True) == {97: '4', 98:'|3', 99: '<'}

        get_trans() with no parameters returns the last requested translation,
        or get_trans(0) if invoked for the first time since loading a database

        """
        trans_tmp = {}
        if self.current_db_name is None:
            return trans_tmp

        def get_val(v):
            if isinstance(v, list) is True:
                if n >= len(v):
                    return v[0]
                else:
                    return v[n]
            else:
                return v

        prep_key = lambda c: c 
        if maketrans is True:
            prep_key = lambda c: ord(c)
        if n is None:
            if self._current_trans != {}:
                return self._current_trans
            n = 0
        for d in self._tmp:
            dmeta = d.get('meta', {})
            dtrans = d.get('trans', {})
            reverse = dmeta.get('reverse', False)
            for k in dtrans.keys():
                val = get_val(dtrans[k])
                if reverse is True:
                    # ignore default translation when reversing
                    if k == '':
                        continue
                    if (len(val)>1) and (maketrans is True):
                        fmt = '{}: multi-char keys unsupported with maketrans'
                        msg = fmt.format(dmeta[KEY_DB_NAME])
                        warn(RuntimeWarning, 'msg')
                        continue
                    trans_tmp[prep_key(val)] = k
                else:
                    trans_tmp[prep_key(k)] = val
        self._current_trans = trans_tmp
        return trans_tmp

    def load_db(self, db_name):
        """
        Loads a database file from the repository.

        Where:
        jr = JSONRepo('trans')

        jr.load_db('aesthetic2')
        loads the 'aesthetic2' database from the 'trans' repository

        This method launches the recursive loading process, and performs
        the necesary cleanups that must be excluded from the recursive
        loading process.

        """
        self._tmp.clear()
        self._filename_memo.clear()
        self.current_db_name = None
        try:
            self._do_load_db(db_name)
            self.current_db_name = db_name
        finally:
            if self._fh is not None:
                self._fh.close()
                self._fh = None

    def _do_load_db(self, db_name):
        """
        Performs the recursive process of reading in data from a database
        files, together with other inclusion-referenced database files.
        The results are cached in self._tmp.

        This method is intended to be called from load_db() only.

        """
        tmp_path = self._get_db_path(db_name)
        if self._fh is not None:
            self._fh.close()
        self._fh = open(tmp_path, mode='r', encoding='utf-8')
        jd = JSONDecoder()
        tmp_dict = jd.decode(self._fh.read())
        # insert runtime metadata
        tmp_dict['meta'][KEY_DB_NAME] = db_name
        ##
        self._tmp.insert(0, tmp_dict)
        self._filename_memo.insert(0, db_name)
        incs = self._tmp[0].get('trans-include', [])
        if len(incs) > 0:
            for e in incs:
                if e == db_name:
                    fmt = 'trans-include: {}: cannot include self'
                    msg = fmt.format(db_name)
                    warn(msg, RuntimeWarning)
                elif e in self._filename_memo:
                    fmt = 'trans-include: {} to {}: inclusion loop detected'
                    msg = fmt.format(db_name, e)
                    warn(msg, RuntimeWarning)
                else:
                    self._do_load_db(e)
                
    def _get_db_path(self, db_name):
        filename = db_name + SUFFIX_JSON
        return path.join(self._repo_dir, filename)

    def _dump_trans(self, full=False):
        # TODO: Return all possible translation dictionaries available.
        # When full=False, only the first translation will be returned
        # in full. Alternate dictionaries will only contain differences
        # from the first.
        raise NotImplementedError

