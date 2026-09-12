# Small Hall-deficiency normalizers

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-Hall-profile-normalizers)
contains the full common-zero graph criterion, affine map, NS certificates,
original-degree transfer, sparse family, and scope limitations.

## Exact checks

The checker uses the full weak base with four rows and three columns, without
same-row exclusions. Selected rows are 0 through r-1; their allowed zero columns
are 0 through r-2. Each other column has a designated weighted probe. Weights
on row i are `1 + i % (p-1)` and are nonzero in Fp.

| p | Selected rows r | Accuracy h | Witness degree | Product certificate ceiling W |
| -: | -: | -: | -: | -: |
| 2 | 3 | 3 | 1 | 6 |
| 3 | 2 | 2 | 2 | 6 |
| 5 | 1 | 2 | 1 | 2 |

The quadratic case uses weighted cell squares plus one column-collision term.
Extra inputs use an earlier retained coefficient variable, with a cell factor
in the quadratic case. The final case includes an unused coefficient row.

All 41 NS certificates passed, including local state identities, row relations,
collision finishes, complete product certificates, nine companions, and all
nonzero coefficient-field images. Twenty field images are accounted for in total;
the remainder are explicitly recorded literal zeros. The collision-finish
certificates use no Boolean or row generator. Source companion degrees are
retained separately from the smaller image certificate ceilings.

Each case has two controls:

- Omit the last selected row equation. A saved point satisfies the column
  axioms and remaining selected rows, while the product and extra companion
  both evaluate to one.
- Enlarge the allowed columns to r. A saved matching satisfies the column
  axioms and selected rows, and the collision-finish product survives proper
  normal form with value one.

These six points model only the explicitly stated partial bases. They are not
full PHP models or lower bounds against other normalization methods.

## Output and reproduction

`checks-01.jsonl` preserves every certificate's complete axiom/cofactor/target
polynomials, source inputs, coefficient rows, original companion degrees, and
controls. Residual/source incidence x_i_j has variable index 3*i+j, and the
earlier retained coefficient has index 12. Indices start at zero. Polynomials
use the existing coefficient/exponent-pair encoding; the empty list means zero.
The source ENS product is specified by its inputs, accuracy, and fresh coefficient
row indices, without expanding it into a larger symbolic source ring.

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_hall_profile_normalizers.cpp -o /tmp/check_hall_profile_normalizers
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_hall_profile_normalizers --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. Compilation and all checks passed.
`provenance.json`, the timing fragment, and the archived session preserve sources,
the full command output, and measured intervals.

The analytic sparse family in the notebook is not an additional numerical run.
The theorem is a sufficient criterion; it does not assert general impossibility
when a small Hall witness is absent. Current mathematical status remains in the
notebook rather than this evidence record.
