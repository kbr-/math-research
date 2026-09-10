# Preserved resource validation

The 11 GB allocator test was performed earlier in this session, not rerun for
this commit. Its original output and measurement JSON are preserved here.
The watchdog killed the workload at 10,000,871,424 combined bytes. The wrapper
exit status is not the boundary criterion; the final test accepts any nonzero
termination with enforcement evidence and an empty workload group.

The earlier 15-worker CPU test reported CPUs 0-13 only (mask 0x3fff), 4.003 seconds
wall time, 55.910 seconds CPU time, and 13.965 average occupied CPUs. These CPU
figures are transcribed from the observed tool output, not a new execution.
Source: resource-controls/stress.c. The six later runner integration checks and
the small aggregate-memory regression are recorded in the archived
unify_compute_20260910_01 timing session.
