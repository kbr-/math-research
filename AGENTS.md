# Noemesis research workspace instructions

These are explicit user constraints. Honor later explicit user overrides.

[COMPUTATION_RULES.md](COMPUTATION_RULES.md) owns resource limits, execution, numerical checks,
timing-tool operation and result retention: read it before computations. All substantial local jobs
use `./compute.sh`, sharing at most 14 logical CPUs and 10 GB combined RAM plus swap. Never bypass
failed controls, and install no dependencies or virtual environments without explicit approval. This
file owns research workflow, notebook editing and Git/publication policy.

Keep the framework small: revise/consolidate existing guidance before adding it, state each rule in
one authoritative place and link elsewhere. This file holds only rules that apply to every notebook:
a rule about one goal's mathematics (which results count, what a candidate must satisfy, how to
weigh its bounds) goes into that notebook's living sections, normally a **Route decisions**
paragraph of **Where we stand** (user, 10 October 2026). `tools/tests/test_agents_scope.py` refuses
goal vocabulary here, and reviewers audit new rules for scope; neither catches a goal-specific rule
written in general words, so ask of each new sentence whether another notebook could use it. Remove
obsolete history and repetition while preserving explicit constraints. Prefer actionable rules to
growing checklists or one-off setup narratives.

## Restoration and research discipline

- Named prompts (Resume, Branch, Spin, Formalize, Spin-formalize, Spin-formalize-parallel, Fossick
  and others) are defined in [PROMPTS.md](PROMPTS.md); read the named section before acting on one.
- Restore with `python3 tools/resume.py`, then read its listed bounded parts. For Codex resume
  calls, omit `max_output_tokens` on `exec_command` and omit `max_output_tokens` on any enclosing
  `functions.exec` directive: keep their default output allowances for both preparation and part
  reads. The bundle includes `research/notes/RESUME.md`, the computation rules, notebook living
  sections/gaps and compact contents; this file is not bundled, since the harness loads it itself,
  also after compaction. Retry missing parts without preparing another resume or concatenating the
  full file into one tool response. Follow the guide without rereading bundled files, then load only
  relevant records. Do not load the growing record or index wholesale. Keep `php_codex_handoff/`
  immutable; its import is complete. New work belongs outside it, usually in `research/`. Use
  targeted source passages.
- On opening a research cycle, state the concrete missing implication needed for the goal, how this
  task tests/discharges it, and what evidence ends the test or changes the next action. Route IDs
  are navigation, not a substitute for that explanation or evidence of progress. Prioritize a
  necessary unproved obligation, and among those the item the latest review names highest risk: work
  on it first, developing its leads and bridges when it lacks a mechanism, rather than moving to
  lower-risk items (user, 1 October 2026: "focus on highest risk item first"); distinguish a
  sufficient endpoint from stronger conveniences before adding steps, and before working toward a
  convenience (another measure, a smaller class, a stronger norm) try to refute it on the plainest
  instance that separates it from the goal's own form (16 October 2026: four entries aimed at a
  Lebesgue-measure form that functions concentrated at the sample points refute). Read **Open
  statements** first and name the statement and top-level remaining-route item advanced; do not
  inherit the previous entry's gap without assessing the line. Read in full every parked or linked
  item that **Proposed next step** names on that route. Before reopening an older question, search
  for later links to its anchor and read those entries; restate restart conditions/calibrations only
  from the latest applicable entry after checking for later fulfillment or replacement.
- A property defined over all inputs (linearity, uniqueness, monotonicity, additivity) is not
  concluded from one computed instance: exhibit the defining relation failing, such as two inputs
  whose sum breaks it, or call the instance what it shows (16 October 2026: a rule was called
  nonlinear because one instance differed from a linear flow).
