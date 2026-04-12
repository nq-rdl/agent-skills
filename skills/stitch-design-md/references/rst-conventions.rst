=================================
RST Conventions for this Skill
=================================

The reference documents in this skill use standard Sphinx reStructuredText (RST) conventions. This file outlines the basic syntax used to ensure consistency.

Headings
========

Headings are created by underlining (and optionally overlining) the title text.

.. code-block:: rst

   =============
   Document Title
   =============

   Section Level 1
   ===============

   Subsection Level 2
   ------------------

   Sub-subsection Level 3
   ^^^^^^^^^^^^^^^^^^^^^^

Inline Markup
=============

*   Emphasis (italics): ``*text*``
*   Strong emphasis (bold): ``**text**``
*   Inline code/literals: ````text````

Lists
=====

Bullet Lists
------------

Use asterisks (``*``), plus signs (``+``), or hyphens (``-``) for bullet lists.

.. code-block:: rst

   * First item
   * Second item
     * Nested item
   * Third item

Numbered Lists
--------------

Use numbers followed by periods, or hash symbols for auto-numbering.

.. code-block:: rst

   1. First step
   2. Second step

   #. Auto-numbered step 1
   #. Auto-numbered step 2

Code Blocks
===========

Use the ``.. code-block:: <language>`` directive for syntax highlighting.

.. code-block:: rst

   .. code-block:: markdown

      # This is markdown code
      * item 1
      * item 2

Admonitions
===========

Use admonitions like ``note``, ``warning``, or ``tip`` to call out important information.

.. code-block:: rst

   .. note::
      This is an important note regarding the format.
