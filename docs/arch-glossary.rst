UILAAT Architecture and Glossary (0.5)
--------------------------------------
This is a summary of the software architecture used within the library,
and the technical terms used in its documentation.

Glossary
========
The following technical terms are used as follows:

* **Translation**: A single process of substituting text, or more
  precisely, code points, for another according to a specification.

* **Preprocessing**: The process of preparing text for a *translation*.
  This may include normalising characters into precomposed forms,
  stripping control characters and redacting confidential information.

* **Operation**: The process of changing text from one form to another
  designated final or intermediate form. A single operation may involve
  multiple *translation* or *preprocessing* stages.

* **Target**: A particular string to be replaced or removed during
  a *translation*, *preprocessing* or *operation*.

* **Replacement**: Strings to replace a *target*.

* **Mapping**: The relationship between a *target* and its *replacement*.

* **Idempotence**: The property of an *operation* or *translation* that,
  when performed two or more times, has an identical effect to performing
  it only once.

* **Database**: A consolidated store of information. In the context this
  software, databases contain information on how to perform *operations*.
  Frequently abbreviated to **DB** in documentation.

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

Architecture
============
UILAAT's architecture comprises three main parts:

1. **Translation Databases** that contain details on how to perform
   translations and operations

2. **Repositories** to load the information from the Databases

3. **Text Processors** organise operations that produce output text

This design is intended to allow translation databases to be updated
or created without any changes to the codebase.

