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
