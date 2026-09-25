# Binary multiplicity degree, version 2: self-review checklist

Copied from [the shared publication checklist](../CHECKLIST.md) on 25 September 2026 and
applied to version 2 of this paper. Each item carries its disposition: **applied** (the paper
was changed), **satisfied** (checked, no change needed), **not applicable**, or
**outstanding**. A checked box records an internal check by Claude Code (Opus 5.5), not
independent review, author approval or publication readiness. The earlier referee pass and
its corrections are in [REVIEW-v2.md](REVIEW-v2.md).

## 1. Main claim and scope

- [x] **State the contribution precisely.** Make the main result easy to find in
  the title, abstract and introduction. Distinguish a new theorem, a new proof,
  an application of a known result, and an observation connecting existing work.
  — **Applied.** The title, abstract and Theorem 1.2 lead with the per-order value. The
  introduction separates what is new (the per-order value below Menezes' range, and D(n,k)
  for k < 2^(n−2)) from prior results: Menezes' range n ≥ k − 1, BBDM's covers for
  k ≥ 2^(n−2), the Schwartz–Zippel bound of the earlier note. It now also says that the case
  ℓ = k − 1 is Sauermann–Wigderson's Theorem 1.5 and is not new.
- [x] **Match every headline to the theorem.** Check all quantifiers, domains,
  encodings, inference rules, size measures and restrictions. Define what is
  counted, including initial proof-lines when relevant. Explain which restrictions
  are absent rather than relying on an unexplained adjective such as “general.”
  — **Applied.** Menezes' result now carries k ≥ 2 in the abstract and introduction. The
  abstract's description of the final step now names the lowest part of P composed with the
  local inverse (not "of the polynomial"), and its claim about links now says that an
  appendix maps every numbered result to its formal proof, since the grid-vanishing lemma
  has no link of its own. "Origin order" is defined in Definition 1.1.
- [x] **Make quantitative language unambiguous.** Give the actual bound and its
  parameter. Relate different size parameters explicitly; qualify terms such as
  “exponential” where conventions differ. Recheck abstract asymptotics after
  changing parameters or strengthening a theorem.
  — **Satisfied.** All bounds are exact formulas with their ranges; there are no asymptotic
  claims. The examples (n = 1, k = 3; n = 2, k = 5; D(n, 15) = n + 25) were rechecked.
- [x] **Separate sufficient criteria from general characterizations.** Preserve
  density factors, side conditions and unproved premises. Do not rename a
  sufficient condition as a size–degree relation, equivalence or general method
  unless that stronger assertion is proved.
  — **Applied.** "Below one block the truncated product does better", which was not proved
  as stated, is replaced by what the construction does. Every "if and only if" is either
  proved in Lean or flagged (see section 5).
- [x] **State the boundary once, where useful.** Explain the important conclusions
  that do not follow. Keep a caveat next to a statement if omitting it would
  mislead; consolidate repeated scope and novelty disclaimers elsewhere.
  — **Satisfied.** "What does not follow" (Section 5) states the binary-only scope once; the
  novelty caveat appears once, after the related work.

## 2. Attribution and literature

- [x] **Trace both the subject and the proof ingredients.** Credit the introduction
  of a system or method separately from later variants and lower bounds. Cite
  antecedents of intermediate results even when giving a self-contained proof.
  — **Applied.** Added: Legendre's formula for the 2-adic valuation of r! behind Lemma 3.2; the
  Artin–Schreier additive root behind the local inverse; Sauermann–Wigderson's Theorems 1.4
  and 1.5 (per-order values over R, and the case ℓ = k − 1 over every field); BBDM's
  refinement of covers by the origin's coverage. Already present: Menezes (truncated
  product), BBDM (hyperplane product), Alon (grid vanishing), DKSS (Schwartz–Zippel),
  Alon–Füredi (k = 1).
- [x] **Verify references against primary sources.** Check authors, titles, years,
  journal details, page ranges, identifiers and theorem numbers. Do not retain
  bibliographic details from memory or a reviewer's illustrative citation.
  — **Satisfied, with checks run on 25 September 2026:** Alon (1999) against Crossref;
  Sauermann–Wigderson Theorems 1.3–1.5 against arXiv v2; BBDM Theorem 1.2(a), Section 1.3 and
  Section 2 against arXiv v1; DKSS "Lemma 8 of arXiv v2" against the arXiv PDF. BBDM's journal
  Question 4.3, DKSS Definition 2.2 and Lemma 2.7 and Alon–Füredi's details were checked
  against the primary sources in the earlier note's audit
  ([READINESS_AUDIT.md](../binary-polynomial-multiplicity/READINESS_AUDIT.md)) and are
  unchanged.
- [x] **Use the right version.** Check revisions and corrections. Identify the
  version when numbering or statements differ, especially for a question the
  paper claims to answer.
  — **Satisfied.** Journal numbering for BBDM's question, with the arXiv v1 numbering noted;
  arXiv v1 for BBDM's theorem and sections; arXiv v2 for Sauermann–Wigderson; Menezes' arXiv
  listing checked on 25 September 2026 (version 1 only).
