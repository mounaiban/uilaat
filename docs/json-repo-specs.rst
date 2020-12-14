UILAAT JSON Database Format (Version 0.5)
-----------------------------------------
This is a brief description of the format used by the database files
in the JSON Repositories. A more comprehensive specification will be
made available once the format matures.

Repositories
============
A *repository* is simply a directory containing *databases*, files
that in turn containing translation data. A repository should not
contain any other files.

Unexpected files are to be ignored during normal operation.

Databases
=========
A *database* (DB) is a text file containing translation data, formatted
to ECMA-404 specifications (commonly called JSON).  DBs have a
``.json`` suffix in their filename for easy identification on file
managers and in scripts. However, the *database name* is the filename
with the suffix excluded.

Thus, a DB named ``aesthetic`` is defined as the database contained in
a file named ``aesthetic.json`` in a repository.

When publishing DBs to a worldwide user base, please use only the most
basic ASCII Latin characters (a-z, A-Z) and Western Arabic Digits
(0-9) when naming DBs. Use hypens ``-`` (``U+0045``) in place of
punctuation symbols and avoid spaces. Names using any other characters
may be written in the ``comments`` object under ``meta``.

Database Structure
==================
A DB is a JSON file with three objects structured as such:

::

    {
      "meta": meta,
      "trans": trans,
      "trans-include": incude_array
    }

Unrecognised objects and values must be ignored.

meta
****
The *meta* object contains information not directly related to the
text processing operation, but still influential to the operation.

The following values are recognised:

::

    "meta": {
        "reverse-trans": bool
        "reverse-out": bool
        "comments": comments
    }

The ``bool`` means either ``true`` or ``false``.

* ``reverse-trans``: when set to ``true``, translation targets and
  replacements will be swapped to the fullest extent possible.

  * Please see also the section on *Reversibility* in the ``trans``
    specification, and *Locality of reverse-trans* in ``trans-include``
    for important information.

* ``reverse-out``: when set to ``true``, all text will be output in
  reverse order.

* ``comments``: an object containing comment variables; the names of
  these comment variables should be a language code. There should be
  only **one comment per database**. Multiple accurate translations
  of the same comment are counted as one comment. Inaccurate or
  inconsistent translations are regarded as extra comments and must
  be replaced or removed.

*Runtime variables* may be present in ``meta`` in in-memory DBs. These
have names starting with an underscore, like ``_db_name``. Such
variables are implementation-specific and system-dependent, and should
not be present in exported DBs.

trans
*****
The trans dictionary contains *translations*, mappings deciding how to
mangle text. UILAAT processes text character-by-character. *Targets*
are characters to be changed to their *replacements*.

The format is as follows:

::

    trans = {
      target_1: replacement_1,
      ...
      target_n: replacement_n
    }


Supported target strings
~~~~~~~~~~~~~~~~~~~~~~~~
* ``''`` **(empty string)**: default translation. Please use this
  only if replacements have to be made by default. Do not use if
  the range of code points to be replaced is very narrow. *Ranges
  are strongly recommended over default translations in most
  cases*, see the Recommendations section below for more information.

* **Single code point** (e.g. ``"a"``, ``"\uff47"``): either a one-
  character string, or a single ECMA-404 escape sequence. Please see
  the Recommendations section below for guidelines on when to use
  literals or escape sequences.

* **Surrogate pairs:** required when accessing code points ``U+10000``
  to ``U+10FFFF``, as ECMA-404 only supports four-digit, 16-bit escape
  sequences.

* **Offset declaration:** (e.g. ``"\uf811 aesthetic"``): use the
  ``U+F811`` code point as the target followed by a space (``U+0032``),
  then followed by the name of the translation.

* **Range declaration:** (e.g. ``"\uf813 Squares"``): the ``U+F813``
  code point, followed by a ``U+0032`` space, then followed by the
  name of the translation.

* **Embedded Regex declaration**: (e.g. ``"\uf812 STRIP EMAILS"``):
  use the ``U+F812`` code point, followed by a ``U+0032`` space, then
  followed by the name of the translation.

Names of offset, range and regex declarations are only for identification
purposes in user applications. They must not influence the translation.

All code point and the default translations share the highest precedence.
For offset, range and regex translations, precedence is in order of
appearance in the DB, with earlier translations taking place before
later ones.

Multi-code point targets other than surrogate pairs are not supported,
but may be included in anticipation of multi-code point support or
for preprocessing by user applications.

Supported replacement strings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
There are currently two kinds of supported replacements: strings and
arguments.

For *code point* translations, replacements can be **strings** or
**null**:

* String replacements may be made of one or more code-points, so both
  single and multi-character replacements are supported. Both character
  literals and ECMA-404 escape sequences are accepted.

* As ECMA-404 supports only 16-bit escape sequences, *surrogate pairs*
  must be used when accessing code points ``U+10000`` to ``U+10FFFF``
  inclusive, with escape sequences.

* Avoid using 32-bit escape sequences, as they vary across platforms.

* The ``U+FFFC`` code point places copies of the target in the replacement,
  each instance expands into one copy of the target.

* Specifying ``null`` as the replacement causes the target character to
  be dropped from the translated text, as seen with ``str.translate()``.

