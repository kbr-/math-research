# Existing Lean coverage for the chessboard filling theorem

Search date: 15 September 2026. Outcome: **no matching checked formalization
located**, not a proof that none exists. No external project was installed or
built, and no new dependency was added to the Lean project.

## Target and search scope

The required interface is: for s≥2 and N≥2s−1, every reduced (s−2)-cycle
in the chessboard complex Δ(s,N) over F₂ admits a filling. Finite-instance
homology calculations would not establish this parameterized theorem.

Searched the pinned Mathlib sources at
`67248ba34806c60bf24b5e99f0f09946ffc465c9` for chessboard, BLVZ, matching-complex,
author-name, shellability, nerve-theorem, and discrete-Morse terms, and inspected
the relevant simplicial-complex and simplicial-set homology module descriptions.
The broad author-name search hit Lovasz's Kruskal–Katona theorem, not BLVZ.

Web searches included `Lean mathlib chessboard complex BLVZ formalization`,
`"chessboard complex" "Lean" theorem`, `"BLVZ" "Lean"`,
`"matching complex" "Lean" formalization`, GitHub-restricted variants,
and searches for Lean homological nerve theorems. Public GitHub repository
searches and revision-pinned file inventories are retained in the JSON files.
Repository search is metadata search, not a global source-code scan. An attempted
GitHub code search via `gh` could not run because that CLI is unavailable.
Search-engine indexing and the inspected project descriptions/trees are not
exhaustive evidence of absence.

## Reusable foundations and leads

| Source | Located coverage | Relation to our obligation |
| --- | --- | --- |
| [Mathlib abstract simplicial complexes](https://github.com/leanprover-community/mathlib4/blob/67248ba34806c60bf24b5e99f0f09946ffc465c9/Mathlib/AlgebraicTopology/SimplicialComplex/Basic.lean) | `PreAbstractSimplicialComplex` and `AbstractSimplicialComplex` definitions and operations. | Foundation only; no chessboard filling theorem located. Faces in these definitions are nonempty, so a reduced-chain/augmentation convention needs explicit attention. |
| [Mathlib simplicial homology](https://github.com/leanprover-community/mathlib4/blob/67248ba34806c60bf24b5e99f0f09946ffc465c9/Mathlib/AlgebraicTopology/SimplicialSet/Homology/Basic.lean) | Simplicial-set chain complexes and homology; nearby modules cover relative homology and homotopy invariance. | Available infrastructure, but a bridge from our finite matching complex and its reduced cycles is still needed. A simplicial nerve of a category is not the homological cover nerve theorem used in the paper appendix. |
| [not-gary/pachner](https://github.com/not-gary/pachner), [authors' paper](https://arxiv.org/html/2607.10216v1) | Abstract complexes, simplicial maps, links, joins, and stellar subdivisions. | The paper's §4.3.1 lists simplicial homology/cohomology as future work; no chessboard or homology module appeared in the inspected repository file names. It is not a ready BLVZ implementation. |
| [smorel394/AbstractSimplicialComplex](https://github.com/smorel394/AbstractSimplicialComplex) | Shellability, decompositions, and Euler–Poincaré characteristic machinery, according to its detailed README. | Potential combinatorial infrastructure. Euler-characteristic information alone does not imply the required individual homology vanishing. No target theorem located. |
| [jeffrey-dot-li/lean-homology](https://github.com/jeffrey-dot-li/lean-homology) | Repository describes basic homotopy computations; tree includes cellular homology and Kneser-conjecture development. | Broader topology lead, not an identified match. Individual theorem statements and proof completeness were not audited. |
| [sdong1212/lean-homology-cert](https://github.com/sdong1212/lean-homology-cert) | File inventory includes matrix complexes, kernel/exactness certificates, and Smith-presentation code. | Potential finite-certificate tooling, not evidence of the universal chessboard theorem. No build or axiom audit performed. |

The theorem-named web searches also returned unrelated chessboard puzzles and
ordinary mathematical papers. These were not accepted as Lean coverage of the
topological theorem. GitHub metadata query counts are preserved as search results,
not treated as numbers of applicable formalizations.

## Consequence for the route

Keep external boundary H open. There is real reusable infrastructure, but this
search does not justify replacing H with an imported checked theorem. The next
design task is to match our explicit F₂ reduced-chain filling statement to an
existing homology API or a direct finite-chain representation, then plan its
proof. That task was not undertaken here.

The initial web/local search batch preceded timing instrumentation. Subsequent
searches, review, and recording were measured in `lean_chessboard_coverage_20260915`.
Full GitHub query output and inspected tree revisions are retained alongside this
note; source hashes and the timing archive accompany the research-record entry.
