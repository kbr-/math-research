# Noemesis research workspace instructions

These are explicit user constraints; later explicit user overrides take precedence.

This file owns research workflow, notebook editing, interaction and Git/publication policy.
[COMPUTATION_RULES.md](COMPUTATION_RULES.md) owns resource limits, execution, numerical
verification, test execution, timing and result retention. Read it before computations.
[PROMPTS.md](PROMPTS.md) defines named prompts; read the requested section before acting.

Keep one authoritative rule per requirement. Before changing instructions, locate the existing rule
by its purpose and the failure it should prevent, including synonyms and linked owners. Determine
whether the rule was missing, ambiguous, ignored or inadequately enforced. Extend, clarify, replace
or enforce that rule; do not append another account of the incident. A new rule needs an uncovered
requirement, not different wording of an existing one. Review instruction changes for both lost
constraints and duplication. Remove obsolete history, repeated examples and unnecessary attribution.

Only rules applicable to every notebook belong here. Goal-specific mathematics, admissibility,
priorities and bound comparisons belong in that notebook's living sections, normally **Route
decisions** in **Where we stand**. `tools/tests/test_agents_scope.py` checks vocabulary, not
semantic scope: ask whether another notebook could use each proposed rule. Read the owning file
before editing it; shared rules do not belong in `CLAUDE.md` or private memory.

Before naming any artifact, including a result folder, claim ID, anchor or session, list existing
uses of that name. Never overwrite or reuse an earlier artifact by accident.

## Restoration and research discipline

- Restore with `python3 tools/resume.py`, then read every listed part in full. On Codex, omit
  `max_output_tokens` on both `exec_command` and enclosing `functions.exec` directives for
  preparation and part reads. Retry a missing/truncated part without preparing another bundle or
  concatenating the whole bundle into one response. The bundle contains `research/notes/RESUME.md`,
  computation rules, notebook living sections, formalization gaps and compact contents; the harness
  supplies this file separately. Follow the guide without rereading bundled files. Load only
  relevant records and source passages, never the growing notebook record or claim index wholesale.
- Keep `php_codex_handoff/` immutable; its import is complete. New work belongs outside it, normally
  in `research/`.
- At a research cycle's opening, read **Open statements** and identify the stable statement and
  top-level remaining-route item being advanced. State the necessary missing implication, how the
  work tests or discharges it, and what evidence ends the test or changes the next action. Route IDs
  alone do not explain progress. Assess the current line rather than inheriting the previous gap.
- Prioritize necessary unproved obligations, highest risk first as identified by the latest review.
  Develop leads/bridges for a high-risk obligation lacking a mechanism instead of switching to
  easier lower-risk work. Read in full the parked or linked items the **Proposed next step** names.
  Before reopening an older question, search backlinks and read later developments; use the latest
  applicable restart conditions after checking whether they were fulfilled or replaced.
- Restricted examples must test a named general hypothesis, obstruction or mechanism. State it in
  **General statement.**, citing its registered all-parameter claim ID. A build entry declaring no
  claims states that none applies. Two finite-check-only research entries in a row on one route are
  refused; at most three of any five consecutive research entries on a route may register new finite
  checks other than refutations. Registered claims, not status wording, determine these counts.
- Test a mechanism against recorded obstructions, hard instances and allowed equivalent
  representations before refining it. Check preserved hypotheses and accumulated composition costs
  against the goal's budget. A simpler surrogate, equivalent reformulation or growing case list does
  not discharge the original implication. If cycles repeatedly leave it untouched, change mechanism
  or develop a lead/bridge in the next cycle and carry the failure to the scheduled review. Carry
  weak assessments and descents more than one reduction below every open statement to that review
  for revision of the list.
- Recheck standing hypotheses against the goal's instances each cycle. If those instances violate
  them, the line no longer applies. When an upper bound excludes a family, extract its structural
  reason, test it on other candidates and ask whether a stronger candidate or replacement evades it.
  Compare direct constructions, method repairs and specification changes by their effect on the
  missing implication; upper bounds are a test, not the default objective. State which proved
  properties a change preserves or trades away, and recheck nonvacuity and the full budget.
- For evolving specifications, distinguish structural admissibility from conjectural hardness. Adopt
  a refinement only with a proved nonvacuity witness at unbounded sizes within the encoding budget;
  otherwise label it provisional. Concrete families are existence/falsification controls, not
  restrictions on the abstract proof. A conjectured sufficient condition for a size lower bound must
  use the size and must not exclude refutations of every size in a complete proof system.
- Distinguish working proofs, imported statements, conditional results, finite checks, conjectures
  and refutations. Preserve source hypotheses, encodings, original joint degrees, parameter costs,
  versions and qualifiers distinguishing the target from related statements. A named source
  condition retains its defining clause, including whether it concerns the whole object or slices.
  Record complete arguments, actual tests, dependencies and remaining gaps.
- Folklore, remembered facts, experience and forecasts are not evidence. Support a decision or
  status by a proof, a source read in the cycle with its hypotheses, or a discriminating test at the
  sizes run. Otherwise label it an **untested hypothesis** and base no decision on it. A universal
  structural property requires its defining relation, not one instance differing from a familiar
  example.

### Record search and source application

- Before proposing a next step or naming/developing a result, run `tools/search-claims.py WORDS` or
  `--show LABEL`. Before drafting each new lemma, search by technique, structural names/synonyms,
  dual or adjoint form, statement content, the objects its proof or next attempt works on, and the
  smallest recorded class containing those objects. Apply that class's bounds before inventing a new
  method. Repeat object searches when drafting or review changes the next attempt's objects.
- Follow relevant matches and, for generic mechanisms, the immutable [historical
  index](php_codex_handoff/manuscript/CLAIM_INDEX.md). Bounded suggestions and missing graph edges
  do not prove absence or independence. Test against recorded counterexamples, refutations and
  obstructions for the objects. Check whether the record already implies the result before drafting
  its proof, and include applicable prior results in the review brief.
- Use `tools/claim-dependencies.py packet --claim ID` for bounded orientation and
  `tools/claim-index.py list --fields id,summary --format tsv` when a complete minimal inventory is
  necessary. Packets and summaries are not proof sources. Before reliance, reread exact statements,
  proofs, conventions and applicable corrections from the full records. For a pointed-to publication
  or Lean file, read its theorem statement first.
