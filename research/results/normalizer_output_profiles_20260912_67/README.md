# Normalizer output profiles and later packages

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-normalizer-output-profiles)
contains all claims, proofs, original-degree accounting, the selector control,
and the strategic discussion prompted by the user. No new mathematical numerical
run was needed.

For a k-input column tuple, choose a single nonzero witness at each nonzero
state. Its coefficient vector is an inverse nonzero value times one coordinate
vector. Common-zero states can reuse an existing vector because all companions
already vanish there. This gives at most k(p-1) output profiles, or k for Boolean
state values. Tracking the selector's zero-state flag adds at most one class.

The later package must use removed blocks through the specified outputs.
Refinements from multiple blocks in one column are charged multiplicatively.
Selector use requires the certified proper-normal-form input-replacement pass;
raw earlier inputs are not silently replaced by their output profiles.
The common bit-label example retains a largest class floor((n+1)/2) and hence
a linear-size hard residual for qualifying later packages at fixed p.

Exact proof dependencies read or retained:

- [Column normalizer and degree ledger](https://kbr-.github.io/math-research/#column-state-normalizer).
- [Full-input normal-form replacement](https://kbr-.github.io/math-research/#input-reduction-transfer).
- [Orbit-sum recognition](https://kbr-.github.io/math-research/#partition-statistic-recognition).
- [Common-partition transfer](https://kbr-.github.io/math-research/#partition-statistic-elimination).
- [Previous affine inventory and label control](https://kbr-.github.io/math-research/#entry-2026-09-12-affine-inventory-profiles).
- [Prior finite column evidence](../column_state_normalizers_20260912_46/checks-01.jsonl),
  not rerun here.

## Strategic source discussion, 12 September 2026

The user asked whether PHP remains a suitable target because stronger systems
have short proofs and the target formula has no MOD gates; they explicitly did
not request a switch. The notebook retains PHP and prioritizes a comparison of
known algebraic extension upper bounds with the actual ENS interface.

Sources consulted through public bibliographic pages, abstracts, and indexed
introductory text, without importing their complete proofs:

- Samuel R. Buss, Polynomial size proofs of the propositional pigeonhole
  principle, Journal of Symbolic Logic 52(4), 1987, pages 916-927.
  [Publisher abstract and metadata](https://doi.org/10.2307/2273826).
- Eli Ben-Sasson and Prahladh Harsha, Lower Bounds for Bounded-Depth Frege Proofs
  via Buss-Pudlack Games, ECCC TR03-004.
  [Primary report page](https://eccc.weizmann.ac.il/report/2003/004/).
- Russell Impagliazzo, Sasank Mouli, and Toniann Pitassi, The Surprising Power
  of Constant Depth Algebraic Proofs, ECCC TR19-024, including the indexed
  introduction of revision 2.
  [Report and version links](https://eccc.weizmann.ac.il/report/2019/024/).
  Their exact field and extension assumptions have not yet been audited for
  applicability to our prime-field ENS construction.

Only source locators and our own bounded summaries are retained here; this
record adds no third-party full text to the repository.

## Process and measurement scope

The initial mathematical outline was measured in the preceding cycle. This
session first completed the separately committed exact-anchor excerpt helper
and its checks. One JavaScript patch submission failed to parse before making
any edits; the corrected submission and the actual helper checks succeeded.
The user-requested source discussion was marked as a web window, including its
interpretation. Later exact theorem reads have their separate reading marker.

The helper checks covered real heading and article boundaries, explicit end
anchors, current-state extraction, and missing, reversed, and duplicate-anchor
failures with no partial stdout. Its first mathematical reads used the helper
successfully. This was utility verification, not a new mathematical finite check.

The timing fragment, provenance hashes, and archived session preserve the
measured evidence. Publication remained blocked by automatic review despite
standing user authorization; local research checkpoints continued.
Final preparation included a brief outline of the next extension-system audit;
that small mixed window is not retrospectively split into invented timings.
