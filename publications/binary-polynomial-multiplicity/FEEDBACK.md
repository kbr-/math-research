# Feedback and self-review

## Version 1 — in-place checklist review, 20 September 2026

The author has not circulated the note. This is an internal AI-assisted review
against [CHECKLIST.md](CHECKLIST.md), not an external review or a new public version.
Numbers follow the checklist’s order; checked items mean the stated internal
review disposition, not human approval or novelty certification.

- [x] **1. Describe the actual contribution. — Changed.** The abstract already identifies the implication of a known lemma. The closing scope statement now says this once, without a catalogue of unrelated claims.

- [x] **2. Align the statement throughout. — Changed.** The proposition displays its degree bound directly. Field, positive n and k, total degree and multiplicity hypotheses remain consistent with the question and proof.

- [x] **3. State the improvement precisely. — Satisfied.** The proof never uses k >= 2^(n-2); the conclusion explicitly drops this restriction without claiming invention of the standard estimate.

- [x] **4. Keep the boundary concise. — Changed.** Consolidated repeated novelty/method caveats into one concise contribution statement. The exact question remains explicitly identified.

- [x] **5. Verify both ends of the connection. — Satisfied.** Recompared the journal Question 4.3 with published DKSS Definition 2.2 and Lemma 2.7, including the nonzero-polynomial hypothesis and unrestricted degree.

- [x] **6. Make version numbering unmistakable. — Changed.** Shortened the version explanation to journal numbering versus arXiv-v1 Question 5.2. Both external numbers were checked against their respective PDFs.

- [x] **7. Credit the prior theorem fully. — Satisfied.** All four authors of the question and all four authors of the lemma are credited; the note presents a direct implication, not a missing standard estimate.

- [x] **8. Check bibliography and links. — Satisfied.** Compared author names, accents, publication details and DOI identifiers with the primary papers; retained the explicit arXiv v1 reference and date.

- [x] **9. Avoid unsupported priority or intent claims. — Satisfied.** The paper makes no priority claim and does not speculate about author intention. Prior acknowledgement and intended scope remain outstanding clarification items.

- [x] **10. Make the abstract immediately understandable. — Satisfied.** Retained the concise abstract: exact binary question, named existing lemma, and the removed threshold. No process history or proof-system jargon added.

- [x] **11. Explain the idea in one short passage. — Changed.** Added a short opening explanation: add the required multiplicities and compare with degree times half the binary grid size.

- [x] **12. Define exactly what the reader needs. — Changed.** Made the field and positive dimension explicit before introducing translated polynomials. Retained only the multiplicity and degree definitions needed here.

- [x] **13. Make each hypothesis's role visible. — Satisfied.** The proof explicitly uses the origin condition to exclude zero; the post-proof paragraph explains that this is its only role.

- [x] **14. Keep the decisive calculation together. — Satisfied.** Kept the entire multiplicity inequality chain and integer-rounding calculation together in the proof.

- [x] **15. Keep the note proportionate. — Changed.** Shortened version commentary and repeated caveats. Added no overview section, example, parameter table, appendix or new generalization.

- [x] **16. Use the correct multiplicity convention. — Satisfied.** The translated-polynomial definition matches Hasse derivatives in positive characteristic; zero has infinite multiplicity. Ordinary derivatives are not substituted.

- [x] **17. Apply the lemma with all hypotheses satisfied. — Satisfied.** P is nonzero, n >= 1 and S = F2 is finite and nonempty. The imported total-degree bound has no degree/field-size condition.

- [x] **18. Check counting and inequality directions. — Satisfied.** There are 2^n-1 nonzero points; multiplicities are nonnegative; division by 2^(n-1) is valid and preserves the inequality.

- [x] **19. Check rounding and boundary cases. — Satisfied.** Checked analytically: ceil(m-x)=m-floor(x) for integral m=2k. For n=1 the bound is k; for k=1 it is 1 when n=1 and 2 when n>=2. Integral quotients cause no exception. No sharpness outside the original range is claimed.

- [x] **20. Do not lose multiplicity information. — Satisfied.** Every step concerns the original formal polynomial; no field-equation reduction occurs. The warning about losing multiplicity remains beside the definition.

- [x] **21. Keep notation consistent. — Satisfied.** Checked n,k,d,S, the fields, multi-index weight and origin notation. Internal references use labels; external numbers are version-qualified.

- [x] **22. Disclose assistance accurately. — Changed.** Made the author’s directing role and substantial AI role explicit, and stated the absence of independent mathematical review and formal verification. No human proof check is claimed.

