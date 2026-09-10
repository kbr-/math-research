<!-- Generated from ../latex/09_decomposition.tex. Do not silently edit this reading copy. -->

<a id="ch-decomposition"></a>

# 9. Exact decomposition and a sharp limitation

> For affine inputs, both the ordering and the optimal partition cost of the current core--residual rule can be determined exactly. Nevertheless, a polynomial-size admissible family has optimum $D+(p-1)n$, exceeding the available budget. This is a limitation of the rule, not of every elimination method.

## Ordering is solved

Assume one level, common accuracy $h$, and affine input spaces $V_1,\ldots,V_s$ over $\mathbb F_p$. Supplied affine consequences can first be quotiented out. Zero spaces are discarded; spaces containing a nonzero constant are handled by the separate free-elimination rule.

For a family $S$ and an order $a_1,\ldots,a_t$, define its residual radius $$R(a_1,\ldots,a_t)=\max_i\left[
 \dim V_{a_i}-\dim\left(\bigcap_{j=i}^tV_{a_j}\right)\right].$$ Let $R_*(S)$ be the minimum over orders.

<a id="lem-ordering"></a>

### Lemma 9.1: Optimal order and exact obstruction formula

Ordering by nondecreasing dimension minimizes the residual radius. Moreover, $$\boxed{R_*(S)=\max_{\varnothing\ne A\subseteq S}
 \left[\min_{a\in A}\dim V_a-\dim\left(\bigcap_{a\in A}V_a\right)\right].}$$

**Proof.** For the exchange argument, consider adjacent spaces $A,B$ with $\dim A\ge\dim B$, and let $W$ be the intersection of the spaces after them. Before swapping, the residual of $A$ is $\dim A-\dim(A\cap B\cap W)$. After swapping the two affected residuals are $$\dim B-\dim(A\cap B\cap W),\qquad
 \dim A-\dim(A\cap W),$$ both at most that previous residual. All other terms are unchanged. Removing inversions therefore yields a nondecreasing-dimension optimum.

For the formula's lower bound, in any order take the first member of a nonempty subfamily $A$. Its suffix contains all of $A$, so its residual is at least the bracketed quantity. For the upper bound, repeatedly remove a smallest-dimensional remaining space. At each step its residual is exactly the bracketed quantity for the remaining family, hence at most the maximum over all subfamilies. *End of proof.*

## Optimize the whole level

Put $$T(r)=\max\left\{1,\left\lceil\frac{(p-1)r}{h}\right\rceil-1\right\}.$$

<a id="lem-batchcost"></a>

### Lemma 9.2: The optimal certified batch cost

Within the affine core--residual criterion, the best budget for a nonempty batch $S$ acting on degree $d$ is $$\boxed{C_S(d)=\min\{T(R_*(S))d+(p-1),\
                       T(\max_{a\in S}\dim V_a)d\}.}$$ The alternatives are maximal nonzero cores and all-zero cores. This optimizes the stated sufficient bound, not all possible proof transformations.

