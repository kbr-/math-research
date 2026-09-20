# Development history

This page records how I developed and reviewed my [short note on binary
polynomial multiplicities](whitepaper.pdf), including the role of AI assistance. The paper contains the full argument; this history provides
background rather than mathematical prerequisites.

The note arose within **Noemesis**, my research project on lower bounds in
proof complexity. The project maintains a public [research notebook](https://kbr.is-a.dev/math-research/):
a dated working record of arguments, literature comparisons, unsuccessful
approaches and reviews. It also contains a summary of the project's current
mathematical position. Notebook entries are working research records, not
independently reviewed publications. I direct the investigation, with
substantial assistance from AI coding and research tools, including GPT-6 Astra
in Codex.

## Version 1 — 20 September 2026

While examining whether an earlier result in that project connected to a
published open problem, Codex compared related work on polynomial vanishing and
coverings of finite grids. During this literature comparison, it identified that
the bound printed in Question 4.3 of Bishnoi, Boyadzhiyska, Das and Mészáros's
*Subspace coverings with multiplicities* follows directly from the earlier
multiplicity Schwartz–Zippel lemma of Dvir, Kopparty, Saraf and Sudan.

This deduction is independent of the project's earlier results: it uses only
the published question and the standard lemma. The notebook's
[full deduction and source-version comparison](https://kbr.is-a.dev/math-research/#binary-multiplicity-cover-question)
records the observation and its scope. A subsequent bounded web search found
no public correction or acknowledgement of this particular implication; that
search does not establish priority or exclude prior knowledge.

I then requested a short, self-contained preprint. Definitions and the
imported lemma are stated explicitly, and the full deduction is given. The note
presents an application of an existing theorem, not a new multiplicity theorem.
It has not received independent mathematical review or formal verification;
no contact with the original authors or submission is recorded here.

### In-place checklist review

I clarified that I had not sent the note to anyone and that it is version 1,
not a first revision. The initial local draft's “revision 1” label was corrected;
subsequent pre-circulation edits remain within version 1. Earlier notebook entries
and build snapshots preserve the historical label rather than being rewritten.

The paper-specific checklist prompted a short explanation of the counting idea,
a directly displayed conclusion in the proposition, a shorter explanation of
external question numbering, consolidated scope wording, and a clearer disclosure
of the author/AI roles and outstanding independent review. The mathematical
statement and proof are unchanged. Item-by-item dispositions are in
[the feedback and self-review record](FEEDBACK.md).

### Additional feedback applied within version 1

Further AI feedback prompted clearer implication wording and a distinction
between validity and sharpness. The edits added the Alon–Füredi comparison
with a supporting reference. The review also checked the suggested literature
and characteristic-two construction. Details and source-version limits
are in [the application notes](feedback-application-20260920.md). The proof and
version remain unchanged; independent review and prior knowledge remain open.

### Second feedback application within version 1

Replaced the secondary Alon–Füredi citation with the original Theorem 5, checked
its arbitrary-field polynomial statement, and removed the unused
Sauermann–Wigderson reference.
Rendered and visually inspected both pages, including the flagged nonzero sign
and display (3); both render correctly. Optional equality examples remain in the
review notes. These were editorial and source-checking updates; the main
statement and proof did not change.
