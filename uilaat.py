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
from json import JSONDecoder
from os import path
from warnings import warn

# Supported Replacement Scopes
SCOPE_CHAR = 'C'
SCOPE_STR = 'S'
SCOPE_NOP = ''

KEY_DB_NAME = '_db_name'
SUBPOINT = '\ufffc' # Unicode Object Replacement
SUFFIX_JSON = '.json'
VERSION = '0.5'
iformat_default = SUBPOINT # nothing but a single SP
insert_default = lambda c : iformat_default.replace(SUBPOINT, c)

# Please review the notes at the end of this file for an
# understanding of the conventions used in this library.

def in_range(r_start, r_end, char):
    if (r_start is None) or (r_end is None):
        return True
    elif (r_start > r_end):
        warn('r_start is past r_end', RuntimeWarning)
    if len(char) > 1:
        n = ord(char[0])
    else:
        n = ord(char)
    return n >= r_start and n <= r_end 

def sfunc_from_covar(r_start, r_end, offset):
    """
    Create a Code Point Value Arithmetic substitution function.
    These are used for substitutions that can be performed by
    transposing code point values with a single addition or
    subtraction.

    This function has character scope.
    
    Arguments
    ---------
    * r_start - (int) the beginning of the code point range to which
        the replacement applies
    
    * r_end - (int) the last code point in the code point range to
        which the replacement applies

    * offset - (int) the value to add to or subtract from for an
        affected code point; use a negative int for subtraction

    Limitations
    -----------
    Handling of multi-code point characters is currently rather basic.
    Only the first code point of the character can be modified, while
    the other code points are copied unmodified.
    """

    # TODO: Is there another way of performing this using
    # more built-in Python features or regular expressions?
    def fn_covar(c):
        if isinstance(c, str) is False:
            raise TypeError('this function is only for characters')
        if in_range(r_start, r_end, c):
            n = ord(c[0])
            if len(c) > 1:
                return ''.join((chr(n+offset), c[1:],))
            else:
                return chr(n+offset)
        else:
            return c

    return (fn_covar, SCOPE_CHAR,)

def sfunc_from_dict(r_start, r_end, dic):
    """
    Create a Dictionary Substitution function.
    These are used for substitutions where replacements for targeted
    characters are specified in a dictionary.

    This function has character scope.

    Arguments
    ---------
    * r_start - (int) the beginning of the code point range to which
        the replacement applies; if set to None, replacements will be
        performed on as many characters as possible.
    
    * r_end - (int) the last code point in the code point range to
        which the replacement applies; if set to None, replacements will
        be performed on as many characters as possible.

    * dic - (dict) Dictionary containing the substitutions, with
        targeted characters as keys, and the replacements as
        substitutions. Characters not targeted by the dictionary are
        copied over unchanged.

    Limitations
    -----------
    Multi-code point characters and Multi-character targets are currenly
    not supported. However, multi-code point or multi-character
    replacements are still supported.
    """

    if isinstance(dic, dict) is False:
        raise TypeError('use only dicts with this substitution type')

    def fn_dict(c):
        if isinstance(c, str) is False:
            raise TypeError('this function is only for characters')
        elif len(c) > 1:
            fmt = 'multi-char or multi-codepoint char {} not supported'
            msg = fmt.format(c)
            warn(msg, RuntimeWarning)
        if in_range(r_start, r_end, c) is False:
            return c
        pre_out_default = dic.get('', iformat_default)
        out = dic.get(c)
        if out is not None:
            return out.replace(SUBPOINT, c)
        else:
            return pre_out_default.replace(SUBPOINT, c)

    return (fn_dict, SCOPE_CHAR,)

