# Resume protocol comparison

The user's objection matters: an explicitly optimized batching plan does not
establish what agents normally do. This comparison separates a historical
observation from controlled command-execution measurements.

## Actual historical observation

`historical-sample.json` audits the explicit post-compaction resume request in
this same session on 10 September 2026. It used **three outer tool calls and three
nested shell calls**, with file reads combined inside commands. Completion was
22.319 seconds after the request; the final response indicated readiness. No
truncation marker was detected in the saved tool results.

This was not prompted as a batching benchmark. It demonstrates that batching
occurred naturally, but is **one sample from an earlier guide/notebook version**,
not an estimate of average behavior or proof that all required context was fully
understood. COMPUTATION_RULES.md was not among the detected file references in
that restore-only turn. Do not equate its payload with the full-context benchmark.

Only counts, tool/file categories and timestamps were exported. No source text,
commands, conversation text, session identifiers or transcript paths are retained.
The private log is not published. `audit_trace.py` reproduces the filtered audit
only when the correctly bound local historical session log is available; it cannot
reproduce that observation from a public clone alone.

## Controlled measurements

`measure.py --out PATH` runs seven repetitions in temporary checkouts, alternating
scenario order deterministically. The old protocol is pinned to `23cedfe`; the
new tool to `5388dec`. Temporary source copies and synthetic recovery records are
removed afterward; only measurement data is persisted.

| Scenario | Planned shell-tool calls | Output bytes | Median command time |
| --- | ---: | ---: | ---: |
| Old, separate reads | 6 | 52,863 | 0.5689 s |
| Old, deliberately batched control | 3 | 52,863 | 0.5628 s |
| Old batching with current documents | 3 | 54,115 | 0.5720 s |
| New cached bundle | 4 | 55,105 | 0.4809 s |

The old separate/batched outputs concatenate to identical content. New emitted
parts reconstruct the full cached bundle exactly. The new delivery adds 990 bytes
over manually reading the same current documents; changed guidance accounts for
the rest of its increase over the old revision. The largest old batched response
is 30,121 bytes versus 16,275 bytes for new delivery including delimiters.

These are **subprocess timings**, not API round trips, model reading/thinking or
end-to-end restoration. OS caches were not flushed. The model was not asked to
choose a natural sequence under blinded conditions. Tool-call counts follow the
specified grouping plans; the benchmark does not observe an agent distribution.
Capturing subprocess stdout does not simulate transport truncation. No token
usage is inferred from bytes or words.

## Conclusion and reproduction

The new tool has demonstrated bounded, retryable delivery and explicit resume
instrumentation. **A reduction in natural tool calls, total recovery time or token
usage has not been demonstrated.** Its small command-time saving cannot establish
an end-to-end speedup. Keep the optimized control labelled as a control; collect
several ordinary resumes before drawing a typical-cost conclusion.

Run the scripts through `compute.sh` under the computation policy, using new output
paths. Initial planning and source inspection preceded this cycle's timing; no
unmeasured time was reconstructed. The trace audit had one UTC-parsing compatibility
retry, recorded as a tool failure rather than a failed mathematical argument.
