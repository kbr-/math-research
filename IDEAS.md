# Ideas for the framework

Draft begun 18 September 2026; now tracked. The user's notes are rewritten in prose.
Comments labelled **Assistant's comments** below are from Claude Fable. Additions labelled
**Codex comments (19 September 2026)** are from GPT-6 Astra. These are proposals, not active
workspace rules or authorization to launch parallel research or formalization.

Implementation checklists: [one plan per idea](research/notes/INDEX_MIGRATION.md#separate-plans-by-idea).
The index plan covers item 5 and index curation only.

## 3. Parallel agents on separate worktrees pursuing alternative next steps

**The idea.** Spend more tokens per unit of time: several agents in separate worktrees each take
a different candidate "next step", and the best branch wins.

**Assistant's comments.**

- The infrastructure mostly exists: Spin-formalize-parallel already runs workers in worktrees
  with a coordinator, and the resource controls are shared across worktrees. The plan limits
  were far from binding in the measured session (11% of the five-hour window after 1 h 45 min
  of Fable), so three or four workers are affordable.
- Where it pays: at genuine forks, when the remaining route lists two or three mechanisms and
  nobody knows which to refine; and when cycles keep stalling on the same obligation, where a
  fresh-context agent is a better falsifier than the one with sunk cost. Where it does not pay:
  when the next step is clear; parallel workers then duplicate the Resume reading (about 45k
  tokens each) and produce near-identical entries.
- Two protocol variants worth having:
  1. Explore: the coordinator writes N distinct assignments that must attack different
     obligations or different mechanisms (state this constraint; otherwise the workers converge
     on the same obvious step). Every branch is recorded, including the losers: failed attempts
     are part of the record and prevent repetition.
  2. Adversary: one worker develops the argument, another tries to break it (known obstructions,
     hard instances, boundary cases), with no shared context. The AGENTS rule "try to falsify
     the intended general claim" is better done by someone who did not write the claim.
- Integration is the hard part. Append-only entries all go before the same marker comment in
  `notebook.html`, so every merge conflicts there. Options: a script that re-appends the
  incoming entries in chronological order (deterministic, no manual conflict resolution); or
  workers write only their entry and the coordinator does the append. Living sections stay
  coordinator-only, as the existing parallel-formalization rule says.
- Compute contention: research workers are light, but parallel Lean builds all share the
  14-CPU, 10 GB budget. Limit to one formalization worker at a time or give each an explicit
  thread count.

**Codex comments (19 September 2026).**

- Agree at genuine forks. Assign a common mathematical interface and budget, but distinct
  hypotheses to test. Preserve every branch's result; choose which result to pursue next,
  rather than treating the other records as disposable losers.
- `tools/merge-formalization-appends.py` already handles a restricted append-only merge.
  Extend that existing mechanism if needed. Preserve released entries and their dependency
  order; do not globally reorder the historical record by wall-clock timestamps.
- Give an adversary the exact statement and relevant source assumptions, without the
  author's persuasive narrative. Fresh context is useful; missing definitions are not.
  Start with two bounded workers and measure duplicated reading before scaling up. Historical
  usage figures are not evidence of the current token or compute headroom.

## 4. Formalize everything, then require formalization on every cycle

**The idea.** Bring the whole notebook to Lean, then make formalization part of each cycle so the
verified frontier never lags.

**Assistant's comments.**

- "Everything" is more than can be formalized: much of the record is obstructions to methods,
  finite computations, conjectures and failed attempts. What can be formalized is the set of
  results later cycles build on. So formalize the frontier, not the history: every claim that
  enters Working mathematical context as an active tool, and every dependency of a result that
  is flagged under idea 2.
- A rule that bounds the debt: a later cycle may cite a claim as a dependency only if it is
  formalized, or else must name it as an unverified dependency in its own status line. The
  companion-degree discrepancy found during the bit-PHP formalization is the argument for this;
  it had propagated through several downstream uses before Lean caught it.
- Per-cycle formalization roughly doubles the cost and time of a cycle (formalization cycles
  were the expensive ones in the cost report), and it slows exploration at exactly the moments
  when exploration is the point. Two cheaper shapes:
  1. Statement-first: each cycle formalizes only the Lean statement of its new claim (an
     interface module, no proof). This is cheap, catches ambiguity in hypotheses and degree
     conventions immediately, and leaves the proof for a later sweep.
  2. Asynchronous: research and formalization run concurrently in separate worktrees (idea 3);
     the formalizer works down the list of unverified active tools, and the claim index shows
     which are done. Research is never blocked, and the verified frontier catches up during quiet
     periods (nights, or while the user is reviewing a paper).
- Expect corrections. If formalizing the older record finds discrepancies, that is the value, not
  a cost; the correction policy (new dated entry, gaps section) already handles it.

**Codex comments (19 September 2026).**

- I would not require Lean on every exploratory turn. Prioritize publication dependencies,
  claims used repeatedly, and uncertain interfaces whose failure would invalidate much work.
  Obstructions and finite certificates can also be formalized; their priority depends on use,
  not on whether they are positive theorems.
- Statement-first work is specification, not verification. Isolate unproved interfaces from
  verified modules, and prevent an assumed statement from making downstream results appear
  fully verified. The scope comparison between the informal and formal statements still matters.
- Prefer "not formally verified" to "unverified" for a mathematically reviewed working proof.
  Asynchronous formalization is attractive once explicitly assigned, with a clear notification
  path when a discrepancy affects ongoing research.

## 6. Interruption notes — deferred pending evidence

The remaining part of the small-utilities idea is whether narrowly scoped
work-in-progress notes save more recovery work than they cost to maintain.
Evaluate several ordinary resumes before deciding on a trial; do not introduce
a mandatory note on every cycle. Existing plans already preserve work in progress.
See [the remaining workflow-utilities tasks](research/notes/WORKFLOW_UTILITIES_PLAN.md).

Recovery instrumentation and the benchmark map are implemented and listed under
Completed below. Neither proves that interruption notes would be worthwhile.

## 8. Claim graph: structured, visualized on GitHub Pages

**The idea.** Represent the claims and their relations as a graph in a structured format that a
visualization tool can read, and render it on GitHub Pages: zoomable, inspectable, with links
into the notebook.

**Assistant's comments.**

- Data model. Nodes are claims (the labels of the claim index) and possibly entries; a node
  carries label, statement, status code, topic, date, notebook anchor, Lean file, significance.
  Edges are typed: `depends_on`, `refines`, `supersedes`, `corrects`, `rediscovers`,
  `formalizes`, `applies` (a special case used as a test), `obstructs` (an obstruction to a
  method). This is the structured claim source of idea 5 with edges added, so one file feeds
  the index, the search tool, the fossick scan and the graph. Plain JSON `{nodes, edges}` is
  enough; emit GraphML or DOT from it for Graphviz and Gephi users.
- Where the edges come from. This is the real work: today dependencies live in prose. Two
  sources: (1) bootstrap automatically from the entry links, since every `<a href="#anchor">`
  from an entry to an earlier entry or claim is a candidate edge, typed `cites` until reviewed;
  (2) require new entries to declare their dependencies in the status line or the index row
  (`depends_on: lem:x, thm:y`), which `finish-turn.py` validates against existing labels. The
  automatic edges can be upgraded to typed ones during the index audit cycle.
- Rendering. `tools/build_pages.py` already builds the Pages artifact; add `graph.html` that
  loads the JSON and draws it with a client-side library from a CDN (Cytoscape.js or d3-force;
  vis-network is the simplest for click-and-inspect). No installation and no build step; a
  vendored copy of the library keeps local live mode working offline. Features worth having:
  zoom and pan, colour by status, shape by type (theorem, obstruction, finite check), size by
  in-degree, click a node for a side panel with the statement and links (notebook entry, Lean
  file, index row), highlight ancestors or descendants of a node, filter by topic, status,
  formalized or not, and date range, and a "route" view showing only the nodes cited by the
  current Working mathematical context.
- Layout. 719 nodes is fine for these libraries but unreadable as one hairball. Cluster by
  topic with collapsible groups, or lay out by date on one axis and topic on the other, which
  also shows how the research moved.
- What it buys beyond a pretty picture. Load-bearing claims are the high in-degree nodes, and
  those are the formalization priorities of idea 4. The verified frontier is visible as the
  boundary between formalized and unformalized nodes. A correction's blast radius is the
  descendant set of the corrected node, which is exactly the audit scope the formalization
  rules ask for. Rediscoveries show up as near-duplicate nodes with no edge between them.
  Dead branches are components with no path to the current route.
- Keep it honest. The graph should show only edges that exist in the record; it is navigation,
  not a proof certificate. A `depends_on` edge means "the entry uses this", not "the dependency
  has been checked".

**Codex comments (19 September 2026).**

- Build this after the structured registry has a useful set of reviewed edges. A one-hop
  dependency view around a selected claim is a better first interface than the whole graph.
- Preserve edge provenance and review state. A hyperlink may cite a counterexample, contrast
  an older approach, or explain history; it is not automatically a proof dependency. Likewise,
  missing edges mean the graph is incomplete, not that a claim is independent.
- Citation count alone does not identify the most important claims, and disconnection from
  the current route does not make a result worthless. Formalization priorities should also
  reflect uncertainty and consequence of failure. Descendant traversal suggests an audit
  scope; whether the correction actually invalidates each use still needs mathematical review.
- A CDN library is still a dependency even without an installation step. Choose and approve
  that dependency explicitly when implementing the visualization, following the existing
  dependency policy; prefer a pinned local asset if offline reproducibility matters.

## 10. Structured Git merge drivers for notebook and claim additions

Implementation plan: [GIT_MERGE_PLAN.md](research/notes/GIT_MERGE_PLAN.md).

**The idea (20 September 2026).** Automatically resolve independent notebook
appends and claim-index additions during rebase/merge, while retaining genuine
conflicts. Side notebooks reduce contention between different research threads;
merge drivers also help when two Git branches work on the same thread.

**Codex comments (20 September 2026).**

- Extend/consolidate `tools/merge-formalization-appends.py`, whose existing resolver
  is restricted to an older formalization workflow. Use separate rules for each
  authoritative format rather than treating structured content as arbitrary lines.
- For notebooks, match complete articles by stable ID, preserve existing entries
  byte-for-byte and in order, combine independent additions deterministically, and
  deduplicate identical additions. Reject different bodies with the same ID,
  deleted/modified history or malformed structure. Preserve each branch's addition
  order and account for dependencies; do not globally sort history by timestamps.
  Merge living sections normally and retain their genuine conflicts for review.
- For the claim registry, merge claims and relationships by ID. Independent additions
  and non-overlapping field changes can be combined; competing edits to the same
  field or incompatible deletion/edit combinations require review. Related fields
  may be semantically coupled even when their JSON paths differ.
- Combine distinct attention events while preserving each history's order. Equal
  timestamps do not make events identical, and event ordering affects the current
  disposition. Flag incompatible ordering rather than inventing a latest decision.
- Regenerate derived claim indexes, topic views and attention views from the merged
  authoritative data. Do not independently union generated Markdown. Determine a
  reliable regeneration checkpoint, since per-file drivers have no guaranteed order.
- Run structural, append-only, evidence-hash and dependency checks after merging.
  Never manufacture reviewed status or refresh evidence hashes just to make a merge
  pass: source changes may require a new substantive review. Surface stale metadata
  explicitly, even where the textual merge is clean.
- Extra whitespace cannot reliably separate appends at a common insertion point.
  Git's line-based `merge=union` can interleave repeated HTML/table markup; it is
  unsuitable here. Prefer a custom driver that refuses unsupported changes.
- Track path attributes and driver code, with an explicit per-clone setup step for
  Git configuration. Verify actual merge/rebase behavior, missing-driver behavior,
  duplicate IDs, conflicting edits and preservation of both sides' records before
  enabling automatic resolution. Avoid depending on a private one-off merge script.

**Commit hashes recorded in tracked files (25 September 2026).** Rebasing rewrites the hash
of every rebased commit, but tracked files keep naming the old ones, and no check notices.
A branch of 76 commits prepared for rebase onto `main` had three kinds of such references:
- review `revision` fields in `research/claims/index.json` (about 830);
- a preprint's Lean pin (`\leancommit`, checkout commands, the repository citation, its README);
- prose in a notebook entry and a review record.

`main` already carried 160 stale `revision` fields naming 21 commits that earlier rebases
had replaced. The mapping was recoverable only because the old commits were still in the
local object store: each matched exactly one commit on `main` with the same author timestamp,
subject and message, and a patch that differed only in re-rendered or conflict-resolved
files. After garbage collection that recovery would be impossible. So the integration
tooling should also:
- remap recorded hashes whenever history is rewritten. Git's `post-rewrite` hook receives the
  old→new pairs for rebase and amend, so it can apply them to the registry `revision` fields
  and to publication pins, then re-render; a merge driver alone never sees the rewrite;
- add a mechanical check (in `tools/check-claims.py` or `verify-checkout.py`) that every
  recorded revision and publication pin is an ancestor of the checked branch, so a stale
  hash fails before a push rather than being found later;
- repair the 21 known stale revisions on `main` with the recovered mapping
  ([research/provenance/rebased-revisions-main-2026-09-25.json](research/provenance/rebased-revisions-main-2026-09-25.json),
  old → new full hashes).

## 11. A searchable literature corpus: arXiv metadata, full-text and embedding search

**The problem (24 September 2026).** Prior-art checks are the weakest step of the workflow.
The multiplicity note answered a published question with a standard lemma (the DKSS
multiplicity Schwartz–Zippel lemma) that one of the question's authors had studied and
overlooked, as he confirmed by email. The novelty checks behind the headline items in
[ATTENTION.md](research/ATTENTION.md) are still outstanding. The verification gate searches
our own claim index, but nothing searches the outside literature systematically: web searches
are ad hoc, and `search-claims.py` only knows what we have recorded ourselves.

**The idea.** Keep a local corpus of arXiv metadata (titles, abstracts, authors, categories,
dates) for the relevant categories, fetched automatically and kept current. Search it **on
demand** whenever a cycle formulates a new lemma, obstruction or technique: first with
full-text search, then with embedding-based semantic search on the local GPU.

**Why on demand, not a relevance filter at arrival.** The first proposal was to classify each
new paper as relevant or not, with a cheap model, when it appears. The user rejected that,
correctly: relevance is not a fixed property of a paper. We started with no tools; expanders,
matching switching, chessboard-complex fillings and covering arguments were all developed
along the way, and the tools we will use are unknown. A filter written today encodes today's
route and would permanently discard the papers that supply tomorrow's tools, which are the
most valuable finds. So the corpus stores everything in the chosen categories, and the
questions change with the research: a paper that looked irrelevant in 2025 can surface in a
2027 query. Graph theory and combinatorics in particular are not "unrelated": we analyse proof
DAGs, and much of our machinery is combinatorial.

**Components.**

1. **Corpus and automatic fetch.** Harvest the whole arXiv history of the chosen categories
   once (not only recent years; see the coverage section below), then add new listings daily
   or weekly. arXiv permits this for metadata: the
   [API terms](https://info.arxiv.org/help/api/tou.html) put metadata under CC0 and ask for
   at most one request every three seconds on one connection; the
   [bulk-data page](https://info.arxiv.org/help/bulk_data.html) offers the API, OAI-PMH (the
   intended harvesting protocol, by set and date) and RSS. Full text is different: do not
   harvest PDFs programmatically or re-host them. The corpus is metadata only. For a large
   initial load, the bulk-data page points to a complete metadata snapshot (Kaggle, S3), which
   avoids paging through the API.
2. **Full-text search, no install.** Python's bundled SQLite has FTS5 (checked: SQLite 3.37.2
   with FTS5), with BM25 ranking and phrase and prefix queries answering in milliseconds over
   tens of thousands of abstracts. NumPy is also installed if a hand-written TF-IDF ranking is
   wanted. This is the baseline.
3. **Embedding search on the GPU.** A small embedding model maps abstracts and queries to
   vectors and ranks by meaning rather than shared words. Relevant combinatorics papers rarely
   use our vocabulary ("every bounded annihilator on a matching board extends" versus
   "homology of chessboard complexes"), which is exactly where keyword search fails. The
   machine has an NVIDIA RTX 3070 Laptop GPU with 8 GB of video memory; suitable models have
   from about a hundred million to a few hundred million parameters and need 1–2 GB of it.
   Embedding the two-year corpus once should take minutes on the GPU and the all-time arXiv
   categories somewhat longer (both to be confirmed by a sizing run); each query is instant,
   and the vectors take tens to hundreds of megabytes.
   Candidates: one general-purpose model and one trained on scientific papers, such as
   AllenAI's SPECTER family, which learns from citation links, close to our question "is this
   paper useful for that one".
4. **Hooks into the workflow.** Add a corpus search to step 2 of the verification gate,
   alongside the claim-index search, using the new lemma's own statement as the query. Use it
   in Fossick and in the novelty checks for ATTENTION.md items. Keep one light weekly skim for
   plainly on-topic papers (PHP, algebraic proof systems, Res(⊕), AC^0[p]-Frege), the one area
   where an up-front relevance judgement is safe; its findings go into ATTENTION.md or the
   notebook, not into a separate alert.

**Measured volume (arXiv API, 24 September 2026; categories include cross-lists).**

| Category | Last 4 weeks | Last 2 years |
|---|---:|---:|
| cs.CC | 163 | 2,460 |
| cs.LO | 165 | 3,783 |
| math.CO | 1,149 | 15,099 |
| cs.DM | 145 | 2,529 |
| All four, deduplicated | 1,485 | 21,723 |

That is about 370 new papers a week, too many to read in full, and a two-year backlog of
roughly 6–7 million tokens of abstracts.

**Coverage beyond the last two years (added 24 September 2026).** A two-year window cannot
serve the evaluation, or most prior-art checks: the literature the record actually relies on
is older. The arXiv API reports these all-time totals (including cross-lists):

| Category | All time |
|---|---:|
| math.CO | 82,593 |
| cs.CC | 13,450 |
| cs.LO | 20,240 |
| cs.DM | 16,174 |

That is about 115,000–130,000 papers after deduplication, still small. Of the evaluation
papers, DKSS (`0901.2529`, 2009) and Sauermann–Wigderson (`2010.00077`, 2020) are on arXiv;
Alon–Füredi (1993) and the BLVZ chessboard-complex paper (1994) are not. Anything from the
2000s on is mostly covered by arXiv; the classics are not. Sources for them:

- **zbMATH Open**: a mathematics-specific database reaching back to the nineteenth century,
  with an open API. Many records carry a reviewer's summary, which serves as the abstract for
  old papers. This is the best fit for exactly the Alon–Füredi and BLVZ kind of paper.
- **OpenAlex**: an open catalogue of most scholarly works, with a free API and a full data
  snapshot. It has abstracts for part of it and, importantly, citation links.
- **Semantic Scholar**: similar, but needs an API key.

ECCC is excluded: the user decided (24 September 2026) that the corpus must not harvest or
scrape it. Proof-complexity papers posted only there are reached through OpenAlex or
Semantic Scholar metadata and citation links, where those sources carry them.

Check each source's licence and rate limits before harvesting; do not assume they match
arXiv's CC0 metadata terms.

Citation links are a side door to the classics. Old papers are cited heavily by newer ones,
so once the arXiv records carry OpenAlex reference lists, "papers cited by the top search
hits" reaches Alon–Füredi even with no abstract of it on file. That is often how an expert
finds a classic too: through the recent paper that uses it.

"Abstracts of all mathematics" is within this machine's reach: a few million records, a few
gigabytes of text, embeddings of a few gigabytes stored on disk and searched from there, and
an embedding run of hours on the GPU rather than days (an estimate for a sizing run to pin
down). The limit is coverage, not compute: an old paper with no abstract or review anywhere
is invisible to text search, and only the citation route reaches it.

Stages, each evaluated on the known connections it should be able to find:

1. All of arXiv in the chosen categories. The evaluation then covers DKSS and
   Sauermann–Wigderson.
2. zbMATH Open for older mathematics, covering Alon–Füredi and BLVZ if their reviews are
   there.
3. OpenAlex citation links, for classics without usable abstracts and for follow-up searches.

**Assistant's comments (Claude Opus 5.5, 24 September 2026).**

- Evaluate before trusting either search mode. Use the literature connections the record has
  already made as test queries with known answers: DKSS for the multiplicity question,
  Alon–Füredi and Sauermann–Wigderson for its comparisons, the BLVZ chessboard-complex
  filling, and the sources behind the switching and expander tools. Each test counts only
  once the corpus stage that should contain its paper exists. Write each query in our
  own words and compare how highly FTS5, a general embedding model and a scientific one rank
  the known paper. If FTS5 already finds them, skip the install; if it misses many, that is
  the concrete case for the embedding stack.
- The install needs explicit approval under COMPUTATION_RULES.md: a virtual environment with
  PyTorch built for CUDA (several gigabytes) plus `sentence-transformers`, and one model
  download of a few hundred megabytes, all run through `./compute.sh`. Video memory is outside
  the 10 GB RAM-plus-swap budget, but the host process needs a few gigabytes of RAM that must
  actually be free. On 23 September a k3d cluster and the ChatGPT desktop app held about
  1.7 GB; available RAM rose from 4.9 GB to 6.6 GB once they were stopped.
- Storage: the arXiv metadata is CC0, so committing it is legally fine, but at tens of
  megabytes or more and fully regenerable it is better kept out of Git. Commit the harvest script, a manifest
  (categories, date range, counts, hashes) and the evaluation results instead. The embedding
  vectors are derived data and likewise regenerable.
- Choosing categories is itself an up-front relevance judgement, so keep the choice generous
  and revisit it. Candidates beyond the four above: math.AC (the Gröbner bases and Hilbert
  functions behind PC degree), math.AT (chessboard and matching complexes), math.PR (the
  permutation-probability tools) and cs.DS. Sources beyond arXiv and the citation route are
  in the coverage section above; "papers citing X" is also often the best way to find
  follow-ups to a known key result.
- Search results are leads, not verdicts. A missing hit does not establish novelty, and a hit
  must be read in the primary source before the record cites it, as the gate already
  requires.
- Automated requests should identify the tool in the User-Agent, but must not carry the
  user's email or other personal data unless the user asks. An early count script sent the
  user's address to arXiv by mistake.
- Practical note: Python's `urllib` got HTTP 406 from the API for date-range queries that
  `curl` served normally. Use `curl`, or set request headers deliberately.

**Considered and rejected: a decision model such as Jev.** TypeSafe AI's Jev (released
September 2026) returns probabilities over options fixed in advance, quickly and cheaply. It
does not fit the retrieval problem above, which ranks papers against statements that do not
exist yet. Nor should it choose research steps: that choice requires reading proofs and
recorded obstructions, happens once per cycle, has no outcome data to calibrate against, and
AGENTS.md forbids uncalibrated probabilities for research prospects. Its documented
sensitivity to prompt injection also matters when the agent that prefers one option writes
the option list. A cheap classifier could still serve a genuinely high-volume, low-stakes
triage task if one appears.

