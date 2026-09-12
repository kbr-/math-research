# ENS input reduction and reduced-product Booleanity

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-ens-input-reduction)
contains the full original-degree replacement theorem and the exact generic PC/NS gap.
This directory preserves complete finite evidence over consistent local systems.

## Reproduce

With active resource controls, from the repository root:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_ens_input_reduction.cpp -o /tmp/check_ens_input_reduction
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_ens_input_reduction --out PATH-TO-NEW-OUTPUT.jsonl
```

The saved session is `ens_input_reduction_20260912_48`, with output `checks-01.jsonl`.
The program refuses to replace an existing output and uses no random choices.
It reuses the exact sparse kernel and helpers in `check_small_probe_normalizers.cpp`
and `pc_boundary.hpp`, without invoking an earlier suite.

The first build succeeded with a formatting warning; this was fixed before the
mathematical run. The final build and every check succeeded.

## Input replacements

Six cases use primes 2, 3, 5 and accuracies 1, 2. Old variables at indices 0, 1, 2
are Boolean x, y, z; index 3 is a field-valued a. Include the genuine local column
collision xy=0, but no row equations. The input tuple

```
(x^2+xy, (a^p-a)z+y^2, z^3+xy)
```

reduces to `(x,y,z)`. Coefficient variables start at index 4 and remain unchanged.
The program records three input-difference certificates, a product-difference
certificate, three derivations of old companions from the new system, and the
original/replayed nonzero NS consequence in each case: 54 NS certificates.
The target is the old product's Booleanity polynomial plus a coefficient field
equation; the replay keeps this ordinary polynomial exactly unchanged.

All 120 local base points across the six cases receive a saved canonical common
coefficient lift. This enumerates the base states, not every possible coefficient
completion. Old and new companion systems and the target are checked at each lift.

## Exact Booleanity gaps

Twelve cases use primes 3, 5, monomial degree t=1,2, and accuracy h=1,2,3. The first
t variables are Boolean; the next h variables are field-valued coefficients. Set
`g=product(z_i)`, `P=product(1-r_u*g)`, and retain the original companion `E=gP`.
The reduced value is `V=1-(1-product(1-r_u))*g`.

Each case records three NS certificates, a complete verified PC trace, two source
models, and a missing-companion countermodel. Its exact target degrees are

```
e = (h+1)t+h
NS degree of V^2-V = e+h
PC degree of V^2-V = max(e, 2(h+t))
```

The NS lower functional sets all old variables to one, reduces coefficient fields,
and extracts the coefficient of `product(r_u^2)`. It takes one on the target.
At the lower ceiling `e+h-1`, companion cofactors have original degree at most h-1.
The 56 saved monomial checks exhaust their possible coefficient-variable images;
every functional value is zero. The notebook proves the reduction of arbitrary
eligible cofactors to this enumeration and the universal lower bound.

In total: 90 NS certificates, twelve complete PC traces (with corrupted-trace
rejection), 56 lower-bound monomial checks, 144 model controls, and twelve
missing-companion controls. These are not full PHP instances and do not establish
the gap in the presence of arbitrary other extensions.

## Evidence format and timing

`checks-01.jsonl` stores all polynomials, original axiom arrays, NS cofactors,
targets, complete PC proof lines, monomial controls, and model points. It uses the
sparse polynomial format of `pc_boundary.hpp`, with variable indices as above.
Certificate degrees are checked using ordinary polynomial products, without
silently lowering an original axiom degree after specialization.

`provenance.json`, `timing.html`, and the archived session preserve hashes,
commands, and actual intervals. Some early checker design is included in the
mathematics window, as disclosed in the notebook; no retrospective split was made.