- [x] **23. Keep history outside the argument. — Satisfied.** Kept development details in DEVELOPMENT_HISTORY.md; the PDF contains only a concise disclosure and direct development-history link.

- [x] **24. Keep revision and review status consistent. — Changed.** Corrected the premature revision-1 label to version 1 in the paper and current publication documents. The author has not circulated it; these are in-place edits, not a version increment.

- [x] **25. Check the final PDF after source edits. — Satisfied.** Rebuilt only after all source edits. Final PDF has two pages, version 1 on the title page, no warnings, embedded fonts and resolved references. Extracted content, external PDF links, page bounds and rendered raster margins passed fresh checks; this is automated layout QA, not independent human visual review. Source/PDF hashes refreshed.

- [x] **26. Record the review outcome honestly. — Satisfied.** Recorded each disposition below. Formalization and long-paper apparatus remain not applicable; human-author approval, independent review and possible author clarification remain outstanding.

## Not applicable

Formalization/declaration maps, axiom reports, proof-system comparisons, long proof
overviews, parameter tables, worked-example sections, experiments and technical
appendices are not needed for this draft. These are deliberate scope decisions,
not missing tasks or claims that such work was performed.

## Outstanding external questions

- [ ] Obtain independent confirmation of the source comparison and deduction.
- [ ] Clarify whether the connection is already known or a stronger question was intended before claiming novelty.
- [ ] Incorporate any authorized author correspondence, paraphrasing public feedback and retaining private verbatim excerpts only in the ignored private area.

Human-author approval and submission decisions remain in [PUBLICATION_PREREQUISITES.md](PUBLICATION_PREREQUISITES.md).
No author contact or submission was performed or authorized by this review.

## Additional AI feedback — triage, 20 September 2026

Paraphrased from a privately retained AI conversation. The accepted items below
were applied or checked in place on 20 September 2026, at the author's request,
without a research cycle or version increment. This remains internal AI-assisted
review, not independent mathematical review or a novelty certification.

### Accepted follow-up items — completed

- [x] **Distinguish validity from sharpness.** Added a short qualification and
  the concrete k=1, n>=3 comparison: the displayed bound gives 2, whereas
  Alon–Füredi gives n. The origin condition for k=1 is nonvanishing, as required.
  Cited Sauermann–Wigderson, Theorem 1.1 and Section 4.2, which explicitly records
  validity over arbitrary fields. Excluding n=1,2 avoids both the exceptional
  value and the equality case. No claim about the original authors' intentions.

- [x] **Make the implication wording explicit.** Replaced “answers the published
  Question 4.3” with “implies the bound asked for in the published Question 4.3.”
  The precise conclusion and proof are unchanged.

- [x] **Follow up the concrete literature leads.** Checked the stated problems
  and relevant introductory/concluding passages in the suggested papers and
  compared the original preprint's Section 5 with the journal's Section 4.
  The leads concern related real-grid or real-hypercube problems; the checked
  passages did not establish prior acknowledgement of this binary implication.
  Exact versions and the limits of this bounded check are recorded in
  [the application notes](feedback-application-20260920.md). No priority claim
  or speculative explanation of author intent was added.

- [x] **Check the suggested construction as a consistency test.** Checked the
  displayed characteristic-two construction in Sauermann–Wigderson Section 4.2:
  multiplicity at least 4 off the origin and a nonzero origin value. Its degree
  n+4 matches the note's bound at (n,k)=(3,4) and (4,4), giving 7 and 8.
  Kept this check in the application notes; a table would add little to the short
  deduction. The vague (5,8) gap was not imported as a claim about the optimum.

### Suggestions not adopted as stated

- **Replace the binary focus by a general-field paper:** not adopted. An optional
  general-field remark can be considered later, but this note's purpose is the
  exact printed binary question. Extending the elementary inequality alone does
  not establish that the different q-ary Question 4.2 is answered; its precise
  target and hypotheses would need a separate comparison. No such resolution is
  asserted here.

- **Explain why the authors missed the implication:** not adopted. Their choice
  of methods may supply factual context if sourced, but it does not establish what
  they knew or why the question was posed. Preserve the existing prohibition on
  speculation about author intent.

- **Treat an expert glance as removing review concerns:** independent human
  feedback is welcome and already requested in the outstanding items, but any
  resulting disclosure must describe the actual review scope. Neither a second
  AI's agreement nor an informal glance is formal verification or evidence of
  novelty. Keep assistance attribution accurate.

The suggestion to seek clarification from an original author reinforces the
existing external questions rather than creating a duplicate task. Correspondence
still requires explicit authorization; no message was sent. The feedback's
qualitative assessment of likely folklore is not adopted as a novelty finding.
