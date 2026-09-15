# Prerequisites for an arXiv v1

This is our recommended readiness threshold for the bit-PHP lower-bound
paper, not an arXiv requirement or a guarantee of acceptance. A green light
means that posting a carefully prepared, explicitly unreviewed preprint is
reasonable. It does not mean that external peer review has occurred.

Complete the common checks, **one of the two validation paths**, and the
release checks below. Full Lean verification can support publication before
an independent expert reading; both paths are not required.

**Readiness review:** 15 September 2026. Validation path B is complete: the clean project
build, final axiom report, and fresh kernel replay passed. Submission packaging
was subsequently authorized and the exact source archive compiled successfully. Checked boxes refer to the evidence in
[READINESS_AUDIT.md](READINESS_AUDIT.md), not to independent peer review.

## Common mathematical checks

- [x] The statement specifies the usual bit-PHP encoding, unrestricted
  DAG-like resolution over parities, the exact inference rules, and the
  asymptotic proof-size bound with all quantifiers. No unintended regularity,
  width, or proof-depth restriction enters a definition or hypothesis.
- [x] The end-to-end proof and its dependency chain are complete. Encoding
  changes, simulation overheads, ordinary degree conventions, and the final
  parameter inequalities are checked. There is no known unresolved
  mathematical gap. Finite computations support the argument without being
  presented as a proof of its asymptotic conclusion.
- [x] Refresh the
  [publication audit](https://kbr.is-a.dev/math-research/#bit-PHP-publication-audit-verdict)
  against relevant primary literature before release. Explain the distinction
  from regularity-restricted and depth-restricted results, and keep novelty
  claims within what the search supports.
- [x] The human author has read the manuscript, understands its stated scope,
  and takes responsibility for its contents. The paper claims the result
  actually established; the broader AC0[p]-Frege research goal remains
  separate.
  **Confirmed by the author in this session, 15 September 2026.**

## Validation path A: independent expert reading (not selected)

- [ ] At least one independent researcher with suitable proof-complexity
  expertise gives the end-to-end argument a substantive reading, including
  its critical interfaces and parameter accounting.
- [ ] Address the mathematical concerns raised, and retain an audit note
  describing the review's scope and the resolutions. An encouraging comment
  or a skim is not the review intended here.

This can be an informal expert reading. Journal acceptance or completed
formal refereeing is not necessary for this publication path.

## Validation path B: complete Lean formalization (selected)

- [x] Formalize the actual theorem, including the bit-PHP encoding, proof
  system, unrestricted proof objects, and final asymptotic size conclusion.
  Carefully compare the formal definitions, hypotheses, and quantifiers
  with the manuscript. Kernel checking verifies the formal statement;
  this comparison establishes what that statement means.
- [x] Prove the full dependency chain. Imported mathematical results must
  be proved in the pinned libraries or project. Declaring the chessboard
  homology input, an ENS transfer, or another needed lemma as an axiom leaves
  this path incomplete.
- [x] Inspect `#print axioms` for the final theorem. The standard foundational
  axioms `propext`, `Classical.choice`, and `Quot.sound` are acceptable.
  There must be no `sorryAx`, unproved custom assumptions, or unchecked
  shortcuts. For this route, use proof evidence that passes kernel checking
  without additional native-evaluation trust axioms.
  **Evidence:** [final theorem type and transitive axiom report](../../research/results/r25_publication_20260915/verification-final.txt); only the three allowed foundations occur.
- [x] Pin Lean and library versions, retain all project sources, and document
  the commands. Reproduce a clean build and a fresh kernel recheck, using
  `leanchecker --fresh` on the final theorem's module. Preserve the
  verification output and the exact checked commit.
  **Completed:** an isolated clean build of both project claim directories passed,
  using the pinned library caches. See [build evidence](READINESS_AUDIT.md#build-and-axiom-evidence).
  **Passed:** the bundled `leanchecker --fresh claims.BitPHPSuperpolynomial`
  exited successfully without diagnostics in 4 min 22.98 s. The module and
  imported declarations were replayed in a fresh environment. See the
  [kernel replay evidence](../../research/results/publication_kernel_replay_20260915/replay.json).


These checks follow the
[Lean proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).
With this path complete, an independent expert reading can follow arXiv v1.
It remains valuable for interpretation, novelty, and exposition.

## Release checks and sequence

- [x] The self-contained manuscript, bibliography, TeX sources, and rendered
  PDF agree. All claimed verification applies to this exact revision.
  **Evidence:** [reviewed source/PDF hashes](reviewed-files.json), successful
  rebuild without warnings, and the unchanged published Lean source revision.
  Refresh this check after further manuscript edits.
- [x] State the review status accurately. Under path B, identify the formally
  verified theorem and link the reproducible Lean project; describe the paper
  as not yet externally peer reviewed when that is the case.
- [x] Preserve the human authorship and disclose the substantial AI
  assistance. arXiv requires disclosure of significant generative-AI use and
  keeps responsibility with the human author; AI tools are acknowledged,
  rather than listed as authors.
  [arXiv moderation and AI policy](https://info.arxiv.org/help/moderation/index.html)
- [x] Follow the repository's [attribution and licensing](../../LICENSE) and
  [third-party source policy](../../THIRD_PARTY_NOTICES.md) when preparing the
  submission package. Follow [AGENTS.md](../../AGENTS.md) for publication authority.
  **Passed:** the source-only archive contains the ten TeX files and CC BY 4.0
  license text. Its extracted contents compiled without warnings; no private or
  third-party source copies are included. See [package manifest](submission-package.json).

The intended sequence is **arXiv v1 → expert feedback and/or journal or
conference refereeing → revised arXiv v2, v3, …**. The initial preprint is
already v1; earlier versions remain publicly accessible.
[arXiv replacement policy](https://info.arxiv.org/help/replace.html)

arXiv moderation is separate from peer review.
[arXiv moderation policy](https://info.arxiv.org/help/moderation/index.html)
