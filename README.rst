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
written language and dingbat, and the human fascination with
the foreign and exotic.

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

Demo and Quick Start
~~~~~~~~~~~~~~~~~~~~
There is a demo module ``demos/demo.py`` which contains a ready-to-play
Text Processor. To run the demo, run the following command from the repo
root (same directory as the main module ``uilaat.py``):

::

    python -im demos.demo

You should end up in the Python interactive prompt. There should be a
TP called ``demo``.

A database and repository has been prepared for you. The demonstration TP
has been linked to a built-in database ``trans`` via a repository named
``jr``.

Loading Translations and Preparing Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to start making fancy text, the translations have to be loaded
and queued into an operation list.

Bring up a list of available translations with the list_trans() method:

::

    demo.list_trans()

The list will contain *fully-qualified* names which include the name of the
database of the translation.

Load the translations like this:

::

    demo.add_trans_dict('trans:wip-squares', n=0)
    demo.add_trans_dict('trans:wip-squares', n=2) # alternate translation
    demo.add_trans_dict('trans:ascii-aesthetic')
    demo.add_trans_dict('ascii-tiny-capitals')    # non-FQ name

Non-fully qualified names may be safely used when using only one repository,
or if there aren't multiple databases from different repos sharing the same
name. The ``n`` argument selects alternate mappings where available.

 *PROTIP:* translations that lack alternate mappings will produce the same
 output regardless of ``n`` index.

Confirm that the translations have been added like this:

::

    >>> for d in demo.trans_dicts.keys():
    ...     print(d)
    ...
    trans:wip-squares.0
    trans:wip-squares.2
    trans:ascii-aesthetic.0
    trans:ascii-tiny-capitals.0

Note the a dot-and-number suffixes; these correspond to the alternate
translation index specified by the ``n`` argument when the translation was
added to the TP.

Define the default translation operation by queuing one or more dictionaries
like this:

::

    demo.add_trans_ops('trans:wip-squares.0')
    demo.add_trans_ops(3)

Translation names must match those in ``demo.trans_dicts.keys()``.
Numerical indices are also accepted. The ``3`` is a reference to
``trans:ascii-tiny-capitals.0``.

Verify the operation by checking the contents of ``trans_ops_list``:

::

    >>> demo.trans_ops_list
    ['trans:ascii-tiny-capitals.0, 'trans:wip-squares.0']

Finally, use ``translate()`` to generate some text:

::

    >>> print(demo.translate("kitsune express"))
    ᴋ⃞  ɪ⃞  ᴛ⃞  s⃞  u⃞  ɴ⃞  ᴇ⃞  　ᴇ⃞  x⃞  ᴘ⃞  ʀ⃞  ᴇ⃞  s⃞  s⃞  
    # print() formats the string to show wide spaces and squares

How's that for a start? 🦊

Removing Operations
~~~~~~~~~~~~~~~~~~~
Remove a translation from the default operation with ``pop_trans_ops()``:

::

    >>> demo.pop_trans_ops('trans:wip-squares.0')
    'trans:wip-squares.0'
    >>> demo.translate("kitsune express")
    'ᴋɪᴛsuɴᴇ ᴇxᴘʀᴇss'

Overriding Operations with the order Argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``order`` argument references the dictionaries in ``trans_dicts``
directly, overriding the default translation:

::

    >>> print(demo.translate("KITSUNE EXPRESS", order=[2,1]))
    Ｋ⃞Ｉ⃞Ｔ⃞Ｓ⃞Ｕ⃞Ｎ⃞Ｅ⃞　Ｅ⃞Ｘ⃞Ｐ⃞Ｒ⃞Ｅ⃞Ｓ⃞Ｓ⃞
    # remember the contents of demo.trans_dicts.keys()

In this example, ``trans:ascii-aesthetic.0`` was applied to the input
text, followed by ``trans:wip-squares.2``.

Wrapping Up and Starting All Over
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start over, simply clear the translations from the TP with:

::

    >>> demo.clear_trans()

*PROTIP:* To exit the Python shell, press CTRL-D on an empty command
line.

Application Support and Previewing Your Text
============================================

Web Sites and Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~
Most web sites or apps provide their own fonts, so levels of support
will vary.

Page inspectors featured in most desktop web browsers may be used as
a previewing tool, by making transient edits to content currently
displayed in the browser:

Chrome
``````
1. Press ``CTRL + Shift + C``/``Cmd + Opt + C`` to bring up the
   `Inspect option <https://developer.chrome.com/docs/devtools/open/#elements>`_.
   The DevTools pane will also appear.

2. Select some text of the same type as what you are going to post or
   insert (such as a comment or caption) with the element picker. 
   Further navigation in `Elements <https://developer.chrome.com/docs/devtools/dom/>`_ in the DevTools may be needed to reach the text.

3. Once you find the text, simply double-click on it in Elements to
   edit it, then copy your own text over to preview it.

4. Close DevTools by clicking on the ``X`` on the far upper right hand
   side of the pane.

Firefox
```````
1. Press ``CTRL/Cmd + Shift + C`` to bring up the Element Picker. The
   Toolbox pane will also appear.

2. Select some text of the same type as what you are going to post or
   insert (such as a comment or caption) with the element picker. 
   Further navigation in the `inspector <https://developer.mozilla.org/en-US/docs/Tools/Page_Inspector>`_ may be needed to reach the text.

3. Once you find the text, simply double-click on it in the inspector to
   edit it, then copy your own text over.

4. Close the Toolbox by clicking on the ``X`` on the far upper right hand
   side of the pane, or by pressing ``CTRL + Shift + I``/``Cmd + Opt + I``

On devices with limited processing speed, inspectors may be rather
unresponsive on long and complex pages. Try testing on a shorter page
where possible.

Some apps or sites may restrict the use of fancy text.

For other browsers, consult the relevant documentation for instructions
on how to do this, where available.

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

