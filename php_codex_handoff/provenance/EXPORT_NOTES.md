# Export provenance and scope

This handoff was prepared from the mounted `php_research_sources_and_checks.zip` and the selected final `php_extension_research_compendium.pdf`, plus the earlier mounted PDF artifacts copied as archival bytes. It is a source-grounded continuation package, not a new research proof or literature audit.

## Preserved without alteration

- The twelve original LaTeX files in `manuscript/latex/`.
- All eleven historical check ZIP archives and every unpacked member.
- The selected final PDF (47 pages).
- The initial report and alternative compendium as archival copies, explicitly not automatically imported into the current theorem set.
- Original compilation/QA/manifests in this directory, identified by their preexisting filenames.

## New reading and navigation assets

`HANDOFF.md`, `AGENTS.md`, the full and split Markdown, the claim/label indices, notes, reference manifest, utility scripts, and their QA reports were made for this export. The Markdown conversion expands custom macros, resolves cross-references, and changes layout environments into headings/tables; the original mathematical TeX is retained to resolve conversion ambiguities.

The conversion retains 68 source proof blocks, 74 statement/example/imported records, and all 14 labeled equation anchors. Its first layout review caught a conversion issue with the layout-only `\\path` command dropping archive filenames; this was fixed in the converter and all original filenames were rechecked. A naive local-link scan initially mistook four occurrences of coefficient extraction `[u^d](1+nu)` for links; the final scan masks mathematics and reports zero missing targets over 335 actual local links.

These are structural and utility checks, not verification that all working proofs are correct. The external encoding match and the remaining proof audits retain the manuscript's status.

## Computations in this export

No historical research suite was run. The new tools were syntax-checked and exercised with help/listing, a disposable prepare-only copy of A11, and a tiny timing-logger subprocess. Original/unpacked byte equality was verified. This does not convert archived research outputs into newly reproduced results.

## External references

The current compendium has four direct mathematical references. Their records/reading targets are included. Web browsing could inspect official/source pages; direct downloads from this runtime failed with DNS errors. No full external paper is claimed to be cached. `tools/import_references.py` lets the local session acquire legitimate copies and records actual successes, failures, extraction status, URLs, and hashes. It does not validate mathematical hypotheses automatically.

The project `AGENTS.md` convention was checked against the official Codex documentation at `https://developers.openai.com/codex/guides/agents-md/`, which redirected to `https://learn.chatgpt.com/docs/agent-configuration/agents-md` on 2026-09-10. No model/configuration settings or API credentials are assumed or shipped.

## Timing

`export_timing.jsonl` holds marks from the export. Reading/review windows include interpretation; one source-reading/follow-up-lookup window is explicitly mixed. Tool windows include service and orchestration latency. Direct-download failures and the utility QA are counted. Only instrumented program runtimes can be identified separately; preparation, writing, uninstrumented small tool work, and overhead remain in the residual. The final response is generated after the end snapshot.
