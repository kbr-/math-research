# Parallel classification: registry positions 360–519

This worker reviewed the original summary/assessment and bounded notebook packets
for 160 claims against baseline `dc1d95b4cb6a463436256b830afd69029c1dc3ed`.
It does not mutate the canonical registry, alter source mathematics, audit complete
proofs, rerun Lean, or establish novelty. Source-dependent status classifications
retain finite/model controls, conditional scope and explicitly verified coverage.
The entire original summary/assessment/record and formalization metadata are preserved.

## Deliverables and integration

- `patch.json`: integration-ready per-ID field values and reviews for
  mathematical status, topics and significance; exact source hashes and baseline
  claim-text fingerprint; one proposed topic definition.
- `specs.tsv`: individually chosen topic groups, significance categories and
  scope-sensitive rationales for every row (not an automatic keyword classifier).
- `packets.json`: complete saved compact extraction, with omissions and source hashes.
- `collect.py`: reproduction of packet collection.
- `build_patch.py`: writes and schema-validates the isolated proposed field changes;
  never writes `research/claims/index.json`.

Apply only each row's `fields` and corresponding `reviews`, preserving current
original text, formalization, relationships and unrelated reviews. Verify the
baseline claim fingerprint before applying. Add the proposed topic if absent; if
merging different topic wording, regenerate topic review hashes using the final
topic definition. No relationship review is made complete by this patch.

Counts: 160 status reviews, 160 topic reviews, 158 significance reviews, and two
explicit pending significance audits. They are the earlier binary Res(parity)
corollary and the odd-prime affine-disequality size theorem. The former belongs to
the existing publication chain and must not be counted as an independent second
result. The latter's full-field disequality rules differ from general equation
clauses; a primary-literature comparison remains necessary.

One new topic, `algebraic-branching-programs`, locates the formal matrix program
constructions and their scoped selector-realization width obstructions. It is a
subject tag, not a route or importance judgment.

## Suggested notebook record text

A parallel source-relative metadata pass covered the next 160 claims, spanning
selector-valued module interfaces, compact-bit filtrations and cube arguments,
source normalization, algebraic branching-program controls, the affine-clause
publication chain, and all-prime/shared-probe extensions. Each disposition used
an exact preserved indexed assessment and compact source evidence. No full proof
or literature audit was implied. The two possible publication scopes remain
pending the appropriate novelty comparison; the earlier binary corollary is
explicitly linked conceptually to the existing publication theorem rather than
counted anew. Dependency curation is untouched by this classification pass.

## Reproduction and limitations

Run from the repository root, inside the shared protected launcher:

```sh
./compute.sh run parallel_index_classify_360_520 --threads 1 --category local_processing -- \
  python3 research/results/parallel_index_classify_360_520/collect.py \
  --out research/results/parallel_index_classify_360_520/packets.json
./compute.sh run parallel_index_classify_360_520 --threads 1 --category local_processing -- \
  python3 research/results/parallel_index_classify_360_520/build_patch.py \
  --out research/results/parallel_index_classify_360_520/patch.json
```

The first unprivileged protected-job attempt could not reach user systemd; the
escalated invocation succeeded under the same shared limits. No resource limit
was bypassed. Timing began after policy reading. Extraction/review were recorded
under reading and implementation under coding; time after final export is excluded.
Worker elapsed intervals overlap the coordinator and other workers and must not
be summed as total wall-clock time.
