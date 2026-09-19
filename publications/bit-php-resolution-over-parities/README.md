# Bit PHP in unrestricted resolution over parities

**Preprint, revision 2 (19 September 2026); theorems and dependencies verified in Lean.**
The whitepaper proves an exponential lower bound, more than exp(n/(32768 ℓ²)) nodes for every
ℓ ≥ 32 ([Lean](https://github.com/kbr-/math-research/blob/8904bf09a5376f48a00d1c25d079bf0c6441502a/formalization/claims/BitPHPExponential.lean)),
the [superpolynomial form of version 1](https://kbr.is-a.dev/math-research/#lean-publication-bit-PHP-superpolynomial)
([Lean](https://github.com/kbr-/math-research/blob/8904bf09a5376f48a00d1c25d079bf0c6441502a/formalization/claims/BitPHPSuperpolynomial.lean)),
and a generic sufficient condition for Res(⊕) size lower bounds. Each statement links to its Lean
source at published revision `8904bf09`; version 1 (15 September 2026) corresponds to `54f0937`.
The appendix includes all H01–H13 homological prerequisites and their proofs. External review
of the manuscript remains separate from formal verification.

Revision 2 improves attribution, exposition, table readability, and verification
navigation without changing the theorems or Lean proofs. Appendix B contains the
verification map and complete reproduction instructions: the submitted paper is
self-contained and needs no supplementary README. Its reproduction checkout is
`8904bf09a5376f48a00d1c25d079bf0c6441502a`, which includes the aggregate verification
module; the theorem links use that same commit.

## Verify the formal proofs

From the repository root, after the one-time Lean setup in
[formalization/README.md](../../formalization/README.md):

~~~sh
./formalization/verify.sh --target claims/BitPHPPreprintRevision1.lean
~~~

The expected axiom report for each listed declaration, for example the main theorem, is

~~~
'MathResearch.bitPHP_exponential' depends on axioms: [propext, Classical.choice, Quot.sound]
~~~

that is, Lean's standard foundations only. The target is an import-only module gathering every
formal result the paper cites; it also passed `leanchecker --fresh` on 18 September 2026
([record](../../research/results/preprint_rev1_review_fixes_20260917/replay.json)). To replay it:

~~~sh
cd formalization && lake env leanchecker --fresh claims.BitPHPPreprintRevision1
~~~

- [Rendered PDF](whitepaper.pdf)
- [Main TeX source](whitepaper.tex), with the complete argument in [sections](sections)
- [Bibliography](references.tex)
- [Development history](DEVELOPMENT_HISTORY.md), moved out of the paper in revision 1
- [Feedback and revision checklist](FEEDBACK.md)

Author: Kamil Braun, with assistance from Claude Sonnet, Claude Opus,
Claude Fable, and GPT-6 Astra. GPT-6 Astra was the main contributor to the
mathematical development and drafting of version 1. Claude Fable 5.1 formalized the additions
of revision 1 (one proof batch delegated to Claude Opus 5) and drafted the revised text.
GPT-6 in Codex applied the revision-2 feedback and prepared its verification appendix.

The preprint proves its algebraic dependencies inline and includes a homological
proof of the required chessboard-complex input. It also describes the Noemesis research
framework and links to the repository and live notebook. It uses the audited
h=3*ell route; the subsequent constant-accuracy investigation is not a dependency.

## Build

From the repository root, with the resource controls active:

~~~sh
./publications/bit-php-resolution-over-parities/build.sh
~~~

During an instrumented research turn, attach the build to its existing clock:

~~~sh
./publications/bit-php-resolution-over-parities/build.sh --session TURN
~~~

The script runs three pdflatex passes inside the shared compute.sh limits,
with shell escape disabled. It uses the installed TeX Live packages listed in
whitepaper.tex and installs nothing. The sources and final PDF are tracked;
rebuildable LaTeX artifacts are ignored by the parent .gitignore.

Original manuscript material uses CC BY 4.0 under the repository's root license.
Third-party work is cited and retains its own rights.
