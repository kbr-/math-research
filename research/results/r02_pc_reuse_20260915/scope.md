# R02: completed-line reuse

Targets: historical lem:reuse, including its contrasting NS flattening bound,
and the elementary NS_B ⊆ PC_B inclusion used by lem:duality. Sources were read
in the R01 setup; brief initial proof planning preceded this cycle's clock.
Dependencies: R01 primitive Derives/NS definitions, Mathlib monomial expansion,
total-degree inequalities and exact multiplicative degree over an integral domain.

Prove actual max(B, deg q + deg f) reuse for all q,f including zero. Do not
multiply earlier proof lines. NS multiplication uses B+deg q because it
multiplies each old certificate term. Then derive every legal NS generator
using the exact degree of a nonzero product; the zero product is separate.
Substitution (R03), duality (R04), and all downstream lower bounds are excluded.
