# Append structure guard

The append command validates its next-step fragment and the candidate notebook before writing. A
fragment may contain inner content and other headings, but not a section wrapper or a second
retained Proposed next step heading. The context-budget module supplies the shared living-section
parser; its budgets and queue exclusion remain unchanged. The command reports the written file's
byte count.

The real-command regression uses a temporary notebook and checks that invalid fragments and
duplicate living-section IDs leave it unchanged. Its positive case permits other headings, math
containing tag-like text and escaped markup. The context test also checks unlimited queue/record
contents, exact prefix boundaries and math in the record tag's attributes.

The final full framework suite passed 1,033 tests in 8.3 seconds. The five-test mutation control
passed before the two targeted guard-removal mutations; the named CLI regression failed on each, as
required. The initial scratch harness could not locate the real finisher and was corrected before
its control passed; that setup failure is not counted as a killed mutant.

Generic mutation testing ran 90 mutants in the two changed validation functions. It killed 82; the
eight survivors change error-message wording only: fragment-guard mutants 24 and 26, and
living-section mutants 39–42, 46 and 60. All were inspected. No selected mutant was untested. Other
generated functions were outside this selected run. The first run exposed missing positive coverage
for a different heading and queue/math boundary behavior; the existing tests were strengthened, then
the selected run repeated. The production guard logic did not change to accommodate mutants.

The read-only append API replayed the actual final entry and next step on the 9,599,994-byte main
notebook with 708 entries in 317 ms. The shared structure validator ran on the largest notebook,
18,339,779 bytes, in 258 ms. Each is one measured invocation, excluding import/input preparation;
neither is a claim about the full CLI's reporting time or an added-latency comparison.

Saved output: [suite](suite.txt), [mutation control](control.txt), [fragment-call
omission](omit-fragment.txt), [prefix-call omission](omit-prefix.txt), [generic
mutations](mutations.txt), [real append](real-append.txt), [largest prefix](largest-prefix.txt). The
tests are committed in `tools/tests/test_notebook_append.py` and
`tools/tests/test_notebook_context.py`; the mutation harness uses copies of those tests with module
imports and source-root paths adjusted, preserving the code under test.
