# Small probes and the pebbling antichain obstruction

Full statements, proofs, and scope are in the
[12 September notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-small-probe-normalizers).
This extends the existing weighted-refutation and factor-packing mechanisms.
It does not establish a PHP elimination theorem or convert PC witnesses into NS.

## Reproduce

From the repository root, with the shared controls active and a new output path:

    ./compute.sh start small_probe_reproduction
    ./compute.sh run small_probe_reproduction --threads 1 --category local_processing --timeout 120 -- g++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_small_probe_normalizers.cpp -o /tmp/math-check-small-probe-normalizers
    ./compute.sh run small_probe_reproduction --threads 1 --timeout 120 -- /tmp/math-check-small-probe-normalizers --out research/results/small_probe_reproduction/checks.jsonl

The checker refuses to overwrite output. It uses exact modular C++ arithmetic,
no randomness or new dependency, and the existing ordinary-PC kernel.
The original protected compile and run both succeeded. Full command evidence
and timing are archived under
`research/provenance/session-records/small_probe_normalizers_20260912_36/`.
No historical mathematical suite, page build, rendering check, or stress test
was rerun merely for verification.

## Complete saved evidence

`checks-01.jsonl` contains nine complete PC traces and 26 exact NS certificates:

- One PC-three refutation with Boolean probe b and field probe f=x+y over F3,
  under the goal H=(1-b)(1-f^2)=0, and its weighted PC-six proof of H.
- Two source/replayed trace pairs for G=(b,x,y,w), using constant accuracy three
  and affine accuracy two. The target deliberately includes a selected field
  axiom; its affine image f^3-f is proved from old Boolean domains.
  Source/replay degrees are 9/6 and 7/6 respectively.
- A degree-six NS Booleanity certificate for H and a degree-three NS certificate
  for f^3-f. The latter degree is the certificate's own bound, independent of
  unrelated lines already present in the PC proof.
- Three PC-three pebbling refutations over F2, F3, F5 on the seven-vertex binary
  tree, and all eight input Booleanity certificates in each field.

All sixteen old Boolean points are saved for each positive realization, with
fourteen common source/retained models per case. The two explicit missing-goal
controls have b=x=y=0,w=1 and H=wH=1; they are models of the old Boolean base,
not of the omitted goal or the original selected companions.

For each pebbling field the output retains all eight unit violation vectors and
all 31 nonzero Boolean patterns on the four leaves plus the sink input: 24 unit
points and 93 cube points in total. It also records the two-source point showing
that one is not in the input span, after unit points force all coefficients to
one. The lower bound uses the analytic NOR-degree argument, not an unperformed
enumeration of normalizer matrices. The general control is a Boolean-domain
pebbling system, not PHP or an identified tuple from a PHP Frege proof.

## Format and verification

The first JSONL record describes the schema. Polynomials are arrays of
`[coefficient, [[variable, exponent], ...]]`, with coefficients reduced modulo p;
the empty array is zero. Source coefficient ranges and their exact polynomial
images are included in each normalizer-case record. Original variables in the
positive cases are b,x,y,w at indices 0,1,2,3; pebbling variables are 0 through 6.

A proof header supplies all axioms, the final line, the maximum degree, and the
number of following line records. Rules `a`, `l`, and `m` mean axiom introduction,
two-term field linear combination, and multiplication by one variable. Index -1
means zero and is not an extra axiom. Every line is recomputed and checked, and
corrupting the final line is rejected. NS records supply all axioms and cofactors
and verify both their sum and the maximum ordinary degree of each summand.

`provenance.json` hashes the checker, shared kernel, complete output, this README,
and claim index. The authoritative notebook is preserved by the Git checkpoint;
its final timing fragment is added after the provenance snapshot.

The cycle continued across compaction. Its earlier mathematics window includes
unseparated exploration and the compaction interval; restored source reading and
subsequent coding have explicit phase markers. No retrospective time split was
invented. The process assessment records the excessive exploration rather than
adding another framework checklist.
