# Limits of affine partition-statistic freezing

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-partition-freezing-limits)
contains the full necessary bound. This is an analytic cycle; no new numerical
run was performed.

Let an affine substitution map the original weak PHP base into degree-two PC
consequences of a residual F_N with N>=3. Suppose every statistic of one common
pigeon partition equals a field constant through degree-two PC as well. If the
largest original class has size s, then N<=2(s-p).

## Proof ledger

- N>=3 excludes any nonzero field constant from the residual C2 space.
- Column Booleanity, cross-class collisions, and PC reuse make the statistic
  constants zero/one and disjoint within each column.
- Class row sums imply k_t=m_t modulo p for each assigned-column count k_t.
  Some class is deficient, with k_t<=m_t-p; at least p-1 columns are unassigned.
- Forbidden cell images are affine degree-two consequences. Clearing them
  gives completed affine row relations on the k_t assigned columns.
- A product of k_t+1 completed row sums, followed by the collision expansion,
  yields a PC refutation through max(2,k_t+1). The residual lower bound forces
  k_t>=2 and N<=2k_t<=2(s-p).

The proof uses no same-row exclusions. Its sharp upper budget is a PC reuse
statement; no equally sharp flattened NS certificate is asserted. Literal
freezing and original-degree base-image proofs satisfy the hypotheses, but
the theorem also allows affine row images and statistic-constant equalities
proved through degree two.

## Reused evidence and scope

The n=3, p=3 all-but-one-column occupancy control has one class of four pigeons
and one assigned column. Its counts have the required congruence but its PC
degree-two refutation excludes such a hard residual projection. The complete
trace already lives in
`../occupancy_probe_feasibility_20260912_57/checks-01.jsonl`; it was not rerun.

The audited residual PC lower bound and the existing partition construction
provide the remaining comparison. For fixed p, the largest-class size scaling
is optimal within this affine freezing class; leading constants can still vary.
Larger budgets, nonlinear substitutions, and maps leaving some statistics
nonconstant are outside the theorem.

`provenance.json`, the timing fragment, and the archived session identify the
reused evidence and actual intervals. The initial capacity outline was included
in the preceding cycle; this interval also includes the preliminary idea of
varying copy assignments by column for the next cycle.
