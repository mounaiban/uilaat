UILAAT Architecture and Glossary (since 0.6)
--------------------------------------------
This is a summary of the software architecture used within the library,
and the technical terms used in its documentation.

Glossary
========

The following technical terms are used as follows:

* **Target**: A character, string or pattern to be replaced or removed.

* **Replacement**: A string or character to replace a *target*.

* **Mapping**: The relationship between a *target* and its *replacement*.

* **Translation**: A collection or set of one or more *mappings*.

* **Operation**: The process of changing text from one form to another
  designated final or intermediate form. A single operation may involve
  multiple *translations* or *preprocessing* stages.

* **Preprocessing**: The process of preparing text for a *translation*.
  This includes normalising characters into precomposed forms, stripping
  control characters and redacting confidential information.
  Preprocessing is optional.

* **Idempotence**: The property of an *operation* that, when performed
  two or more times, has an identical effect to performing it only once.

* **Database**: A consolidated store of information. In this context,
  a collection of information necessary to replicate *operations*.
  Databases may include translations and other metadata to guide the
  operations. Frequently abbreviated to **DB** in documentation.

* **Repository**: A software device that enables access to a *database*,
  in order to load operational information in a ready-to-use format.
  For example, JSONRepo objects are repositories that loads operational
  information from directories of JSON-formatted text files.

* **Text Processor**: A software device which acts on the front end to
  take input from the user, produce the desired text output and manage
  the process of achieving the desired output.

See Also
~~~~~~~~
* **Code Point**: defined in the *Unicode Standard Core Specification*,
  Chapter 2.4.

* **Character**: defined in the *Unicode Standard Core Specification*,
  Chapter 2.4.

Architecture
============

UILAAT's architecture comprises three main parts:

1. **Databases** that contain details on how to perform translations
   and operations

2. **Repositories** to load the information from the *Databases*

3. **Text Processors** to organise operations that produce output text

Here is an example of the stack used by the Demo Text Processor

+---------------------------+
| **Text Processor**        |
|                           |
| ``TextProcessor``         |
+---------------------------+
| **Repository**            |
|                           |
| ``JSONRepo``              |
+---------------------------+
| **Translation Database**  |
|                           |
| ``.json`` files           |
+---------------------------+

A potential future stack supporting more DB backends may permit the use
of another stack like:

+---------------------------+
| **Text Processor**        |
|                           |
| ``TextProcessor``         |
+---------------------------+
| **Repository**            |
|                           |
| ``SQLRepo``               |
+---------------------------+
| **Translation Database**  |
|                           |
| PostgreSQL Server DB      |
+---------------------------+


This design is intended to allow translation databases to be updated
or created without any changes to the codebase.

