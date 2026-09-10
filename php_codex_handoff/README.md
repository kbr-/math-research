# PHP research — Codex handoff

Unzip this directory, open a local agent session here, and use:

> Read HANDOFF.md and import all references. Read the complete local mathematical record, record coverage and any failed reference imports, then continue from the refutation-sensitive elimination task. Do not assume that the lower-bound goal is already proved.

`HANDOFF.md` is the primary handoff. It is standalone as a mathematical checkpoint, but the complete proofs and computational record are in this package. The archive should be extracted as a directory, not pasted into one prompt.

## Contents

- Full Markdown with raw LaTeX, in one file and split chapters; all 68 original proof blocks, stable labels, a 74-entry index including imported inputs/examples, and machine-readable statements and dependencies.
- The unchanged original TeX source and final 47-page PDF.
- All eleven historical computational archives, both intact and unpacked, with their original results and scope notes.
- A four-reference bibliography, exact source-reading targets, and a local importer that records download/availability/extraction status.
- Audit/continuation notes, portable check launcher, integrity manifest, and timing utilities.

**Full external papers are not prebundled:** the export runtime could browse source records but its direct downloads failed at DNS resolution. Run the importer on the laptop. It reports inaccessible publisher papers; it does not pretend they were imported. The entire independent research proof corpus is already local and needs no network or PDF extraction.

## Commands

```bash
python tools/verify_bundle.py
python tools/import_references.py --list
python tools/import_references.py --fetch --extract
python tools/run_check.py --list
```

Python 3.10+ is required by the scripts. No dependency installation is needed to read the handoff or use basic integrity/timing tools. Numerical suites need NumPy, and the A01 suite additionally needs Numba; see `requirements.txt`. Import text extraction uses an existing `pdftotext` or `pypdf`, if present. Missing extraction support is reported separately from download status.

To regenerate the reading copy after a deliberate TeX revision:

```bash
python tools/rebuild_markdown.py
```

This requires Pandoc. It overwrites only generated manuscript reading/index files, not the original source. Preserve the initial snapshot in version control before editing. PDF rebuilding is optional; compile `manuscript/latex/main.tex` using the original packages, with at least two passes.

## Provenance

This is a continuation package, not an independent validation of the research. The source manuscript's distinctions between working proofs, imported results, method barriers, and unproved obligations are retained. No original research suite was rerun to create this handoff. Export utility and conversion checks are described separately in `provenance/`.

The root `AGENTS.md` follows the documented project-instruction convention for Codex. Official documentation reference: <https://developers.openai.com/codex/guides/agents-md/> (checked 2026-09-10; redirected to <https://learn.chatgpt.com/docs/agent-configuration/agents-md>).
