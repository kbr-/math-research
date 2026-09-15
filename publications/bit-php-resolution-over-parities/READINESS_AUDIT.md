# Publication readiness review — 15 September 2026

**Validation path B is complete.** After the clean project build and axiom
review, the author authorized the fresh replay using the bundled `leanchecker`.
It passed with exit code zero and no diagnostics. No installation was needed:
our first tool search had used the obsolete name `lean4checker`.
The author also subsequently authorized preparation of a local source package.
Nothing was submitted, pushed, committed, or staged during this review.

## Exact revision and proof scope

The manuscript started from `dfbab68`; the local release edits update references
and review-status wording without changing its mathematics. `reviewed-files.json`
identifies the reviewed TeX files and resulting PDF by SHA-256, so these unstaged
edits are not misleadingly attributed to a new commit.
All project Lean sources and dependency pins are unchanged from published
[`54f0937`](https://github.com/kbr-/math-research/tree/54f09378e97465522b7f1caf115f90ad1faa7a57).
The permanent Lean links therefore still identify the checked mathematical sources.

The review reused the completed route, its per-claim scope records and the
[statement-to-source map](../../research/results/whitepaper_formal_revision_20260915/statement-links.json),
then inspected the final theorem and its actual encoding/proof definitions.
This is a focused correspondence review, not independent expert peer review.

| Manuscript requirement | Formal correspondence checked |
| --- | --- |
| Usual bit-PHP CNF, not only compact initial clauses | `usualBitPHPInitials` includes every ordered pigeon pair and every bit label; `usualCNFClause` uses the two rows' disequality indicators `x(i,t)+z(t)` over `ZMod 2`. |
| Arbitrary finite acyclic proof DAG | `C : Fin S → FiniteParityClause ...`; each `AffineDAGStep` refers to earlier nodes, permits reuse, and imposes no regularity, width, or height bound. Any finite acyclic DAG admits such an ordering. |
| Both rule conventions | Constructors for semantic weakening, complementary affine resolution, and arbitrary sound binary inference. Clause semantics are ordinary affine evaluation on all binary assignments. |
| Actual refutation and size quantifiers | Every real `K>0`; a threshold `L`; all bit lengths above it; every `S` and valid DAG; an empty final clause; conclusion `(2^ell)^K < S`. |
| Ordinary, unquotiented polynomial degree | `MvPolynomial`, primitive `Derives`, and `nsSpace` charge each individual generator multiple. Zero has total degree zero. |
| Entire compilation and parameter chain | R24 gives the actual initial-clause transfer and complete registry; R17 gives uniform exclusion; R25 uses `a=max(ceil K,2)`, inventory at most `13*2^(a*ell)+1`, degree at most `13*(ell+1)`. The chain includes the H13 proof, not an assumed interface. |

The formalization-era proofs and generalized statements were compared during the
preceding whitepaper revision. No new mathematical discrepancy was identified in
this review. The recorded telescoping degree correction is reflected in the paper:
upper bounds remain upper bounds, with exact block degrees separately justified.
Finite experiments are described as development checks, not an asymptotic proof.
The broader ordinary-PHP AC0[p]-Frege objective is explicitly still open.

## Build and axiom evidence

- Lean: `leanprover/lean4:v4.34.0-rc2`.
- Mathlib: `67248ba34806c60bf24b5e99f0f09946ffc465c9`; transitive versions
  are locked in `formalization/lake-manifest.json`.
- Copied both claim directories, `lakefile.lean`, `lake-manifest.json` and
  `lean-toolchain` into a new temporary directory with **no project build outputs**.
  Linked its `.lake/packages` to the existing pinned dependency checkout/cache.
- Ran `lake --no-cache --wfail build` under the shared resource controller.
  All project modules rebuilt successfully, including the final theorem;
  Lake reported 2490 jobs. Existing library artifacts were reused, not rebuilt.
- In that clean project, imported `claims.BitPHPSuperpolynomial` and ran
  `#check @MathResearch.bitPHP_superpolynomial` and
  `#print axioms MathResearch.bitPHP_superpolynomial` with warnings as errors.
  The only axioms reported were `propext`, `Classical.choice`, and `Quot.sound`.
- A focused project-source scan found no custom axiom declaration, native-decision
  invocation, or explicit kernel-check bypass. This scan is not a kernel replay.
- Full command outputs, timings and reproduction details are retained in the
  [review session archive](../../research/provenance/session-records/publication_readiness_20260915/).

To reproduce normal validation, follow [the Lean project guide](../../formalization/README.md).
The additional replay ran as:

```sh
./compute.sh --session publication_kernel_replay_20260915 --threads 1 \
  --timeout 3600 --category formal_verification bash -c \
  'source "$HOME/.elan/env"; cd formalization; lake env leanchecker --fresh claims.BitPHPSuperpolynomial'
```

It exited successfully without diagnostics after 262.98 seconds, replaying
all declarations in the final module and its imports in a fresh kernel environment.
The [result and provenance](../../research/results/publication_kernel_replay_20260915/replay.json)
and [complete session evidence](../../research/provenance/session-records/publication_kernel_replay_20260915/)
record the command, exit status, timing, toolchain and source revision.
This uses Lean's own kernel, not an independently implemented external checker.
See the [official validation guide](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## Primary-literature refresh

This bounded search on 15 September 2026 updates the earlier
[publication audit](https://kbr.is-a.dev/math-research/#bit-PHP-publication-audit-verdict).
It reviewed primary report/publisher abstracts, revision metadata and author
publication listings; it did not reread every cited proof or establish exhaustive
novelty. Queries included “resolution over parities bit pigeonhole principle
unrestricted superpolynomial 2026” and searches for the merged STOC paper.

- [Efremenko–Garlík–Itsykson](https://eccc.weizmann.ac.il/report/2023/187/)
  and the [journal record](https://epubs.siam.org/doi/10.1137/24M1696640):
  the bit-PHP exponential size result has a regularity restriction.
- [Bhattacharya–Chattopadhyay, TR25-106 revision 2](https://eccc.weizmann.ac.il/report/2025/106/):
  the exponential bounds retain a near-quadratic proof-depth restriction.
- [Byramji–Impagliazzo, TR25-118](https://eccc.weizmann.ac.il/report/2025/118/):
  the usual bit-PHP consequence also has a depth restriction. The
  [author's publication list](https://fbyramji.github.io/) confirms the two
  works were merged for STOC 2026. The ACM DOI endpoint was unavailable during
  this refresh; existing proceedings metadata was retained.
- [Itsykson–Podolskii–Shekhovtsov, CCC 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2026.13):
  the published version gives near-quadratic-depth lifting and an unrestricted
  quadratic size consequence. Updated the bibliography to this proceedings version.
- [Alekseev–Gaevoy, TR26-007](https://eccc.weizmann.ac.il/report/2026/007/):
  polynomial-depth bounds for constrained bit PHP are conditional in general
  Res(⊕); unconditional variants restrict the calculus or depth. Added a brief
  comparison and citation, since this is closely related to the paper's scope.
- [Itsykson–Knop, ITCS 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.81):
  a size-versus-depth tradeoff, not an unrestricted superpolynomial size result.
- [de Rezende–Engström–Ghannane–Risse, TR26-078](https://eccc.weizmann.ac.il/report/2026/078/):
  semantic lower bounds retain tree-likeness and bounded line size.

None of the examined sources states the paper's unrestricted usual-bit-PHP
superpolynomial node bound. The manuscript explicitly limits this conclusion to
the scope of the search; formal verification itself is not evidence of novelty.

## Authorship, review status, and release contents

The author explicitly confirmed in this session that he has read the manuscript,
understands its scope and takes responsibility for its contents. Kamil Braun is
the sole listed author; the title block and Section 8.3 disclose substantial model
assistance and describe the work performed. The abstract and closing paragraph
now explicitly say the manuscript has not yet been externally peer reviewed.
The formal-verification account now records the successful fresh kernel replay. These disclosures were compared with the
[arXiv AI and moderation policy](https://info.arxiv.org/help/moderation/index.html).
Moderation is distinct from peer review; the checklist does not promise acceptance.

The source inventory was reviewed against an explicit whitelist: `whitepaper.tex`,
`references.tex`, the eight `sections/*.tex` files, and the CC BY 4.0 license text.
The authorized source-only archive was prepared at `/tmp/noemesis-bit-php-arxiv-v1.tar.gz`
and its exact extracted contents compiled successfully in three pdfLaTeX passes
with no warnings or unresolved references. [submission-package.json](submission-package.json)
records the archive hash and all eleven entries. The working PDF is the output
of that isolated build.
It excludes cited papers, third-party PDFs, private backups, compiled outputs,
session data and Git history. Classical citations and the author's CC BY 4.0
attribution are present. The package follows the
[arXiv TeX source guidance](https://info.arxiv.org/help/submit_tex.html); its main
file is `whitepaper.tex`, with pdfLaTeX as processor and the bibliography already
included in `references.tex` (no BibTeX run required).

The manuscript's current status is “Preprint”; historical references to its
first draft remain. `reviewed-files.json` identifies this source/PDF snapshot;
further manuscript edits require rebuilding and refreshing the release check.
No arXiv upload or publication was authorized or attempted. Visual PDF inspection
remains with the author, as previously requested.
