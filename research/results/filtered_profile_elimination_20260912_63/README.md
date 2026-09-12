# Filtering chosen classes into a majority profile

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-filtered-profile-elimination)
contains the exact criterion, full matching and copy ledger, uniform-density
corollary, and a chosen-class family with empty intersection. This cycle is
analytic; no new numerical run was performed.

For selected classes C_j, let u be the minimum pigeon membership count, v the
minimum class size, and d the maximum pigeon membership count. Put
t=min(u,v-1). If 2t+d>2n, choose a maximum-degree pigeon, match away the q=n-d
columns missing it, and obtain a d-by-d profile with majority margin
epsilon=(t-q)/d-1/2.

The preceding majority theorem then applies with its exact conditions on K,
using d instead of n. The final residual has floor(d/K)-1 holes; the total
matching deletion is q+(d mod K). The rest of the size loss comes from copying.
Every original base image still fits its degree, selected extension images
vanish, and completed NS/PC degree and witness ceilings are preserved.

Uniform pigeon membership at least alpha*n and class size at least alpha*(n+1)
give a positive margin for sufficiently large n when alpha>2/3. The notebook
retains the finite correction and the explicit sufficient n bound. This density
threshold is sufficient for these estimates, not an optimality claim.

The direct-counting example chooses C_j as all pigeons except j and j+1.
Its intersection is empty, u=n-2, v=n-1, d=n-1, and the filtering margin is
(n-5)/(2(n-1)) for n>5. The later K conditions are still needed.

## Reused evidence

- The genuine matching restriction preserves the weak PHP base at original degree.
- The [majority theorem](https://kbr-.github.io/math-research/#majority-profile-elimination)
  supplies the remaining random-grouping, local-matching, and copy-map proof.
- The complete source layout evidence remains in
  `../majority_profile_layouts_20260912_62/checks-01.jsonl`; it was not rerun.
- The constant-collapse and design arguments are reused with the actual
  restricted statistics and original proof-degree ledger.

`provenance.json`, the timing fragment, and the archived session identify those
dependencies and measured work. The initial filtering outline was measured in
the preceding cycle; the present interval also contains the preliminary bounded-
exception observation proposed for the next cycle. Mathematical status remains
authoritative in the notebook.
