<!-- Generated from ../latex/10_route.tex. Do not silently edit this reading copy. -->

<a id="ch-route"></a>

# 10. The remaining route to the payoff

> The payoff is a superpolynomial size lower bound for ordinary PHP in $AC^{0}[p]$-Frege, at every fixed depth and fixed prime. The static decomposition work does not establish that theorem. This chapter isolates the published inputs, gives the conditional final implication, and ranks the remaining obligations.

## Published inputs, not new proofs

<a id="imp-php"></a>

### Imported input 10.1: The PHP algebraic degree budget

Razborov's polynomial-calculus lower bound for the algebraic pigeonhole principle is at least $n/2+1$ over every field [Razborov](../../references/README.md#razborov). Krajíček records degree-$n/2$ designs for the Boolean PHP system containing both row and column exclusions [Krajicek Lemma 4.1](../../references/README.md#krajicek). Deleting the extra row exclusions preserves these lower bounds and designs whenever the remaining equations coincide with [Equation eq:base](01_foundations.md#eq-base).

The exact identification of the polynomial encoding is an application obligation, not something to obtain merely by recognizing the name "PHP." The uses of this imported input in the manuscript, including the residual-system argument for affine rigidity, are explicitly subject to that match. For the sufficient contradiction calculations, write $b_n=\lfloor n/2\rfloor$.

<a id="imp-simulation"></a>

### Imported input 10.2: The Frege-to-ENS simulation

