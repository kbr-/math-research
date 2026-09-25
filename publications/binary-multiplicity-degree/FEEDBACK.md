# Origin

- [x] In correspondence about the earlier [note](../binary-polynomial-multiplicity/) (24 September
  2026, paraphrased), an author of Bishnoi–Boyadzhiyska–Das–Mészáros explained that their
  question's threshold k ≥ 2^(n−2) is the range where hyperplane covers attain the bound. He
  suggested two directions: decide whether the algebraic bound is tight for smaller k, where
  extremal polynomials cannot be products of linear forms, or improve it; and look at the open
  questions of Sauermann and Wigderson.
  - Version 1 (24 September 2026): D(n,k) = 2k + n − 2 − ⌊log₂k⌋ for k < 2^(n−1), so the bound
    is attained if and only if k ≥ 2^(n−2); the extremal polynomials are Menezes' Catalan
    truncations, not products of linear forms.
  - Version 2 (25 September 2026): the least degree δ(n,k,ℓ) for every origin order ℓ, in every
    dimension.

# Version 2

The items below come from these sources:

- the author's own requests during the version-2 work (A);
- Claude Code's assessments of readiness (C);
- a blind referee pass by a fresh Claude Opus 5.5 agent that read only `whitepaper.tex`,
  `references.tex` and `sections/`, with no access to the rest of the repository or the web
  (R, 25 September 2026).

R found no mathematical error. It checked every step of Sections 3–5 and Appendix A, including
the edge case ℓ = k − 1. Its findings are reviewer comments, not independent expert review;
R's numbers are given in brackets.

### Done before the blind referee pass

