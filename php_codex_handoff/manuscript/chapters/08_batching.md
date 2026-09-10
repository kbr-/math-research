<!-- Generated from ../latex/08_batching.tex. Do not silently edit this reading copy. -->

<a id="ch-batching"></a>

# 8. Nested spans and core--residual batches

> The original refutation can be replayed while previously learned inputs are reused. This removes chain length from the degree cost. Polynomial factor packing then allows the full spaces to be incomparable, provided suitable cores are nested and the remaining directions are inexpensive.

## A chain costs one block

<a id="thm-nested"></a>

### Theorem 8.1: Nested-span batch elimination

Let same-level blocks, fresh for the old system $\mathcal G$, have input spans $$V_1\subseteq V_2\subseteq\cdots\subseteq V_s.$$ If all inputs have degree at most $\delta$, a degree-$D$ augmented PC refutation yields a refutation of $\mathcal G$ of degree at most $$\boxed{B=D+(p-1)\delta.}$$ The bound is independent of the length of the chain and all fan-ins.

**Proof.** Fix the original degree-$D$ refutation $\pi$ and never replace it by an inflated proof. Process blocks in increasing order, maintaining derivations of the earlier inputs within degree $B$.

Choose an input $f=g_{a,j}$ of the current block. For every later block $b\ge a$, nesting gives constants $c_{b,i}$ with $f=\sum_i c_{b,i}g_{b,i}$. For a fixed $\alpha\ne0$, zero-specialize all earlier blocks; in every current or later block set $r_{b,1,i}=\alpha^{-1}c_{b,i}$ and other factor coefficients zero. Weight each specialized line of the original $\pi$ by $\chi_\alpha(f)$.

