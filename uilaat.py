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
from os import listdir, path
from warnings import warn

KEY_DB_NAME = '_db_name'
SUBPOINT = '\ufffc' # Unicode Object Replacement
SUFFIX_JSON = '.json'
VERSION = '0.5'
is_odd = lambda x : x%2 != 0

#
# There are notes in the comments at the end of this module.
#

# Helper functions
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

def dump_code_page(plane, page):
    """
    Naively dumps a code page of Unicode code points as a string, without
    regard for a code point's properties.

    A code page is defined as a series of 256 code points starting from
    U+0000, or any code point value that is a multiple of 256.

    Use this function for testing translation operations.

    To avoid malfunctions in terminals, especially when print() is used
    with dumps, code points U+0000 to U+00FF inclusive will not be returned.

    Arguments
    ---------
    PROTIP: decimal values are accepted for (int) arguments too

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
        # Avoid dumping code points identical to ASCII control codes
        # to avoid messing up terminal emulators
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

def key_by_index(d, i, default=None):
    # get a key from a dict d of index i, return default if i is out of bounds;
    # i=0 returns the the first key inserted into d.
    if not isinstance(i, int):
        raise TypeError("only int indices are accepted")
    elif not isinstance(d, dict):
        raise TypeError("only dicts are supported")
    elif i >= len(d):
        return default
    keys = tuple(d.keys())
    return keys[i]

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
    A list which returns items according to the range which the
    search key falls into.

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

        * validate - (bool) if set to True, bounds and values will be
          checked for correctness when the RIL is created, see validate()
          for details.

        """
        self._copy_key = kwargs.get('copy_key', False)
        self._default = kwargs.get('default', self.DEFAULT_VALUE)
        self._bounds = list(bounds)
        self._values = None
        self._validate = kwargs.get('validate', True)

        if values is None:
            self._values = [self._default,]
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
        L = RangeIndexedList(vs, keys)

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

        A RangeIndexedList is well-formed when:

        1. Every bound has a start and an end; this is determined by
           bounds having an even number of values.

        2. The bounds are sorted and non-overlapping; this is determined
           by ensuring all bounds in ``bounds`` are sorted smallest first,
           and that there is gap of at least 1 between bounds.

        3. There is a value for every bound; this is determined by making
           sure ``values`` has either one, or half of the number of values
           in ``bounds``.

        Raises ValueErrors if any check fails.

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
        self.out_default = SUBPOINT
        self._super = super()
        self._super.__init__()
        if len(args) > 0:
            init_dict = args[0]
            if isinstance(init_dict, dict):
                for k in init_dict.keys():
                    self.__setitem__(k, init_dict[k])
                self.out_default = init_dict.get('', SUBPOINT)
            else:
                raise TypeError('only dicts are supported as initialisers')

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key == '':
                self.out_default = value
                self._super.__setitem__('', value)
            elif len(key) == 1:
                self._super.__setitem__(ord(key), value)
            else:
                self._super.__setitem__(key, value)
        elif isinstance(key, int):
            self._super.__setitem__(key, value)

    def __getitem__(self, key):
        out = self._super.get(key, self.out_default)
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
        Return a plain dict equivalent to the TranslationDict.

        """
        temp = {}
        for k in self.keys():
            temp[k] = self.__getitem__(k)
        return temp

    def reset_default(self):
        self.out_default = self.get('', SUBPOINT)

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
        self._repo_dir = None
        self._current_trans = {}
        self._used_maketrans = False  # TODO: remove this?
        self._tmp = []
        self._filename_memo = []
        self._fh = None

        self._set_repo_dir(repo_dir)

    def __repr__(self):
        name = self.__class__.__name__
        return "{}('{}')".format(name, self._repo_dir)

    def get_meta(self, key=None):
        """
        Return metadata items from the currently loaded database. If
        key is None, the whole metadata dict for the currently-loaded
        DB is returned.

        If a DB 'x' includes data from another using links in the
        include property, the metadata from DB 'x' takes precedence
        over any other linked DB.

        """
        if key is None:
            return self._tmp[-1]['meta']
        else:
            return self._tmp[-1]['meta'].get(key)

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

        get_trans() with no parameters returns get_trans(0).

        The maketrans option requests dictionaries that are ready for use
        with str.translate(), these use decimal codepoint values for keys
        instead of characters or strings.

        get_trans(0, maketrans=True) == {97: '4', 98:'|3', 99: '<'}

        The one_dict option condenses all dict-like lookups in the DB
        into a single plain dict, placed first in the list of translation
        objects.

        """
        # Summary of Handler Function mini-API
        # Arguments: (k, v, n, dls, **kwargs)
        #   k - translation key from JSON translation database
        #   v - translation value from JSON translation database
        #   n - alternate translation selector
        #   dls - list of dicts to add the translation to. For
        #         JSONRepos, this is always trans_dicts.
        #
        # Optional arguments:
        #   dmeta - 'meta' object of the translation database,
        #   reverse_trans - bool flag to indicate that the translation in the
        #                   database file should be reversed.
        #   maketrans - bool flag to indicate output is for use with
        #               str.translate(); this may have different effects on
        #               different lookup types, but always results in int
        #               keys being applied.
        #
        # PROTIP: The instance variables are set in the main loop, whose
        #  code begins after the last handler function below.
        #
        first_dict = TranslationDict({})
        trans_dicts = [first_dict,]
        if self.current_db_name is None:
            return None

        def _prep_one_dict(trans_list):
            # TODO: spin off this function to a class method?
            # Condense a list of translation lookup objects so that all
            # non-regex lookups are combined into a single lookup at index
            # 0 of the list.

            if not isinstance(trans_list[0], dict):
                raise ValueError("debug: dictionary not on top of trans list")
            out = [{},]
            for t in trans_list:
                if hasattr(t, 'dict'):
                    # handle types with dict() e.g. CodePointOffsetLookup
                    tmp = t.dict()
                    ktmp = tmp.keys()
                    for k in ktmp:
                        out[0][k] = tmp[k]
                elif hasattr(t, 'get_dict'):
                    # Handle types with get_dict() e.g. TranslationDict
                    tmp = t.get_dict()
                    ktmp = tmp.keys()
                    for k in ktmp:
                        out[0][k] = tmp[k]
                else:
                    out.append(t)
            if '' in out[0]:
                # TODO: Find a faster way to do this
                out[0] = TranslationDict.from_dict(out[0])
                out[0][''] = trans_list[0].out_default
            return out

        handlers_k = {
            self.CODE_OFFSET: self._prep_trans_cpoff,
            self.CODE_RANGE: self._prep_trans_ril,
            self.CODE_REGEX: self._prep_trans_regex,
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
                    handler = self._prep_trans
                elif isinstance(k, str):
                    handler = handlers_k.get(k[0], self._prep_trans)
                else:
                    handler = self._prep_trans
                handler(
                    k, dtrans[k], n, trans_dicts, maketrans=maketrans,
                    reverse_trans=reverse_trans
                )
        if one_dict is True:
            return _prep_one_dict(trans_dicts)
        else:
            return trans_dicts

    def _prep_trans(self, k, v, n, dls, **kwargs):
        """
        String-to-string or int-to-string translation handler
        k is the input string, v is the output; only single-char inputs
        are supported at the moment

        Please see get_trans() for info on the other arguments
        """
        reverse_trans = kwargs.get('reverse_trans', False)
        maketrans = kwargs.get('maketrans', False)
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
            elif isinstance(v, (list, tuple)):
                for item in v:
                    dls[0][item] = k
            else:
                dls[0][v_out] = k
        else:
            dls[0][k] = v_out


    def _prep_trans_cpoff(self, k, v, n, dls, **kwargs):
        """
        Code Point Offset translation handler
        k is the name of the translation, like "\uf811 aesthetic"
        v is the definition of the offset lookup, like:
        [s, e, off] => s: start code point, e: end code point, off: offset
        when offering alternate translations, wrap everything in an
        outer array like: [[s0, e0, off0], ... [sN, eN, offN]]

        Please see get_trans() for info on the other arguments
        """
        reverse_trans = kwargs.get('reverse_trans', False)
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
        dls.append(cpoff)

    def _prep_trans_regex(self, k, v, n, dls, **kwargs):
        """
        Regex translation handler
        k is the name of the translation, like "\uf812 aesthetic"
        v is a definition like [re, s], re is a regular expression matching
        target text, s is its replacement string

        when offering alternate translations, wrap everything in outer
        arrays like:
        [[re0, s0]...[reN, sN]]

        Please see get_trans() for info on the other arguments
        """
        reverse_trans = kwargs.get('reverse_trans', False)
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
        dls.append(out)

    def _prep_trans_ril(self, k, v, n, dls, **kwargs):
        """
        Code Point Range Translation handler

        k is the name of the translation, like "\uf813 aesthetic"
        v is the definition of the offset lookup, like:
        [s0,e0..,sN,eN],[r0...,rN]
        s: : start target code point range, e: end code point range,
        r: replacement code point.
        There must be either a correspoinding r-value for each s,e pair,
        or a single r-value.

        when offering alternate translations, wrap everything in outer
        arrays like:
        [[[s0A,e0A...sNA,eNA],[r0A...rNA]],[[[s0B,e0B...sNB,eNB],[r0B...rNB]]]

        Please see get_trans() for info on the other arguments
        """
        reverse_trans = kwargs.get('reverse_trans', False)
        if reverse_trans:
            # TODO: Code point ranges are actually easily
            # reversed... maybe implement a reverse method, or
            # even check if the reversal method has been implemented?
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
        dls.append(ril)

    def _set_repo_dir(self, rdpath):
        db_names = self.list_trans(rdpath)
        if len(db_names) <= 0:
            msg = f"{rdpath}: no .json files found in directory"
            raise FileNotFoundError(msg)
        else:
            self._repo_dir = rdpath

    def list_trans(self, rdpath=None, incl='names'):
        """
        List or count available translations in the Repository.
        In a JSONRepo, there is only one translation per database, so
        this method lists translations by listing DBs.

        Any file with .json suffix in a repository's directory is assumed
        to be a valid DB.

        If rdpath is None, self._repo_dir is used instead.

        Valid options for incl (str):

        * 'name': include DB names for use with load_db()

        * 'filenames': include DB names including .json suffix

        * 'count': returns the number of DBs only

        """
        msg_notfound = f"{rdpath}: repository not found, deleted or moved"
        if rdpath is None:
            if self._repo_dir is not None:
                if path.isdir(self._repo_dir):
                    rdpath = self._repo_dir
                else:
                    raise NotADirectoryError(msg_notfound)
        elif not path.isdir(rdpath):
            self._repo_dir = None
            raise NotADirectoryError(msg_notfound)
        fnames = listdir(rdpath)
        fmap = filter(lambda s:s.endswith(SUFFIX_JSON), fnames)
        if incl == 'names':
            fmap_out = map(lambda s:s.split('.json')[0], fmap)
            return [n for n in fmap_out]
        elif incl == 'filenames':
            return [n for n in fmap]
        elif incl == 'count':
            return len([n for n in fmap])
        else:
            raise ValueError('invalid option for incl= argument')

    def load_db(self, name):
        """
        An alias for _load_trans() on JSONRepo.

        JSONRepo files contain only one database per file.

        """
        self._load_trans(name)

    def _load_trans(self, name):
        """
        Links the JSONRepo to a translation file. Returns None.

        Where:
        jr = JSONRepo('trans')

        jr.load_db('aesthetic2')
        links the 'aesthetic2' translation file from the 'trans'
        repository, importing other files linked with the 'trans-include'
        keyword as necessary.

        This method launches the recursive linking process, and performs
        the necesary cleanups that must be excluded from the recursive
        loading process.

        """
        if self._repo_dir is None:
            raise NotADirectoryError('repository directory not set')
        self._current_trans = None
        self._tmp.clear()
        self._filename_memo.clear()
        self.current_db_name = None
        try:
            self._do_load_trans(name)
            self.current_db_name = name
        finally:
            if self._fh is not None:
                self._fh.close()
                self._fh = None

    def _do_load_trans(self, name):
        """
        Performs the recursive process of reading in data from a database
        files, together with other inclusion-referenced database files.
        The results are cached in self._tmp.

        This method is intended to be called from load_trans() only.

        """
        tmp_path = self._get_db_path(name)
        if self._fh is not None:
            self._fh.close()
        self._fh = open(tmp_path, mode='r', encoding='utf-8')
        jd = JSONDecoder()
        tmp_dict = jd.decode(self._fh.read())
        # insert runtime metadata
        tmp_dict['meta'][KEY_DB_NAME] = name
        ##
        self._tmp.insert(0, tmp_dict)
        self._filename_memo.insert(0, name)
        incs = self._tmp[0].get('trans-include', [])
        if len(incs) > 0:
            for e in incs:
                if e == name:
                    fmt = 'trans-include: {}: cannot include self'
                    msg = fmt.format(name)
                    warn(msg, RuntimeWarning)
                elif e in self._filename_memo:
                    fmt = 'trans-include: {} to {}: inclusion loop detected'
                    msg = fmt.format(name, e)
                    warn(msg, RuntimeWarning)
                else:
                    self._do_load_trans(e)

    def _get_db_path(self, name):
        filename = name + SUFFIX_JSON
        return path.join(self._repo_dir, filename)

    def _dump_trans(self, full=False):
        # TODO: Return all possible translation dictionaries available.
        # When full=False, only the first translation will be returned
        # in full. Alternate dictionaries will only contain differences
        # from the first.
        raise NotImplementedError


# TextProcessor Class
#

class TextProcessor:
    """
    Unifies repositories and string translation objects, allowing
    translations to be loaded and applied in one place.

    This class is intended to be a building block for interactive
    applications or command line tools.

    """
    FQ_SEP = ':'
    def __init__(self, repo_dict={}):
        """
        To create a TextProcessor:
        TextProcessor() => empty TextProcessor
        TextProcessor(dict) => TP with preloaded repositories

        Format for dict: {REPO_NAME: REPO_OBJECT, ...}
        Only JSONRepo's are supported as repo objects at the moment.

        Repositories must be added before translations can be loaded
        and applied, please see add_repo().

        """
        self.repos = repo_dict
        self.trans_dicts = {}
        self.trans_ops_list = []
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

    def add_trans_dict(self, trans_name, n=0):
        """
        Add a translation dictionary to the TP in order to use it
        with translate(). Dictionaries can be loaded just once, but
        may be used multiple times in an operation.

        If multiple repositories have been added, to access a dictionary
        that shares a name with another in a different repository,
        use a fully qualified name like: 'REPO:TRANS', where REPO is
        the name of the repository, and TRANS is the name of the
        translation.

        Please avoid using the colon ':' in translation or database names.

        The n value selects alternate translations where available.

        """
        tname = trans_name
        repo = None
        repo_name = None
        if self.FQ_SEP in tname:
            # handle fully-qualified translation names
            alrepo = tname.split(self.FQ_SEP)[0]
            tname = tname[tname.index(self.FQ_SEP)+1:] # extract db name
            repo_names = tuple(self.repos.keys())
            if alrepo in repo_names:
                repo_name = alrepo
                repo = self.repos[repo_name]
                repo.load_db(tname)
        else:
            # if a non-FQ translation name is used, look through all
            # added repos and get the first translation found
            for name in self.list_repos(incl='valid'):
                try:
                    repo = self.repos[name]
                    repo.load_db(trans_name)
                        # load_db() raises FileNotFoundError if trans
                        # not found
                    repo_name = name
                except FileNotFoundError:
                    continue
        if repo_name is None:
            raise KeyError(f"translation {trans_name} not found in any repo")
        else:
            k = f"{repo_name}{self.FQ_SEP}{tname}.{n}"
            self.trans_dicts[k] = repo.get_trans(n=n, one_dict=True)
            self.meta[k] = repo.get_meta()

    def add_trans_ops(self, k, p=None):
        """
        Add a translation k, to the translation operations list,
        self.trans_ops_list. This list contains keys referencing translations
        in self.trans_dicts. Translations will be applied as ordered in this
        list when translate() is used.

        The argument k may be a name of a translation in self.trans_dicts,
        or its integer index. If integer indices are used, if k==0 references
        the first key in self.trans_dicts.keys().

        Optionally, the ordinal p of the new translation may be specified.
        The translation will be added before position p. By default,
        translations are added to the end of the list.

        The same translation can occur more than once on the list.

        """
        if p is None:
            p = len(self.trans_ops_list)
        if isinstance(k, int):
            dname = key_by_index(self.trans_dicts, k)
            self.trans_ops_list.insert(p, dname)
        elif isinstance(k, str):
            if k in self.trans_dicts:
                self.trans_ops_list.insert(p, k)
            # TODO: Should invalid keys/names be ignored,
            # or should they raise exceptions?

    def clear_trans(self):
        self.trans_dicts.clear()
        self.trans_ops_list.clear()

    def list_repos(self, incl='valid'):
        """
        Gets a list of names of repositories. Valid options for incl are:

        * 'valid': list names of valid repositories.

        * 'all': list names of all loaded repositories, valid repositories
          first, followed by invalid repositories in a nested list.
          A repository is invalid when it is non-existent or inaccessible.

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

    def list_trans_ops(self):
        """
        Return a list of translations that will be applied when
        translate() is used.

        """
        return self.trans_ops_list

    def pop_trans_ops(self, i):
        """
        Remove a translation i from the translation operations list,
        self.trans_ops_list and return its name.

        i is an int index, or the full name as it appears in the list.

        """
        if len(self.trans_ops_list) <= 0:
            raise ValueError("ops dict-list is empty")
        elif isinstance(i, str):
            i = self.trans_ops_list.index(i)
        elif isinstance(i, int):
            if i >= len(self.trans_ops_list):
                raise ValueError(f"last op has index {len(names)}")
        else:
            raise ValueError("please specify translation name or int index")
        return self.trans_ops_list.pop(i)

    def sample(self, plane, page, order=[]):
        """
        Returns a string of consecutive code points for previewing the
        final effects of the translation operations selected using
        add_trans_ops(). See translate() for details on using the order
        argument.

        The definition of plane is specified in the Unicode Standard
        Core Specification (e.g. plane 0x0 is U+0000 to U+FFFF inclusive,
        plane 0x1 is U+10000 to U+1FFFF, and so on...)

        A page (short for code page) is a series of 256 code points
        starting at U+0000 or any other value that is a multiple of 256.

        """
        dump = dump_code_page(plane, page)
        return self.translate(dump, order)

    def translate(self, s, order=[]):
        """
        Make some fancy text!

        Returns a string made by applying translations listed in the
        translation operation list self.trans_ops_list on s.

        Add translations to the operation list using add_trans_ops(),
        remove it using pop_trans_ops(). Translations will be performed
        as they appear in self.trans_ops_list.

        Use the order argument to override self.trans_ops_list.

        Format for order: a list of one or more dictionary names or integer
        indices. Dictionary names must be taken from the keys of
        self.trans_dicts, while indices refer to the n-th dictionary added.

        """
        if len(order) == 0:
            olist = self.trans_ops_list
        else:
            olist = [key_by_index(self.trans_dicts, i) for i in order]

        out = s
        for tn in olist:
            tdata = self.trans_dicts[tn]
            if len(tdata) > 1:
                # handle regex preprocessing if defined
                for p in tdata[1:]:
                    if type(p[0]) is re.Pattern:
                        out = (p[0]).sub(p[1],out)

            # now handle lookup-based translations
            tdict = tdata[0]
            if self.meta[tn].get('reverse-out', False):
                # handle reversed output
                tmp_rev = ''
                for c in out:
                    tmp_rev = ''.join((tdict.get(ord(c), c), tmp_rev))
                    out = tmp_rev
            else:
                out = out.translate(tdict)
        return out

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

