# Affine column-state normalizers

This checkpoint supplies exact evidence for the notebook entry
[Remove arbitrary polynomial column tuples with affine state selectors](https://kbr-.github.io/math-research/#entry-2026-09-12-column-state-normalizers).
The universal proofs, degree budgets, and limitations are in that entry.

## Reproduce

From the repository root, with active resource controls:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_column_state_normalizers.cpp -o /tmp/check_column_state_normalizers
./compute.sh run CHECK --threads 1 --category computation --timeout 60 -- \
  /tmp/check_column_state_normalizers --out PATH-TO-NEW-OUTPUT.jsonl
```

The saved run used session `column_state_normalizers_20260912_46` and
`checks-01.jsonl` in this directory. The checker refuses to replace existing output.
It reuses the sparse exact kernel and certificate helpers from earlier tools;
their earlier test suites are not executed. No random choices are used.

## Instances and output

For each prime 2, 3, 5 and column size 3, 5, four tuples are checked at accuracy one.
Variables `Y0,...,Y(m-1)` describe one column. Type C also has an outside Boolean `Z`.
Fresh coefficient variables follow these old variables in the exponent arrays.

- A: `(Y0 + 2 Y1, Y1 + Y2)`, including non-Boolean input values in odd characteristic.
- B: `(Y0^2 + Y1 Y2, (1-Y0)Y2, Y1^3-Y1)`, with nonlinear inputs.
- C: `(1-Y0, 1-Y1, Z)`, normalizing from the inconsistent first two inputs alone.
- D: `(Y0^2-Y0, Y0 Y1, Y1^3-Y1)`, whose profiles all vanish, giving selector one.

The local base consists of old Boolean equations and every pairwise column collision.
There are no PHP row equations. These are consistent systems, with every permitted
column state checked and both Z values checked in type C.

`checks-01.jsonl` preserves state choices and inverses, coefficient polynomials,
original and mapped products, all NS axioms/cofactors/targets, common models, and
omitted-collision controls. Polynomials use the sparse coefficient/exponent-array
format emitted by `pc_boundary.hpp`. Each NS certificate is checked by exact
polynomial addition/multiplication and its maximum original-axiom-multiple degree.

Results: 24 cases; 210 NS certificates (66 companion images, 66 field images,
24 selector Booleanity identities, six inconsistent-subset identities, and
48 original/mapped consequences); 150 common models; six omitted-collision controls.
There are 36 nonzero field images and four non-Boolean input state values.

The original nonzero consequence is the block product's Booleanity polynomial plus
`Y2^2-Y2` and a coefficient field equation. Its mapped target is also required to be
nonzero. In type C, omitting the collision `Y0 Y1` permits a model of every remaining
local base equation with `ZH=1`, witnessing the need for that collision.

These finite checks do not test full PHP satisfiability, prove general coverage,
or numerically verify the universal grouped-column and row-coordinate arguments.
Compilation and all checks succeeded. `provenance.json` records the session and
path/size/hash metadata; the timing report and archived session preserve execution.
