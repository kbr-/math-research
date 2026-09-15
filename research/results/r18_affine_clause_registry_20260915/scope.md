# R18: fixed affine clause registry

Target def:affine-clause-PC-system, including finite old affine map to ordinary
polynomial bridge, all prefix/value/companion bounds, complete fixed system,
and empty-clause convention. Registry C:FinN→ParityClause(σ→F2), for arbitrary finite σ, uses
σ ⊕ Σc, Finh×{g∈C c}; empty literal sets contribute no coefficient variables.
Inputs are old-only affine polynomials. System includes lifted old axioms,
Booleanity for all old/coefficient variables, and every companion. Values are
not automatically axioms. Accuracy h≥1 for prefix 2h−1; empty value holds allh.

Dependencies: R06 explicit ENS prefixes, affine form/polynomial map bridge from
R07, generalized to arbitrary finite coordinate types in FiniteAffinePolynomial; R01 primitive PC. A concrete PCClause certificate-data structure packages
actual products/identities and proved companion lines for later rule engines;
its existence is constructed, not assumed as replacement for the registry.
R22/R23 local PC rule proofs and R24 source DAG/counting/CNF bridge are separate.
The fresh single-block API uses σ⊕(Finh×ι), naturally embedded by the registry's
Σ-tagged variables; coordinate this interface with the affine-removal worker.
Initial instruction/source reading preceded this cycle's instrumentation.
