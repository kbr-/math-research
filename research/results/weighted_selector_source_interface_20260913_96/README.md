# Weighted selectors and binary NS source modules

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-weighted-selector-interface)
proves ordinary weighted-degree reflection for genuine leveled selectors over
any field, then constructs a binary source NS identity with selector-valued
outer coefficients. The PHP boundary map gives an old-target identity for one.
Global elimination of that identity is still open.

The embedding requires nonzero input tuples and disjoint fresh own coefficient
families. It does not identify Boolean/field quotients, include arbitrary raw
coefficients, or survive treating shared products as independent selectors.
The binary source profile is asserted after the standard affine PHP map and
constant cleanup, before optional packing.

## Degree tests and controls

The file <code>weighted-degree-checks.jsonl</code> has four cases: p=2 with
first-block accuracy 1 or 2, and p=3,5 with accuracy 1. Old variables x,y,z
have indices 0,1,2. Formal selectors A,B,C have slots 60,61,62; slot 63 is
reserved for deliberate sharing and constant-product controls.

Actual blocks use fresh variables starting at index 3:

    A: inputs (x,y), accuracy h_A
    B: inputs (xy+1,z), accuracy 1
    C: formal inputs (Z_A+x, y*Z_B), accuracy 1

Weights are (2,3,5), except (4,3,5) for h_A=2. The polynomial input y*Z_B
tests the general embedding theorem; it is not an example of the more
restricted binary source profile.

Each case saves all actual products, formal and actual C inputs, and seven
complete test polynomials with their images. All 28 weighted degrees equal
the corresponding ordinary concrete degrees. The tests include powers,
mixed selector terms, and potential leading-term cancellations.

The field control Z_C^p-Z_C has nonzero ordinary image but zero normal form
modulo old Booleanity and coefficient field equations. The zero-fiber control
(1-x)(1-y)(Z_A-1) vanishes after old Boolean reduction alone, while its formal
value at x=y=Z_A=0 is p-1. Sharing a product or retaining a constant product as
a new formal variable gives the recorded nonzero kernel controls. A bare
coefficient has degree one; its absence from the valid selector image follows
from the proved reflection theorem and selector weights exceeding one.

## Complete NS gate witnesses

The file <code>selector-gate-checks.jsonl</code> uses p=2 and h=1,2. Each of
two independent child tuples has rank r=2h+1. The first uses old coordinates
0..r-1 and the second r..2r-1. Their genuine products are a,b. The parent c
uses the input tuple (a, second-child inputs), so it is a genuine later block.
Own coefficient rows follow the old coordinates in A, B, C order.

The formal relation is Z_C-(1-Z_A)Z_B. The output supplies the full
ordinary-polynomial NS certificate, including the field-only proof of
a^2-a, with every original axiom and its cofactor.

| h | Actual variables | Selector weights | Relation degree | Witness degree | New / old MP multiplier degree |
| ---: | ---: | --- | ---: | ---: | --- |
| 1 | 16 | 2,2,3 | 4 | 7 | 2 / 3 |
| 2 | 42 | 4,4,10 | 10 | 18 | 4 / 10 |

The witness costs equal deg(a)+deg(b)+deg(c), within 3L. The new external
MP multiplier is b; the older prefix multiplier is b*U_0^C. The formal MP
identity is checked separately. These are proper gate-parameter examples,
not nonconstant original-level-one theorem antecedents. The reported witness
degrees are upper bounds for these certificates, not minimum-degree claims.

## Encoding and reproduction

Polynomial records use exact residues modulo the recorded prime. Each term
is [coefficient, [[variable_index, exponent], ...]]. Degrees are ordinary;
no implicit Boolean reduction is used in identities or degree comparisons.
Domain controls explicitly state their different reduction.

Use fresh output paths from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_mp_composition.cpp -o /tmp/check_mp_composition
./compute.sh run TURN --threads 1 -- \
  /tmp/check_mp_composition --out NEW_DEGREES.jsonl --weighted-selectors
./compute.sh run TURN --threads 1 -- \
  /tmp/check_mp_composition --out NEW_GATES.jsonl --selector-gates
~~~

No random seed or extra dependency is used. The two modes refuse to replace
existing output files. Only these new modes were run for this cycle.
<code>provenance.json</code> pins the code, shared header, this description,
and complete outputs. Timing and full command evidence are retained in the
matching session archive. These finite tests support the local identities;
they do not constitute a global PHP proof or an elimination algorithm.
