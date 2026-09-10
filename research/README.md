# Current PHP research

Start with [notes/RESUME.md](notes/RESUME.md) after compaction or session resume.
This directory holds all work performed after importing the handoff:

- `notes/`: restart context, mathematical checkpoint, source audit, and research log.
- `references/cache/`: the licensed public PDF and local-only source caches; see references/README.md.
- `references/user_supplied/`: preserved copies of the two PDFs supplied by the user.
- `tools/`: local acquisition and timing tools.
- `logs/`, `provenance/`, `tmp/`: current measurements, provenance, and temporary renders.

The historical manuscript, original computational archives, and original notes
remain in `../php_codex_handoff/`. All 128 original files were restored/verified
against the originally supplied ZIP; see `provenance/handoff_restoration.json`.
The outer ZIP is redundant and is not tracked; the complete directory is tracked.
Do not modify or generate artifacts in that historical directory.

Timing commands run from this directory, for example:

```bash
../compute.sh start research_turn_NAME
../compute.sh phase research_turn_NAME reading
../compute.sh run research_turn_NAME --threads 1 -- python3 calculation.py
../compute.sh report research_turn_NAME --stop --html-out results/research_turn_NAME/timing.html
```

Computations use `../compute.sh ...`. The math page remains at
`../notebook.html`, served by `../server.py`.

The root `compute.sh` combines protected execution and timing. The historical
timing implementation remains only in the immutable handoff.


Completed timing sessions and their command outputs are preserved with
`../tools/archive-session.py NAME` under `provenance/session-records/` before
research-result commits. Live `logs/` and scratch `tmp/` are ignored. Earlier
notes mentioning `logs/NAME...` refer to the original operational paths; durable
copies and path mappings are in each archived session's manifest.json.

Every research attempt, including failed or no-progress attempts, gets a notebook
entry with a measured timing table. Archive timing, preserve full result files,
and commit the complete checkpoint. Do not invent unmeasured categories.
