# Source audit — completed import, 10 September 2026

All four direct references are acquired and extracted. Acquisition is not a
claim of independently verifying every proof in every paper. Earlier failures
remain in the import log. Source paths below are relative to `research/`.

## Razborov: base and residual PC lower bound

User supplied `references/user_supplied/Razborov.pdf`; the document identifies
itself as *Computational Complexity* 7 (1998), 291-324. SHA-256:
`a733438feeda422d58c004b2331b742380d11d84e587990a2fd240466ecda47f`.
Exact download URL was not supplied; do not fabricate it.

Read extracted lines 1-32, 130-164, and 214-251; visually inspected PDF pages
6-7 (printed pp. 296-297). Definition 2.4 has row equations 1-sum_j x_ij and
both row/column exclusions, in the Boolean quotient. Theorem 3.1 gives degree
at least n/2+1 over every field for every m>n.

**Degree-convention bridge.** Definition 2.1 works in the multilinear Boolean
quotient and charges multiplication by x the degree of its predecessor plus one.
Map each line P of our ordinary-ring degree-D PC proof to its Boolean reduction.
Linear combinations commute with reduction. For a nonzero ordinary multiplication
P -> xP, deg(P)+1<=D, so the source inference charge is also <=D. Zero lines can
be omitted. Boolean axioms map to zero; row axioms differ only by sign. Thus an
ordinary-PC refutation of our weaker base gives a degree-at-most-D source proof
from the stronger row-exclusive system. Its lower bound therefore applies.

Under a partial matching of t pigeons to t distinct holes, assigned rows/columns
become constants and the surviving equations are exactly our base on m-t rows
and n-t columns, plus zeros. Since m-t>n-t, the same theorem applies. This
discharges the imported base/residual PC hypothesis used by `thm:rigidity`.
It does not prove the missing elimination theorem or ordinary-PHP proof transfer.

## BIKPRS: actual simulation structure

User supplied `references/user_supplied/BIKPRS.pdf`, a six-author, author-layout
copy with the cited title. SHA-256:
`78fff21cb13fb81d110bcfacba57d9be5a7dbd0ab36e1e1e2e4207fbcb09f4d2`.
Exact origin/version beyond document identification was not supplied. Do not
label it the publisher's paginated version without further evidence.

Read the title, Definitions 6.1/6.4/6.5, Theorem 6.7(1), Definition 6.8,
the first part of Lemma 6.9, Lemmas 6.10-6.12, and the concluding proof of
6.7(1). Extracted ranges: 1-28, 1120-1148, 1191-1231, 1246-1255,
1360-1455, 1484-1563. This is targeted reading, not a full-paper proof audit.

Theorem 6.7(1) (PDF p. 26) supplies |E|<=S^{O(1)}, extension depth ell+C,
arbitrary accuracy h>=1, and NS degree (d_0+log S)(h+1)^{O(1)}, with the
depth dependence made explicit by Krajicek Theorem 5.2 as O(ell).
Definitions 6.1 and 6.4 include Boolean original variables and field-valued
extension variables with their respective domain equations.

The proof first replaces the Frege proof by a polynomial-size tree-like proof
of height O(log S), with only constant additive formula-depth overhead.
Definition 6.8 creates blocks from the complements of approximations of the
children of disjunctions. The source encodes TRUE by zero; account for this
when transferring Boolean formulas. Polynomial input degrees grow with formula
depth; Lemma 6.10 bounds them by (ell+1) max{p-1,h}^{ell}.

Lemmas 6.9-6.12 provide local algebraic derivations. The final NS certificate
is assembled by induction on derivation height, yielding the logarithmic S
factor. Local multipliers and their products along proof branches determine
cofactors; no bound on residual rank, chain count, or essential cofactor support
small enough for our elimination has been established by this import. Balanced
derivation height alone must not be silently promoted to that missing theorem.

## Previously checked inputs

Krajicek v3: exact ENS syntax; ordinary-design lower bound and residual-board
matching by axiom deletion; simulation statement. Full extracted text read.
The p. 10 Boolean-redundancy display has an odd-prime sign typo, harmless because
Boolean axioms are explicitly included. Details are in IMPORT_LOG.md.

Pebbling v1: equations (2.5)-(2.6), Theorem 3.1, Definition 4.7, and Lemma 4.9
match the pebbling encoding, any-field NS-degree correspondence, and the
Gamma(1,r) single-sink family needed by the generic-design obstruction.

**Obligations at the historical import checkpoint:** affordable refutation-sensitive elimination/joint
design, exact ordinary-PHP proof transfer, and final quantified parameter closure.

## Follow-up source reading: ordinary-PHP transfer, 11 September 2026

