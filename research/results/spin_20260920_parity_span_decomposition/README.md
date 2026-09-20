# Hybrid row-local and global parity correction

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-20-parity-span-decomposition)
proves a relative coded-kernel lift and uses it to combine local row targets
with a collectively wide global family. It states the mixed compatibility
conditions explicitly and gives a span that a basis change alone cannot put
into the proved form. Restriction and full-source consistency remain open.

Reproduce the bounded binary check with a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_hybrid_parity_lift.cpp -o /tmp/check_hybrid_parity_lift
./compute.sh --threads 1 /tmp/check_hybrid_parity_lift --out /tmp/hybrid-image.json
```

The board has three rows, sixteen labels and d=1. Operators 0,1,2 condition on
the first bit of rows 0,1,2, respectively. Operator 3 is the sum of the second
bits of all three rows. Thus each local dimension is one and the global family
has relative distance three. The sufficient label bound is 16>2*(1+1-1)*(1+3).

Source coordinates are injective label pairs on row pairs (0,1),(0,2),(1,2),
ordered lexicographically. Target coordinates are ordered by operator, retained
row and label. Source marginal constraints are fixed-label sums at each pair
endpoint. Target constraints include all ordinary zero sums; zero output of
local operator i on its own row i; every self contraction; every cross contraction.
The weakened comparison drops only local/global cross contractions.

All ranks are exact over F2. The actual image and full compatible space have
dimension 128; omitting the mixed constraints gives dimension 131. The saved
control puts e_0+e_1 in the global target on row zero and zero in every local
target. It meets all weakened conditions and violates exactly one mixed equation.
All rank and pivot outputs, operator bit masks and the complete sparse control
are in `hybrid-image.json`. The largest matrix is 288 x 720 bytes plus copies.
No randomness, floating-point arithmetic or added dependencies are used.

The structural equality-difference example and its restriction behavior are
proved symbolically in the notebook; no finite sample is being used to justify
a general restriction theorem.
