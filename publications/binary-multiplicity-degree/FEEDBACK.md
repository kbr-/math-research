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
R's numbers are given in brackets, and the item texts use the numbering of the version R read;
the notes use the current numbering. All of R's findings were applied on 25 September 2026, and
the Lean pin moved to eec3af0e.

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

### Lean links

- [x] Inline [Lean] links in the prose disrupt reading; keep them next to the numbered statements
  (A, R23).
  - Applied: every [Lean] link now sits at the end of a numbered statement. Facts that the prose
    states are mapped in Appendix B. Three facts that the proofs use became numbered lemmas with
    links: the substitution lemma (Lemma 2.3), Catalan parity (Lemma 3.5) and the local inverse
    (Lemma 4.1). The dimension-step inequalities became Remark A.7.

### Statements and attribution

- [x] The abstract's "every mathematical claim of the paper is formalized in Lean" is broader
  than true (R13). The exceptions are statements about other papers, the grid-vanishing lemma
  (Mathlib), the computational evidence of Remark 5.3, and the identification of g_s with
  Menezes' truncation. Say "every theorem, lemma and corollary", or list the exceptions.
  - Applied: the abstract says every theorem, lemma and corollary. The introduction adds the
    arithmetic facts mapped in Appendix B and names the exceptions: the grid-vanishing lemma
    comes from Mathlib, and statements about other papers are cited.
- [x] "g_s is the specialization to F₂ of the Catalan truncation of Menezes" cannot be checked
  from the paper (R14). Display Menezes' polynomial and the one-line reduction mod 2 through
  v₂(C_{a−1}) = s₂(a) − 1, or weaken the claim to "coincides with (cf.)".
  - Applied: Section 3 displays Menezes' equation (12), read in his arXiv v1 text, and reduces
    it mod 2 using the new Catalan parity lemma (Lemma 3.5).
- [x] The value n + 2k − 2 at ℓ = k − 1 is attributed to Sauermann–Wigderson within n ≥ 2k − 3 in
  one place and for every n ≥ 1 in another (R11). Harmonize: their Theorem 1.5 holds for every
  n ≥ 1.
  - Applied: the comparison with the reals gives each theorem its own range, and compares over
    F₂ in the range n ≥ k − 1.
- [x] Missing comma in "In the range n≥2k−3 k−ℓ−1<2^n" (R12).
  - Applied: the sentence was rewritten.
- [x] Bishnoi et al. are cited by journal numbering for Question 4.3 but by arXiv v1 numbering
  for Theorem 1.2(a), Section 1.3 and Section 2 (R18). Cite the published version throughout, or
  give the correspondence for every cited item.
  - Applied: the version of record (open access through the University of Birmingham portal) was
    read. Theorem 1.2 and Sections 1.3 and 2 have the same numbers there as in arXiv v1, so the
    text now cites the published version throughout. The bibliography entry records the
    correspondence, including Question 4.3 = arXiv Question 5.2.
  - Found while checking: the version of record introduces Question 4.3 as "a question of
    Sauermann and Wigderson, this time over F₂". The introduction now credits that origin.
- [x] Menezes' entry pairs identifier arXiv:2609.19009v1 (a September identifier) with the date
  14 August 2026 (R19).
  - Applied: 14 August 2026 is the submission date arXiv's abstract page shows for v1, so the
    mismatch is on arXiv's side. The entry now says "submitted 14 August 2026 according to
    arXiv".
- [x] Sauermann–Wigderson is cited only as arXiv v2 (R20). Add the journal version, J. London
  Math. Soc. 106 (2022), no. 3, 2379–2402, and check that Theorems 1.3–1.5 keep their numbers.
  - Applied: the entry cites the journal version with its DOI (10.1112/jlms.12637). The journal
    text was not accessible, so the entry states that theorem numbers are those of arXiv v2.
- [x] The abstract says the Schwartz–Zippel bound was "asked for" by Bishnoi et al.; they asked
  whether it is a lower bound for k ≥ 2^(n−2) (R22). Also, "the product of the 2^n − 1 affine
  hyperplanes" should be "of their affine forms".
  - Applied: both reworded.
- [x] "the lower bound is the case F = F₂ of [AF93, Theorem 5]": R could not check the theorem
  number from the text (R21).
  - Kept: checked against the source in the earlier note's audit
    ([READINESS_AUDIT.md](../binary-polynomial-multiplicity/READINESS_AUDIT.md)).

### Notation

- [x] δ is both the least degree δ(n,k,ℓ) and the shift vector in Lemma 4.2 (R4). Rename the
  shift vector.
  - Applied: the shift vector is γ.
