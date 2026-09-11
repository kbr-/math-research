# Inherited consequent families and positive zero replay

11 September 2026. The [full notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-inherited-consequents)
proves the live-forest invariant, positive-boundary zero replay, and inherited
PC transfer with mode-dependent degree charges. Essential argument and MOD
families remain an open obligation.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp research/results/inherited_consequent_20260911_18
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_inherited_consequent.cpp -o research/tmp/check_inherited_consequent
./compute.sh --threads 1 research/tmp/check_inherited_consequent \
  --out research/results/inherited_consequent_20260911_18/checks-REPRO.jsonl
```

Use a new output path. The accepted run used GCC 11.4.0, C++17, one thread,
and the existing exact `pc_boundary.hpp` engine without changes. No packages
were installed. `checks-01.jsonl` preserves all 348,893 bytes of output.

## Structural evidence

There are 25 cases: one two-step projection spine with simple positive
antecedents, and 24 mixed cases of lengths 1,2,7,31 with six terminal shapes.
They are conditional MP syntax spines; long initial implications are not
claimed to be individual axioms of the fixed Frege basis. The structural
statement does not depend on the existence or degree of a leaf certificate.

Each record saves the complete physical forest, node edges, shared original
variable IDs, origin leaf, initial leaf roots, every inherited representative,
removed interfaces, surviving block IDs, source depth, and ENS level. OR
nodes are binary but depth is computed from their flattened non-OR frontier.
Node kinds are x (atom), t (TRUE), n (negation), o (OR), m (one-input MOD_0).
MOD and negation raise source depth and preserve structural ENS level; OR
raises the maximum frontier level by one. Every syntax occurrence has its own
node, even if its formula is repeated. A coefficient family is identified by
its OR node; this part of the checker does not expand polynomial companions.

At every step the selected interfaces have no live OR ancestor. The inherited
representative retains every OR node except its own signed boundary. Every
surviving OR subtree is also intact. Restoring the original implication root
breaks the ancestor test whenever an interface is selected. The simple
two-step case asserts seven leaf-only OR blocks versus eleven with fresh
internal-line families and no surviving blocks after the stated schedule.

## Exact PC evidence

Four cases over F2 and F3 exercise both direct and negation-wrapped positive
boundaries, saving eight full traces. Variables 0,1 are Boolean x,y and 2,3
are the accuracy-one block coefficients. The old base contains 1-x and is
satisfiable at (x,y)=(1,0). The block has inputs (x,y).

Each raw degree-three proof uses a live companion to derive
P = xP + (1-x)P. It then derives one using either the input assumptions x,y
and prefix telescoping, or the extra assumption 1-P. Zeroing coefficients
maps companions to the supplied conclusion inputs and gives a degree-two
trace. Every operation and final target is checked; all removed coefficients
are absent and corruption of every final line is rejected. The nonzero
companion image x is recorded as a control against dropping its justification.
The old-domain system itself is satisfiable; the refutation requires the
additional assumptions stated in the lemma.

Polynomial terms use the boundary engine encoding
`[coefficient, [[variable_id, exponent], ...]]`. PC rules are a (axiom),
l (linear combination), m (variable multiplication); line -1 denotes zero.
These tests do not mechanically compile the full Frege simulation.

## Provenance and timing

`provenance.json` hashes the checker, shared engine, and complete output.
The source inputs are the preceding notebook's occurrence-copy and strict-leaf
proofs, whose entries preserve their source provenance; no new paper was read
or downloaded for this extension.

Compilation and all mathematical checks passed. The first execution could not
open its output because the new result directory did not yet exist; it produced
no output file. After creating the directory, the unchanged checker passed.
This is the single failed command in the timing record, not a failed proof test.
No historical suite or rendering build was repeated.

`timing.html` is embedded in the notebook. Initial preparation includes the
preceding checkpoint's archival, source-history audit, and authorized push.
Mathematics includes the inheritance proof and notebook drafting; coding was
marked separately for the new checker. Full evidence is archived under
`research/provenance/session-records/inherited_consequent_20260911_18/`.
