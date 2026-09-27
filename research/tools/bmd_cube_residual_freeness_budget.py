#!/usr/bin/env python3
"""Exact small Hilbert budget for one six-root freeness test, not a size series.

At c2=0 the polynomial coefficient weights are3,4,5,6. The complete cyclic
presentation has six free target weights4,5,6,6,7,8 and at most one new relation
in each weight11 onward. The upper quotient has the explicit Hilbert function
of t4/((1-t)(1-t2)) + t9(1+t)/(1-t). Its c2-flatness identifies the difference
with the actual residual parameter fibre. Rank54 is known independently.
Fewer than2000 integer additions suffice through degree80; no numerical kernel
or polynomial elimination is used. Positive lower bounds alone can refute
freeness; failure to exceed54 does not prove it.
"""
import json

limit = 80
coeff = [1] + [0] * limit
for weight in (3, 4, 5, 6):
    for degree in range(weight, limit + 1):
        coeff[degree] += coeff[degree - weight]
prefix = []
total = 0
for value in coeff:
    total += value
    prefix.append(total)
rows = []
cumulative = 0
for degree in range(limit + 1):
    target = sum(coeff[degree - weight] if degree >= weight else 0
                 for weight in (4, 5, 6, 6, 7, 8))
    relation_columns = prefix[degree - 11] if degree >= 11 else 0
    upper = ((degree - 4) // 2 + 1) if degree >= 4 else 0
    if degree >= 9:
        upper += 1 if degree == 9 else 2
    lower = max(0, target - relation_columns - upper)
    cumulative += lower
    if degree >= 11:
        rows.append(dict(degree=degree, target=target, columns=relation_columns,
                         upper=upper, residual_lower_bound=lower,
                         cumulative_lower_bound=cumulative))
    if cumulative > 54:
        break
print(json.dumps(dict(N=6, generic_parameter_rank=54, rows=rows,
                     freeness_refuted_by_budget=cumulative > 54,
                     through_degree=degree), indent=2))
