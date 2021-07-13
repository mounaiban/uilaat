UILAAT JSON Database Format (Version 0.7)
-----------------------------------------
This is a brief description of an upcoming version of the format
used by the database files in the JSON Repositories. Comprehensive
specifications will be published as the format matures.

Definitions in the Glossary apply to this document. The glossary is
in ``docs/arch-glossary.rst``.

An understanding of the ECMA-404 standard is assumed, especially
the definition of the JSON value types in Section 5 of ECMA-404.

Repositories
============
A *repository* is simply a directory containing *databases* (DBs).

Databases
=========
A DB is a text file containing translation and operation data, formatted
to ECMA-404 specifications (commonly called JSON).  DBs have a
``.json`` suffix in their filename for easy identification on file
managers and in scripts.

The *database name* is the filename without the suffix. For example, the
name of a DB contained within the file ``aesthetic.json`` is simply
``aesthetic``.

Files that are not DBs should be ignored during normal operation.

Advice for Public Databases
***************************
When publishing DBs to a worldwide public user base, please use only
basic ASCII Latin characters (a-z, A-Z) and Western Arabic Digits
(0-9) when naming DBs. Use hypens ``-`` (``U+002D``) in place of
punctuation symbols and avoid spaces.

Where necessary, the native name containing characters other than the
ASCII Latin characters may be written in the ``db-name`` section inside
the ``meta`` section. See the Database Structure for details.

Database Structure
==================

Summary
*******
Here is a summary of the correct placement for recognised *sections*:

::

    {
      "meta": {
            "db-name": {
                    lang_0: c_0,
                    ...,
                    lang_n: c_n
                }
            "authors": [author_0, ..., author_n],
            "comments": [c_0, ..., c_n],
            "copyright": copyright,
            "license": license,
            "reverse-trans": bool,
            "reverse-out": bool,
            "_runtime_0": runtime_0,
            "_runtime_n": runtime_n
        }
      "trans": {
            target_0: repl_0,
            ...,
            target_n: repl_n
        }
      "trans-include": [db_0, ..., db_n]
    }

Unrecognised sections must be ignored. A section is identical to a JSON
*object*.

The ``bool`` means either ``true`` or ``false``.

meta
****
The *meta* section contains information other than mappings for the
translation data.

* ``db-name``: section containing zero or more descriptive names for the DB
  as strings. Use only one name; alternate names must be the translations of
  the original. Each ``db-name`` is named with an IETF BCP 47 language tag.

  * The language tag syntax is specified in Section 2.1 of BCP 47.

* ``authors``: an array one or more strings identifying contributors to the
  database. The creator ``author_0`` is named first, with subsequent
  contributors ``author_1`` until ``author_n`` named *in order of time of
  first contribution*.

  * If the DB is an adaptation of another DB, name the original creators
    first. The creator of the adaptation must appear only after the last
    contributor of the original DB. Subsequent contributors are named
    thereafter, in order of time of first contribution.

* ``comments``: an array containing zero or more notes as strings. These
  notes are intended for communicating technical issues between database
  creators, maintainers and end users.

* ``copyright``: a string identifying the copyright owner of the database;
  if the database is public domain, a dedication is used instead.

* ``license``: a URI referencing a document containing the full terms
  and conditions of use of the DB.

  * The default value is ``NDA`` (Unicode: U+004E, U+0044, U+0041).
    Unlicensed databases are assumed to be confidential and restricted
    from distribution.

  * Examples for Creative Commons licenses:

    * CC-BY-4.0: https://creativecommons.org/licenses/by/4.0/legalcode

    * CC-BY-SA-4.0: https://creativecommons.org/licenses/by-sa/4.0/legalcode

    * CC-BY-ND-4.0: https://creativecommons.org/licenses/by-nd/4.0/legalcode

  * Example for Public Domain DBs:

    * CC0: https://creativecommons.org/publicdomain/zero/1.0/legalcode

  * Examples for GNU Licenses:

    * GPLv3: https://www.gnu.org/licenses/gpl-3.0.html

    * GFDLv1.3: https://www.gnu.org/licenses/fdl-1.3.html

