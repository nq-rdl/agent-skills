===========================
Stitch design.md Examples
===========================

This document provides worked examples of ``design.md`` snippets alongside their reStructuredText (RST) equivalents to demonstrate how design specifications translate between the formats.

Example 1: Basic Button Component
=================================

RST Equivalent
--------------

.. code-block:: rst

   Button Component
   ================

   A reusable button component used for primary actions.

   States
   ------

   * **Default:** Solid blue background, white text.
   * **Hover:** Darker blue background.
   * **Disabled:** Gray background, gray text, unclickable.

   Properties
   ----------

   * ``label`` (string): The text displayed on the button.
   * ``onClick`` (function): Callback triggered when clicked.

Stitch design.md Format
-----------------------

.. code-block:: markdown

   # Button Component

   A reusable button component used for primary actions.

   ## States

   * **Default:** Solid blue background, white text.
   * **Hover:** Darker blue background.
   * **Disabled:** Gray background, gray text, unclickable.

   ## Properties

   * `label` (string): The text displayed on the button.
   * `onClick` (function): Callback triggered when clicked.

Example 2: User Profile Card
============================

RST Equivalent
--------------

.. code-block:: rst

   User Profile Card
   =================

   Displays user information in a compact card format.

   Layout
   ------

   Use a flex container with a horizontal layout.

   1. **Avatar:** 48x48px circular image on the left.
   2. **Details:** Vertical flex container on the right.
      * **Name:** Bold, 16px font.
      * **Email:** Regular, 14px font, gray color.

Stitch design.md Format
-----------------------

.. code-block:: markdown

   # User Profile Card

   Displays user information in a compact card format.

   ## Layout

   Use a flex container with a horizontal layout.

   1. **Avatar:** 48x48px circular image on the left.
   2. **Details:** Vertical flex container on the right.
      * **Name:** Bold, 16px font.
      * **Email:** Regular, 14px font, gray color.
