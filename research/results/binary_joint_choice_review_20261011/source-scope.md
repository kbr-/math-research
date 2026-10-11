# Sources and reading scope

Read on 11 October 2026. These are bounded source checks, not independent
certifications of entire papers. Third-party source files remain outside public
history. The complete proof of the new restricted construction is in the notebook.

- Zeev Dvir, [On the size of Kakeya sets in finite fields](https://arxiv.org/abs/0803.2336).
  Read the interpolation step in the main proof and the improved-bound proof.
  Only the elementary evaluation dimension argument is used. No Kakeya incidence
  hypothesis or field-size bound is transferred to the binary cube.
  Downloaded TeX SHA-256:
  `2a251b0397808b10d29d424c737d00f7d9cb81e9583bd967da0adbabe14e5f50`.
- Guy Moshkovitz and Jeffery Yu,
  [Sharp Effective Finite-Field Nullstellensatz](https://arxiv.org/abs/2111.09305).
  Read Theorem 1 and its complete proof. The conclusion is functional equality
  over the finite field. For the binary cube, Boolean division gives a literal
  certificate at the polynomial expression's degree; its input-count cost is
  retained. Lower-bound examples and the later arbitrary-subset generalization
  were not used. Downloaded TeX SHA-256:
  `87f101c887720acf7e1f7cb4b83cbda02adb6ea67f02ee9b41d1d3124fbfd0b4`.
- János Kollár,
  [Sharp Effective Nullstellensatz](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Kollar/kollarnullstellen.pdf).
  Read Definitions 1.3–1.4, Theorem 1.5 and Corollary 1.7 on printed pages
  964–965. The cited version excludes degree two; no application to the Boolean
  generators is asserted. The degree-product comparison is a test of the stated
  bound, not an optimality claim for our systems. Full proof not read.
- Charles H. Bennett,
  [Logical Reversibility of Computation](https://www.cs.princeton.edu/courses/archive/fall06/cos576/papers/bennett73.html).
  Read the main simulation theorem and compute/copy/uncompute explanation.
  No claim to have checked the full transition-table construction. The polynomial
  graph shear and its inverse are proved directly; the degree limitation is the
  already recorded reversible-value theorem, whose full proof was reread.
- Mihalis Yannakakis,
  [Algorithms for Acyclic Database Schemes](https://www.researchgate.net/profile/Mihalis-Yannakakis/publication/200034379_Algorithms_for_Acyclic_Database_Schemes/links/5745c2a708ae9f741b430b62/Algorithms-for-Acyclic-Database-Schemes.pdf).
  Read join definitions and Section 4's algorithm and Theorem 4.1 via the original
  paper. The VLDB URL failed; the author-associated copy was accessible.
  The theorem concerns time polynomial in explicit input/output table sizes.
  No polynomial-degree certificate theorem is attributed to it.

Registry searches found the relevant prior relative-learning, offset-compression,
triangular-pruning and reversible-value records. Searches for Moshkovitz–Yu gave
no match; this is not an exhaustive claim of absence. No full handoff import was
repeated. Some broad search output was truncated; only the separately read exact
proofs are mathematical premises.
