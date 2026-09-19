# Structured claim registry

`index.json` is the single editable source of continued-research claim metadata.
`../CLAIM_INDEX.md` is generated navigation. The notebook remains authoritative
for mathematics and current research status; this registry does not replace it.
The historical handoff index is separate and unchanged.

## Find a claim without loading the index

From the repository root:

```bash
./tools/search-claims.py point support lower bound
./tools/search-claims.py --show lem:mp-telescoping
./tools/search-claims.py --has-lean -n 5
./tools/search-claims.py --status conditional -n 5
./tools/search-claims.py --formalization unknown --json --out /tmp/claim-results.json
./tools/claim-index.py list --fields id,summary --format tsv
./tools/claim-index.py list --topic bit-php --fields id,summary --format tsv
./tools/claim-index.py coverage --field formalization --state unreviewed -n 10
```

Search ranks content words, prints bounded summaries with status and a source
link, and reports omitted matches. `--show` returns full metadata and all links.
Read the linked notebook passage with `tools/notebook-excerpt.py ANCHOR`.
`--has-lean` means a Lean link exists, not that the whole claim is verified.
`--kind`, `--topic`, and `--formalization` filter reviewed metadata when available;
`unknown` is distinct from `not_started` and from verified coverage.

`list` emits every matching claim in registry order, without an implicit limit.
TSV output has no headers, scores, metadata, footer or truncated values. `--fields`
selects and orders fields; `--format tsv` also works for ranked search. Limits are
explicit with `-n`, and omission notices go to stderr. `--out` writes the selected
TSV/JSON data without echoing it. TSV escapes backslash, tab, newline and carriage
return as `\\`, `\t`, `\n`, `\r`; null is `\N`, distinct from a literal backslash-N.
Array/object fields use compact JSON inside one escaped cell. Use `--format json`
for lossless typed projections. Ordinary human-readable search remains bounded.

## Schema and scope

[schema.json](schema.json) defines version 2; [schema-v1.json](schema-v1.json)
retains import/backward validation. `claim-index.py upgrade --out PATH` adds the
new fields without inferring reviews. The standard-library validator
implements the vocabulary used by that schema and adds ID, reference and scope
checks. Unsupported schema versions, unknown fields and duplicate JSON keys fail.

Each claim has:

- `id`: the original stable label, including its prefix. Never rename it casually.
- `summary`, `assessment`, `record`: the original claim, status and full-record
  Markdown cells, preserved verbatim. `assessment` retains all qualifications,
  including partial verification, stronger hypotheses and corrections.
- `mathematical_status`: reviewed classification, or `null` when unreviewed.
- `formalization`: independent `status`, exact `scope`, and source `references`.
  Partial or complete classifications require a scope and reference. A complete
  classification is a human assertion about the exact claim, not a verdict of
  this metadata validator.
- `formalization.artifacts`: multiple verified/specification/counterexample scopes,
  declarations, files, and existing verification evidence; a counterexample does
  not verify the original false claim.
- `topics`: optional curated tags; an empty list means unclassified.
- `topic_definitions` at the registry root gives stable topic IDs and descriptions.
- `significance`: a structured category/rationale, novelty and publication status,
  references and next action, or `null`; independent of mathematical status.
- `reviews`: per-field reviewed/pending/not-applicable dispositions with source
  revision, date, reviewer, evidence hashes, rationale and next action. Missing
  field reviews mean unreviewed, not absence of applicable metadata.

The initial migration deliberately left the new classifications unreviewed. This does
not downgrade existing results: their full original assessments and Lean links
remain intact. Parsing prose into new mathematical judgments is separate curation.
Inline Markdown links are parsed into structured `references` in lookup/export
output; they are not stored a second time as editable metadata. Currently the
parser supports inline links, balanced parentheses, and angle-bracket targets;
unsupported link syntax fails rather than silently losing a destination.

`coverage` reports every field, pending reviews and stale evidence. With `--out`
it saves the complete report even when the displayed list is bounded. Notebook
evidence hashes cover exact anchored excerpts, so appending an unrelated entry
does not invalidate an existing review. Changed claim text, field values, topic
definitions or cited evidence do invalidate it. External URLs without a local
snapshot cannot be checked automatically for changes; a recorded literature
assessment is not a new literature search. Curation uses existing proof reports,
not an implied new kernel replay.

`formalization.status = "no_record"` has a narrow meaning: no explicit per-claim
mapping in the audited index links and per-claim Lean directories. It does not
assert that the mathematics has never been formalized or that an existing theorem
cannot imply it. These reviews also hash the audited Lean inventory; new or changed
artifacts make the negative mapping results stale until the census is refreshed.

