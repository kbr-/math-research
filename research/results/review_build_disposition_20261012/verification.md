# One completed build in a scheduled review

The queue validator now permits a scheduled review to record one completed standalone build. It
retains normal evidence validation and rejects unresolved children, nested builds, multiple
completions including a mixed Developed/Closed pair, mathematical-item completion through this
exception, and unrelated completions in research entries. It does not broaden research spell
counting or restore batch triage.

The regression drives the queue append and validation paths. Its final control passed one test and
eight subtests. Removing the exception fails that named test; omitting Closed items from the
completion count fails its mixed-completions subtest. This second case was added after the same
research reviewer found that gap in the initial patch. No broken version was committed.

Generic mutation testing killed all 24 selected mutants of the new predicate, with no survivors or
selected untested mutants. Other generated functions were not tested by this selected run.
Generation by the installed mutation tool took 45.8 seconds; the selected mutations themselves took
about two seconds with two children. This is tool-generation cost, not a numerical computation
scaled from a smaller case. The tested predicate did not change after that run; the subsequent
correction changes its call to include Closed items and has the targeted regression.

The queue check passed on the actual new review/build-removal diff in the main notebook: 9,619,284
bytes, 709 entries, 0.349 seconds. It also passed the latest real entry diff in the largest
notebook: 18,339,779 bytes, 1,341 entries, 1.055 seconds. These are individual validation timings,
including parsing and excluding input retrieval, not speedup claims. The final full-suite result is
in [final-suite.txt](final-suite.txt): 1,034 tests passed in 8.3 seconds. The same medium reviewer
read the corrected implementation and targeted failure and returned pass, with no remaining code or
process findings.

Saved evidence: [control](final-control.txt), [omitted exception](omission.txt), [mixed-completion
omission](mixed-omission.txt), [generic mutations](mutations.txt), [main diff](main.txt), and
[largest diff](largest.txt). The scratch harness copied the committed queue tests, changing its
module import and root path to select the scratch code. Production code was never mutated.