A current or later extension axiom becomes $\alpha^{-1}g_{b,i}(f^p-f)$, an old-field consequence within the weighted-line degree ceiling $B$. An earlier axiom becomes $\chi_\alpha(f)g_{b,i}$, where $g_{b,i}$ is already derived. Reuse its final polynomial and multiply it by the selector; the product degree is at most $B$ for every axiom line occurring in $\pi$. The earlier derivation itself is not multiplied. Old axioms, new field axioms, and inferences are handled by [Lemma 1.4](01_foundations.md#lem-substitution), [Lemma 1.5](01_foundations.md#lem-fieldreduction).

The transformed conclusion is $\chi_\alpha(f)$. Combining these derivations over $\alpha\ne0$ derives $f$ within $B$. Repeat for the current inputs and move on. The same original proof and the same ceiling $B$ are used at every learning stage.

Finally zero-specialize all new variables in $\pi$. Every extension axiom is now an already derived input. Reuse the derivations to get a base refutation within $B$. Unused axioms need no substitution certificate; a block absent from the used extension axioms can simply be zero-specialized. *End of proof.*

<a id="lem-nestedquotient"></a>

### Lemma 8.2: Nested modulo supplied base consequences

Let $H\subseteq k[y]_{\le\delta}$ be a vector space whose elements have supplied PC derivations from $\mathcal G$ within degree $c$. Suppose $$(V_1+H)/H\subseteq\cdots\subseteq(V_s+H)/H.$$ The batch can be eliminated within degree $$\boxed{B_H=\max\{c,D+(p-1)\delta,(p+1)\delta\}.}$$ If $c\le D$ and $D\ge2\delta$, this is $D+(p-1)\delta$.

**Proof.** A selected input now has $f=\sum_i c_{b,i}g_{b,i}+u_b$ with $u_b\in H$. The same first-factor specialization gives $$\chi_\alpha(f)E_{b,i}(y,\beta)
 =\alpha^{-1}g_{b,i}(f^p-f)
  +\alpha^{-1}\chi_\alpha(f)g_{b,i}u_b.$$ The first term is a field consequence, the second a multiple of an already derived $u_b$. Both have degree at most $(p+1)\delta$. Reuse their derivations within $B_H$; the rest of [Theorem 8.1](08_batching.md#thm-nested) is unchanged. The quotient here is a vector-space quotient backed by low-degree derivations, not the full ideal of the unsatisfiable base. *End of proof.*

<a id="cor-chaincharge"></a>

### Corollary 8.3: Global chain charge

Partition every level into nested chains $C$, with maximum input degree $\delta_C$. Eliminating in reverse level order yields $$\boxed{D_{\rm base}\le D+(p-1)\sum_C\delta_C.}$$ The quotient version uses the extra ceilings in [Lemma 8.2](08_batching.md#lem-nestedquotient). Literal equality of all spaces is the special case of a constant chain.

**Proof.** After later levels have been removed, a chosen chain is fresh for all other remaining axioms. Apply [Theorem 8.1](08_batching.md#thm-nested), treating those axioms as old. Scalar substitutions do not increase the degrees of surviving blocks. Add the increments. *End of proof.*

For example, $1{,}000$ strictly nested linear spaces over $\mathbb F_2$ at target degree $49$ cost degree $50$, rather than the per-block budget $1049$. This is a degree transformation; its proof length is not bounded here.

## Nested cores with incomparable full spaces

<a id="thm-cores"></a>

### Theorem 8.4: Core--residual batch elimination

For same-level input spaces $V_a$, suppose there are nested cores $$U_1\subseteq\cdots\subseteq U_s,\qquad U_a\subseteq V_a,$$ each generated in degree at most $\gamma$. Choose representatives $v_{a,1},\ldots,v_{a,r_a}\in V_a$ for a basis of $V_a/U_a$, with degrees at most $\eta_a$. Put $$T_a=\max\left\{1,\eta_a
 \left(\left\lceil\frac{(p-1)r_a}{h_a}\right\rceil-1\right)_+\right\},
 \quad T=\max_aT_a.$$ When $r_a=0$ take $\eta_a=0$. A degree-$D$ augmented PC refutation yields a base refutation of degree at most $$\boxed{B=TD+(p-1)\gamma.}$$ The full spaces $V_a$ need not be nested.

**Proof.** For one block, decompose $$g_{a,i}=u_{a,i}+\sum_\nu c_{i,\nu}v_{a,\nu},\qquad u_{a,i}\in U_a,$$ and define $Z_a=\prod_\nu(1-v_{a,\nu}^{p-1})$. By the packed coefficient construction, using the residual representatives rather than a basis of all inputs, there are substitutions $\beta_a(y)$ of degree at most $T_a$ making the common extension factor exactly $Z_a$. The representatives are constant linear combinations of the original tuple, so these are legitimate coefficients in its original input coordinates. Then <a id="eq-coreabsorb"></a>

$$\label{eq:coreabsorb}
 E_{a,i}(y,\beta_a)=g_{a,i}Z_a
 =u_{a,i}Z_a+(g_{a,i}-u_{a,i})Z_a,$$ and the last term belongs to $J_{\mathrm{fld}}$.

Keep the original refutation $\pi$. Process cores in increasing order. Assume the earlier cores and earlier specialized extension axioms have been derived within $B$. Select a core generator $f\in U_a$ of degree at most $\gamma$. For every $b\ge a$, $f\in V_b$, so choose constant coordinates of $f$ in that tuple. Substitute the residual polynomial coefficients in earlier blocks, and in every current or later block use the scalar first-factor coefficients making $1-\alpha^{-1}f$. Weight the image of every original line by $\chi_\alpha(f)$.

All substituted variables have degree at most $T$. Thus every transformed line has degree at most $TD+(p-1)\gamma$. Current and later extension images are old-field consequences by [Equation eq:selectorproduct](01_foundations.md#eq-selectorproduct). Earlier images are already derived and their final polynomials can be multiplied by the selector. Old axioms and field equations map to bounded-degree consequences. For an original multiplication step, the transformed predecessor has degree at most $T(D-1)+(p-1)\gamma$; multiplication by an image of degree at most $T$ stays within $B$. This explicitly validates the use of polynomial, rather than scalar, substitutions.

As before, the transformed conclusion derives $\chi_\alpha(f)$, and combining the nonzero field values derives $f$ within $B$. Learn generators of the core this way.

To finish the block, use [Equation eq:coreabsorb](08_batching.md#eq-coreabsorb). The polynomial $u_{a,i}$ is now derived and has degree at most $\gamma$. For an extension axiom actually used in $\pi$, $\deg E_{a,i}\le D$, hence $\deg(g_{a,i}Z_a)\le TD$. If $Z_a=0$ the image is zero. Otherwise the ordinary polynomial ring is a domain, so $\deg Z_a\le TD$. Therefore both $u_{a,i}Z_a$ and $(g_{a,i}-u_{a,i})Z_a$ have degree at most $TD+\gamma\le B$. The former is derived by reuse, the latter by bounded-degree field reduction. This derives the specialized extension image within the same ceiling.

Continue through all cores and finally substitute all residual coefficients into the original $\pi$. Every extension image has a supplied derivation and every inference is simulated within $B$, yielding the extension-free refutation. *End of proof.*

<a id="cor-cheapantichain"></a>

### Corollary 8.5: Cheap incomparable families

For affine-linear inputs, residual rank $r_a\le\lfloor2h_a/(p-1)\rfloor$ gives $T=1$. Thus nonzero affine cores cost only $p-1$ degrees per batch. For arbitrary nonlinear residual inputs, the stronger rank condition $r_a\le\lfloor h_a/(p-1)\rfloor$ also gives $T=1$, and the cost is $(p-1)\gamma$ regardless of their degrees.

**Proof.** In the affine case $\eta_a\le1$ and the ceiling in [Theorem 8.4](08_batching.md#thm-cores) is at most two. In the nonlinear case it is at most one, so every residual substitution is scalar. Apply the theorem. *End of proof.*

An example is $V_a=U+P_a$ with the same arbitrarily large affine core $U$ and different residual subspaces of dimension at most $2h$ over $\mathbb F_2$. The full spaces can form an arbitrarily large antichain, yet the entire batch costs at most $D+1$. At $h=16,D=49$, residual rank $32$ is allowed while full-group interactions are already active.

<a id="lem-corequotient"></a>

### Lemma 8.6: Affine cores modulo base consequences

Let $H\subseteq k[y]_{\le1}$ have supplied derivations within degree $c$. Form affine input spaces modulo $H$, and suppose they have nested cores and residual representatives as above. For $D\ge2$ a sufficient budget is $$\boxed{\max\{c,TD+p-1\}.}$$

**Proof.** Lift each quotient core generator $f$ to an affine representative. In a later block write $f=\sum_i c_i g_i+u$ with $u\in H$. The weighted image of a selected companion is the sum of $\alpha^{-1}g_i(f^p-f)$ and $\alpha^{-1}\chi_\alpha(f)g_i u$. Their degrees are at most $p+1\le TD+p-1$; the second uses the supplied derivation of $u$. For residual absorption, the discrepancy between an input and its residual combination belongs to the learned core plus $H$, so it is already derivable within the stated ceiling. The rest is [Theorem 8.4](08_batching.md#thm-cores). *End of proof.*

For PHP one may take $H=\mathop{\mathrm{span}}\{\rho_i-1\}$, whose generators are degree-one axioms. Larger supplied consequence spaces are allowed only when their derivations are genuinely available within the asserted degree.

<a id="lem-maxcores"></a>

### Lemma 8.7: Maximal cores for a fixed order

For an order $a_1,\ldots,a_t$, the maximal possible nested cores are $$U_{a_i}=\bigcap_{j=i}^tV_{a_j}.$$ Every other nested core choice satisfying $U_{a_i}\subseteq V_{a_i}$ is contained in these suffix intersections.

**Proof.** If $U_{a_i}$ is nested, it lies in $U_{a_j}\subseteq V_{a_j}$ for every $j\ge i$, so it is contained in the intersection. The suffix intersections themselves form an increasing chain and lie in the corresponding spaces. *End of proof.*

<a id="scope"></a>

##### Scope

A batch transforms a degree budget as $d\mapsto T_{\mathcal B}d+(p-1)\gamma_{\mathcal B}$. For $T_{\mathcal B}=1$, charges add; otherwise they compose as affine functions and can multiply earlier budgets. A constant number of levels with polylogarithmic $T$ and core degree would be affordable. No such uniform decomposition was proved. The next chapter determines the exact optimum of this criterion for affine data and shows it can exceed the PHP budget.