## Dependency discovery and review

Use evidence extraction before opening long entries. For research orientation and status, topic or
significance curation, start with `tools/claim-dependencies.py packet --claim ID`:
it preserves the summary and assessment verbatim and selects bounded statement,
status and qualification excerpts (including adjacent formula blocks). `--out`
saves the packet with source hashes; `-n` and `--width` control displayed excerpts.
Omitted blocks, truncated text and widened source ownership are explicit.
The packet marks `proof_ready: false` and displays recorded formalization scope
when available. A five-case evaluation (partial formalization, conditional theorem,
correction history, finite check and theorem with omitted definitions) supports
orientation use; it does not establish extraction completeness. Follow the root
source-reading rule before relying mathematically on a claim. These
are retrieval aids, not complete proofs. Open a larger passage only to resolve
unclear scope, conflicting evidence or an unsupported judgment. Use dependency
candidates for relationships; do not reread every full source as a routine step.

Dependency evidence:

```bash
./compute.sh --threads 1 --category local_processing python3 tools/claim-dependencies.py \
  scan --out /tmp/dependency-candidates.json
./tools/claim-dependencies.py show --input /tmp/dependency-candidates.json \
  --claim thm:publication-Res-parity-bit-PHP --method lean_declaration_reference -n 5
```

The scan parses notebook regions once, inventories hyperlinks and explicit claim
labels, and finds Lean imports and declaration references outside comments/strings.
Shared or widened source regions and ambiguous targets are flagged. Each candidate
has a stable ID, extraction method, source locator, occurrences and evidence hashes.
Unmapped targets and external/file references are retained in the report. Context
snippets and keyword hints are aids, not semantic judgments; negation, unused
imports and helper declarations can defeat a naive dependency inference.

`decide --input PATH --candidate ID --state accepted|rejected|pending --reason TEXT
--reviewer NAME --date YYYY-MM-DD [--relation-id ID]` stores the review decision in
the registry's optional `dependency_decisions` list. Acceptance requires a matching
relationship already recorded in the registry; it does not create one automatically.
The command refuses stale evidence, and `show --state ...` rechecks current source
hashes. Repeated scans retain decisions by stable candidate identity; changed
evidence becomes stale. Review ambiguous snippets and the exact owning proof before
recording `depends_on`; ordinary citations stay distinguishable from proof use.

## Edit and regenerate

1. Add or update a claim in `index.json`. Preserve its ID and record precise scope
   in the assessment; link corrections to their new dated notebook entries.
2. Set reviewed classifications only when justified. Keep an old partial-scope
   qualification unless the full claim has actually been verified.
3. Run `./compute.sh --threads 1 --category local_processing python3 tools/claim-index.py render`.
4. Run `./compute.sh --threads 1 --category local_processing python3 tools/claim-index.py validate`.
   Use `--out PATH` to preserve the report, and the active research session when applicable.
5. Commit the source and generated Markdown together with the research checkpoint.

Rendering preserves row order and text, removes internal blank lines that break
Markdown tables, and escapes bare math pipes for GFM. `finish-turn.py` rejects a
stale generated index before stopping the clock. Checkout verification and the
claim-index CI check additionally validate local targets. External URLs remain
intact; validation does not fetch them or certify their mathematical content.

The parallel append helper merges new structured claims/relationships by ID,
then regenerates Markdown. Changes to existing records, conflicting IDs, or
other unsupported conflicts require manual review. Its legacy Markdown mode
remains available for older worktrees; new work must edit JSON.

## Changed-claim maintenance contract

The root AGENTS.md requires complete, evidence-backed metadata for new or
substantively revised claims. `tools/claim-index.py changed --base REV --out PATH`
pins the base commit and checks current working-tree changes against it. Use
`EMPTY` only to audit every claim as new. The turn finisher checks HEAD before
stopping its clock; CI checks the push/PR base, covering all commits being integrated.

- New claims or changed summary/assessment/source records require all five current
  field reviews. A reviewed empty relationship set is valid when its rationale
  explains the inspected scope. Absence of a formalization is separate from
  mathematical incompleteness.
- Metadata-only enrichment checks changed fields/reviews, allowing the historical
  backlog to be curated incrementally. Changed topic definitions affect all their
  users. Changed incident edges affect endpoint relationship reviews.
- Corrections and supersessions require an explicit new status review of the
  target. They do not automatically mark it false: partial corrections and
  refinements need their actual scope recorded. Preserve its stable ID and dated
  source; no silent deletion of indexed claims.
- Changed edges need source evidence and a review note. Candidates may remain
  unreviewed, but must be identified as such; discovery is not acceptance.
