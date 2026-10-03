# Audit bar: odd-prime-reslin-php leads and bridges (3 October 2026)

The user's standard: "I don't want any idea lost or closed prematurely." When unsure, queue it.

## The squeeze rule (AGENTS.md, user 3 October 2026)

Squeeze an item until it can produce nothing more, not until its first usable result:

- **Continuing** whenever its translation still bears on an open statement, naming and where possible
  making the concrete next attempt;
- **Developed** only when its results leave it no remaining application to an open statement;
- **Closed** only for a reason the attempt found: a restatement of the open problem, inapplicability,
  a falsification, or supersession by a stronger result.

A one-step objection (a structural remark, a record match, one encoding tried) falsifies only that
formulation; it is not a proper closure of the idea (user, 26 September 2026).

## Verdicts, one per item

- `properly-closed`: the closing follow-up shows a real attempt and a reason from the list above that
  covers the idea, not only one formulation of it; or a Developed whose result leaves no remaining
  application to any current open statement (open-statements.txt). Cite the entry anchor whose text
  establishes it.
- `reopen`: closed (or developed) at a first usable result, by a one-step objection, by a reason that
  covers only one formulation, or while its translation still bears on a current open statement.
  Name the open statement and the concrete next attempt.
- `undecided`: the record does not let you decide. These are queued (when unsure, queue it).

For older reviews without the standard sections (`older-*.txt`): list each idea that the review
presents as a lead or bridge from another area (named theorem, source, or translation) and that was
tested with a positive outcome or never tested, with whether any later entry developed it to
exhaustion. Undeveloped or partly developed ideas: `queue`; exhausted ones: `exhausted`, citing the
entry that exhausts it; unclear: `undecided`.

## Reading

Open the anchors with
`python3 tools/notebook-excerpt.py --notebook odd-prime-reslin-php --text ANCHOR` (articles are long;
read the relevant part, e.g. pipe through `grep -n` and `sed -n`). Do not load the whole notebook. Judge
against the current open statements in open-statements.txt and remaining-route.txt.