## Remaining implementation priorities

1. Add bounded parallel exploration and targeted asynchronous formalization when
   assigned (items 3 and 4).
2. Build graph navigation on the reviewed claim data (item 8).
3. Evaluate recovery evidence before deciding whether to trial interruption notes
   (remaining part of item 6).
4. Add structured integration support for notebook and claim additions (item 10).
5. Build the literature corpus in stages (all-time arXiv categories, then zbMATH Open, then
   OpenAlex citations) with full-text search, and evaluate embedding search against known
   literature connections before requesting the install (item 11).

These priorities are proposals, not authorization to launch the work.

## Completed

### 1. Fossick protocol: scan the research record for nuggets

**The problem.** The agent solved a twelve-year-old open problem (unrestricted Res(⊕) lower
bounds) and recorded it as casually as any other cycle: "here is a theorem, moving on". The
result was noticed only because the user happened to read that entry and asked for a
publication assessment. That was luck, not process.

**The idea.** A prompt, "Fossick", that scans the Research record for results of independent
interest. It should persist where the last scan finished and resume from there next time.

**Assistant's comments.**

- Why it was missed: the agent judges every result against the main goal (AC0[p]-Frege), so a
  theorem that does not advance that route reads as a tool or a side remark. Significance to the
  field is a different question, and nobody was asked it. The fix is to ask that question
  explicitly, at two moments: once per cycle (cheap, see idea 2) and periodically over the whole
  record (the fossick scan, which also catches what the per-cycle check missed).
