# Sources read for the source-coverage review

Reading scope is stated per source. These are mechanism comparisons, not
certification of entire external papers. No third-party full text is committed.

- Gessel–Viennot, *Binomial Determinants, Paths, and Hook Length Formulae*,
  [primary paper](https://sites.math.washington.edu/~billey/classes/561.fall.2019/past.articles/Gessel.Viennot.1985.pdf),
  Sections 1–2: Theorem 1 and the full Lemma 5 involution proof. Intersecting
  paths are paired; disjoint families survive. The record already proves the
  needed weighted layered version, so this is source confirmation, not novelty.
- Fomin, *Loop-erased walks and total positivity*,
  [primary paper](https://arxiv.org/html/math/0004083v1), Theorem 6.1,
  its switching construction and lexicographic choice, and Example 6.2.
  The formal-walk interpretation and its denominators are not a finite-field
  rank bound. No stochastic positivity theorem is imported.
- Raz, *Multi-Linear Formulas for Permanent and Determinant are of
  Super-Polynomial Size*,
  [ECCC source](https://eccc.weizmann.ac.il/report/2003/067/download),
  definition of multilinear formulas, Theorem 1 and its final deduction in
  Section 7. The underlying random-restriction lemmas were not audited.
  The theorem is over any field but concerns gatewise multilinear formulas.
  The author-page link and CiteSeer retrieval failed; ECCC supplied the paper.
- Behera–Hansen–Limaye–Srinivasan, *Separation Results for Constant-Depth and
  Multilinear Ideal Proof Systems*,
  [primary paper](https://arxiv.org/html/2601.06299v1), Theorems 1.5 and 1.7,
  Section 1.3's proof outline, the characteristic qualification after Lemma 2.3,
  and Lemma 3.1 with its short proof. The two separation theorems assume
  characteristic zero. Neither full lower-bound proof was audited.
- Markov–Shi, *Simulating quantum computation by contracting tensor networks*,
  [primary paper](https://arxiv.org/html/quant-ph/0511069v7), Theorems 1.1,
  1.7, 4.5 and 4.6, bounded gate-width convention, and the contraction proof
  of 4.6. Small fixed circuit depth alone does not imply small treewidth;
  this is also explicit in their depth-four example. No quantum computation
  is identified with the inconsistent old proof quotient.
- Abdesselam, *Grassmann–Berezin Calculus and Theorems of the Matrix-Tree Type*,
  [primary paper](https://arxiv.org/html/math/0306396v2), Section 2's ring
  assumption, Definitions 1–2, Proposition 1 and Proposition 5 / equation (15).
  The stated calculus assumes a ring containing the rationals; its exponential
  formula is not directly imported into characteristic two. The displayed
  determinant formula is a statement read, not a full proof audit.

Additional orientation only: the abstract of Behera–Limaye–Ramanathan–Srinivasan,
[*New Bounds for the Ideal Proof System in Positive Characteristic*](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2025.22),
reports restricted-system lower bounds and constant-depth upper bounds.
No theorem from that abstract is used as evidence or imported here.
