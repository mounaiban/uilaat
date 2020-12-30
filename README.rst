UILAAT: Unicode Interlingual Aesthetic Appropriation Toolkit
------------------------------------------------------------

*A Mounaiban mini-project*

What's This?
============
UILAAT is a Unicode text processing library for working with decorative
Unicode text, artistic communication devices produced by appropriation
of graphemes between languages and superfluous use of non-word symbols
and combining characters.

UILAAT is part of yet another chapter in the history of an Internet
tradition that resulted from the encounter between an ambitious goal, to
proliferate telegraphic typography support for every known (and unknown)
written language system (along with their typographic ornaments), and
the human fascination with the foreign and exotic.

*UILAAT is free software, licensed to you under the Terms of the GNU
General Public License, Version 3 or later. Please view the LICENSE file
for full terms and conditions.*

*Unicode is a registered trademark of Unicode, Inc.*

Demo
====
*Also: 𝔀𝓱𝓪𝓽 𝓬𝓪𝓷 𝔀𝓮 𝓭𝓸 𝔀𝓲𝓽𝓱 𝓽𝓱𝓲𝓼？*

Well, actually not a lot for now...

A Really Short Intro
~~~~~~~~~~~~~~~~~~~~
There is a demo module ``demos/demo.py`` that is designed for use in
the interactive prompt. To run the demo, run the following command from
the repo root (same directory as the main module ``uilaat.py``):

::

    python -im demos.demo

You should end up in the Python interactive prompt. A ready-to-play
*Text Processor* object named ``demo`` should be available.

The TP should be linked to two *repositories*; links are kept in the
``repos`` dictionary:

::

    >>> demo.repos
    {'trans': ..., 'asdf_notfound_404': ...}

    # system and version-dependent details will not be shown in
    # this example and all subsequent examples...

Repositories are simply interfaces that enable access to
*translations* (or details on how to mangle text) that are kept in
*databases*.

The built-in translation repository is called ``trans``, while
``asdf_notfound_404`` is a dummy repo for testing error handling.

To list available translations, call:

::

    >>> demo.list_trans()
    [...]

You should have a list of fully-qualified names of some translations.

Let's Fancy Text 〜⭐ﾌｧﾝｼｰﾃｯｸｽﾄ⭐しましょっ〜
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The demo Text Processor is able to run one or more translations on
input text. Get started by adding the ``trans:ascii-aesthetic``
translation:

::

    >>> demo.add_trans('trans:ascii-aesthetic')

Verify that you have added the translations by reviewing the applied
*operations*, with ``list_trans_ops()``:

::

    >>> demo.list_trans_ops()
    ['trans:ascii-aesthetic']

Now that you have added the translations, it's time to make some fancy
text with the ``translate()`` method:

::

    >>> demo.translate("quick brown fox '92-'98")
    'ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ＇９２－＇９８'

How's that for a start? 🦊

But wait, there's more!

Multi-Translation Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Translations may sometimes be combined. For example, the Squares 
translation can be used in conjnction with ``trans:ascii-aesthetic``.
To add another translation to the operation, use ``add_trans()``:

::

    >>> demo.add_trans("trans:wip-squares", n=2)

    # please note the n=2 argument, this is necessary for the wide
    # characters output by trans:ascii-aesthetic

Confirm that both translations are in effect:

::

    >>> demo.list_trans_ops()
    ['trans:ascii-aesthetic', 'trans:wip-squares']

Now, let's try making some more fancy text:

::

    >>> print(demo.translate("KITSUNE EXPRESS"))
    Ｋ⃞Ｉ⃞Ｔ⃞Ｓ⃞Ｕ⃞Ｎ⃞Ｅ⃞　Ｅ⃞Ｘ⃞Ｐ⃞Ｒ⃞Ｅ⃞Ｓ⃞Ｓ⃞

    # print() formats the string to show the wide spaces as spaces

Now, that's twice the ａｅｓｔｈｅｔｉｃ for the price of one!

To start all over, simply clear the translations from the operation
with:

::

    >>> demo.trans_ops.clear()


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

2. The software in this project is intended to be usable entirely
   offline; this is not a web API or any other kind of RPC software
   service run over the Internet.

   * Any hacker is welcome to adapt the software herein to run a
     web service (and get rich doing so) given that the software is
     free and open-source under GPLv3 T&Cs, but such use is beyond
     the scope of this project.

3. Amusement value is not the highest priority 😞

Operating System Support
========================
Unicode fancy text often borrows graphemes from scripts far beyond the
most common ones (Arabic, Cyrillic, Devanagari, Greek, Han, Hangeul,
Kana, Latin) and the other Brahmic scripts. Support for most scripts
seem to be well-covered on Android, Apple (iOS, macOS, etc...) and
Microsoft Windows systems.

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