For *offset*, *range* and *regex* translations **arguments** are used
instead:

* Parameters for Range: ``[[s1, e1, s2, e2, ... sn, en], [r1, r2, ... rn]]``

  * There are two arrays wrapped in an outer array. The first array is the
    bounds array and the second is the replacement array.

  * Bound starts: ``s1, s2, sn`` are values of code point range starts, in
    *decimal*.

  * Bound ends: ``e1, e2, en`` are values of code point range ends, in
    *decimal*.

  * Every odd value in the bounds array is a range end. Ranges must have
    a minimum span of one; ``sn-en >= 1``.

  * Bounds must be ordered from lowest to highest value.

  * Replacements: ``r1, r2, rn`` are replacement strings of single or
    multiple code points, or ``null``. In this example ``r1`` is the
    replacement for code points with decimal value ``s1`` to ``e1``
    inclusive, ``r2`` is the replacement for code points ``s2`` to ``e2``,
    and so on...

  * The ``U+FFFC`` code point places copies of the target in the replacement,
    each instance expands into one copy of the target.

  * When ``null`` is used as a replacement, target characters will be
    excluded from output, as seen with Python's ``str.translate()``.

* Parameters for Regex: ``[regex, repl]``

  * ``regex`` is a string representation of a regular expression.

  * ``repl`` is a replacement string for text matched by ``regex``.

  * The ``U+FFFC`` code point places copies of the target in the replacement,
    each instance expands into one copy of the target.

  * When ``null`` is used as a replacement, target characters will be
    excluded from output, as seen with Python's ``str.translate()``.

* Parameters for Offset: ``[s, e, off]``

  * ``s`` and ``e`` are the first and last code point values affected
    by the translation, in *decimal*.

  * ``off`` is the offset value in *decimal*. Any code point ``v``
    between ``s`` and ``e`` will be translated to ``v + off``.

Alternate Replacements 
~~~~~~~~~~~~~~~~~~~~~~
When multiple replacements translations are wrapped in an array, the
replacement at index zero becomes the preferred replacement, and
subsequent replacements become *alternate replacements*.

If a DB has an unequal number of alternate replacements, the preferred
replacement will be used where alternate replacements are not available.

Reversibility
~~~~~~~~~~~~~
Only two types of translations may be reversed at this time:

* single code point or surrogate pair target to single code point or
  surrogate pair replacement

* multi code point target to single code point or surrogate pair
  replacement

Unsupported replacements should be ignored with a warning or log event.

Alternate translations must be expanded, maintaining order of appearance.
For example, ``{"z" : ["Ꙁ", "🆉", "𝖟"]}`` should expand to
``{"Ꙁ": "z", "🆉": "z", "𝖟": "z"}``.

trans-include
*************
TODO: ``trans-include`` is an array of names of other DBs within
the same repository from which all translations will be imported. If
a translation is defined in both the current and imported DB, the current
DB's translation *replaces* the imported translation.

Locality of reverse-trans
~~~~~~~~~~~~~~~~~~~~~~~~~
In an inclusion chain, the ``reverse-trans`` property in each DB must not
be imported; it applies only to the containing DB.

Recommendations
===============

Normalisation (Precomposed or Decomposed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Please use the precomposed form (NFC or NFKC) of a character where
available. This is because decomposed characters are multi-code point
and therefore not supported as targets. Moreover, consistency of
notation between targets and replacements is strongly encouraged.

Use of Escape Sequences versus Literals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Escape sequences are strongly recommended for:

* Combining characters that decorate or enclose other characters

* Characters with widespread visibility or readability problems
  due technical limitations

Escape sequences are mandatory for:

* Invisible 'characters' such as zero-width spaces, joiners and
  control code points

* The replacement character ``U+FFFC``, Offset ``U+F811``,
  Range ``U+F813`` and Regex ``U+F812`` declarations.

Escape sequences and visible characters should be mixed to maximise
human readability.

Handling of Surrogates
~~~~~~~~~~~~~~~~~~~~~~
UTF-16 surrogate pairs in JSON files must be parsed into a their
single character equivalent, as with Python's ``JSONDecoder`` by
default.

Please consider this when implementing support for this format on
other software platforms.

Use of the Default Target ''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default target causes the assigned translation to apply to **all**
code points not targeted in ``trans``, with no regard for Properties
such as Combining Class. It is only intended for development,
diagnostics and preprocessing.

When used for visual effects, default translations may cause text to
unexpectedly decompose or become disjoint when joiners, diacritics or
combining characters with semantic meanings are affected.

Examples of scripts that rely on combining and joining for legibility
include Arabic (and derivatives), and many Brahmic scripts.

Tentative Specifications
========================

Order of Precedence of Inclusions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

Database Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

Examples
========
TODO

References
==========
Ecma International. ECMA-404: *The JSON Data Interchange Syntax.* 2nd Ed,
2017 December.

Unicode Consortium. *The Unicode Standard Version 13.0 - Core Specification.*
Section 2.12, Section 3.9 (D91), Section 3.11 (D118-121).

See Also
========
Lunicode.js Repository (GitHub). https://github.com/combatwombat/Lunicode.js