- [x] **Compare like with like.** Align fields, encodings, proof systems, rules,
  regularity/depth hypotheses and size parameters before comparing bounds.
  Explain why the closest prior result does not already imply the claim.
  — **Applied.** The comparison with the reals now states Sauermann–Wigderson's range
  n ≥ 2k − 3 and compares per origin order. The Menezes comparison states his range and why
  it does not reach n < k − 1.
- [x] **Qualify novelty honestly.** Distinguish established prior work from a
  potentially new formulation or proof. A bounded search with no match does not
  establish priority. Attribute reviewer opinions as opinions, not literature facts.
  — **Applied.** The ℓ = k − 1 case is now credited to Sauermann–Wigderson. The search caveat
  is kept.
- [x] **Check the relevant recent work.** Give the actual scope and date of any
  literature refresh. Do not carry forward a stale date or imply an exhaustive
  review. Use a comparison table only if verified rows improve on the prose.
  — **Applied.** The web searches are now dated (24 September 2026), and the Menezes version
  check is dated (25 September 2026). No new search was run for version 2; this is stated
  implicitly by the date. No comparison table.

## 3. Exposition for human readers

- [x] **Write the abstract in the area's vocabulary.** State the problem, exact
  result and central idea plainly. Mention formal verification accurately when
  it is part of the contribution; keep process history and repeated review-status
  notices out of the abstract.
  — **Applied** (the corrections under section 1); no process history in the abstract.
- [x] **Explain the proof before its machinery.** For a substantial argument, give
  a readable overview of the main steps, why they fit together and where the hard
  step lies. For a short deduction, a clear introductory paragraph may suffice.
  — **Applied.** The proof outline now names the hard case (q ≥ 1) and why the recursion and
  the reduction are needed there. Section 4 opens with a plan paragraph.
- [x] **Expose the conceptual center.** Name the decisive construction, invariant
  or bridge, explain why it works, and point directly to the supporting lemma.
  Distinguish nearby notions that the argument cannot interchange, such as
  equality of formal polynomials and equality of their values on a finite set.
  — **Applied.** The plan paragraph of Section 4 separates vanishing on V (values) from being
  zero (coefficients), and points to Lemma 4.6 as the bridge.
- [x] **Help readers enter the main statements.** Introduce important theorems
  with their purpose and intuition. Explain what their hypotheses accomplish.
  Expand terse nontrivial transitions rather than merely adding more references.
  — **Applied** through the plan paragraph, which says what each lemma of Section 4 contributes.
- [x] **Make the proof's structure visible.** Separate genuinely different cases;
  retain boundary and degenerate cases. Present a key chain of estimates together
  when that makes its logic easier to check.
  — **Satisfied.** Steps 1–3 of Theorem 4.7, the three cases of the reduction, and the case
  splits of Lemma 5.1 and Corollary 1.3 are displayed as lists, including n = 1 and k = 2^n.
- [x] **Use an example when it earns its space.** A small worked instance should
  explain a mechanism, translation or construction that is otherwise hard to
  follow. Do not add examples as decoration or substitute them for a proof.
  — **Satisfied.** The example n = 1, k = 3, ℓ = 0 with (1 + x)³ shows the change of form in one
  line; no further example is added.
- [x] **Explain the relation to previous methods.** Identify the obstacle being
  bypassed and the borrowed ideas. Verify characterizations of others' methods;
  do not portray an unverified interpretation as an established limitation.
  — **Satisfied.** The paper says it read Menezes' statements, not his proofs, and does not
  claim his argument is limited to his range. The borrowed ideas are credited (section 2
  above).
- [x] **Keep useful generality; move incidental generality aside.** The main
  argument should follow the setting readers need. Put optional abstractions in
  a remark or a skippable section, with their full hypotheses. Formal-library
  generality alone is not a reason to complicate the exposition.
  — **Satisfied.** The only generality beyond F₂ is in two short lemmas (integral domains in
  Lemmas 4.5 and 4.6, any field in Section 2), where it costs nothing.
- [x] **Keep supporting detail proportionate.** Retain appendices that supply
  genuinely useful proofs or verification information. Remove repetitive
  summaries and duplicated lemmas rather than cutting essential arguments.
  — **Satisfied.** The second proof (Section 6) is kept because the formal proof of Lemma 5.1
  uses it; the appendix is the verification map.

## 4. Terminology, notation and layout

- [x] **Prefer accepted terminology.** In proof complexity use “proof-lines” or
  “lines” for proof size, with the exact counting convention stated. Reserve
  “nodes” for genuinely graph-theoretic descriptions. Define necessary project
  vocabulary once and connect it to standard terms; formal declaration names
  need not dictate the paper's prose.
  — **Applied.** "Origin order" is now defined. Proof-complexity terminology is not applicable.
