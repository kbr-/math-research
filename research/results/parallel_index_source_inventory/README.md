# Full Research-record source inventory

This scan traverses the **entire Research record**, including unindexed articles,
not merely source regions already named in the registry. It records a snapshot
of 315 articles, 1,552 headings and 381 matched mathematical statement/claim-label
signals. The input notebook/registry hashes and base revision are in `inventory.json`.
The coordinator appended an entry while the worker was active; the saved hash,
not a claim about an immutable live worktree, identifies the final scan.

## Outputs

- `inventory.py --out PATH`: read-only inventory generator using the existing
  Notebook parser and canonical source references; no registry mutation.
- `inventory.json`: complete heading inventory, all matched signals and bounded
  context, exact section hashes, direct/enclosing/fragment ownership, sibling
  article claims, and all candidate gaps.
- `candidates.tsv`: all 91 candidates in compact form (priority, anchor, heading,
  spot-review disposition, line). No truncation.
- `triage.json`: targeted review of 18 concrete candidates or false positives.
- `summarize.py --out PATH`: generates the complete TSV and checks accounting,
  scheduled work and indexed nonheading-anchor controls.
- `timing.html` and archived session: measured worker evidence.

Run the two scripts via `./compute.sh run parallel_index_source_inventory
--threads 1 --category local_processing -- python3 SCRIPT --out PATH`.

The final snapshot has 1,067 directly indexed headings, 312 entry-title overviews,
46 unowned setup/proof sections, 81 unowned mathematical sections, ten unowned
statement-signal sections, 35 unrecognized/nonmathematical sections and one
coordinator-scheduled section. The priority subset contains seven high and 84
medium candidates. The remaining lower-priority sections are still retained in
`headings` and `all_unowned_headings`; they have not been silently discarded.
All actual indexed notebook anchors resolve, including the nine paragraph/list
anchors that a heading-only parser would miss. Entry metadata and HTML attribute
inventories are not counted as new prose claims. Historical labels are recognized
separately from current registry labels.

## Concrete priorities

1. **`many-out-rows-lemma`** states a separate probabilistic reduction with an
   explicit exponential bound; its article indexes only the trigger-label
   observation. It invokes out-loading and should be included in the current
   negative-association audit before assigning a mathematical status.
2. **`product-sampler-preliminary-bound`** proves a separate random-product
   character/sampler estimate. A later better generator does not erase this
   recorded preliminary result.
3. **`literal-star-cover-normalizers`** supplies a reusable k-star normalization
   construction with original-degree images. It may need its own claim or explicit
   ownership as an ingredient of the existing restriction theorem.
4. **`frontier-exposed-requests`** gives an OR-free outer-frame degree statement;
   check whether an existing MOD/copy claim intentionally includes it.
5. **`random-flat-light-lemma`** explicitly transfers an earlier switching lemma
   and saves its finite verification. It may need a source link or a scoped reuse
   entry rather than a new independent theorem.

These are navigation/completeness findings, not new mathematical claims. Exact
statements were spot-read only for prioritization; no new proof or correctness
judgment is asserted. `pinned-class-reduction` is already scheduled by the root
coordinator and must not be duplicated.

Examples of false-positive distinctions: the level-one conjecture is already
indexed through its paragraph anchor; the BLVZ interface explicitly names an
existing third-party claim, so a missing historical source link is not a missing
imported theorem. Verified Lean statement subsections often belong to existing
formalized claims. Positive/negative case headings can be parts of one indexed
proof. A literature scope audit or failed counterexample is not automatically a
new theorem. The exact choices and remaining editorial questions are in triage.

## Scope and controls

Automatic heading accounting, the concrete missing-lemma signal, the scheduled
pinned-class work and the indexed nonheading conjecture were checked. The scan
adds unformatted labels to code/backtick labels and bold/plain paragraph statement
markers. It also retains unowned sections containing mathematical delimiters even
when their titles do not say theorem or lemma.

This is **not a completeness proof for arbitrary natural-language mathematics**.
A new assertion can occur inside an already indexed passage, a statement can have
no recognizable marker, and a whole-article source link is only broad ownership.
The report preserves those distinctions; the 91 candidates are not 91 confirmed
omissions. A source-link edit or new registry record requires ordinary semantic
review. Existing append-only notebook prose must remain intact.
