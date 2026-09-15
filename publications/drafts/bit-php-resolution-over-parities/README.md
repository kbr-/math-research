# Bit PHP in unrestricted resolution over parities

**Draft for review; theorem and dependencies verified in Lean.** This whitepaper expands the
[publication theorem](https://kbr.is-a.dev/math-research/#publication-Res-parity-bit-PHP-theorem)
and its dependencies, using the generalized statements and human-readable proofs
recorded during formalization. Each statement links to its Lean source at published
revision `54f09378e97465522b7f1caf115f90ad1faa7a57`. The appendix includes all
H01–H13 homological prerequisites and their proofs. External review of the
manuscript remains separate from formal verification.

- [Rendered PDF](whitepaper.pdf)
- [Main TeX source](whitepaper.tex), with the complete argument in [sections](sections)
- [Bibliography](references.tex)

Author: Kamil Braun, with assistance from Claude Sonnet, Claude Opus,
Claude Fable, and GPT-6 Astra. GPT-6 Astra was the main contributor to the
mathematical development and drafting of this result.

The draft proves its algebraic dependencies inline and includes a homological
proof of the required chessboard-complex input. It also describes the research
framework and links to the repository and live notebook. It uses the audited
h=3*ell route; the subsequent constant-accuracy investigation is not a dependency.

## Build

From the repository root, with the resource controls active:

~~~sh
./publications/drafts/bit-php-resolution-over-parities/build.sh
~~~

During an instrumented research turn, attach the build to its existing clock:

~~~sh
./publications/drafts/bit-php-resolution-over-parities/build.sh --session TURN
~~~

The script runs three pdflatex passes inside the shared compute.sh limits,
with shell escape disabled. It uses the installed TeX Live packages listed in
whitepaper.tex and installs nothing. The sources and final PDF are tracked;
rebuildable LaTeX artifacts are ignored by the parent .gitignore.

Original manuscript material uses CC BY 4.0 under the repository's root license.
Third-party work is cited and retains its own rights.
