# R03: polynomial substitution with fixed-weight replay

Target: full historical lem:substitution. Variables map to ordinary polynomials
g(v) of degree≤T. The source finite PC tree has degree ceiling D. Prove all
substituted lines through TD; the weighted version derives weight*φ(f) through
TD+degree(weight), from supplied weighted images of each eligible original axiom.
This is not an assumption that arbitrary weighted images are axioms.

Dependencies: R01 primitive PC; R02 completed-line reuse; Mathlib monomial
expansion, algebra evaluation, and ordinary total-degree bounds. The key
nonzero multiplication premise has degree(p)+1≤D, not merely degree(p)≤D.
Zero predecessors are treated separately. The proof also covers T=0.
No source-specific axiom-image construction or ENS removal theorem is included.
Brief local API reading and initial proof planning preceded this clock.
