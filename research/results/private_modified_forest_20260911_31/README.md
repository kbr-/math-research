# Global cleanup with private modified ancestors

Research cycle `private_modified_forest_20260911_31`, 11 September 2026.
The complete invariant, proof, endpoint qualification, and finite-check scope are
in the [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-private-modified-forest).

## Saved structural evidence

`checks-01.jsonl` contains sixteen deterministic cases: p=2/3, spine length
1/2/7/15, width 3/7, accuracy two. They are conditional constant-depth MP forests,
not primitive-Frege proofs of the arbitrary premise leaves. The source maximum
ENS level is three for every case. No PHP refutation was computed.

The full output saves physical nodes, leaf origins, parent edges, representatives,
the distinction between cuts and private ancestors, shared family IDs, ordinary
cuts, cleanup batches, copy-pair mappings, retained product images, and controls.
There are 1,400 cleanup cuts, including 800 nonmaximal cuts, 6,000 copy-pair
subtree-availability checks, and 200 final modified private ancestors. Each final
forest has exactly twice its spine length many modified ancestors.

The checker verifies the ancestor closure of the private set and descendant
closure of its shared complement. At every step it checks protected proper
representatives, ordinary interface freshness, batch antichains via the planned
eligible-ancestor selection, intact copy subtrees, witness support avoiding the
current cuts, and saturation of the stated sufficient eligibility rule. Roots
with previously modified proper subtrees are not automatically eligible.

The local PC replay algebra was verified in the preceding cycle's 24 full traces;
this suite tests the new global structural hypotheses without repeating that
expanded calculation. The notebook supplies the analytic degree induction.

## Expressions and controls

Product expressions are formal syntax trees, not expanded polynomials. Node
letters use the existing forest convention: `x` is an original proposition,
`n` negation, `m` a MOD gate, and `o` an OR approximation. An OR expression
identifies its coefficient family and lists the flattened non-OR child values;
its block inputs are their complements. `unit` is the value one of a removed
OR product. Negation and MOD retain their ordinary source evaluation formulas.
The stored original forest and family IDs define every specialized ENS input.

Each case also forces two same-syntax affected ancestors to share coefficients
prematurely, while their private inner copies still differ. The saved assignment
makes their values one and zero. Original proposition values and unspecified
coefficients are zero; listed coordinates of coefficient vector index zero are
one. The inherited field name `vector_zero_coordinates` denotes that vector
index, not the assigned value. These are coefficient-domain nonidentity points,
not models of all companion equations. The control rejects the simple canonical
quotient before input coherence, not every later or proof-dependent quotient.

The remaining modified ancestors in these particular fixtures are not claimed
essential. Their specialized tuples have a constant-one coordinate, making a
further constant product-zero assignment possible. Integrating that propagation
into the global schedule is the next bounded question.

## Reproduction

From the repository root with resource controls active, choose a fresh output
path. The checker refuses to replace existing output.

```bash
./compute.sh start modified_forest_reproduction
./compute.sh run modified_forest_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_private_modified_forest.cpp \
  -o research/tmp/check_private_modified_forest
./compute.sh run modified_forest_reproduction --threads 1 --timeout 120 -- \
  research/tmp/check_private_modified_forest \
  --out research/results/NEW-private-modified-forest.jsonl
```

Run the executable only after its build succeeds. The new suite reuses
`check_goal_input_cleanup.cpp`, which in turn reuses the existing physical
occurrence kernel. Only a compile-time guard around that cleanup checker's CLI
was added; its ordinary executable behavior is unchanged. Compilation and every
check passed. No dependencies, historical test reruns, or rendering checks were
needed.

## Provenance and timing

The proof extends the notebook's existing local specialized-ancestor replay,
inherited live-forest construction, and source copy/degree bounds. The current
source record was already restored; no outside reference was imported.

`provenance.json` hashes the complete output and all three source dependencies.
`timing.html` is embedded in the notebook. Full timing and command evidence is
archived in `research/provenance/session-records/private_modified_forest_20260911_31/`.
Preparation includes the preceding checkpoint's final archive, commit, audit,
and authorized publication. Mathematical and coding windows cover this cycle's
invariant, implementation, focused review, and proof writing.
