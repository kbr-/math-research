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

This account was reconstructed by Codex from the exported Claude conversation, the mathematical
handoff produced after the later ChatGPT phase, the archived Codex session, and the append-only
research record maintained by the user's research framework.

The browser ChatGPT transcript was not yet available when this reconstruction was made.
Consequently, the Claude and Codex phases can be reconstructed from direct dialogue, while the
intervening ChatGPT phase is known mainly through its detailed handoff package and later
retrospective descriptions.

### What actually happened

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

Claude recommended:

> My pick is the finite-field IPS route to AC⁰[p]-Frege.

Its stated reason was unusually concrete. Unlike the other candidate directions, this route had
an explicit simulation or translation theorem: a suitable finite-field algebraic lower bound
would imply an AC⁰[p]-Frege lower bound. This supplied a checkable payoff condition instead of a
vague hope that understanding an adjacent model might eventually help.

The alternatives were:

- roABP and noncommutative IPS, potentially reaching full Frege but apparently requiring a
  substantially harder breakthrough;
- constant-depth IPS lower bounds on non-CNF instances, where results appeared more attainable
  but had a lower ceiling.

AC⁰[p]-Frege was therefore selected as an intermediate frontier: a decades-old open problem
connected to a named algebraic bridge and a potentially testable next step.

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

#### 5. The missing ChatGPT phase

The detailed browser ChatGPT transcript was unavailable during this reconstruction. Its handoff
package nevertheless records the endpoint precisely.

By 10 September, the research goal had become:

> Superpolynomial lower bounds for ordinary pigeonhole principle in fixed-depth AC⁰[p]-Frege,
> for each fixed prime p.

The route had narrowed through the BIKPRS simulation. In simplified form:

> A short AC⁰[p]-Frege proof would produce a bounded-degree extended Nullstellensatz or
> Polynomial Calculus object.

The ChatGPT phase produced a large body of intermediate mathematics—68 working lemmas,
theorems, and corollaries were recorded in the handoff—but affordable elimination of the
introduced extension blocks remained open.

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