For the notebook entry
[The ordinary-PHP simulation bridge](https://kbr-.github.io/math-research/#entry-2026-09-11-ordinary-php-transfer),
read additional BIKPRS extracted lines 166–218 and 254–269: the fixed Frege
basis, MOD recursion axioms, flattened-disjunction depth convention, and the
TRUE-by-zero translation, including its input convention.
Revisited lines 1120–1264, 1320–1397, and 1484–1548 for the NS/domain convention,
effective assumption degree, full-companion leveled extensions, Theorem 6.7(1),
and the approximation construction. The source PDF is the same locally supplied
copy identified by its hash above.

The relevant distinction is that an ordinary row disjunction has source
effective degree n, while a MOD-one row has effective degree p-1.
The notebook supplies the explicit modular-row-to-clause derivation and
the ordinary-ring substitution argument; this addendum records source coverage.
Krajicek v3's paragraphs around Lemma 5.1 and Theorem 5.2 were also reread to
separate that source's functionality-containing equivalence from this argument.

## New source reading: matching switching lemma, 18 September 2026

For the notebook entry
[Importing the matching switching lemma](https://kbr-.github.io/math-research/#entry-2026-09-18-switching-lemma-import),
read Paul Beame, *A Switching Lemma Primer*, technical report (University of Toronto / University of
Washington, 1994), from the author-course copy at
http://www.cs.utoronto.ca/~toni/Courses/Complexity2015/handouts/primer.pdf (also hosted at
https://users.cs.duke.edu/~reif/courses/complectures/Beame/SwitchingLemmaPrimer.pdf and
https://homes.cs.washington.edu/~beame/papers/primer.ps). Local private copy
private/references/Beame1994-switching-lemma-primer.pdf, sha256 67329a8a506ec20f741e565fa1bb038e820601091b4f113cd916a3cbab798050, with a pdftotext extraction.
Read Section 5 (printed pages 13–17): the q-variables and q-terms over a set D with |D|=qn+1, the
restriction family M^ell_{D,q} of partial q-matchings leaving q ell+1 unmatched points, matching
decision trees, representation and refinement, the canonical tree T_D(F), and Lemma 4 with its
counting proof. Also Section 6.3 headings (Lemma 10, representation after restriction). The statement
is nonbipartite (hypergraph matchings on one point set); the bipartite PHP-board versions in PBI 1993
and KPW 1995 were not obtainable (see the Git-ignored user_requests note).

## New source reading: polynomial calculus with extension variables, 18 September 2026

For the notebook entry
[Plain exact elimination on the functional PHP cannot reach the recorded second-level loss](https://kbr.is-a.dev/math-research/#entry-2026-09-18-level-two-feasibility),
two papers were retrieved and read in part. Their statements are imported as context only;
no notebook result depends on them.

1. Russell Impagliazzo, Sasank Mouli, Toniann Pitassi, *Lower Bounds for Polynomial Calculus
   with Extension Variables over Finite Fields*, CCC 2023, LIPIcs 264, 7:1-7:24,
   https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2023.7 (CC BY 4.0). Local
   private copy private/references/IMP2023-LIPIcs-CCC-2023-7.pdf, sha256
   4f2ec474d5651e8889073880e2e426b3f9ac18f306a30c2572734185a1fa364c, with a pdftotext
   extraction. Read: the abstract (main theorem: M extension variables of arity kappa =
   O(log n), size exp(Omega(n^2)/(10^kappa (M + n log n)))); the introduction's paragraph on
   size lower bounds from degree lower bounds over {0,1}-valued variables; the opening of
   Section 3 (extracted lines 296-305): the case p = 2 needs no new ideas, extension
   variables are zero-one valued so size-degree tradeoffs apply, kappa-local extension
   variables change the degree by at most a factor kappa, tolerating close to n^2/kappa^2
   extension variables. Also read: the first paragraph of the introduction (superpolynomial
   bounds for AC^0[p]-Frege are open), Theorems 1 and 2 (extracted lines 94-101), and the remark
   after Theorem 2 (lines 104-114): extension variables depend on original variables only, the
   recursive case corresponds to AC^0[p]-Frege, the result is for depth-2.5 refutations.
   Proofs not read.
2. Yogesh Dahiya, Meena Mahajan, Sasank Mouli, *New lower bounds for Polynomial Calculus over
   non-Boolean bases*, ECCC TR23-132 (SAT 2024, LIPIcs), https://eccc.weizmann.ac.il/report/2023/132/.
   Local private copy private/references/DMM2023-ECCC-TR23-132.pdf, sha256
   ed4e6045b5d038868092e739aa4b4ed93aa9ddc27fdba7e94c34045c676a14cb, with a pdftotext
   extraction. Read: the abstract; the introduction (constant-depth PC of Grigoriev and Hirsch
   simulates AC^0[p]-Frege; Theorem 1.2 with N^(1+eps(1-delta)) extension variables of arity
   N^(1-eps) and size N^c, size exp(Omega(N^(eps delta)/polylog N)), for an XOR-ification of
   Razborov's generalised PHP^{m,r}_n); "Our Techniques" and the proof outline of Section 4.1
   (XOR_2 lift, random restriction reducing extension axioms to logarithmic degree, removal of
   bounded-degree extension variables by restrictions of small Hamming weight with cleanup,
   quadratic degree; restriction to p > 2 with a reference to item 1 for p = 2); the caveat of
   the introduction (extracted lines 72-80) that constant-depth PC also simulates Cutting
   Planes, SOS, AC^0[q]-Frege for every prime q and TC^0-Frege, so that general lower bounds
   for it are much harder than for AC^0[p]-Frege. Proofs not
   read; the license of the ECCC report was not determined, so the copy stays private.

## New source reading: the PHP under linear constraints, 18 September 2026

For the notebook entry
[The PHP under linear constraints](https://kbr.is-a.dev/math-research/#entry-2026-09-18-parity-subspace),
two papers were retrieved and read in part. Their statements are imported as context; the
definition of a safe linear system is used in the entry's Lemma SL with attribution, and the
lemma's proof uses recorded notebook tools only.

1. Mladen Mikša, Jakob Nordström, *A Generalized Method for Proving Polynomial Calculus Degree
   Lower Bounds*, CCC 2015 (LIPIcs 33, 467-487); journal version J. ACM 2024,
   doi:10.1145/3675668 (not read). Read: arXiv:1505.01358v1, local private copy
   private/references/MN2015-arXiv-1505.01358v1.pdf, sha256
   6fb604d9a47ba37e697a9699b7d0f1c74faf824da8961c904f2552f397a18230, with a pdftotext
   extraction. Passages: the abstract; Definitions 3.6, 3.7 and Theorem 3.8 (an
   (s, delta, xi, E)-expander with overlap d forces degree greater than (delta s - 2 xi)/(2d));
   Definition 4.1 and Theorem 4.2 (Alekhnovich-Razborov: degree greater than delta s/2 for an
   (s, delta)-boundary expander incidence graph); the graph PHP axioms (4.2a)-(4.2d);
   Theorem 4.5 (onto graph PHP, degree greater than delta s/2 - xi under a matching condition);
   Theorem 4.9 (graph functional PHP over an (s, delta)-boundary expander of left degree at most
   d requires degree greater than delta s/(2d)). Proofs not read. The arXiv license does not
   permit redistribution by us, so the copy stays private.
2. Farzan Byramji, Russell Impagliazzo, *Lower Bounds for Bit Pigeonhole Principles in
   Bounded-Depth Resolution over Parities*, arXiv:2511.20023v1 (25 November 2025), ECCC
   TR25-118. Local private copy private/references/BI2025-arXiv-2511.20023.pdf, sha256
   59f46b182affa0a26ab5af1ce26332311fc675706ae4afa76e23cf1c4dcc9715, with a pdftotext
   extraction. Read: the abstract (depth N^(2-eps) Res(parity) refutations of the bit PHP with
   n+1 pigeons have exponential size; no superpolynomial bounds were known for depth superlinear
   in the formula size); the proof overview, extracted lines 497-531 (affine restrictions; a
   linear system of rank r is safe if it can be rewritten as fixing r variables from distinct
   blocks as affine functions of the others, and then the r pigeons go to 2r holes without
   collisions, each to a pair of holes differing in one bit; closure Cl(Phi) with the
   decomposition into a part on the closure of rank at least |Cl(Phi)| and a part that is safe
   once the closure is fixed; all attributed there to Efremenko, Garlík and Itsykson, whose
   paper was not retrieved) and lines 806-823 (safe dimension; probability bounds for safe
   systems of rank r + l when r <= cn for a small constant c). Proofs not read; the copy stays
   private.

## Further reading of Dahiya, Mahajan, Mouli, 18 September 2026 (route review, cycle 224)

Same private copy and hash as in the entry above (private/references/DMM2023-ECCC-TR23-132.pdf,
sha256 ed4e6045b5d038868092e739aa4b4ed93aa9ddc27fdba7e94c34045c676a14cb). Read in full in the
pdftotext extraction: Section 4.1 (lines 372-453: the framework of Impagliazzo, Mouli and
Pitassi as described there, with cleanup restrictions that need extension variables of
logarithmic arity and a subquadratic number of them; the outline of the new proof), Section 5.1
(the formula PHP^{m,r}_n and Razborov's degree bound n/2 + 1), and Section 5.2 through the three
cases of the proof of Theorem 5.5 (lines 582-760): Lemma 5.3 (an assignment of Hamming weight at
most l deg(Q) that brings Q to the form (b-a)x + a), Corollary 5.4, Theorem 5.5 (size at least
exp(Omega(n^2 / ((M + mn) kappa k))) for M extension variables of degree at most k in at most
kappa variables, r > 2pk), the removal of at most kappa affected holes per round, the
observation that an assignment of weight below r/2 commits no pigeon to a hole, and the final
substitution of the definitions at a factor k in degree. Not read: Section 3 (the +-1 basis),
Section 4.2 beyond the definitions, the remainder of Case 3 and the proof of Theorem 1.2 from
Theorem 5.5. The statement that the ordinary PHP does not survive these assignments is the
notebook's own reading, not the paper's. The copy stays private.
