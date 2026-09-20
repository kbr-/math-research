# Revision-1 readiness audit

20 September 2026. Internal source and build review only; no independent expert
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
- [x] PDF has two US-letter pages and embedded subset fonts.
- [x] Extracted definitions, hypotheses, proof, references and disclosure checked.
- [x] Both pages rendered locally. Automated word-coordinate and raster-margin
  checks pass; no rendered previews are published. This is not a claim of human
  visual review.
- [x] Source/PDF hashes saved in `reviewed-files.json`.

Full logs and reproducible QA are in
[the retained build evidence](../../research/results/multiplicity_note_rev1_20260920/).
The first build exposed loose bibliography spacing, corrected before the final
build. QA parser retries accommodated Poppler's control-code representations and
zero-width combining math accents; those were extraction issues, not proof errors.

## Outstanding

See [publication prerequisites](PUBLICATION_PREREQUISITES.md) for human review,
independent confirmation, possible author clarification, and a submission decision.
The bounded public search found no acknowledgement of this exact implication, but
absence of a search result does not establish priority. The PDF requires no
supplementary README to understand its mathematical argument.
