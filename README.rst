UILAAT: Unicode Interlingual Aesthetic Appropriation Toolkit
------------------------------------------------------------

*A Mounaiban mini-project*

What's This?
============
UILAAT is a Unicode text processing library for working with decorative
Unicode text, artistic communication devices produced by appropriation
of graphemes between languages and superfluous use of non-word symbols
and combining characters.

UILAAT is a part of yet another chapter in the history of an Internet
tradition that resulted from the encounter between an ambitious goal, to
proliferate telegraphic typography support for every known (and unknown)
written language system (along with their typographic ornaments), and
the human fascination with the foreign and exotic.

*UILAAT is free software, licensed to you under the Terms of the GNU
General Public License, Version 3 or later. Please view the LICENSE file
for full terms and conditions.*

*Unicode is a registered trademark of Unicode, Inc.*

Usage
=====
*Also: 𝔀𝓱𝓪𝓽 𝓬𝓪𝓷 𝔀𝓮 𝓭𝓸 𝔀𝓲𝓽𝓱 𝓽𝓱𝓲𝓼？*

The software can be broken down into three main parts, and its usage into
five main steps.

Parts

* Databases (DBs)

* Repositories

* Text Processors (TPs)

Steps

1. Prepare the Repositories

2. Prepare the Text Processors, and attach the Repositories to the TPs

3. Load the translations from the DBs in to the TPs

4. Prepare operations in the TPs

5. Apply the operations to input strings to make fancy text!

Demo
~~~~
There is a demo module ``demos/demo.py`` which contains a ready-to-play
Text Processor. To run the demo, run the following command from the repo
root (same directory as the main module ``uilaat.py``):

::

    python -im demos.demo

You should end up in the Python interactive prompt. There should be a
TP called ``demo``.

Preparing Repositories and TPs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Please ensure that the necessary components have been imported:

::

    from uilaat import JSONRepo, TextProcessor

Create a Repository like this:

::

    trepo = JSONRepo("trans")

JSON Repositories are the only supported repositories at time of writing,
``trans`` is a JSON repository containing built-in translations.

With the JSONRepo now ready, create a TP and attach the repository:

::

    tp = TextProcessor()
    tp.add_repo(trepo)

Verify that the repository has been attached:

::

    >>> tp.repos
    {'trans': JSONRepo('trans')}
    # the name 'trans' was automatically detected by the TextProcessor

Alternatively, repositories may be added more explicitly when creating
the TP:

::

    tp2 = TextProcessor({'repo2': JSONRepo('trans')})
    # attaching repos this way allows overriding of the repo names,
    # the JSONRepo will be added as 'repo2', instead of 'trans'

Loading Translations and Defining Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bring up a list of available translations with the list_trans() method:

::

    tp.list_trans()

The list will contain *fully-qualified* names which include the name of the
database of the translation.

Add translations to the TP's dictionary to enable their use, like this:

::

    tp.add_trans_dict('trans:wip-squares', n=0)
    tp.add_trans_dict('trans:wip-squares', n=2) # alternate translation
    tp.add_trans_dict('trans:ascii-aesthetic')
    tp.add_trans_dict('ascii-tiny-capitals')    # non-FQ name


Non-fully qualified names may be safely used if there are no databases
across multiple repositories sharing the same name. The ``n`` argument
selects alternate mappings where available.

 *PROTIP:* translations that lack alternate mappings will produce the same
 output regardless of ``n`` index.

Confirm that the translations have been added:

::

    >>> tp.trans_dicts.keys()
    dict_keys(['trans:wip-squares.0', 'trans:wip-squares.2', 'trans:ascii-aesthetic.0', 'trans:ascii-tiny-capitals.0'])

Note that translation names in ``trans_dicts`` have a dot-and-number suffix.
This corresponds to the alternate translation index specified by the ``n``
argument when the translation was added to the TP.

Define the default translation operation by adding one or more dictionaries
like this:

::

    tp.add_trans_ops('trans:wip-squares.0')
    tp.add_trans_ops(3)

Translation names must match those returned by ``tp.trans_dicts.keys()``.
Numerical indices are also accepted. The ``3`` is a reference to
``trans:ascii-tiny-capitals.0``.

Verify the operation by checking the contents of ``trans_ops_list``:

