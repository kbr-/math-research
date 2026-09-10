# Mathematical checkpoint — local import, 10 September 2026

**Goal.** For every fixed prime p, depth ell, and polynomial exponent K, prove
that ordinary PHP has no depth-ell AC^0[p]-Frege proofs of size n^K for all
sufficiently large n. **This has not been proved.**

## Exact base and invariants

Work over F_p with n+1 rows and n columns. The current base is

\[
\mathcal F_n=\{\rho_i-1\}_i\cup
\{x_{ij}x_{i'j}:i\ne i'\}\cup\{x_{ij}^2-x_{ij}\}_{i,j},
\qquad \rho_i=\sum_jx_{ij}.
\]

There are no same-row exclusions. A row sum of one in F_p does not mean exactly
one occupied cell. The non-Boolean graded ring is a separate branch.
An ordinary degree-D design annihilates original-axiom multiples through D;
annihilating all degree-D PC consequences is stronger. Preserve that distinction.

An ENS block has all companions
\[
E_{a,i}=g_{a,i}\prod_{u=1}^{h_a}\left(1-\sum_jr_{a,u,j}g_{a,j}\right)
\]
and field axioms r^p-r. Inputs may be nonlinear and use earlier-level variables.
Always retain original joint-variable degree when determining permitted cofactors.

## Reusable working results

The local proof audit found no gap in PC reuse/substitution, selector-based
one-block elimination, reverse-level additive elimination, nested-span replay,
or the core/residual absorption argument. This is a mathematical review of those
arguments, not a formal verification of the entire manuscript.

The useful bounds are
\[
D+(p-1)\sum_a\delta_a,\qquad
D+(p-1)\delta\ \text{for one nested chain},\qquad
TD+(p-1)\gamma\ \text{for a core/residual batch}.
\]
Previously derived final polynomials are reused without multiplying their whole
derivations. All field-ideal reductions need degree-bounded certificates.

The static affine ordering/partition problem is solved within its criterion.
Its spread family has optimum
\[
\min\{D+(p-1)n,T(r)D\}>\lfloor n/2\rfloor
\]
in the stated fixed-p asymptotic regime. The family is admissible extension data,
not a supplied refutation. A better static ordering is not the next objective.

## Literature checks completed

- Krajicek v3 Definition 2.1 matches ENS syntax. Its p. 10 axioms and Lemma 4.1
  give ordinary base/residual designs after deleting row exclusions. Theorem 5.2
  cites BIKPRS Theorem 6.7(1): polynomially many companions, ell+O(1) levels, and
  degree (O(1)+log k)(h+1)^{O(ell)}. No inexpensive cofactor structure follows
  from that statement alone.
- Pebbling v1 Theorem 3.1 matches the manuscript's encoding and all-field NS
  degree correspondence. Gamma(1,r) supplies the stated single-sink
  Theta(r^3)-vertex, Omega(r)-price family.
- Both remaining PDFs were supplied and extracted. Razborov Definition 2.4 /
  Theorem 3.1 and the degree-convention bridge now match the base/residual PC
  lower bound. BIKPRS Theorem 6.7(1) and its construction use disjunction blocks
  over a balanced tree-like proof of height O(log S). This does not establish
  affordable cofactor support. The ordinary-PHP proof transfer remains open.
  See SOURCE_AUDIT.md for precise scope; no full-paper proof audit is claimed.

## Next step

The first local research note proves that blocks absent from an actual NS
certificate can be removed by constant substitution at no degree cost, even
when their variables occur in surviving inputs or cofactors. It suggests applying
batching only after this pruning. This handles irrelevant spread blocks and is
compatible with the prefix-pebbling control, but supplies **no uniform affordable
bound** on the remaining relevant blocks.

The central missing theorem is still refutation-sensitive elimination below
\(b_n=\lfloor n/2\rfloor\), or a suitable joint design, for every relevant
translated certificate. See IMPORT_LOG.md, RESEARCH_LOG.md, and
STATUS_AND_AUDIT.md for coverage and qualifications.
