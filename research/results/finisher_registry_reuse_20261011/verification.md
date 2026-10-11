# Finisher registry parse reuse

Status lookup and strict registry validation now share one parsed snapshot,
keyed by resolved path, modification time and size. Strict schema validation
still runs. The cache holds one snapshot; the finisher does not write the
registry. This changes no research or review rule.

The live-registry status-plus-validation benchmark used 46,200,660 bytes.
Across three measurements per version, median elapsed time was 3.0166 seconds
before and 2.4253 seconds after. This measures that path, not the entire
finisher or a guaranteed runtime under concurrent load. The baseline was the
pre-change committed finisher; the saved command and full observations are in
benchmark.txt.

The two focused tests pass. Four targeted mutants were killed by named test
failures after the two-test unmutated control passed: disabling reuse, skipping
strict validation, ignoring modification time and ignoring size. The generic
run killed all 11 mutants in the selected changed functions, with no remaining
survivor. Its first run exposed an untested size-only change; the existing
change-invalidation test was strengthened to cover it. Three generated mutants
in unchanged validation/reporting functions were outside the selected run,
not uncovered new paths. Decorated functions were checked by the targeted
reuse mutant rather than credited to generic mutation coverage.

The complete framework suite ran 890 tests successfully but took 10.3 seconds,
so its timing gate failed. The three browser groups were slowest. No claim that
the full suite passed its time requirement is made. The snapshot tests do not
change browser code, and no unverified cause is assigned to that timing result.