For fixed depth $\ell$ and a size-$s$ bounded-depth modular-counting Frege refutation of the appropriate Boolean polynomial axioms, the BIKPRS simulation produces a leveled ENS system with $M=s^{O(1)}$ companions, $\ell+O(1)$ levels, and an NS refutation of degree $$D\le (O(1)+\log s)(h+1)^{O(\ell)}.$$ The accuracy $h$ is a parameter. For polynomial $s$, taking $h=O(\log n)$ gives polylogarithmic $D$. This is the published simulation, cited through [Krajicek Theorem 5.2](../../references/README.md#krajicek) and [BIKPRS](../../references/README.md#bikprs), not a result proved here.

The earlier informal regime $d=\Theta(\log s)$ was too narrow as a substitute for the full simulation budget. The actual growing degree above, including its depth dependence, must be covered.

## The exact conditional implication

<a id="thm-conditionalpayoff"></a>

### Theorem 10.3: A sufficient payoff theorem

Fix a prime $p$. Assume the following three statements.

1.  An ordinary-PHP depth-$\ell$, size-$n^K$ refutation can be converted to a refutation of [Equation eq:base](01_foundations.md#eq-base) with polynomial size and bounded depth overhead.

2.  Imported Inputs [Imported input 10.1](10_route.md#imp-php) and [Imported input 10.2](10_route.md#imp-simulation) apply to that exact encoding.

3.  Every translated NS certificate arising from those hypothetical proofs has an elimination to a base PC refutation of degree at most $b_n$, for all sufficiently large $n$ (with the threshold permitted to depend on $p,\ell,K$).

Then ordinary PHP has superpolynomial $AC^{0}[p]$-Frege proof size at every fixed depth: $$\forall\ell,K\ \exists n_0\ \forall n\ge n_0:
 \operatorname{Size}_{\ell,p}(\mathrm{PHP}_n)>n^K.$$

**Proof.** Fix $\ell,K$ and suppose such a size bound holds for some sufficiently large $n$. The first assumption converts the proof to the exact Boolean polynomial system. The simulation gives its augmented NS certificate in the required parameter range. NS certificates are PC refutations of no larger degree by [Lemma 1.2](01_foundations.md#lem-duality). The third assumption eliminates the relevant extension data and produces a base PC refutation within $b_n$, contradicting Imported Input [Imported input 10.1](10_route.md#imp-php). Since $\ell,K$ were arbitrary, the displayed quantifiers follow. *End of proof.*

Equivalently, instead of an elimination one could construct a normalized degree-$D$ joint design for every relevant translated system. Applying it to $1=\sum_fq_ff$ gives $1=0$. Preserving a prescribed old functional, finding a universal specialization, or handling all degree-$D$ PC proofs are stronger requirements than this final implication needs.

## Remaining obligations, riskiest first

<a id="refutation-sensitive-elimination-beyond-static-input-spaces"></a>

### 1. Refutation-sensitive elimination beyond static input spaces

**Highest risk.** Prove that each relevant translated NS certificate can be converted to a base PC refutation at degree at most $b_n$, or construct a suitable joint design directly. Existing sufficient costs include $$D+(p-1)\sum_a\delta_a,\qquad
 D+(p-1)\sum_C\delta_C,$$ and compositions of $d\mapsto T_{\mathcal B}d+(p-1)\gamma_{\mathcal B}$. None is uniformly affordable on all admissible data. [Theorem 9.6](09_decomposition.md#thm-spreadcost) proves that optimizing the current static affine criterion cannot by itself repair this.

The missing theorem must use information not captured by that criterion: which extension axioms actually occur with nonzero cofactors, the organization of the translated certificate, nonlinear PHP consequences, or another jointly consistent functional construction. The spread family is not a refutation, so it leaves these possibilities open.

A precise sufficient target is $$\pi:\mathcal F_n\cup\mathcal E\cup\mathcal R\vdash_D^{\mathrm{NS}}1
 \quad\Longrightarrow\quad
 \mathcal F_n\vdash_{B(\pi)}^{\mathrm{PC}}1,\qquad B(\pi)\le b_n,$$ for the actual simulation outputs under consideration. A bound polynomial in $D,h,\log M$, with exponent depending on fixed depth and $p$, would suffice. It is a proposed sufficient form, not a proved estimate. Any bound below the linear threshold is enough.

<a id="coverage-of-the-real-simulation-output"></a>

### 2. Coverage of the real simulation output

**High risk.** Establish that the elimination's hypotheses hold for the whole output of the published simulation, with nonlinear inputs, all companions, prior-level dependencies, and new field equations. General ENS syntax does not guarantee a cheap chain decomposition, small residual ranks, small shared-feature sets, or special affine-inverse tuples.

A structural theorem for translated NS certificates could settle this together with item 1. We need not eliminate every arbitrary extension system in the strongest PC sense if restricting to the translated NS certificates makes the task easier. The quantifier is "for each relevant certificate, there exists a valid affordable transformation," not "every imaginable auxiliary family has a small static decomposition."

<a id="audit-the-working-proof-transformations"></a>

### 3. Audit the working proof transformations

**Medium technical risk; logically prior to relying on them.** The current elimination and batching proofs should be independently checked for active-axiom degree bounds, freshness after reverse-level elimination, weighting of inference rules, reuse of final polynomials, and all field-reduction certificates. In the consequence-quotient variants, every relation used to create a span inclusion must have a genuinely available derivation within the budget.

The recorded primitive-PC checks support finite instances, but do not constitute a formal verification of the general statements or their novelty. This audit is distinct from discovering the missing compression theorem.

<a id="the-ordinary-php-encoding-transfer"></a>

### 4. The ordinary-PHP encoding transfer

**Lower risk, but necessary.** Our row axiom is $\sum_jx_{ij}=1\pmod p$; the ordinary row clause says some $x_{ij}$ is true. On Boolean inputs the former implies the latter, but the bounded-depth proof of that implication, with polynomial overhead, must be written in the chosen Frege presentation.

Only the direction from a short ordinary-PHP refutation to a short refutation of our stronger row-hypothesis system is needed. The converse need not hold. Row exclusion must not be silently added to our working base system; invoking a literature encoding equivalence that uses it is not automatically the required transfer.

<a id="constants-degree-losses-and-all-polynomial-exponents"></a>

### 5. Constants, degree losses, and all polynomial exponents

**Final parameter check.** For each fixed $p,\ell,K$, track the proof-size overhead, number of companion polynomials, accuracy, level count, and every elimination degree loss. The degree theorem must hold for the growing polylogarithmic simulation degree, not just $d=2$, one block count, or one exponent $K$.

Results restricted to $p>n$ cannot establish the fixed-$p$ asymptotic goal. A result for one selected polynomial proof bound is not yet superpolynomial. Once all hypotheses of [Theorem 10.3](10_route.md#thm-conditionalpayoff) are supplied, the last contradiction is straightforward.

## What no longer needs to be the main target

The exact erosion formula, a stronger generic survival threshold, and survival-until-complete-dimension-exhaustion are not necessary separate objectives for the current PC-elimination route. Generic linear survival has a proved range in the non-Boolean branch, but the route may bypass it entirely. Likewise, one-block feasibility is not the decisive remaining issue: there are multiple exact constructions and a compatible additive elimination. The central unknown is the *total affordable cost for the complete relevant certificate*.

<a id="status"></a>

##### Status

**Current research endpoint.** The decomposition has been solved within the stated affine criterion and can be too expensive even at its optimum. The next substantive advance must exploit the refutation or richer PHP algebra, rather than search for a better ordering of those same affine spaces. This is the remaining route, not an announcement that the payoff theorem has been proved.
