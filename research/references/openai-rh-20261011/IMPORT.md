# OpenAI Math: Riemann-hypothesis material

This is an attributed source import from [OpenAI Math](https://github.com/openai/math), obtained
after pulling its main branch on 11 October 2026. The exact source revision, file hashes and reading
scope are recorded in
[source-scope.json](../../results/openai_math_rh_import_20261011/source-scope.json) and the
accompanying provenance manifest. The live source checkout continues to track main.

The manuscripts and upstream metadata are retained unchanged under the accompanying [Apache-2.0
license](LICENSE). OpenAI remains their author. This project's original research license does not
replace their license. The October 5 quasi-Riemann paper says it was written with human assistance.

## Imported manuscripts

| Manuscript | Source-reported conclusion |
| --- | --- |
| [Seven-eighths half-plane](preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf) | Nonvanishing for all Dirichlet L-functions, including zeta, and finite-order Hecke L-functions over the Eisenstein quadratic field, for real part greater than 7/8. Principal poles are allowed. |
| [Eleven-twelfths alternative](preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/paper2.pdf) | The corresponding strict half-plane with real part greater than 11/12, through a separate mean-square argument. |
| [Landau–Siegel gap](preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/paper.pdf) | One positive constant bounds (1−β) log q below for real zeros β between zero and one of primitive nonprincipal real Dirichlet characters of conductor q at least three. |
| [Primitive roots and cyclotomic Hecke functions](preprints/Primitive-roots-for-every-admissible-integer-base-October-4-2026/primitive-roots-all-integer-bases.pdf) | A separate theorem states nonvanishing in real part greater than 1−10⁻⁶ for finite-order Hecke characters of cyclotomic fields containing the twelfth roots of unity. |

Complete TeX sources and upstream citation READMEs accompany the PDFs. The main import notebook
records the exact statements and which proof sections were read. These results are imported as
source-reported statements; this import does not independently establish their correctness or RH.
The usual RH asks for every nontrivial zeta zero to have real part one half, a stronger endpoint.

## Lean material

The [upstream scope note](lean/docs/003.md), four comparator targets and their JSON configurations,
and selected solution entry files are included. Comparator targets intentionally use `sorry`; their
configurations point to separate solution modules. The selected solution declarations are present,
but this snapshot does not include the whole transitive Lean dependency tree or toolchain. It is a
scope and navigation aid, not a standalone verified Lean project. No build, comparator replay or
axiom-closure check was performed in this import. The upstream scope note does not claim
verification of every later application, and the eleven-twelfths alternative and general cyclotomic
theorem must not acquire verification merely from another paper's Lean mapping.

The inspected Hecke target uses a custom residue-character model and a theta/lattice-defined
function. Its correspondence with every analytic finite-order Hecke character and with the
manuscript's meromorphic L-function was not independently checked; this is a separate encoding
bridge in addition to compilation and axiom closure.

## Reading and future use

Begin with the dated notebook import and its source-scope record. Before mathematical reliance, read
the required full source argument and corrections, and obtain independent verification at that exact
scope. Check all quantifiers, fields and allowed poles. For a future repeat of the repository
search, pull its main branch first under the import notebook's source-refresh policy.
