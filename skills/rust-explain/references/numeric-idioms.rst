Numeric & Scientific Rust
=========================

A recognition guide for numeric Rust, plus the highest-value job: catching code
that compiles but is **quietly wrong**. The reader has a computational-science
background — correctness is the deliverable.

Ecosystem Idioms to Recognize
-----------------------------

- **ndarray** — N-dimensional arrays (the NumPy of Rust). ``Array2<f64>`` is an
  owned 2-D array; ``ArrayView2<f64>`` borrows one. Watch for ``.slice()`` with
  the ``s![..]`` indexing macro.
- **nalgebra** — linear algebra with *compile-time* dimensions: ``Matrix3<f64>``,
  ``Vector4<f64>``. Dimension mismatches become type errors.
- **faer** — high-performance dense linear algebra (decompositions, solves) built
  for speed; recognize ``faer::Mat``.
- **polars** — dataframes (the Rust pandas): a lazy ``LazyFrame`` query plan and
  an eager ``DataFrame``.
- **rayon** — data parallelism by changing ``.iter()`` to ``.par_iter()``. If you
  see ``par_iter`` / ``par_bridge`` / ``into_par_iter``, the loop runs on a
  thread pool.

FFI Reading: Rust Calling Native Libraries
------------------------------------------

A call into a C-ABI library (BLAS / LAPACK, a vendor kernel) looks like this:

.. code:: rust

   extern "C" {
       // declares a function provided by a C library, linked at build time
       fn cblas_ddot(n: i32, x: *const f64, incx: i32, y: *const f64, incy: i32) -> f64;
   }

   let dot = unsafe {                 // unsafe: the compiler cannot verify the C side
       cblas_ddot(n, x.as_ptr(), 1, y.as_ptr(), 1)
   };

Reading rules:

- ``extern "C"`` = "this uses the C ABI" (the calling convention for FFI).
- Raw pointers ``*const T`` / ``*mut T`` are the C-facing types; ``.as_ptr()``
  hands a slice's buffer to C.
- ``unsafe`` does **not** mean "wrong." It means *the compiler's guarantees stop
  here; a human asserts the contract*. Read every ``unsafe`` block as a claim to
  audit: are the pointers valid, the lengths right, the data still live?

Silent-Bug Radar (highest value)
--------------------------------

Rust's compiler eliminates whole bug classes — but only some. Anchor every review
on this split.

**The compiler catches** (do not re-audit these): use-after-free, double-free,
data races on shared memory, out-of-bounds via a runtime panic, null
dereferences, uninitialized reads.

**The compiler cannot catch** (audit these every time): *your math.* Code that
satisfies the borrow checker can still compute the wrong number.

Look hard at:

- **Stencil / index off-by-ones.** Loop bounds such as ``1..n-1`` versus
  ``1..n``, halo / ghost-cell handling, ``len()`` versus ``len()-1``. A bounds
  check turns a bad index into a *panic*, not a silently wrong result — but the
  wrong-but-in-range index is silent.
- **Aliasing assumptions in ``unsafe`` / FFI.** Code using ``get_unchecked``,
  ``split_at_mut``, or raw pointers promises "these do not overlap." If they can
  overlap, results are silently corrupt.
- **Parallel-reduction nondeterminism.** Floating-point ``+`` is not associative,
  so a ``rayon`` reduction can give a *different sum* per run depending on
  chunking — correct-looking, not reproducible. Flag when a ``par_iter().sum()``
  or a custom ``reduce`` feeds a result that must be bit-reproducible.
- **Integer / float casts.** ``as`` truncates or saturates silently
  (``300_i32 as u8`` is ``44``); ``usize`` index arithmetic can wrap.

When reviewing a generated kernel, state the split explicitly: "the compiler
guarantees memory and thread safety here; it does **not** guarantee the
arithmetic — check the indices, the reduction order, and the casts."