- Read every version listed under **Newer versions** and compare field, range and encoding
  hypotheses separately; a later or formalized version need not be stronger. Inspect reviewed
  dependencies and correction/refinement links with `claim-index.py graph` and exact metadata. Check
  conditional premises, stronger versions and transformations already present in older proofs before
  imposing a new interface requirement. Follow dependencies relevant to the argument; an impact
  warning does not establish falsity.
- Write **Record comparison** before **New mathematics**, the title or any novelty claim. Compare
  from the cited record's side, including dependencies, dependents and proof steps, not only from
  the draft's wording. Apply recorded dualities in both directions to find bounds on equivalent
  objects. Label rediscoveries/refinements and link originals. Before drafting a corollary, check
  for an earlier result under fewer hypotheses.
- When drafting the claim spec, before review, run `tools/claim_resemblance.py SPEC`; read the
  nearest matches, including those below its refusal threshold, before stating novelty. Registration
  requires a relation for a sufficiently similar claim. Search logs and resemblance logs must
  describe actual work: the finisher checks them against **Record search** and the entry's declared
  claims.
- Apply a cited statement and its proof to the actual instance, part by part, at every jointly
  allowed parameter range. Try the free range of its proof even if its statement fixed a value. If
  the object preserves a hypothesis on other sets or at another level, rerun the proof there before
  proposing a stronger theorem. When replacing a hypothesis, identify every direct and indirect use
  in the proof itself, including locality, measurability or event identities.
- Quote the record's own condition beside its application. A construction property used by a proof
  step must be quoted from the construction's record with its anchor; for a script, use the code
  constructing the object, not its comments. Identify exactly where a vanishing factor sits relative
  to every bracket or enclosing operation. Derive modelling choices before computing from them.
- Before the review brief, run `tools/draft_claim_sentences.py DRAFT --notebook NOTEBOOK`. Read the
  full listing: each claim-citing sentence beside its registered statement, each entry link beside
  its title/status, and each reported count beside its saved output. Restate a bound's hypotheses
  and error terms beside the instance and scale used for a decision. A listing read only for its
  total is not a check.

### Order of work

Apply these rules to proofs, tests, witnesses, next attempts, summaries and replies. A rule adopted
after a mistake applies immediately to the next text written.

1. **Take the shortest route.** State a known direct route in both the entry and the reply and take
   it before side lemmas, further exclusions or stronger conveniences. Exploration is appropriate
   while no direct route is known. Each research entry has **Shortest route.**: the route taken;
   **Not taken** with a concrete reason; or **No direct route known yet** with what exploration must
   find. The append tool requires it; `tools/route_judge.py` uses a Sonnet judge every third
   research entry, with the preceding two and living sections, to check unjustified detours. When
   obstructions identify the required mechanism and no construction has it, build and test a
   candidate before excluding more classes.
2. **Try the plainest argument first.** Choose the target by the goal, not by available tools.
   Distinguish a sufficient endpoint from stronger conveniences and first try to refute a
   convenience on the simplest separating instance. Draft **Plainest bound.** before choosing a
   method: the bare count, oldest applicable lemma, one-function estimate, or that estimate plus a
   union over a polynomial-size family. Apply it to the goal's own objects and intermediate ones.
   Once a proof exists, try its steps individually: a step already deciding the question makes the
   rest a variant. Compose the draft's results with all applicable recorded bounds, splitting where
   ranges meet, before posing a conjecture or new method. Use computed means/averages through
   elementary cost properties before planning a more elaborate next attempt.