**Proof.** Every nonzero affine core has generator degree one and therefore charge $p-1$. Maximal suffix cores minimize every residual for a fixed order, and [Lemma 9.1](09_decomposition.md#lem-ordering) minimizes their maximum. Shrinking some but not all cores cannot lower that charge and cannot improve the residual maximum. If all cores are zero, there is no core charge but each residual rank is the whole input rank. These give the two displayed alternatives. *End of proof.*

<a id="lem-subsetdp"></a>

### Lemma 9.3: Exact subset optimization

The best degree bound supplied by this rule over all partitions and batch orders of a family $S$ is given by $$\boxed{B(\varnothing)=D,\qquad
 B(S)=\min_{\varnothing\ne A\subseteq S}C_A(B(S\setminus A)).}$$ This is an exact finite algorithm, generally exponential in the number of blocks.

**Proof.** Choose the last eliminated batch $A$. Every $C_A$ is nondecreasing, so among eliminations of the preceding blocks only the smallest resulting degree can improve the final answer. Induction on $|S|$ proves the recurrence. Conversely, every choice in the recurrence corresponds to a partition and batch order, establishing attainability of its certified value. *End of proof.*

## An admissible family with unaffordable optimum

Let $m=n+1$ and $$H_0=\mathop{\mathrm{span}}_{\mathbb F_p}\{\rho_i-1:i\in[n+1]\},\qquad
 W=\mathop{\mathrm{span}}_{\mathbb F_p}\{x_{ij}:i\in[n+1],j<n\}.$$

<a id="lem-coordinatequotient"></a>

### Lemma 9.4: A large affine coordinate space survives the row quotient

The $n^2-1$ displayed coordinate variables, together with one, are linearly independent modulo $H_0$.

**Proof.** If $c+w=\sum_i a_i(\rho_i-1)$ with $w\in W$, compare coefficients of $x_{i,n}$: every $a_i=0$. Then $c+w=0$ forces $c=0$ and every coefficient of $w$ to be zero. *End of proof.*

<a id="lem-spread"></a>

### Lemma 9.5: A polynomial-size spread of input spaces

Set $$d=\lceil\log_p n\rceil,\qquad
 q=\left\lfloor\frac{n^2-1}{2d}\right\rfloor,\qquad r=qd,$$ for $n$ large enough that $d,q\ge1$. There exist $n$ admissible same-level input spaces of dimension $r$ in the original PHP variables, pairwise intersecting only at zero, even modulo $H_0$.

**Proof.** Let $K=\mathbb F_{p^d}$ and choose $n$ distinct scalars $\alpha\in K$. Embed the $2r$-dimensional $\mathbb F_p$-space $K^q\oplus K^q$ into $W$. Define $$V_\alpha=\{(u,\alpha u):u\in K^q\}.$$ Each has $\mathbb F_p$-dimension $r$. If $(u,\alpha u)=(v,\beta v)$ and $\alpha\ne\beta$, then $u=v$ and $(\alpha-\beta)u=0$, forcing $u=0$. [Lemma 9.4](09_decomposition.md#lem-coordinatequotient) preserves this intersection property after the row quotient.

Choose a basis of each space as its homogeneous linear input tuple and introduce a fresh accuracy-$h$ block with all its companions. This is valid ENS syntax. There are $n$ blocks, $nr=O(n^3)$ companions, and $hnr$ new variables. Each companion has original degree $2h+1$. *End of proof.*

<a id="thm-spreadcost"></a>

### Theorem 9.6: The exact best decomposition bound for the spread

For the family in [Lemma 9.5](09_decomposition.md#lem-spread), the best degree bound supplied by the current affine criterion is $$\boxed{B_{\rm criterion}^{\rm opt}
       =\min\{D+(p-1)n,T(r)D\}.}$$ For fixed $p$, $h=\Theta(\log n)$, and $2h+1\le D=\operatorname{polylog}n$, this equals $D+(p-1)n>n/2$ for all sufficiently large $n$.

**Proof.** In any batch of at least two spaces, the first core is contained in the intersection with a later space and is therefore zero. Its residual already has rank $r$, so $R_*=r$ for every such batch. The best multi-block cost is $T(r)d$. A singleton offers $\min\{d+p-1,T(r)d\}$.

If every singleton uses a full core, the cost is $D+(p-1)n$. Any multi-block batch, or any all-zero-core singleton, incurs a multiplicative step $T(r)$ and therefore costs at least $T(r)D$ overall; all other steps are nondecreasing. One all-zero-core batch attains this latter bound. This proves the exact minimum over all allowed decompositions.

For fixed $p$, $r=\Theta(n^2)$ and $T(r)=\Theta(n^2/\log n)$. Since $D\ge2h+1=\Theta(\log n)$, $T(r)D=\Omega(n^2)$, while $D+(p-1)n=\Theta(n)$. The first branch of the minimum eventually wins and exceeds $n/2$. *End of proof.*

<a id="example-9-7"></a>

### Example 9.7: A numerical instance of the criterion

At $p=2,n=256,h=8,D=25$, the construction has $r=32760$ and $T(r)=4094$. The two optimized certified costs are $281$ and $102350$, while the available target budget is $128$. This is an illustration of the degree-bound criterion, not a claimed ENS refutation or a fully matched Frege-simulation instance.

## Low-degree affine consequences do not improve this quotient

<a id="thm-rigidity"></a>

### Theorem 9.8: Affine-consequence rigidity, conditional on the PHP degree input

Using Imported Input [Imported input 10.1](10_route.md#imp-php) for the base and the residual PHP systems, for $1\le b\le\lfloor(n-2)/2\rfloor$, $$\boxed{\mathcal C_{b}(\mathcal F_n)\cap\mathbb F_p[x]_{\le1}=H_0.}$$

**Proof.** Let $f=a_0+\sum_{i,j}a_{ij}x_{ij}$ have a degree-$b$ PC derivation. Fix distinct rows $i,i'$ and columns $j,k$. Restrict the derivation to the partial matching $i\mapsto j,i'\mapsto k$, and to the matching $i\mapsto k,i'\mapsto j$. Both leave exactly the same labeled residual PHP system. The two restricted affine polynomials differ by the constant $$a_{ij}+a_{i'k}-a_{ik}-a_{i'j}.$$ A nonzero difference would give a degree-$b$ residual refutation by subtraction and scalar division, forbidden by the residual lower bound. Thus all coefficient rectangles vanish, which implies $a_{ij}=u_i+v_j$ (fix one row and column to construct $u_i,v_j$).

Subtract a combination of row axioms. It remains to consider a derived polynomial $f'=c+\sum_jv_j\sigma_j$, where $\sigma_j=\sum_i x_{ij}$. If $v_j\ne v_k$, permute columns $j,k$ in its derivation and subtract. Dividing by $v_j-v_k$ derives $\sigma_j-\sigma_k$ within degree $b$.

Match one pigeon to column $j$. This yields $1-\sigma'_k$ in the residual system. Permuting its remaining columns derives $1-\sigma'_\ell$ for all $n-1$ residual holes. Sum these polynomials and the $n$ residual row equations: $$\sum_{\ell=1}^{n-1}(1-\sigma'_\ell)
 +\sum_{i=1}^{n}(\rho'_i-1)=-1.$$ This is another forbidden residual refutation. Therefore all $v_j$ agree. Row equations reduce $f'$ to a constant, which must be zero by the base lower bound. Hence $f\in H_0$. The opposite inclusion consists of base axioms and their linear combinations. *End of proof.*

<a id="scope"></a>

##### Scope

Thus adding all base-PC affine consequences within the displayed range creates no new affine identifications beyond the row equations. In particular, polylogarithmic-degree affine consequences cannot improve the spread decomposition. This does not exclude nonlinear reductions, relations using remaining extension blocks, or transformations informed by the actual refutation.

## The precise boundary reached

The decomposition problem for the stated affine criterion is solved, but its universally affordable version is false. The spread construction supplies admissible data, *not* a refutation using those data. It does not show that the blocks occur essentially in the translation of a short Frege proof. Nor does the criterion's optimum lower-bound all possible elimination methods.

The next theorem must therefore be sensitive to the refutation: discard or rewrite irrelevant blocks, exploit the coefficients and cofactors of a translated NS certificate, or use PHP structure outside static affine spaces. A better ordering of the same spaces cannot by itself repair the example; ordering and partition costs have already been optimized.