- Implementation sketch:
  - `tools/fossick.py --next` prints the next unscanned entries (title, status line, claim labels,
    anchor) after a stored cursor, in bounded batches, without dumping the full entries. The
    cursor is the anchor of the last scanned entry, stored in a small tracked file
    (`research/notes/FOSSICK_STATE.md`) so the scan survives sessions and machines.
  - The prompt: for each entry, decide whether it contains (a) an unconditional theorem about a
    standard proof system, formula or object named in the literature, (b) a refutation of a
    published claim or conjecture, (c) a reusable general tool. For (a) and (b) do a targeted
    literature check and write a one-paragraph assessment. Append findings to a tracked
    `research/NUGGETS.md` (label, one-line claim, why it matters, literature status, suggested
    action), advance the cursor, commit.
  - Judge against the literature, not against the route. A results-first reading: "if a stranger
    posted exactly this theorem, would the field care?"
  - Keep the scan cheap: read status lines and claim-index rows first, open the full entry only
    for candidates. Working proofs and finite checks are the candidates; obstructions and failed
    attempts rarely are, though a clean obstruction can be a publishable negative result.
- A cheaper variant that needs no new tool: give the claim index a `significance` column
  (`route-only`, `tool`, `independent`, `open-problem?`) filled in at write time and reviewed
  during the fossick scan. The scan then reads one file.