3. **Work the open step.** Before calling a step open, hard, impossible or too costly, try the
   cheapest relevant argument yourself: concentration, gluing/composition, converse, relaxation or
   necessary condition. A failed method is reported as that method's failure, beside the plainest
   alternative on the same instance. A negative claim about available results stands beside the
   actual search/attempt. A question is decided only when its entire quantified class matches the
   argument's class. Vary ambiguous quantifiers, not only constants. A cheap test of a forecast is
   made; computational design, sizing and stopping rules are in
   [COMPUTATION_RULES.md](COMPUTATION_RULES.md#before-computing).
4. **Read off the proof's scope.** State hypotheses, free parameter ranges and qualifiers after the
   proof, from the steps that use and establish them. Redo each step without a proposed hypothesis;
   retain only the weakest form it needs. A condition used only to describe different conclusions
   becomes a case split, not a restriction. Check each branch separately. State the more general
   result when it costs no extra proof. Do not fix a free parameter merely for a convenient
   constant. A narrowing must name its necessary proof step; recheck every comparison, application
   and summary affected by a scope change.
5. **Check the whole domain.** Evaluate every hypothesis and inequality at both ends of free ranges,
   on extreme family members and at the witness's actual parameters, including limiting behaviour as
   size grows. Use the object's own exact parameters when comparing or dismissing a recorded result,
   not a weaker conventional bound. Before a Not covered list or next attempt, drive each parameter
   to the largest permitted value. State factor signs before multiplying inequalities or taking
   powers. A violated sign hypothesis may make the statement false, not merely vacuous. For
   probabilistic uniformity, name the union bound covering each parameter and the independence
   behind each concentration step.
6. **Build meaningful witnesses and cases.** Derive a case split from the construction's definition,
   including coincident boundaries and contact between its parts, before selecting witnesses. A
   witness exercises every branch it is offered for and, for an extension, a step or instance not
   already covered by the earlier theorem. Compute the illustrated quantity beside it. Before
   generalizing from one construction, test the most unlike construction. A conclusion transferred
   to another field, characteristic, parameter or class is rederived there, or marked not covered.
   Before claiming a family property, check extreme configurations such as coincident boundaries or
   many members through one point.
7. **Use exact comparisons.** First seek a natural injection or a map with exactly described zero
   set for a dimension/rank bound; use a bare count only after recording the attempted map and its
   failure. Count a construction's size/depth from its written gates level by level. Compare a sum
   to a budget in the quantity that budget prices, including tails rather than typical values where
   applicable. Derive thresholds and signs from displayed formulas, with extreme/saturating cases;
   distinguish bookkeeping losses from properties of the object. Evaluate both ends of any claimed
   window and use the needed bound direction. A bound on one part is not a bound on the whole.
8. **Justify relations and decisions.** Set the earlier statement's exact words beside the new one
   before declaring implication, equivalence, strict strengthening, falsity or supersession. Use the
   weakest justified relation. One-sided bounds remain bounds, not equalities or equivalences.
   Relations asserting a failed converse need its proof or counterexample. Mathematical merges or
   claims that questions are restatements require a construction transporting every member with its
   cost. A better method does not falsify a correct result about an older method. Keep elementary,
   dominated and superseded results, registering their relations; withdraw only false results.
   Decisions cite a proof, a record or explicitly say **judgement**. Apply status definitions
   without either overstatement or understatement.
9. **Correct from sources, not wording.** Re-derive a rejected sentence from its statement and
   sources, recomputing figures. If wrong twice, redraft from the sources before returning it.
   Update every copy of its claim: spec notes, living sections, next step, title and commit message.
   Test a reviewer's proposed case split on a member of every branch before adopting it. For a
   suggested next attempt, reread constants and ranges and redo accounting. Reread assembled
   paragraphs as a whole for internal contradictions. Before retracting, undoing or sending a
   corrective message, read and quote the record showing what actually happened.
10. **Summarize last.** Titles, New mathematics, Bearing, scope lists, claim rationales, next
    actions, commit messages and replies come from the final statement, retaining its exact
    hypotheses and qualifiers. Shorthand class names cannot replace hypotheses. State the quantity
    bounded and the class actually covered, not the class suggested by the mechanism. Explain
    whether a change is more general (weaker hypotheses), less general (the necessary restriction),
    or false; avoid bare “weakened”/“narrowed”. Relay agents' findings with their source's
    qualifiers, distinguish their suggestions from your additions, and return added arguments for
    review before crediting them. Before durable text, associate each finding/figure with its proof,
    saved output or attributed agent report; unsupported memory is not a source.
11. **Verify effects and compliance.** A command issued is not work done: read the resulting file,
    tool report or committed subject. Await a prerequisite edit's result before submitting a call
    that consumes it. Run required tools for their substantive purpose, never merely to leave a log,
    stamp or passing phrase. Only the tool doing the duty records its completion. If a gate is
    burdensome, change it openly; do not satisfy its form with placeholders or filtered output. A
    claimed comparison quotes one compared line and its outcome; a claimed prevention gives the
    exposed case's actual passing run at the earliest applicable stage.
12. **Resolve refusals.** Before retrying, read the emitting code, quote the refusal's rule line and
    state what input broke it. Diagnose an unexplained error by varying one suspected factor in the
    same operation; otherwise label the cause a guess. Passing because text was remembered, retrying
    timing until it passes or changing routes without resolving the cause is not a fix. Resolve
    recurring adverse verdicts in the same turn by correcting the work, its source guidance or the
    check, or file a decision in `user_requests` with its default. Do not defer them to another
    review. Harness/classifier refusals are not bypassed through another command or tool: report the
    action/reason to the user, file the decision and default of leaving the refused target
    unchanged, and continue unaffected work. If a written rule lets the same mistake through twice,
    replace or back it with a check in that turn.

Replies obey the same evidence and scope rules as entries. Search the record in the objects' words
in that turn before describing its coverage or presenting a direction as new; living summaries are
not the record. Investigate the question's readings rather than handing them back untested. Try or
queue a discovered gap or promising idea in the same turn and report the action. Before each review
brief, including a corrected draft, reread the draft against these rules individually; recompute
record comparisons and instances at parameter endpoints and extreme family members.

### Draft and correctness review

Write required labelled paragraphs as `<p><strong>Label.</strong> ...</p>` using the exact names
below so the append tool and finisher can validate them.

- At the start of drafting, run the headings and labelled-paragraph skeleton through
  `tools/notebook-append.py DRAFT --check`. Each entry registering a proof includes: **Hypotheses,
  each with its step.** (weakest needed form and the class of each conclusion), **Degenerate
  cases.** (evaluated or excluded by a named hypothesis), **Nonvacuity.** (an input checked against
  every hypothesis), **Plainest bound.** and **Baseline.** (what the obvious construction or oldest
  bound gives, and what the statement adds at every claimed cost class). Each example/test also gets
  its own baseline, computed first. For uniform families, distinguish what a one-function bound
  decides from what uniformity adds. “None applies” follows an actual attempt. State composition
  lemmas in a common setting with full proofs, not references to sketches.
- Once the question, argument and evidence are stable, obtain one focused correctness review of
  every new mathematical lemma, theorem, rule or encoding before assigning status. Run the
  exhaustive checker for a rule/tree/encoding change before relying on it. Use at most one
  fresh-context reviewer subagent for the consolidated review; no separate novelty reviewer. Perform
  novelty searches yourself. Scheduled architecture stages and necessary corrections use the same
  reviewer.
- Reviewer agents always use **medium** reasoning. Claude uses `.claude/agents/medium-reviewer.md`;
  Codex uses a native subagent with no conversation history, explicit `gpt-6.1-sol` and `medium`,
  following [tools/CODEX.md](tools/CODEX.md). Supply the canonical reviewer instructions, stable
  draft, exact anchors/dependency excerpts, at most one or two named claim searches and a short list
  of requested checks. Instruct read-only behaviour; permissions are inherited. Never create a root
  session for review or substitute higher effort if medium is unavailable: leave the gate
  conditional and file a user request. Needed Spin reviewers are already authorized.
- After correctness, ask the same reviewer to help with the cycle's open point: a repair to a failed
  step, a proof/counterexample to an expectation, or tightness of a bound. Record suggestions under
  `<h4>Reviewer's suggestions, unverified</h4>`, each ending **Record.** with a search performed
  before recording it: relevant IDs/anchors or searched words without a match. Verify a suggestion
  yourself before reliance or selection as a next step. Reports retain **unverified** until then;
  your added or strengthened arguments require the follow-up review below.
- Resolve every gap and justify or remove unused hypotheses. Follow up with the same reviewer for
  architecture stages, a concrete gap, or a correction adding/strengthening a claim, outcome,
  argument or code the reviewer did not write. Only deletion or adoption of the reviewer's exact
  wording counts as narrowing; code implementing a suggestion still needs review. Always obtain
  review of corrected work before removing its queue item. Defer optional extensions.
- **Verification gate.** names dependencies reread, checks and the reviewer's actual verdict. Credit
  only what the report checked; sketches marked unverified remain so. An incomplete gate means
  conditional status, not a working proof. Until review and correction checks complete, prefix every
  current-cycle mathematical conclusion to the user with **Unreviewed:**, including opening reports
  before a draft exists. If review narrows or withdraws a reported conclusion, the next report names
  both the old and new scope. Scope statements leave open everything unchecked.
- Every reviewer also audits process, including title/status scope. Record **Process audit.** in the
  Verification gate, explicitly comparing title with body. Write or rewrite title/status after
  review from the reviewed body. The finisher's independent `tools/stand_in_review.py` reviews the
  session's conduct at most once per 40 minutes, returning up to five quoted objections. Check each
  against the record; the next entry's **Review.** records fixed, queued, or wrong with reasons.
  Apply the Prevention/Meta requirements below to each report.

### Goal progress and scheduled review

Keep the cadence: **six research cycles, then one route review**. Neither early reviews nor a
seventh consecutive research entry are allowed. Audits/unrelated work do not erase warnings after
two cycles leave the same obligation unchanged. A review is goal-level (`data-scope="goal"`) exactly
when the line's open-item count has not dropped since the review ten or more research entries back;
otherwise it is ordinary. The finisher checks both directions and startup reports which review is
due. Do not add reviewers or reviews every two cycles.

Each new research/review article names its stable **Open statements** ID in `data-obligation` and
sets `data-goal-progress="advanced|narrowed|unchanged"`. Separate **New mathematics.** (including no
result) from **Goal progress.** (the necessary implication changed and why, or unchanged).
Advanced/narrowed cite an entry-declared proof, conditional reduction or refutation. Narrowed states
**Removed part.** and **Remaining part.** in the open statement's terms. Unchanged while citing an
own proved claim explains what remains untouched and why. A toolbox, stronger convenience,
equivalent reformulation or finite check alone is not progress. Keep the obligation ID stable while
the implication is unchanged; reviewers challenge understatements as well as overstatements.

- From the third consecutive unchanged research entry on a route, end Goal progress with
  **Bearing.**: what the result gives at the goal's parameters, or why it gives nothing and what
  outcome could have justified the cycle. Being requested by an earlier review/entry is not a
  justification. Declare matching `data-bearing="none|some"`; **some** ends with **Not covered.**
  and the cases not reached.
- After two consecutive **none** entries on one queue item, develop a different item next. After
  three on a route across items, state **Best outcome.** before the next work: its consequence at
  the goal's parameters and the registered result it must beat. A Continuing follow-up in that run
  includes **Record search.** for its named next attempt.
- Enforce work-admission rules at `compute.sh start` and Proposed next step, with finalization as
  backstop. If work was already done against a rule, checkpoint it immediately with **Against the
  rule.** naming the stage that should have stopped it. Preserve the work, but do no further
  excluded work, name no next step on it and claim no unearned spell extension.
- Every **some** Bearing links the matched parameter ledger with a named link, e.g. `<a
  data-ledger="selection" href="#selection-ledger">selection budget</a>`. Each Nonvacuity identifies
  its particular budget by a matching named link; assertions about multiple budgets need separate
  references. Tools check declarations/references; the reviewer checks the mathematics.

Each scheduled review states the line's general claim, what the goal needs, a falsification attempt,
an evidence-based qualitative assessment of that line, a precise **Obstacle** heading, and the next
step on the highest-risk item. Include `<h4>Architecture review</h4>` with labelled paragraphs:

- **Necessary target.** Give the weakest sufficient endpoint, quantifiers, instances and degree/size
  budget. End **Downstream.** by evaluating it through proved downstream statements, citing IDs and
  stating whether the consequence is the goal or weaker.
- **Extra requirements.** Identify and justify the approach's additional demands, or say which may
  be relaxed: existence versus arbitrary choices, derivability versus literal vanishing, one
  survivor versus a separately large space.
- **Independent alternative.** First give the existing medium reviewer only the goal and bounded
  available-result excerpts, including registered open conjectures with evidence. Withhold the
  preferred route, period results, their route grouping and ranking. Draft the brief from that
  withheld-information list; put it in its own folder and begin `BLIND STAGE`. Ask open questions
  admitting “none” or “not these”, not questions prescribing the answer's form or a preferred class.
  Ask for a materially different architecture or why none was found. Then reveal the current route
  for comparison and correctness review. Link the reviewer evidence; do not fabricate an alternative
  or spawn another reviewer.
- **Rank normalization.** For dimension comparisons, check that losses and survivors use the same
  quotient and whether relative contraction can replace absolute smallness; otherwise explain why
  this question does not apply.
- **Decision.** Choose the endpoint/architecture to test or justify retaining the current one. If
  changing a user-set ordering of goal statements, record it in Route decisions and the next user
  report as the agent's reversible judgement. A pre-run branch identifies possible instance
  artefacts; a decision based on a run departing from earlier data first executes their suggested
  cheap control or states its measured cost.
- **Decisive test.** Name the next cycle's concrete operation and distinguishing outcomes, as
  relations among computed quantities with meanings derived from definitions/containments. Declare
  **Test disposition.** as **New operation** (with **Operation.** and **Prediction.**) or **Retained
  exploratory** (link the earlier review, claiming no new mechanism). A rewritten parameterization
  is not an operation. Read `tools/notebook-excerpt.py --review-tests`, search the test as a new
  lemma and end with **Record search.** and results. Before Operation/Prediction, include: **Trivial
  cases.** (trivial transformations, instances giving each outcome, and structural reasons that may
  decide it); **Power.** (recorded bounds/method limits, reachable sizes, discriminating outcomes,
  and whether the instance lies in the goal's parameter window); **Instance check.** (evaluate those
  inequalities numerically on each instance and at parameter extremes); and **Attempt.** (what was
  already tried using the cited results, where it stopped, and cheap recorded computations run or
  their measured cost). Drop instances these checks decide. If the attempt or reviewer resolves the
  proposed test in a few lines, rewrite the decision/next step as a lemma-first entry. The
  second-stage brief asks the reviewer to try the stopping step; **Attempt checked.** in the
  Verification gate records its outcome.

The next research cycle on that route reports **Architecture test.**, opening **Decided.** or **Not
decided.**, naming the actual outcome and linking the review. A proof attempt can satisfy it;
unrelated local lemmas cannot. A user-picked task may defer but does not clear it. Apply these
requirements to new entries, not by retrofitting historical assessments.

## Notebook and claim metadata

### Ownership, living sections and records

- `notebook.html` owns the main goal; each registered side notebook owns its thread's current state
  and full record. Select it through [tools/SIDE_NOTEBOOKS.md](tools/SIDE_NOTEBOOKS.md). Never
  replace main living sections with a side goal. Edit the selected notebook directly; `python3
  server.py` serves it at localhost:8000 with reload notices. `index.html` owns layout.
  `research/notes/RESUME.md` is navigation only. Supporting notes contain proofs, evidence and dated
  audits, not duplicate living summaries. Label historical snapshots; Git preserves prior overviews.
- After every research turn, update **Where we stand**, **Open statements**, **The remaining route**
  (highest risk first), **Proposed next step** and **Working mathematical context**. Open statements
  contains at most about five self-contained statements whose conjunction with proved results gives
  the goal, each with status and covered instances. Keep the selected goal, exact setup, degree
  conventions, linked hypotheses/proofs, unresolved dependencies and next step central; mention side
  publications briefly. Consolidate by purpose, not by adding a subsection each turn.
- Declare notebook-specific per-entry duties on a living section with `data-entry-paragraphs="Label
  one|review:Label two"`; unqualified labels apply to research entries. Startup prints them and the
  finisher requires the corresponding `<p><strong>Label.</strong>`.
- Pre-record regions have [configured budgets](research/context-budgets.json), except the two queue
  sections. Run `python3 tools/notebook_context.py` while drafting; see [budget
  operation](research/notes/CONTEXT_BUDGET_PLAN.md#budget-operation). Review soft excess; hard
  section/aggregate excess blocks finalization and CI. Allocate a budget for a new section. Only an
  explicit recorded user override permits raising/waiving hard limits. Consolidate yourself,
  preserving unique substance durably and essential hypotheses/warnings with links to full records.
- Append a dated Research-record entry for every research turn, including failures and no-result
  turns. State the question, approach, actual outcome and remaining gap; invent no lemma to justify
  the entry. Put all substantial new mathematics there in full; chat or supporting notes alone do
  not suffice. The record is unlimited. Routine setup/admin work needs no mathematical entry.
- Give each article a stable anchor, descriptive title/date, explicit status, assumptions, precise
  claim, complete argument, dependencies, original parameter costs and checks. Tag
  `data-kind="research|review|formalization"` and `data-route` with a top-level remaining-route
  `data-route-item` slug (or `side-...`), never a sub-gap. Do not number cycles; use anchors and
  route IDs for parallel formalization. Keep `<p class="entry-meta">` at most 300 characters before
  the generated producer credit: status, at most one scope clause, then a descriptive cycle label.
- Use MathJax for inline and displayed notation, code formatting for identifiers/source references.
  Name new results in one to four plain descriptive words; variants get meaningful names/qualifiers,
  not letter codes or prime/digit/letter suffixes. Cite older coded results descriptively, normally
  using their claim-ID words. New letter-code names outside tables are refused.
- Keep entries chronological and append-only, including disputed assessments. Correct/retract in a
  new dated entry linked to the old anchor, updating living status and correction metadata. Never
  silently rewrite mathematics. Link repairs and presentation-only changes preserving text are
  allowed. `tools/check-append-only.py` checks HEAD at finalization and must pass against
  `origin/main` before publication unless explicitly overridden.
- Historical labels link to statement/proof anchors through
  `php_codex_handoff/manuscript/CLAIM_INDEX.md`. Use public GitHub file URLs so notebook links work
  locally and on Pages; verify files/anchors locally and read local excerpts when available.

### Leads, bridges and mathematical queues

Outside draining mode, each scheduled review includes at least three **Outside leads** and two
**Absurd bridges**, selected to answer its Obstacle. A lead names a theorem/source from another
area, its target open statement and break point, including recorded leads not followed. A bridge may
come from any field and states the object translation, what a theorem there would give and its
smallest discriminating translation test. Reach beyond familiar fields without waiting for the user.

- Each item ends **Answers.** explaining its bearing, and **Test.** with **Passed**, **Falsified**
  or **Not run:** with reason. Run every cheap named test during that review. Test where recorded
  bounds and plain counts leave the outcome open; falsified items remain listed and count toward the
  minimums. Passed requires **Break point.** stating where translation could fail and what the test
  found there. Testing only the source theorem, or an unread recalled statement, is Not run for the
  translation. A source-based Not run includes **Retrieval.** with the attempted tools and outcome.
  Write outcome words after the findings and Decision after Attempt; update every summary of a
  corrected item in the same edit.
- Mark the three most promising passed leads and two passed bridges with `<li data-pick>`, or all
  when fewer pass. Only picks enter the queue; drop other passed proposals. Research entries carry
  no Outside leads or Absurd bridges: unfinished intended work goes under **Sub-ideas**. Do small
  work now, drop work not intended, and do not invent items to fill a section.
- The mathematical **Lead and bridge queue** is `<section id="lead-queue">`, an unbudgeted living
  section before the record. Restoration shows previews of its first five items. It is FIFO; new
  picks join the tail. Develop at most one top-level item per research entry. The head is default;
  another item is allowed with **Chosen.** naming the open statement it bears on and why it comes
  first, during draining too. Tag the entry `data-lead` or `data-bridge="REVIEW-ANCHOR:N"`, or the
  appropriate check/build/idea kind. Before planning, run `tools/lead_queue.py history NOTEBOOK ID
  --status`, read the latest development, and use its computed spell count rather than older prose.
- Four consecutive research entries form the default spell. At the boundary rotate to the tail and
  develop a different item; do not re-file the same attempt under a related item. Extend by two
  cycles only when a proof, refutation or reduction from the current spell/extension materially
  advances a named open statement and the next necessary implication uses that mechanism. Use [the
  queue tool's extension format](tools/lead_queue.py). A narrowed result qualifies only when
  **Spell-start remainder.**, **Smaller remainder.**, **Same mechanism.** and **Reviewer
  confirmation.** establish a smaller remainder than at spell start. Reassess each two-cycle
  extension; there is no lifetime cap. Finite checks, promise and reused old progress do not
  qualify.
- Sub-ideas nest one level under their item; development counts toward the parent's spell. Sub-ideas
  of the same top-level item may share an entry, each with its own follow-up and evidence. Batch
  triage of top-level items is retired. A parent keeping any sub-idea open is Continuing, not
  Closed; sub-ideas do not become independent items merely because the parent closes.
- Every developed item has **Follow-up.**: **Continuing** while useful application to an open
  statement remains, **Developed** when results leave no such application, or **Closed** for a
  reason the attempt established (restatement, inapplicability, falsification, supersession). Do not
  stop at the first usable result. A justified closure can take one short cycle; no permission to
  prune is needed. Continuing names and where possible attempts a concrete next step, with
  **Smallest case.** tried and **Own statements.** applying the entry's results; if a few lines
  decide it, the next entry is the lemma, not another test.
- Before Developed/Closed, enumerate the question's readings, including ambiguous quantifiers,
  beside their actual attempts. Closed includes **Stakes.** (what yes/no would give), **Sources
  read.** (exact statements, or recorded-only reliance; no abstract-only closure), **Not examined.**
  (each named part not examined and why closure remains valid, or none), **Owed attempt.** (latest
  promised/reviewer attempt made and its outcome, or none), and a link to the reviewer's closure
  verdict. Developed also requires Not examined, Owed attempt and that review link. A named part
  unexamined or an owed attempt unmade keeps the item Continuing. Every entry whose predecessor
  named an attempt gives Owed attempt, whatever the outcome; if another came first, explain why.
  After two consecutive deferrals, make or explicitly drop the attempt in the third with reasons.
  Closed/Developed remove the item only after corrected work has been reviewed.
- A user pick may choose any item: `data-picked="user"` and **Picked.** quoting the user's words.
  Waiting items remain queued and are passed over; use **Waiting:** and **Unblocked:** follow-ups.
  Reopen a prematurely closed mathematical item with a list-item **Follow-up. Reopened:** and
  reason; `lead_queue.py append` returns it to the tail.
- A queue audit (`data-kind="audit"`, outside cadence) collects older ideas named outside standard
  sections in `<li data-source="REVIEW-ANCHOR">`; queue them all. List intended unfinished checks
  and builds under `<h4>Sub-ideas</h4>` using `<li data-sub="check|build">`. Sub-ideas of a research
  entry developing no queue item wait in their source entry, appear in `lead_queue.py pending`, and
  a later review promotes selected ones with **Follow-up. Promoted:** and its judgement.
- Use `lead_queue.py append` after the entry and `done` operations as directed by its help. It and
  `similar` report similar wording. Merge genuinely identical questions with **Closed: merged into
  ID**; the tool retains the merged wording. Mathematical equivalence still needs the costed
  transformation required under Order of work. A check is Developed with resolving evidence; a build
  with a linked opened task or implementation path. Relative evidence links must resolve.
- Backpressure starts at **30 top-level items** and lasts until **10** remain. During it each
  research entry develops a queued item or its child, with the same head/Chosen rule. Reviews omit
  Outside leads and Absurd bridges and assess existing work; cadence and other review duties remain.
  Declare `data-queue-items="N"`; startup compares it with the previous two reviews' counts. Declare
  items a review leaves with `data-left-items="ID ID"`; until the next review, returning to one or
  its children needs **Returns.** explaining why. Report only changed follow-up statuses. If fewer
  builds were made than remain queued from the period, **Builds.** gives each one's disposition:
  built, dropped, or dated reason for waiting. Section attributes configure counted entry kinds,
  backpressure and extra kinds; [tools/lead_queue.py](tools/lead_queue.py) owns their syntax.
- One objection excludes only its tested formulation. Before declaring a goal without mechanism or
  moving away from it, develop each relevant Not run item and each item closed by a single
  objection: read the full source and try other encodings/settings where it does not apply.
- Proposed next step names its top-level route and selected queue item by ID or development link.
  While draining it must name an item; naming a developed item's ID requires quoting eight
  consecutive words from its latest follow-up or queued text. Read the tool's printed text/history
  before drafting the step. During an authorized Spin, continue the next cycle/review in the same
  turn while the goal is open; do not idle for possible redirection or a user decision. If recorded
  routes close, propose and test another idea. Stop when the goal is proved or the user stops the
  work. Report progress, obstructions and uncertainty without invented probability estimates.

### Classification and framework queue

- Work raised outside an entry joins a queue with `lead_queue.py add NOTEBOOK.html
  --check|--build|--idea ID SOURCE TEXT --summary SUMMARY --scope math|framework`. No research entry
  is required. The author classifies by purpose, not kind; newly listed items use
  `data-queue="math|framework"`. Every item has an agent-written plain-text summary of at most **160
  characters**, supplied by `--summary` or source `data-summary`. Full descriptions remain
  canonical. Rendered notebooks hide these attributes; agent list/resume previews require summaries
  with no prefix fallback. Repair missing metadata with `lead_queue.py summarize`; `history
  --status` shows full mathematical queued text before history.
- Framework items from any notebook go immediately to main's `<section id="framework-queue">`,
  including otherwise-waiting sub-ideas. `lead_queue.py append` routes listed items; stage main with
  the originating notebook after a transfer. Main means the current worktree's main notebook,
  integrated by normal Git synchronization. Framework work has no mathematical draining, spell,
  research-cycle or context-budget obligation. Resume reports only its count. The rendered section
  shows five items with remaining-item disclosure and full-text expansion.
- Use `framework-list`, `framework-status ORIGIN::KIND:ID`, and `framework-edit ORIGIN::KIND:ID TEXT
  --summary SUMMARY` through `lead_queue.py`. `framework-close ORIGIN::KIND:ID --record REVIEW.txt
  --path PATH --note TEXT` closes any framework kind with reviewed evidence in
  `research/queue-closures.jsonl`. Closed IDs retain ownership and cannot be silently
  reopened/reused; new work uses a new ID. Migration retains IDs, summaries, source links and parent
  provenance; origin disambiguates notebooks.
- Mathematical items stay local. A finished top-level mathematical build can leave without a new
  entry through `lead_queue.py close-built NOTEBOOK.html ID --record REVIEW.txt --path PATH --note
  TEXT`, with reviewer evidence and the closure ledger staged alongside it.

### Claim registry and formalization

- [research/claims/index.json](research/claims/index.json) owns metadata; the Markdown index and
  topic views are generated. Follow [research/claims/README.md](research/claims/README.md), author
  compact specs with `tools/claim-index.py author build`, and regenerate with `render`. Preserve
  stable IDs, exact scope and full-record links.
- New/substantively revised claims need current evidence-backed reviews of mathematical status,
  topics, formalization, significance and relationships. Use the registry's cheap
  [significance/attention workflow](research/claims/README.md#significance-check-and-attention) at
  each checkpoint and surface new/reopened candidates. Unknowns have a specific pending question and
  next action; do not invent metadata. Record dependencies, refinements, corrections and
  obstructions, refreshing affected claims. A `refines` edge requires implication in one direction.
- `claim-index.py changed --base REV` checks changed scope: HEAD at finalization, integration base
  in CI; untouched backlog stays separately visible. Articles declare matching `data-claims="ID
  ..."`, or `data-claims="none"` with a specific `data-claim-note`. Unregistered labels and
  mismatched source/inventories block finalization. Follow the editing contract for metadata-only
  changes.
- Read **Gaps identified by formalization** on ordinary restoration; keep its living list concise
  with links to discrepancies and audits, full corrections in dated records. Begin Lean only under
  explicit assignment, including an assigned parallel formalizer; then read
  [formalization/AGENTS.md](formalization/AGENTS.md) and its README. Record exact per-claim Lean
  scope/file links. Partial coverage or stronger hypotheses do not verify the full informal claim;
  absence of Lean is not mathematical incompleteness. Use the normal evidence and checkpoint rules.
- In coordinated parallel formalization, only the coordinator edits all living sections, including
  gaps, at integration checkpoints. Workers review them, append full records, maintain metadata and
  promptly send proposed overview changes/discrepancies without waiting for all workers to finish.

### Research checkpoint

Finish notebook and registry edits before the final snapshot. Prepare staging paths, commit message
and focused metadata checks during review. Run `./tools/check_records.py --diff`; focus checks on
mathematics and touched links, with rendering checks only for layout/tool changes or a concrete
concern. Do not display PNG previews unless requested.

Run the small controller `./tools/finish-turn.py TURN` directly, not inside the session it stops.
For continuous research use `--next NEXT`; checkpoint work belongs to preparation. It checks the
entry, exports timing, archives evidence and fills its unique `<!-- TIMING TURN -->`. Follow
[timing/export rules](COMPUTATION_RULES.md#timing-export-and-evidence-archival). End each entry with
the generated **Measured category / Elapsed** table and bold total, followed by generated **Model
use** when available in the producing session. Keep its footnote one short sentence plus exceptional
limitations; distinguish tool failures/timeouts from mathematical failures.

Checkpoint sequentially: preparation marker, checks, provenance, timing export/archive, staging,
commit, then any authorized push. Stop on failure. After the finisher only stage, commit and perform
authorized publication; a necessary edit requires rerunning its checks, including context budgets
for all notebooks and claim checks, against the new snapshot. Commit the entry, timing fragment,
archive and supporting results together. For asynchronous checkpoints, observe terminal commit and
required base-synchronization success before planning further mathematics; meanwhile do only
checkpoint preparation.

## Framework maintenance and interaction

- Search `tools/` before writing a helper. Extend committed, tested tools for recurring work,
  including integration/maintenance and jobs recurring by nature even on first use. A scratch script
  whose output enters a tracked record becomes a tested framework tool before that commit. Use
  `tools/notebook-append.py` for entries/next steps and `tools/notebook-excerpt.py` for reviewer
  excerpts (`--claims ID ...` includes registered statements and assessments).
- Wrap every edited Markdown file with `tools/rewrap_md.py` at its default width. Use
  `tools/replace_text.py` for prose passage replacement preserving indentation, and the editing tool
  for exact edits; do not write ad hoc replacement scripts. Improve an inadequate recurring tool
  instead of working around it.
- Before proposing a tool replacement or dropped capability, compare what each provides, implement
  the smallest improvement closing our tool's gap and measure both. A cost belongs to the actual
  attempt/mechanism measured. Offer retaining the existing tool alongside the comparison.
- Follow [framework test and measurement
  rules](COMPUTATION_RULES.md#framework-tests-and-measurements). A changed refusal requires
  legitimate uses of each matched phrase, actual triggering cases, cheapest bypass attempts, and
  corpus replay with catches, losses and false refusals judged from their sources. Scope exemptions
  to the relevant sentence and verify their claimed reason. Replaying a rewrite includes earlier
  true catches it loses. Calibrate every record threshold/filter over all records it will read,
  judging losses as well as catches before committing. A zero scan count is reported with the input
  coverage (`tools/record_scan.py` block-counts). Do not fit thresholds to the prompting case or
  mistake tracked output/data for source code.
- Durable process lessons belong in the committed framework. Never write machine-local memory,
  including `~/.claude/projects/*/memory/`; `tools/hooks/memory-gate.py` enforces this. Store
  general rules, not mathematical incident narratives. Apply the instruction-maintenance procedure
  at the top of this file before adding any lesson. If an existing rule was ignored, repair the
  workflow or enforcement that allowed it instead of adding synonymous rules.
- Resolve demonstrated process mistakes without waiting to be asked. Build a mechanical prevention
  where possible; a written rule is appropriate only where a mechanical check cannot serve the
  purpose. A queued build's text may be extended at most once: a later mistake requires a fix in
  that turn or a separate queued item, not an ever-longer promise. Implement the substantive work a
  budget or gate requires in the turn it arises; do not defer it merely to get a checkpoint through.
- Report each admitted mistake, reviewer report and correct stand-in objection with **Prevention**
  and **Meta**, unasked. Prevention names the general failure class, entry stage, why prior controls
  missed it, and the committed tool/check change at that stage with the exposed case's passing run.
  Fixing only the instance is insufficient. If no agent mistake was found, say where none was found.
  If prevention cannot be built this turn, queue it separately with **Tried:** evidence and **Not
  built in the turn:** reason, meeting `lead_queue.py add --build`'s requirements. Build and commit
  a valid objection's prevention before the reply claiming it is fixed; name that commit.
- Meta identifies the wider working habit that produced both the mistake and the need to repair it,
  where else it occurs, and the changed behaviour in its named durable home. Do not repeat the
  Prevention mechanism as Meta. An entry's **Process assessment.** ends with **Prevention.** and
  includes **Meta.** A mistaken reviewer objection also requires correcting the review setup (brief,
  reviewer instructions or stand-in prompt) so the same misreading does not recur.
- Every command/path must serve the current step; drop unused actions and reach outside the worktree
  or owned scratch only through supported framework routes. Read tool output needed for decisions
  before the next dependent action. Post-restart notifications about instructions, stopped tasks or
  changed files are not work requests: do not restart work or call tools on those alone; at most
  acknowledge once and await the user.
- File every user request in main's Git-ignored `user_requests` (linked from worktrees by
  `compute.sh start`): sources, installations, permissions, direction choices or other questions.
  State what is needed, why, attempts made and the recommended default followed meanwhile. Continue
  under that default rather than idling; mention a new request in one sentence and mark it fulfilled
  when answered. A required approval is not supplied by elapsed time.

## Portable sessions, Git and publication

- Work from the repository root without machine-specific path assumptions. `start-codex.sh`
  starts/reuses remote control; `start-session.sh` and `start-claude.sh` resume exact local IDs or
  restore fresh sessions. Only launchers bind IDs; workers never replace bindings.
  `remember-codex-session.py` only validates an existing binding. Never commit session IDs. See
  [tools/CODEX.md](tools/CODEX.md) for startup/repair and hook trust. Clones restore from files, not
  local chat or memory.
- Background sessions use persistent worktrees, never the shared checkout. Create with `git worktree
  add --track -b NAME PATH BASE`; repair a missing local upstream with `git branch
  --set-upstream-to=BASE`. Codex manages `.codex/worktrees/`; Claude uses `.claude/worktrees/`.
  After **every** worktree commit run `tools/ff-base.sh`: rebase onto a moved local upstream and
  fast-forward it, including main. Resolve dirty bases/conflicts. This never authorizes a push;
  record any run-specific override in `run_state`.
- Every research turn ends in a local commit, including failures/no results. Include living
  sections, full records, metadata, provenance, code and complete important outputs. Promote
  valuable scratch evidence first; preserve no research only in chat or ignored runtime files.
  Review changes and exclude unrelated edits. Logs, credentials, IDs, binaries, environments and
  scratch renders remain untracked. Commit-message lines are at most **100 characters**, with blank
  lines between paragraphs. Follow [scratch/result
  retention](COMPUTATION_RULES.md#persist-computation-outputs).
- Publish only with explicit authorization, including an active scoped/time-limited grant. Editing,
  research and local commits do not authorize publication. Record grants and run-specific overrides
  in main's Git-ignored `run_state`, using the user's words and date; remove them when ended.
  Worktrees link to it, startup ensures the link, and resume bundles it. Restore actual grants after
  compaction, honor expiry/later overrides and do not re-ask within authorized scope. A clone
  without that file has no grant; this file contains no run state.
- Respect the user's branch. Do not switch/merge into main merely to publish. Pin integration
  targets to immutable commits after fetching/receiving workers and validate against them.
  Immediately before fast-forwarding, inspect destination HEAD and worktree; if advanced,
  refresh/rebase or leave unmerged. Old-target validation does not validate a new target.
- If another clone moves the remote, rebase in a temporary worktree with a backup branch under the
  user's `rebase-math-research-branches` skill; if unavailable, follow this rule and the registry
  remapping workflow. At stops run `tools/notebook_rebase.py --continue` for element-wise notebook
  merging. Use `tools/merge_md_words.py FILE` for wrapped Markdown conflicts or its configured merge
  driver. Repeated conflict shapes need tested guarded resolvers, not scratch loops. For registry
  conflicts, `tools/claim_rebase.py --spec SPEC` keeps the base registry, rebuilds from the compact
  spec, renders, stages and checks; it refuses unrelated conflicts.
- Preserve private `pre-publish`; never publish it or use `--all`/`--mirror`. Before authorized
  publication run `tools/verify-checkout.py --public-history BRANCH` (including claim-index CI
  against `origin/BRANCH`) and append-only checks, unless explicitly overridden. Push with
  `tools/checked-push.sh`; from a worktree use `tools/checked-push.sh main` for fast-forward-only
  publication of HEAD to main. It also rejects hard context-budget excess. Pages targets main only.
  Build site/layout changes with `tools/build_pages.py --out _site --site-url URL`, using the site's
  HTTPS base URL for citations. Upload only the minimal generated artifact, never the checkout or
  private sources. Preserve live mode and project-relative published revision URLs.
- Original software is MIT; original research CC BY 4.0. Preserve attribution and distinguish
  working from established results. Third-party sources follow `THIRD_PARTY_NOTICES.md` and
  `research/references/redistribution.json`; they are not ours to relicense. Keep uncleared PDFs,
  full text and source-containing diagnostics out of public commits and reachable history. Preserve
  needed private copies locally; never publish private files/backups.

### Source retrieval

Before declaring a source unavailable or filing a request, run `tools/held_sources.py WORDS` using
author/title words; it searches held private sources and existing requests. Search beyond the
source's own copies for needed definitions/statements in authors' talks, theses, surveys and papers
using them; record which source supplied the statement. Read rendered pages when text extraction
fails. A scripted 403/bot wall is tried in the browser with `node tools/browser_get.cjs URL --out
FILE [--click TEXT]` before requesting help. It uses the user's Firefox session and paces visits per
site, at most ten per hour; do not immediately retry a refused site through another route. For a
login the user holds, request Firefox sign-in and `tools/firefox_cookies.py HOST`; then use
`tools/firefox_get.py HOST PATH` or the browser tool.

Record a retrieval only after opening the file and verifying its identity. Check a number/range
transcribed from a scan against a second use in the source or mark it uncertain. Read arXiv papers
from source with `tools/arxiv_source.py ID --out DIR --expect WORDS`; it uses external or owned
Git-ignored scratch, refuses tracked destinations/links, prints the title and checks expected title
words. A model-generated report of a fetched page is not a reading of its statements; an entry
relying on one says so in its status line. After an honest failed attempt, file a user request with
citation, attempted links and purpose.
