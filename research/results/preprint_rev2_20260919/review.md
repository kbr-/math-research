# Bit-PHP preprint revision 2: focused editorial review

Date: 19 September 2026. Starting feedback checkpoint:
`952844a393b5eed56e82a53465e69d89cf8e995c` on branch `feedback`.

## Scope and decisions

Apply the new expert, ChatGPT, and author feedback recorded in FEEDBACK.md.
No new theorem, change of degree bound, or Lean formalization is attempted.
The main ordinary-PHP Frege obligation remains open. The sufficient endpoint
for this assigned side-publication cycle is the revised, visually checked paper,
its evidence and notebook record, and a local commit and annotated date tag.

Retain the author's title and terminology choices. Omit the optional literature
table because the existing prose is more precise about differing restrictions.
Provide the verification map and reproduction instructions within the paper.
The mathematical meaning of the three removal cases and the ordinary polynomial
restriction/cofactor identity is unchanged. Both parameter tables get extra
row spacing; the second maps conditions to their use, rather than repeating
symbol definitions.

## Targeted attribution provenance

Read on 19 September 2026 using web search, with primary-source metadata and
abstracts rather than retaining third-party full text:

- Raz–Tzameret, *Resolution over linear equations and multilinear proofs* (2008),
  https://doi.org/10.1016/j.apal.2008.04.001 and
  https://arxiv.org/abs/0708.1529 . Introduces resolution over linear equations.
- Itsykson–Sokolov, *Resolution over linear equations modulo two* (2020),
  https://doi.org/10.1016/j.apal.2019.102722 . Credits the integer system to
  Raz–Tzameret and studies the modulo-two system, including tree-like bounds.
- Part–Tzameret, https://eccc.weizmann.ac.il/report/2018/117/ , explicitly
  describes the lineage from Raz–Tzameret to Itsykson–Sokolov's tree-like work.

The revised introduction distinguishes these settings and makes no assertion
that integer and F₂ proofs are identical systems. The abstract gives a
consistent descriptive formulation without a competing priority attribution.
This is a targeted attribution check, not a renewed exhaustive novelty search.

## Formal-source pinning and reproduction scope

At the author's request, the paper's current mathematical links and reproduction
recipe both use `8904bf09a5376f48a00d1c25d079bf0c6441502a`, the
revision-1 tagged commit, which adds the import-only aggregate
`claims/BitPHPPreprintRevision1.lean`. Inspection of the diff from the earlier `b47e9b1` source pin found that aggregate to be the only changed file in the two Lean claim
directories. The appendix explicitly keeps its historical module name.

The new table's filenames and declarations are checked against pinned sources.
The recipe is reviewed against that commit's verifier and setup rather than
claimed as a new clean-machine Lean build. Existing fresh-kernel evidence from
18 September remains the formal verification evidence; no theorem source is
changed by revision 2. The recipe's output path is relative to its current
working directory, formalization/, despite the verifier's generic help text.

## Instrumentation and operational notes

The feedback commit and initial policy reading preceded the research clock.
The first Git write needed sandbox escalation because this is a linked worktree.
The first sandboxed resource-status read could not access user systemd; the
escalated check found the slice inactive. The prescribed setup reinitialized
and verified the controls before any protected build. These are operational
failures, not mathematical refutations. Two exploratory source lookups named
nonexistent guessed filenames; the exact declaration map uses discovered paths.
All later builds/rendering use the protected launcher. No dependencies installed.

## Final build and visual QA

All feedback source edits preceded the first PDF build, per the author's request.
The first final-build attempt found a LaTeX line-break parse error in the new
axiom display, plus a long namespace line; both were fixed. The successful PDF
then showed three contents entries on an otherwise empty overflow page. A
compact contents setting removes that page; table columns are ragged-right,
with explicit row gaps in addition to larger array spacing. The final build is
37 pages and has no LaTeX warnings or overfull/underfull boxes.

Rendered all pages locally with Poppler, reviewed whole-document contact sheets
and the changed parameter/verification pages at larger size. Final corrected
pages were rendered again for the concluding review. Previews stay in /tmp and
are not publication artifacts. The final build logs are copied here, while the
protected command records are archived by finish-turn.py. No full Lean rerun or
new external review is claimed. The existing revision-1 source-package JSON is
a historical artifact, not a revision-2 package; no submission package was requested.

The evidence-collection helper needed two operational fixes: path concatenation,
and the discovery that the existing launcher/build combination retained the
pass stdout as `pdflatex-pass-.log`, not separate numbered files. The final
stdout and full LaTeX log are preserved; earlier successful pass stdout was
overwritten. The PDF, final log, and wrapper output establish the completed build.