**Codex comments (19 September 2026).**

- Strong priority. Separate discovery of a candidate from a novelty audit and publication
  readiness. A striking theorem or an agent's claim that it settles an open problem warrants
  attention; it does not establish novelty or correctness by itself.
- A cursor should mean "screened through here", not "everything here has been resolved".
  Preserve pending candidates separately, and link later corrections to previously screened
  claims. Otherwise an incremental scan silently misses changes to its earlier conclusions.
- Use one candidate register for Fossick findings and per-turn flags, with attention/review
  states. Separate `NUGGETS.md` and `FLAGS.md` would duplicate the same objects. Do not
  systematically discount negative results or failed attempts: the useful item may be the
  counterexample or obstruction they exposed.

**Completed 20 September 2026**, in commit `408ad76`. The [Fossick protocol](tools/FOSSICK.md)
is implemented and tested, with a durable `ended_at` marker and shared attention
handoffs. The separately authorized initial scan then completed all 887 starting
claims across 320 articles; see the [completion audit](research/results/fossick_goal_20260920/completion-audit.json).
Candidate reviews remain in the shared attention history.

### 2. Do not solve an open problem and walk away

**Completed 19 September 2026**, in commit `e1ae8c3`. Original proposal and comments
are retained below; the implementation uses shared metadata and file/console
notifications rather than separate FLAGS/NUGGETS files or a desktop hook.