- [x] **Resolve overloaded symbols.** A symbol should not silently change meaning.
  Where parameters are numerous, provide one compact summary of their meanings,
  dependencies and where the main inequalities are used.
  — **Applied.** A Notation subsection (1.3) summarizes n, k, ℓ, m, q, r, h, y_i, F, g_s, x̂_K,
  w and f_d, and states that y_i is an independent variable in Section 4. In Section 6 and
  the outline, m and q no longer take other meanings (renamed M, c and n₀).
- [x] **Make tables readable.** Use adequate row spacing or restrained horizontal
  rules, sensible column widths and alignment. Check the rendered table, including
  long explanations; do not duplicate a glossary or table without a reader benefit.
  — **Satisfied.** The verification table was checked in the rendered PDF: rules, spacing and
  wrapping are readable.
- [x] **Use navigable references.** Use LaTeX labels instead of hard-coded section
  numbers. Verify cross-references after reorganization. Keep long implementation
  names and repository paths out of the proof narrative.
  — **Applied.** All references use labels; the build reports no undefined references. The two
  places with two indistinguishable "[Lean] [Lean]" links (Corollary 1.3, Theorem 6.9) now
  say what each link covers. Declaration names stay in the appendix.

## 5. Mathematical and formal-verification evidence

- [x] **Review the exact dependency chain.** Check that every invoked result has
  the required hypotheses and that every conversion preserves the claimed
  object and parameter budget. Retain original degree/cost conventions where
  simplification would otherwise conceal a loss.
  — **Satisfied** by the fresh-context referee pass ([REVIEW-v2.md](REVIEW-v2.md)) and the Lean
  proofs; no statement changed since.
- [x] **Use meaningful controls where warranted.** Known easy instances and edge
  cases can reveal a definition, scope or interpretation mistake. Describe what
  a check establishes; one toy example is not a survey of known upper bounds.
  — **Satisfied.** Edge cases n = 1, k = 2^n and ℓ = k − 1 (now matched against
  Sauermann–Wigderson's Theorem 1.5) agree; Remark 5.3 describes the finite checks as evidence.
- [x] **Separate evidence types.** Distinguish an informal proof, finite check,
  AI review, independent expert review and formal verification. Reused archived
  evidence is not a fresh run. Verification does not establish novelty or the
  correctness of the correspondence between formal and conventional definitions.
  — **Satisfied.** Sections 1.5 and 7 keep these apart; the finite checks are cited from the
  notebook, not rerun.
- [x] **If formalized, verify the actual headline.** Match the paper's definitions,
  rules, hypotheses and quantifiers to the declarations. Explain partial coverage,
  stronger assumptions, or informal additions. Audit transitive dependencies and
  distinguish proved prerequisites from custom axioms or admitted interfaces.
  — **Satisfied.** per_order_value, min_phi and degree_complete were compared with Theorem 1.2,
  Lemma 5.1 and Corollary 1.3 when they were formalized; the axiom report of the aggregate
  module is transitive and lists only the standard axioms.
- [x] **If formalized, give every boundary claim a formal statement or a flag.**
  — **Applied.** Formal: "if and only if k ≥ 2^(n−2)" (cover_bound_attained_iff) and
  "agrees with Menezes when k − ℓ − 1 < 2^n" (phi_of_lt_two_pow). Now flagged as not
  formalized: the strict comparison for k − ℓ − 1 ≥ 2^n (already flagged), the "does better
  otherwise" in the Changes paragraph, and the characterization of the extremal orders in
  Remark 5.3.
- [x] **If formalized, provide a compact verification map.** — **Satisfied.** Appendix A, with
  every cited declaration name checked by script against the Lean sources.
- [x] **If formalized, make reproduction self-contained.** — **Applied.** The appendix gives the
  repository, the pinned commit (which contains the aggregate module and all cited files),
  prerequisites, commands and the expected axiom report. Kernel-replay instructions and the
  result of a local replay are added.
- [ ] **Represent independent validation accurately.** — **Outstanding, and stated in the
  paper.** No hosted or third-party build of this paper's module exists: the repository's Lean
  CI workflow targets a different preprint. Running that workflow on this module, or an
  independent build, remains to be done.

## 6. Assistance, versions and final checks

- [ ] **Disclose assistance specifically and concisely.** — **Outstanding for the author.**
  Section 7.3 identifies the AI contributions and the AI reviews. It does not say what the
  author checked personally; only the author can state that, so no sentence was invented.
- [x] **Keep development history separate.** — **Satisfied.** Section 7 is brief; the history
  is in the linked notebook.
- [x] **Make revision identity clear.** — **Satisfied.** Version 2 with date, a "Changes from
  version 1" paragraph, and one Lean commit used consistently in the links, the commands, the
  repository citation and the README.
- [x] **Keep the submitted document sufficient for its readers.** — **Satisfied.** Proofs,
  qualifications and verification commands are in the paper; the README is a summary.
- [x] **Check the finished artifact.** — **Applied.** Every page of the rebuilt PDF was checked: no
  bad breaks, overfull boxes or broken references; one underfull box in the appendix table
  is cosmetic. Source and PDF were rebuilt together.
- [x] **Close the review honestly.** — **Satisfied** by this file: two items remain
  outstanding, and no external review, publication or author approval is implied.
