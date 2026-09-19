# Complete adjudication of the 91 source-inventory candidates

This completes editorial disposition of the frozen candidate list from
`../parallel_index_source_inventory/inventory.json`. It does not change historical
mathematics or claim exhaustive detection of unlabelled prose beyond that scan.

- `decisions.tsv`: one individually reasoned disposition for every candidate, in
  the original order; none remains a generic unreviewed placeholder.
- `passages.json`: exact historical source passages, compact text and surrounding
  indexed scopes used for adjudication. Raw HTML preserves every formula and
  qualification; no third-party paper text is included.
- `proposals.json`: all 91 decisions and **18 new historical claim proposals**, each
  with all five reviewed metadata fields, source evidence hashes and exact scope;
  **24 reviewed relationships** distinguish prerequisites and applications.
- `build.py --out PATH`: reconstructs and schema-validates the isolated append
  proposals using the current registry, without writing canonical files.
- `timing.html` and archived session: actual worker evidence, overlapping other
  workers and therefore not additive to their wall-clock totals.

The 18 proposals include an explicit companion-versus-factor control, an OR-free
frontier degree bound, two batching-method obstructions, a literal-star normalizer,
a preliminary sampler bound, a sparse-collision-residual obstruction, three
reader-method controls, and seven finite-check records. These are extractions of
existing dated mathematics, not new discoveries or freshly rerun computations.
No independent novelty or publication claim is made.

The many-out-row exponential bound is **conditional** on the recorded out-loading
estimate. The coordinator's newly recorded generic permutation negative-association
counterexample invalidates that generic proof input; it does not automatically
refute this more structured conclusion. Its unresolved mathematical premise is
explicit in its assessment, source evidence and dependency edge. Root-owned NA
and pinned-class records are not duplicated.

The other 73 candidates receive explicit existing-claim, proof, setup, supporting
check, duplicate, strategic-review or framework dispositions. In particular:

- The sharper compact heavy-term bound was already present in the current
  `thm:random-flat-literal-switching` summary; it needs no duplicate theorem.
- The conjecture paragraph and several controls already have nonheading source
  anchors. The finite conservativity suite is separately indexed by one proposal.
- Formal statements and certificate subproofs remain owned by their existing Lean
  claims. The earlier generic-CNF initial bridge and criterion were subsequently
  indexed and are not added twice.
- Corrections to the single-row full-class theorem remain its dated correction
  history. This adjudication does not certify its later probability inputs.
- Dated failed strategies and open-case assessments are not silently upgraded to
  theorems. Where an explicit reusable obstruction is present, its narrow scope
  receives a proposed entry; purely prospective assembly plans do not.

## Integration

Add all proposed claims before the proposed edges. Refresh affected existing-target
relationship reviews after merging; an incoming edge does not complete their own
outgoing inventories. Existing original text and formalization remain untouched.
The proposals link to the old append-only notebook statements; no historical
article content is rewritten. They can be described in the coordinator's new
framework checkpoint without claiming new mathematics.

`build.py` validates the complete isolated registry schema and current source hashes
through `make_review`. All 91 candidate numbers occur exactly once; the 18 append
decisions match the 18 proposed records exactly. Formalization `no_record` records
absence of a dedicated claim-to-Lean mapping in the audited inventory, with corpus
staleness hashes, not proof of mathematical nonformalizability.

Reproduce through the protected launcher:

```sh
./compute.sh run parallel_index_source_adjudication --threads 1 --category local_processing -- \
  python3 research/results/parallel_index_source_adjudication/build.py \
  --out research/results/parallel_index_source_adjudication/proposals.json
```