def sfunc_from_re(re_str, repl):
    """
    Create a Regular Expression (RE) function.
    These are used for substitutions that cannot be trivially described
    in terms of characters. By leveraging the capabilities of REs,
    pattern, multi-character and multi-code point targets are fully
    supported.

    This function has string scope.

    Arguments
    ---------
    * re_str - (str) a string representation of an RE, for 
        information on RE syntax, see the Python Standard Library
        documentation on Regular Expressions:
        https://docs.python.org/3/library/re.html

    * repl - (str) a replacement string for characters matched
        by re_str

    Limitations
    -----------
    Regular expressions can be slow and computationally expensive.
    Please use this type of function sparingly.

    As there is no single standard for REs, the Perl-Compatible Regular
    Expressions (PCRE) standard is preferred for compatibility with
    other implementations of UILAAT. Please be aware that the level of
    support for PCRE can vary widely between platforms.
    """

    def fn_re(s):
        rs = repl
        if isinstance(s, str) is False:
            raise TypeError('this function is only for strings')
        wrex_f = re.compile(re_str)
        finish_rs = lambda m : rs.replace(SUBPOINT, m.group(0))
        return wrex_f.sub(finish_rs, s)

    return (fn_re, SCOPE_STR,)

def sfunc_from_list(sf_list):
    """
    Create a Multi-Substitution Function which applies one or more
    other functions in a single call. This type of function may also be
    used as an adaptor for converting a single character-scoped function
    to a string-scoped one.

    This function has string scope.

    Arguments
    ---------
    * sf_list - (iter) an iterable collection (e.g. tuple, list, ...)
        containing substitution functions to be run, and metadata for
        guiding the execution of the functions.

    Warnings
    --------
    * RuntimeWarning - emitted when a function of an unsupported
        scope is encountered; such functions are skipped over.
    
    Usage Notes
    -----------
    Please see the Function Format and Usage at the end of this file
    for information on the syntax and format of sf_list.
    """
    
    subs = sf_list
    def fn_multi(s):
        nonlocal subs
        i = 0
        i_cs_start = 0
        i_cs_end = 0
        out = s
        def do_fns_char():
            # run all collected character-scope functions on input 
            nonlocal out
            tmp_s = ''
            for c in out:
                tmp_c = c
                for i in range(i_cs_start, i_cs_end+1):
                    fn_il = subs[i][0]
                    tmp_c = fn_il(tmp_c)
                tmp_s = ''.join((tmp_s, tmp_c,))
            out = tmp_s

        sb_scope_prev = None
        for sb in subs:
            sb_scope = sb[1]
            fn_ol = sb[0]
            if (sb_scope == SCOPE_CHAR):
                # for performance reasons, identify multiple successive
                # char-scope functions, and run them on the same pass
                if (sb_scope != sb_scope_prev):
                    i_cs_start = i
                i_cs_end = i
            elif sb_scope == SCOPE_STR:
                #i_cs_end = i
                do_fns_char()
                out = fn_ol(out)
            else:
                fmt = '{}: function with invalid scope not included'
                msg = fmt.format(i)
                warn(msg, RuntimeWarning)
            i += 1
            sb_scope_prev = sb_scope
        do_fns_char()
        return out

    return (fn_multi, SCOPE_STR,)


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
        # assign operating values
        self._start = start
        self._end = end
        self._offset = offset

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

    Where:
    vs = ('\u2615', '\U00001f35c', '\U0001f356')
    keys = (7,9,12,14,17,21)
    L = (vs, keys)

    7 <= x <= 9; L[x] == '\u2615'
    12 <= x <= 14; L[x] == '\U0001f35c'
    17 <= x <= 21; L[x] == '\U0001f356'

    All other values of x raise a LookupError.

    See __init__ for more options.

    This class, when used with int keys, is intended for use with
    str.translate().

    """
    DEFAULT_VALUE = True

    def validate(self):
        # TODO: This method will check if the list is well-formed.
        #
        # The range keys must be sorted from the smallest value to
        # the largest. All keys must be of the same type.
        raise NotImplementedError

    def __init__(self, range_keys, values=None, **kwargs):
        """
        How to create a basic RangeIndexedList:
        L = RangeIndexedList(keys, values)

        * keys is a sorted sequence (list, tuple), of items which
          specifies the ranges; zero and even-indexed items specify
          range starts and odd-indexed items specify range stops.
          Range includes starts and stops.

        * values is a sequence of items specifying items to be returned
          as a result of a lookup. Each item corresponds to a range
          defined in keys, thus values must contain exactly half the
          number of items as keys.

        Accepted keyword arguments:

        * default - when values is None, this value will be returned
           for all keys falling into any range.

        * copy_key - (bool) if set to True, all instances of the Unicode
           Replacement Character, U+FFFC, in the output will be replaced
           by a single copy of the key.
           If int keys are used, the ord() of the key is used as the
           replacement instead.

        """
        if len(range_keys) & 0x01 != 0:
            name = self.__class__.__name__
            msg = '{} must contain an even number of keys'.format(name)
            raise ValueError(msg)
        if values is None:
            default = kwargs.get('default', self.DEFAULT_VALUE)
            values = (default,) * (len(range_keys)//2)
        else:
            if len(values) != len(range_keys)//2:
                msg = 'number of values must be half the number of keys'
                raise ValueError(msg)

        self._copy_key = kwargs.get('copy_key', False)
        self._range_keys = list(range_keys)
        self._values = values

    def __getitem__(self, key):
        # This method performs a binary search to find a spot where
        # key would have been placed if it were in the range list.
        #
        # If key is equal to any value in the range list, or ends up
        # with an odd index/even position, then the key is in a range.
        #
        i_start = 0
        i_end = len(self._range_keys)
        i = i_end // 2
        while i_end - i_start > 1:
            i = i_start + ((i_end-i_start) // 2)
            i_prev = i-1
            key_low = self._range_keys[i_prev]
            key_high = self._range_keys[i]
            if key_low <= key <= key_high:
                if key == key_low or key == key_high or i_prev & 0x01 == 0:
                    out = self._values[i//2]
                    if self._copy_key is False:
                        return out
                    else:
                        if ('\ufffc' in out) and (isinstance(key, int) is True):
                            return out.replace('\ufffc', chr(key))
                        else:
                            return out
                else:
                    raise LookupError('key not in a range')
            else:
                if key < key_low:
                    i_end = i
                else:
                    i_start = i
        raise LookupError('key is before first range or past last range')

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
      where a replacement character is found.

    * One-character string keys are not allowed, but are
      automatically converted to their Unicode code point value
      with ord().

    This class is for use with str.translate().

    """
    _super = None

    def __init__(self, *args, **kwargs):
        self._out_default = SUBPOINT
        self._super = super()
        self._super.__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key == '':
                self._out_default = value
                self._super.__setitem__('', value)
            elif len(key) == 1:
                self._super.__setitem__(ord(key), value)

    def __getitem__(self, key):
        out = self._out_default
        ins = key
        try:
            out = self._super.__getitem__(key)
        except LookupError:
            if isinstance(key, int) is True:
                ins = chr(key)
            else:
                ins = key
        finally:
            if out is None:
                return None
            if SUBPOINT in out:
                return out.replace(SUBPOINT, ins)
            else:
                return out

    def reset_default(self):
        if '' in self:
            self._out_default = self.__getitem__('')
        else:
            self._out_default = SUBPOINT

    def set_default(self, value=None):
        self._out_default = value

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
# Function Format and Usage
# =========================
# Substitution functions accept a single argument like: f(x)
# The scope of a function determines what is accepted for the argument.
# There are currently only three scopes:
# 
#   * Character - the function takes a character (a one-character str 
#       in Python) and returns its replacement.
#
#   * String - the function takes an entire string and outputs a
#       another version with the subsitutions.
#
#   * NOP - do not use the function (this is used for toggling functions
#       temporarily during runtime)
#
# A function can only be of one scope at any given time.
#
# Multi-Substitution function lists contain tuples that are formatted as
# follows: (function, scope, meta_dict)
#
# The scope is implemented as a str, supported scopes are found near
# the top of this file. The meta_dict is a dict-like object which
# contains additional information for a user's application.
#
# Functions are applied in the same order as they appear in the list.
# 

