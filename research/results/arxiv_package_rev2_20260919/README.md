# arXiv upload package for manuscript revision 2

Prepared on 19 September 2026 from tag `bit-php-preprint-2026-09-19`.
This is submission preparation only, with no manuscript or mathematical change.
The author reports receiving endorsement and is performing the submission.

Upload `/tmp/bit-php-arxiv-revision-2.tar.gz` (50,804 bytes). SHA-256 and
individual member hashes are in `manifest.json`. Run `prepare.py` through
`compute.sh` from the repository root to reproduce the archive and checks.
Its gzip/tar metadata are fixed for reproducibility. The archive contains
12 TeX files and the CC BY 4.0 license, with the main file at its root and
section paths preserved. It includes no generated PDF, build output, README,
feedback, private conversation, third-party paper, or Lean project.

The exact extracted package compiled using PDFLaTeX in three passes without
warnings. It produced 37 pages. Extracted PDF text and every rendered page
(Poppler PNG at scale 700) match the tagged PDF. Full per-pass output and the
final log are retained here; scratch PDFs/PNGs remain local and untracked.
This verifies the local TeX installation, not arXiv's remote compiler.

Guidance consulted:
- https://info.arxiv.org/help/submit/index.html
- https://info.arxiv.org/help/submit_tex.html
- https://info.arxiv.org/help/tar.html

For a TeX-authored paper, arXiv requires sources instead of its generated PDF.
On Add Files, upload the archive, choose Check Files, confirm `whitepaper.tex`
as the top-level file and PDFLaTeX as the compiler, and inspect arXiv's generated
PDF before proceeding to metadata. Standard TeX Live packages need not be bundled;
this paper has no custom external styles, figures, or BibTeX-generated bibliography.
The license text records the source's existing terms; it is not a compile input.