- [x] s is the index of g_s, the summation index of x̂_K, the exponents s_a, the tuple in
  "τ = s" (Section 4, Step 3) and part of s₂ (R4). Rename the tuple and the exponents.
  - Applied: x̂_K sums over j, the exponents and tuple are b_a and b, and the diagonal index in
    Lemma 4.5 is ν.
- [x] w is the series of Section 4, the local sum Σa_i in the degree part of Theorem 3.4, and a
  variable in the proof of Lemma A.5 (R2, R4). Rename the latter two.
  - Applied: μ in Theorem 3.6 and z₀ in Lemma A.5.
- [x] In Definition 3.3 a_i are powers of two, but in the proof of Theorem 3.4 a is a point
  ("a_{i₀} = 1") (R2). In Appendix A, "the multiplicity at a ≠ 0 is at least a2^(n−1)+b" uses a
  for both a point and an integer (R3). Rename the powers (for example p_i) and the integer
  (k = c·2^(n−1) + b).
  - Applied: p_i in Definition 3.4; k = c·2^(n−1) + b in Remark A.9. Menezes' own integers a_i
    appear only in his displayed polynomial.
- [x] The substitution fact of Section 2 reuses z, the formal shift variable, for substituted
  elements, and is stated over F₂ although nothing depends on it (R1). State it over any field
  with a fresh letter.
  - Applied in part: it is now Lemma 2.3 with the letter ζ and a proof. It stays over F₂, where it
    is used and where its Lean statement lies.
- [x] z^β in the proof of Theorem A.6 is a monomial in x′, not in the shift variable (R4).
  - Applied: (x′)^β.
- [x] The outline writes S = P(x′,0) + P(x′,1); Appendix A uses Q(0,x′) + Q(1,x′) after a change
  of coordinates (R6). Make them agree.
  - Applied: the outline uses Q = P∘A and Q(0,x′) + Q(1,x′).

### Proofs and exposition

- [x] The outline calls w "one power series" and x̂ an infinite series; the proof uses the
  polynomial truncation x̂_K with K = k, and w is a polynomial (R5). Say "truncated".
  - Applied.
- [x] Appendix A, proof of Theorem A.6: "for otherwise S = 0, which the next item excludes"
  refers to the wrong item (the fourth one excludes it), and deg S ≤ deg Q − 1 needs S ≠ 0
  (R7).
  - Applied: the degree item now comes last and uses S ≠ 0, established by the item before it.
- [x] The remark "D(n−1,k) ≤ D(n,k) − 1" sits between Theorem A.6 and its proof (R8). Move it
  after the proof.
  - Applied: it is Remark A.7, after the proof.
- [x] Unneeded hypotheses (R9): Lemma 4.3 needs only 2^K ≥ k > ℓ, not the multiplicity condition
  at nonzero points; Lemma 4.4(2) does not need t < k; Lemma 4.6 does not need V nonempty. State
  the minimal hypotheses or add a remark.
  - Lowest part (now Lemma 4.4): restated without the condition at nonzero points. Its Lean
    statement never had that condition.
  - Grid reduction (now Lemma 4.7): "nonempty" dropped in the paper and in Lean. The Lean
    `coeff_reduction` handles V = ∅ by a case split; the earlier statement is kept as
    `coeff_reduction_of_nonempty` (commit eec3af0e).
  - Forms, part 2 (now Lemma 4.5): t < k kept. The Lean statement writes the degree k − 1 − t in
    natural numbers, which truncates to 0 for t ≥ k, so there the hypothesis is needed. The paper
    notes that t < k is the only case used. The unused-variables linter cannot flag any of these:
    the Lean proofs used the hypotheses, and a hypothesis that is not needed mathematically is
    not unused syntactically.
- [x] "D(n,1) = n for n ≥ 2": the corollary also gives D(1,1) = 1 (R10). Drop the restriction or
  say it is there for the comparison with Alon–Füredi.
  - Applied: the examples are stated in the range n ≥ ⌊log₂k⌋ + 2 of the logarithmic formula, and
    the Alon–Füredi comparison says n ≥ 2 is where k = 1 < 2^(n−1).
- [x] Section 3's sentence "It works in every dimension, with the digit-sum bound, also when
  k−ℓ−1≥2^n, where Theorem 3.7 has degree below that bound" is hard to parse (R15). Suggested:
  "Proposition 3.8 holds in every dimension; when k−ℓ−1 ≥ 2^n its degree bound exceeds Φ."
  - Applied.
