# Leaf support under flattened source depth

11 September 2026. This cycle began an occurrence-scoped MP audit and first
corrected a prerequisite. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-leaf-support-repair)
records the invalid proper-descendant inference and the constructive support
repair. A stronger occurrence-scoped MP transfer was not completed in this cycle.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_leaf_support_levels.cpp -o research/tmp/check_leaf_support_levels
./compute.sh --threads 1 research/tmp/check_leaf_support_levels \
  --out research/results/occurrence_mp_replay_20260911_16/checks-REPRO.jsonl
```

Use a new output path. GCC 11.4.0, C++17, one thread, exact polynomial arithmetic
through the existing kernel. No dependencies were installed. Compilation and
all eight cases passed; no unrelated computation suite or rendering build ran.

## Evidence and encoding

`checks-01.jsonl` is 262,137 bytes. Each case records its complete formula DAG,
binary-bracket edges, source depth, structural ENS level, polynomial values,
and every OR block with its inputs, product, prefixes, and companions.

Node kinds are `x` (atom), `t` (TRUE), `n` (negation), and `o` (OR). An OR node
recursively flattens its OR children when computing source depth, inputs, and
ENS level, but retains the original binary edges separately. Negation raises
source depth and preserves ENS level. The fixtures have no MOD nodes; the
general lemma also handles the source MOD schemas analytically.

Polynomials use `[coefficient, [sorted repeated variable IDs]]`. Atom variables
are allocated first and fresh coefficient IDs afterward. Shared repeated nodes
in the negative fixture implement the internally coherent proper evaluations
used by the repaired lemma.

Six positive cases use p=2,3 and a bracketed OR of 3,8,24 negated atoms as X in
TRUE OR X. The root and its m-1 proper OR groups all have ENS level one, while
binary depth is m+1 and source depth stays two. The chosen unit witness uses
only the constant-one root input and no same-level companion; its degree is zero.

Two negative cases use C = NOT(NOT x OR x) and NOT(C OR (C OR C)). The root and
the proper grouping have ENS level two. Each root input is the older core
product P_(x,1-x), derived by summing its two companions at degree three and
level one. The same-level grouping is unused. The source negative-value
certificate has degree four and is also saved.

These are exact controls on the distinction between syntactic containment and
strict certificate support. They do not mechanically compile every axiom scheme.
The notebook supplies that general working construction: pure root-disjunct
variables are ignored for positive roots, and negative root inputs are proved
through their individual non-OR schematic children.

## Source and timing provenance

`provenance.json` hashes the checker, shared polynomial/ENS kernels, full output,
and the locally supplied BIKPRS PDF. The paper itself remains private and is
not included in this checkpoint. Targeted reading was the depth definition in
Section 1, Definition 6.8, and Lemmas 6.11–6.12. The OR depth clause explicitly
flattens arbitrary brackets; it does not authorize assigning one level per
binary bracket while preserving the original fixed-depth bound.

The correction affects the support justification of the earlier automatic
negative-leaf and all-axiom-root applications. Their conditional transfer
lemmas remain valid. The new special certificates through A_* restore the
asymptotic result with explicit revised image bounds. Earlier entries remain
unchanged, and the claim index links their correction.

`timing.html` is embedded in the notebook. Initial preparation includes the
publication-review rejection for the preceding checkpoint; the user renewed
approval with “Push!!!” and that checkpoint was then pushed. Reading includes
interpretation, and the mathematics phase includes the source-support repair.
Coding was marked for the short checker implementation, followed immediately
by mathematics while compilation ran. Full command evidence is archived under
`research/provenance/session-records/occurrence_mp_replay_20260911_16/`.
