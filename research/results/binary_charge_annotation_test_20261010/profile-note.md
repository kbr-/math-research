# Controller diagnosis between cycles

The actual changed-record finalization for binary_tseitin_interpolation_test_20261010
was profiled with cProfile, rather than rerunning a no-change fixture. The full
profiled command took 6.967 seconds, including finalization subprocesses; the
five-second pre-snapshot check warning did not fire on this run.

Largest cumulative entries: subprocess.run 2.739 seconds across sixteen calls;
check_revision 2.082; claim_registry.load 1.160; maintenance 1.013;
claim_registry.validate 0.899. The prior turn-guidance optimization is measured
separately in commit 8b5197893. No additional speedup is claimed here and no
checks were removed. The profile includes archive/start operations, so its total
is not itself the five-second check interval.
