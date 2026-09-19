# Version 1

- [x] A reader from the area noted a lack of attribution in the bibliography: Khaniki proved the first superlinear lower bound for this system, and Tzameret co-authored strong lower bounds for a similar system that, as the reader recalled, sums over the reals instead of modulo 2. Verify both against the sources and cite them.
  - Revision 1: verified against the sources. Khaniki (ACM TOCL 2022) proves almost quadratic dag-like bounds for resolution over low-degree polynomial equations over finite fields; Part–Tzameret (ITCS 2020, Comput. Complexity 2021) prove the first superpolynomial dag-like Res(lin) bounds, exponential for subset sum over the rationals. Both cited in the new related-work paragraphs of Section 1.

The items below come from two Claude review conversations about the preprint, referred to as C1 and C2. Their claims about the literature and venues are unverified reviewer comments, not an independent review.

### Attribution and related work

- [x] Cite the Res(lin) lineage: Raz–Tzameret (2008) and Part–Tzameret on dag-like Res(lin) lower bounds (C1, last answer; overlaps the first item, as does Khaniki's first superlinear bound).
  - Revision 1: done (RT08, PT21, Kha22). Raz–Tzameret page numbers were entered from memory; double-check.
- [x] Cite Razborov's 1998 PC lower bound for PHP, which Section 3 and Appendix A parallel; add a sentence on Impagliazzo–Pudlák–Sgall, Alekhnovich–Razborov, and Mikša–Nordström (C1).
  - Revision 1: done (Raz98, IPS99, AR03, MN15). Bibliographic details of these four were entered from memory, not re-fetched; double-check.
- [x] State explicitly whether Theorem 3.2 (moment extension) is new or a new proof of a known result (C1).
  - Revision 1: a paragraph before the theorem (now 4.2) says the degree range is Razborov's and is not claimed as new; only the proof via chessboard homology is claimed, with a hedge that no exhaustive search for the extension formulation was made.
- [x] Check recent Res(⊕) work for omissions: Alekseev–Itsykson lifting, Efremenko–Itsykson amortized closure, Gryaznov–Pudlák–Talebanfard, Efremenko–Garlík–Itsykson 2026; a grouping sentence may suffice (C1).
  - Revision 1: AI25, EI25, GPT22 verified and cited. No "Efremenko–Garlík–Itsykson 2026" paper was found; the closest match, Efremenko–Itsykson "Strong ETH holds for bounded-depth Res(⊕)" (STOC 2026), is cited as EI26. Author: confirm this is the paper C1 meant.

### Exposition

- [x] Add a roughly two-page proof overview after the introduction (it should also announce the exponential bound and the generic criterion once they are in), in words: why affine extension blocks cost constant degree, why one weighted substitution removes them, why the target is a nonzero polynomial rather than 1, where the rank threshold comes from, why depth never enters (C1, C2 step 4). C2 notes this is effectively required for ECCC.
  - Revision 1: new Section 2 (`sections/01b-overview.tex`).
- [x] Rewrite the abstract in standard vocabulary, state plainly that the main theorem itself is formalized, drop "not yet peer reviewed" from the abstract only (C2 gives a draft); the statement stays in the Section 8 disclosure and the title-page note. Decided: fold the framework mention into the single closing AI-assistance sentence, e.g. "The proof was developed with substantial AI assistance within an open research framework described in Section 8." The small note below the author name ("with substantial...") stays.
- [x] Replace notebook jargon with standard terms or define it once: "complete affine extension blocks", "accuracy-h", "companions", "old base", "row-linear old-base consequence", "registry/slots", "residual NS transport" (C1).
  - Revision 1: terminology subsection in Section 2; "residual NS transport" replaced by the explicit argument in the proof of Theorem 5.7 (4.7 in version 1). The terms themselves are kept in the body because the Lean statements use them.
- [x] Fix overloaded notation (N is both unary columns and registry slots) and add one parameter summary relating k, B, D, h, s, t, r (C1).
  - Revision 1: registry slot count renamed to N_reg; parameter table in Section 2.
- [x] Add a paragraph of intuition before each main theorem in Sections 4–6 and expand terse steps, e.g. the proof of Theorem 4.7 (C1).
  - Revision 1: paragraphs before Theorems 4.2 and 5.7, Lemma 6.4, in Section 6.2, and before Theorem 7.8 (version-1 numbers 3.2, 4.7, 5.4, 5.2, 6.8; the new overview shifted all sections by one); the proof step in Theorem 5.7 is expanded.
- [x] Add one worked small example: a single resolution step through the simulation, or one high-rank block being removed (C1).
  - Revision 1: one resolution step at accuracy 1, in Section 2.
- [x] Move formalization-driven generality ("over any field", "no finite-dimensional hypothesis", exact vs upper-bound degrees) into remarks or leave it to the Lean files; keep generality that the paper or a planned extension uses (C1).
  - Revision 1: one Remark in Section 2 replaces the scattered sentences; lemma-specific hypotheses that the proofs use were kept.
- [x] Consolidate the scattered scope and novelty caveats so they do not interrupt the argument (C1).
  - Revision 1: partly: novelty and scope caveats are now in the Scope paragraph of Section 1 and in "What does not follow" (generic section); the stray remarks after Lemma 2.2 and Corollary 3.3 (version-1 numbers) and the obsolete "no exponential bound is asserted" were removed. Section 8.1 "What the conclusion uses" was shrunk to one short remark pointing to the overview (author's decision).
- [x] Explain why prior approaches stalled and which step bypasses the obstacle; connect explicitly to the 1996 extension-variable method (BIKPRS) and Razborov-style degree bounds (C1).
  - Revision 1: last subsection of Section 2, hedged with "as we understand". Author or an expert should check the characterization of the closure/lifting papers.
- [x] Possibly shorten Section 2 to brief preliminaries (C1). Decided: Appendix A stays; it is a real service (C2), despite C1's suggestion to cut it.
  - Revision 1: not shortened beyond removing the generality sentences; Appendix A kept.

### Section 8 and AI disclosure

- [x] Condense Section 8.3 to one paragraph that keeps the honest disclosure: models used, GPT-6 Astra as main contributor to version 1, the author's contribution, that the author did not check the mathematics and relies on Lean, formalization scope, no peer review (C1 gives a draft). Do not soften it into vagueness (C2).
- [x] Disclose Claude Fable 5.1's role in revision 1, in the same paragraph and consistently with the title-page note: it formalized the exponential corollary and the generic criterion (statements and proofs, with one proof batch delegated to Claude Opus 5), triaged this feedback, and will draft the revised text. The author again did not check the mathematics and relies on Lean.
- [x] Move the development story (subscription plans, usage limits, model frustrations, classifier episode, prompt history) out of the paper to a permanently linked document: fixed Git commit, Zenodo, or Software Heritage; a personal website only as a convenience link (C1).
  - Revision 1: moved verbatim to `DEVELOPMENT_HISTORY.md`, linked from the paper together with the version-1 source at fixed commit b47e9b1. Author: archive on Zenodo or Software Heritage if a DOI is wanted.
- [x] Consider a separate Noemesis writeup for the framework, later (C2 step 8). Until it exists, Section 8 keeps its short description of the framework (8.2), which the abstract's closing sentence points to; only the development story of 8.3 moves out.
  - Decided by the author: deferred on purpose. A framework whitepaper should come only after a track record of several solved open problems; until then Section 10.2 of the paper is the description.

Note, not a task: ECCC requires submissions to be understandable by researchers in the area; the overview, abstract, and Section 8 items above serve that criterion (C2).

### Mathematical content

- [x] Exponential corollary S > exp(n/(32768 ℓ²)) (C1, C2). Decided: formalization is a prerequisite.
  - [x] Formalized in Lean for every ℓ ≥ 32, with a base-two form: `formalization/claims/BitPHPExponential.lean`, notebook `#lean-bit-PHP-exponential`. The explicit threshold replaces "sufficiently large".
  - [x] Add it to Section 7 with the constant and threshold, and update the abstract and headline to "exponential".
    - Revision 1: it is now Theorem 1.1 (the old statement became Corollary 1.2), proved in Section 7; title and abstract say "exponential".
- [x] Generic subspace-consequence theorem: decided against C2's separate companion note; state it as a section or remark in this paper (around Section 7.1). Phrase it as a "sufficient condition", never as a size–degree or size–width tradeoff, and keep the {x, x²−x} caveat next to it. Decided: formalize it in Lean before mentioning it in the paper.
  - [x] PC-level theorem formalized over F₂ for arbitrary variables, base, accuracy and subspace: `GenericAffineSubspaceConsequence.lean`, notebook `#lean-generic-affine-subspace-consequence`.
  - [x] Proof-size form formalized: generic clause-polynomial bridge through 2h+w, transfer with 3S+t slots and degree max(2h+w, 4h+1), and dim U ≤ (3S+t)·C(v−(h(k+1)+1)+k, k) for a separated U: `GenericCNFSubspaceCriterion.lean`, notebook `#lean-generic-CNF-affine-DAG-subspace-criterion`. Decided to formalize this so the paper can speak about refutation size, not only PC.
  - Placement, to reconcile this with the "generality breaks the flow" item under Exposition: that item is about incidental generality inside the main argument, and C1 itself recommended giving one general framework theorem its own section instead. So Sections 2–6 stay concrete (bit PHP, F₂, the row-linear space) and lose their scattered generality remarks; the generic material goes into one short, skippable section after the main theorem, roughly two pages: the criterion, the density form, the caveats, and links to the Lean files, with proofs given by reference to the bit-PHP proofs they abstract. The headline and abstract stay about bit PHP. This also answers C2's worry about enlarging the review surface.
  - [x] Write the section. The pointer sentence can now say that Sections 5–6 are generic for any clause set whose clause polynomials are axioms of the base; what is specific to bit PHP is the separation Theorem 4.7 over the compact base and the bridge to it. State that no other formula is shown to admit a separated subspace, and that everything is over F₂.
    - Revision 1: new Section "A generic sufficient condition" after the main proof.
  - [x] Density form formalized: dim U ≤ (3S+t)·C(v+k,k)·exp(−hk²/(v+k)) under h(k+1)+1 ≤ v, i.e. 3S+t ≥ δ·exp(hk²/(v+k)) with δ = dim U / C(v+k,k): `GenericCNFDensityBound.lean`, notebook `#lean-generic-CNF-density-exponential-form`. Use this instead of the bare shape below; it makes the needed density of U explicit.
  - [x] Short-proof control formalized ({L, 1−L} in the base leaves no nonzero separated subspace): `ShortProofControl.lean`, notebook `#lean-generic-criterion-short-proof-control`. It is a consistency check on one trivial family, not an audit of known short Res(⊕) refutations.
- [x] Optional remark on formulas with short Res(⊕) refutations (C1, C2). The reviewers proposed this as a stress test of an unverified argument (C1 tried Tseitin and graph ordering; neither breaks it). Now that the criterion is Lean-verified, such a test cannot refute it; what remains is its contrapositive, which may deserve one sentence: a formula with a size-S refutation admits no separated degree-k subspace of dimension above (3S+t)·C(v−(h(k+1)+1)+k, k). The formalized {L, 1−L} control is the trivial instance. No experiment is required for the revision; a systematic look at known Res(⊕) upper bounds is separate research.
  - Revision 1: Remark on formulas with short refutations in the generic section.
- [x] Say plainly what does not follow: unary PHP (recommended wording: no sufficiently dense separated subspace is known for it; C2's quantitative density explanation is unchecked and would need its own proof before it may be stated), a Res(⊕) size–width relation, and the AC0[p]-Frege goal where nested blocks have no removal step (C2).
  - Revision 1: subsection "What does not follow".
- [x] Candidate material for that section or remark, only where checked: the general shape S ≥ exp(Ω(d²/(h·v))) (do not state it bare: it hides the density factor δ and the unformalized substitution k ≈ d/(4h); use the verified density form above), the succinct-encoding observation (only in the hedged form of the previous item), other succinctly encoded principles, Res(lin) over F_p, and the CDCL-with-XOR reading (C2). These are reviewer suggestions, not checked claims.
  - Revision 1: only the verified density form is stated; the other suggestions get one sentence saying they were not examined.
- [x] If notebook text from the 16 September assessment migrates into the paper, attribute it plainly as feedback from an AI review (Claude Fable 5.1), never in a way that suggests a human reviewer. C2 advised omitting the model name; decided to name it.
  - Revision 1: the generic section states that the criterion was first extracted in an AI review by Claude Fable 5.1.

### Versioning and verification

- [ ] Add a version marker and date near the title ("revision 1, DATE"); add the ECCC report number once assigned; mention mathematical changes in the introduction, and any error correction explicitly (C1).
  - Revision 1: "Preprint, revision 1, 17 September 2026" and a "Changes in revision 1" subsection. ECCC number still to be added once assigned.
- [x] Update the cited Lean commit hash everywhere (it must include the five new modules above) and state which commit the revision corresponds to; either keep or genuinely redo the "literature refresh of 15 September 2026" rather than carrying a stale date (C1).
  - Revision 1: all [Lean] links pin b47e9b1; Section 10.1 names 54f0937 for version 1 and b47e9b1 for revision 1. Novelty searches were genuinely redone on 17 September 2026 and the text names both dates.
- [ ] Make independent verification trivial: a one-line verify script at the top of the README with the expected `#print axioms` output, a public green CI run, and a tagged release for a stable reference (C2 step 5). Check what already exists; the hosted Lean workflow is now manual-only.
  - Revision 1: verify command and expected axiom line added to the publication README. Not done, author decisions: a public green CI run (the hosted workflow is manual-only and targets only `claims.BitPHPSuperpolynomial`) and a tagged release.
  - Later author clarification: the submission is a self-contained paper with no supplementary README. Put the reader-facing verification instructions and expected output in the paper itself; the existing repository README is not a substitute. See the focused reproduction item below.
- [ ] Get the formalization built and its axioms printed by an independent party (C1).
- [ ] Ask an independent Res(⊕) expert to check that the Lean definitions are the standard system (`AffineDAGRegistry.lean`, `BitPHPInitialBridge.lean`, top-level statement: arbitrary affine pivots, unrestricted semantic weakening, size as node count, BPHP encoding, axiom report). Do this first, without waiting for the rewrite (C2 step 1).

# Revision 1

Items from a further Claude review conversation of revision 1 (an AI review, not an independent one). It also rechecked the arithmetic of the new Section 8 proof and of the density corollary and found no problem.

- [x] Error in the abstract: "at degree o(n)" was true of version 1's parameters only; with k ≈ n/(32ℓ) the degree B = k(D+1) is about 3n/8. Replaced by "at degree at most n/2". The o(n) in (8.1) belongs to the corollary's smaller k and stays.
- [x] Run `leanchecker --fresh` on the modules behind Theorem 1.1 and Section 9 and update Section 10.1, so the strongest evidence attaches to the headline statement.
- [x] "Exponential" in the title: some readers reserve it for 2^Ω(n). Options: "nearly exponential", or the bound itself in the title. Decided by the author: keep "exponential" with a clarifying sentence.
  - Revision 1: title unchanged; a sentence after Theorem 1.1 now says the bound is 2^(L^(1/3−o(1))) in the formula size L and that no 2^Ω(L) or 2^Ω(n) bound is claimed.
- [x] Strengthen the short-refutation remark with Tseitin formulas: the clause polynomials derive one at the maximum vertex degree, so no nonzero space is separated. Added with its two-line argument, marked as not formalized.
- [x] Decided by the author: keep the notebook vocabulary, defined once in Section 2.5; it is part of the paper's character. Suggestion was: terminology, if revised again: "extension axiom" for companion and "block family" for registry, keeping the notebook names in parentheses for the Lean links.
- [x] Citation key [BIKPRS] lacked a year; now [BIKPRS96].

### From an expert asked for arXiv endorsement (18 September 2026)

An expert in the area, asked to endorse the arXiv submission, wants time to read and check the argument before deciding. He raised one correction:

- [x] The introduction says Res(⊕) "was introduced by Itsykson and Sokolov". This overlooks Raz–Tzameret (2008), which introduced resolution over linear equations under an essentially equivalent definition, formulated over the integers; Itsykson and Sokolov subsequently studied the tree-like F₂ version, resolution over parities. Cite both and say, for example, that resolution over linear equations was introduced by Raz and Tzameret and that its F₂ version, resolution over parities, was subsequently studied by Itsykson and Sokolov in the tree-like setting. The same sentence pattern occurs in the abstract's first line ("extends resolution by allowing …") and in the related-work paragraph, which already credits Raz–Tzameret; make all three consistent.
  - Revision 2: corrected the introduction and related-work attribution, and aligned the abstract’s description. Primary-source records for RT08 and IS20 support the distinction between the integer formulation and the subsequent tree-like F₂ work.

### From a ChatGPT review of revision 1

Triaged from the author's additional conversation excerpt. These are AI reviewer
suggestions, not an independent mathematical or literature audit. Checked items
below mean completed, already covered, or explicitly declined; revision-2
implementation notes distinguish these outcomes. The optional literature table
was not adopted; declaration names in the new verification map were checked
against the pinned Lean sources.

#### Focused follow-up edits

- [x] Make the common-kernel argument easier to find as the conceptual center of
  the proof: many high-rank affine restrictions → one common low-degree
  polynomial → weighted elimination. Section 2 already explains this and
  Section 5 has an “Idea of the common kernel” paragraph. Strengthen their
  signposting and cross-reference the affine-exclusion theorem; a wholesale
  restructuring or an additional novelty claim is unnecessary.
- [x] Emphasize the exact bridge from restriction to elimination in the overview:
  **zero ordinary polynomial restriction**, not just vanishing at F₂ points,
  gives `f = Σ a_i g_i` with `deg a_i ≤ k−1`. Cite the existing standalone
  “Ordinary restriction dimension and ideal membership” lemma directly at that
  step. The lemma already states and proves the distinction; no duplicate boxed
  lemma is needed.
- [x] Make the three removal cases visually explicit in Section 5: low rank
  uses packing; high rank with one in the input span uses a constant substitution
  making the product zero; proper high rank uses the common kernel and bounded
  cofactors. The weighted-removal proof already handles all three. Explain once
  that properness makes the zero flat nonempty and its codimension equal to the
  input-span rank, and that `3ℓ(k+1)+1` is the integer threshold for
  `r > 3ℓ(k+1)`.
- [x] Extend the existing parameter table with where the conditions are used,
  rather than adding a second symbol glossary: `m ln(4M) ≤ k²` and `k ≤ m`
  for the kernel estimate, `D ≥ 2h+1` for removal, `B = k(D+1)` for its output
  degree, `4(k−1) < n` for cube separation, and `2B−1 ≤ n` for the old-system
  moment/separation range. Keep `n = 2^ℓ` explicit and use the actual theorem
  hypotheses rather than the excerpt's compressed formulas.
- [x] Add a compact formal-verification map in the paper's verification section
  or an appendix: paper label → pinned Lean file → exact declaration
  and scope. Prioritize the common kernel, bounded-cofactor ideal membership,
  cube degree drop/coefficient isolation, matching extension and filling,
  clause simulation, and headline theorem. Existing per-statement [Lean] links
  already supply much of this; verify declaration names from source rather
  than copying the review's illustrative names. Keep Lean details out of the
  proof narrative and link to the map there.
- [x] Include a self-contained reproduction guide in the paper's verification
  section or an appendix: repository URL, clone → immutable checkout → setup →
  verify commands, required prerequisites, expected axioms, and the fresh-replay
  command. The existing repository README supplies some of this material, but
  the submission must not require a supplementary README. Resolve
  the version distinction explicitly: the cited theorem sources are pinned to
  `b47e9b1`, but `claims/BitPHPPreprintRevision1.lean` was added later, so that
  aggregate command needs a pinned commit containing it. This refines the
  existing reproducibility item; it does not require a new build merely to
  record this feedback.
- [x] Optional: summarize the existing related-work prose in a small comparison
  table if it improves scanning. Give each row its citation, exact formula,
  inference system, regularity/depth restrictions, and bound with its size
  parameter. Do not copy the excerpt's placeholder rows or presume all prior
  results concern standard bit-PHP. Verify those facts against primary sources
  when preparing the table; omit tree-like or other restricted variants unless
  they materially clarify the comparison. Coordinate with the expert's pending
  attribution correction above.

#### Already covered or not adopted

- [x] Retitle with “superpolynomial” instead of “exponential”: not adopted.
  This conflicts with the author's explicit decision above. Keep the title and
  the existing clarification after Theorem 1.1: the bound is
  `2^Ω(n/log² n)`, or `2^(L^(1/3−o(1)))` in formula size, with neither
  `2^Ω(n)` nor `2^Ω(L)` claimed. The reviewer is right to insist on the
  parameter distinction; the current text already supplies it.
- [x] State the system and unrestricted scope prominently: already covered by
  the introduction's displayed rules, arbitrary affine pivots, semantic
  weakening, DAG node count, and explicit absence of regularity and proof-depth
  restrictions. Theorem 1.1 and the scope paragraph state the result. Preserve
  that precision; no second headline theorem or expanded catalogue of systems
  is needed.
- [x] Give the dimension argument in one uninterrupted calculation: already
  present in the common-kernel proof, including the binomial comparison,
  exponential factor, and total image dimension at most one quarter of the
  lower bound for `dim L_k`. Preserve the separate `r_* > v` case; the review's
  compressed display is not a replacement for the proof.
- [x] State that the homological prerequisites are proved, not axiomatized:
  already explicit in Section 10.1, which names the chessboard filling theorem
  and reports no custom axiom or unproved chessboard interface. Appendix A and
  the existing Lean links support this. The verification map can make it easier
  to locate without adding another assurance to the mathematical narrative.
- [x] Globally replace “affine polynomial” with “affine-linear polynomial”:
  unnecessary as a blanket edit. The affine input tuples and affine forms are
  defined in context; use “affine-linear” selectively if a particular sentence
  could be confused with a general polynomial on an affine space. Retain the
  author's earlier terminology decision.

### From the author: parameter-table readability

- [x] Increase the vertical whitespace between rows of the parameter table in
  Section 2. The current rows are hard to distinguish. Prefer extra row spacing
  over horizontal rules between every row, retaining the existing table rules.
  Check readability in the rendered PDF when implementing this change, including
  any added explanations of where parameter conditions are used.

### From the author: self-contained submission

The paper will be submitted as a self-contained document; there will be no
supplementary README. Include the verification map and reproduction instructions
in the paper or its appendices. Pinned links to the formal proof sources remain
appropriate, but reader-facing explanations must not be delegated to a README.

### Revision 2 implementation (19 September 2026)

- Applied the common-kernel signposting, explicit ordinary-restriction/cofactor
  bridge, and three-case removal presentation in the overview and affine-exclusion
  section. The rank/codimension and integer-threshold explanations are explicit.
- Increased vertical spacing in the symbol table and added a separate compact
  condition/use table with matching spacing. Section references use LaTeX labels;
  the feedback's earlier section numbers were not all current.
- Added Appendix B within the paper: a map to exact formal declarations and a
  complete pinned checkout/setup/build/axiom-check/kernel-replay procedure. At the author’s request, all current theorem links and reproduction instructions
  use `8904bf09`, which contains the aggregate module. No supplementary README is required.
- Did not add the optional related-work comparison table: the existing prose
  preserves distinctions among formulas, rules, and restrictions better than
  the review's placeholder rows. The attribution correction was source-checked;
  no new broad novelty audit is claimed.
- Retained the title, its quantitative clarification, and the established
  terminology. Existing independent-expert review and ECCC-number items remain
  outstanding; this editorial revision does not claim to satisfy them.
- Revision 2 uses the local annotated tag `bit-php-preprint-2026-09-19`
  after its PDF and checkpoint review. No publication or hosted CI run is part
  of this revision task.