**The idea.** An AGENTS.md rule so that a cycle which settles something long open raises a flag
instead of moving on.

**Assistant's comments.**

- Proposed rule (one paragraph, no checklist): "When a cycle produces an unconditional result
  about a standard system, formula or object with its own literature, add a Significance line
  to the entry status stating whether the result is new, known, or unknown after a targeted
  literature check, and append one line to `research/FLAGS.md`. The flags file is the list of
  items awaiting the user's attention; the user clears it." The Spin process-assessment step
  already asks what went wrong in the cycle; add "did this cycle produce anything an expert in
  the field would want to know about?"
- Make the flag visible outside the notebook. A tracked `research/FLAGS.md` is portable and
  survives compaction. On Claude, a Stop hook can also fire a desktop notification when the file
  gained lines during the turn (cheap, local, no dependencies). Codex has no equivalent hook
  that I know of, so the file is the primary mechanism.
- Over-flagging is the risk. Keep each flag to one line and let the fossick scan be the second
  filter. A false positive costs the user ten seconds; a false negative cost days here.
- The "Where we stand" section already has a "Publication side branch" paragraph. Generalize it
  to "Results of independent interest" with a link per result, so the living overview itself
  carries the list.

**Codex comments (19 September 2026).**

- Make the per-turn check cheap: flag a plausible candidate with its exact scope and why it
  might matter. Require targeted literature work when assessing that candidate, rather than
  automatically conducting a novelty search for every lemma about a standard object.
