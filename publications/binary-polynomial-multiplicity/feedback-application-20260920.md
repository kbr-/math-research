# Version-1 feedback application — 20 September 2026

Editorial/source follow-up requested by the author, explicitly outside a research
cycle. No notebook entry, new research claim, version increment or author contact.
The proof is unchanged. Source comparisons below are bounded checks, not an
exhaustive citation search or independent expert validation.

## Manuscript changes

The conclusion now says that the proposition implies the bound asked for in the
published question. A brief paragraph distinguishes validity from sharpness, using
k=1 and n>=3: the displayed estimate gives 2, while Alon–Füredi gives n. The latter
hypothesis holds because multiplicity at the origin is at most zero. Added the
Sauermann–Wigderson reference, whose Theorem 1.1 states the result and Section 4.2
explicitly extends Alon–Füredi to arbitrary fields. No tightness table or q-ary
resolution claim is added.

## Primary-source passages checked

- [Sauermann–Wigderson, arXiv:2010.00077v2](https://arxiv.org/pdf/2010.00077v2),
  Theorem 1.1 and Section 4.2: arbitrary-field validity and the displayed
  characteristic-two polynomial. The latter has multiplicity at least four at
  nonzero binary points and value one at zero. At n=3,4 its degree n+4 equals
  8-floor(4/2^(n-1)), namely 7,8. These are consistency/equality examples, not a
  characterization of all sharp cases. For n=5, squaring that construction gives
  degree 18 and multiplicity at least 8, versus the lower bound 16; this comparison
  alone cannot establish the optimal degree. The conversation did not specify
  what its claimed gap meant. Publication: [JLMS DOI](https://doi.org/10.1112/jlms.12637).
- [Bishnoi–Boyadzhiyska–Das–den Bakker, arXiv:2305.00825v1](https://arxiv.org/pdf/2305.00825v1),
  abstract, Definition 1 and introductory bounds: line coverings of real planar
  grids, with the origin uncovered. This is not the binary formal-polynomial
  question. A text search for Schwartz found no match; this is not proof of
  absence of an equivalent argument elsewhere in the literature.
- [Ghosh–Kayal–Nandi, arXiv:2207.13752v2](https://arxiv.org/pdf/2207.13752v2),
  abstract and introduction: real polynomials, multiplicity at least t off a
  chosen Hamming layer, exactly t-1 on it. The characteristic and origin
  hypotheses differ from the question here. The v1 and current v3 have different
  titles/content, so the comparison is pinned to v2 (16 February 2023).
- [Ghosh–Kayal–Nandi–Venkitesh, arXiv:2307.16881v1](https://arxiv.org/pdf/2307.16881v1),
  abstract: further hyperplane/polynomial covering results for symmetric subsets.
  This additional lead did not supply an acknowledgement of the present
  implication in the checked material; no exhaustive review is claimed.
- [BBDM arXiv:2101.11947v1](https://arxiv.org/pdf/2101.11947v1), Section 5,
  compared with [the journal Section 4](https://doi.org/10.1017/S0963548323000123).
  The concluding discussion explicitly asks about transferring the hyperplane
  double-counting bound to polynomials (preprint Question 5.2, journal 4.3).
  The distinct q-ary question (preprint 5.1, journal 4.2) asks for the
  dimension-dependent hyperplane-cover value (q-1)(n+1)+q(k-2) at large n.
  A q-ary version of the sum-of-multiplicities inequality does not prove that
  assertion. The text supplies no basis for speculation about why the authors
  posed their polynomial question.

These checks leave prior knowledge and intended scope unresolved. The suggested
expert correspondence remains a separate, unauthorized action.

## Artifact verification

All source edits precede the final protected three-pass build. Build logs,
extracted text, PDF links, fonts and automated page/raster checks are retained in
[the feedback application evidence](../../research/results/multiplicity_feedback_application_20260920/).
These checks do not constitute independent human review.
