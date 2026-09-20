# Hierarchical parity span: row puncturing versus a hole subcube

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-20-row-localization-test)
proves the structural obstruction and the canonical joint restriction, then
gives a symbolic original-cost whole-block zero witness for this input family.
It does not assert a general or simultaneous source restriction theorem.

Reproduce with fresh output paths:

```bash
./compute.sh --threads 1 g++ -O2 -std=c++17 -Wall -Wextra -Werror \
  research/tools/check_hierarchical_span.cpp -o /tmp/check_hierarchical_span
./compute.sh --threads 1 /tmp/check_hierarchical_span --out /tmp/hierarchical-restrictions.json
./compute.sh --threads 1 /tmp/check_hierarchical_span \
  --out /tmp/canonical-subcube-pin.json --canonical-only
```

At tree height h, leaves are integers 0 through 2^h-1 in binary-tree order.
A node at depth j uses the old label bit h-1-j on every descendant row. Node
supports are disjoint as row/bit coordinate sets, making their nonzero projections
independent. Row-local projected generators have exactly one surviving leaf;
quotient generators have at least two. Their minimum row weight is the minimum
nonlocal support size, since different generators cannot cancel coordinate cells.

The default run checks all 65,536 row subsets at height four and preserves every
record as `[row_mask, surviving_rows, local_dimension, quotient_dimension,
quotient_min_row_distance_or_zero]`. Distance zero means the quotient is zero.
For all 65,519 subsets with at least two leaves, dimension is at least k-1 and
distance exactly two. This is a complete finite support census, not an independent
numerical proof of the general theorem.

The default output also preserves an initial height-five fixture: five leaf rows
survive, four low-bit holes remain, coefficient rank is ten and all nonconstant
generators are row-local. Its arbitrary pinning produced fourteen constant-one
generators. It is only a structural projection control, not evidence of a hard
surviving common-zero system.

The canonical-only run removes that shortcut. It keeps leaf rows 0,8,16,24 and
the extra row 32, and holes 0,1,2,3. Every removed leaf row i is assigned its
five-bit reversal, bijectively exhausting holes outside the subcube. The output
records all 28 pins and every restricted affine generator. Coefficient bit
`2*surviving_row_position + low_bit` refers to that remaining row/bit coordinate.
Generator records are `[depth, node_index, coefficient_mask, affine_constant]`.
The rank is eight, local dimensions are [2,2,2,2,0], and there is no nonlocal or
constant-one generator. Each original node parity vanishes under the complete
bit-reversal assignment; this is checked explicitly.

The symbolic degree-(t+1) old-functional refutation with the resulting local
input equations, and its whole-value cost max(w+t+1,rho+t), are proved in full
in the notebook. The checker does not certify an arbitrary source or infer
fresh-coefficient elimination from that whole-value witness.

This cycle includes the user's reporting correction. Its numerical-prospect
withdrawal was checkpointed separately; that administrative interval is marked
as overhead here and separately instrumented in its own entry. The correction
supersedes the unsupported prospect percentages; no new ones are used.
