# Bounded tooling acceptance crosscheck

This is a tooling/wiring audit, not a completion declaration for index migration.
It compares implemented interfaces with INDEX_MIGRATION sections 6–13. No broad
test suite was repeated; the coordinator will run the combined integration suite.

| Requirement | Implemented evidence | Remaining acceptance responsibility |
|---|---|---|
| Minimal full inventory and exact lookup | `claim-index.py list`, `search-claims.py --show`, registry retrieval tests | Final migrated-label reconciliation and reviewed metadata coverage |
| Bounded source packets | `claim-dependencies.py packet`, prior five-case research-use evaluation | Exact proof reading whenever packet evidence is insufficient |
| Entire Research-record citation inventory | `record-scan`, `record-show`, `record_citations.py` and its tests | Run/persist current report; reconcile unowned/ambiguous evidence and semantic roles |
| Direct dependency discovery and decisions | `scan/show/decide`, graph query/audit interfaces | Review all required inventories and candidate dispositions; extraction is not acceptance |
| Topic/lifecycle navigation | `views bundle`, generated `views/topics.md`, explicit unclassified view, stable hashed filenames | Regenerate after final metadata edits; review taxonomy and scoped supersessions |
| Similarity-based duplicate aid | `views duplicates`, deterministic Jaccard candidates with no auto merge | Semantic review of hypotheses/encodings/costs and recording true relationships |
| Current correction visibility | Generated marked notices in primary renderer, scoped warnings in derived views | Correct structured scopes and dated links; renderer cannot discover omitted corrections |
| Source-backed new claims | `author template/prepare`; five explicit dispositions, evidence hashes, base conflict detection | Human judgments and final import against unchanged base |
| Changed-claim and missing-registration gates | `changed`, maintenance/registration checks in finalizer and CI | User-facing notebook inventory remains semantically truthful |
| Finalizer-safe evidence | `claim_evidence.py`, article/fragment versioned normalization, actual finalizer regression | Preserve raw legacy hash conventions; do not mass-refresh stale reviews |
| Correction/formalization/resume/parallel acceptance | Authoring fixtures plus merge and real finalizer suites | Coordinator's final combined tests and checked integration checkpoint |
| Portable checkout | Essential tool/test inventory, executable checks, tracked/fresh derived views | Stage generated files and run checkout/history checks when authorized |
| Machine-readable export | Existing `claim-index.py export --out PATH` | Produce/retain final export if needed by the plan; generator availability is not evidence of a final export |
| Formalization/significance curation | Schema, coverage, exact scope/artifact/review fields | Complete population and targeted novelty audits or explicit allowed pending dispositions |

Wiring added in this follow-up: `record_citations.py` and
`test_record_citations.py` in CI push triggers/test execution and checkout essential
files; registry guide documents both whole-record commands and their limits.
Verified the article evidence helper, unit test and actual finalizer test were
already in both inventories. The guide now explains normalized-new versus
raw-legacy evidence hashes without introducing another policy file.

Important limits: full-record extraction inventories explicit links/visible label
tokens, not every implicit prose citation. Source ownership remains a candidate.
Generated view/CI success alone does not settle graph completeness, novelty,
formalization scope consistency or duplicate semantics. Plan boxes should be
checked only after the corresponding current reports and substantive reviews exist.

No canonical registry, notebook, plan or Git state was modified. Timing session:
`parallel_claim_final_wiring_20260920`.