- Restricted examples must test a named general hypothesis, obstruction or mechanism. A growing case
  list or equivalent reformulation leaves the general implication open. `finish-turn.py` enforces
  this: each research entry has a "General statement." paragraph citing the registered claim ID of
  its all-parameter claim (an entry on a build item that declares no claims says there that none
  applies), two finite-check-only entries in a row on one route are rejected (judged from the
  registered claims, not status words), and at most three of any five consecutive research entries
  on a route may register new finite checks other than refutations, so case lists cannot grow behind
  small lemmas; `./compute.sh start` prints the matching warnings before the work begins. State that
  implication and test it against known obstructions, hard instances and allowed equivalent
  representations before further refinement; a surrogate becoming simple need not resolve the
  original obligation. Check preserved hypotheses and accumulated composition costs against the
  goal's budget. Report mathematics and goal progress separately under [Goal progress and scheduled
  review](#goal-progress-and-scheduled-review). If these fail, or repeated cycles leave the same
  required implication untouched, address the failure in the next research cycle (a different
  mechanism, a lead or bridge) rather than refining the same mechanism, and record it for the
  scheduled review; a weak assessment or a descent of more than one reduction below every listed
  open statement is likewise carried to that review, which revises the list. Recheck standing
  hypotheses against the goal's instances every cycle; an obstruction showing that those instances
  violate them ends the line's relevance. When an actual upper bound rules out a candidate family,
  extract the structural reason and check whether it applies to the other candidates. Assess whether
  a strengthened candidate or a stronger replacement can evade that reason; record what the bound
  teaches, not only the exclusion. When using an evolving formula specification, separate structural
  admissibility from the conjectural hardness conclusion. Adopt a refinement only with a proved
  non-vacuity witness at unbounded variable counts and the required encoding budget; otherwise mark
  it provisional. Concrete families are existence and falsification controls, not restrictions on
  the abstract proof. Before choosing each next step, compare direct lower-bound constructions,
  method repairs and structural restrictions by their effect on the missing implication. Upper
  bounds are a possible test, not the default objective. At a method failure, also consider changing
  the specification so the method applies. State which proved properties survive and which are
  traded away, recheck non-vacuity and the goal's full budget, and choose by the resulting evidence
  of progress rather than automatically preserving either the method or the specification. Keep
  unfinished follow-ups under the existing Sub-ideas and queue rules. Stop a series of runs once its
  prediction has passed or failed at the sizes that test it. A larger size, degree or sample needs a
  stated question that the finished runs cannot answer, and an answer that would change the goal's
  missing implication; sharper constants for a result off the critical path are not a reason. Once
  the cases answer their question, develop the general proposition. Before fitting a formula,
  combine computed witnesses by every recorded applicable composition rule (products, restrictions,
  transports). A conjectured sufficient condition for a size lower bound must use the size and must
  not exclude refutations of every size in a complete proof system.
- Distinguish working proofs, imported statements, conditional results, finite checks, conjectures
  and refutations. Match source hypotheses, encodings and versions. For named source conditions,
  retain the defining clause and distinguish whole-object hypotheses from hypotheses on individual
  slices. Preserve original joint degrees and exact parameter accounting. In records and
  conversation, retain qualifiers that distinguish the target from related systems or statements; do
  not shorten its name to one whose problem has a different status. Record full arguments, actual
  tests, dependencies and remaining gaps. Use meaningful falsifying tests/controls; do not rerun old
  suites to simulate progress. A general belief, folklore or "experience" is not evidence (user, 9
  October 2026): support a statement by a proof, a source read in the cycle with its hypotheses, or
  a test able to distinguish it from the alternative at the sizes run. Otherwise label it an
  untested hypothesis and base no decision or status on it. When a proof's steps hold in a more
  general setting at no extra cost, state and prove the general version (each object the statement
  names, a coordinate, a level, a class, checked for a step that uses it; 17 October 2026: a
  crossing count stated at mixed levels used only the first coordinate and held for every matching),
  then recheck every sentence that relied on the narrower form (comparisons, bearings, instances);
  narrow a statement, also on a reviewer's correction, only after naming the step that needs the
  narrower setting, and record that step. A report of a changed hypothesis or statement says which
  way its scope moved (weaker hypotheses: more general; a narrower setting: less general, with that
  step; or false), never a bare "weakened" or "narrowed" (the finisher checks the Verification gate;
  16 October 2026: weaker hypotheses were read as a generalization thrown away). A correct result is
  withdrawn only when false: one that is elementary, dominated or superseded is kept and registered
  with that relation (user, 16 October 2026: "If we get a general version for free, we do the
  general version. Don't throw away results."). To compare dimensions or bound a rank, first seek a
  natural map: an injection into the space claimed larger, or a map whose zero set is described
  exactly, which shows which elements survive. Use a bare dimension count only after the entry says
  which map was tried and where it failed (user, 16 October 2026: dimension counts only when no such
  map is found after an honest attempt).
- Before proposing a next step or naming/developing a result, use `tools/search-claims.py WORDS` or
  `--show LABEL`. The tool logs each search, and the finisher refuses an entry with a Record search
  paragraph whose session ran none, printing the session's searches to compare with the paragraph.
  Unfiltered display searches also surface up to three historical statement matches. For a generic
  mechanism, follow relevant matches and search the immutable [historical
  index](php_codex_handoff/manuscript/CLAIM_INDEX.md) further when needed; bounded suggestions do
  not establish absence of prior work. Use `tools/claim-dependencies.py packet --claim ID` for
  bounded orientation, or `tools/claim-index.py list --fields id,summary --format tsv` for a
  complete minimal inventory when needed. Packets omit proof details and sometimes hypotheses:
  before reliance read the exact statement, proof and applicable corrections. Re-read dependencies
  from their full notebook records, including conventions, never from summaries or memory. When a
  user or source points to a publication or Lean file, read its theorem statement first. Read every
  version listed under "Newer versions" by the search tool and compare field, range and encoding
  hypotheses individually; a later/formalized version need not be stronger. Before committing to a
  direction, inspect the relevant claims' reviewed dependencies and correction/refinement links
  using `claim-index.py graph` and exact metadata. Check conditional premises, stronger available
  versions and concrete transformations in relevant older proofs before imposing a new interface
  requirement; follow only dependencies that matter to the argument. Missing edges do not establish
  independence, and an impact warning is not a verdict that a claim is false. Label
  rediscoveries/refinements and link their original records. Search each newly formulated lemma, not
  only the opening question, by technique name, the record's synonyms/structural names, dual or
  adjoint formulation, and statement content words with `tools/search-claims.py`, one search in the
  words of the objects its proof or its next step works on (the extremal examples, the records it
  could contradict) rather than its own name; when a next attempt's objects change during drafting
  or review, that search is made again in the new objects' words (17 October 2026: an attempt moved
  from nested chains to closed lattice curves, and three records charging such curves were missed).
  Test it against every recorded counterexample, refutation and obstruction for those objects.
  Before drafting its proof, check yourself whether the record already implies it; include the
  relevant prior results in the end-of-cycle review brief. Registration refuses a new claim whose
  summary resembles a registered one unless the spec relates the two (`claim-index.py author
  build`); read the record it names before deciding which. Run the same search when the spec is
  first drafted, before the review, with `tools/claim_resemblance.py SPEC`, which prints the nearest
  registered claims below the refusal threshold too, and read them before the entry says what is
  new; the tool logs its runs and the finisher refuses an entry declaring a claim it was not run on
  in the session. Before drafting a corollary, check for an earlier result under fewer hypotheses.
  Before sending a proved statement to review, name for each hypothesis the step of the proof that
  uses it and the weakest form that step needs, and state that form: a hypothesis copied from the
  instance at hand, rather than read off the proof, narrows the lemma and the next step drawn from
  it (16 October 2026), and a free parameter (a mesh, a scale, a threshold) is stated with the whole
  range its proof allows before a value is chosen for the instance; a statement holding with high
  probability for every value of a parameter names, in its proof, the union bound that covers that
  parameter, and each concentration inequality it uses names the independence it rests on (16
  October 2026: a union over a slope parameter was missing, and dependent multinomial counts were
  summed as independent); say there too which class each conclusion holds for, after
  `<strong>Hypotheses, each with its step.</strong>` (the finisher requires the paragraph of an
  entry registering a proof). Evaluate every inequality a statement or a sentence about the goal's
  endpoint uses at the Nonvacuity witness's parameters, before the review and again for each
  sentence a correction rewrites: a corrected sentence is a new claim (16 October 2026: a correction
  wrote a degree condition its own example violated). Try it on degenerate inputs (the trivial
  instance, the empty one, an input outside its stated form) and report it in the entry after
  `<strong>Degenerate cases.</strong>`: what the statement gives on each, or the hypothesis that
  excludes it (the finisher requires the paragraph of an entry registering a proof). Write down also
  one input that satisfies all the statement's hypotheses, with its parameters, after
  `<strong>Nonvacuity.</strong>`: a statement about a class with no member proves nothing (the
  finisher requires it of the same entries). When the statement extends a recorded one, the input
  must be one the recorded statement does not already cover, and it is checked step by step against
  the rules it uses; it, and a next attempt's Smallest case, say after `<strong>Plainest
  bound.</strong>` what the plainest available bound (a bare count, a one-dimensional estimate, the
  record's oldest applicable lemma) gives on that instance, or why none applies (the finisher
  checks). For a statement uniform over a family, every fixed witness is decided by a bound for one
  function (its variance, or a one-dimensional estimate after a change of variables): the sentence
  then says so and names what the uniformity adds; over a family of polynomially many members that
  bound with a union over the members is the plainest uniform bound, tried before any other (17
  October 2026: two nested blocks, at most \(N^2\) of them, were called a case for a deep lemma that
  the union bound decides). "None applies" is written only after the plainest bound was tried on the
  instance; and a recorded result the draft cites is read also for what it already implies about the
  new statement's special cases. Before a required paragraph or artifact is called done, name what
  it is meant to establish in the case at hand and check that it does: a witness exercises the step
  the statement adds, a Meta names the change its commit made, a message reports a result and not an
  intent (16 October 2026: each of the three passed its rule's wording first); a reply's sentence on
  a blocker, a retry or a prevention reports the act done, with its file or commit, or names it
  undone (17 October 2026: a push blocker was mentioned, not filed). Likewise a prevention, a count
  or a check is reported as in force only beside the output of its run on the case that exposed it,
  at the earliest stage it can run: that it exists is not that it works (16 October 2026: a message
  check announced in force missed its own case's other form, and a replay count could not fail on
  the case it was quoted for). An example or witness offered for a claim, in an entry or a reply, is
  written with the quantity it illustrates computed beside it, never from memory of its shape, and a
  witness offered for a case analysis exercises each branch it is offered for. A proof step that
  makes a term vanish by the value of a factor says where that factor sits relative to every bracket
  or certificate around it, quoted from the construction's record (16 October 2026: a factor inside
  a commutator was used as if it stood outside, and the witness had no branch where it mattered). A
  statement covering several parts (cases, forms, earlier lemmas it refines) gives each part its own
  form, and a simplification true of some parts is attached to those parts only. Name after
  `<strong>Baseline.</strong>` the construction or bound that needs no idea (the obvious witness,
  the trivial estimate) and what the statement adds over it (the finisher requires it of the same
  entries; 16 October 2026: a comparison omitted a multiplier that survived every choice), evaluated
  at each cost class a part of the statement claims (a depth, a field, a size): a route that fails
  in one class may give another part's result (17 October 2026: a logarithmic-depth construction was
  built while the plain route, dismissed at constant depth, gave it at smaller size). An example or
  test computed with the entry's method also gets its own baseline, computed first: what the
  plainest available bound gives on that example. State compositions as lemmas in one common setting
  with a complete proof, not a reference to a sketch. At the start of drafting, run the entry's
  skeleton (its headings and labelled paragraphs, before the body) through `tools/notebook-append.py
  DRAFT --check`, which lists each failing entry check of the append and the finisher that applies
  to a draft, so a required paragraph is planned before the work. Before the reviewer's brief, run
  `tools/draft_claim_sentences.py DRAFT --notebook NOTEBOOK` and read each sentence that cites a
  claim beside that claim's registered statement, and each that links an entry beside that entry's
  title and status line: a sentence may say no more than its source, and one that draws a decision
  from a bound of the entry restates the bound's hypotheses and error terms beside the instance and
  the scale decided. The tool also lists the draft's sentences outside its mathematics that hold a
  count: read each beside the saved output the count came from. A property of a recorded
  construction that a proof step uses (what its terms contain, where a factor sits, what it
  specializes to) is quoted from that construction's record, with its anchor, in the step: a
  property written from the agent's picture of the construction is an untested hypothesis. So is a
  modelling choice behind a computed figure (an area, a weight, the step a correction is assigned
  to): it is written with its derivation before the figure it feeds, since checking the figure
  checks only its last step (17 October 2026: a leg's area was halved in a smallest case, and a
  theorem's step decomposition was not tried before a docstring said the theorem did not apply).
  Evidence for a property of the object at hand (a construction's map, a flow's dependence on the
  counts) is computed on that object, in the variables the property is stated in; a result on a
  model, or on inputs the object never receives, is written as the model's (17 October 2026: a
  nonlinearity in the counts was first shown on a two-value model, then on fields no counts produce,
  before the counts themselves were tried).
- Once the question, argument and evidence are stable, make one focused correctness review of every
  new mathematical lemma, theorem, rule or encoding before assigning its status. Run the exhaustive
  checker for any rule, tree or encoding change before relying on it. Near the end of the cycle, use
  at most one fresh-context reviewer subagent for the consolidated review, given only the stable
  drafts and dependency anchors/excerpts, to try to break the arguments and identify unused
  hypotheses. After that check, the same reviewer also helps (user, 9 October 2026): name the
  cycle's open point in the brief, after the correctness items, and ask for a way past a failed step
  or a reason none exists, a proof or counterexample for an unproved expectation, or whether a new
  bound is tight. Its suggestions are unverified leads: list them in the entry under `<h4>Reviewer's
  suggestions, unverified</h4>`, each item ending `<strong>Record.</strong>` with the outcome of a
  record search made before recording it (claim IDs or anchors that bear on it, or the words
  searched without a match; the finisher checks this), and verify one yourself before relying on it
  or naming it as a next step; until then a report to the user that uses one says "unverified"
  beside it, as the entry does (16 October 2026: a reply narrowed an open case on a reviewer's
  computation without the label); one that adds or strengthens a claim gets the follow-up check
  below. Handle pre-proof novelty searches yourself; do not spawn a separate novelty reviewer. The
  user authorizes and encourages spawning reviewers for any needed review in this and all future
  Spin runs; no separate confirmation is needed. In both Codex and Claude Code, explicitly set
  reviewer subagents to **medium** reasoning, regardless of the main agent's reasoning level; do not
  inherit its high or higher setting. Claude Code uses the committed `medium-reviewer` agent type
  (`.claude/agents/medium-reviewer.md`, loaded at session start). Codex uses a native subagent with
  no conversation history, explicit `gpt-6.1-sol` and `medium` effort; see [the reviewer
  protocol](tools/CODEX.md). Give it the canonical reviewer instructions and only the review brief
  and dependency excerpts. Read-only behavior is an instruction, not a separate sandbox: child
  agents inherit parent permissions. Do not create root sessions for reviews. If medium effort is
  unavailable, never substitute a higher-effort reviewer: leave the gate incomplete (conditional
  status) and file a user request. Resolve every reported gap and drop or justify each unused
  hypothesis. Brief reviewers narrowly: exact files/anchors, at most one or two named claim
  searches, dependency excerpts in a scratch file, and required changes as short bullets. Use one
  consolidated pass by default; scheduled reviews use the staged architecture brief below with that
  same reviewer. Follow up with that same reviewer only for those stages, to resolve a concrete gap
  or check a correction that adds or strengthens a claim, adds an outcome or an argument the
  reviewer did not write, or rewrites code it read (only deleting text or adopting the reviewer's
  own wording counts as narrowing; code written to carry out a reviewer's suggestion is not its
  wording, and goes back to it before the commit), and always before an entry removes a queue item
  on corrected work (the finisher refuses a removal whose gate says the reviewer did not read the
  corrections); do not spawn additional reviewers in the cycle. Defer optional extensions. Record
  dependencies re-read, checks and reviewer verdict in a short **Verification gate.** paragraph, not
  the status line; it credits the reviewer only with what its report says it checked, a sketch it
  marked unverified staying unverified, and an entry's scope sentences (Not covered, a commit
  message) leave open what no one checked. An incomplete gate means conditional status, not a
  working proof; correctness takes precedence over cycle speed. A report to the user about
  current-cycle mathematics, from opening until its correctness review has returned and its
  corrections are checked, prefixes each conclusion with **Unreviewed:**, including before an entry
  draft exists; saying later that a reviewer is checking it does not replace the label. When a
  review narrows or withdraws a conclusion already reported, the next report says so explicitly,
  naming the old and the new scope. Prepare staging paths, commit message and focused metadata
  checks during review; the checks include `./tools/check_records.py --diff`, which flags commit
  hashes, environment literals, backticks in the notebook's HTML and long status lines in the lines
  being committed. Then run a sequential checkpoint batch: preparation marker, checks, provenance,
  timing export/archive, staging, commit, and any authorized push. Stop on failure. For asynchronous
  checkpoint commands, observe terminal success of the commit and required base synchronization
  before planning the next result; until then, do only checkpoint preparation. A launched command is
  not a completed local checkpoint.
- Measure every research turn from as early as practical, including reading, failed attempts and
  retries: `./compute.sh start TURN`. Codex uses active session metadata; omit `--model` rather than
  supply a guessed or placeholder label. For other agents or unavailable metadata, follow the
  computation policy's fallback. Disclose work before instrumentation. Follow the computation policy
  for phase markers, protected commands, honest timing scope, numerical accuracy and outputs. Keep
  full output on disk and display bounded excerpts. Focus checks on mathematics and touched links;
  run site/rendering checks only for layout/tool changes or a concrete rendering concern. Do not
  display PNG previews unless requested.

### Order of work

For any proof, test, witness, next attempt or summary (each line from a mistake of 16 or 17 October
2026; a rule added after a mistake is applied at once to the next text written; moved here from
CLAUDE.md on 17 October 2026, user: "Please don't perform improvements in CLAUDE.md. the place is
AGENTS.md"):

- Choose a target by what is true at the goal, not by what the tools at hand prove easily: a target
  the tools reach easily is first tried for refutation on its plainest counterexample. A method's
  failure is written as the method's, beside the plainest recorded tool tried on the same instance,
  before it is said to bear on the question or to choose the next direction (17 October 2026: a cell
  scheme's stop was read as forcing a refutation, while the per-level counts reduced the instance to
  a repair).
- **Shortest route first.** Once the shortest direct route to the goal is identified, it comes
  before everything else; work that orbits the goal (one more exclusion, a side lemma, a stronger
  convenience) waits, since time and tokens are finite (user, 17 October 2026: "When you identify a
  direct shortest route above all else, you prioritize it above all else. You do not keep orbiting
  around the goal and producing math just for the sake of producing math."). Exploring the field,
  obstructions included, is right while no direct path is known; once one is identified it is acted
  on at once (user, same day). A direct path the agent sees is stated out loud, in the entry and the
  reply, never left unnamed to keep exploring (user, same day: "If you got the idea, state it out
  loud"). Every research entry names that route in a `<strong>Shortest route.</strong>` paragraph
  and takes it, or writes "Not taken" and the concrete reason, or, where none is known, "No direct
  route known yet" and what the exploration is to find; `tools/notebook-append.py` refuses an entry
  without the paragraph, and a Sonnet judge (`tools/route_judge.py`; Haiku missed the prompting
  case) reads each entry against the living sections and refuses a detour that does not say why.
- When the record's obstructions name the mechanism a proof needs and no recorded construction has
  it, the next cycles build a candidate with that mechanism and test it, before any further class is
  excluded: an exclusion narrows the search, and only a construction can reach the goal (user, 17
  October 2026: "You identified exactly what is needed to reach the goal ... But you did not make
  any attempt to construct this?").
- First draft the Plainest bound: the bare count or the oldest recorded lemma on the instance,
  before any method is chosen; then, once a proof exists, each of its own steps used alone (a
  substitution, a reduction, a restriction), since a step that already decides the instance makes
  the rest of the proof a variant to compare, not the result. Apply it to the question's own objects
  as well as to the intermediate ones the method introduces (17 October 2026: a bare difference of
  certificates was applied to an intermediate sum and not to the transformed image itself, where it
  showed the conclusion empty). A recorded bound used as the baseline is run with each free
  parameter of its proof at its whole range, not at the values its statement fixed (17 October 2026:
  a corollary's argument at a free level already gave the new bound but for one length).
- Before calling a case hard, handing a step to someone else or asking a question, take the cheapest
  step on the instance yourself: a union bound over its family's members, the default the rules
  already give, the result of the edit just made (17 October 2026: a two-block case called deep, a
  question the Spin rules answered, a commit sent before its edit's result).
- A threshold, constant or range drawn from a bound is computed from the bound as displayed, at the
  instance's parameters (the saturating ones included), and says which of its parts comes from the
  bookkeeping rather than the object (17 October 2026: a budget threshold contradicted its own
  displayed bound, and a saturating perimeter was written without its level). So is the sign a proof
  step gives a term ("at most \(0\)", "contributes nothing", "negligible"): the term is written out
  and evaluated at its extreme member before the sign is (17 October 2026: \(N-|T_j|\) was bounded
  by \(0\) from its shape, and a reviewer passed it).
- A sentence a reviewer finds wrong is replaced by one derived again from the statement and the
  records, its figures computed, not patched from the old wording; a sentence wrong twice is
  redrafted from its sources before it goes back (17 October 2026: three versions in a row of one
  case's dismissal, each patched from the last, each wrong). The claim the sentence makes is
  replaced wherever it is written (the claim spec's notes, the commit message, the living sections),
  not only where the reviewer quoted it (17 October 2026: a spec note kept an exclusion the entry
  had withdrawn). So is a reviewer's lead adopted as a next attempt: each statement it uses is
  reread for its constants, levels and ranges, and the accounting is redone, before it is written
  down (17 October 2026: a lead written into a Follow-up dropped a theorem's constant and the box
  growth of a raised level).
- When a tool refuses, collides or reports something unexpected, find its cause before trying
  another route, and state the cause; an opening claim is stated only in the scope already proved. A
  retry that passes because the check remembers the text, a rerun until a timing passes, or a rule
  left written after it let the same thing through is another route: the refusal is a finding about
  the tool or the work, fixed or queued with its cause (17 October 2026: all three in one framework
  turn). Before a second attempt at a refused step, write in the reply the line of the refusal that
  names its rule and what in the input broke it; an input changed until a gate passes, without that
  line, is the same route (17 October 2026: a launcher's five-word line rule and a qualifier gate
  were each answered by edits before their cause was read). A refusal that names no rule (a bare git
  error) has its cause found by changing one suspected factor and rerunning the same step; a cause
  not so shown is written as a guess, and no other route is taken on it (17 October 2026: a rebase's
  refusal was put down to a commit hook, a hand commit took its place and wrote git's conflict
  comments into the message, and the cause was unstaged files). Before an action meant to undo or
  forestall something (a correction, a retraction, a note to an agent), read the record showing that
  the thing happened and quote it in the reply (17 October 2026: a "disregard" note went to a
  reviewer that had been sent nothing).
- A property of a family (nested, disjoint, packed, few per point) enters a proof only after it is
  checked on the family's extreme members: boundaries that coincide, many members through one point.
- A sentence that gives a decision its reason (dropping, choosing, calling a case decided) names its
  source: a proof, a statement of record, or the word judgement; the reason is written from that
  source, not from the decision it is meant to support.
- A size or depth stated for a construction is counted from the construction written out in the
  proof, level by level of its gates, and the count is written beside the figure: a cost read from
  the picture of a construction is a guess (17 October 2026: two depth bounds in one draft, \(k+5\)
  for five and \(+4\) for \(+5\), and an unstated depth the entry before).
- Check a witness's or construction's constraints as functions of the growing parameter, in the
  limit, never at the size written for; check there also what the recorded statements it is meant to
  escape give on it, and read each line a listing tool prints beside the source it names before the
  draft goes on (17 October 2026: a witness fit its own hypotheses in the limit while the record's
  bound covered it there, and a listed sentence applied a lemma outside its image). Its parameters
  are the object's own quantities, computed (the largest valid constant, an exact degree), wherever
  a recorded statement is dismissed or compared on it; a valid smaller constant is otherwise
  legitimate, but a recorded statement dismissed at a convention may apply at the object's value (17
  October 2026: two recorded bounds were called inapplicable at the expansion \(n/2\) of a graph
  whose expansion is \(33\), where they apply and are only vacuous). A family's or an object's
  parameters are copied from its registered statement, read in the turn, never from a summary line
  that may describe a neighbouring construction (17 October 2026: a script took a growth rate from
  the living section's line on another family and printed every figure off the family it named).
- Recheck each step's preconditions (independence, quantifier ranges, domains), not only its
  arithmetic. An inequality multiplied by another or raised to a power keeps its direction only
  where each factor is nonnegative: write each factor's sign range beside such a step, take a free
  parameter's range from it, and read a computation that finds a factor outside that range as a case
  where the statement may be false, not one where it is empty (17 October 2026: a bound with a
  factor \((1-x)^t\) was stated for every \(x>0\); at an even \(t\) and \(x>2\) it was false where a
  script's domain error had been read as an empty bound).
- Write a negative sentence ("no estimate applies", "the record lacks it") only beside the attempt
  that failed.
- Write the Record comparison before New mathematics, the title or any sentence calling a result
  new: compare from the record's side (the entries a draft leans on, their dependencies and
  dependents), not from the draft's own wording, and only then decide what is new. The comparison
  reads the proofs of the results the draft builds on for a step, not only their statements: a step
  that is inside a cited proof is a citation, not new. A result computed on one side of a recorded
  duality (a flow and its dual class, a cut and its single layer) is first read on the other side,
  whose recorded bounds apply through that duality (17 October 2026: a single set's forced flow cost
  was called new while a recorded single-layer bound gave it through conjugacy).
- Name a relation between two statements (false, superseded, implied, a special case) only after
  setting the earlier statement's own words beside the new one, and choose the weakest relation both
  support: a statement true of its own method is not made false by a better method; a one-sided
  bound is summarized as a bound or a sufficient condition, never with "is", "equals" or "reduces
  to". A question is called a restatement of a wider one, or the same question as another, or an
  item merged into another for its mathematics, only beside the construction that carries every
  member of the wider class to the property asked about, with its cost (17 October 2026: a count
  argument was merged into a mixed-level question before the counting step over levels and its
  factor were written): what a narrower class has is not yet what every member can be given (17
  October 2026: an item was closed from what matched images share with an initial segment, before
  the envelope certificate that gives it to every certificate was cited).
- A condition taken from a record (what a lemma covers, what a numbering needs, when a test applies)
  is written with the record's own sentence quoted beside it, never restated from the gist kept
  while reading: a paraphrase keeps the condition and loses which way it runs (17 October 2026: a
  review's "necessary for such a numbering, not sufficient" was restated as covering every case).
- A choice made to save cost or fitted to the case at hand (a sample size, a check's scope, a
  summary word) is written beside what it changes in the quantity measured or the class covered,
  before it is used (17 October 2026: a seed count cut for time moved an estimator's bias, a
  launcher check covered only the command that prompted it, and "Gaussian by the theorem" stood for
  a lower bound).
- Write every summary (title, New mathematics, Bearing, commit message, a claim spec's rationale and
  next action, report) last, from the final statement with its hypotheses and qualifiers; relay what
  a reviewer, agent or tool found from its source, with its qualifiers word for word, and explain a
  failing check only by quoting the lines of its output that show the cause. A shorthand coined
  while drafting (a name for a class of objects) is a new statement, not a name for the hypotheses:
  a sentence using a result says its hypotheses in the statement's own words (17 October 2026: a
  shorthand stood for "one reversible rule" in five sentences, which lost reversibility). A summary
  of a result's reach (a Bearing, a living-section clause, a review's Decision, a reply) names the
  class its hypotheses cover, never the class its mechanism suggests (17 October 2026: "no rule can
  change the square means" was summed up as "no flow", in an entry and then in the review after it).
- When a computation agrees with what was expected, write next what it does not show, and read each
  of its figures for what it says against the conclusion (a statistic on the far side of a bound the
  conclusion assumes), before the sentence that concludes from it (17 October 2026: a closure read a
  kurtosis offset as support while that kurtosis, below the baseline's, pointed against it); and
  before posing a statement drawn from one worked construction, write down the construction most
  unlike it and check the statement there.
- Before writing any durable text (docstring, commit message, entry, reply), list each figure and
  finding it will carry beside its source (a saved output, a named agent's report, a proof in the
  entry); one whose only source is another agent's report is written as that agent's, or recomputed
  and saved first.
- A conjecture drawn from a check states the quantity the check computed (its maxima, its field, its
  representatives) and the range of sizes it computed; a stronger form, a wider range included, is
  tried first against the system's trivial transformations and its smallest instances (16 October
  2026: a conjecture dropped the check's maximum over representatives and failed on the plainest
  one; 17 October 2026: a conjecture from boards of three to six holes, stated for every size, was
  false at one and two).
- Before a script compares two quantities over choices (a maximum or minimum over representatives,
  the side of a bound), derive in its docstring from the containment or inequality which extreme the
  question needs (17 October 2026: a domain saving was taken as a maximum where the bound needs the
  minimum).
- A conclusion carried to another case (another field or characteristic, the next value of a
  parameter such as \(K\), a single family where two were worked) is derived again there, in the
  draft, with the step that carries it; a case not rederived is written as not covered (17 October
  2026: a single-family failure read from characteristic \(2\) was stated for every field, and a
  ballot count at \(K=1\) was carried to \(K=2\), where a two-pigeon pair breaks it).
- Before listing a hypothesis (a field, a characteristic, a closure type, a size), redo the step it
  is listed for without it, with signs or general coefficients, and list it only if that fails (17
  October 2026: an identity valid over every field was listed as needing characteristic 2). A
  hypothesis that the step uses only to say what the conclusion is (a zero set, a value, a formula),
  not for the conclusion to hold, is not a hypothesis: the statement gives the conclusion per case
  instead (17 October 2026: a result stated outside characteristic 2 because a set it named read
  differently there).
- Write a statement's hypotheses, scope and qualifiers ("exactly", "every") after its proof, from
  what the proof's steps use and give, and its witness after that, one on which the step the
  statement adds is used: a statement drafted first carries the instance it was drafted for (17
  October 2026: a duality stated with coercivity and one grid, neither used, an equality summarized
  where the proof gives one up to constants, and a witness that never used the implication). When
  the proof splits into cases (characteristics, sizes), each hypothesis is stated per case, from the
  branch that uses it (17 October 2026: a pigeon bound needed in two characteristics was stated for
  all).
- Read a rule or a listed record by applying it to the case in hand (the next attempt, the instance,
  the sentence being written) and writing what it gives there, never as seen once read (17 October
  2026: a listed lemma, read, already answered the entry's next attempt). A cited lemma is applied
  through its proof as well as its statement: each step is run on the case, and a hypothesis no step
  uses does not limit it there (17 October 2026: a lemma stated for balanced thresholds decided an
  unbalanced case by its own proof step, and a sub-idea was closed as open).
- When a written rule lets the same mistake through a second time, replace or back it with a check
  in that turn, rather than citing the rule again (17 October 2026: a rule on forced controls,
  written after one, did not stop the next).
- A reply to the user is held to an entry's rules: say what the record covers, or offer a direction
  as new, only after a search of the record in the words of its objects in that turn; label a belief
  without proof or test an untested hypothesis; settle a question by searching and testing its
  readings rather than handing it back; and run work through the launcher as in an entry (17 October
  2026: a reply offered substitutions and extension variables as unexplored, both recorded, and the
  stand-in review found four more replies that broke entry rules).
- A gap found in the record, or a promising idea met in conversation, is the next attempt: try it or
  queue it in that turn, and report it so; describing it as missing, or offering it to the user, is
  not an answer (user, 17 October 2026: "We are the ones developing the record").
- Before a follow-up is Developed or Closed, write the item's question in each reading its words
  allow, each with its attempt: what the entry's own definition covers is not the item (17 October
  2026: a corollary covered the reading the draft had defined, and two other readings of the item
  were listed as covered without an attempt). The readings vary each quantifier the words leave open
  (some or every choice, one or all levels), not only each constant (17 October 2026: readings
  varied in their constant only missed the universal one, the only one that glued).
- Before calling a question decided, write the class its words range over (all forms, all closures,
  all errors, every value of a parameter it bounds by an inequality) beside the class the argument
  covers; it is decided only where the two agree (17 October 2026: a bound stated as an inequality
  was decided at its equality, and "forms" were read as the ones the argument built).
- Put a new rule or check where the file that owns its kind says it belongs, read before writing,
  not beside the lines last added (17 October 2026: two days of rules went into CLAUDE.md, which
  says that shared rules are in AGENTS.md, because the previous rules were there).
- Before naming a new artifact (a results folder, a claim ID, an anchor, a session), list what
  already exists under that name: a name chosen from memory of a pattern can be an earlier entry's
  (16 October 2026: a new review's folder overwrote an earlier review's record).
- Count a step done only when its effect is seen, not when its command was issued: read the written
  file's new content or the tool's own report of the write, the commit's subject in the log, a mark
  matching on the case it is for (17 October 2026: an excerpt refused behind a silenced error, a
  stale commit subject printed and not read, and a word mark that matched a path). A reply or entry
  that says a comparison or check was made (summaries against statements, a draft against a rule)
  quotes one line of what was compared, its outcome beside it (17 October 2026: a flag certifying a
  comparison was passed on a reply that showed none). A check's refusing test cases are the
  sentences that prompted it, quoted before its pattern is written, and a scan count of zero is
  reported beside the listing of what the check reads (`tools/record_scan.py` block-counts): a
  pattern fitted to a paraphrase matches nothing and its zero looks like a clean record (17 October
  2026: a block-count check missed every form the record writes).
- Before choosing a method for a next attempt, apply to the goal's own quantity what the entry has
  already computed (an average, a mean the constraints fix, a smallest case's value) through the
  plainest properties of the cost (convexity by Jensen, monotonicity): a method that a few lines of
  this decide is not needed (17 October 2026: a next attempt planned a fraction argument with an
  energy bound, while Jensen applied to averages its own smallest case had computed decided the
  whole class).
- Before writing a script for an attempt, run the attempt by hand on its smallest nontrivial
  instance and write the outcome down; a script is written only for what that hand step leaves open,
  and each of its controls is first tried on an input where it must fail (17 October 2026: a routing
  rule was simulated over four sizes when two levels by hand already gave the dyadic flow, and its
  control was constant by construction). A question that does not change when its objects are
  replaced by another presentation (a set by its span or a sum of its members, an object by an
  equivalent one) is first tried, by the recorded lemmas, on each presentation they decide; the
  entry lists the presentations tried before any script (17 October 2026: a joint quantity was
  computed after one representative per object ran out of room, while a sum of the objects had
  room).
- Every command and every path in it serves the step at hand: before a call, drop each part whose
  output nothing reads, and reach outside the worktree and the session's scratch only through the
  route the framework names, since in auto mode such a reach stops the user at a prompt (17 October
  2026: a copy of a subagent transcript to /dev/null, added for nothing, prompted the user).
- Run a required tool or check so that it does its job, never in the cheapest form that passes its
  gate (an output cut short, a paragraph filled with placeholder words, a search run only to be
  logged, a clause such as Tried: written before the action it reports): if a gate's form is a
  burden, change the gate in the open, not its use. A tool's recording step (a read log, a stamp, a
  marker) is left to the tool that does the duty it records, never called from a script of one's own
  (17 October 2026: a scratch script that printed 300 characters of each summary logged its claims
  as read). Work that a budget or a tool makes harder is done in the turn that meets it, by the work
  the obstacle stands for (consolidating the full section, queuing the item, fixing the failing
  tool), never moved to a later commit (17 October 2026: a full section, a build to queue and a
  failing tool were each set aside).
- Before every reviewer brief, reread the draft once against each item of this list and against the
  rules above on statements (free parameters at their whole range, searches under other names), item
  by item, rather than relying on having known them while drafting.

### Goal progress and scheduled review

Keep the existing cadence: six research cycles, then one route review. Do not add reviews or
reviewer agents every two cycles. Two cycles reporting the same obligation unchanged produce a
turn-start warning for the next scheduled review; audits and unrelated work do not erase it.

Each new research/review article names its stable **Open statements** ID in `data-obligation` (not a
newly named local lemma) and sets `data-goal-progress="advanced"` or `"unchanged"`. Give separate
**New mathematics.** and **Goal progress.** paragraphs. The first states what was obtained,
including no result; the second states exactly which necessary implication changed and why, or that
it remains unchanged. `advanced` cites a claim declared by the entry with a proof, conditional
reduction or refutation. A bigger toolbox, stronger convenience, equivalent reformulation or finite
check is not by itself goal progress. From the third research entry in a row that reports a route
unchanged, the paragraph ends with `<strong>Bearing.</strong>`: what the entry's result gives at the
goal's own parameters, or that it gives nothing there and why the cycle was spent on it (what the
result could have given; that a review or an earlier entry asked for the work is not a reason, and
the finisher refuses it), and the article declares `data-bearing="none"` or `"some"` to match, a
`some` bearing ending with `<strong>Not covered.</strong>` and the cases its result does not reach;
after two entries in a row on one queue item declaring `none`, the next entry develops a different
item; after three entries in a row on the route declaring `none`, across items, the next states
before its work, after `<strong>Best outcome.</strong>`, what its best outcome would give at the
goal's own parameters and, by claim ID, the recorded result it must beat; and an entry in such a run
whose follow-up is Continuing states `<strong>Record search.</strong>`, the registry searches made
for the next attempt it names (the finisher checks all six). A rule that limits which work may be
started (an item, a route, a kind of entry) is checked where that work starts, at `compute.sh start`
and at the Proposed next step, the finisher's copy being a backstop; work done against such a rule
is never discarded but held for the user's choice (user, 17 October 2026: "work should be blocked
before you waste time and tokens, not when it is already done", and "Do not throw away work ever").
Keep the obligation ID stable while that implication is unchanged. The finisher checks declarations
and evidence references, not the truth of the agent's assessment; the existing reviewer must
challenge that assessment. Every new `data-bearing="some"` entry links its matched parameter ledger
from **Bearing** with a named link such as `<a data-ledger="selection"
href="#selection-ledger">selection budget</a>`. Each **Nonvacuity** paragraph uses a matching named
link to identify the particular budget its witness verifies. Assertions about both or all budgets
need separately named references. These checks validate references and declarations; the reviewer
checks that the inequalities and application really hold.

Fold an `<h4>Architecture review</h4>` section into each scheduled review, with these
`<p><strong>Label.</strong> ...</p>` paragraphs:

- **Necessary target.** State the weakest endpoint that suffices for the actual goal, with its
  quantifiers, instances and degree/size budget. End with `<strong>Downstream.</strong>`: the target
  evaluated through the proved downstream statements, citing their claim IDs, with the explicit
  consequence and whether it is the goal or weaker (the finisher checks presence).
- **Extra requirements.** Contrast that endpoint with the current approach's additional demands:
  existence versus arbitrary choices, derivability versus literal vanishing, or one surviving object
  versus a separately large space. Justify each demand or identify what can be weakened.
- **Independent alternative.** Initially give the review's existing medium reviewer only the goal
  and bounded available-result excerpts, withholding the preferred route, and ask it open questions:
  one that presupposes its answer's form (a single reason, a negative, a named class) steers the
  stage (16 October 2026: a blind reviewer reported two such questions). Its brief opens with a line
  "BLIND STAGE" and sits in a folder of its own, which `tools/hooks/reviewer_brief.py` checks (17
  October 2026: a brief beside the previous review's text leaked the route). List the route's
  registered open conjectures with their evidence beside the proved results. Ask for a materially
  different architecture or a reason none was found. Then reveal the current route for comparison
  and the usual correctness review. Link the reviewer evidence here; do not manufacture an
  alternative or spawn a second reviewer for this step.
- **Rank normalization.** For dimension counts, ask whether losses and surviving objects are
  measured in the same quotient and whether relative contraction could replace absolute smallness.
  Otherwise state why this question does not apply.
- **Decision.** Choose the weakened endpoint or competing architecture to test, or justify retaining
  the current one against the comparison. A decision that moves cycles away from an order the user
  set for the goal's statements says so in the notebook's Route decisions and in the next report to
  the user, as the agent's decision the user may reverse (16 October 2026: a review switched
  priorities by its own rule and the user had to ask). A branch written before a run names what
  would make its outcome an artefact of the instance (odd or even sizes, one size, one input form);
  a Decision drawn from a run that departs from the earlier ones first runs the cheap control those
  data suggest, or states its measured cost (17 October 2026: a review left a testbed on one even
  board after odd ones, and the even control, run in a second, reversed it).
- **Decisive test.** Name the next cycle's concrete test and the outcomes that would change the
  required implication or the chosen route. State **Test disposition.** New operation or Retained
  exploratory. A new operation states **Operation.** and **Prediction.**: the actual operation or
  restricted hypothesis, and outcomes distinguishing it; a rewritten parameterization is not an
  operation. Each outcome is written as a relation among the quantities the test computes, and what
  it means is derived from their definitions and containments, never named from the mechanism hoped
  for (17 October 2026: an outcome "larger than the sum over choices" was called a survivor no
  representatives explain, while a further computed quantity, the intersection of per-error sums,
  explained it). A retained exploratory attempt links its earlier review after Test disposition and
  claims no new mechanism. The same reviewer checks this classification and the operation's content;
  the finisher checks the declaration, new-operation reports and retained-review link. Read the
  earlier reviews' tests first (`tools/notebook-excerpt.py --review-tests`). Search the registry for
  the test as for a new lemma and end with `<strong>Record search.</strong>`, the searches and what
  they returned (the finisher checks it): a test the record already answers decides nothing. Before
  both state `<strong>Trivial cases.</strong>`: how each quantity the test compares behaves under
  the object's trivial transformations (implied or duplicated rows, another presentation of the same
  object), and the trivial instance, if any, that would give each outcome, and the structure of the
  instance's own system that could decide it (an axiom of degree one, a member defining a variable,
  an inert or domain-model range); a question with a trivial answer is not given a block (the
  finisher checks presence; 16 October 2026: a test was decided by its system's linear axioms, which
  its Trivial cases did not list). Then state `<strong>Power.</strong>`: what the recorded upper
  bounds and method limits give on the test's object, and for a computation the reachable sizes and
  why its outcomes differ there, and whether the test's instance lies in the goal's parameter window
  and, if not, what its outcome bears on (the finisher checks it); work out for each instance the
  operation names the outcome its Trivial cases and Power already fix, and drop an instance they
  decide (twice on 16 October 2026 a review posed a test whose every instance its own bounds
  decided, so it could not fail); an operation that states an inequality is tried there also at both
  extremes of each parameter it names (objects packed and spread apart, one and many), since the
  case it was drafted from is one extreme (16 October 2026: a bound in a chain's band width failed
  for layers spread across the square). Write that work out after `<strong>Instance
  check.</strong>`: each inequality the Trivial cases and Power use, evaluated with the instance's
  numbers (the finisher requires a numeric relation there; a third review that day called a room
  tight that its numbers gave as \(2<3\)). Say after `<strong>Attempt.</strong>` what was tried,
  before posing the test, to answer it from the statements it cites, and where that stopped: a test
  those statements answer in a few lines is a lemma for the next entry, not a test. The Attempt also
  runs, on each instance, the computation the record's scripts already build for its objects when it
  takes seconds, and states for an instance it leaves to the test the measured cost of that step (17
  October 2026: an Attempt stopped at a step a recorded script decided in seconds). Apply this again
  when the reviewer supplies the missing argument: rewrite the decision and next step as a
  lemma-first entry before finalization, rather than retaining an unanswered test. The second-stage
  brief asks the reviewer to try the step at which the Attempt stops, and the review's Verification
  gate says what it found after `<strong>Attempt checked.</strong>` (the finisher checks).

The next research cycle on that route reports the actual outcome in **Architecture test.**, opening
with `<strong>Decided.</strong>` or `<strong>Not decided.</strong>` and which of the review's
outcomes occurred (the finisher checks the word), and links the review's anchor. This can be a proof
attempt, not necessarily a computation. More local lemmas without that test do not satisfy the
requirement. An explicit user-picked task may defer the test, but does not clear it. These checks
apply to new entries; do not retrofit or rewrite historical assessments.

## Notebook and claim metadata

- `notebook.html` owns the main goal; each registered side notebook owns its thread's current
  mathematical state and full record. Select the thread via [the side-notebook
  workflow](tools/SIDE_NOTEBOOKS.md); never replace main living sections with a side goal. Edit the
  selected notebook directly; `python3 server.py` serves the live notebook on localhost:8000 and
  offers a reload when it changes. `index.html` owns layout. `research/notes/RESUME.md` is
  navigation only: change it for workflow/navigation, not new findings. Supporting notes hold
  evidence, proofs and dated audits, not duplicate living summaries. Label historical snapshots; Git
  already preserves prior overviews.
- After every research turn, review/update **Where we stand**, **Open statements**, **The remaining
  route** (highest risk first), **Proposed next step**, and **Working mathematical context**. **Open
  statements** lists at most about five self-contained open statements whose conjunction with proved
  results gives the goal, each with its status and the instances it must cover; every cycle names
  the one it advances. Lead with the selected thread's goal, keep the route/next step on its path,
  and mention side publications briefly. Do not invent progress. Keep exact setup, degree
  conventions, linked hypotheses/proofs and unresolved dependencies needed next; consolidate by
  topic/purpose, not by adding a subsection every turn.
- A notebook whose route has a standing per-entry duty declares it on a living section as
  `data-entry-paragraphs="Label one|review:Label two"` (an item without a kind applies to research
  entries): the finisher then rejects an entry of that kind without a `<p><strong>Label.</strong>`
  paragraph, and `compute.sh start` prints the research ones. The duty binds only the notebook that
  declares it. Use this instead of stating such a duty only in a living paragraph.
- All pre-record regions have [configured budgets](research/context-budgets.json). Run `python3
  tools/notebook_context.py` while drafting; see
  [counting/enforcement](research/notes/CONTEXT_BUDGET_PLAN.md#budget-operation). Soft excess
  requires your editorial review; any section or aggregate hard excess blocks finalization and CI.
  New sections need budget allocation. Only an explicit user override authorizes raising/waiving
  hard limits; record it transparently. Consolidate yourself without asking the user to edit.
  Preserve essential hypotheses/warnings and link full arguments/history in the unlimited record;
  preserve unique substance durably before shortening. Do not duplicate Git snapshots.
- Append a dated Research-record entry for **every research turn**, including unsuccessful attempts,
  obstructions and turns with no useful result. State the question/approach, actual outcome and
  remaining gap honestly; invent no lemma to justify an entry. All substantial new mathematics
  belongs there **in full**; supporting notes/chat alone are insufficient. The record has no size
  limit. Routine setup/admin turns need no mathematical entry.
- Use MathJax for inline mathematical notation as well as displayed equations; reserve code
  formatting for program identifiers and source references.
- Give each article a stable anchor, descriptive title/date and explicit status (working proof,
  conditional result, conjecture, finite check, refutation, etc.). Include assumptions, precise
  claim, complete argument, dependencies, parameter/ degree costs and checks. Keep `<p
  class="entry-meta">` at most 300 characters before the producer credit added from the timing
  session. Do not number cycles; use anchors, and route IDs for parallel formalization entries. The
  status line contains the status and at most one scope clause, then a descriptive cycle label;
  details belong in the entry's sections. Name new lemmas, theorems, corollaries and conjectures in
  one to four plain, descriptive words. Variants get their own name or a meaningful qualifier, never
  letter codes or prime/digit/letter suffixes. Follow the descriptive names already used in the main
  notebook; cite older coded results descriptively, usually using their claim ID's words. The
  finisher rejects new letter-code result names outside tables.
- Tag articles with `data-kind="research|review|formalization"` and `data-route`, naming a top-level
  remaining-route `data-route-item` slug (or `side-...`), never a sub-gap. Route reviews come once
  in seven entries: six research entries, then a review (user, 3 October 2026: "Drop to one in
  seven"); the finisher rejects both a seventh research entry in a row and an earlier review. A
  review is goal-level (`data-scope="goal"`) exactly when its line's open-item count has not dropped
  since the review ten or more research entries back, and ordinary otherwise (user, 3 October 2026);
  the finisher enforces both directions and `compute.sh start` prints which one is due. A review
  states the line's general claim, what the main goal needs, a falsification attempt, an
  evidence-based qualitative assessment of **that line only**, and the next step on the highest-risk
  item. Under an **Obstacle** heading it states precisely what the line is stuck on. Outside leads
  and Absurd bridges exist to answer that obstacle, not as items of their own: choose them by asking
  which theorem, in any field, solves a problem of this shape, and end each with
  `<strong>Answers.</strong>` saying how it would resolve the obstacle (user, 26 September 2026:
  "They are supposed to provide answers to our current obstacles"; the finisher checks both).
  Outside draining mode (defined below), it has an **Outside leads** section (the finisher requires
  at least three): ideas from other areas of mathematics, each a named theorem or source rather than
  a field, with the open statement it targets and where it would break, including leads the record
  names but never followed. It also has an **Absurd bridges** section (at least two): areas that
  never stood near these objects because nobody thought of applying them here, from any field
  (mathematics, computer science, theoretical physics, chemistry or anything else), each with the
  translation that would carry the objects across, what a theorem there would give, and the smallest
  test of the translation. Choose each test by where the question is open, not by the instrument at
  hand: before building it, name the instances on which the recorded bounds and the plainest count
  leave its outcome undecided, and run it there. Run every cheap test named in these sections within
  the review cycle itself, and end each item with its outcome, `<strong>Test.</strong>` followed by
  Passed, Falsified or "Not run:" and the reason (the finisher checks this); falsified items stay
  listed and count toward the minimums (user, 25 September 2026). A Passed item states, after
  `<strong>Break point.</strong>`, where its translation would break and what the test found there:
  a test of the named theorem alone, or of a statement recalled and unread, is Not run for the
  translation (the finisher checks the paragraph). Write each item's outcome word last, from what
  its Break point found, and a review's Decision after its Attempt has tried the step it names with
  the sources at hand. A summary is rewritten with what it summarizes: when a correction narrows a
  passage, reread in the same edit every sentence that summarizes or cites it (its Answers, its
  outcome word, the Decision, Bearing and commit message) before the draft goes back. A Not run item
  resting on a source recalled or unread says after `<strong>Retrieval.</strong>` what retrieval was
  tried (tools/held_sources.py, tools/arxiv_source.py, tools/browser_get.cjs, a search) and how it
  ended (the finisher checks). Outside draining, the review marks its three most promising passed
  Outside leads and two most promising passed bridges with `<li data-pick>` (or all passed items
  when fewer pass); only these are queued and the rest are dropped at once (user, 5 October 2026). A
  picked item is a lead to develop, not only to list: every picked, unclosed item waits in the
  notebook's **Lead and bridge queue** (`<section id="lead-queue">`, the last living section; no
  word budget; restoration reads its first five items), FIFO, maintained per
  [tools/lead_queue.py](tools/lead_queue.py). A review appends its picks at the end. A research
  entry develops at most one top-level item, by default the head; the agent may take another queued
  item first when a `<strong>Chosen.</strong>` paragraph says which open statement it bears on and
  why it comes first (user, 9 October 2026: "You can select the order. Make this a general framework
  rule."); no item is skipped by this. At an item's spell boundary rotate it and develop a different
  item, the head or any other chosen one; work refused at the boundary is not re-filed under a
  related item (user, 10 October 2026: "You should not bypass the spell limit. Why not just rotate
  the item and move to next one?" and "Doesn't have to be the head. You can select the item to
  develop, just a different one."). Sub-ideas belong to their item: a parent that keeps one open is
  Continuing, not Closed, and they never become items of their own when it closes (user, 10 October
  2026). Any item the agent develops, chosen ones included, may earn the spell extension described
  below. The entry is tagged `data-lead` or `data-bridge="REVIEW-ANCHOR:N"`, and states
  `<strong>Follow-up.</strong>` Closed, Developed or Continuing. Squeeze an item until it can
  produce nothing more, not until its first usable result (user, 3 October 2026): Continuing
  whenever its translation still bears on an open statement, naming and where possible making the
  concrete next attempt, first tried on its smallest nontrivial instance and written as the next
  entry's lemma when a few lines decide it (16 October 2026: two named attempts in one entry failed
  at their first case; the entry reports that try after `<strong>Smallest case.</strong>`, which the
  finisher requires), and never one the entry's own statements already decide, which that paragraph
  shows after `<strong>Own statements.</strong>` by applying them to the attempt (the finisher
  requires it from 17 October 2026, after three named attempts in a row were decided so); Developed
  only when its results leave it no remaining application to an open statement; Closed only for a
  reason the attempt found (a restatement of the open problem, inapplicability, a falsification, or
  supersession by a stronger result). One cycle, which may be short, is enough to find that an item
  deserves closing; state the reason and its limits and close it, without asking the user whether it
  may be pruned (user, 10 October 2026: "the existing process already supports closing an item
  quickly if it deserves it"). Every Closed follow-up carries `<strong>Stakes.</strong>`: what a yes
  and what a no to the item's question would each give the open statement. The reviewer reads each
  closure, and the entry links its record (the finisher checks both; user, 10 October 2026). It also
  states, after `<strong>Sources read.</strong>`, which statements of each source the closure relies
  on were read, or that it relies on recorded results only; a closure resting on an abstract is
  refused (the finisher checks). After `<strong>Not examined.</strong>` it lists what the item's own
  statement names (objects, sources, forms) that the entry did not examine and why the closure
  stands without each, or says nothing it names is left; an item with a named part unexamined is
  Continuing (the finisher checks the paragraph, the reviewer its content). After `<strong>Owed
  attempt.</strong>` it says which attempt the item's latest follow-up or its reviewer named and
  that it was made, with its outcome, or that none was named; an item whose named attempt is unmade
  is Continuing (the finisher checks the paragraph). Every entry on an item whose last entry named a
  next attempt carries that paragraph too, whatever its outcome: the attempt made, with its result,
  or why another came first (the finisher checks). An attempt reported unmade in two entries in a
  row on an item is made or dropped, with the reason, in the third (the finisher prints a third
  deferral in a row by its words, and cannot tell which attempt each entry defers). Closed and
  Developed remove the item, and a Developed follow-up carries the Not examined and Owed attempt
  paragraphs and the link to the reviewer's record as a Closed one does (the finisher checks).
  Before planning a queued item, run `tools/lead_queue.py history NOTEBOOK ID --status` and read its
  latest development; take the spell count from this computed status, not an older entry's prose.
  Four consecutive research entries are the default spell. At its boundary, extend by two cycles
  when a proof, refutation or reduction from the current spell/extension period materially advances
  a named open statement and a concrete next necessary implication uses the same mechanism. Record
  that evidence and next attempt using [the queue tool's extension format](tools/lead_queue.py).
  Reassess after each two-cycle extension; there is no lifetime cap, but finite checks, promise
  alone or reused old progress do not earn more time. Without fresh qualifying progress, rotate to
  the tail (user, 5 October 2026). Every top-level item, also during backpressure, is developed in
  its own entry; batch triage is retired (user, 9 October 2026: "Revert it back to the state where
  each item was done one at a time"). Sub-ideas of the one item an entry develops may be batched in
  that entry, each in a follow-up list item with its own outcome and evidence (user, 9 October 2026:
  "An entry may develop at most one top level item. Sub ideas attached to a single parent can be
  batched."). Research entries carry no Outside leads or Absurd bridges of their own (user, 9
  October 2026); undone work they name goes under Sub-ideas. An item closed too early is reopened by
  a follow-up list item ending `<strong>Follow-up.</strong> Reopened: <reason>` and goes to the tail
  (`lead_queue.py append`). A queue audit (`data-kind="audit"`, outside the review cadence) lists
  ideas that older reviews named outside the standard sections, each `<li
  data-source="REVIEW-ANCHOR">`; all of them are queued ("when unsure, queue it"). Any entry lists
  the questions, checks and builds it names and leaves undone under `<h4>Sub-ideas</h4>` (`<li
  data-sub="check">` or `"build"`), but only those it intends to carry out: do a small one in the
  entry, drop one that will not be done, and add none to fill the section (user, 9 October 2026).
  Work that comes up outside an entry (a conversation, a review, a tool's defect) joins the queue at
  once with `lead_queue.py add NOTEBOOK.html --check|--build|--idea ID SOURCE TEXT`: a top-level
  item at the tail, which needs no entry and which a commit without an entry may add (user, 7
  October 2026: "You should be able to queue items by just running the tool"). A finished top-level
  build leaves the same way: `lead_queue.py close-built NOTEBOOK.html ID --record REVIEW.txt --path
  PATH --note TEXT` records the reviewer's record, the implementation paths and what was built in
  `research/queue-closures.jsonl`, and a commit without an entry may carry it (user, 16 October
  2026: "Isn't that a gap in the framework? Why can't you close items"). Those of a research entry
  that develops no queue item have no parent: they wait in their entry, `lead_queue.py pending`
  lists them, and the next review promotes any number by judgement with a follow-up list item ending
  `<strong>Follow-up.</strong> Promoted: <reason>` (user, 9 October 2026). `lead_queue.py append`
  and `similar` show queued items with similar wording; when two ask the same thing keep one,
  closing the other with "Closed: merged into ID", which adds its wording to that item. The others
  join the queue nested under the item they belong to (user, 3 October 2026: "I want it to look like
  a nested list of entries"), a sub-idea's development counting toward its parent's spell; a check
  is Developed only with evidence that resolves, a build only with its opened task or its path. The
  user may pick any item out of order (`data-picked="user"`, the words quoted in a
  `<strong>Picked.</strong>` paragraph), and an item waiting on the user's answer stays queued and
  passed over (`Waiting:` and `Unblocked:` follow-ups). The queue section's attributes set, per
  notebook, the entry kinds that count, backpressure and extra kinds;
  [tools/lead_queue.py](tools/lead_queue.py) holds the details. Backpressure: at 30 top-level items
  (user, 9 October 2026; 50 before) the queue drains (`data-draining="true"`), and until 10 remain
  every research entry develops a queued item or one of its sub-ideas: the head by default, or any
  other queued item under the same choice rule as outside draining, a `<strong>Chosen.</strong>`
  paragraph saying which open statement it bears on and why it comes first. Draining restricts
  entries to the queue; it does not restrict them to the head (user, 11 October 2026: "it moves you
  to where you choose, the only restriction being to select a diff item"). Then work returns to the
  route, or to a better route the leads opened. While the queue is draining, reviews produce no
  Outside leads or Absurd bridges: omit both sections and assess existing work (user, 5 October
  2026). Review cadence and the other review requirements still apply. A review of a draining queue
  declares `data-queue-items="N"`, its top-level count (the finisher checks), and `compute.sh start`
  prints the last two recorded counts beside the present one: draining is a rule, and only the
  counts show whether the queue shrinks. A review that decides to leave items declares them in
  `data-left-items="ID ID"`, and until the next review an entry on one of them, or on a sub-idea of
  one, says after `<strong>Returns.</strong>` why it returns (the finisher checks the item, not the
  subject, which the reviewer checks). Reviews report only follow-ups whose status changed. A review
  whose period queued build items that are still queued, and made fewer builds than remain queued
  from it, says in a `<p><strong>Builds.</strong>` paragraph what becomes of each: built now,
  dropped, or the dated reason it waits (the finisher checks that each is named; the queue tool
  stamps an added item with the record's last entry, by which the period is known). The finisher
  checks all of this against HEAD and `compute.sh start` prints the queue's state and head. A
  one-step objection (a structural remark, a record match, one encoding tried) falsifies only that
  formulation. Before a review declares an open statement without mechanism, or moves cycles away
  from it, each "Not run" item and each item closed by such an objection that bears on that
  statement gets a development cycle: read the source in full, and try other encodings, formulations
  and settings where the objection does not apply (user, 26 September 2026: "Did you make an honest
  attempt at developing some of these in order to solve A1?"). In the user's words (25 September
  2026): "absurd bridges can reach for mathematics, computer science, theoretical physics, quantum
  fucking chemistry, I don't give a fuck. That's why they are absurd." Reaching for other areas is
  the agent's job at every cycle, not only when the user names a field. Proposed next step names its
  route item, and the queue item it takes, by identifier or by a link to an entry that developed it:
  the append tool prints that item's queued text and latest follow-up, to write the description
  against, refuses a next step naming none while the queue drains, and refuses one that names a
  developed item by its identifier without quoting eight consecutive words of the item's latest
  follow-up or queued text. While the goal is open that step is always research: never park, pause
  or stop the goal, or wait for a user decision; when recorded routes are closed, propose and test a
  new idea. Once the goal is proved, a Spin loop stops ([PROMPTS.md](PROMPTS.md#spin)). During an
  authorized Spin, continue the next cycle or review in the current turn; possible user redirection
  is no reason to idle or request a check-in. Low-yield cycles, corrections and hard next steps call
  for developing the latest review's Outside leads and Absurd bridges, not stopping the loop while
  the goal is open. Explain progress, obstructions and remaining uncertainty; do not invent
  numerical probabilities for research prospects. A probability requires a stated quantitative
  method and evidence, not an uncalibrated impression.
- Keep entries chronological and append-only, including opinions/assessments even when the user
  objects. Withdraw/correct/retract in a new dated entry linking the old anchor; update living
  status and correction metadata. Never silently rewrite prior mathematics to match later results.
  Link repairs and presentation-only changes that leave the text unchanged, such as non-breaking
  spaces, are allowed. `tools/check-append-only.py` checks HEAD at finalization and must pass
  against `origin/main` before a push, unless the user explicitly overrides the check.
- Historical labels link directly to Markdown statement/proof anchors using
  `php_codex_handoff/manuscript/CLAIM_INDEX.md`. Use public GitHub file URLs in the notebook so
  links work locally and on Pages; verify file/anchor locally and read local excerpts when
  available. Mathematical corrections require new entries.
- [research/claims/index.json](research/claims/index.json) owns claim metadata;
  [research/CLAIM_INDEX.md](research/CLAIM_INDEX.md) and topic views are generated. Follow the
  [registry workflow](research/claims/README.md); regenerate with `tools/claim-index.py render`.
  Preserve labels, exact scope and full-record links.
- **Index maintenance:** each new or substantively revised claim needs current evidence-backed
  mathematical status, topics, formalization scope/disposition, significance and relationship
  review. Use the [cheap significance/attention
  workflow](research/claims/README.md#significance-check-and-attention) at each checkpoint; surface
  new/reopened candidates to the user. Unknowns need a specific pending question and next action; do
  not invent metadata to pass. Record applicable dependencies, refinements, corrections and
  obstructions; refresh affected existing claims. Record a `refines` edge only when one version
  implies the other. `claim-index.py changed --base REV` checks changed scope (HEAD at finalization,
  integration base in CI); untouched backlog remains visible separately. New articles declare
  `data-claims="ID ..."` matching claims sourced there, or `data-claims="none"` with a specific
  `data-claim-note`. Unregistered explicit labels and source/inventory mismatches block
  finalization. Preserve stable IDs and dated records; follow the registry editing contract for
  metadata-only work.
- Read **Gaps identified by formalization** on ordinary restoration too. Its concise living list
  links discrepancies and audit status; full corrections stay in dated records. Begin Lean work only
  under explicit assignment, including an assigned parallel formalizer. Then read
  [formalization/AGENTS.md](formalization/AGENTS.md) and its README, not as routine research/Spin
  reading. Record exact per-claim Lean scope and file links, distinguishing partial
  coverage/stronger hypotheses from complete verification. Absence of Lean is not mathematical
  incompleteness; a verified special case does not verify the full informal claim. Use normal
  research evidence, timing and checkpoint rules for formalization.
- During coordinated parallel formalization the coordinator alone edits **all** living sections,
  including formalization gaps, at integration checkpoints. Workers review them, append full
  records, maintain claim metadata and promptly send proposed overview changes/discrepancies; do not
  wait for all workers to finish.
- Finish every notebook and claim-registry edit before the final snapshot. Run the small controller
  `./tools/finish-turn.py TURN` directly, not in the session it stops: it exports timing, archives
  evidence and fills the unique `<!-- TIMING TURN -->` marker. For continuous research add `--next
  NEXT` to start the next clock immediately; subsequent checkpoint work is preparation. Each entry
  ends with a generated two-column **Measured category / Elapsed** table and bold total instrumented
  interval (`compute.sh report TURN --stop --html-out PATH`), followed by the cycle's generated
  **Model use** table when the finisher runs in the cycle's Claude Code or Codex session. Use actual
  measured categories, count overlap once, and distinguish tool failures/timeouts from failed
  mathematics. Keep its footnote one short sentence plus exceptional limitations; do not repeat the
  methodology or backfill unmeasured time. Commit the entry, fragment, archive and supporting
  results together. After the finisher, only stage, commit and perform any authorized push. If an
  edit is necessary, rerun the finisher's checks, including `tools/notebook_context.py --all` and
  the claim checks, before committing; its earlier checks validate only the earlier snapshot. The
  checked push rejects hard context-budget excesses.

## Framework maintenance and interaction

- Extend committed, tested tools for recurring helpers instead of rebuilding scratch scripts,
  including integration/maintenance jobs and jobs recurring by their nature even on their first use.
  A scratch script whose output is committed to a tracked record becomes a tested framework tool
  before that commit. Register claims with `tools/claim-index.py author build` and a compact spec
  per the registry README. Append drafted entries and new Proposed next steps with
  `tools/notebook-append.py`; build reviewer excerpts with `tools/notebook-excerpt.py`, whose
  `--claims ID ...` writes the registered statement and assessment of named claims. Wrap every
  Markdown file written here with `tools/rewrap_md.py`, at its default width, after every edit:
  never by hand or with an ad hoc script. Replace a passage of prose with `tools/replace_text.py`,
  which keeps its indentation, and make an exact edit with the editing tool, never with a replace
  helper written into a script, which the Bash guard refuses. Where the tool falls short, improve it
  until it does the job (user, 5 October 2026: "The tool exists for you to use it. Always."); a
  limit stated in a tool's documentation that misses a case in use is improved then, not worked
  around.
- Before proposing to replace a tool of ours with another, or to give up something ours does, list
  what each does that the other does not, build the smallest change to ours that closes the gap, and
  measure both. A cost given for that change is a measurement of an attempt, never an estimate, and
  a measurement taken under the other tool's mechanism says nothing about ours. Offer the
  replacement only with that comparison, and offer keeping ours beside it (user, 10 October 2026:
  "Instead of giving me the choice of losing an advantage, you should be giving me the choice of
  keeping it").
- The framework suite is every `tools/tests/test_*.py`, which covers `compute.sh`, the session
  launchers, `tools/` and the site: `test_site.py` runs the tests in `tests/`, including the
  real-browser ones, each within 5 s (user, 28 September 2026). New framework tests go there or into
  `tests/` with a case in `test_site.py`, never beside the code. Before committing an edit to any of
  these, run the tests the change could affect: a standalone new tool needs only its own test file
  (`./compute.sh --threads 14 --timeout 60 python3 tools/tests/run.py test_NAME`, the parallel
  runner on that one module: a file whose tests each start processes takes several times longer
  under `unittest`, which runs them one after another); a change to shared code, fixtures, hooks, CI
  or names other files use needs the whole suite, through the protected launcher: `./compute.sh
  --threads 1 --timeout 60 python3 tools/tests/run.py`, which runs the tests in parallel worker
  processes. The whole suite stays under 10 seconds (user, 26 September 2026: "The suite should run
  in 10s tops"); the runner fails a slower run and lists its slowest tests. That is a defect to find
  and fix, such as repeated work in the code under test, not a wait to accept. The runner prints the
  CPU time the run used itself and what was other work on the machine, and names an overrun under
  load "TOO SLOW (machine busy)"; it still fails. A change that would let a limit quoted here from
  the user pass where it failed is built as an option that is off and filed as a question, never
  made the default by the agent. A timing-limit failure alone does not require another suite run.
  For the same reason `compute.sh start` warns when its turn guidance takes over 1 s, the finisher
  when its checks take over 5 s, and `tools/resume.py` when preparing a bundle takes over 2 s. A
  check that refuses text on its words gets, for each phrase it matches, an accepted test case using
  that phrase in a legitimate sentence, and is run on the record's past entries before its commit,
  so that its false refusals are counted, not only its catches (16 October 2026); that holds for
  each word a widening adds, in the edit that adds it, and an exemption is scoped to the sentence
  that carries its reason and checked to mean what it claims (17 October 2026: one word exempted a
  whole paragraph, and an unchecked commit hash exempted any deferral); a check that refuses an
  action is also tried, before its commit, against the cheapest way around it (an edit that changes
  nothing that matters, another flag, an older input), and the run is reported beside the change (16
  October 2026: two new checks let a comment edit and a two-commit-old message through); likewise a
  threshold or filter a tool applies to records is counted over all the records it will read, its
  losses as well as its catches, before it is committed, not fitted to the case that prompted it (16
  October 2026: a floor fitted to one brief hid real statements); and a rewrite of such a check is
  replayed beside its earlier form's catches, each one it no longer makes judged against its source
  (17 October 2026: a tightened wiring pattern dropped two real wirings while its replay was read
  only for the false hits it lost). Tests run on small fixtures, where work repeated per item costs
  nothing: a change to a framework tool that reads the repository's records, or whose work grows
  with the directory it is given (a copy, a walk, a scan), also gets one timed run against the real
  repository, and against the largest one it will be used in; such a tool prints what its work grew
  with (files, megabytes), so a jump is seen at its first use. That run reaches the path the change
  adds, and prints which path it took: a run that returns early on real data has not measured the
  change (16 October 2026: a check's two timed runs printed that it found nothing to check). For a
  check, that run also lists what it found and each finding is read against its source: a fast run
  is not a correct one (17 October 2026: a refusal check, timed but tested only on fixtures, counted
  two printed files that quote its message as two refused calls). What git tracks is not all source:
  recorded data and archived output are tracked too, so a tool that needs the source is told which
  paths. The run uses a real diff where the tool compares revisions (an unchanged base skips whole
  code paths), before its commit, and a profile if it is slower than the work it does. Measure a
  change's effect before claiming it: a framework commit message, a tool's docstring and help, and a
  queue-closure note state only what was measured or checked, each figure beside the saved output it
  came from, written after that output exists, with every measured value of the comparison it draws,
  not only those that support it; and a mechanism (a cache, an option, a helper) needs a measured
  use. Other tests run only on their own trigger: `formalization/tests/` needs the Lean toolchain
  and runs when formalization tooling changes; `resource-controls/test_watchdog.py` and
  `test_11gb.py` validate the memory controls and run only when those controls change. Scripts and
  tests under `research/` are computations or provenance of finished one-off jobs, tied to the data
  of their date, and are not rerun.
- Durable process lessons belong in the committed framework, not machine-local memory: nothing is
  written to `~/.claude/projects/*/memory/`, and `tools/hooks/memory-gate.py` refuses such writes
  (user, 10 October 2026: "We need a mechanical check... No memories...."). State general rules, not
  narratives of the mathematics that prompted them. When the user or a reviewer shows a mistake in
  how the work was done, the same reply names its prevention and commits it, a mechanical check
  where one can exist, without being asked (user, 10 October 2026). A longer queue item is not a
  prevention: the text of a queued build is extended at most once, and what a later mistake adds is
  built in that turn or queued as an item of its own (the finisher refuses a second dated addition
  to a queued build's text). So that the user is not the only check on conduct, every reviewer also
  audits how the work was done (overstated titles, unasked questions, unsupported decisions; see the
  `medium-reviewer` definition, and ask for it in every brief), and each reviewed entry reports the
  findings after `<strong>Process audit.</strong>` in its Verification gate (the finisher checks;
  user, 10 October 2026). An entry's title and status line are written, or rewritten, after its
  review, from the reviewed body, and the audit says what the reviewer found of the title against
  the body (the finisher refuses an audit that does not speak of the title). A second reviewer reads
  what the subagent never sees, what the agent wrote while working: at the end of the finisher, and
  at most once in 40 minutes, `tools/stand_in_review.py` gives a reviewer with no memory of the
  session this file and the agent's text since its last run, and prints up to five things the user
  would object to, each with a quote (user, 11 October 2026: "Offer him the job"). Check each
  against the record before acting on it, since about one in ten misreads the text, and say in the
  next entry, after `<strong>Review.</strong>`, what became of each: fixed, queued, or wrong and why
  (the finisher checks). An entry's **Process assessment.** paragraph ends with
  `<strong>Prevention.</strong>`: the committed check or rule for each mistake it reports, or why
  none applies (the finisher checks). Repeated question marks signal increasing frustration with the
  process: implement and commit a real fix, preferably a mechanical check, rather than only
  apologizing.
- A fix of the agent's own mistake is reported with its prevention, unasked, in the same reply, in a
  paragraph that starts "Prevention": the class of the mistake in general terms, why the existing
  rules and checks let it through, and the framework change made in that turn that stops the class
  (a check, a hook, a test, a tool that reports or refuses; a written rule only where nothing
  mechanical can), or, only where it can't be built in that turn, the build item queued for it with
  that reason (user, 13 October 2026; `lead_queue.py add --build` refuses a text without "Not built
  in the turn:" and the reason). Fixing the one instance is not a prevention. The Prevention names
  the stage the mistake entered at (drafting, a reviewer's suggestion adopted, a reply, a commit)
  and changes the tool of that stage (16 October 2026: answers addressed the sentence, not the
  stage, and the same stage leaked again). A fix is finished when the case that exposed it passes at
  the earliest point a check can run, not when a rule, a statement of the limit or a later check
  covers it. The order of work follows: the check for a right objection is built and committed
  before the reply that answers it is written, and the reply names that commit (16 October 2026:
  answers written first were prose, and the checks came a turn later). The Stop hook and the commit
  check block a turn that admits a mistake without that paragraph (user, 10 October 2026, on having
  to ask after every fix how the mistake is prevented). Beside it goes a paragraph that starts
  "Meta", the meta-question: what should change so that in future neither the mistake nor its fix
  would have been needed at all. It is about the agent's own behaviour, as a class wider than this
  mistake and its kind: the way of working that produced it (a habit of deciding, of weighing cost
  against the user's stated priority, of reading or of stopping), where else that habit shows, and
  the change in how the agent works that ends it, in its durable home, named by its path. A Meta
  that names the Prevention's mechanism again, or only this mistake, answers the Prevention twice
  (user, 14 October 2026: "The answer should also be meta, with broader, more general scope than
  prevention"). It is asked for each admitted mistake, for each reviewer agent's report (answered
  after it with both paragraphs, Prevention saying where it found no mistake of the agent's) and for
  each stand-in review's right objections, in the entry's `<strong>Meta.</strong>` paragraph; the
  Stop hook, the commit check and the finisher enforce it (user, 13 October 2026: "I won't be there
  forever ... AIs will live on and they must learn to become better on their own"; ported from
  another branch, 16 October 2026). A reviewer's wrong objection is a mistake too, of the reviewer's
  setup: its answer changes what let the reviewer make it (the brief,
  `.claude/agents/medium-reviewer.md`, or the stand-in prompt in `tools/stand_in_review.py`), so
  that the same misreading costs no second round (user, 17 October 2026: "Perhaps we need
  prevention+meta for reviewer's mistakes to reduce friction, wasted tokens and time").
- When the harness or its classifier refuses a tool call, its goal is not reached by another command
  or tool: say in the reply which call was refused and why, file the decision in `user_requests`
  with the default being followed (leave the file as it is), and continue other work (17 October
  2026: a refused checkout of CLAUDE.md was redone by a checkout from a commit).
- After a session restart, notifications about instructions, stopped tasks or changed files are not
  new work requests. Run no tools or restart tasks in response to those notifications alone; say at
  most one sentence and wait for the user's message.

## Portable sessions, Git and publication

- Work from the repository root without assuming a machine/user/absolute path. `start-codex.sh`
  starts/reuses the remote-control daemon. `start-session.sh` and `start-claude.sh` resume exact
  machine-local IDs or restore context for a fresh session. Launchers bind their own IDs outside the
  agent; workers and unrelated sessions must never replace a binding. The legacy
  `remember-codex-session.py` only validates an existing binding. Never commit IDs. Codex
  startup/repair and hook trust are described in [tools/CODEX.md](tools/CODEX.md). Clones restore
  files, not chat history. Private agent memory is not written at all (see Framework maintenance),
  and never holds mathematics or research progress.
- Background sessions use one persistent Git worktree, never the shared checkout. Create it from the
  intended local base with `git worktree add --track -b NAME PATH BASE`; set a missing local
  upstream with `git branch --set-upstream-to=BASE`. The branch name is only a convention. Codex's
  launcher manages `.codex/worktrees/`; Claude uses `.claude/worktrees/`. After every worktree
  commit, run `tools/ff-base.sh`, with or without a push grant. It rebases onto a moved local
  upstream and fast-forwards that upstream, including local main when main is the base. It never
  pushes; dirty bases/conflicts require resolution. The post-commit hook reminds about lag or a
  missing upstream. This local synchronization does not authorize publication. An override of a rule
  for one run (such as a suspension of this synchronization) is recorded in `run_state`, as grants
  are (below).
- Every research turn ends in a local Git commit, including failures/no results. Include living
  sections, full record, sources/provenance, code, reproducibility data and complete important
  outputs per the computation policy. Promote essential scratch/runtime results into
  `research/results/` or `research/provenance/`; research must not exist only in ignored files/chat.
  Do not include unrelated user edits; review relevant changes and report commit blockers honestly.
  Logs, credentials, session IDs, binaries, environments and scratch renders stay untracked. Every
  commit-message line must be at most 100 characters; wrap prose and separate paragraphs with blank
  lines.
- A session's scratch files are its own to delete by the end of the cycle that made them; promote
  anything worth keeping to `research/results/` or `research/provenance/` first (user, 3 October
  2026, with the disk near its 10 GB floor). The finisher fails while the session's scratchpad holds
  more than 500 MB; it never deletes for you. Codex gets its owned directory with `python3
  tools/codex_state.py scratch`; use it for all temporary work. Do not place symlinks inside managed
  scratch.
- Publish only under explicit user authorization, including a still-active scoped/ time-limited
  grant. Research/edit/commit requests alone do not authorize it. Restore the actual grant after
  compaction, honor expiry/later overrides and do not ask again within authorized scope. A grant,
  and an override of a rule for one run, is in force only while the Git-ignored `run_state` file of
  the main checkout lists it: record it there when the user gives it, with the user's words and
  date, and remove it when it ends. In a worktree `run_state` is a link to that file, which
  `compute.sh start` creates, and `tools/resume.py` puts the file into every resume bundle, so a
  grant survives a compaction; a clone without the file has no grant. This file holds no run state.
- Respect the user's branch; do not switch/merge into main just to publish. Pin integration targets
  to immutable commits after fetching/receiving workers, rebase and validate against those IDs.
  Immediately before fast-forwarding check the destination HEAD and worktree: if advanced,
  refresh/rebase or leave unmerged; validation against an old target is not validation of a new one.
- A branch whose remote moved under it (another clone pushed) is rebased onto the remote in a
  temporary worktree, with a backup branch, under the `rebase-math-research-branches` skill (a skill
  of the user's own agent setup, not kept in this repository; without it, follow this rule and the
  registry workflow's remap step). Run `tools/notebook_rebase.py --continue` from that worktree at
  each stop: it merges the notebook's conflicts element by element (entries, queue items, a living
  section's paragraphs), continues, and stops on what needs a person. A conflict in wrapped Markdown
  is merged word by word with `tools/merge_md_words.py FILE`, or by itself where the clone has
  turned on the merge driver that tool describes. A conflict shape that recurs in another file gets
  a guarded resolver there too, with tests, never a scratch loop. When a commit that registers
  claims is replayed onto a base that registered others, the registry and its views conflict: run
  `tools/claim_rebase.py --spec SPEC` (the commit's compact spec), which keeps the base's registry,
  rebuilds the claims on it, renders, stages and rechecks, and refuses any other conflict.
- Preserve private `pre-publish`; never publish it or use `--all`/`--mirror`. Before authorized
  publication run `tools/verify-checkout.py --public-history BRANCH` (it includes the claim-index CI
  job, `tools/check-claims.py`, against `origin/BRANCH`) and the append-only check, unless
  explicitly overridden by the user; push with `tools/checked-push.sh` (from a worktree branch
  `tools/checked-push.sh main`, which pushes HEAD to main only as a fast-forward), which runs both
  and pushes only if both pass. Pages targets main only; local commits are checkpoints. The Pages
  workflow builds HTML/site-tool changes with `tools/build_pages.py --out _site --site-url URL`, URL
  being the site's HTTPS base URL that every page's citations use: upload only that minimal
  artifact, never the checkout/private sources. Preserve live mode and project-relative published
  revision URLs.
- Follow LICENSE: original software MIT, original research CC BY 4.0. Preserve attribution, cite
  upstream mathematics and distinguish working from established results. Third-party papers are not
  ours to relicense: follow THIRD_PARTY_NOTICES.md and research/references/redistribution.json. Keep
  uncleared PDFs/full text and source-containing diagnostics out of public commits/reachable
  history; preserve needed personal copies locally, never publish private/backups. A source that
  cannot be retrieved after an honest attempt is a user request (below), with citation, attempted
  links and purpose. Before a retrieval is called failed or a request is filed, run
  `tools/held_sources.py WORDS` (author, title word): it lists the files already held in the main
  checkout's private folder and the request paragraphs that name the source. An honest attempt goes
  beyond the source's own copies: where what is needed is a definition or a statement, look for it
  also in its authors' other writings (talks, theses, surveys) and in papers that use it, and say in
  the entry which of these the statement was read in. A file whose text does not extract is read
  from its pages rendered as images before it is called unreadable. A source that refuses a scripted
  client (a 403 or a bot wall) is tried in a browser, `node tools/browser_get.cjs URL --out FILE
  [--click TEXT]`, before a request is filed; it carries the session of the user's own Firefox and
  paces visits like a person (spaced per site, at most ten an hour; a refused site is not retried at
  once by other means, since rapid repeats get a session flagged). Where the obstacle is a login the
  user holds, the request asks the user to sign in in Firefox and run `tools/firefox_cookies.py
  HOST`; `tools/firefox_get.py HOST PATH` or `tools/browser_get.cjs` then reads through that
  session. A retrieval is recorded, in a request or an entry, only after the retrieved file has been
  opened and identified as the source. A number or range transcribed from a scanned page is checked
  against a second place where the source uses it, or marked uncertain. A paper on arXiv is read
  from its source: `tools/arxiv_source.py ID --out DIR --expect WORDS` unpacks into external scratch
  or the actor's managed, Git-ignored scratch, rejects tracked destinations and links, prints the
  title, and fails when it holds none of the words given of the title meant. A web fetch that
  returns a model's report of a page is not a reading of its statements; an entry that relies on one
  says so in its status line.
- Every request to the user goes into the Git-ignored `user_requests` file of the main checkout, the
  one the user reads; in a worktree `user_requests` is a link to it, which `compute.sh start`
  creates and insists on: a missing source, an installation, a permission, a choice between research
  directions, or any other question. Give what is needed, why, what was tried, and the default being
  followed meanwhile. Never stop, pause or idle to wait for the answer: follow the recommended
  default and continue. Mention a new request in one sentence of the turn's report, and mark items
  fulfilled when answered.
