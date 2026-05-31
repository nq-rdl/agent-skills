Canonical Rust Documentation — Where to Verify
==============================================

The source of truth for everything this skill explains. Rust evolves by
**edition** (2015 → 2018 → 2021 → 2024) and the standard library grows every
six weeks, so a remembered fact can be one version stale — the bare
``extern "C"`` block, a cast rule, a lint name. When the reader's correctness
depends on a detail you are not certain of, **fetch the page below and read the
current wording** instead of asserting from memory. That is the difference
between teaching Rust and teaching last year's Rust.

This is the master list: keep full URLs here, and cite docs *by name and
section* at the point of use elsewhere (e.g. "Reference → Type cast
expressions") so this file stays the one place a link is maintained.

When to reach for these
-----------------------

``SKILL.md`` ("Verify against the source of truth") is the single statement of
*when* to fetch — in short: edition-sensitive syntax, a precise ``unsafe`` /
cast / aliasing contract, the exact meaning of an ``error[E####]``, or a
"guaranteed / safe" claim near the boundary of what the compiler promises. This
file is the *where*.

Use the ``stable`` channel (latest release) by default. If the code targets a
specific edition, the **Edition Guide** is what reconciles "this compiles for
them but looks wrong to me."

The core documentation set
--------------------------

- **The Rust Programming Language** ("the Book") —
  https://doc.rust-lang.org/stable/book/ — concept-first learning: ownership,
  borrowing, lifetimes, traits, smart pointers. Best for building a reader's
  intuition.
- **The Rust Reference** — https://doc.rust-lang.org/stable/reference/ — the
  authoritative description of syntax and semantics. The source of truth for
  "what *exactly* does this do" (cast rules, operator behavior, item forms).
- **Standard library API** — https://doc.rust-lang.org/stable/std/ — every
  ``std`` type and method, each ``unsafe`` method carrying a **Safety** section
  that states its contract. Use the search box at the top.
- **The Rustonomicon** — https://doc.rust-lang.org/stable/nomicon/ — the
  authority on ``unsafe`` Rust: raw pointers, aliasing, FFI, and the invariants
  an ``unsafe`` block must uphold. Reach here to audit ``unsafe`` / FFI.
- **The Edition Guide** — https://doc.rust-lang.org/stable/edition-guide/ — what
  changed between editions. First stop when syntax looks new or "wrong."
- **Error code index** — https://doc.rust-lang.org/stable/error_codes/ — the
  long-form explanation behind every ``error[E####]`` (the same text
  ``rustc --explain E0382`` prints).
- **Rust by Example** — https://doc.rust-lang.org/stable/rust-by-example/ —
  short, runnable, annotated examples.
- **The Cargo Book** — https://doc.rust-lang.org/stable/cargo/ — ``cargo``
  commands and the manifest format.
- **Clippy lint index** — https://rust-lang.github.io/rust-clippy/stable/ —
  what each Clippy lint means and *why* it fires (official, but hosted on
  ``rust-lang.github.io`` rather than ``doc.rust-lang.org``). Prefer the
  ``/stable/`` index over ``/master/``.

Pinpoint links for what this skill teaches
------------------------------------------

The deep links behind the trickier, drift-prone passages in the other
references:

- ``as`` cast semantics (int→int: narrowing truncates, widening
  sign/zero-extends, same-width reinterprets; float→int saturates, ``NaN`` → 0)
  — `Reference: Type cast expressions
  <https://doc.rust-lang.org/stable/reference/expressions/operator-expr.html#type-cast-expressions>`__.
- 2024-edition ``unsafe extern`` blocks (and per-item ``safe`` / ``unsafe``) —
  `Edition Guide: Unsafe extern blocks
  <https://doc.rust-lang.org/stable/edition-guide/rust-2024/unsafe-extern.html>`__,
  with the full grammar in `Reference: External blocks
  <https://doc.rust-lang.org/stable/reference/items/external-blocks.html>`__.
- Reference cycles and ``Weak<T>`` — `Book §15.6: Reference Cycles Can Leak
  Memory <https://doc.rust-lang.org/stable/book/ch15-06-reference-cycles.html>`__;
  `std::rc::Weak <https://doc.rust-lang.org/stable/std/rc/struct.Weak.html>`__ /
  `std::sync::Weak
  <https://doc.rust-lang.org/stable/std/sync/struct.Weak.html>`__.
- Aliasing and ``unsafe`` contracts — `Reference: Behavior considered undefined
  <https://doc.rust-lang.org/stable/reference/behavior-considered-undefined.html>`__
  is the authoritative list (e.g. two live ``&mut`` to overlapping memory is UB;
  raw pointers are exempt). Conceptual intro: `Nomicon: Aliasing
  <https://doc.rust-lang.org/stable/nomicon/aliasing.html>`__; FFI specifics:
  `Nomicon: FFI <https://doc.rust-lang.org/stable/nomicon/ffi.html>`__.
- Slice splitting / unchecked access contracts — `std::slice
  <https://doc.rust-lang.org/stable/std/primitive.slice.html>`__ (read the
  *Safety* note on ``get_unchecked`` and the guarantee on ``split_at_mut``).
- Borrow / move diagnostics — `error_codes: E0382
  <https://doc.rust-lang.org/stable/error_codes/E0382.html>`__ (use/borrow of a
  moved value), `E0502
  <https://doc.rust-lang.org/stable/error_codes/E0502.html>`__ (mutable +
  immutable borrow).
