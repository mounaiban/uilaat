UILAAT: Unicode Interlingual Aesthetic Appropriation Toolkit
------------------------------------------------------------

*A Mounaiban mini-project*

What's This?
============
UILAAT is a Unicode text processing library for working with decorative
Unicode text, artistic communication devices produced by appropriation
of graphemes between languages and superfluous use of non-word symbols and
combining characters.

UILAAT is yet another chapter of the history of an Internet tradition
that resulted from the encounter between an ambitious goal, to 
proliferate telegraphic typography support for every known (and unknown)
written language system (along with their typographic ornaments), and
the human fascination with the foreign and exotic.

*UILAAT is free software, licensed to you under the Terms of the GNU
General Public License, Version 3 or later. Please view the LICENSE file
for full terms and conditions.*

Unicode is a registered trademark of Unicode, Inc.

Rationale 
=========
*Also known as: why create yet another fancy Unicode text library?*

This project was inspired by contemporaries such as Lunicode.js and
LingoJam. However, it attempts a different approach towards the art
and science of Unicode mangling:

1. It aims for usability on large-scale processing operations.

2. A greater emphasis is placed on the linguistic aspects of
   Unicode decorations. The project aims to curate the relationships
   and similarities between grapheme substitutes.

3. Amusement value is not a priority 😞

Demo
====
*Also known as: what can we do with this?*

Well, actually not a lot for now...

Interactive Demo
****************
There is a demo module ``demos/demo.py`` that is designed for use in
an interactive shell. You can access it from the repo root (same
directory as the main module ``uilaat.py``) by running:

::

    python -im demos.demo

If your system is correctly set up, you should be inside the Python
REPL shell. There will be several demo text generators. Try ``aesthetic``
for a start:

::

    >>> aesthetic.print("quick brown fox '92-'98")
    ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ＇９２－＇９８  

There are several other generators in ``demos/demo.py``, have a look
inside to find out what they are...

The generators have two methods of interest: ``get_text()`` and ``print()``,
the former returns strings for use with other modules, while the latter
prints the text to the screen, well, to the terminal's best ability.

You can also chain the text generators to apply, to a certain extent,
decorations from multiple generators at once:

::

    >> witch_aesthetic = witch + aesthetic
    >> witch_aesthetic.print('trance coven')

Please be aware that doing this comes at a *huge* performance cost.
Processing a string of a hundred thousand characters in the example
generator above was found to take about half a minute, on a low-end 
laptop PC running Fedora. The processing time increases dramatically
for each extra generator chained, or as the size of the string
increases.

Using With Other Modules
************************
Alternatively, you can copy the main module into your project and
``import`` the module in your own code. Look inside the main module file
for more details on how things are currently being implemented. Can
you find a way of creating your own text generator?


TODO
====
There are perhaps only two issues with this library at the moment;
firstly, it's **slow** and secondly, it's *incomplete*.

Most Wanted Features
********************
* **Preset Translation Databases**: a ready-to-use repository of
  common substitutions would add to the out-of-box usefulness of
  this library.

* **Multi-Code Point Targets**: currently, only single code point
  characters can be targeted for substitution without the use of
  computationally-expensive regular expressions. Overcoming this
  limitation would make things a lot easier.

* **ＰＥＲＦＯＲＭＡＮＣＥ**: several bottlenecks are suspected in
  the handling of string-scoped functions in the main module,
  a reduction of function calls in the inner loops is currently
  believed to be able speed things up a bit.

