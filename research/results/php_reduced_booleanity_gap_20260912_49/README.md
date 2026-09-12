# Reduced-product Booleanity over the full weak PHP base

This is the evidence/dependency record for the analytic notebook result
[The reduced-product Booleanity gap survives the full weak PHP base](https://kbr-.github.io/math-research/#entry-2026-09-12-PHP-reduced-Booleanity).
The full statement and proof are in the notebook; no new numerical suite was run.

## Parameters and scope

Over any odd prime field, take a t-cell matching monomial g on an n-hole board,
one accuracy-h ENS block with input g, and no other ENS blocks. Define

```
P = product_u(1-r_u*g)
E = gP
e = (h+1)t+h
V = 1-(1-product_u(1-r_u))*g
S = e+h
```

If `n-t >= 2S-3`, the exact NS degree of `V^2-V` is S and its exact PC degree is
`max(e,2(h+t))`. This board condition is sufficient, not claimed necessary.
For t=2 and h>=2 it reads `n>=8h+3`, with PC degree `3h+2` and NS degree `4h+2`.

| t | h | Sufficient n | Degree of V | PC degree | NS degree |
| -: | -: | -: | -: | -: | -: |
| 2 | 2 | 19 | 4 | 8 | 10 |
| 2 | 3 | 27 | 5 | 11 | 14 |

These are exact degrees of the specified Booleanity target, not refutation-degree
claims for arbitrary augmented families. Extra ENS axioms require a separate
residual-design argument. The characteristic-two normal-form results are unaffected.

## Dependency map

- The preceding result's complete NS/PC upper certificates use only the matching
  cells' Boolean domains and E. They remain valid when the full PHP base is added.
  See `research/results/ens_input_reduction_20260912_48/checks-01.jsonl`.
- `research/notes/SOURCE_AUDIT.md`, the Razborov section, records the exact weak-base
  bridge and the residual PC lower bound `N/2+1` over every field.
- Historical `manuscript/chapters/01_foundations.md`, Lemma 1.2, gives normalized
  ordinary-design existence from absence of a bounded-degree NS refutation.
- A genuine matching restriction leaves N=n-t holes, sends g to one, and sends
  base axioms to residual base axioms or zero. It does not infer row functionality.
- At D=S-1, the residual lower bound is strictly greater than D. Apply the resulting
  normalized design coefficientwise in the distinguished block's still-free r's.
  The original companion cofactor has degree at most D-e=h-1. Extracting the
  coefficient of `product(r_u^2)` after field reduction gives the NS contradiction.
- For PC below e, the companion is unavailable. The same matching restriction
  followed by `r_1=-1`, other r's zero, turns the target into nonzero constant two,
  contradicting the residual base lower bound. No PC replay through a design is used.

No large design was numerically constructed, no historical suite was rerun, and
no private reference source was copied. `provenance.json` records the cited local
dependencies and prior exact evidence. Timing and the archived session preserve
the actual reading, proof, and checkpoint intervals.
