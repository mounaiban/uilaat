UILAAT JSON Database: Comment on UTF-16 Surrogates
--------------------------------------------------
This is an explanation for those new to the concept of surrogate
pairs used in JSON Unicode escape sequences.

Summary
~~~~~~~
This is one way surrogate pairs may be created in Python:

::
    
    v = ord(code_point)

    high_upper_bits = (((v & 0x1F0000)>>16) - 1) << 6
    high_lower_bits = ((v & 0xFC00)>>10 
    high surrogate = 0xD800 | high_upper_bits | high_lower_bits

    low_surrogate = (v & 0x3FF) | 0xDC00

This method uses only bitwise operations and one subtraction, making
it suitable for systems without fast division.

Background
~~~~~~~~~~
Unicode, as of version 13.0, is a *21-bit* character encoding system.
For usability on systems with 8-bit bytes, methods are specified for 
representing codes as 32, 16 and 8-bit values.

UTF-16 maps the 21-bit code space onto 16-bit values. All code points
with a value up to ``U+FFFF`` are addressable from a single value.
All other characters with a code point at ``U+10000`` and beyond must
be mapped with a two-code point sequence called a *surrogate pair*.

JSON, as specified in ECMA-404, uses only 16-bit escape sequences, which
are equivalent to UTF-16 code points, making surrogate pairs necessary
for higher code points.

Using surrogate pairs when constrained to 16-bit values simplifies
mitigation of data corruption and makes processing more efficient
compared to mode-switching mechanisms (i.e.  next ``n`` code points are
from code page ``x``), at the expense of storage space.

Due to constraints of compatibility, the arithmetic used in obtaining
the surrogate pairs may be rather contrived to the uninitiated, but
this can be overcome by breaking down the process into small steps.

Working Out Surrogate Pairs
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The method of obtaining surrogate pairs was specified in the *Unicode
Standard Core Specification*, section 3.9, D91. This method is intended
for code points ``U+10000`` to ``U+100000`` inclusive only.

1. Split the code point value (herein named ``v``) between high and
   low surrogates.  Work with the value as a binary number.

   * The lowest ten bits are encoded in the *low surrogate*

   * The other 11 bits are encoded in the *high surrogate*

2. Obtain the low surrogate by a bitwise and ``&`` with the lowest ten
   bits. Combine the bits with ``0xDC00`` with a bitwise or ``|``;
   The low surrogate is complete.

   * The lowest ten bits 0 to 9 may be masked out by ``v & 0x3FF``.

3. Prepare the high surrogate by splitting the high 11 bits into two
   further parts:

   * high upper for bits 16 to 20 inclusive of the original value
     (5 bits), obtain by masking out the bits with ``v & 0x1F0000``,
     and shifting sixteen bits to the right.

   * high lower for bits 10 to 15 inclusive of the original value
     (6 bits), obtain by masking out with ``v & 0xFC00`` and shifting
     ten bits to the right.

4. Obtain the high surrogate by subtracting the high upper by one,
   then recombining high upper, high lower and the high surrogate
   prefix ``0xD800``.

   * Recombine the components with a bitwise or, with shifts to the
     left to put the bits in the correct places:
     ``(((v & 0x1F0000)>>16 - 1) << 6) | ((v & 0xFC00)>>10) | 0xD800``

   * The subtraction is already done in the process above.

   * The high surrogate is complete.

Visualisation
~~~~~~~~~~~~~
Here is a diagram which should be easier to read than the one from
the Unicode Standard and ISO/IEC 10646.

All values shown are in binary. Lowest bit is bit 0 (for 2^0).

Original Value (zero-padded to 32-bit):

::

    0000 0000 000u uuuu vvvv vvxx xxxx xxxx

* ``0`` - always zero, as the highest code point is 0x10FFFF

* ``u`` - bits 16-20

* ``v`` - bits 10-15

* ``x`` - bits 0-9

High surrogate prefix (as 16-bit):

::

    1101 1000 0000 0000

Low surrogate prefix (16-bit):

::

    1101 1100 0000 0000

Prefixes and values shown together:

::

    1101 1000 0000 0000 -- high surrogate prefix
    0000 00ww wwvv vvvv -- w = u - 1, w has a max of 1111

    1101 10ww wwvv vvvv -- finished high surrogate
    
    1101 1100 0000 0000 -- low surrogate prefix
    0000 00xx xxxx xxxx -- low 10 bits

    1101 11xx xxxx xxxx -- finished low surrogate
    

See Also
========
StackOverflow. *Why using complex surrogate pairs?* Accessed 2020-12-21.
https://stackoverflow.com/questions/59836319/utf-16-encoding-why-using-complex-surrogate-pairs

Unicode Consortium. Unicode Standard Core Specification, Version 13.0.

