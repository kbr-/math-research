# Registry search for a test's missed claims: measurement, 16 October 2026

The queued build decisive-test-auto-search asked the finisher to search the registry on the words of
a review's Decisive test (Operation and Prediction) and of a research entry's named next attempt,
and to print the registered claims the entry does not cite. Its two motivating cases:

- the matched image review's decisive test (commit 33696f91a), which missed
  cor:growing-expansion-flat-removal and thm:growing-rank-gap-exclusion;
- the spread defect cover entry's next attempt (commit 85aa78616), which missed
  lem:weighted-chain-cells beside thm:growing-rank-gap-exclusion and thm:core-star-source-exclusion.

Measured on the registry of 16 October 2026 (4949 claims); outputs in the run files here. Two query
texts were used for the review case, and the table says which: the committed decisive test (250
words, rewritten after its review, so it no longer holds the union-bound wording that missed the
claims) and a paraphrase of that wording taken from the build item's text. The spread case uses the
next attempt's committed words.

| Method, query | Flat removal | Rank-gap exclusion | Chain cells | Core star | Cost |
|---|---|---|---|---|---|
| search-claims scoring, committed review test | 623 | 31 | — | — | 7.3 s per query |
| exact stems with idf, committed review test | 284 | 36 | — | — | 0.06 s |
| BM25 over exact stems, TeX removed, item's paraphrase | 1673 | 569 | — | — | 0.003 s per query |
| BM25 over exact stems, spread next attempt | — | 61 | 1362 | 462 | 0.003 s per query |
| one-hop registry neighbours of the claims the test text cites | absent (26) | — | absent (54) | — | — |
| two-hop neighbours ranked by shared stems | 100 of 156 | — | 195 of 277 | — | — |

Ranks are out of 4949 unless a pool size is given. No method puts a missed claim in a short list
(the best is rank-gap exclusion at 31). The misses were changes of vocabulary (a union bound over
label conjunctions against affine-flat removal; exact evaluation against branching on chain cells),
which neither the registry's words nor its edges bridge. The report was therefore not wired into the
finisher or the skeleton check: a mechanism needs a measured use, and here it measured none on its
own cases. Its code, removed before commit, is kept as uncited_report_removed.py.

The check is given to the reviewer instead (.claude/agents/medium-reviewer.md, Process audit):
search under the object's other names and report a recorded result the draft missed. This duty is
untested: no run here shows that such a search would have found these claims.

The scripts are one-off provenance of this measurement: they import from the session's scratch
directory and record its absolute paths, and are not rerunnable as committed.
