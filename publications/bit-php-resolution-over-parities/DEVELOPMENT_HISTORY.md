# Development history of the bit-PHP preprint

This is the author's first-person account that appeared as Section 8.3 ("Contributions and
development history") of version 1 of the preprint (15 September 2026). Revision 1 condensed that
section to one paragraph and moved the account here, unchanged except for conversion from LaTeX.
The version-1 LaTeX source is fixed at commit
[`b47e9b1`](https://github.com/kbr-/math-research/blob/b47e9b1ef1f5b273822001983e83d35d7acbe117/publications/bit-php-resolution-over-parities/sections/07-main-proof-framework.tex).
It describes version 1 only; the AI assistance in revision 1 is disclosed in the paper itself.

The principal models used were Claude Sonnet 5, Claude Fable 5.1,
Claude Opus 5, and GPT-6 Astra. GPT-6 Astra was the main contributor
to the mathematical development and drafting of this result.
The following account describes my experience; assessments
of model performance are my impressions from this investigation.

I began in a Claude conversation on the
$20 Pro plan, initially attempting to attack P ≠ NP.
I used Sonnet 5; Fable models were unavailable to me on that plan.
As the conversation progressed, the objective shifted to the
narrower, though still ambitious, problem of superpolynomial lower
bounds for ordinary PHP in fixed-depth AC0[p]-Frege.
Repeatedly reaching the five-hour usage limit, and dissatisfied with
Sonnet 5's capabilities for this task, I upgraded to the Max 20x plan.

I then attempted research with Fable 5.1. Hypotheses and proposed
lemma proofs accumulated, but no clear route to the goal emerged.
During the conversation, Claude began classifying my requests as
unsafe cybersecurity research; the interface
repeatedly switched me to Opus 4.8. I also attempted to continue
with Opus 5, but remained dissatisfied with its performance.
Increasingly frustrated, I purchased OpenAI's ChatGPT Pro x20 plan
to try GPT-6 Astra.

In the browser-based ChatGPT interface, GPT-6 Astra appeared much more
confident and optimistic than Opus 5 and produced dozens of proposed
lemmas and theorems. Two obstacles became apparent. First, it was
unclear whether this growing body of mathematics advanced the main
goal or merely supplied additional results without a sufficient
application. Second, context compaction caused important information,
including previously derived results, to be lost from the model's
working context. I therefore sought an explicit context
management strategy outside the chat interface. I asked ChatGPT to
prepare a handoff package for Codex, an AI coding-agent environment,
collecting the results and arguments developed in the conversation
so that work could continue from files.

I created a Git repository and specified requirements for
the research framework described above. Using Codex CLI with
GPT-6 Astra at Max thinking effort, I refined the framework through
several rounds of interaction. Its first version was preserved in
the initial commit of the public *math-research* repository,
[`2f9568f`](https://github.com/kbr-/math-research/commit/2f9568f).

Initially, I manually requested individual research turns,
each followed by a request to identify friction in the framework and
implement improvements. After several such turns, the need to automate
this cycle became clear, particularly when I needed to step away
from the laptop. The resulting *Spin* prompt, introduced in commit
[`5570c3e`](https://github.com/kbr-/math-research/commit/5570c3e), instructs the agent to repeat research, record its
results, assess the process, and improve the framework when warranted.
I assigned this continuing task through Codex's */goal*
feature. At the time this manuscript version was prepared, the agent
was continuing these cycles autonomously under that assignment.

My main contribution is the design, direction, and iterative
refinement of the framework, rather than the mathematical derivations
themselves. Explicit resume protocols restore context, durable records
preserve results and failed attempts, and computation tools support
mathematical reasoning with software. I continue to provide
strategic questions and steering prompts when I notice weaknesses
in the process. For example, I questioned whether successive lemmas
were approaching the main goal or merely orbiting it. This concern is
recorded in the notebook entry
["Classify column-literal selectors and realize arbitrary joint profiles
within literal OR syntax."](https://kbr.is-a.dev/math-research/#entry-2026-09-12-column-literal-selector-profiles)
The resulting reassessment and route audit appear in commits
[`432269f`](https://github.com/kbr-/math-research/commit/432269f)
and [`603a99d`](https://github.com/kbr-/math-research/commit/603a99d).
Commit [`e25983e`](https://github.com/kbr-/math-research/commit/e25983e) revised the workflow to require each research cycle
to address a named missing implication, explain how its task could
test or discharge that obligation, and state a concrete stopping point.
The Git history and notebook research record preserve these framework
changes and the strategic questions that motivated them.

After the first draft of this whitepaper, I decided that formal
verification was required, as I did not have enough expertise to check the
mathematics myself. I began by extending the framework with a Lean project,
introduced in commit
[`afa42b4`](https://github.com/kbr-/math-research/commit/afa42b493549efec332378d1eb40ef55eb335bac). Working with GPT-6 Astra in Codex, I first requested
three small formalizations individually, asking after each what the experience
suggested improving in the framework. This repeated the earlier pattern of
research followed by process refinement. The telescoping formalization exposed
a distinction between an upper degree bound and an exact degree that the
original statement had overlooked. The resulting guidance required checking
the entire indexed claim and its dependencies, recording discrepancies,
and explaining any alternative proof adopted during formalization. Separate
claim files and links from the claim index made the verified results reusable;
formalization remained an explicitly assigned activity alongside the continuing
research.

I then turned to the complete proof of this whitepaper's theorem.
I asked the agent to map its dependencies and tackle the external chessboard
homology input first, proving the required statement rather than leaving it
as an assumption. The dependency map also identified independent branches,
which Codex subagents developed in separate Git worktrees while a coordinating
agent integrated their results. This process became the
*Spin-formalize-parallel* prompt. After completing the topological input,
the same approach covered the algebraic dependencies, the translation of the
actual proof DAG, and the final asymptotic argument. Some statements became
more general, and some proofs changed; the notebook recorded these arguments
as the formalization proceeded. The final theorem and its complete dependency
chain were verified in commit
[`54f0937`](https://github.com/kbr-/math-research/commit/54f09378e97465522b7f1caf115f90ad1faa7a57). I then requested that this manuscript be revised
to present those statements and proofs, with permanent links to their Lean
sources.

The statements on this publication route are formally verified; this revised
manuscript has not yet been externally peer reviewed.
The classical topological input is attributed to Björner, Lovász, Vrećica, and Živaljević (1994);
the product-extension methodology is attributed to Buss, Impagliazzo, Krajíček, Pudlák, Razborov, and Sgall (1996).
Original manuscript material is distributed under the
[Creative Commons Attribution 4.0 International license (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

---

## What happened, according to Codex after mining the conversation transcripts

#### 1. SAT algorithm → P = NP

On 3 September 2026, the user began with:

> Come up with a deterministic polynomial algorithm for the SAT problem.

When Claude declined to claim one, the user explicitly doubled down:

> We don't know if P is NP or not. Let's try to prove that P = NP.

The user then proposed the first substantive direction: a topological view inspired by
Alpern–Schneider, followed by Herlihy–Shavit and a search for a SAT analogue of the asynchronous
computability theorem.

That path gradually transformed into proof complexity:

1. A proposed topological decision-tree measure failed because its complexity was trivially
   bounded by the number of variables.
2. The user asked for a better formulation.
3. The conversation began treating proof systems as closure rules on partial assignments.
4. That led to resolution, Polynomial Calculus, feasible interpolation, bounded-depth Frege
   systems, and the Ideal Proof System.

The user therefore did not initially decide to attack P ≠ NP. The attempted algorithmic and
topological programme drifted naturally into studying why SAT proofs must be large.

#### 2. P = NP → P ≠ NP

Claude eventually pointed out that everything developed so far—width, degree, switching lemmas,
interpolation, and algebraic proof lower bounds—was machinery for proving hardness. It therefore
pointed in the opposite direction from the original goal.

The user's explicit decision was:

> If we prove P != NP, that's okay too, although sad. Well, that's life.

The user then asked Claude to choose among three surviving research directions.

The switch was therefore not based on a new argument that P ≠ NP was easier. The user accepted
that the useful machinery uncovered during the failed P = NP attempt was intrinsically
lower-bound machinery.

#### 3. Why AC⁰[p]-Frege?

Claude briefly recommended:

> My pick is the finite-field IPS route to AC⁰[p]-Frege.

Its stated reason was unusually concrete. Unlike the other candidate directions, this route had
an explicit simulation or translation claim: a suitable lower bound over a constant-size finite
field, for a sufficiently strong algebraic proof system, would imply an AC⁰[p]-Frege lower bound.
At that point Claude had read only abstracts, and explicitly described the payoff condition as
something still needing verification.

The alternatives were:

- roABP and noncommutative IPS, potentially reaching full Frege but apparently requiring a
  substantially harder breakthrough;
- constant-depth IPS lower bounds on non-CNF instances, where results appeared more attainable
  but had a lower ceiling.

This was not Claude's stable methodological recommendation. After reading further, it concluded
that the functional lower-bound method under discussion was blocked for Boolean instances and
shifted its recommendation to meta-complexity and diagonalization. The finite-field connection
nevertheless kept AC⁰[p]-Frege visible as an intermediate target while the proposed method
changed.

#### 4. Where Cook's programme entered

There were two stages.

Claude mentioned Cook–Reckhow and the hierarchy of proof systems early while explaining why
Frege lower bounds matter. But the user did not explicitly ask about Cook's programme until
11 September, after AC⁰[p]-Frege had already become the target and after the ChatGPT handoff had
been created.

The user's question was:

> What is the ladder of problems towards P NP? AC0 frege, AC0 p frege, frege, what else? What is
> Cook's programme? Short statement of each problem on the list

Cook's programme therefore did not cause the pivot to AC⁰[p]-Frege. It retrospectively explained
why proving lower bounds for progressively stronger proof systems was connected to the original
P versus NP question.

The resulting conceptual ladder was roughly:

> Resolution and Polynomial Calculus → AC⁰-Frege → AC⁰[p]-Frege → TC⁰-Frege → Frege → Extended
> Frege → stronger proof systems → the Cook–Reckhow question.

The important qualification was that no finite climb up this ladder proves NP ≠ coNP. There is
no known strongest propositional proof system. The Cook programme is therefore a research
philosophy and source of intermediate lower bounds, not a path with a known final rung.

#### 5. The ChatGPT phase: from imported target to handoff

The ChatGPT research phase began on 9 September 2026 at 23:57 Warsaw time and reached the
completed Codex handoff on 10 September at 20:13.

The user opened the phase by uploading a PDF produced during the Claude work and asking ChatGPT
to read it fully and summarize the research. ChatGPT identified the goal already present in that
report as:

> Superpolynomial lower bounds for ordinary pigeonhole principle in fixed-depth AC⁰[p]-Frege,
> for each fixed prime p.

The report already framed the route through the BIKPRS simulation. In simplified form:

> A short AC⁰[p]-Frege proof would produce a bounded-degree extended Nullstellensatz or
> Polynomial Calculus object.

The user immediately asked whether proving the report's proposed Lemma B would yield the desired
lower bound, then asked ChatGPT to decompose it into separate lemmas. After that orientation, the
user instructed:

> Stop reading the pdf now. We will now work on the problem ourselves. Attempt proof of item (a).

The first attempted imported statement did not survive. ChatGPT found that the claimed
Koszul-vanishing range below degree n was false and replaced it with a corrected range sufficient
for polylogarithmic degrees. It then constructed a generic annihilating functional tolerating t
restrictions when t + 2d - 1 ≤ n, while stating explicitly that this was not yet a functional for
the full BIKPRS-augmented system.

The rest of the phase was tightly user-steered rather than autonomous. The user repeatedly
requested the remaining gaps ordered by risk and then issued prompts such as “Work on the highest
risk item now,” “Find a lifting,” “Reduce the cost,” “Pack them,” “Attack the remaining obstacle,”
and “Do the batch elimination.” The user also required optimized computation and increasingly
detailed timing measurements.

Across these turns, ChatGPT developed nonlinear and joint-moment liftings, additive Polynomial
Calculus elimination, same-level batching, nested-span and nested-core arguments, and an exact
optimization of the affine core-and-residual decomposition. The endpoint was also negative:
ChatGPT exhibited an admissible one-level family whose best certified degree exceeded the
available PHP degree budget. This showed that optimizing that static affine decomposition could
not uniformly finish the argument. It did not prove that every possible elimination method
fails.

At the user's request, ChatGPT consolidated the work into a 47-page compendium containing 68
working lemmas, theorems, and corollaries with proofs. The user then asked to continue on a laptop
in Codex, specifying the future instruction “read HANDOFF.md and import all references.” ChatGPT
produced a self-contained directory centered on HANDOFF.md, with the manuscript, TeX sources,
computational supplements, claims and reference metadata, and a precise restart point.

This was the state imported into Codex. The handoff explicitly warned that the final lower bound
had not been proved and identified refutation-sensitive extension elimination, or an equivalent
joint-design construction, as the main missing theorem.

#### 6. From the handoff to autonomous Codex research

Before importing the mathematical handoff, the user spent the beginning of the Codex session
preparing the environment for long mathematical work. The user checked sign-in and plan status,
tested LaTeX-heavy rendering through a local notebook server, enlarged the context window,
established CPU and memory controls for computations, created persistent computation rules,
configured a resumable launcher, and tested multiline prompt editing.

After this setup, the user signalled the transition to research:

> Time for our research. Excited?
>
> The current directory contains a subdirectory: php_codex_handoff. Which contains a file
> HANDOFF.md with instructions. This was created by ChatGPT where I did my research; it is a
> handoff package created by it to continue the research here, inside Codex.

Codex then imported the ChatGPT handoff. Only afterward did the user and Codex construct the
durable research framework around the imported mathematics:

- a Git repository preserving the handoff, mathematics, code, computations, and provenance;
- an append-only notebook research record;
- concise living sections describing the current status, remaining route, and next step;
- explicit context-restoration procedures for surviving compaction and session changes;
- resource-controlled computation and timing tools;
- a rule requiring every research cycle, including failures, to be recorded and checkpointed.

The first research cycles were initiated manually. After each one, the user asked Codex to assess
friction in both the mathematics and the framework itself. This iterative process led to the
`Spin` workflow: a saved prompt instructing Codex to perform bounded research cycles, test
claims, update the notebook, preserve evidence, and continue autonomously. A persistent Codex
Goal was then used to keep `Spin` running without a new user prompt for every cycle.

This distinction matters. The later Res(⊕) direction was not selected by the user in advance. It
arose inside the autonomous research loop.

#### 7. How Codex arrived at Res(⊕)

During the autonomous run, Codex developed a one-level affine-bit algebraic lower-bound
endpoint. It then attempted to connect the full AC⁰[p]-Frege source to that endpoint.

The attempted transfer failed at a concrete point. Substituting Boolean labels into the source
could turn a sparse affine disjunction into a dense nonlinear object. Packing the selectors
removed one problem but changed the old input class, so the previously proved affine-bit theorem
no longer applied directly.

At the end of that failed transfer audit, Codex wrote:

> This makes a direct audit of an affine-clause proof system on the bit encoding a better next
> test than another balancing lookup.

Its self-selected next question was whether affine-clause resolution and semantic weakening
could be simulated in low-degree Polynomial Calculus using only the already controlled one-level
affine-bit extension family.

That affine-clause proof system was Res(⊕).

In the next autonomous cycle, Codex:

1. represented each affine clause by an extension block;
2. simulated complementary-parity resolution in Polynomial Calculus;
3. simulated semantic weakening;
4. handled an alternative two-premise semantic inference convention;
5. supplied the compact bit-pigeonhole initial clauses at the required degree;
6. composed this simulation with the previously established one-level affine-bit exclusion
   theorem.

This yielded a working superpolynomial lower bound for unrestricted DAG-like Res(⊕) refutations
of bit PHP. Unlike the previously known bit-PHP results found during the subsequent literature
audit, the statement had no regularity or proof-DAG-depth restriction.

Codex therefore did not consciously abandon AC⁰[p]-Frege in favour of Res(⊕). It chose Res(⊕) as
the nearest clean proof-system test after a transfer to the main goal failed. The test
unexpectedly produced a potentially publishable result. It remained a side branch of the
AC⁰[p]-Frege project rather than a replacement for its main goal.

#### 8. The “is this publishable?” moment

On the morning of 14 September, the user asked for an overnight progress assessment. Codex
replied:

> The strongest overnight result is a working superpolynomial size lower bound for bit PHP in
> DAG-like Res(⊕), with no proof-height restriction. A second internal audit found no gap. This is
> our strongest concrete result so far, but it still needs independent review.

Then came the publication question from the user:

> If our lower bound for bit PHP is actually new, perhaps it deserves publication?

Codex answered that, if the unrestricted-DAG statement was correct and new, it would be a serious
publication candidate. The user instructed Codex to conduct a focused literature and correctness
audit and, if the result survived, to formulate an end-to-end theorem and proof before preparing
a whitepaper.

The audit distinguished the result from known regular and bounded-depth Res(⊕) lower bounds,
recorded the system's introduction around 2014, and treated the unrestricted
superpolynomial-size problem as having remained open for roughly twelve years.

#### 9. The elapsed time

The initial SAT prompt was sent on 3 September 2026 at 23:11 Warsaw time. The publication
question was sent on 14 September at 12:00 Warsaw time.

The elapsed wall-clock time was approximately:

> 10 days, 12 hours, and 49 minutes.

In other words, about ten and a half days passed between the joking request for a polynomial-time
SAT algorithm and the moment the user asked whether an apparent solution to a twelve-year
proof-complexity problem deserved publication.

#### 10. How the side result emerged

The result did not emerge from a direct attack on the open Res(⊕) problem.

The path was:

> SAT algorithm joke → attempted P = NP programme → topology → proof complexity → acceptance of
> the P ≠ NP direction → finite-field IPS → AC⁰[p]-Frege → PHP extension-elimination research →
> autonomous research framework → failed label-substitution transfer → direct affine-clause test
> → Res(⊕) lower bound → publication audit.

The ten-and-a-half-day interval was not an isolated proof effort. The process used existing
proof-complexity results, pretrained models, several AI systems, local computations, and a
framework designed to preserve claims, failed attempts, corrections, and dependencies across
long sessions.

The roles were different. The user supplied the initial prompts, accepted or rejected strategic
directions, imposed recording and verification requirements, and designed the persistent
workflow with Codex. The models generated and tested mathematical routes, searched for
connections, and drafted arguments. The notebook and supporting tools retained the resulting
chain of evidence across model changes and context compactions.

The Res(⊕) problem was not selected as an original target. It appeared when Codex tested an
adjacent affine-clause proof system after a transfer toward the AC⁰[p]-Frege goal failed. That
test produced the theorem later audited and prepared for publication.

---

## Time spent, according to Claude after analyzing the log timestamps

This report measures how much time the user and the AI models spent between the first prompt and
the Res(⊕) lower bound for bit PHP. It is based on message and event timestamps in three logs: the
exported Claude conversation, the exported ChatGPT conversation, and the transcript of the Codex
session named "Math research", in which the result was found. All times are Warsaw time (UTC+2).

#### Summary

- The weekly usage limit was never hit before the result. The Res(⊕) bound was committed on
  14 September 2026 at 03:55; the first weekly limit was hit on 16 September at 02:16.
- Codex ran essentially without interruption for about 73 hours from the start of the autonomous
  run to the result. In that stretch it did work close to 24 hours a day.
- From the first SAT prompt (3 September, 23:11) to the result, 10 days 4 hours 44 minutes of
  calendar time passed. In roughly 96 hours of that, a model was actually working: 16.4 hours in
  Claude, 6.5 hours in ChatGPT and 73 hours in Codex.
- The 10 days 12 hours 49 minutes given under "The elapsed time" above run to a later moment: the
  user's question, at 12:00 on 14 September, whether the result deserved publication.

#### Claude conversation (3–9 September)

The user spent about 42 hours in sessions over six days. A session here is a run of messages with
no gap longer than 30 minutes. Within those sessions Claude was generating for 16.4 hours, measured
from the start and stop timestamps of its response blocks. The rest is the user reading and typing.

| Day | Sessions | Session time | Claude generating |
|---|---|---|---|
| Thu 3 → Fri 4 Sep (night) | 23:11–05:02 | 5.9 h | 5.1 h (3–4 Sep together) |
| Fri 4 Sep | 09:17–10:54, 14:16–16:33, 19:18–21:21 | 6.0 h | (included above) |
| Sat 5 → Sun 6 Sep | 17:33–21:34, 22:31–03:08 | 8.6 h | 2.2 h |
| Sun 6 → Mon 7 Sep | 10:55–19:00, 20:03–20:18, 23:08–01:58 | 11.2 h | 5.3 h |
| Mon 7 → Tue 8 Sep | 13:49–19:36, short ones, 00:05–02:32 | 9.0 h | 2.8 h |
| Tue 8 → Wed 9 Sep | 10:35, 21:55, 23:50–00:35 | 1.4 h | 0.7 h |

- The conversation has 2,636 messages, about half of them from the user. Many of the user's
  messages are one-word prompts such as "Go.", "Yes." and "Please continue."
- After 9 September the user returned to this conversation only for side questions: about 3 hours
  in total, mostly on 12 September, plus the question about Cook's programme on 11 September.

#### ChatGPT conversation (9–10 September)

The ChatGPT phase took one night and one day: 8.9 hours of sessions, of which the model reported
6.5 hours of work in its "Worked for …" recaps.

- Wed 9 Sep 23:57 → Thu 10 Sep 02:25 (2.5 hours).
- Thu 10 Sep: 09:03–09:16, 10:38–10:59, 13:42–14:19, then 14:59–20:13 continuously (5.2 hours).
- The user sent 31 prompts. Individual answers took up to 32 minutes, and typically 15–25 minutes
  in the afternoon.
- The handoff package for Codex was finished at 20:13. The user had already opened the Codex
  session at 19:19, so the two phases overlap by about an hour.

#### Codex: building the framework before the autonomous run

Building the framework took 6 hours 5 minutes, from 10 September 19:19 to 11 September 01:24, with
99 prompts from the user.

| Step | When | Wall time | Agent working |
|---|---|---|---|
| Environment setup (context window, CPU and memory limits, launcher) | 19:19–20:44 | 1.4 h | 0.5 h |
| Handoff import and framework (notebook, repository, resume guide, timing) | 20:44–00:00 | 3.3 h | 2.4 h |
| First manual research cycle, framework feedback, phone remote control, Spin prompt | 00:00–01:24 | 1.4 h | 0.8 h |

- The log shows one manually requested research cycle before the autonomous run: the user wrote
  "Go." at 00:00 and the cycle took 15 minutes. The first-person account above says "several such
  turns"; the log does not support that.
- At 01:24 the user wrote "Create a goal to execute the 'Spin:' prompt in notes, and start it now."
  Spin is the saved prompt that tells the agent to repeat research cycles on its own.

#### Codex: the autonomous run to the result

| Stretch | When | Wall time | Agent working |
|---|---|---|---|
| First Spin turn | Fri 11 Sep 01:24 → Sat 12 Sep 23:18 | 45.9 h | 45.9 h |
| Stopped (the user noticed and asked why) | 23:18 → Sun 13 Sep 00:51 | 1.5 h | 0 |
| Second Spin turn, up to the Res(⊕) commit | Sun 13 Sep 00:51 → Mon 14 Sep 03:55 | 27.1 h | 27.1 h |
| **Spin start to result** | | **74.5 h** | **73.0 h** |

- Inside those turns the log is never silent for more than 21 minutes, so the agent was working
  continuously and not waiting.
- Up to and including the result, the agent recorded 122 research cycles in the notebook and went
  through 18 context compactions. It processed about 375 million tokens, most of them cached
  context read again, and wrote about 5.3 million.
- The user sent about 30 messages in those three days: permissions to push, requests to improve the
  framework, and strategic questions such as whether the accumulated lemmas were approaching the
  goal or orbiting it.
- The agent's internal audit of the result followed at 05:39. The user asked for an assessment of
  the night's progress at 11:49 and asked whether the result deserved publication at 12:00.
- The same turn continued until 15 September 04:18 (51.5 hours in total). The later part covered
  the publication audit and the first whitepaper draft.

#### Weekly usage limits

The readings are for the whole account, so they include the user's other Codex sessions.

| Window | First use | Hit 100% | Time to hit | Wait until usable again |
|---|---|---|---|---|
| 1 | Thu 10 Sep 19:16 (counter restarted Sat 12 Sep 10:28) | Wed 16 Sep 02:16 | 5.3 days from first use, 3.7 days from the restart | 3.5 days (reset Sat 19 Sep 10:28, first use 14:10) |
| 2 | Sat 19 Sep 14:10 | Mon 21 Sep 15:36 | 2.1 days | 4.9 days |
| 3 | Sat 26 Sep 14:59 | Mon 28 Sep 16:38 | 2.1 days | 5.9 days (reset Sat 3 Oct 19:02, first use Sun 4 Oct 14:10) |
| 4 | Sun 4 Oct 14:10 | Tue 6 Oct 18:26 | 2.2 days | see below |

- In window 1 the usage counter went back to zero on 12 September at 10:28, when it had been at
  14% or more. The log does not say why.
- When the result was committed, the account was at roughly 27–41% of that window (27% on
  13 September at 23:02, 41% on 14 September at 17:39).
- Usage then rose from 55% to 90% in about four hours on the night of 14–15 September, while a
  second session was running alongside. The "Math research" session stopped on 15 September at
  10:32, at 97%.
- From 7 October the counter reset four times ahead of schedule (7 Oct 05:28, 7 Oct 22:08,
  8 Oct 21:07, 10 Oct 08:45) and was exhausted again within 14–22 hours each time. The logs do not
  show what caused the early resets.

#### Not measured

- Claude's five-hour usage limits and the changes of plan and model: the export has no limit
  events.
- The Lean formalization and the later preprint revisions, which came after the result and ran
  partly in other sessions.
