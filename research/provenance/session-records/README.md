# Archived timing and execution evidence

Each session directory preserves its completed timing journal, summary, and
full command outputs. `manifest.json` maps the original operational paths to
archived files and records SHA-256 hashes. Older notes that mention
`research/logs/NAME...` can be resolved through these manifests after cloning.

Live `research/logs/` is ignored. Before committing a new research result, run
`./compute.sh report NAME --stop` and `./tools/archive-session.py NAME` from the
repository root. Preserve substantive output files separately under
`research/results/` when appropriate and reference them from the research log.
