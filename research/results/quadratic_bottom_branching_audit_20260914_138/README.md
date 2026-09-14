# General binary rank-two bottoms and affine branches

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-quadratic-bottom-affine-branches)
gives the working source theorem. Complete rank-two affine bottom blocks
normalize to quadratic products without degree loss. A maximal collection
of r jointly independent factor pairs supplies 2r linear coordinates whose
Boolean branches make all parent inputs affine.

The complete coefficient interpolation creates at most 2^t affine cores per
parent and transfers degree D to (t+1)D, at any common accuracy h >= 1.
Polylogarithmic t and polynomial original inventory therefore reach the
quasipolynomial-inventory affine exclusion. Large independent-pair counts,
mixed families with other quadratic blocks, and later nonlinear inputs remain
open. This is a binary result; no odd-prime affine-probe extension is inferred.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_quadratic_affine_branches.cpp -o /tmp/math-quadratic-branches
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-quadratic-branches --out NEW_OUTPUT_PATH
~~~

The checker refuses an existing output path. No new dependency is needed.

## Exact scope and evidence

The old variables are a,b,c,d,e. The bottom values are ab,
(a+c)(b+c), (a+d)(b+d), and (a+e)(b+e). Two overlapping parent lists are
(0,1,2) and (1,2,3), with coordinate pairs (a,b) and (a+c,b+c).
Each parent has full factor-span rank four, a maximal independent-pair
collection of size one, and no common affine polynomial factor.

- Accuracy one: the actual complete two-level source, 33 original axiom
  images, and 59 NS certificates.
- Accuracy two: the quadratic intermediate source, 23 axiom images,
  and 49 NS certificates.
- Each fixture retains 24 branch-input comparisons and two complete
  parent-product comparisons, with formal new coefficients.
- Every old Boolean assignment gives a complete model: 64 in total.
  Two missing-companion models and two incorrect fixed-branch maps fail
  exactly where intended.
- Adding the product cd gives quotient rank two modulo (a,b), with a
  nonzero quadratic branch input. This detects insufficient coordinates,
  without excluding a different coordinate set.

All 108 certificates reconstruct exactly, with every ordinary generator
multiple within the stated degree. Every original coefficient receives one
image and all its Boolean equations are checked. The complete source systems,
maps, retained axioms, targets, cofactors, and assignments are stored in
`NS-affine-branches.jsonl`. Polynomial encoding is
`[coefficient,[variable IDs with repetitions]]`.

The final compilation is clean; two indentation warnings in the initial
compilation were corrected before the mathematical run. All mathematical
checks passed. These are local Boolean-domain controls, not finite PHP
instances satisfying the asymptotic lower-bound hypotheses.

`check-metadata.json` records focused output and new-link checks.
`provenance.json` hashes the sources and evidence. The complete command
journal and output are archived under the matching session name in
`research/provenance/session-records/`.