* ``reverse-trans``: when set to ``true``, translation targets and
  replacements will be swapped to the fullest extent possible.

  * Please see also the section on *Reversibility* in the ``trans``
    specification.

* ``reverse-out``: when set to ``true``, the output of the translation
  will be in reverse order (i.e. ``reverse`` => ``esrever``).

*Runtime variables* specific to the application (or an instance of it)
may also be placed in ``meta``. These variables should have a name
starting with an underscore, like ``_db_name``. Runtime variables should
be excluded from exported DBs as they are system-dependent, and may leak
confidential information.

Please do not abuse the ``meta`` section by cramming excess miscellaneous
data.

trans
*****
The trans section contains *translations*. UILAAT processes text
character-by-character, replacing *targets* with *replcements*.

The supported translation types are: **default**, **single character**,
**offset**, **range** and **regex**.

Regex is not quite a translation, but a preprocessing stage. However, it
is placed in ``trans`` with the translations for readibility.

Replacement Points (\ufffc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every instance of the Unicode Object Replacement Character ``\ufffc`` in
the replacement string will be replaced with a copy of the target.

This example surrounds every letter ``a`` with grinning cat faces:

::

    "trans": {
        "a": "😸\ufffc😸"
    }

Deleting Targeted Characters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Specifying ``null`` as the replacement causes the target character to
be dropped from the translated text, as seen with ``str.translate()``.

This example removes all instances of the *reversed hand with middle
finger extended* emoji:

::

    "trans": {
        "🖕": null
    }

Default Mapping
~~~~~~~~~~~~~~~
When the empty string ``""`` is used as a target, this sets the default
translation. *Any* string that does not match any other mapping will be
replaced.

Ranges are strongly recommended over default translations in most cases,
see the Recommendations section below for more information.

Examples:

Delete all characters not targeted by any other mapping. Be aware of the
lack of ``"`` quote marks around the ``null`` keyword:

::

    "trans": {
        "": null
    }

Effectively leave the original text alone, by replacing the target with
itself:

::

    "trans": {
        "": "\ufffc"

Surround all characters not targeted by any other mapping with weary cat
faces:

::

    "trans": {
        "": "🙀\ufffc🙀"
    }

TODO: How to handle multiple definitions of the default translation?

Single Character Mapping
~~~~~~~~~~~~~~~~~~~~~~~~
A basic mapping can be made by targeting a single character or a code
point, and replacing it with null, a single or multiple characters.

Please see the Recommendations section below for guidelines on when to
use literals or escape sequences.

Examples:

Replace the letter ``a`` with its fullwidth version ``ａ``, using code
points:

::

    "trans": {
        "a": "\uff41"
    }

Replace the letter ``a`` with its fullwidth version ``ａ``, using string
literals:

::

    "trans": {
        "a": "ａ"
    }

Delete zero-width non-joiner control characters.

::

    "trans": {
        "\u200c": null
    }

Delete zero-width non-joiner control characters, using ``U+F8FF``:

::

    "trans": {
        "\u200c": "\uf8ff"
    }

The ``U+F8FF`` code point is accepted as a substitute for ``null``.

Multi-character targets are not supported.

TODO: What about multi-code point single characters, like emoji with
skin tone and hair colour modifiers?

Surrogate Pair Mapping
~~~~~~~~~~~~~~~~~~~~~~
This is another form of a Single Character Mapping for characters
encoded by code points ``U+10000`` to ``U+10FFFF`` inclusive.
As ECMA404 only supports 16-bit code points, surrogate pairs
mapping is used instead.

For the method of deriving surrogate pairs, please see D91 in
section 3.1 in the *Unicode Standard Core Specification*.

Examples:

Replace a *martyria plagious tetartos ichos* symbol ``U+1D0B3``.

::

    "trans": {
        "\ud834\udcb3": "λˮπδ"
    }

Replace ``B`` with a Phaistos Disc Manacles symbol ``U+101DD``:

::

    "trans": {
        "B": "\ud800\udddd"
    }


Offset Mapping
~~~~~~~~~~~~~~
Transpose any code points within a single range by a fixed value.

An offset mapping is declared by using ``U+F811`` as the first character
of a target in the ``trans`` section. The mapping can be named by adding
a space (``U+0020``) followed by a name.

The offset parameters are set in the corresponding replacement as such:
``s e off; comments``. A code point ``x`` of a value from ``s`` to ``e``
inclusive will be transposed to ``x + off``.

All content from the last semicolon ``;`` will be regarded as a comment.
Code point values are specified in decimal.

Examples:

Change all basic ASCII characters (``U+0021`` to ``U+007F``) to their
Shift JIS-esque fullwidth equivalents (``U+FF01`` to ``U+FF5F``):

::

    "trans" : {
        "\uf811 aesthetic": "33 127 65248"
    }

Change Shift JIS-esque fullwidth back to regular ASCII characters:

::

    "trans" : {
        "\uf811 reset_A": "65281 65375 -65248; negative offset"
    }

The resulting code point value must be from 0 to 111411 inclusive
(``0x0`` to ``0x10FFFF``).

Range Mapping
~~~~~~~~~~~~~
Replace code points within ranges with a corresponding string.

Declare a range mapping by using ``U+F813`` as the first character
of a target under the ``trans`` section. The mapping can be named by
adding a space (``U+0020``) followed by a name.

The following range mapping types are supported:

* One value per range: ``s1..e1 v1, s2..e2 v2, ...; comment``
  A code point between ``s1`` and ``e1`` inclusive will be mapped
  to ``v1``.

* One value for all ranges: ``s1..e1, s2..e2 v; comment``
  Assign a value only to the last range. A code point that is between
  any given ``s`` and ``e`` inclusive will be mapped to ``v``.

All content from the last semicolon ``;`` will be regarded as a comment.
Code point values are specified in decimal.

Examples:

Enclose all Shift JIS-esque fullwidth Latin characters in squares:

::

    "trans": {
        "\uf813 sjfw_squares": "65281..65376 65504..65510 \ufffc\u20de"
    }

Enclose basic uppercase and lowercase letters from Alpha to Omega
in bubbles:

::

    "trans": {
        "\uf813 lbubbles": "913..937, 945..969 \ufffc\u20dd;"
    }

Normalise space characters and remove enclosing characters:

::

    "trans": {
        "\uf813 cup": "8194..8203 \u0020, 8413..8416 \uf8ff, 8418..8420 \uf8ff;"
    }

An ``s`` value must be equal to or smaller than its corresponding
``e`` value. Every subsequent ``s`` value must be larger than all
``s`` and ``e`` values before it; the ranges must be ordered from
smallest to largest.

All values are specified in decimal.

When ``U+F8FF`` is used as a replacement, target characters will be
deleted.

Embedded Regex
~~~~~~~~~~~~~~
Embed a regular expression (regex) for preprocessing text.

Declare a range mapping by using ``U+F812`` as the first character
of a target under the ``trans`` section. The mapping can be named by
adding a space (``U+0020``) followed by a name.

The regex and replacement is set up in the corresponding mapping like:
``regex repl; comments``. Text matching the regular expression
``regex`` will be replaced with ``repl``.

All content from the last semicolon ``;`` will be regarded as a comment.
If the replacement contains a semicolon, end it with another semicolon to
protect it.

Examples:

Redact email addresses:

::

    "trans": {
        "\uf812 strip_emails": "\b\S+@\S+\b \uf8ff; remove most emails"
    }

When ``U+F8FF`` is used as a replacement, target characters will be
deleted.

Add an *incoming envelope* icon next to email addresses:

::

    "trans": {
        "\uf812 mark_emails": "\b\S+@\S+\b 📨\ufffc; put envelope on email"
    }

Using regexes that end with a space with a terminal escape sequence:

::

    "trans": {
        "\uf812 space_end": "\b SPACEMAN\u0020 👽;"
    }

All content between the last space and the last semicolon will be regarded
as the replacement. If the regex ends with a space, use a second space or
``\u0020`` to protect the regex.

All content from the last semicolon ``;`` will be regarded as a comment.
If the replacement contains a semicolon, end it with a semicolon to
protect the statement.

Alternate Replacements
~~~~~~~~~~~~~~~~~~~~~~
When multiple replacements translations are wrapped in an array, the
replacement at index zero becomes the preferred replacement, and
subsequent replacements become *alternate replacements*.

In the following example, the possible translations for the word
``piazza`` are ``pi⋀ꙀꙀ⋀``, ``pi🅰🆉🆉🅰`` and ``pi𝔞𝖟𝖟𝔞``:

::

    "trans": {
        "a": ["⋀", "🅰", "𝔞"],
        "z": ["Ꙁ", "🆉", "𝖟"]
    }

If a DB has an unequal number of alternate replacements, no
translation will be performed if there is no replacement for the
selected alternate translation.

In the following example, the possible translations for the word
``piazza`` are ``pi⋀ꙀꙀ⋀``, ``pi𝔞🆉🆉𝔞`` and ``pia𝖟𝖟a``:

::

    "trans": {
        "a": ["⋀", "𝔞"],
        "z": ["Ꙁ", "🆉", "𝖟"]
    }

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

The choice between escape sequences and literals should be made to
maximise human readability.

Handling of Surrogates
~~~~~~~~~~~~~~~~~~~~~~
UTF-16 surrogate pairs in JSON files must be parsed into a their
single character equivalent, as with Python's ``JSONDecoder`` by
default.

Please consider this when porting support for JSON Repositories to
other programming languages or software platforms.

Use of the Default Target ''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The default target causes the assigned translation to apply to **all**
code points not targeted in ``trans``, with no regard for Properties
such as Combining Class. It is only intended for development,
diagnostics and preprocessing.

When used for visual effects, default translations may impact the
legibility of the text when joiners, diacritics or combining characters
with semantic meanings are affected. Examples of scripts that rely on
combining and joining for legibility include Arabic (and derivatives),
and many Brahmic scripts.

Tentative Specifications
========================

Locality of reverse-trans
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO: if a DB with reverse-trans applied is imported, the reversal must
be performed *before* importing.

Order of Precedence of Inclusions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO

Order of Precedence of Mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Mappings are broken up into groups terminated by embedded regexes. The
groups are then processed in order of appearance, starting from the top
of the list.

Consider the following example:

::

    "trans": {
        "🜁": "a",
        "🝁" : "t",
        "\uf812 strip_emails": "\b\S+@\S+\b 🙊",
        "\uf811 sfjw": "33 127 65248"
    }

The phrase ``13bl🜁ckc🜁🝁s spri🝁espiri🝁@moun🜁iban.com`` should translate
to ``１３ｂｌａｃｋｃａｔｓ 🙊``.

The translation should be divided into two groups. The first two mappings
are in group 0. The regex marks the end of group 0. The offset mapping
``sfjw`` is in group 1.

The translation is then to be done in three stages:

1. ``13bl🜁ckc🜁🝁s spri🝁espiri🝁@m♥un🜁iban.c♥m`` is translated to
   ``13blackcats spritespirit@mounaiban.com`` by group 0,

2. ``13blackcats spritespirit@mounaiban.com`` to ``13blackcats 🙊``
   by the regex,

3. ``13blackcats 🙊`` to ``１３ｂｌａｃｋｃａｔｓ 🙊`` by group 1.

TODO: If two or more regexes appear in a row, regard them as delimiters
for empty groups.

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

IETF Trust. BCP 47. https://tools.ietf.org/html/bcp47

Unicode Consortium. *The Unicode Standard Version 13.0 - Core Specification.*
Section 2.12, Section 3.9 (D91), Section 3.11 (D118-121).

See Also
========
Lunicode.js Repository (GitHub). https://github.com/combatwombat/Lunicode.js

