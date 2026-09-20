# Version-1 readiness audit

20 September 2026. The uncirculated version 1 was self-reviewed in place against
[CHECKLIST.md](CHECKLIST.md); all 26 internal dispositions are in [FEEDBACK.md](FEEDBACK.md).
This is an internal source and build review only; no independent expert
review, human-author approval, Lean verification or submission is claimed.

## Source and mathematical scope

- [x] The question is the polynomial Question 4.3 in the **2023 journal version**
  of Bishnoi–Boyadzhiyska–Das–Mészáros, not the different Question 4.3 in the
  earlier arXiv version. The equivalent older question is numbered 5.2.
- [x] DKSS **Definition 2.2 and Lemma 2.7** were checked in the published SIAM
  version as well as the earlier author manuscript. The lemma permits every
  nonzero polynomial, with no degree-versus-field-size restriction.
- [x] The note uses Hasse multiplicity of formal polynomials, not reduced
  polynomial functions or ordinary derivatives in positive characteristic.
- [x] The origin hypothesis excludes the zero polynomial; the sum over the
  other 2^n-1 points and the ceiling/floor identity give the stated bound.
- [x] The unnecessary k threshold is identified. The note claims only an
  implication of an existing theorem, with full attribution.
- [x] Significant AI assistance in the source comparison, identification and
  drafting is disclosed in the PDF.

Primary references checked:

- [Published BBDM paper](https://pure-oai.bham.ac.uk/ws/files/194705078/subspace_coverings_with_multiplicities.pdf)
- [Published DKSS paper](https://people.csail.mit.edu/madhu/papers/2009/merger-journ.pdf)
- [Earlier BBDM arXiv version](https://arxiv.org/abs/2101.11947v1)

## Final artifact checks

- [x] Three protected pdflatex passes completed with shell escape disabled.
- [x] Final pass: no warnings, overfull/underfull boxes, missing glyph warnings,
  undefined references or unresolved citations.
- [x] PDF has two US-letter pages, the version-1 label and embedded subset fonts.
- [x] PDF hyperlinks contain the three DOI targets, the explicit arXiv v1 target and the direct development-history URL.
- [x] Extracted definitions, hypotheses, proof, references and disclosure checked.
- [x] Both pages rendered locally. Automated word-coordinate and raster-margin
  checks pass; no rendered previews are published. This is not a claim of human
  visual review.
- [x] Source/PDF hashes saved in `reviewed-files.json`.

Fresh final-build logs and reproducible QA are in
[the feedback application evidence](../../research/results/multiplicity_feedback_application_20260920/).
The additional feedback and source comparisons are recorded in
[the application notes](feedback-application-20260920.md). An initial build
overflowed to three pages; a shorter paragraph and compact bibliography restored
two pages before the final three-pass build. Rounding and
the n=1 and k=1 boundary cases were checked analytically. Earlier build snapshots
remain in [the initial drafting evidence](../../research/results/multiplicity_note_rev1_20260920/);
its directory name is historical and does not define the paper's version.

The initial “revision 1” wording was an editorial labeling error, corrected to
“version 1” at the author's request. No new public version or release was made.

## Outstanding

See [publication prerequisites](PUBLICATION_PREREQUISITES.md) for human review,
independent confirmation, possible author clarification, and a submission decision.
The bounded public search found no acknowledgement of this exact implication, but
absence of a search result does not establish priority. The PDF requires no
supplementary README to understand its mathematical argument.
