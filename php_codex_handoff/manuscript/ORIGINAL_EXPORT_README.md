# Pigeonhole Designs and Extension Elimination

Compiled from the independent research developed in the conversation.

## Contents
- `latex/`: editable manuscript source. Compile `main.tex` with pdfLaTeX (two or more passes), or run `latexmk -pdf main.tex`.
- `historical_checks/`: all eleven original computational ZIP archives, preserved byte-for-byte. Each contains its original scripts and results. They were not rerun merely to compile this document.
- `provenance/archive_manifest.json`: filenames, sizes, SHA-256 hashes, and archive member lists.
- `provenance/manuscript_manifest.json`: source and PDF hashes.
- `provenance/qa_report.json`: PDF rendering and structural checks, not a verification of the mathematical theorems.
- `provenance/compilation_timing.jsonl` and `timing_report.json`: observable timing for this compilation turn.

## Manuscript scope
The PDF contains 47 pages: ten chapters, three appendices, and references. There are 68 working lemmas, theorems, and corollaries with proofs, plus explicitly imported literature inputs. Reusable preliminary lemmas make the sequence self-contained within the document; external lower bounds and simulations are attributed rather than reproved.

Working derivations are not represented as independently refereed or generally machine-verified results. The PDF distinguishes established arguments within the conversation, superseded claims, method limitations, imported assumptions, and the remaining research obligations. No superpolynomial Frege lower bound is claimed.

## Build dependencies
A recent TeX Live installation with newtx, amsmath/amsthm, mathtools, microtype, booktabs, longtable, enumitem, titlesec, fancyhdr, tcolorbox, hyperref, and cleveref. No images or separately supplied font files are needed. Font files are not included.

## Historical computations
See Appendix B and the original archives' scope statements. Finite checks on satisfiable domains, truncated designs, or primitive proof instances do not establish the general PHP extension theorem. The eleven archives are intentionally nested rather than unpacked to preserve the original packages.

## Timing
Process runtimes include failed compilation attempts, revisions, all rendering passes, and packaging where instrumented. Marked reading intervals include interpretation and visual review. Pure internal reasoning and pure network latency are not observable. The final timing snapshot excludes its own small write/ZIP-update overhead and final chat generation/delivery.
