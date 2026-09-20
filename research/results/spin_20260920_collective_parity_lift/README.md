# Collective parity lifting and cancellation control

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-20-collective-parity-lift)
proves a common lift from projective-combination exactness through a stated
higher-degree range. The matching application requires minimum active-row
distance greater than d+s-1 and N>6(d+s-1); this is a sufficient, unoptimized
condition. Its MP application retains companion and cross-closure premises.

Reproduce the bounded finite controls with a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_collective_parity_lift.cpp -o /tmp/check_collective_parity_lift
./compute.sh --threads 1 /tmp/check_collective_parity_lift --out /tmp/collective-images.json
```

All calculations are exact over F2. There are three rows, sixteen labels, d=1
and s=2. Row bit masks encode the parity of the label bits selected by the mask.
The positive masks are [1,1,1] and [2,2,2]; the negative masks are [1,1,1] and
[3,1,1]. Nonzero binary combinations are enumerated in mask order 1,2,3.
Their row widths are respectively [3,3,3] and [3,3,1].

Source coordinates enumerate row pairs (0,1),(0,2),(1,2), followed by their
injective ordered label pairs lexicographically. Target coordinates enumerate
parity operator, retained row, label. Ordinary source marginal equations have
one fixed-coordinate sum for each row-pair endpoint and label. Target constraints
are its six zero sums, the two self contractions and the one cross contraction.
The stack for the actual joint image contains source marginals followed by both
contraction operators. These definitions reproduce every matrix; pivot indices
are zero based. The largest matrix is 192 x 720 bytes plus small copies.

The positive image and compatible target space both have dimension 87. The
negative dimensions are 73 and 87. The negative target is zero for the first
parity and e_0+e_4 on row zero for the second. The dual sums target indices 0
and 48; it kills every source column but gives one on that target. Complete
ranks, pivot lists, masks, target and dual are in `collective-images.json`.

`sources.json` records the standard projective cohomology fact checked in its
primary source, and distinguishes the historical graded Koszul branch that
was inspected but not used. No third-party full text was saved. Finite checks
support the scoped theorem, not its general proof or full source consistency.
