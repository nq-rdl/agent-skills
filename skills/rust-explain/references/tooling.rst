Rust Tooling as a Teaching Aid
==============================

Let the tools do the mechanical work, then explain *why* their output is right.
None of this needs a wrapper script — run the tools directly.

cargo clippy — the free senior reviewer
---------------------------------------

``cargo clippy`` is Rust's idiom linter. Let it find the non-idiomatic code, then
explain the reasoning instead of merely echoing the fix.

.. code:: text

   warning: the loop variable `i` is only used to index `v`
    --> idiom.rs:3:14
     |
   3 |     for i in 0..v.len() {
     |              ^^^^^^^^^^
     |
     = note: `#[warn(clippy::needless_range_loop)]` on by default
   help: consider using an iterator
     |
   3 -     for i in 0..v.len() {
   3 +     for <item> in &v {
     |

Teach it: "Clippy flags ``needless_range_loop`` (see the `clippy lint index
<https://rust-lang.github.io/rust-clippy/stable/index.html#needless_range_loop>`__).
Indexing ``v[i]`` re-checks bounds every iteration and hides intent; ``for x in
&v`` (equivalently ``v.iter()``) iterates the elements directly — clearer, and
it lets the optimizer elide the per-iteration bounds check in the common case
(bounds-check *elimination* is an LLVM optimization, not a language guarantee).
This is the gap between *works* and *fluent*." For the
idiomatic-rewrite mode, run clippy first, then walk each lint.

rustc errors as teachers
------------------------

Feed the **code and the real compiler message together**, then explain what the
rule protects against. Two canonical examples:

.. code:: text

   error[E0382]: borrow of moved value: `s`
    --> move.rs:4:20
     |
   3 |     let t = s;
     |             - value moved here
   4 |     println!("{}", s);
     |                    ^ value borrowed here after move

"``s`` was *moved* into ``t``, so ``s`` is no longer usable — not emptied,
**invalidated**: the value now lives in ``t`` and the compiler statically
forbids touching ``s``. It is preventing two owners of one heap buffer — which
would double-free at scope end. Fix: borrow (``&s``) if you only need to read,
or ``.clone()`` if you genuinely need a second copy."

.. code:: text

   error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable
    --> borrow.rs:4:5
     |
   3 |     let first = &v[0];
     |                  - immutable borrow occurs here
   4 |     v.push(4);
     |     ^^^^^^^^^ mutable borrow occurs here
   5 |     println!("{first}");
     |                ----- immutable borrow later used here

"``push`` can reallocate the vector, which would leave ``first`` dangling. The
borrow checker forbids a mutable borrow while a shared borrow is still live —
exactly the iterator-invalidation bug that C++ allows silently."

Use ``rustc --explain E0502`` for the long-form explanation of any error code.

rust-analyzer — navigation
--------------------------

The IDE language server. For *reading*, its highest-value features are:

- **Hover** — shows the inferred type of any expression. Rust infers most types,
  so hover makes the invisible visible.
- **Inlay hints** — inline type and parameter-name annotations.
- **Go to definition / find references** — trace where a trait impl or value
  actually comes from.

cargo doc & cargo expand
------------------------

- ``cargo doc --open`` builds and opens the API docs for the crate *and all its
  dependencies* — the fastest way to learn what an unfamiliar type offers.
- ``cargo expand`` shows what a macro expands to. When ``#[derive(...)]`` or a
  ``name!()`` macro is opaque, expand it to read the generated code (requires the
  ``cargo-expand`` tool).
