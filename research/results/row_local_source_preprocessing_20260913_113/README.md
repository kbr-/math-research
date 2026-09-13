# Canonical row-local source preprocessing

The full source pass and its alternative-order limitation are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-row-local-source-preprocessing).
This fixture checks the actual selector-linear input syntax and original
image/cofactor budgets, without instantiating a complete Frege or PHP proof.

## Reproduce

From the repository root, with the shared resource controls active:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_row_local_selector_compression.cpp \
  -o /tmp/math-row-local-selector-compression
./compute.sh run TURN --threads 1 -- \
  /tmp/math-row-local-selector-compression --out NEW_OUTPUT_PATH
~~~

The output must be new. Arithmetic is exact over F2, without randomness or
new dependencies.

## Complete evidence

The local subsystem has two functional four-label rows and their pairwise
column exclusions. It is satisfiable and is not the full five-pigeon PHP base.
Four blocks supported on individual rows are removed; a third-level parent
remains genuine. Inputs are affine in old bits, earlier products, and the
specified old compact equality.

<code>source-certificates.jsonl</code> preserves sixteen row states, all original
blocks, the global affine map, canonical selector values, and the retained
parent. Its thirty ordinary NS certificates comprise:

- Four local product comparisons, through original weights two and three.
- Eight local companion images and eight removed coefficient fields.
- Four decoded bit domains and one decoded compact equality.
- Two retained companion replacements through original degree seven,
  although their new canonical degree is three, and two retained fields.
- One companion multiplied by a raw removed coefficient squared, through
  the original total degree nine.

Two controls preserve a local model refuting an incorrect selector replacement
and a pair of row states exposing an earlier-selector dependency omitted by
literal-old-variable support alone.

Original bits have IDs 0..3. The decoded incidence variables have IDs 100..107,
in row-major order; original coefficient IDs remain unchanged. Polynomial
monomials are sorted variable lists retaining repetitions, with explicit
coefficients. No Boolean reduction is implicit in arithmetic. Every certificate
retains its complete target and all nonzero cofactor/axiom pairs.

Source and output hashes are in the provenance manifest. Timing and complete
command output are archived with the checkpoint. All compiled work used the
shared CPU and memory controls.
