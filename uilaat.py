"""
UILAAT Main Module

A mini-library for working with decorative Unicode text

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

# Unicode is a registered trademark of Unicode, Inc.

import re
from functools import reduce
from json import JSONDecoder
from os import path
from sfunc import sfunc_from_covar, sfunc_from_list, sfunc_from_re, \
    sfunc_from_dict, SCOPE_CHAR, SCOPE_STR, SCOPE_NOP # TODO: Remove sfunc's
from warnings import warn

KEY_DB_NAME = '_db_name'
SUBPOINT = '\ufffc' # Unicode Object Replacement
SUFFIX_JSON = '.json'
VERSION = '0.5'
is_odd = lambda x : x%2 != 0

#
# There are notes in the comments at the end of this module.
#

# Surrogate helper functions
#
utf16_hs = lambda v:((((v & 0x1F0000)>>16)-1)<<6) | ((v & 0xFC00)>>10) | 0xD800
    # get UTF-16 high surrogate ordinal from code point ordinal
utf16_hs_c = lambda c: chr(utf16_hs(ord(c)))
    # get high surrogate from character
utf16_ls = lambda v:(v&0x3ff) | 0xdc00
    # get UTF-16 low surrogate ordinal code point ordinal
utf16_ls_c = lambda c: chr(utf16_ls(ord(c)))
    # get low surrogate from character
def surr(c):
    """
    Get UTF-16 surrogate pair for a character

    """
    if len(c) != 1:
        raise TypeError('function takes only single characters')
    cor = ord(c)
    if cor <= 0x10000 or cor <= 0x10FFFF:
        return ''.join((utf16_hs_c(c), utf16_ls_c(c)))
    else:
        raise ValueError('surrogates are for code points 0x10000 to 0x10FFFF')


# Supplementary Mapping Classes
#
class CodePointOffsetLookup:
    """
    A Unicode Code Point offset lookup that mimics a read-only dict.
    Accepts code point values and returns a single character
    corresponding to the offset code point.

    This class is intended for use with str.translate().

    Where:
    cpol = CodePointOffsetLookup(a, b, off)

    cpol[x] == chr(x + off)
    """
    def dict(self):
        """
        Return a Python dict equivalent of the CodePointOffsetLookup

        Lookups will be expanded into multiple keys and values, one for
        each key within the CPOL's lookup range.

        """
        out = {}
        for i in range(self._start, self._end+1):
            out[i] = self.__getitem__(i)
        return out

    def __init__(self, start, end, offset):

        # validate start and end
        if (isinstance(start, int) is False) or (isinstance(end, int) is False):
            raise ValueError('both start and end must be int')
        elif start < 0 or end < 0:
            raise ValueError('start and end must be zero or positive')
        elif start > end:
            raise ValueError('start must come before end')
        # validate offset
        if isinstance(offset, int) is False:
            raise ValueError('offset must be int')
        elif start+offset < 0:
            raise ValueError('offset must not cause negative values to return')

        self._start = start
        self._end = end
        self._offset = offset

    def __eq__(self, other):
        """
        Given two CPOL's C1 and C2:

        C1 == C2 is True when when their start, end and offset are of
        equal value.

        """
        return (self._start == other._start) and (self._end == other._end)\
            and (self._offset == other._offset)

    def __getitem__(self, key):
        # validate key
        if isinstance(key, int) is False:
            raise ValueError('only int keys are supported')
        elif key > self._end:
            raise LookupError('requested translation out of range')
        elif key < self._start:
            raise LookupError('requested translation out of range')

        out = key + self._offset
        if out < 0:
            raise ValueError('negative code point suppressed')
        elif out > 0x10FFFF:
            raise LookupError('out of range code point suppressed')
        else:
            return chr(out)

class RangeIndexedList:
    """
    A list which returns items according to the range which the key
    falls into.

    This class, when used with int keys, is intended for use with
    str.translate().

    """
    DEFAULT_VALUE = True

    def __init__(self, bounds, values=None, **kwargs):
        """
        How to create a basic RangeIndexedList:
        L = RangeIndexedList(keys, values)

        * bounds is a sorted sequence (list, tuple), of int's that
          specifiy ranges; zero and even-indexed items specify
          range starts and odd-indexed items specify range stops.
          Ranges must not overlap.

        * values is a sequence of items specifying items to be returned
          as a result of a lookup. Each item corresponds to a range
          pair in keys, values[0] is referenced to by all values betwen
          keys[0] and keys[1], and so on. If there is only one value
          in values, this item will be shared between all ranges. Thus,
          there must be exactly one value, or half as many values as
          bounds.

        Accepted keyword arguments:

        * default - when values is None, this value will be returned
           for all keys falling into any range, if not specified,
           this argument is set to True.

        * copy_key - (bool) if set to True, all instances of the Unicode
           Replacement Character, U+FFFC, in the output will be replaced
           by a single copy of the key.
           If int keys are used, the ord() of the key is used as the
           replacement instead.

        """
        self._copy_key = kwargs.get('copy_key', False)
        self._default = kwargs.get('default', self.DEFAULT_VALUE)
        self._bounds = list(bounds)
        self._values = None
        self._validate = kwargs.get('validate', True)

        if values is None:
            self._values = [self._default,] * (len(bounds)//2)
        else:
            self._values = list(values)

        if self._validate:
            self.validate(bounds, values)

    def __eq__(self, other):
        """
        Given two RILs, L1 and L2,

        L1 == L2 is True when both RILs have the same exact bounds, values
        and options.

        """
        if not isinstance(other, type(self)):
            raise TypeError('can only compare with other range-indexed lists')
        return self.__dict__ == other.__dict__

    def __getitem__(self, key):
        """
        Looking up items from a RangeIndexedList:

        Where:
        vs = ('\u2615', '\U0001f35c', '\U0001f356') # three items
        keys = (7,9,12,14,17,21) # three ranges
        L = (vs, keys)

        7 <= x <= 9; L[x] == '\u2615'
        12 <= x <= 14; L[x] == '\U0001f35c'
        17 <= x <= 21; L[x] == '\U0001f356'

        All other values of x raise a LookupError.

        See __init__ for more options.

        """
        i, found = self._do_index(key)
        out = None
        if found is False:
            if i == 0:
                raise LookupError('key smaller than smallest known key')
            elif i == len(self._bounds):
                raise LookupError('key larger than largest known key')
            elif not is_odd(i):
                raise LookupError('key not in any range')
        # PROTIP: if the key was not found, but an even index was
        # suggested, then the key is considered inside a range.
        if len(self._values) == 1:
            out = self._values[0]
        else:
            out = self._values[i//2]
        if self._copy_key is False:
            return out
        else:
            if out is None:
                return None
            elif ('\ufffc' in out) and (isinstance(key, int) is True):
                return out.replace('\ufffc', chr(key))
            else:
                return out

    def __repr__(self):
        fmt = "{}({},copy_key={},default={},values={})"
        name = self.__class__.__name__
        return fmt.format(name, self._bounds, self._copy_key, self._default,
            self._values)

    def dict(self):
        """
        Return a Python dict equivalent of the RangeIndexedList.

        Range lookups will be expanded into multiple direct key-value
        lookups, covering every available key for each range.

        """
        # TODO: This is part of an investigation on the performance
        # of Python dict's where a large number of keys are involved.
        # Lookups on a basic dict are much faster than with an RIL,
        # at the expense of memory usage.
        out = {}
        for i in range(0, len(self._bounds), 2):
            for kn in range(self._bounds[i], self._bounds[i+1]+1):
                out[kn] = self.__getitem__(kn)
        return out

    def insert(self, new_keys, new_values=None):
        """
        Inserts additional ranges into an existing range-indexed list.

        * new_keys is an even-length list of int's, where zero and even
          indexed-keys contain range starts, and odd indexed-keys contain
          range stops.

        * new_values is a list of values referenced by new_keys; every
          value corresponds to a start-stop key pair in new_keys.

        Where:
        L._bounds == [2,4,10,12]
        L._values == [1,2]

        Invoking:

        L.insert((6,8,14,16,), new_values=(69, 420))

        Will change L to:
        L._bounds == [2,4,6,8,10,12,14,16]
        L._values == [1,69,2,420]

        """
        if new_values is None:
            new_values = (self.DEFAULT_VALUE,) * (len(new_keys)//2)
        if is_odd(len(new_keys)):
            name = self.__class__.__name__
            msg = "{} must contain an even number of keys".format(name)
            raise ValueError(msg)
        elif len(new_values) != len(new_keys)//2:
            msg = "number of values must be half the number of keys"
            raise ValueError(msg)

        i = 0
        for i_nk in range(1, len(new_keys), 2):
            ks = new_keys[i_nk-1]    # range start key
            ke = new_keys[i_nk]      # range end key
            ist, ks_found = self._do_index(ks)
            iend, ke_found = self._do_index(ke)

            if ist != iend:
                msg = "{}: new ranges must not overlap existing ranges".format(i)
                raise ValueError(msg)
            elif is_odd(ist) or ks_found or ke_found:
                msg = "{}: cannot create new ranges within another".format(i)
                raise ValueError(msg)
            elif ke - ks < 1:
                msg = "{}: ranges must have a length of one or more".format(i)
                raise ValueError(msg)

            self._bounds.insert(ist, ke)
            self._bounds.insert(ist, ks)
            self._values.insert(iend//2, new_values[i_nk//2])
            i += 1

    def remove(self, key):
        # TODO: This method will remove a range referred to by key.
        # Given the ranges (2,4),(6,8) and (10,12), when 6 < key < 8,
        # (6,8) will be removed.
        raise NotImplementedError('TODO: implement range removal method')

    @classmethod
    def bounds_from_ranges(self, ranges):
        """
        Create a list of range keys from a list of range objects for
        use with creating new range-indexed lists.
        All range objects must have a start before a stop. Ranges are
        checked for correctness as they are processed.

        """
        out = []
        i = 0
        last_stop = 0
        for r in ranges:
            if not isinstance(r, range):
                raise TypeError('only range objects are accepted')
            elif (r.start > r.stop) or (r.step != 1):
                raise ValueError('use only forward-stepping ranges with step=1')
            elif last_stop > r.start:
                msg = "{}: start must be after last stop".format(i)
                raise ValueError(msg)
            elif len(r) < 1:
                msg = "{}: zero-length ranges not allowed".format(i)
                raise ValueError(msg)
            else:
                out.extend((r.start, r.stop))
                last_stop = r.stop
                i += 1
        return out

    def validate(self, bounds, values):
        """
        Check if bound and key lists are well-formed. Returns None
        if all checks pass.

        Raises ValueErrors if checks fail

        """
        # TODO: Tests for validate()
        if is_odd(len(self._bounds)):
            msg = 'bounds list must have an even number of bounds'
            raise ValueError(msg)

        if values is not None:
            if len(self._bounds)//len(self._values) != 2:
                if len(self._values) != 1:
                    msg = 'only one value, or one value per bounds pair allowed'
                    raise ValueError(msg)

        t = type(bounds[0])
        i = 1
        for b in bounds[1:]:
            if b <= bounds[i-1]:
                msg = 'bounds[{}]: must be larger than the last'.format(i)
                raise ValueError(msg)
            if type(b) != t:
                msg = 'all values must be of the same type as values[0]'
                raise ValueError(msg)
            i += 1

    def _do_index(self, key):
        """
        Return the key's int index or suggested index in self._bounds,
        along with a bool flag indicating if the key was in fact found
        in a tuple like:

        (index, found_flag)

        If key is in self._bounds, return the highest possible index.
        If the key does not exist, return the lowest suggested index.
        The suggested index is a recommended index to be used for
        inserting non-existent bounds while keeping self._bounds sorted.

        A zero index with a False indicates that the key is out of range
        on the smaller side of the first range. A index past the highest
        with a False indicates that the key that is out of range on the
        greater side of the last range.

        """
        i_len = len(self._bounds)
        i_start = 0
        i_end = i_len - 1
        # PROTIP: binary search
        if key > self._bounds[i_end]:
            return (i_len, False)
        i = i_end // 2
        while i_end - i_start > 1:
            i = i_start + ((i_end-i_start) // 2)
            k_rk = self._bounds[i]
            if key == k_rk:
                return (i, True)
            if key <= k_rk:
                i_end = i
            else:
                i_start = i

        # if key was not found, determine the best index
        if key > self._bounds[i_start]:
            return (i_end, (key == self._bounds[i_end]))
        else:
            return (i_start, (key == self._bounds[i_start]))
            # PROTIP: the final equality check is required because the
            # search loop above stops running as soon as i_end meets
            # i_start, missing out on the chance to raise the key found
            # flag.

class TranslationDict(dict):
    """
    Auto-Substitution Translation Dictionary

    This is an extension on the dict class designed to be more in
    line with UILAAT conventions. The key differences are:

    * When a key is not found, a default value is returned
      automatically without the need of the get() method

    * The default output value is the one returned by the empty
      string '' key

    * Any output automatically inserts a copy of the key
      (or a Unicode character of the key's value for int keys)
      where a replacement U+FFFC character is found.

    * One-character string keys are not allowed, but are
      automatically converted to their Unicode code point value
      with ord().

    This class is for use with str.translate().

    """
    _super = None

    def __init__(self, *args, **kwargs):
        self._out_default = SUBPOINT
        self._super = super()
        self._super.__init__()
        if len(args) > 0:
            init_dict = args[0]
            if isinstance(init_dict, dict):
                self._out_default = init_dict.get('', SUBPOINT)
                for k in init_dict.keys():
                    self.__setitem__(k, init_dict[k])
            else:
                raise TypeError('only dicts are supported as initialisers')

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key == '':
                self._out_default = value
                self._super.__setitem__('', value)
            elif len(key) == 1:
                self._super.__setitem__(ord(key), value)
            else:
                self._super.__setitem__(key, value)
        elif isinstance(key, int):
            self._super.__setitem__(key, value)

    def __getitem__(self, key):
        out = self._super.get(key, self._out_default)
        if out is None:
            return None
        if SUBPOINT in out:
            keycopy = key
            if isinstance(key, int) is True:
                keycopy = chr(key)
            return out.replace(SUBPOINT, keycopy)
        else:
            return out

    def get_dict(self):
        """
        Return a Python dict equivalent to the TranslationDict if one
        can be created. This is possible only when a default translation
        (referenced by the empty string key '') has not been set.

        None will be returned instead if the conversion is not possible.

        """
        if '' in self:
            return None
        else:
            temp = {}
            for k in self.keys():
                temp[k] = self.__getitem__(k)
            return temp

    def reset_default(self):
        self._out_default = self.get('', SUBPOINT)

    @classmethod
    def from_dict(self, d):
        """
        Create an Auto-Substitution Translation Dictionary from a regular
        dict.
        """
        # PROTIP: This seemingly redundant deep copy procedure actually
        # performs a str.maketrans()-like conversion. It can also correctly
        # set up default output.
        out = self()
        for k in d.keys():
            out[k] = d[k]
        return out


# Repository Classes
#
class JSONRepo:
    """
    JSON Translation Database Repository

    Supports loading of translations from a directory containing a collection
    of translation files encoded in JSON format.

    """
    CODE_OFFSET = '\uf811'
    CODE_REGEX = '\uf812'
    CODE_RANGE = '\uf813'

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
        self._used_maketrans = False  # TODO: remove this?
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

    def get_trans(self, n=None, maketrans=False, one_dict=False):
        """
        Return a list of translation objects from the currently selected
        repository. Remember to load a database using load_db() first.
        Translation objects may be dict-likes or a two-item list containing
        [creg, repl,] where creg is a compiled regex, and repl is a string
        to replace text matching creg.

        Given this translation loaded from a database:
        {'a': '4', 'b':['|3', '\ua7b4', '\U0001d7ab'], 'c':['<', '\U0001f30a']}

        The n parameter selects alternate translations where available

        get_trans(0) == {'a': '4', 'b': '|3', 'c': '<'}
        get_trans(1) == {'a': '4', 'b':'\ua7b4', 'c': '\U0001f30a'}
        get_trans(2) == {'a': '4', 'b':'\U0001d7ab', 'c': '<'}

        The maketrans option requests dictionaries that are ready for use
        with str.translate(), these use decimal codepoint values for keys
        instead of characters or strings.

        get_trans(0, maketrans=True) == {97: '4', 98:'|3', 99: '<'}

        get_trans() with no parameters returns get_trans(0).

        """
        first_dict = TranslationDict({})
        trans_dicts = [first_dict,]
        if self.current_db_name is None:
            return None
        # Handler Functions
        #
        # Summary of Handler Function mini-API
        # Arguments: (k, v)
        #   k - translation key, v - translation value; k-v pairs are loaded
        #   from the 'trans' object in a UILAAT JSON translation database
        #
        # JSONRepo Instance Variables: dmeta, maketrans, reverse_trans
        #   dmeta - 'meta' object of the translation database,
        #   reverse_trans - bool flag to indicate that the translation in the
        #                   database file should be reversed.
        #   maketrans - bool flag to indicate output is for use with
        #               str.translate(); this may have different effects on
        #               different types of items, but always results in int
        #               keys being applied.
        #
        # PROTIP: The instance variables are set in the main loop, whose
        #  code begins after the last handler function below.
        #
        def _prep_one_dict(trans_list):
            # Convert the list of translation lookup objects into a list
            # with one dict at index zero and optional accompanying regex
            # translations appearing later.
            if not isinstance(trans_list[0], dict):
                raise ValueError("debug: dictionary not on top of trans list")
            out = [{},]
            for t in trans_list:
                if hasattr(t, 'dict'):
                    tmp = t.dict()
                    ktmp = tmp.keys()
                    for k in ktmp:
                        out[0][k] = tmp[k]
                elif hasattr(t, 'get_dict'):
                    tmp = t.get_dict()
                    ktmp = tmp.keys()
                    for k in ktmp:
                        out[0][k] = tmp[k]
                else:
                    out.append(t)
            return out

        def _prep_trans(k, v):
            # String-to-string or int-to-string translation handler
            v_out = SUBPOINT
            if isinstance(v, (list, tuple)):
                if n >= len(v):
                    v_out = v[0]
                else:
                    v_out = v[n]
            else:
                v_out = v
            if maketrans:
                if isinstance(v, str):
                    if len(k) == 1:
                        k = ord(k)
                    else:
                        fmt = "{}: multi-char keys unsupported with maketrans"
                        msg = fmt.format(dmeta[KEY_DB_NAME])
                        warn(RuntimeWarning, 'msg')
                    return
            if reverse_trans:
                if k == '':
                    return
                else:
                    trans_dicts[0][v_out] = k
            else:
                trans_dicts[0][k] = v_out

        def _prep_trans_ril(k, v):
            # Code Point Range Translation handler
            #
            # Translation Database format summary
            #  trans: [[ba1,ba2,...], [va1,va2,...]]
            #  name: CODE_RANGE + ' ' + trans_name
            #  Please see top of class for CODE_RANGE definition
            #  DB entry: {name: trans}
            #  multi-trans DB entry: {name: [trans1, trans2, ...]}

            # PROTIP: k only contains the name of the translation
            if reverse_trans:
                fmt = "{}: reverse range translations unsupported"
                msg = fmt.format(dmeta[KEY_DB_NAME])
                warn(RuntimeWarning, msg)
                return
            it = n
            if isinstance(v[0][0], (list, tuple)):
                # handle alternate translations
                if n > len(v):
                    it = 0
                bs = v[it][0]
                vs = v[it][1]
            else:
                bs = v[0]
                vs = v[1]
            ril = RangeIndexedList(bs, vs, copy_key=True)
            trans_dicts.append(ril)

        def _prep_trans_cpoff(k, v):
            # Code Point Offset translation handler
            it = n
            if isinstance(v[0], list):
                # handle alternate translations
                if n > len(v):
                    it = 0
                args = v[it]
            else:
                args = v

            if reverse_trans:
                offset_tmp = args[2]
                start = offset_tmp + args[0]
                end = offset_tmp + args[1]
                offset = -offset_tmp
            else:
                start = args[0]
                end = args[1]
                offset = args[2]
            cpoff = CodePointOffsetLookup(start, end, offset)
            trans_dicts.append(cpoff)

        def _prep_trans_regex(k, v):
            # Regex handler
            if reverse_trans:
                fmt = "{}: reverse regex translations unsupported"
                msg = fmt.format(dmeta[KEY_DB_NAME])
                warn(RuntimeWarning, msg)
                return
            it = n
            if isinstance(v[0], list):
                # handle alternate translations
                if n > len(v):
                    it = 0
                args = v[it]
            else:
                args = v
            rege = re.compile(args[0])
            repl = args[1]
            out = [rege, repl]
            trans_dicts.append(out)

        handlers_k = {
            self.CODE_OFFSET: _prep_trans_cpoff,
            self.CODE_RANGE: _prep_trans_ril,
            self.CODE_REGEX: _prep_trans_regex,
        }
        ### End of Helper Functions ###

        if n is None:
            n = 0
        for d in self._tmp:
            dmeta = d.get('meta', {})
            dtrans = d.get('trans', {})
            # TODO: Eventually remove support for unqualified 'reverse'
            reverse_trans_old = dmeta.get('reverse', False)
            reverse_trans = dmeta.get('reverse-trans', reverse_trans_old)
            if reverse_trans_old is not False:
                fmt = '{}: use reverse-trans to specify reverse translations'
                msg = fmt.format(dmeta[KEY_DB_NAME])
                warn(msg, DeprecationWarning)
            for k in dtrans.keys():
                if k == '':
                    handler = _prep_trans
                elif isinstance(k, str):
                    handler = handlers_k.get(k[0], _prep_trans)
                else:
                    handler = _prep_trans
                handler(k, dtrans[k])
        if one_dict is True:
            return _prep_one_dict(trans_dicts)
        else:
            return trans_dicts

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
        self._current_trans = None
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

    def _str_to_keys(self, s):
        # Convert specially-formatted string into key list for creating
        # CodePointOffsetLookup and RangeIndexedList objects.
        if isinstance(s, str):
            if ord(s[0]) & 0xF800 == 0xF800:
                return s.split(' ')[1:]

# Important Information
# ---------------------
#
# Substitution Points (SP's)
# ==========================
# SPs are intended to be a platform-agnostic method of including
# characters matched by a dictionary key or regular expression into the
# default translation output. They are indicated by U+FFFC.
# (See also: Unicode Standard, Section 23.8)
#
# In an example default substitution:
#
# dict: {'':'\ufffc\u2e04'}
# code points: U+FFFC + U+2E04
# input: 'J'
# output: 'J' + U+2E04
#

