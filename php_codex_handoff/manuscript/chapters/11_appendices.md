<!-- Generated from ../latex/11_appendices.tex. Do not silently edit this reading copy. -->

<a id="app-ledger"></a>

# A. Corrections, superseded claims, and scope

This ledger preserves the changes of position made in the conversation. It is not a list of additional theorems asserted without proof.

  Earlier formulation                                                     Retained conclusion
  ----------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Koszul vanishing for every $j<n$.                                       False. [Lemma 2.1](02_graded.md#lem-koszul-counter) gives a field-independent counterexample at $n=4,j=3$. The proved replacement is $2j-1\le n$ in [Corollary 2.3](02_graded.md#cor-koszul).
  The initial Hilbert formula holds for every $d<n$.                      Only the corrected low-degree range is proved here. An earlier reported computation at $n=5,d=4$ over $\mathbb F_{1009}$ gave $3150$ rather than $3125$; it is retained as a historical observation, not a reverified theorem or a step in a proof.
  A sharp generic exhaustion threshold was settled.                       The proposed survival-until-exhaustion law and $\Theta(n^2/d)$ threshold were not proved. The proved generic range is $t\le n-2d+1$.
  Positive dimension should establish affine feasibility.                 False for a distinguished vector. [Lemma 2.5](02_graded.md#lem-weakcount) leaves positive dimension under many arbitrary restrictions, while [Lemma 2.10](02_graded.md#lem-linearobstructions) kills $z$ or $z^2$ with one or two.
  Lemma B is simply the final missing lemma for Frege.                    The bridge from generic linear restrictions to complete leveled extension systems was not established. Booleanity, admissibility, the correct growing degree, and encoding transfer must be accounted for.
  Every relevant scalar specialization should work.                       False already for input tuple $(1)$ at the all-zero specialization. The needed quantifier is existential specialization, or directly existential joint functional.
  A nonzero generic minor handles adversarial finite-field families.      It need not meet a constrained coefficient family. Nonzero polynomials can vanish on all of a finite set of permitted points. The generic theorem does provide one explicit good field-rational point.
  All input information can be conditioned on cheaply.                    The shared-feature constructions have explicit feature-degree cost; conditioning on all PHP columns costs $n$. The empty-row support barrier shows why that pointwise requirement can be too strong.
  One polynomial substitution should handle every block at low degree.    Independent-input and bounded-certificate barriers force large selector degree in relevant regimes. These are representational barriers, not obstructions to every joint functional.
  Independent single-block moment corrections should add to a solution.   Full-group interactions can violate mixed equations. The constant two-block example shows the failure. Supported corrections and PC elimination later give different valid finite-block constructions.
  The mixed hierarchy is now solved.                                      Its equations are a sufficient open construction, not a proved universally feasible system. Later results do not establish every restricted component ansatz.
  The $2^s$ moment-preserving cost must be inherent.                      Not proved, and the additive PC elimination improves that bound. The earlier exponential expression is one sufficient construction's cost only.
  Local interaction depth or sparse block interactions should suffice.    The prefix certificate has adjacent-pair interactions along a path but collapses NS degree. Plain old designs do not prevent cumulative propagation.
  High ordinary-design degree and high PC degree are interchangeable.     They are not. Pebbling bases can have high NS degree but PC degree at most three. The stronger closure must be assumed or proved.
  A PC-based single-block output retains PC closure automatically.        The intermediate functional lemma produces an ordinary design only. The later proof-elimination theorem composes actual PC refutations and avoids assuming this output property.
  Pairwise incomparability alone makes a family expensive.                Not under all our bounds. Low-rank residuals around nested cores can handle arbitrarily large antichains cheaply.
  A better ordering must yield an affordable decomposition.               Ordering and the current affine cost criterion are exactly optimized. The spread family still has optimum $D+(p-1)n>n/2$.
  That criterion's optimum lower-bounds all elimination methods.          No. It optimizes a specified sufficient bound; it does not prove intrinsic extension hardness, nor exhibit a relevant translated refutation using the spread family.

## Relation to the initial uploaded report

The initial report motivated the research with a counting/survival split and the distinction between a partial-matching ring and the column-only ring. The independent work here corrected the proposed Koszul range and eventually moved from the non-Boolean generic problem to Boolean extension elimination. Older claims in that report about exact erosion laws, functional-PHP certificates, or auxiliary circuit barriers have not been silently recast as proved findings of this manuscript. Their proofs were not developed in this independent sequence. In particular, a statement from the stronger partial-matching ring is not imported into the weaker column-only ring by a change of notation.

## A useful extra consequence of the generic proof

The generic rank calculation has a Hilbert-series byproduct. At the column-sum point of [Lemma 2.7](02_graded.md#lem-special-columns), the $n+t$ linear forms have vanishing positive Koszul homology through degree $d$. Their quotient therefore has degree-$d$ dimension $$[u^d](1+nu)^n(1-u)^t.$$ The maximal-rank argument in [Theorem 2.8](02_graded.md#thm-generic) shows that this is also the generic degree-$d$ dimension. Thus the relation matrix rank in that proof is $$\dim_k S_d-[u^d](1+nu)^n(1-u)^t.$$ This is a truncated low-degree statement in the non-Boolean ring under $t+2d-1\le n$, not the original all-range erosion claim.

<a id="app-computations"></a>

# B. Computational record and reproducibility

The eleven archives below were available in the active runtime when this manuscript was prepared. Their filenames and internal notes were inventoried; the historical suites were **not rerun merely to prepare this PDF**. Counts below are the results reported in the conversation and archived outputs, not newly performed research computations. The companion download preserves the archives unchanged and includes a SHA-256 manifest.

All numerical checks described in the conversation use exact finite-field arithmetic, not floating-point rank tests. Many checks are identities on satisfiable finite domains. Those are useful implementation checks but do not establish feasibility of the full unsatisfiable PHP system. Primitive-proof verifiers establish correctness of their finite output proofs, not a theorem for all parameter values.

  ID    Archive                                        Recorded scope
  ----- ---------------------------------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  A01   `annihilating_functional_checks.zip`           30 feasible finite-field instances, four infeasible controls, and three fixed-pivot determinant-chart checks. Generic non-Boolean functional construction only.
  A02   `ens_lifting_checks.zip`                       46 reweighted-lifting cases over $\mathbb F_2,\mathbb F_3,\mathbb F_5$; 732 active companions and 26,988 multiplier tests. Includes moment witnesses and revisiting uncommitted blocks.
  A03   `factor_packing_lift_checks.zip`               76 cases over four primes; 125,706 companion/assignment checks and 1,824 multiplier-moment checks. Includes 36 independent-input sharpness controls. Does not test the whole hybrid theorem.
  A04   `shared_conditioning_packing_checks.zip`       48 cases, 1,536 blocks through four levels. Finite-domain tests of shared features, whole-column conditioning, and prior-level dependence; not full PHP designs.
  A05   `base_aware_lifting_checks.zip`                18 cases over three primes, 576 blocks through four levels; 3,079,296 companion/assignment checks and 9,216 moment checks. Most cases include rows with several ones but row sum one modulo $p$.
  A06   `joint_moment_lifting_checks.zip`              42 cases, 126 blocks, 396 companions, 24,654 annihilation checks. Twelve cases use unsatisfiable Horn-chain bases with truncated designs. Includes a boundary failure without mixed moments.
  A07   `two_block_lifting_checks.zip`                 23 characteristic-two cases; 30,063 cofactor tests and 476 explicit complete-group checks. Four unsatisfiable-base cases have constant-input blocks. The odd-prime extension is not exercised.
  A08   `batch_lifting_attack_checks.zip`              Formal prefix-certificate checks in 16 cases over four primes, with 32 term-deletion controls; further checks on 8,192 assignments and 393,216 step identities. Does not verify the imported pebbling lower bound or the PC-based lifting theorem.
  A09   `nested_batch_elimination_checks.zip`          14 proof-transformation cases over three primes; 4,500 source and 9,670 transformed primitive-PC lines, including 328 input reuses. Synthetic propagation bases, not PHP. The consequence-quotient variant is not tested.
  A10   `core_residual_batch_elimination_checks.zip`   Seven exact incomparable-space cases over $\mathbb F_2,\mathbb F_3$; 6,440 source lines, 1,917 extension-free output lines, 26,298 mapped-line identities. Tests $T=1$, not every nonlinear parameter range or quotient variant.
  A11   `decomposition_optimization_checks.zip`        16 cases; 34,796 graph-subspace pairs, 17,604 small-family orderings, 12 quotient-rank checks, and subset dynamic programs on at most eight blocks. Does not test affine-consequence rigidity or a PHP/ENS refutation.

A separate turn checked the elementary selector identities over five primes in 28 exact cases, all passing, but did not produce another archived general proof transformation. Identity checks are not substitutes for the elimination proof.

## What is bundled with the manuscript

The source supplement contains the LaTeX files for this document, a file manifest with hashes and archive contents, the eleven historical ZIP files, and the compilation-turn timing record. No font files are included. Each original archive retains its own runnable code, reported results, and scope statement; nested archives avoid accidentally changing the original test packages.

## Timing methodology

For this compilation turn, the initial timestamp was taken before reading the PDF-creation instructions. Tool-call windows, marked reading/review intervals, and local program runtimes were logged separately where observable. Designated reading includes interpretation; it is not a physiological or model-internal reading timer. Pure network latency and pure reasoning time are not exposed, so those are not invented. A residual interval contains manuscript planning, mathematical organization, writing, and unisolated overhead. The final chat response reports the measured totals through the last timestamp; answer generation and delivery after that timestamp are not included.

Parallel renderer runtimes are reported as elapsed batch time, not the sum of overlapping worker durations. The archived research-suite runtimes from earlier turns are historical metadata and are not added to this turn's computation time.

<a id="app-map"></a>

# C. Dependency map and compact budget reference

## Logical dependencies

**Non-Boolean branch.** Active-row Koszul vanishing gives the initial Hilbert function and weak dimension count. Applied after column-sum restrictions, it also gives exactness, maximal relation rank, and the generic determinant witness. This branch does not imply Boolean extension survival without a separate bridge.

**Elimination branch.** Field selectors, degree-bounded reductions, and PC reuse give one-block and additive elimination. Replaying the original proof gives nested-span batches; polynomial factor packing enlarges them to core--residual batches. Exact affine optimization supplies both an algorithm for that bound and the spread-family limitation.

**Payoff branch.** An ordinary-PHP encoding transfer feeds the published Frege-to-ENS simulation. The missing *affordable refutation-sensitive elimination* must then produce a base PC contradiction. That elimination theorem is not established here.

## Budget reference

  Construction                               Sufficient budget or proved range
  ------------------------------------------ ------------------------------------------------------------------------------------------------------------------------
  Corrected item (a)                         $2d-1\le n$; $\dim\overline B_d=\binom ndn^d$.
  Generic non-Boolean restrictions           $t+2d-1\le n$.
  Reweight a level                           $D+\sum_ac_a(D)$, with $c_a$ from [Equation eq:repaircost](03_reweighting.md#eq-repaircost).
  Packed substitutions                       $TD$, with $T$ from [Lemma 4.2](04_packing.md#lem-packedlift).
  Shared features across levels              $D+(p-1)\sum_\nu\deg f_\nu$.
  Shared columns across levels               $D+q$ for $q$ determining columns.
  Packing plus shared conditioning           $TD+\kappa$.
  Affine-inverse row/column tuples           $D$, under the exact matrix hypotheses.
  Degree-window joint moments, $p=2$         $D$ if all active $e_i>D-h$.
  Supported one-block moments, $p=2$         $\max\{D,2D-h(\delta+2)\}$.
  Supported one-block moments, general $p$   $\Phi_{p,\delta}(D)$ in [Lemma 6.8](06_moments.md#lem-supported-p).
  PC-based one-block functional              $\Psi_{p,\delta}(D)$ in [Lemma 7.5](07_elimination.md#lem-pcbased); stronger input invariant, ordinary output.
  Additive PC elimination                    $D+(p-1)\sum_a\delta_a$.
  One nested-span chain                      $D+(p-1)\delta$.
  Nested cores plus residual directions      $TD+(p-1)\gamma$.
  Exact affine batch criterion               $C_S(d)$ of [Lemma 9.2](09_decomposition.md#lem-batchcost), composed by [Lemma 9.3](09_decomposition.md#lem-subsetdp).
  Spread-family optimum in that criterion    $\min\{D+(p-1)n,T(r)D\}$, eventually $D+(p-1)n$.

These bounds have different hypotheses. Retain the original axiom degrees and the specified input/output invariants; a bound for a subclass is not a uniform theorem for every simulation output.
