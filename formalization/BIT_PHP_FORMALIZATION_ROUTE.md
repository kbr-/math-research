# Bit-PHP publication formalization route

Dependency-first plan for `thm:publication-Res-parity-bit-PHP`, based on the
[linked end-to-end proof](https://kbr.is-a.dev/math-research/#publication-Res-parity-bit-PHP-proof)
and its [dependency table](https://kbr.is-a.dev/math-research/#publication-Res-parity-dependencies),
cross-checked against the expanded
[paper sources](../publications/drafts/bit-php-resolution-over-parities/whitepaper.tex).
Source checkpoint: `bba68c96a04c53e1c3953d91b58d88b893934ea3`.

The target is the usual bit-PHP CNF with `n = 2^ℓ` holes and `m = n+1`
pigeons, in unrestricted DAG-like resolution over parities over `𝔽₂`, under
either recorded rule convention. For each fixed real `K > 0`, sufficiently
large instances require more than `n^K` proof nodes.

This is the shortest sufficient route identified in the recorded proof, not a
claim that no other mathematical proof could be shorter. It retains `h = 3ℓ`
and avoids later improvements that the publication proof does not need.
The current priority is the third-party interface **H**: work through H01–H13
below first, then return to the project-side R01–R25 order. H has a checked
formal statement, not a proof; no downstream completion is inferred from it.

## How to use the list

Rows are in topological order: every `Rxx` prerequisite occurs earlier.
`Rxx` identifiers are planning references, not new claim-index labels.
“Helper to extract” means a necessary statement already proved inside a larger
source, but not separately indexed in the required scope. Give it a claim label
and full research record when it is extracted/formalized. Proving such a helper
does **not** formalize the larger source claim.

The same applies to `Hxx`: these are planning identifiers, not provenance or
directory assignments. Follow the individual-statement
[provenance policy](AGENTS.md) when choosing between `claims/` and
`third-party-claims/` and retain the appropriate attribution.

Existing indexed dependencies receive their own formalization records under
the formalization protocol. New extracted dependencies may share their parent's
record. Mathlib may supply elementary algebra, linear algebra, combinatorics,
and asymptotics, but their exact interfaces still need checking. “Existing Lean”
below means reuse the checked statement and file, not repeat its formalization.

## Ordered claims and prerequisites

| Order | Claim / precise formalization target | Direct prerequisites | Source and scope |
| --- | --- | --- | --- |
| R01 | **Ordinary polynomial proof foundations:** finite variable sets, original joint total degree, primitive PC derivations, truncated ordinary-NS spaces `I_B`, and old Boolean/functional-unary/compact-bit bases. | — | [Paper §2](../publications/drafts/bit-php-resolution-over-parities/sections/02-algebra.tex), [matching base](https://kbr.is-a.dev/math-research/#matching-moment-completeness-audit), [compact base](https://kbr.is-a.dev/math-research/#compact-bit-base-definition). Definitions, not a claim of `PC = NS`. Make each axiom multiple's degree explicit. |
| R02 | **`lem:reuse` and the elementary `I_B ⊆ C_B` inclusion:** multiply a completed PC line by a polynomial through `max(previous ceiling, deg q + deg f)`. | R01 | [Historical Lemmas 1.2–1.3](../php_codex_handoff/manuscript/chapters/01_foundations.md#lem-reuse); paper `lem:pc-product`. Include zero lines and concatenation/reuse of derivations. |
| R03 | **`lem:substitution`: degree-controlled PC substitution, including weighted replay** from supplied weighted axiom-image proofs. | R01, R02 | [Historical Lemma 1.4](../php_codex_handoff/manuscript/chapters/01_foundations.md#lem-substitution). The crucial predecessor bound is `D-1` for a nonzero variable-multiplication step. |
| R04 | **`lem:duality`: finite-dimensional separation and annihilator extension interfaces.** | R01, R02 | [Historical Lemma 1.2](../php_codex_handoff/manuscript/chapters/01_foundations.md#lem-duality). Required for old filtration stability and the common restriction kernel; use Mathlib where it matches. |
| R05 | **Degree-controlled Boolean reduction over `𝔽₂`**: squarefree remainder with ordinary NS witnesses through the original degree; Boolean-grid vanishing implies such membership; `q²-q` has cost at most `2 deg q`. | R01 | Helper to extract from [historical `lem:fieldreduction`](../php_codex_handoff/manuscript/chapters/01_foundations.md#lem-fieldreduction), paper `lem:boolean`. Only the binary Boolean case is needed; no full mixed-domain/all-prime formalization is required for this route. |
| R06 | **`lem:mp-telescoping`: explicit ENS prefixes and their joint-degree bounds.** | — (existing Lean) | [MpTelescoping.lean](claims/MpTelescoping.lean). Reuse its identity and upper bounds. The correction to the loose-ceiling equality remains in force; exact proper-block degrees are separately established in R07. |
| R07 | **Affine-system normal form and scalar cleanup:** proper affine input spans have independent linear parts and nonempty zero flats; zero/unit spans can be eliminated; nonzero proper companions have exact degree `2h+1`. Include affine vanishing on a consistent zero set ⇒ constant linear combination of its defining forms, and empty zero set ⇒ a constant combination equal to one. | R01, R03 | Helpers to extract from [affine learning setup](https://kbr.is-a.dev/math-research/#affine-common-vanishing-learning), [semantic weakening](https://kbr.is-a.dev/math-research/#semantic-weakening-PC-degree), and paper §5 `lem:cleanup`. Fresh independent coefficients and genuine degree-one inputs justify equality. These linear-algebra witnesses are stronger than the existing Boolean semantic separator. |
| R08 | **Low-rank, no-retained-core factor packing:** `r ≤ h(k+1)` affine basis complements fit `h` bins, giving coefficient degree at most `k`, product equal to the zero-flat indicator, and companion Boolean certificates through `r+1`. | R05, R06, R07 | Helper to extract from [mixed packing](https://kbr.is-a.dev/math-research/#mixed-packing-common-vanishing-learning), expanded explicitly in paper §5 `lem:hybrid`. Do not apply the full [optimal retained-core theorem](https://kbr.is-a.dev/math-research/#relative-optimal-linear-packing) with `t=0`: its stated hypotheses require `t≥1`. Its optimality and general retained-core transfer are unnecessary. |
| R09 | **`audit:matching-moment-completeness`: functional-unary matching normal form and the complete marginal equations.** | R01, R05 | [Exact audit](https://kbr.is-a.dev/math-research/#matching-moment-completeness-audit), paper `lem:marginals`. Reduce Boolean powers and row/column collisions without increasing degree; prove that every remaining row-generator multiple is exactly a legal matching marginal. Include both constant-moment values, not just normalized designs. |
| R10 | **`audit:matching-extension-arbitrary-row-count`: extend prescribed moments and derive old filtration stability / `C_B = I_B`.** | R02, R04, R09, **H** | [Exact arbitrary-row audit](https://kbr.is-a.dev/math-research/#matching-extension-arbitrary-row-count), paper `thm:moments` and `cor:stability`. Handle `m≥B`, `N≥1`, `N≥2B-1`, degree zero/one, and disjoint new top moments across row sets. Construct the cycles and translate fillings into marginals locally; only existence of the topological fillings is deferred. |
| R11 | **`lem:two-functional-row-state-interpolation`: bilinear one-hot interpolation with ordinary NS cost `max(d,2)`.** | R01, R05 | [Statement and proof](https://kbr.is-a.dev/math-research/#two-functional-row-interpolation), paper `lem:interpolation`. Its upstream state reduction is the elementary power/collision normal form in [column-state-reduction](https://kbr.is-a.dev/math-research/#column-state-reduction), applied to rows, followed by explicit row-sum homogenization. Prove that small normal-form helper here or reuse R09's reduction infrastructure; the larger column-normalizer theorem is not required. |
| R12 | **Degree-preserving compact-to-functional decoder for arbitrary PC consequences**, with original-degree Boolean/collision image certificates; injectivity and ordinary-degree preservation. | R01, R02, R03, R11 | Helper to extract as paper §4 `lem:decoder`, using [compact decoder certificates](https://kbr.is-a.dev/math-research/#compact-bit-PC-lower-bound) and the map in [transported filtration](https://kbr.is-a.dev/math-research/#compact-bit-transported-filtration). Needed conclusion: `q ∈ C_B(Q_n) ⇒ τq ∈ C_B(Ffun)`. The full `J_k`/annihilator package and separate compact-base degree lower bound are unnecessary. |
| R13 | **Row-linear polynomial space and dimensions:** `dim L_k = Σ_{j≤k} binom(m,j) ℓ^j`; nonzero members have a nonzero maximal-row coefficient; ordinary restrictions to `v-r` variables have image dimension at most `binom(v-r+k,k)`. | R01 | Helpers in paper §4 equation `eq:row-linear-dimension` and §5 `lem:kernel`; [ordinary restriction audit](https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit). Use ordinary polynomial monomials, not Boolean quotient dimensions. |
| R14 | **`lem:cube-residual-dual-separation`: separate every nonzero `f ∈ L_k` from old functional PC after decoding.** | R09, R10, R12, R13 | [Full alternate proof](https://kbr.is-a.dev/math-research/#cube-residual-dual-separation), paper `thm:row-separation`. Construct disjoint bit-direction pairs, residual-board designs, and the tensor functional; check every marginal and the isolated coefficient. Conditions include `ℓ≥2`, `1≤k≤B`, `4(k-1)<n`, `n≥2B-1`; use R10 on the rectangular residual board. |
| R15 | **Common ordinary restriction kernel and literal affine-ideal coefficients.** For `h=3ℓ`, `k=ceil(sqrt(m ln(4M)))`, `k≤m`, construct nonzero `f ∈ L_k` with `f=Σ_i a_i g_i`, `deg a_i≤k-1`, for every high-rank block. | R04, R07, R13 | Helper to extract from [ordinary restriction audit](https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit), paper `lem:kernel`. Prove the binomial ratio / exponential bound and joint-kernel dimension estimate, including the no-high-block case. Literal membership follows from zero **ordinary-polynomial** restriction in affine coordinates, not merely pointwise vanishing. |
| R16 | **Simultaneous low/high weighted affine removal with literal high witnesses:** a degree-`D` refutation produces `f ∈ C_{k(D+1)}(F)` when `D≥2h+1`. | R02, R03, R05, R07, R08 | Helper to extract as paper `lem:hybrid`; [ordinary restriction audit](https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit) specializes the ledger of [mixed packing](https://kbr.is-a.dev/math-research/#mixed-packing-common-vanishing-learning). Check all companions, coefficient Booleanity, old axioms, and primitive replay. R15 supplies the literal witnesses when this lemma is applied; no kernel-existence assumption is hidden in its proof. |
| R17 | **`audit:ordinary-restriction-affine-family`: assemble the sufficient binary one-level exclusion / old-consequence contradiction.** | R14, R15, R16 | [Audit](https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit), paper finite-parameter `thm:affine`. Keep `h=3ℓ`, `B=k(D+1)`, and the board/degree conditions explicit. R15 and R16 split the audit's proof into reusable formalization tasks; they do not require proving the earlier alternative one-level exclusion first. |
| R18 | **`def:affine-clause-PC-system`: clause values in one fixed complete ENS family, and their prefix/value/companion upper bounds.** | R01, R06 | [Definition](https://kbr.is-a.dev/math-research/#affine-clause-PC-system). Supply the bridge from affine maps in the existing Lean clause files to degree-at-most-one polynomials. Include the empty clause value `1` without an empty-clause ENS block. |
| R19 | **`lem:binary-affine-zero-cover`.** | — (existing Lean) | [BinaryAffineZeroCover.lean](claims/BinaryAffineZeroCover.lean). Exact opposite fibers and translated halves; the separator is already an ambient premise literal. |
| R20 | **`lem:affine-clause-basis-compression`.** | R19 (shared clause definitions; existing Lean) | [AffineClauseCompression.lean](claims/AffineClauseCompression.lean). Equivalent width-`v+1` subclauses and finite-registry coefficient-slot bounds. Its use of R19's module is not a proof dependency on the separator theorem itself. |
| R21 | **`lem:binary-semantic-affine-cover`.** | R19, R20 (existing Lean) | [BinarySemanticAffineCover.lean](claims/BinarySemanticAffineCover.lean). Reuse one/three-step reduction, ≤2 auxiliaries, soundness, compression, and restriction. Integration into a shared finite source DAG is still part of R24, not already provided by the local derivation type. |
| R22 | **`lem:affine-clause-resolution-PC-degree`: complementary-parity resolution preserves `max(K,4h+1)`.** | R02, R05, R06, R18 | [Exact polynomial identities](https://kbr.is-a.dev/math-research/#affine-clause-resolution-PC-degree). Derive affine-pivot Booleanity through two; multiply completed lines rather than their earlier derivations. The two context lists may overlap. |
| R23 | **`lem:semantic-weakening-PC-degree`: weakening preserves `max(K,4h)`; tautological conclusions cost at most `2h+1`.** | R02, R06, R07, R18 | [Exact proof](https://kbr.is-a.dev/math-research/#semantic-weakening-PC-degree). Needs affine-span coefficient witnesses from R07; the existing semantic cover proof alone does not supply PC certificates. |
| R24 | **`thm:bit-PHP-affine-clause-PC-transfer`: actual usual-CNF proof to the complete one-level PC endpoint.** | R01, R02, R06, R18, R21, R22, R23 | [Full theorem and CNF bridge](https://kbr.is-a.dev/math-research/#bit-PHP-affine-clause-PC-transfer). Prove compact initial-value certificates through `2h+ℓ`, normalize rule conventions, prepend at most `binom(m,2)` compact initial nodes, and replay the finite DAG without a height factor. Keep the `3S+binom(m,2)` node bound, polynomial input inventory, and original axiom degrees. Conclusion: `D=max(2h+ℓ,4h+1)`. |
| R25 | **Publication parameter closure and final theorem `thm:publication-Res-parity-bit-PHP`.** | R17, R24 | [Steps 3–5 and conclusion](https://kbr.is-a.dev/math-research/#publication-Res-parity-bit-PHP-proof), paper §7. For arbitrary fixed real `K>0`, close ceilings/logarithms and eventual inequalities with `S≤n^K`, `M≤3n^K+n²+1`, `h=3ℓ`, `D=12ℓ+1`, `k=ceil(sqrt((n+1)ln(4M)))`, `B=k(D+1)=o(n)`. Infer contradiction and the quantified superpolynomial node bound. |

The two branches can proceed independently once their foundations are ready:

```text
R09 → R10 → R14 ────────────────────┐
R11 → R12 ────┘                    │
R13 → R15 ────────────────────┐    │
R07 → R08 → R16 ──────────────┴→ R17 ──┐
                                      ├→ R25
R19 → R20 → R21 ──┐                   │
R18 → R22, R23 ───┴→ R24 ────────────┘
```

The table, not this simplified sketch, specifies all prerequisites. R06 and
R19–R21 are already covered by existing Lean files; the rest are remaining
implementation/proof tasks, except for whatever exact interfaces Mathlib supplies.
After H, the next project-side foundational target is R01/R02, because ordinary-PC derivations and
completed-line multiplication are required by both branches and are not supplied
by our current semantic `ParityDerivation` type.

## Third-party boundary

**H:** for `s≥2` and `N≥2s-1`, every reduced `(s-2)` cycle in the chessboard
complex `Δ_{s,N}` over `𝔽₂` has a filling. This is the precise BLVZ consequence
used by R10. Keep the `s=2` augmentation case and coefficient field explicit.
An [existing-Lean coverage search](../research/results/lean_chessboard_coverage_20260915/README.md)
on 15 September 2026 located useful topology infrastructure but no matching
checked theorem; it was not an exhaustive global code audit.
The target is indexed as `third-party:BLVZ-chessboard-filling` and stated in
[third-party-claims/ChessboardFilling.lean](third-party-claims/ChessboardFilling.lean)
as `MathResearch.ThirdParty.ChessboardFilling : Prop`. This is a proposition
definition, not a theorem or an axiom. It introduces no `sorry`.
Until H is supplied by a checked theorem, R10 and downstream claims are not
unconditionally fully formalized. A temporary interface is not permission to
mark them complete.

### Exact interface

`ChessboardFace s N k` is a k-element finite set of cells in `Fin s × Fin N`
whose row and column projections are injective. `ChessboardChain s N k` is
the vector space of F₂ coefficient functions on those faces. Finite support is
automatic because the board is finite. Index k counts cells, so the associated
reduced simplicial degree is k−1; k=0 is the empty-face augmentation coordinate.

For k>0, the coefficient of a (k−1)-cell face τ in `chessboardBoundary c` is
the sum of `c σ` over k-cell faces σ containing τ. Incidence signs are all one
over F₂. The outgoing boundary at k=0 is defined to be zero. In particular,
the boundary of a vertex chain is its total coefficient on the empty face.

The target definition is:

```lean
∀ (s N : ℕ), 2 ≤ s → 2 * s - 1 ≤ N →
  ∀ c : ChessboardChain s N (s - 1), chessboardBoundary c = 0 →
    ∃ b : ChessboardChain s N s, chessboardBoundary b = c
```

This is a direct finite-chain formulation of the required homology vanishing.
Proving boundary-squared-zero and relating this representation to any chosen
homology API are still proof tasks; a formal statement alone does not supply
those facts. The s=2 case requires the reduced augmentation, not the claim that
every unaugmented vertex chain bounds. R10 will build its matching-moment
cycles in this representation and consume the supplied filling.

### Ordered route to H

This is a starting guide based on the paper's
[topology appendix](../publications/drafts/bit-php-resolution-over-parities/sections/08-topology.tex),
not an audited proof of every intermediate statement. Hxx are planning IDs;
extract/index individual dependency claims as their statements settle. Generic
finite-chain helpers may be shared with project claims. Reuse checked Mathlib
results when their exact hypotheses and conventions match.

| Order | Building block to establish | Direct prerequisites | Scope / boundary cases |
| --- | --- | --- | --- |
| H01 | Finite augmented chain API for downward-closed families of finite faces, specialized to chessboard matchings. | — | Verified in [AugmentedChains.lean](claims/AugmentedChains.lean): empty face, finite supported coefficient spaces, exact-face linear equivalence, and boundary linearity. H03 supplies the original-boundary bridge. |
| H02 | Boundary squared is zero. | H01 | Verified in [AugmentedBoundarySquared.lean](third-party-claims/AugmentedBoundarySquared.lean): insertion-pair cancellation over F₂, including edges-to-augmentation; H01 proves the outgoing empty-face boundary is zero. |
| H03 | Relabeling, transpose, and subcomplex inclusion preserve chains and boundaries. | H01, H02 | Verified in [AugmentedChainMaps.lean](claims/AugmentedChainMaps.lean): support-preserving injective maps, inclusions, inverse relabeling/transpose, and the all-degree original chessboard boundary bridge. These interfaces support later column-complement identifications. |
| H04 | Augmented cone/simplex contraction and exactness. | H01, H02 | Verified in [AugmentedCone.lean](claims/AugmentedCone.lean): an actual cone vertex supplies a contraction and exactness in every cell count, including augmentation. Do not treat a complex containing only the empty face as a nonempty cone. |
| H05 | Boundary of a simplex is reduced-acyclic below its top dimension. | H02, H04 | Verified in [SimplexBoundary.lean](third-party-claims/SimplexBoundary.lean): for b vertices, vanishing through b−3; the top degree b−2 is not covered. Keep b=1,2 and negative degree conventions explicit. |
| H06 | Finite cover double-complex construction and horizontal augmented-row exactness. | H01, H02, H03, H04 | Verified in [CoverDoubleComplex.lean](claims/CoverDoubleComplex.lean): finite supported double coefficients, commuting square-zero differentials, total differential squared zero, and explicit horizontal cone fillings in positive vertex count. H07 uses a direct finite chain chase rather than spectral-sequence machinery. |
| H07 | Homological cover lemma through degree q. | H02, H06 | Verified in [HomologicalCover.lean](third-party-claims/HomologicalCover.lean) by a direct finite double-chain induction. With n=q+2, require nerve exactness for k<n and intersection exactness for t+r≤n; conclude exactness for K at k<n. The top relevant intersection degree uses augmentation exactness, not connectivity. |
| H08 | First-row closed stars cover Δ(a,b), after arranging 2≤a≤b. | H01, H03, H04 | Verified in [ChessboardStarCover.lean](third-party-claims/ChessboardStarCover.lean), with cone exactness in H10: a matching avoiding the row extends into it; each star is a cone. Cases with ν=1 can be handled directly by nonemptiness. |
| H09 | Intersections of t≥2 distinct first-row stars identify with Δ(a−1,b−t). | H03, H08 | Verified in [ChessboardStarIntersections.lean](third-party-claims/ChessboardStarIntersections.lean), including chain equivalence and exactness transport. t=b gives only the empty face; singleton intersections remain cones. |
| H10 | The first-row star-cover nerve is the boundary of a (b−1)-simplex. | H08, H09 | Verified in [ChessboardStarNerve.lean](third-party-claims/ChessboardStarNerve.lean), including nerve equality and acyclicity via H05. Every proper subfamily has a common vertex; the full family does not. |
| H11 | [Verified arithmetic](claims/ChessboardParameterArithmetic.lean) and induction bounds for ν(a,b)=min(a,b,⌊(a+b+1)/3⌋). | — | For 2≤a≤b, ν≤b−1. For a nonempty t-fold intersection, t≥2, show ν(a−1,b−t)≥ν(a,b)−t+1. Treat negative required acyclicity degrees as vacuous, and use min(a,b) as a decreasing induction parameter after transposition. |
| H12 | Binary homological chessboard bound: Δ(a,b) is (ν(a,b)−2)-acyclic for a,b≥1. | H03, H04, H05, H07, H08, H09, H10, H11 | Verified in [ChessboardHomology.lean](third-party-claims/ChessboardHomology.lean): strong induction on the smaller dimension, explicit one-row augmentation, transpose, and cover assembly. Full binary homological bound; no homotopical connectivity claim. |
| H13 | Specialize the homological bound and discharge **H**. | H01, H02, H12 | N≥2s−1 gives ν(s,N)=s. Translate degree s−2 to (s−1)-cell cycles filled by s-cell chains, using precisely the interface in ChessboardFilling.lean. |

### Parallelizable branches

The route splits into three branches of one proof, not three alternative proofs
of H. H01–H03 provide shared finite-chain infrastructure; the arithmetic branch
can begin immediately without it.

| Branch | Steps | Shared prerequisites and work |
| --- | --- | --- |
| General homological tools | H04 → H05; H04 → H06 → H07 | Build cone contractions, simplex-boundary vanishing, and the homological cover lemma on H01–H03. H07 is likely the largest task. |
| Chessboard combinatorics | H08 → H09 → H10 | Use H01/H03 and the cone facts from H04 to prove star coverage, identify intersections, and identify the nerve. H05 supplies the nerve's vanishing when the branches are assembled. |
| Parameter arithmetic | H11 | Prove the ν inequalities and the decrease needed for induction; independent of the chain infrastructure. |

```text
H01–H03 → H04 → H05 ────────────────┐
             ├→ H06 → H07 ─────────┤
             └→ H08 → H09 → H10 ───┼→ H12 → H13 (= H)
                    H11 ───────────┘
```

The diagram shows the branch structure; the ordered table above retains the
complete direct prerequisites. Separate work can proceed once those shared
interfaces are fixed, with all three branches joining at H12 before H13
specializes the result to the required filling statement.

H12 is broader than H on purpose: intersections in the star cover can have
fewer columns than the narrow N≥2s−1 range allows. Merely applying H inductively
to each intersection would leave missing cases. A different constructive proof
may avoid H06/H07 or weaken H12; revise this route if that becomes advantageous.
The list is not a requirement to formalize a general homotopy theory.

For explicit reduced acyclicity conventions, use exactness on k-cell chains for
0≤k≤ν−1 to express vanishing in degrees −1 through ν−2. Do not encode negative
dimension bounds using truncated natural subtraction without handling ν=0/1
and the empty-face-only complex separately.

The local construction from matching marginals to cycles and from fillings back
to globally consistent moments remains our R10 obligation. Standard library
support for chains and linear algebra may be reused when available.

The selected chain does **not** need a separate imported Razborov degree lower
bound: normalized matching designs and the cube separator provide the required
contradiction. BIKPRS motivates the ENS methodology, but the paper proves the
specific clause simulation directly; its general Frege simulation need not be
formalized for this bit-PHP theorem. Third-party proof-system definitions are
used as the target specification, not silently assumed lower-bound results.

## Why other linked claims are not additional prerequisites

- `prop:matching-moment-homology-extension` and
  `thm:functional-PHP-stable-filtration` are earlier formulations of the same
  matching-extension mechanism. R09/R10 use the later completeness and
  arbitrary-row audits directly, including their proofs. Back-references do
  not create a dependency cycle or require repeating all three statements.
- `thm:transported-bit-consequence-filtration` provides a broader `J_k` package.
  The publication only needs its decoder-to-old-PC interface, R12, followed by
  R14. The full stable-class/annihilator extension theorem is avoidable.
- `thm:compact-bit-PHP-PC-degree` contains the decoder certificates used in R12,
  but its standalone lower bound and leveled-ENS extensions are not necessary.
- `lem:mixed-packing-common-vanishing-learning` and
  `lem:affine-common-vanishing-learning` also cover Boolean-point vanishing with
  Boolean residuals, and NS versions. R15 gives literal affine membership, so
  the paper's shorter literal-witness PC lemma R16 is sufficient. Do not claim
  those broader indexed lemmas are formalized by proving R16.
- The low-bin proof uses factor telescoping, not the retained-core optimality
  part of `thm:optimal-linear-core-factor-packing`. R08 states its legitimate
  no-core version directly.
- `lem:two-functional-row-state-interpolation` cites the elementary state
  reduction inside `thm:affine-column-state-normalizer`; its larger normalization
  and transfer theorem is not needed. R11 retains the actual reduction proof.
- `lem:cube-residual-dual-separation` is a replacement proof of the earlier
  row-linear quotient-injection result, not a proof that depends on that result.
- The earlier `thm:working-Res-parity-bit-PHP-size-lower-bound` and
  `audit:Res-parity-lower-bound-chain` are predecessor formulations of the final
  theorem. R25 composes the explicit chosen chain instead of proving the target
  by citing its earlier form.
- All-prime endpoints, accuracy-one improvements, `h=2ℓ` refinements, nonlinear
  source/profile work, full AC⁰[p]-Frege compilation, and finite computation
  fixtures are outside this route. `lem:mod-interpolation` is already formalized
  but is not a dependency of this publication proof.

## Completion boundaries

This is a planning artifact, not a correctness certification of the paper.
Read each precise source again when opening its formalization cycle, resolve
applicable correction links, and create the per-claim dependency/scope map.
The companion-degree discrepancy is relevant to R07: exact equality uses the
actual input degree and fresh variables; a loose ceiling only gives an upper
bound. Never infer a cofactor bound by subtracting an inflated degree budget.

Keep existing indexed claims distinct from extracted helpers and separately
indexed corollaries. Record any newly discovered mathematical gap in the
notebook's formalization-gaps section. Do not expand the target to the unrelated
main Frege research goal. This route itself supplies no new Lean formalization.