- Changed cited sources trigger their affected field reviews even if the index
  was not edited. Negative formalization-census staleness remains visible in
  coverage; it does not demand rereading every claim after a new Lean file.
- Pending/not-applicable dispositions need evidence and rationale. Pending also
  needs a specific next action. Passing this gate is not proof that pending work
  is complete or that the mathematical judgments are correct. It checks recorded
  scope, freshness and accountability, not the truth of proofs.

Untouched backlog does not block the current cycle, but stays in coverage and in
the migration acceptance requirements. Use exact source evidence for new reviews;
update original metadata through the JSON registry and regenerate human views.
Codex and Claude entry points inherit the root contract, as do all research and
formalization prompts. The parallel append merger preserves completed additions;
semantic changes to existing records still need manual integration and rechecking
against the pinned integration commit.

## Relationships and future graph clients

`relationships` is an explicit list, initially empty. Each edge has a stable
`id`, typed `source` and `target`, `type`, `evidence` locations, and `review_status`.
Endpoints use namespace `current`, `historical`, or `external`, plus `id` and
`locator` (`null` for current claims; a source location for other namespaces).
Current IDs must exist here; historical/external identities use their locator,
without copying the historical index into this registry.

Types are `cites`, `depends_on`, `refines`, `supersedes`, `corrects`, `rediscovers`,
`formalizes`, `applies`, and `obstructs`. Direction is subject to object: for
example, A `depends_on` B, or correction A `corrects` B. A reviewed edge needs
source evidence. A citation, unreviewed edge, and reviewed dependency are different
objects. Missing edges do not establish independence. No dependency was inferred
from hyperlinks during migration, and the graph is not a proof certificate.

```bash
./compute.sh --threads 1 --category local_processing \
  python3 tools/claim-index.py export --out /tmp/claims-export.json
```

The versioned export includes full claims, derived reference objects, typed edges,
the repository-relative `reference_base` for resolving relative links, and an
explicit incomplete-coverage notice. Search `--json` uses the same format
with selected claims, incident edges and match/omission counts. Future Fossick and
graph clients can use these interfaces without parsing Markdown tables.

## Graph queries and consistency diagnostics

```bash
./tools/claim-index.py graph successors thm:publication-Res-parity-bit-PHP
./tools/claim-index.py graph ancestors audit:ordinary-restriction-affine-family
./tools/claim-index.py graph cites lem:mp-telescoping
./tools/claim-index.py graph impact lem:mp-telescoping --out /tmp/impact.json
./tools/claim-index.py graph audit --out /tmp/graph-audit.json
```

For A → B (A depends on B), successors/descendants follow dependencies;
predecessors/ancestors find users. Immediate queries take one edge; transitive
queries return shortest witness paths. Default traversal uses reviewed
`depends_on` edges; repeat `--type TYPE` to choose other relations and use
`--include-unreviewed` explicitly for candidates. `cites` always finds direct
incoming citations, and `impact` finds transitive incoming dependencies, regardless
of `--type`. Impact identifies a review scope, not invalidity. Alternative proofs
and partial-scope edges still require inspection. Namespaces keep historical and
current labels distinct; use `--namespace` for non-current starting nodes.

Output is bounded by `-n` (default 20) and reports omissions; `--out` preserves
complete query results. The audit reports semantic duplicate edges (same type,
endpoints and scope), inconsistent review states or endpoint locators, self-links,
and dependency strongly connected components. Citation cycles are separate.
Cycles are review findings, not automatically rejected proofs: alternative proofs
or scoped statements may explain them. Structural diagnostics cannot detect all
semantic contradictions. These queries operate on the curated graph, which is
still incomplete; candidate extraction and claim-level review remain necessary.

## Migration evidence

The baseline is `21603c76b82afcc8d91014fa752e61e5cab690ac`.
All 866 labels and all three text fields were reconciled against that revision,
including 1,241 claim links and one preamble link. All local targets resolved.
Rendering repairs affect blank lines and bare pipes in 22 rows, not claim content.
See [the checklist](../notes/INDEX_MIGRATION.md) and
[reconciliation evidence](../results/index_migration_20260919/reconciliation.json).

To reproduce the one-time import into new files (the importer refuses overwrite):

```bash
./compute.sh --threads 1 --category local_processing python3 tools/claim-index.py import \
  --revision 21603c76b82afcc8d91014fa752e61e5cab690ac \
  --out /tmp/imported-claims.json --report /tmp/claim-reconciliation.json
```

`validate --baseline REV` is for checking a pristine migration, not for rejecting
legitimate later claim updates. No new dependencies are required.
