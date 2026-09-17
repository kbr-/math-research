# Dependency and scope map: generic CNF bridge and proof-size criterion

Assignment: user follow-up to the two Formalize cycles of 17 September 2026 (option 2):
formalize the generic initial-value bridge so the generic subspace theorem can be stated for
refutation DAGs of arbitrary affine-clause CNFs. Statements and review by the main session;
proof-writing delegated to a subagent that must not alter statements.

## Source

Notebook entry of 16 September 2026, section "What is generic, and what still depends on the
source": for t initial clauses of width at most w, with ordinary clause polynomials
F_C = prod_i (1 - g_i) and Boolean equations in the old base, each initial value has a
certificate through w + 2h; an S-node refutation gives at most 3S + t slots and a refutation
through D = max(4h+1, w+2h).

## New indexed claims

- lem:generic-CNF-initial-value-bridge: `clauseFalsityPolynomial`, its evaluation
  characterization, and `registry_generic_initial` (value derivable through 2h+w).
- thm:generic-CNF-affine-DAG-subspace-criterion: `generic_CNF_PC_transfer` (3S+|J| slots,
  degree max(2h+w,4h+1)) and `generic_CNF_subspace_criterion`
  (dim U <= (3S+|J|) C(v-(h(k+1)+1)+k, k) for a separated degree-k subspace U).

## Reused verified results

`affine_literal_product_prefix`, registry degree lemmas, `affine_dag_registry`,
`registry_system_eq_ensFamily`, `registry_empty_value`, and the generic module
`generic_affine_subspace_exclusion`, `generic_proper_high_restriction_sum_le`.
Model proof: `registry_compact_initial` and `bitPHP_transfer_of_cover`.

## Boundary cases inspected

- Empty initial clause: polynomial 1, width 0, value derivable (registry value is 1).
- v < h(k+1)+1: no proper high blocks, binomial is C(k,k)=1, and the criterion reads
  dim U <= 3S+|J|, implied by dim U = 0 from the exclusion theorem. Consistent.
- J empty or S = 0 cannot have an empty final clause node; statements remain true vacuously.
- Initial clauses may be covered semantically (`clauseEntails`), as in the bit-PHP transfer.

## Outside the assignment

Short-proof control remark, any concrete new formula, and the preprint text.
