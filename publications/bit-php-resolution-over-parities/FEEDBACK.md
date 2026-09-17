# Version 1

- [ ] A reader from the area noted a lack of attribution in the bibliography: Khaniki proved the first superlinear lower bound for this system, and Tzameret co-authored strong lower bounds for a similar system that, as the reader recalled, sums over the reals instead of modulo 2. Verify both against the sources and cite them.

The items below come from two Claude review conversations about the preprint, referred to as C1 and C2. Their claims about the literature and venues are unverified reviewer comments, not an independent review.

### Attribution and related work

- [ ] Cite the Res(lin) lineage: Raz–Tzameret (2008) and Part–Tzameret on dag-like Res(lin) lower bounds (C1, last answer; overlaps the first item, as does Khaniki's first superlinear bound).
- [ ] Cite Razborov's 1998 PC lower bound for PHP, which Section 3 and Appendix A parallel; add a sentence on Impagliazzo–Pudlák–Sgall, Alekhnovich–Razborov, and Mikša–Nordström (C1).
- [ ] State explicitly whether Theorem 3.2 (moment extension) is new or a new proof of a known result (C1).
- [ ] Check recent Res(⊕) work for omissions: Alekseev–Itsykson lifting, Efremenko–Itsykson amortized closure, Gryaznov–Pudlák–Talebanfard, Efremenko–Garlík–Itsykson 2026; a grouping sentence may suffice (C1).

### Exposition

- [ ] Add a roughly two-page proof overview after the introduction, in words: why affine extension blocks cost constant degree, why one weighted substitution removes them, why the target is a nonzero polynomial rather than 1, where the rank threshold comes from, why depth never enters (C1, C2 step 4). C2 notes this is effectively required for ECCC.
- [ ] Rewrite the abstract in standard vocabulary, state plainly that the main theorem itself is formalized, drop "not yet peer reviewed" (C2 gives a draft). Decided: fold the framework mention into the single closing AI-assistance sentence, e.g. "The proof was developed with substantial AI assistance within an open research framework described in Section 8." The small note below the author name ("with substantial...") stays.
- [ ] Replace notebook jargon with standard terms or define it once: "complete affine extension blocks", "accuracy-h", "companions", "old base", "row-linear old-base consequence", "registry/slots", "residual NS transport" (C1).
- [ ] Fix overloaded notation (N is both unary columns and registry slots) and add one parameter summary relating k, B, D, h, s, t, r (C1).
- [ ] Add a paragraph of intuition before each main theorem in Sections 4–6 and expand terse steps, e.g. the proof of Theorem 4.7 (C1).
- [ ] Add one worked small example: a single resolution step through the simulation, or one high-rank block being removed (C1).
- [ ] Move formalization-driven generality ("over any field", "no finite-dimensional hypothesis", exact vs upper-bound degrees) into remarks or leave it to the Lean files; keep generality that the paper or a planned extension uses (C1).
- [ ] Consolidate the scattered scope and novelty caveats so they do not interrupt the argument (C1).
- [ ] Explain why prior approaches stalled and which step bypasses the obstacle; connect explicitly to the 1996 extension-variable method (BIKPRS) and Razborov-style degree bounds (C1).
- [ ] Possibly shorten Section 2 to brief preliminaries (C1). Decided: Appendix A stays; it is a real service (C2), despite C1's suggestion to cut it.

### Section 8 and AI disclosure

- [ ] Condense Section 8.3 to one paragraph that keeps the honest disclosure: models used, GPT-6 Astra as main contributor, the author's contribution, that the author did not check the mathematics and relies on Lean, formalization scope, no peer review (C1 gives a draft). Do not soften it into vagueness (C2).
- [ ] Move the development story (subscription plans, usage limits, model frustrations, classifier episode, prompt history) out of the paper to a permanently linked document: fixed Git commit, Zenodo, or Software Heritage; a personal website only as a convenience link (C1).
- [ ] Consider a separate Noemesis writeup for the framework, later (C2 step 8).
- [ ] ECCC requires submissions to be understandable by researchers in the area; the overview, abstract, and Section 8 items above serve that criterion (C2).

### Mathematical content

- [ ] Exponential corollary S > exp(n/(32768 ℓ²)) (C1, C2). Decided: formalization is a prerequisite.
  - [x] Formalized in Lean for every ℓ ≥ 32, with a base-two form: `formalization/claims/BitPHPExponential.lean`, notebook `#lean-bit-PHP-exponential`. The explicit threshold replaces "sufficiently large".
  - [ ] Add it to Section 7 with the constant and threshold, and update the abstract and headline to "exponential".
- [ ] Generic subspace-consequence theorem: decided against C2's separate companion note; state it as a section or remark in this paper (around Section 7.1). Phrase it as a "sufficient condition", never as a size–degree or size–width tradeoff, and keep the {x, x²−x} caveat next to it. Decided: formalize it in Lean before mentioning it in the paper.
  - [x] PC-level theorem formalized over F₂ for arbitrary variables, base, accuracy and subspace: `GenericAffineSubspaceConsequence.lean`, notebook `#lean-generic-affine-subspace-consequence`.
  - [x] Proof-size form formalized: generic clause-polynomial bridge through 2h+w, transfer with 3S+t slots and degree max(2h+w, 4h+1), and dim U ≤ (3S+t)·C(v−(h(k+1)+1)+k, k) for a separated U: `GenericCNFSubspaceCriterion.lean`, notebook `#lean-generic-CNF-affine-DAG-subspace-criterion`. Decided to formalize this so the paper can speak about refutation size, not only PC.
  - [ ] Write the section. The pointer sentence can now say that Sections 5–6 are generic for any clause set whose clause polynomials are axioms of the base; what is specific to bit PHP is the separation Theorem 4.7 over the compact base and the bridge to it. State that no other formula is shown to admit a separated subspace, and that everything is over F₂.
  - [x] Density form formalized: dim U ≤ (3S+t)·C(v+k,k)·exp(−hk²/(v+k)) under h(k+1)+1 ≤ v, i.e. 3S+t ≥ δ·exp(hk²/(v+k)) with δ = dim U / C(v+k,k): `GenericCNFDensityBound.lean`, notebook `#lean-generic-CNF-density-exponential-form`. Use this instead of the bare shape below; it makes the needed density of U explicit.
  - [x] Short-proof control formalized ({L, 1−L} in the base leaves no nonzero separated subspace): `ShortProofControl.lean`, notebook `#lean-generic-criterion-short-proof-control`. It is a consistency check on one trivial family, not an audit of known short Res(⊕) refutations.
- [ ] Stress-test the method against formulas with short Res(⊕) refutations and nontrivial PC/F₂ degree (C1 tried Tseitin and graph ordering; both fail to break it); report the outcome, or the lack of a ready candidate, as a remark.
- [ ] Say plainly what does not follow: unary PHP (with the succinct-encoding explanation, once checked), a Res(⊕) size–width relation, and the AC0[p]-Frege goal where nested blocks have no removal step (C2).
- [ ] Candidate material for that section or remark, only where checked: the general shape S ≥ exp(Ω(d²/(h·v))) (do not state it bare: it hides the density factor δ and the unformalized substitution k ≈ d/(4h); use the verified density form above), the succinct-encoding observation, other succinctly encoded principles, Res(lin) over F_p, and the CDCL-with-XOR reading (C2). These are reviewer suggestions, not checked claims.
- [ ] If notebook text from the 16 September assessment migrates into the paper, attribute it plainly as feedback from an AI review (Claude Fable 5.1), never in a way that suggests a human reviewer. C2 advised omitting the model name; decided to name it.

### Versioning and verification

- [ ] Add a version marker and date near the title ("revision 1, DATE"); add the ECCC report number once assigned; mention mathematical changes in the introduction, and any error correction explicitly (C1).
- [ ] Update the cited Lean commit hash everywhere (it must include the five new modules above) and state which commit the revision corresponds to; either keep or genuinely redo the "literature refresh of 15 September 2026" rather than carrying a stale date (C1).
- [ ] Make independent verification trivial: a one-line verify script at the top of the README with the expected `#print axioms` output, a public green CI run, and a tagged release for a stable reference (C2 step 5). Check what already exists; the hosted Lean workflow is now manual-only.
- [ ] Get the formalization built and its axioms printed by an independent party (C1).
- [ ] Ask an independent Res(⊕) expert to check that the Lean definitions are the standard system (`AffineDAGRegistry.lean`, `BitPHPInitialBridge.lean`, top-level statement: arbitrary affine pivots, unrestricted semantic weakening, size as node count, BPHP encoding, axiom report). Do this first, without waiting for the rewrite (C2 step 1).
