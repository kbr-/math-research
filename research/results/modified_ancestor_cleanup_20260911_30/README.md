# Local cleanup with specialized retained ancestors

Research cycle `modified_ancestor_cleanup_20260911_30`, 11 September 2026.
The full local corollary, proof, and limitations are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-modified-ancestor-cleanup).
This is a goal-relative application of the existing constant replay principle,
not a new global source simulation or a PHP refutation.

## Evidence and scope

`checks-01.jsonl` saves twelve deterministic exact cases over F2/F3/F5, accuracy
1/2, and parent input `P` or `1-P`. The inner block is `P_(x,y)`, the retained
parent is `Q=P_(a,z)`, and the goal assumptions are `x=y=0`. The proof derives
`T=x+zQ`, using both the inner companion `xP` and the parent companion `zQ`.

Zeroing only the inner coefficients maps `P` to one and retains the parent as
an ENS block on `(1,z)` or `(0,z)`. Its product remains nonconstant. Every source
line is replayed, every named goal is unchanged, and every selected variable is
absent afterward. Axiom-image records preserve original and image degrees; the
replay does not assume a newly low-degree image was active in the original proof.

The output contains:

- 24 complete PC traces, with corruption checks of each final line;
- twelve common models of both systems with all goal assumptions;
- twelve original-system models that violate a retained ancestor's image when
  the `x` goal is omitted;
- twelve models of the specialized retained system plus the other goal input
  that violate the removed companion's image `x`.

These controls are compatible with the conditional theorem: both countermodels
omit the essential `x` goal. The source systems are satisfiable, so the traces
are nonconstant target derivations, not refutations. The theorem's application
to a refutation preserves target one, but no such global instance was tested.
The source-trace degree is four at accuracy one and eleven at accuracy two;
the replayed degree is three and five respectively. No optimality is claimed.
Compilation and every check passed; no dependencies were installed.

## Encoding

The suite uses the existing exact C++ `pc_boundary.hpp` kernel. Polynomials are
lists `[coefficient, [[variable, exponent], ...]]`, with coefficients reduced
modulo the case prime and ordinary collected degrees. Zero has degree -1 in
this kernel. Variable IDs 0/1/2 denote `x/y/z`; the recorded coefficient ranges
are half-open `[first,end)` intervals. Original and replayed proof records each
have their own axiom array and line references.

The axiom-image ledger maps original axiom indices to retained indices; -1
marks a selected companion or selected field axiom. A selected companion is
replaced by its actual input witness, not accepted as an extra retained axiom.
For `original_model_violates_retained_image`, `tested_axiom` identifies the
original axiom whose image is violated. For
`missing_x_goal_in_specialized_system`, it identifies the original selected
companion whose image is one; `omitted_axiom` is a retained-system index.
Point assignments list every allocated variable, including removed coordinates
when displaying original-system models.

## Reproduction

Run from the repository root after ensuring the resource controls are active.
Choose a fresh output path; the checker refuses to overwrite a result.

```bash
./compute.sh start ancestor_reproduction
./compute.sh run ancestor_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_modified_ancestor_cleanup.cpp \
  -o research/tmp/check_modified_ancestor_cleanup
./compute.sh run ancestor_reproduction --threads 1 --timeout 120 -- \
  research/tmp/check_modified_ancestor_cleanup \
  --out research/results/NEW-modified-ancestors.jsonl
```

Run the executable only if the build succeeds. The suite is deterministic and
uses no floating-point field arithmetic. All new computation ran inside the
shared CPU and memory controls. Existing source and rendering suites were not
rerun; the new traces test the changed mathematical hypothesis directly.

## Provenance and timing

The claim-index search located the earlier learned-input/triangular replay
theorems and the old later-block dependency example. Their exact notebook
hypotheses were read before formulating this local corollary. No outside source
was imported and no new literature claim was made.

`provenance.json` hashes the complete output, new checker, and reused header.
`timing.html` is embedded in the notebook. The complete journal, commands, and
outputs are archived under
`research/provenance/session-records/modified_ancestor_cleanup_20260911_30/`.
Preparation includes finalizing and publishing the preceding checkpoint;
the mathematical and coding phases cover this bounded local step.
