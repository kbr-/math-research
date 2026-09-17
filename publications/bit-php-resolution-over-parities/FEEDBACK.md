# Version 1

- [ ] A reader from the area noted a lack of attribution in the bibliography: Khaniki proved the first superlinear lower bound for this system, and Tzameret co-authored strong lower bounds for a similar system that, as the reader recalled, sums over the reals instead of modulo 2. Verify both against the sources and cite them.

The items below come from two Claude review conversations about the preprint, referred to as C1 and C2. Their claims about the literature and venues are unverified reviewer comments, not an independent review.

### Attribution and related work

- [ ] Cite the Res(lin) lineage: Raz–Tzameret (2008) and Part–Tzameret on dag-like Res(lin) lower bounds (C1, last answer; overlaps the first item, as does Khaniki's first superlinear bound).
- [ ] Cite Razborov's 1998 PC lower bound for PHP, which Section 3 and Appendix A parallel; add a sentence on Impagliazzo–Pudlák–Sgall, Alekhnovich–Razborov, and Mikša–Nordström (C1).
- [ ] State explicitly whether Theorem 3.2 (moment extension) is new or a new proof of a known result (C1).
- [ ] Check recent Res(⊕) work for omissions: Alekseev–Itsykson lifting, Efremenko–Itsykson amortized closure, Gryaznov–Pudlák–Talebanfard, Efremenko–Garlík–Itsykson 2026; a grouping sentence may suffice (C1).

### Exposition

- [ ] Add a roughly two-page proof overview after the introduction (it should also announce the exponential bound and the generic criterion once they are in), in words: why affine extension blocks cost constant degree, why one weighted substitution removes them, why the target is a nonzero polynomial rather than 1, where the rank threshold comes from, why depth never enters (C1, C2 step 4). C2 notes this is effectively required for ECCC.
- [ ] Rewrite the abstract in standard vocabulary, state plainly that the main theorem itself is formalized, drop "not yet peer reviewed" from the abstract only (C2 gives a draft); the statement stays in the Section 8 disclosure and the title-page note. Decided: fold the framework mention into the single closing AI-assistance sentence, e.g. "The proof was developed with substantial AI assistance within an open research framework described in Section 8." The small note below the author name ("with substantial...") stays.
- [ ] Replace notebook jargon with standard terms or define it once: "complete affine extension blocks", "accuracy-h", "companions", "old base", "row-linear old-base consequence", "registry/slots", "residual NS transport" (C1).
- [ ] Fix overloaded notation (N is both unary columns and registry slots) and add one parameter summary relating k, B, D, h, s, t, r (C1).
- [ ] Add a paragraph of intuition before each main theorem in Sections 4–6 and expand terse steps, e.g. the proof of Theorem 4.7 (C1).
- [ ] Add one worked small example: a single resolution step through the simulation, or one high-rank block being removed (C1).
- [ ] Move formalization-driven generality ("over any field", "no finite-dimensional hypothesis", exact vs upper-bound degrees) into remarks or leave it to the Lean files; keep generality that the paper or a planned extension uses (C1).
- [ ] Consolidate the scattered scope and novelty caveats so they do not interrupt the argument (C1).
- [ ] Explain why prior approaches stalled and which step bypasses the obstacle; connect explicitly to the 1996 extension-variable method (BIKPRS) and Razborov-style degree bounds (C1).
- [ ] Possibly shorten Section 2 to brief preliminaries (C1). Decided: Appendix A stays; it is a real service (C2), despite C1's suggestion to cut it.

### Section 8 and AI disclosure

- [ ] Condense Section 8.3 to one paragraph that keeps the honest disclosure: models used, GPT-6 Astra as main contributor to version 1, the author's contribution, that the author did not check the mathematics and relies on Lean, formalization scope, no peer review (C1 gives a draft). Do not soften it into vagueness (C2).
- [ ] Disclose Claude Fable 5.1's role in revision 1, in the same paragraph and consistently with the title-page note: it formalized the exponential corollary and the generic criterion (statements and proofs, with one proof batch delegated to Claude Opus 5), triaged this feedback, and will draft the revised text. The author again did not check the mathematics and relies on Lean.
- [ ] Move the development story (subscription plans, usage limits, model frustrations, classifier episode, prompt history) out of the paper to a permanently linked document: fixed Git commit, Zenodo, or Software Heritage; a personal website only as a convenience link (C1).
- [ ] Consider a separate Noemesis writeup for the framework, later (C2 step 8). Until it exists, Section 8 keeps its short description of the framework (8.2), which the abstract's closing sentence points to; only the development story of 8.3 moves out.

Note, not a task: ECCC requires submissions to be understandable by researchers in the area; the overview, abstract, and Section 8 items above serve that criterion (C2).

### Mathematical content

- [ ] Exponential corollary S > exp(n/(32768 ℓ²)) (C1, C2). Decided: formalization is a prerequisite.
  - [x] Formalized in Lean for every ℓ ≥ 32, with a base-two form: `formalization/claims/BitPHPExponential.lean`, notebook `#lean-bit-PHP-exponential`. The explicit threshold replaces "sufficiently large".
  - [ ] Add it to Section 7 with the constant and threshold, and update the abstract and headline to "exponential".
- [ ] Generic subspace-consequence theorem: decided against C2's separate companion note; state it as a section or remark in this paper (around Section 7.1). Phrase it as a "sufficient condition", never as a size–degree or size–width tradeoff, and keep the {x, x²−x} caveat next to it. Decided: formalize it in Lean before mentioning it in the paper.
  - [x] PC-level theorem formalized over F₂ for arbitrary variables, base, accuracy and subspace: `GenericAffineSubspaceConsequence.lean`, notebook `#lean-generic-affine-subspace-consequence`.
  - [x] Proof-size form formalized: generic clause-polynomial bridge through 2h+w, transfer with 3S+t slots and degree max(2h+w, 4h+1), and dim U ≤ (3S+t)·C(v−(h(k+1)+1)+k, k) for a separated U: `GenericCNFSubspaceCriterion.lean`, notebook `#lean-generic-CNF-affine-DAG-subspace-criterion`. Decided to formalize this so the paper can speak about refutation size, not only PC.
  - Placement, to reconcile this with the "generality breaks the flow" item under Exposition: that item is about incidental generality inside the main argument, and C1 itself recommended giving one general framework theorem its own section instead. So Sections 2–6 stay concrete (bit PHP, F₂, the row-linear space) and lose their scattered generality remarks; the generic material goes into one short, skippable section after the main theorem, roughly two pages: the criterion, the density form, the caveats, and links to the Lean files, with proofs given by reference to the bit-PHP proofs they abstract. The headline and abstract stay about bit PHP. This also answers C2's worry about enlarging the review surface.
  - [ ] Write the section. The pointer sentence can now say that Sections 5–6 are generic for any clause set whose clause polynomials are axioms of the base; what is specific to bit PHP is the separation Theorem 4.7 over the compact base and the bridge to it. State that no other formula is shown to admit a separated subspace, and that everything is over F₂.
  - [x] Density form formalized: dim U ≤ (3S+t)·C(v+k,k)·exp(−hk²/(v+k)) under h(k+1)+1 ≤ v, i.e. 3S+t ≥ δ·exp(hk²/(v+k)) with δ = dim U / C(v+k,k): `GenericCNFDensityBound.lean`, notebook `#lean-generic-CNF-density-exponential-form`. Use this instead of the bare shape below; it makes the needed density of U explicit.
  - [x] Short-proof control formalized ({L, 1−L} in the base leaves no nonzero separated subspace): `ShortProofControl.lean`, notebook `#lean-generic-criterion-short-proof-control`. It is a consistency check on one trivial family, not an audit of known short Res(⊕) refutations.
- [ ] Optional remark on formulas with short Res(⊕) refutations (C1, C2). The reviewers proposed this as a stress test of an unverified argument (C1 tried Tseitin and graph ordering; neither breaks it). Now that the criterion is Lean-verified, such a test cannot refute it; what remains is its contrapositive, which may deserve one sentence: a formula with a size-S refutation admits no separated degree-k subspace of dimension above (3S+t)·C(v−(h(k+1)+1)+k, k). The formalized {L, 1−L} control is the trivial instance. No experiment is required for the revision; a systematic look at known Res(⊕) upper bounds is separate research.
- [ ] Say plainly what does not follow: unary PHP (recommended wording: no sufficiently dense separated subspace is known for it; C2's quantitative density explanation is unchecked and would need its own proof before it may be stated), a Res(⊕) size–width relation, and the AC0[p]-Frege goal where nested blocks have no removal step (C2).
- [ ] Candidate material for that section or remark, only where checked: the general shape S ≥ exp(Ω(d²/(h·v))) (do not state it bare: it hides the density factor δ and the unformalized substitution k ≈ d/(4h); use the verified density form above), the succinct-encoding observation (only in the hedged form of the previous item), other succinctly encoded principles, Res(lin) over F_p, and the CDCL-with-XOR reading (C2). These are reviewer suggestions, not checked claims.
- [ ] If notebook text from the 16 September assessment migrates into the paper, attribute it plainly as feedback from an AI review (Claude Fable 5.1), never in a way that suggests a human reviewer. C2 advised omitting the model name; decided to name it.

### Versioning and verification

- [ ] Add a version marker and date near the title ("revision 1, DATE"); add the ECCC report number once assigned; mention mathematical changes in the introduction, and any error correction explicitly (C1).
- [ ] Update the cited Lean commit hash everywhere (it must include the five new modules above) and state which commit the revision corresponds to; either keep or genuinely redo the "literature refresh of 15 September 2026" rather than carrying a stale date (C1).
- [ ] Make independent verification trivial: a one-line verify script at the top of the README with the expected `#print axioms` output, a public green CI run, and a tagged release for a stable reference (C2 step 5). Check what already exists; the hosted Lean workflow is now manual-only.
- [ ] Get the formalization built and its axioms printed by an independent party (C1).
- [ ] Ask an independent Res(⊕) expert to check that the Lean definitions are the standard system (`AffineDAGRegistry.lean`, `BitPHPInitialBridge.lean`, top-level statement: arbitrary affine pivots, unrestricted semantic weakening, size as node count, BPHP encoding, axiom report). Do this first, without waiting for the rewrite (C2 step 1).
