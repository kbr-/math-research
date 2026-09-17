# Ideas for the framework

Draft, 18 September 2026. Untracked on purpose; commit when it settles. The user's notes are
rewritten in prose; the assistant's comments follow each one, marked as such.

## 1. Fossick protocol: scan the research record for nuggets

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

## 2. Do not solve an open problem and walk away

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

## 5. Claim index: compression, deduplication, second-level index, retrieval tools

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

## 6. Smaller things noticed along the way

- The cost report's "working file per cycle" idea (append intermediate findings during a long
  cycle so an unexpected compaction loses less) worked in the preprint-revision cycle: the notes
  file plus the checklist ticks carried the plan across a compaction. Worth making a habit for
  cycles expected to exceed half an hour.
- Fossick and the per-cycle significance check both need a maintained list of the field's open
  problems and benchmarks (for this project: Res(⊕) size, size–width, unary PHP in Res(⊕),
  AC0[p]-Frege PHP, and so on) with citations. A short `research/OPEN_PROBLEMS.md` would make
  "is this known?" a lookup rather than a search each time.

## 7. Context budget: the claim index and the Resume protocol

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
