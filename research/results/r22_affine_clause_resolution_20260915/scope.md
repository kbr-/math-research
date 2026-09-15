# R22: complementary-parity resolution

Target full indexed lem:affine-clause-resolution-PC-degree, with overlapping
contexts and possible empty conclusion. First prove a reusable concrete
PCClause engine from actual prefix/companion certificates; then instantiate it
in the R18 fixed registry with premise clauses A∨u and B∨(1−u), conclusion A∨B.
No clause values are added as axioms. Premise values come with completed degreeK
primitive derivations. Ceiling is max(K,4h+1), independent of proof height.

Dependencies: R18 actual fixed-system data, R02 completed-line multiplication,
R05 degree2 Boolean proof for an affine pivot, R06 prefix identity/bounds.
Compute residuals RA, RB at4h; multiply RA by1−u and correct its quadratic
pivot error at4h+1; the resulting small polynomial (1−u)PT has actualdegree
atmost2h+1, so multiplying its completed line by the second cofactor costs4h.
R23 weakening and R24 globalDAG/CNF assembly remain separate records.
Initial source reading and proof planning preceded this cycle's clock.