- [x] Formalize every mathematical claim of the paper, not only the numbered results (A).
  - Six modules, commit 8c826402; a fresh audit found the statements about D and δ were stated
    for the closed forms, so they were restated for the least degrees themselves (168a0c8e). See
    [REVIEW-v2.md](REVIEW-v2.md#full-formalization-25-september-2026).
- [x] Shorten to about 12–14 pages: move the second proof to an appendix, reduce the framework
  and assistance material to a paragraph, keep the Lean map (C, A).
  - Main text 14 pages; Appendix A is the second proof, Appendix B the Lean map (eef8bea4).
- [x] Novelty check: read the works citing Sauermann–Wigderson, Bishnoi et al. and Menezes, and
  Menezes' own remarks (C, A).
  - Menezes' Section 8 records n = 1 and names smaller dimensions as open; Huang–Wang–Wang extend
    the real range to n ≥ k − 1. Both credited; the new range is stated as 2 ≤ n < k − 1
    (ab0df628). The shared checklist item was strengthened after this gap (6e755911).

### Statements and attribution

- [ ] The abstract's "every mathematical claim of the paper is formalized in Lean" is broader
  than true (R13). The exceptions are statements about other papers, the grid-vanishing lemma
  (Mathlib), the computational evidence of Remark 5.3, and the identification of g_s with
  Menezes' truncation. Say "every theorem, lemma and corollary", or list the exceptions.
- [ ] "g_s is the specialization to F₂ of the Catalan truncation of Menezes" cannot be checked
  from the paper (R14). Display Menezes' polynomial and the one-line reduction mod 2 through
  v₂(C_{a−1}) = s₂(a) − 1, or weaken the claim to "coincides with (cf.)".
- [ ] The value n + 2k − 2 at ℓ = k − 1 is attributed to Sauermann–Wigderson within n ≥ 2k − 3 in
  one place and for every n ≥ 1 in another (R11). Harmonize: their Theorem 1.5 holds for every
  n ≥ 1.
- [ ] Missing comma in "In the range n≥2k−3 k−ℓ−1<2^n" (R12).
- [ ] Bishnoi et al. are cited by journal numbering for Question 4.3 but by arXiv v1 numbering
  for Theorem 1.2(a), Section 1.3 and Section 2 (R18). Cite the published version throughout, or
  give the correspondence for every cited item.
- [ ] Menezes' entry pairs identifier arXiv:2609.19009v1 (a September identifier) with the date
  14 August 2026 (R19).
  - Note: 14 August 2026 is the submission date arXiv's abstract page shows for v1, so the
    mismatch is on arXiv's side. Keep the date and identifier as arXiv gives them, perhaps with a
    remark.
- [ ] Sauermann–Wigderson is cited only as arXiv v2 (R20). Add the journal version, J. London
  Math. Soc. 106 (2022), no. 3, 2379–2402, and check that Theorems 1.3–1.5 keep their numbers.
- [ ] The abstract says the Schwartz–Zippel bound was "asked for" by Bishnoi et al.; they asked
  whether it is a lower bound for k ≥ 2^(n−2) (R22). Also, "the product of the 2^n − 1 affine
  hyperplanes" should be "of their affine forms".
- [ ] "the lower bound is the case F = F₂ of [AF93, Theorem 5]": R could not check the theorem
  number from the text (R21).
  - Note: checked against the source in the earlier note's audit; recheck before submission.

### Notation

- [ ] δ is both the least degree δ(n,k,ℓ) and the shift vector in Lemma 4.2 (R4). Rename the
  shift vector.
- [ ] s is the index of g_s, the summation index of x̂_K, the exponents s_a, the tuple in
  "τ = s" (Section 4, Step 3) and part of s₂ (R4). Rename the tuple and the exponents.
- [ ] w is the series of Section 4, the local sum Σa_i in the degree part of Theorem 3.4, and a
  variable in the proof of Lemma A.5 (R2, R4). Rename the latter two.
- [ ] In Definition 3.3 a_i are powers of two, but in the proof of Theorem 3.4 a is a point
  ("a_{i₀} = 1") (R2). In Appendix A, "the multiplicity at a ≠ 0 is at least a2^(n−1)+b" uses a
  for both a point and an integer (R3). Rename the powers (for example p_i) and the integer
  (k = c·2^(n−1) + b).
- [ ] The substitution fact of Section 2 reuses z, the formal shift variable, for substituted
  elements, and is stated over F₂ although nothing depends on it (R1). State it over any field
  with a fresh letter.
  - Note: the Lean statement is over ZMod 2; a general statement needs either a remark or a
    generalized declaration.
- [ ] z^β in the proof of Theorem A.6 is a monomial in x′, not in the shift variable (R4).
- [ ] The outline writes S = P(x′,0) + P(x′,1); Appendix A uses Q(0,x′) + Q(1,x′) after a change
  of coordinates (R6). Make them agree.

### Proofs and exposition

- [ ] The outline calls w "one power series" and x̂ an infinite series; the proof uses the
  polynomial truncation x̂_K with K = k, and w is a polynomial (R5). Say "truncated".
- [ ] Appendix A, proof of Theorem A.6: "for otherwise S = 0, which the next item excludes"
  refers to the wrong item (the fourth one excludes it), and deg S ≤ deg Q − 1 needs S ≠ 0
  (R7).
- [ ] The remark "D(n−1,k) ≤ D(n,k) − 1" sits between Theorem A.6 and its proof (R8). Move it
  after the proof.
- [ ] Unneeded hypotheses (R9): Lemma 4.3 needs only 2^K ≥ k > ℓ, not the multiplicity condition
  at nonzero points; Lemma 4.4(2) does not need t < k; Lemma 4.6 does not need V nonempty. State
  the minimal hypotheses or add a remark.
  - Note: the Lean statements carry some of these hypotheses. A remark keeps the links exact;
    changing the statements needs a new Lean commit and pin.
- [ ] "D(n,1) = n for n ≥ 2": the corollary also gives D(1,1) = 1 (R10). Drop the restriction or
  say it is there for the comparison with Alon–Füredi.
- [ ] Section 3's sentence "It works in every dimension, with the digit-sum bound, also when
  k−ℓ−1≥2^n, where Theorem 3.7 has degree below that bound" is hard to parse (R15). Suggested:
  "Proposition 3.8 holds in every dimension; when k−ℓ−1 ≥ 2^n its degree bound exceeds Φ."
- [ ] "the grid-vanishing lemma … for a grid of 2^n polynomials" is opaque in the introduction
  (R21). Say "a grid V^h with V ⊂ F₂[y] of size 2^n".
- [ ] δ(n,k,ℓ) is defined as a least degree before the set is known to be nonempty (R25). Add
  "(the set is nonempty by Theorem 3.7)".

### Editorial cuts for a journal version

These fit the journal version better than the arXiv preprint, where some of the material helps
readers; decide per venue.

- [ ] Remove the dated search diary and the arXiv-version check from the introduction, and the
  "Changes from version 1" paragraph (R23).
- [ ] Thin the [Lean] links on prose facts, such as "Its 2^n−1 factors [Lean]" and the comparison
  sentences, to one per numbered result, keeping the map of Appendix B (R23).
- [ ] Cut the "Independent validation" and machine-timing paragraphs of Appendix B (R23).
- [ ] Move the paragraph about the second Lean proof of Lemma 5.1 to Appendix B (R17).
- [ ] Shorten the abstract's description of the lower-bound mechanism to one sentence (R22).
- [ ] Turn Theorem A.8 (hyperplane covers) into a remark: in polynomial form it follows in two
  lines from Lemma 3.6 and is not needed for the upper bound (R16). Also make the appendix's
  stated upper-bound source consistent: its introduction names Theorem 3.7 or the covers, but
  Theorem A.9(2) uses Proposition 3.8.
- [ ] Remark 5.3's computational evidence is cited only through the notebook URL (R24). Archive it
  with a permanent identifier, or drop the sentence now that the theorem is proved.
- [ ] Replace the one-sentence "What does not follow" with a concluding remark that states the
  natural open question: other fields and other grids (R26).

### Outstanding before a journal submission

- [ ] An expert reads the Section 4 lower bound (C). Das or Menezes are the natural readers;
  correspondence is the author's decision.
  - A reply to Dr. Das is drafted (private, not in the repository).
- [ ] The author adds a sentence on what they checked personally to "How this paper was produced"
  (C; the shared checklist's assistance item).
- [ ] Run the Lean build outside the author's machine, for example by pointing the repository's
  Lean workflow at `claims/BinaryMultiplicityDegreePaper2.lean` (C).
- [ ] Check the chosen journal's policy on AI-assisted manuscripts (C).