- Keep mathematical status, formalization coverage, and possible significance separate.
  "Unknown novelty" is an honest useful outcome. Keep a compact visible link to the candidate
  register in the overview instead of letting a second result catalogue accumulate there.

**Implementation update (19 September 2026).** The cheap check now reuses claim
metadata and the checkpoint gate; [attention](research/ATTENTION.md) is generated
from one decision history with bounded resume visibility. See the
[completed implementation plan](research/notes/SIGNIFICANCE_ALERTS_PLAN.md).
Fossick retrospective scanning remains separate.

### 5. Claim index: compression, deduplication, second-level index, retrieval tools

**Completed 19 September 2026.** All items in the
[index migration and curation plan](research/notes/INDEX_MIGRATION.md) are checked off.
Implemented in commit `cdaadcc`; the original proposal and comments are retained below.

**The idea.** The claim index is growing; review it for duplicates, add a second-level index or
grouping, and give agents a way to retrieve entries without loading the whole index into
context (the notebook excerpt tool does this for entries but not for claims).

**Assistant's comments.**

- Structure first: convert the index to a structured file (JSON or YAML) with fields such as
  label, one-line statement, status, topic, anchor, depends_on, superseded_by, formalized_in,
  significance, and generate the Markdown from it. Tooling then becomes trivial: search, topic
  listing, dependency graphs, "what cites this", and the fossick scan (idea 1) reads it directly.
  The Markdown stays the human view.
- Second level: a topic map of roughly thirty lines, one per topic, each pointing to its group of
  labels. Working mathematical context is already close to this role; the topic map would be
  its skeleton without the prose.
