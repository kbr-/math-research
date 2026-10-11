# Source reading

Limaye, Srinivasan and Tavenas, *New Non-FPT Lower Bounds for Some Arithmetic
Formulas*, ECCC TR21-094, retrieved primary PDF:
https://eccc.weizmann.ac.il/report/2021/094/download/

Retrieved PDF SHA-256:
fdab69f90128269c6c779a5f70af1cc328734f3331219526d35cb5ad56b4cc0b.

Read the definitions and Theorem 4, Section 2.1's coefficient-matrix measure,
Lemma 6 and its complete projection proof, and Section 4's Proposition 15
and Corollary 16 proofs. The homogeneous/ordered set-multilinear hypotheses
are essential. No full-paper audit or quantitative exponent is imported.
The PDF text extractor warned about annotation destinations; the statements
and selected proofs were present. No conclusion relies on a damaged link
destination or an ambiguous extracted exponent. The primary PDF and text
remain private scratch, not redistributed.

Notebook reading: the full original-input noncommutative Tseitin construction,
its pre-descent factor ledger, the binary component-depth obstruction, the
balanced modular/positive-flow distinction and the matched-frontier flow
degree ceiling. The latter does not settle circuit size.

GAP control 20c55a8123, with its complete output in check.txt: local edge and
star identities, all Laurent monomials in the two-edge interpolation range,
a nonzero formal path product and omitted-point negative control, and scalar
trace/conjugate projections. The first attempt used unsupported Int(boolean)
and was rejected despite GAP's zero process exit; the next passed with
forward-global warnings, then explicit declarations removed those warnings.
No count from either earlier attempt is used as the final verification run.