- [x] "the grid-vanishing lemma … for a grid of 2^n polynomials" is opaque in the introduction
  (R21). Say "a grid V^h with V ⊂ F₂[y] of size 2^n".
  - Applied.
- [x] δ(n,k,ℓ) is defined as a least degree before the set is known to be nonempty (R25). Add
  "(the set is nonempty by Theorem 3.7)".
  - Applied, in Definition 1.1.

### Editorial cuts

- [x] Remove the dated search diary and the arXiv-version check from the introduction, and the
  "Changes from version 1" paragraph (R23).
  - Applied. One sentence keeps the search's scope and date, as the shared checklist requires. The
    version history is one sentence in "How this paper was produced".
- [x] Thin the [Lean] links on prose facts to one per numbered result, keeping the map of
  Appendix B (R23).
  - Applied; see "Lean links" above.
- [x] Cut the "Independent validation" and machine-timing paragraphs of Appendix B (R23).
  - Applied. The kernel-replay command stays.
- [x] Move the paragraph about the second Lean proof of Lemma 5.1 to Appendix B (R17).
  - Applied, together with the Lean encoding of g_s and the note on the DKSS proof.
- [x] Shorten the abstract's description of the lower-bound mechanism to one sentence (R22).
  - Applied.
- [x] Turn Theorem A.8 (hyperplane covers) into a remark: in polynomial form it follows in two
  lines from Lemma 3.6 and is not needed for the upper bound (R16). Also make the appendix's
  stated upper-bound source consistent: its introduction names Theorem 3.7 or the covers, but
  Theorem A.9(2) uses Proposition 3.8.
  - Applied: Remark A.9 with its short proof; the appendix introduction names Proposition 3.9 for
    k < 2^(n−1) and the covers for k ≥ 2^(n−1).
- [x] Remark 5.3's computational evidence is cited only through the notebook URL (R24). Archive it
  with a permanent identifier, or drop the sentence now that the theorem is proved.
  - Applied: dropped; the computations remain in the notebook.
- [x] Replace the one-sentence "What does not follow" with a concluding remark that states the
  natural open question: other fields and other grids (R26).
  - Applied: Remark 5.4.

### Second blind referee pass

A second fresh Claude Opus 5.5 agent reviewed the version tagged
`binary-multiplicity-degree-preprint-2026-09-25-rev1` (commit edabe475) under the same brief
(R2, 25 September 2026). It found no mathematical gap. It re-derived by hand the inversion in
Lemma 4.3, the diagonal recursion in Lemma 4.5, the case split in Step 3 of Theorem 4.8 and the
case analysis in Lemma 5.1. Numbers are those of the version it read.

- [x] Quote Question 4.3 of Bishnoi et al. verbatim, with its multiplicity convention (R2-1,
  marked major). A referee may doubt that an open question is answered in two lines from the
  multiplicity Schwartz–Zippel lemma. If the quotation matches, say plainly that the answer is
  immediate. In the abstract, make clear that only the "only if" direction of the attainment
  criterion is new.
  - Note: the paraphrase was checked against the version of record on 25 September 2026 and
    matches, including "multiplicity at most k − 1 at the origin".
  - Applied in revision 2: the introduction says the bound is a direct application of the
    multiplicity Schwartz–Zippel lemma, that their covers attain it for k ≥ 2^(n−2), and that
    what was open is k < 2^(n−2), where Corollary 1.3 shows it is not attained. The abstract says
    the same. Not quoted verbatim: the paraphrase is exact.
- [ ] Menezes' identifier arXiv:2609.19009 is a September identifier but the entry gives
  14 August 2026 (R2-2). Also: the key SW20 labels a 2022 article, and the [Note] URL points to
  `tree/main` instead of a pinned commit.
  - Note: the date is the one arXiv shows, and the entry now says so. The key and the unpinned
    URL still need fixing.
- [ ] Lemma 3.1(2) is proved only by "Mathlib proves it for every base" (R2-3). Give the
  one-line induction s₂(m) = (m mod 2) + s₂(⌊m/2⌋) ≤ 1 + ⌊m/2⌋ ≤ m.
- [ ] Move Lean-motivated remarks out of the mathematics to Appendix B (R2-4): the Lean encoding
  of mult after Definition 2.1; the remark on t < k after Lemma 4.5; "Mathlib proves this lemma"
  after Lemma 4.6; the V = ∅ case in the proof of Lemma 4.7, which the argument never uses.
