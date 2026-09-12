# Packing with nonsharp Booleanity witnesses

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-nonsharp-Boolean-packing)
contains the complete ledgers, ordering argument, common-ceiling induction, and
application to the new PHP endpoint. This was an analytic cycle with no new
numerical suite.

## Budget map

For a degree-adapted basis b_j of degrees d_j, set W=sum(d_j), Q=product(1-b_j).
An input g_i of degree a_i has original companion degree e_i=a_i+h(delta+1).
The existing affine-bin realization ensures W<=h(delta+1).

- With NS Booleanity witnesses through s_j, the supplied image budget is
  `N_i=max(s_j+W-d_j : c_ij!=0)`. Same-degree NS transfer needs `N_i<=e_i`.
- With PC Booleanity witnesses through c_j, the image budget is
  `max(c_j,W+d_j : c_ij!=0)<=max(C,e_i)`, where C=max(c_j).
  This gives PC transfer through max(D,C), by reusing completed polynomials.
- Write kappa_j=s_j-2d_j. The displayed product-Booleanity NS certificate costs
  `2W+max(kappa_j-sum(d_k before j))`. Ordering by nondecreasing kappa minimizes
  this bound. It does not establish optimality among all NS certificates.

If all current inputs have degree <=L and earlier PC Booleanity proofs through
C>=2L, stable input reduction and the level-ordered packing/sharing pass preserve
that common witness ceiling. The new endpoint supplies C=2L and D=(c+2d)L>=C,
so its degree, level count, and polynomial family count remain unchanged.
Retained inputs are normal forms in the current stable domain/column ideal.
This does not bound the surviving wide family or automatically give NS witnesses.

## Exact image-budget example

Use the preceding full-PHP reduced-product gap with lower accuracy a and matching
degree t. An upper single-input block on b=1-V, of degree a+t and accuracy k,
has original companion degree `(a+t)+k(a+t+1)`.
The coefficient assignment (1,0,...,0) yields the Booleanity target up to sign.
Its exact NS/PC image costs come from the preceding theorem.

For a=t=2 and n>=19 over any odd field:

| Upper accuracy | Original companion degree | PC image degree | NS image degree |
| -: | -: | -: | -: |
| 1 | 9 | 8 | 10 |
| 2 | 14 | 8 | 10 |

These compare the specified image with its original axiom budget. They are not
lower bounds against every possible normalizer. If k=a in general, the original
upper companion's NS slack for this assignment is exactly a^2.

## Dependencies and evidence

- Existing notebook anchors `affine-basis-image-ledger` and `wide-Boolean-ideal-cover`
  give the exact companion and coefficient assignments refined here.
- `virtual-php-normal-form` supplies strictly earlier sharp input Booleanity before
  the new processing, hence the initial uniform PC ceiling 2L.
- `input-reduction-transfer` supplies original-degree old-axiom replacement.
- `research/results/ens_input_reduction_20260912_48/checks-01.jsonl` preserves the
  concrete NS upper certificates, full PC traces, and generic exact-gap controls.
- `research/results/php_reduced_booleanity_gap_20260912_49/README.md` maps the
  full-PHP lift and its precise additional-family exclusions.

No historical suite was rerun and no timing was assigned to an unperformed
computation. `provenance.json`, `timing.html`, and the archived session preserve
the consulted evidence and actual proof/checkpoint intervals.