::

    >>> tp.trans_ops_list
    ['trans:ascii-tiny-capitals.0, 'trans:wip-squares.0']

Finally, use ``translate()`` to generate some text:

::

    >>> print(tp.translate("kitsune express"))
    ᴋ⃞  ɪ⃞  ᴛ⃞  s⃞  u⃞  ɴ⃞  ᴇ⃞  　ᴇ⃞  x⃞  ᴘ⃞  ʀ⃞  ᴇ⃞  s⃞  s⃞  
    # print() formats the string to show wide spaces and squares

How's that for a start? 🦊

But wait, there's more!

Remove a translation from the default operation with ``pop_trans_ops()``:

::

    >>> tp.pop_trans_ops('trans:wip-squares.0')
    'trans:wip-squares.0'
    >>> tp.translate("kitsune express")
    'ᴋɪᴛsuɴᴇ ᴇxᴘʀᴇss'

Overriding Operations with the order Argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Override the translation with alternate ops lists without redefining
the default operation with the ``order`` argument:

::

    >>> print(tp.translate("KITSUNE EXPRESS", order=[2,1]))
    Ｋ⃞Ｉ⃞Ｔ⃞Ｓ⃞Ｕ⃞Ｎ⃞Ｅ⃞　Ｅ⃞Ｘ⃞Ｐ⃞Ｒ⃞Ｅ⃞Ｓ⃞Ｓ⃞
    # remember the contents of tp.trans_dicts.keys()

Wrapping Up and Starting All Over
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start over, simply clear the translations from the TP with:

::

    >>> tp.clear_trans()


Rationale
=========
*Also:* w⃞  ʜ⃞  ʏ⃞  　ᴍ⃞  ᴀ⃞  ᴋ⃞  ᴇ⃞  　ᴀ⃞  ɴ⃞  o⃞  ᴛ⃞  ʜ⃞  ᴇ⃞  ʀ⃞  　ꜰ⃞  ᴀ⃞  ɴ⃞  c⃞  ʏ⃞  　ᴛ⃞  ᴇ⃞  x⃞  ᴛ⃞  　ʟ⃞  ɪ⃞  ʙ⃞  ʀ⃞  ᴀ⃞  ʀ⃞  ʏ⃞  ?⃞ 

This project was inspired by contemporaries such as `Lunicode.js
<https://github.com/combatwombat/Lunicode.js>`_ and `LingoJam
<https://lingojam.com>`_, yet attempts a different take on the art
and science of text mangling:

1. A stronger emphasis is placed on the linguistic aspects of fancy
   text. This project attempts to curate the relationships between
   grapheme substitutes, and possibly spark public interest and
   appreciation of language studies.

2. The software in this project is intended for on-device use; this is
   not a web API or any other kind of internet RPC software service.

   * Any hacker is still welcome to redistribute this software as
     a service (and get rich doing so), as the software is free and
     open-source under GPLv3 T&Cs, but such use is beyond the scope
     of this project.

3. Amusement value is not the highest priority, but language nerds
   can still get plenty of amusement out of the project regardless.

Operating System Support
========================
Unicode fancy text often borrows graphemes from scripts far beyond the
common ones. Support for most scripts seem to be well-covered on Android,
Apple (iOS, macOS, etc...) and Microsoft Windows systems.

On GNU/Linux or the libre BSD systems (FreeBSD, OpenBSD, etc...),
optional font packages may have to be installed to get the fancy
text to show correctly. The following fonts are recommended for
excellent coverage and permissive licensing terms:

1. `Noto <https://www.google.com/get/noto/>`_ 🥇

   * Package name prefixes: ``google-noto-*`` (DNF), ``fonts-noto*``
     (APT), ``noto-fonts`` (Pacman).

   * Unmatched coverage of both majority and minority scripts at
     time of writing.

   * SIL Open Font License terms and conditions.

2. `DejaVu Sans <https://dejavu-fonts.github.io/>`_ 🥈

   * Preinstalled on most major GNU/Linux systems.

   * Package name prefixes: ``dejavu-*`` (DNF), ``fonts-dejavu*`` (APT),
     ``ttf-dejavu*`` (Pacman).

   * Comprehensive coverage second only to Noto at time of writing.

   * `Non-standard but permissive <https://dejavu-fonts.github.io/License.html>`_     terms and conditions.

3. `GNU Unifont <https://unifoundry.com/unifont/index.html>`_ 🥉

   * Package names: ``unifont-fonts.noarch`` (DNF), ``unifont`` (APT),
     ``bdf-unifont`` (Pacman)

   * Preinstalled and used as the console font on most Debian, Ubuntu
     and derivative systems.

   * Comprehensive coverage for scripts with isolated graphemes that
     do not typically rely on combining and overlapping.

   * Aesthetics may appeal to pixel art and retrocomputing fans.

   * GNU GPLv2 (with Font Embedding Exception) terms and conditions,
     available under SIL Open Font License T&Cs for version 13.0.04 up.

TODO
====
We've got 🅱🅸🅶 🅰🅼🅱🅸🆃🅸🅾🅽🆂, but here are the ones that matter
most now:

* **More Preset Databases**: more types of fancy text, and also cleanup
  translations to convert fancy text back to clear text (really helpful
  for users of screen readers and text archivists)

* **Database Creation Tools**: creating databases is a laborious
  endeavour but helper tools such as translation managers and
  visualisers could make things easier.

* **User Apps**: desktop and mobile apps for GTK, maybe Android and
  iOS, that generate text automatically on-device at the touch of a
  button. Ideas include:

  * clipboard monitors that automatically mangles copied text

  * input methods to generate fancy text as they are typed

* **Multi-Code Point Targets**: a low-cost method of supporting
  multi-code point targets in translations would be really nice,
  as these are currently only possible with computationally-expensive
  regular expressions.

Want More?
==========
Additional information that don't quite fit here may be found in the
Wiki or the ``docs`` directory of the source tree.

