# R01: ordinary polynomial proof foundations

Assigned worker targets: R01, R02, R03, R04, in that dependency order.
This checkpoint supplies definitions and their elementary well-formedness facts,
not the later completed-line multiplication, PC/NS comparison, substitution,
or separation theorems. Sources: paper section 2; notebook matching-moment
completeness audit and compact-bit-base-definition; historical foundations.

Use ordinary `MvPolynomial V K` over a field, with Mathlib natural total degree
(zero has degree zero). Finite applications use `Fin` variable types. PC has
only zero, axiom, addition, scalar multiplication, and variable multiplication;
every input axiom and variable-multiplication output is checked against B.
NS is the span of individual products whose actual total degree is at most B.
Neither quotient reduction nor cancellation across illegal multiples is implicit.
Boolean, weak-unary, functional-unary and binary compact bases are explicit.

Dependencies: pinned Mathlib polynomial degree inequalities and submodule span.
R02--R04 and all publication consumers remain outside this checkpoint.