- Compression: mark superseded, retracted and rediscovered claims and move them to an archive
  section, so the live index lists only claims that a new cycle could still use. Nothing is
  deleted; the archive keeps the links. Do this in a periodic index-audit cycle, like the
  working-context consolidation, not on every turn.
- Retrieval: `tools/claim-search.py QUERY` over labels, statements and entry titles, printing
  matching rows only (label, status, anchor, one line), with `--show LABEL` handing off to the
  notebook excerpt tool for the full entry. Plain keyword or TF-IDF scoring in pure Python is
  enough and needs no new dependencies. An embedding index would need a library and approval;
  start without it.
- Duplicate detection can use the same scoring: list pairs of claims whose statements are
  near-identical, for the audit cycle to merge or link as rediscoveries.

**Codex comments (19 September 2026).**

- `tools/search-claims.py` already implements ranked, stemmed content-word retrieval. Extend
  it with exact-label lookup, status and source links before creating another search command.
- Structured data is worthwhile, but migrate incrementally and validate every label and
  target. Keep one editable source; generate the other views. Start with the fields already
  known reliably, leaving unreviewed dependencies explicitly unknown rather than inferred.
- Similar wording is a review hint, not permission to merge claims: encodings, quantifiers,
  degree conventions and hypotheses can make near-duplicates mathematically different.
  Preserve stable labels and correction links. Retracted claims must remain searchable so
  they are not rediscovered or used accidentally.

### 6a. Recovery instrumentation and bounded resume delivery

**Completed 19 September 2026.** The [recovery collector](tools/RECOVERY_EVIDENCE.md)
records explicit restoration and observable recovery proxies through existing tools.
The cached resume bundle currently fits three bounded, retryable calls; ordinary
notebook reads do not count as resumes. See the
[measured comparison](research/results/resume_protocol_comparison_20260919/README.md).
Typical token or recovery-time savings have not been demonstrated. Evaluating
ordinary resumes and deciding whether to trial interruption notes remain pending above.

### 6b. Open-problem and benchmark map

**Completed 19 September 2026**, in commit `360400a`.
[OPEN_PROBLEMS.md](research/OPEN_PROBLEMS.md) records precise formulations, dated
primary-source checks and links to relevant research for Res(⊕) size, size–width,
unary and bit PHP, AC⁰[p]-Frege PHP, and the no-MOD baseline. It is connected to
significance assessment and the Fossick plan. The map guides fresh novelty checks;
it is neither another candidate queue nor a permanent novelty verdict.

### 7. Context budget: the claim index and the Resume protocol

**Completed 19 September 2026.** See the [implemented context plan](research/notes/CONTEXT_BUDGET_PLAN.md)
and its measurement evidence. Hard budgets cover every pre-record region; original
proposals and comments are retained below.

