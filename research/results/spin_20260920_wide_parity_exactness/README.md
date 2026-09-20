# Wide-parity contraction complex

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-20-wide-parity-exactness)
uses forced coded rows to establish characteristic-two exactness for a parity
on more than d active rows, under the explicit robust-label budget. The MP
application requires a supplied annihilator companion at its original cost.

Reproduce with a fresh output path:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_wide_parity_exactness.cpp -o /tmp/check_wide_parity_exactness
./compute.sh --threads 1 /tmp/check_wide_parity_exactness --out /tmp/parity-complex.json
```

The fixed board has three rows and sixteen labels; d=2. Each active predicate is
the low label bit. Rank checks use F2, with active rows {0,1,2} and {0,1}.
Source columns are all injective triples in lexicographic order. Target pairs
are ordered by their missing row (0,1,2), then lexicographically on the labels
of the remaining rows in increasing row order. Singletons are row-major.

The upper differential removes an active row and multiplies by the bit of its
label. The lower differential does the same on pairs, adding all contributions.
Ordinary source marginals enforce the K3 domain. Ordinary target marginals and
the lower differential together define the cycle space. All matrix and pivot
indices are zero based; arithmetic is exact. No randomness or dependencies.

For three active rows, image and kernel dimensions are 583. For two active rows,
they are 403 and 583. The latter output includes a four-cell top trade supported
on both active rows and a coordinate dual which is zero on the entire image but
one on that target. Every case checks the two deletion orders on all 3,360 source
triples and each retained row (10,080 checks). The F3 guard records coefficient 2
on a raw triple column; the notebook additionally gives a symbolic zero-marginal
trade on which the actual twice-contracted operator is nonzero over F3.

All computed ranks and complete pivot lists, control targets and the separating
coordinate are preserved in `parity-complex.json`. The largest matrix is
1440 x 3360 bytes plus small copies. The finite checks corroborate the proof and
its width/characteristic scope; they do not construct a complete proof source.