- [x] The result may hold over every field of characteristic 2 (R2-5). The expansion and the
  congruence use only shifts in {0,1}ⁿ, the forms need only Frobenius additivity, V stays the
  F₂-span in an integral domain, the construction has F₂ coefficients, and multiplicity does not
  change under field extension. State it, or say why not.
  - Note: a stronger theorem if true; it needs a written proof and a Lean generalization first.
  - Applied: proved by a descent to F₂ (an additive map R → F₂ applied to the coefficients), for
    every commutative ring of characteristic two, and verified in Lean (PerOrderCharTwo.lean,
    commit 7fc6175b). The paper states it as Lemma 5.4 and Theorem 5.5, and the abstract and
    introduction mention it.
- [ ] Lemma 3.5 (Catalan parity) is used only for the comparison with Menezes' truncation
  (R2-6). Demote it to a remark with its citations, or say that it serves only that comparison.
  Explain the restriction "for s ≥ 2" (Menezes' own range), and define v₂ and C_a.
- [x] Say exactly what is taken from Menezes (R2-7). "A short self-contained proof that the
  truncation works in every dimension" can read as a correction of Menezes; cite his statement
  (equation or theorem number) and its range.
  - Note: Menezes' Theorem 3.2 states the Catalan truncation for every s ≥ 2 and n ≥ 1, so the
    truncation is his in every dimension; the sentence must not suggest otherwise.
  - Applied in revision 2: the introduction credits his Theorem 3.2 (vanishing in every
    dimension) and Section 8 (degrees of his basis elements, including y₁^ℓ ĝ_{k−ℓ} for
    ℓ ≤ k − 2, for all n), says only his exact minimum needs n ≥ k − 1, and calls the telescoping
    proof an alternative. Section 3 says Proposition 3.9 is his result specialized to F₂.
- [x] Comparison with the reals: "lower by s₂(k−ℓ−1) − 1 ≥ 0" is not lower when k − ℓ − 1 is a power
  of two (R2-8). Say "at most the real value, and strictly lower unless k − ℓ − 1 is a power of
  two". The Sauermann–Wigderson real result appears three times with Theorems 1.3 and 1.4; check
  the numbers and merge the passages.
  - Applied in revision 2: "at most the real value n + 2k − 3, and strictly lower unless k − ℓ − 1
    is a power of two; for ℓ = k − 1 it is n + 2k − 2, as over the reals". Merging the three
    passages is left for the journal version.
- [ ] The abstract's "span of x₁² + x₁, …, xₙ² + xₙ" should be the span of y₁, …, yₙ with yᵢ standing
  for xᵢ² + xᵢ (R2-9).
- [ ] Notation (R2-10): y means x² + x in Section 3 but an independent variable in Section 4; σ is
  both an index set and a set of variables; n is reused in the proof of Lemma 3.5; Y is both the
  variable of x̂_K and L_V and the arguments of E^(t)_j; h is the number of parts, the number of
  grid variables and the function in Lemma 5.1.
- [ ] Lemma 4.4 states x̂_k but the note and proof use K with K = k (R2-11). Use one symbol.
- [ ] The abstract and the introduction disagree on what is formalized (R2-12): the introduction
  adds propositions and excepts the grid-vanishing lemma. Make them agree.
- [ ] Length and journal fit (R2-13): Appendix A and the version history belong in the arXiv
  comments or the repository; Appendix B's table and commands, the "Formal verification"
  subsection and the dated search sentence could be supplementary material; the Menezes
  comparison appears three times.
  - Note: the dated search sentence is required by the shared checklist; keep it in some form.
- [ ] Mention Corollary 5.2 next to Corollary 1.3, since the logarithmic formula holds up to
  k < 3·2ⁿ⁻¹, or give one closed form (R2-14, optional).
- [ ] Remark 5.3 describes the extremal orders only for k ≤ 2ⁿ (R2-15). Give the maximizers the
  proof of Lemma 5.1 finds for k > 2ⁿ: m = Q·2ⁿ + 2^λ − 1, and m = Q·2ⁿ − 1 when λ ≤ n − 2.
  - Note: needs a Lean statement if added.
- [ ] Alon's Lemma 2.1 is stated over a field, while the paper applies it over the integral
  domain F₂[y] (R2-16). Say "pass to the fraction field", or rely on the included proof, which
  works over any integral domain.

### Outstanding before a journal submission

- [ ] An expert reads the Section 4 lower bound (C).
- [ ] The author adds a sentence on what they checked personally to "How this paper was produced"
  (C; the shared checklist's assistance item).
- [ ] Run the Lean build outside the author's machine, for example by pointing the repository's
  Lean workflow at `claims/BinaryMultiplicityDegreePaper2.lean` (C).
- [ ] Check the chosen journal's policy on AI-assisted manuscripts (C).
