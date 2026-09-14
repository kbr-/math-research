# Accuracy-one affine exclusion and shared-bit source transfer

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-unit-accuracy-shared-bit-source)
contains the complete working argument. For each fixed prime, one affine ENS
level excludes polylog-degree PC refutations at accuracy one, including
quasipolynomial inventory. A complete dense two-level family whose bottom
tuples share one old Boolean bit maps to that endpoint without degree loss.

This is a refutation theorem. General rank-two bottoms, later nonlinear
inputs, and the earlier old-target/joint-clamping conclusions at the new
accuracy remain outside its scope. The publication draft is unchanged.

## Reproduce

From the repository root, with an active timing session TURN and the resource
controls running:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_constant_accuracy_affine.cpp -o /tmp/math-unit-affine
./compute.sh run TURN --threads 1 -- \
  /tmp/math-unit-affine --unit-accuracy --out NEW_AFFINE_OUTPUT

./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_shared_bit_source.cpp -o /tmp/math-unit-shared-bit
./compute.sh run TURN --threads 1 -- \
  /tmp/math-unit-shared-bit --unit-accuracy --out NEW_SOURCE_OUTPUT
~~~

Use new output paths; the checkers refuse overwrites. No installation is needed.
Omitting `--unit-accuracy` reproduces the previous checker mode.

## Evidence

Polynomials are lists of `[coefficient,[variable IDs with repetitions]]`.
The files retain original systems, simultaneous coefficient maps, targets,
ordinary NS cofactors, degree ceilings, and complete model assignments.
The shared verifier reconstructs every target and checks each generator multiple.

- `NS-unit-affine.jsonl`: 100 weighted source-image certificates and three
  Boolean-reduction certificates; 512 conditional models; two unweighted
  high-companion controls; an F3 coefficient-domain control; five retained
  exact dimension fixtures. The new multiplier is the kernel raised to p-1.
  A separate four-bit-row example detects growth of its Booleanized row degree.
- `NS-unit-shared-bit.jsonl`: 60 certificates, covering all 26 original axiom
  images per field, two exact parent comparisons and two parent Booleanity
  certificates per field. There are 32 ordinary models, two missing-companion
  countermodels, and one F3 non-Boolean coefficient model. Two incorrect
  ungated-parent controls and two incorrect constant bottom-map controls
  preserve the formula and coefficient boundaries.

All mathematical checks and clean compilations passed. These local fixtures
do not instantiate the theorem's asymptotic PHP board conditions.
The default affine output is byte-identical to cycle 136; the default source
output is byte-identical to cycle 129. The first source comparison failed
because its archived path was misspelled, after both mathematical runs had
passed; the corrected comparison passed without rerunning the checkers.

`check-metadata.json` records focused output/anchor checks; `provenance.json`
records source and evidence hashes. The timing journal and full command
outputs are archived under the matching session name in
`research/provenance/session-records/`.
