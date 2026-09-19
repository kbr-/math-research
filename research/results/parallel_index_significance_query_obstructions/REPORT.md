# Bounded significance audit: two ENS query-rate obstructions

Audit date: 19 September 2026. This assesses significance and attribution, not a
new proof, full correctness review, kernel verification or publication decision.
Both metadata reviews can be marked **reviewed**, with **novelty unknown** as the
result of an actual bounded search, rather than an unperformed-audit placeholder.

## Exact scope checked locally

For `thm:universal-ENS-pseudosolution-rate-obstruction`, the recorded statement
concerns any unsatisfiable Boolean quadratic system over a prime field. For
`h>=1`, `S>=2`, it excludes the guarantee `gamma>S(1-1/p)^h` against every
ordinary degree-D tree of height `h+ceil(log_2 S)`, when `D>=2h`; over F2,
`D>=h+1` suffices. The argument combines growing full-polynomial moment rank
with a covariance conflict probe, and permits a finite weighted distribution of
designs. It is stronger in distribution scope than testing one uniform candidate.

For `thm:depth-four-ENS-query-obstruction`, the same attack is implemented with
arithmetic-depth-four prime-field query formulas. In the stated logarithmic
accuracy/polynomial inventory PHP regime, queries have size
`O(n^2 log^3 n)` and the separately described tree has size `O(n^2 log^4 n)`.
This removes polynomial description size and generic depth at least four as
repairs of this particular sufficient-rate route. It does not show that such
queries arise from every particular source proof's companion/cofactor structure.

The exact statement anchors, their compact-query predecessor, the full-space
covariance probe, moment flatness argument, degree-mixture sampler and the rate
versus diagonal comparison were read. All remain working notebook arguments;
this audit changes neither their mathematical status nor their formalization.

## Primary-literature comparison

[Krajíček, v3](https://arxiv.org/abs/2301.10617v3), Definition 3.1 and Theorem 3.2,
uses finite sets of designs, degree/height-limited query trees and a quantitative
pseudo-solution criterion. Problem 3.5 states the diagonal parameter family
`((log n)^r,r log n,n^-r)`. Those exact passages were reread in the existing
local extraction and compared with the primary author-page search result.
The notebook's stricter sufficient rate must not be conflated with that printed
question. Neither audited obstruction settles the diagonal question or refutes
the published sufficient implication.

[Laurent–Mourrain, v1](https://arxiv.org/pdf/0812.2563v1), introduction and
Theorem 1.4, supplies established flat-extension machinery, explicitly in a
field-based algebraic setting. This supports the notebook's existing attribution;
the flat-extension method should not be advertised as newly invented here.

A further close comparison found during this audit is
[Guruswami–Ren–Tang, May 2026](https://arxiv.org/html/2605.11545v1#S4), Section 4,
particularly Lemmas 4.3–4.7: finite-field pseudo-moment flatness leads to commuting
idempotent multiplication operators and a Boolean satisfying assignment. This
substantially overlaps the rank-growth ingredient. The paper concerns promise
rank hardness; the inspected material does not state the ENS survival-rate or
depth-four query obstruction. Attribution to the existing ingredient is needed
before presenting the combination as a research contribution.

[Alon–Goldreich–Håstad–Peralta, June 1992 author copy](https://www.wisdom.weizmann.ac.il/~oded/PSX/aghp.pdf),
introduction, third construction, explicitly gives the classical finite-field
power/linear-functional small-bias mechanism. That is relevant background for
the notebook's compact sampler. Its distinct shallow degree-mixture construction
and its ENS application should not be described as establishing novelty of
small-bias sampling in general. The PDF was successfully accessed after removing
an extra slash in the recorded author URL.

## Audited dispositions

1. **Universal rate obstruction:** retain `independent_result` as a possible
   standalone *method-limitation* result, `novelty: unknown`, and publication
   status `candidate`. Its breadth across Boolean quadratic systems and arbitrary
   finite design distributions gives it relevance beyond one failed candidate.
   The bounded search found no exact prior statement, but the known rank-growth
   mechanism prevents inferring novelty from that absence. A paper would need
   to isolate precisely the additional quantitative query/probability conclusion.
2. **Depth-four obstruction:** retain `independent_result`, `novelty: unknown`,
   publication status `candidate`. This is a potentially useful refinement of the
   same barrier, best assessed jointly with the universal obstruction rather than
   counted as an independently validated discovery. Its concrete formula bounds
   distinguish it from an unrestricted dense-query attack. No exact prior match
   was identified in the bounded search; this is not a comprehensive priority
   conclusion about shallow samplers or conflict-search procedures.

For either result, the next publication-oriented action is a focused comparison
of the exact additional rate/query statement against the cited finite-field
moment and small-bias literature, followed by independent expert assessment.
That future publication decision does not prevent recording the completed
significance audit as reviewed with explicitly unknown novelty.

The obstructions do **not** establish an ENS refutation, Frege upper bound,
Frege lower bound, or solution to the project's main goal. No new paper or
public announcement is authorized by this audit.

## Search and retention scope

`sources.json` records the actual queries, primary URLs and inspected portions.
The search was bounded and returned irrelevant hits for several exact phrase
queries; those were not treated as evidence. No exact-match result was found,
which is weak evidence about priority. No external full texts were downloaded
or copied into the repository; the durable report contains summaries and links.
The existing Krajíček extraction was read in place. Sources and theorem labels
are sufficient to reproduce the comparisons without reproducing copyrighted
papers. Agent timing is exported separately and overlaps coordinator work.
