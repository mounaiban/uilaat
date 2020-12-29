UILAAT: Unicode Interlingual Aesthetic Appropriation Toolkit
------------------------------------------------------------

*A Mounaiban mini-project*

What's This?
============
UILAAT is a Unicode text processing library for working with decorative
Unicode text, artistic communication devices produced by appropriation
of graphemes between languages and superfluous use of non-word symbols
and combining characters.

UILAAT is yet another chapter of the history of an Internet tradition
that resulted from the encounter between an ambitious goal, to
proliferate telegraphic typography support for every known (and unknown)
written language system (along with their typographic ornaments), and
the human fascination with the foreign and exotic.

*UILAAT is free software, licensed to you under the Terms of the GNU
General Public License, Version 3 or later. Please view the LICENSE file
for full terms and conditions.*

Unicode is a registered trademark of Unicode, Inc.

Demo
====
*Also: 𝔀𝓱𝓪𝓽 𝓬𝓪𝓷 𝔀𝓮 𝓭𝓸 𝔀𝓲𝓽𝓱 𝓽𝓱𝓲𝓼？*

Well, actually not a lot for now...

A Really Short Intro
~~~~~~~~~~~~~~~~~~~~
There is a demo module ``demos/demo.py`` that is designed for use in
an interactive shell. You can access it from the repo root (same
directory as the main module ``uilaat.py``) by running:

::

    python -im demos.demo

If your system is correctly set up, you should be inside the Python
REPL shell. You will have instant access to a *Text Processor* object
named ``demo``.

The TP should be linked to two *translation repositories*; these links
are kept in the ``repos`` dictionary:

::

    >>> demo.repos
    {'trans': ..., 'asdf_notfound_404': ...}

    # system and version-dependent details will not be shown in
    # this example and all subsequent examples...

The built-in translation repository is called ``trans``, while the other,
``asdf_notfound_404`` is a dummy repo intended to test error handling
routines.

Translation repositories are simply interfaces to databases that contain
*translations*, or details on how to mangle text.

To list all translations, call:

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
*operations*, by peeking into the ``trans_ops`` attribute:

::

    >>> demo.trans_ops
    {'trans:ascii-aesthetic': ... }

Note that some translations may contain a large number of *mappings*,
making them hard to read in the REPL shell. Here's an alternative that
shows only the names:

::

    >>> list(demo.trans_ops.keys())
    ['trans:ascii-aesthetic', ...]

    # quick Python quiz: what data type is demo.translations, and
    # what are you doing with list()?

Now that you have added the translations, it's time to make some fancy
text with the ``translate()`` method:

::

    >>> demo.translate("quick brown fox '92-'98")
    'ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ＇９２－＇９８'

How's that for a start? 🦊

Rationale
=========
*Also:* ``w⃞ h⃞ y⃞  ⃞ c⃞ r⃞ e⃞ a⃞ t⃞ e⃞  ⃞ a⃞ n⃞ o⃞ t⃞ h⃞ e⃞ r⃞  ⃞ f⃞ a⃞ n⃞ c⃞ y⃞  ⃞ U⃞ n⃞ i⃞ c⃞ o⃞ d⃞ e⃞  ⃞ t⃞ e⃞ x⃞ t⃞  ⃞ l⃞ i⃞ b⃞ r⃞ a⃞ r⃞ y⃞ ?⃞``

This project was inspired by contemporaries such as `Lunicode.js <https://github.com/combatwombat/Lunicode.js>`_
and `LingoJam <https://lingojam.com>`_, but with a different take on the art and science of text mangling:

1. A stronger emphasis is placed on the linguistic aspect of fancy text:
   this project attempts to curate the relationships between grapheme
   substitutes, and possibly spark public interest and appreciation of
   language studies.

2. The software in this project is intended to be usable entirely
   offline; this is not a web API or any other kind of RPC software
   service run over the Internet.

   * Any hacker is welcome to adapt the software herein to run a
     web service (and get rich doing so) given that the software is
     free and open-source under GPLv3 T&Cs, but such use is beyond
     the scope of this project.

3. Amusement value is not the highest priority 😞

TODO
====
We've got 🅱🅸🅶 🅰🅼🅱🅸🆃🅸🅾🅽🆂, but here are the ones that matter
most now:

* **More Preset Translation Databases**: more types of fancy text,
  and possibly cleanup translations to convert fancy text back to
  clear text for screen readers or note takers.

* **Translation Database Creation Tools**: creating a translation
  database is a laborious endeavour but having some helper tools,
  such as a translation manager or a graph visualiser, can make it
  easier.

* **User Apps**: desktop and mobile apps for GTK, maybe Android and
  iOS, so that users may generate text automatically on-device at the
  touch of a button. Ideas include:

  * clipboard monitor that automatically mangles copied text

  * input methods to generate fancy text as they are typed

* **Multi-Code Point Targets**: the ability to handle multi-code point
  targets in translations would be really nice, as these can currently
  only be done with computationally-expensive regular expressions.

