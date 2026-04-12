---
name: stitch-design-md
description: >-
  Work with Google Stitch's design.md format. Use this skill when generating UI,
  designing with Stitch, or writing design.md specs. Teaches how to structure the
  spec and uses reStructuredText (RST) for detailed references.
license: MIT
metadata:
  repo: https://github.com/nq-rdl/agent-skills
---

# stitch-design-md — Google Stitch design.md format

Use this skill when tasked with creating, editing, or understanding Google Stitch `design.md` files. This format is used by Stitch for AI-assisted UI design generation.

## How to use this skill

This skill provides references in reStructuredText (RST) format detailing the `design.md` spec and examples.

Review the following references when generating a `design.md` file:

- Read `references/format-overview.rst` for the structural requirements of a `design.md` file.
- Read `references/examples.rst` for concrete examples of `design.md` files alongside their RST explanations.
- Read `references/rst-conventions.rst` to understand the RST conventions used in these reference documents.

## Generating design.md files

When writing a `design.md` file, you must:

1. Follow the exact Markdown structure expected by Stitch (as detailed in `references/format-overview.rst`).
2. Use the provided examples (`references/examples.rst`) to guide your content organization.
3. Keep the output strictly as Markdown, even though the references in this skill are written in RST.