**The problem.** The claim index costs about 90k tokens when read whole (GPT's estimate), and a
Resume costs 50–60k tokens before any work starts.

**Measurements (18 September 2026).**

- `research/CLAIM_INDEX.md`: 280 KB, 719 rows in one flat table, about 390 bytes per row, so
  roughly 70k tokens. About 22% of the bytes are URLs: every row carries two to four full
  `https://kbr.is-a.dev/math-research/#...` links. No topic sections, no grouping.
- Resume reading: the instruction files that every request carries (`AGENTS.md` 18 KB,
  `COMPUTATION_RULES.md` 13 KB, `research/AGENTS.md` 3 KB, `formalization/AGENTS.md` 7 KB when
  assigned) are about 40 KB, roughly 10k tokens; `RESUME.md` plus the living sections are 34 KB,
  about 8k tokens; the entry-title scan (`rg` over `<article|<h3>|entry-meta`) is 91 KB if run
  without the `tail`, about 23k tokens, and this is the largest avoidable item; the latest
  entries read afterwards are 5–15k. The harness's own system prompt and tool definitions add a
  fixed 15–20k. Working mathematical context is about 1451 words against the 1,000-word target,
  so its consolidation is overdue and would cut the living sections roughly in half.

**Assistant's comments.**

- Never read the index whole. That is the single biggest saving, and it needs only the search
  tool from idea 5: `claim-search.py QUERY` returns matching rows, and the AGENTS rule "search
  the index before naming a result" changes from "open the file" to "run the tool". With the
  structured source of idea 5, the tool reads JSON and the Markdown is only for humans.
- Shrink the rows for the cases where it is read: relative anchors (`#anchor`) instead of full
  site URLs, one link per row (the full record; statement and Lean links live in the entry),
  and short status codes (`proof`, `lean`, `finite`, `obstruction`, `conjecture`, `retracted`)
  with the long status text kept in the entry. Together this is about a 50% cut with no loss of
  navigation.
- Split by topic once the index is structured: one generated Markdown file per topic under
  `research/claims/`, plus the thirty-line topic map. An agent working on the affine route
  never needs the chessboard rows.
- For Resume: replace the `rg` scan with a `tools/notebook-toc.py` that prints one compact line
  per entry (date, anchor, ten-word title) with `--tail N` and `--since DATE`; 233 entries fit
  in about 5k tokens, and the default tail of 30 in about 1k. Make the living sections the
  only mandatory read, and read entries by anchor only when the task needs them.
- Consolidate `AGENTS.md`. It has grown to 18 KB with dated authorization history, repeated
  policy statements and long checklists. Its own first section asks for a small framework. A
  pass that keeps every user constraint but states each once, and moves expired grants to a
  dated note, should bring it near 10 KB. This is paid on every request, so it is the cheapest
  saving per byte, even though caching hides most of the cost within a session.
- Keep the working context at its target. The 1,000-word rule exists; it has not been applied
  for a while because Spin cycles add faster than they consolidate. A dedicated consolidation
  cycle every N research cycles (or when the section exceeds 1,500 words, checked by
  `finish-turn.py`) would keep the Resume cost flat.
- What not to do: do not trim the entries themselves, and do not drop the append-only record
  to save tokens. The cost problem is in what is read by default, not in what is stored.

**Codex comments (19 September 2026).**

- This is an immediate improvement, independent of a JSON migration. The existing search and
  excerpt tools already allow bounded reads. Add a compact TOC mode to the existing notebook
  tool instead of a second parser, and use bounded output that reports truncation explicitly.
- The living overview also needs consolidation. During this resume, **Where we stand** and
  **The remaining route** had become substantial chronological histories, while only Working
  mathematical context has a size target. Keep the current conclusion, decisive obstruction
  and next obligation in the overview, with links to the full history. Trimming only Working
  mathematical context will not fix that growth.
- Plain `#anchor` links in a GitHub Markdown index target that Markdown page, not the live
  notebook. Compact links must still resolve correctly in each rendering surface; shorter
  agent-facing tool output is a safer first saving than globally rewriting public links.
- The dated byte counts above are snapshots, not token measurements. Judge improvements by
  the text actually loaded during restoration and whether it retains necessary hypotheses.
  Consolidate duplicate rules and expired grants without erasing current constraints.

### 9. Side research notebooks with shared claim infrastructure

**Completed 20 September 2026**, in commits `3fcd105e` and `eef76117`.
[SIDE_BRANCHES_PLAN.md](research/notes/SIDE_BRANCHES_PLAN.md) records the checkpoints and
acceptance; use [the workflow](tools/SIDE_NOTEBOOKS.md). Original proposal and comments
follow.

**The idea (20 September 2026).** Give each side research branch its own notebook,
initially with an empty research record and living sections adjusted to its goal.
Serve it locally and on GitHub Pages at `/math-research/branches/<name>/`, alongside
the main notebook. Support multiple such notebooks while sharing the claim registry
and other framework infrastructure. This avoids temporarily replacing the main
notebook's goal and then discarding the side branch's living sections at integration.

**Proposed `Branch` protocol in `PROMPTS.md`.** Invoke it by naming the protocol
and describing the new research goal, optionally referencing the notebook entry
where the goal was first identified (for example, `Branch: investigate the
odd-field double-covering question discussed in <entry link>`). The agent reads
the referenced entry and relevant claim/dependency records, then invokes the
appropriate setup tools to create the new research branch and its side notebook.

The protocol initializes an empty research record and fills the pre-record
sections with the new goal, starting position, remaining obligations, proposed
first step, necessary mathematical context and any applicable formalization gaps.
It links inherited results to their existing records, preserves their hypotheses
and review status, and does not copy the parent notebook's research history or
invent progress. Setup includes a stable research-thread name, navigation and
source-link registration, context-budget configuration, and selection of the new
notebook for subsequent restoration and research tools. Any Git branch/worktree
created for the assignment is associated with, but distinct from, that stable
research-thread identity. The agent verifies the initialized notebook and reports
its path/URL and initial scope. Opening the branch does not itself authorize
unbounded research, parallel agents or publication.

The `Branch` protocol is now available in `PROMPTS.md`. Implementation used
temporary test notebooks; no side mathematical investigation was started.

**Codex comments (20 September 2026).**

- Use stable research-thread names independent of Git branch names: a Git branch
  can be renamed or deleted without breaking published source links. Each notebook
  retains its own goal, status, remaining route, next step, working context,
  formalization gaps and append-only record after integration into main.
- Keep a small directory of side notebooks with goals and active/completed/abandoned
  status. Each notebook identifies its thread and links back to the main notebook.
  A result useful to the main goal gets a brief integration entry there linking to
  its full argument; do not duplicate proofs or discard unsuccessful side records.
- Share global claim IDs and relationships. Source locators must identify both
  notebook and anchor; cross-notebook dependency and correction links need to work
  in local serving, GitHub Pages and source/evidence checks.
- Parameterize existing restoration, excerpt/search, context-budget, timing/finishing,
  append-only, source-validation and publication tools. Preserve the main notebook
  as the default. Give each side notebook explicit living-section budgets and
  restore only the selected thread plus relevant shared dependencies, not every
  notebook. Do not fork the framework into separate implementations.
- Reuse the existing lazy math rendering and navigation. Search can default to the
  current notebook with an explicit all-notebooks option; load broader indexes on
  demand so adding threads does not slow every page's startup.
- The odd-field multiplicity/double-covering question is a proposed first use case,
  not an assigned investigation or a claim that a short proof is available.
