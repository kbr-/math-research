<!-- Generated from ../latex/04_packing.tex. Do not silently edit this reading copy. -->

<a id="ch-packing"></a>

# 4. Factor packing and pointwise barriers

> Polynomial substitutions can use all $h$ extension factors in parallel. This removes block count from one budget, but not the worst-case rank of the input tuple. Shared weights and substitutions can be combined; the barriers here delimit those pointwise mechanisms.

## Exact factor packing

<a id="lem-packedcoeff"></a>

### Lemma 4.1: Packed zero-test coefficients

Let $g_1,\ldots,g_k$ span a polynomial space of dimension $R$, and choose a basis $f_1,\ldots,f_R$ from the tuple, of degree at most $\delta$. For accuracy $h$, there are polynomial coefficients $\beta_{u,j}(y)$ such that $$\prod_{u=1}^h\left(1-\sum_j\beta_{u,j}g_j\right)
 =Z:=\prod_{\nu=1}^R(1-f_\nu^{p-1}),$$ with $$\boxed{\deg\beta_{u,j}\le
 \delta\left(\left\lceil\frac{(p-1)R}{h}\right\rceil-1\right)_+.}$$ Moreover $g_iZ\in J_{\mathrm{fld}}$ for every $i$.

**Proof.** By [Equation eq:factorzero](01_foundations.md#eq-factorzero), $Z$ is a product of $(p-1)R$ factors $1-\alpha^{-1}f_\nu$. Partition them into $h$ groups of at most $Q=\lceil(p-1)R/h\rceil$ factors. For a group ordered as $(\alpha_\ell,\nu_\ell)$, define the coefficient of $f_\nu$ by $$\beta_{u,\nu}=
 \sum_{\ell:\nu_\ell=\nu}\alpha_\ell^{-1}
 \prod_{v<\ell}(1-\alpha_v^{-1}f_{\nu_v}).$$ The identity $1-\prod_{\ell=1}^b(1-a_\ell)=\sum_{\ell=1}^b a_\ell\prod_{v<\ell}(1-a_v)$ proves the group formula, and the largest coefficient uses at most $Q-1$ inputs. An empty group uses zero coefficients. Convert the chosen basis back to original input coordinates by constants. Finally, $f_\nu Z=(f_\nu-f_\nu^p)\prod_{\mu\ne\nu}(1-f_\mu^{p-1})\in J_{\mathrm{fld}}$; linearity gives the assertion for every $g_i$. *End of proof.*

<a id="lem-packedlift"></a>

### Lemma 4.2: A level costs a maximum, not a sum

For blocks $a$ let $R_a$ and $\delta_a$ be their input ranks and degree bounds, and put $$T_a=\max\left\{1,\delta_a
 \left(\left\lceil\frac{(p-1)R_a}{h_a}\right\rceil-1\right)_+\right\},
 \qquad T=\max_aT_a.$$ A degree-$TD$ old design lifts to a degree-$D$ design for the entire level via $$\Lambda(P)=\lambda(P(y,\beta(y))).$$ It preserves all old moments through degree $D$.

**Proof.** Use [Lemma 4.1](04_packing.md#lem-packedcoeff) in every block simultaneously. All substituted variables depend only on old variables, so no within-level nesting occurs and a degree-$D$ polynomial has image degree at most $TD$. Extension images belong to $J_{\mathrm{fld}}$, and a new field equation has image $\beta^p-\beta\in J_{\mathrm{fld}}$. Degree-bounded reduction handles their multiples. Old axioms remain old-axiom multiples. Substitution fixes old polynomials and one. *End of proof.*

<a id="cor-packingvariants"></a>

### Corollary 4.3: Variants and level composition

If the basis inputs are Boolean-valued modulo $J_{\mathrm{fld}}$, replace $(p-1)R_a$ by $R_a$. Only active companions need be spanned when constructing a degree-$D$ design. Across levels the sufficient degree is $D\prod_jT_j$. For affine inputs over $\mathbb F_2$, rank $R_a\le2h_a$ gives $T_a=1$, regardless of the number of blocks.

**Proof.** For a Boolean-valued $f$, use $1-f$ instead of $1-f^{p-1}$. Inactive companions have no permitted multipliers, so a zero test for the active inputs suffices. Compose degree inflation one level at a time, retaining the original axiom degrees. For affine inputs and $R_a\le2h_a$, $\lceil R_a/h_a\rceil-1\le1$. *End of proof.*

<a id="lem-hybrid"></a>

### Lemma 4.4: Packing plus repair

Fix $\tau\ge1$. Pack all blocks with $T_a\le\tau$, and reserve the others for scalar repair. Define $$c_a^{(\tau)}(D)=\max\left(\{0\}\cup
 \{\tau(D-e_{a,i})+(p-1)\delta_{a,i}:e_{a,i}\le D\}\right).$$ A sufficient old-design degree is $$\boxed{B_{\rm hybrid}(D)=
 \min_{\tau\ge1}\left[\tau D+\sum_{a:T_a>\tau}c_a^{(\tau)}(D)\right].}$$ In particular it is no worse than either $D+\sum_ac_a(D)$ or $D\max_aT_a$.

**Proof.** After packed substitutions an allowed cofactor of $E_{a,i}$ has old-variable degree at most $\tau(D-e_{a,i})$. In the repair procedure of [Lemma 3.2](03_reweighting.md#lem-levelrepair), test all moments $\lambda(Wqg_{a,i})$ up to that enlarged degree. Each repair costs at most $c_a^{(\tau)}(D)$. Packed blocks already vanish modulo $J_{\mathrm{fld}}$, so reweighting cannot spoil them. The final weighted substituted polynomial has degree at most $\deg W+\tau D$. At $\tau=1$ this only deletes costs from the old repair bound; at $\tau=\max T_a$ no repaired blocks remain. Between consecutive $T_a$ values the displayed cost is nondecreasing, so only those thresholds and $1$ need be tested. *End of proof.*

<a id="lem-sharedhybrid"></a>

### Lemma 4.5: Packing plus shared conditioning

For one level, suppose one group is handled by substitutions of degree at most $T$, and all remaining blocks are determined by common features with weight cost $\kappa$. Then $B=TD+\kappa$ suffices.

**Proof.** Choose one nonzero shared weight $W$ and scalar values for its blocks, and use the polynomial substitutions on the first group. Define $\Lambda(P)=\lambda(WP(y,\beta_{\rm packed}(y),\beta_{\rm shared}))/\lambda(W)$. Its domain fits $TD+\kappa$. Packed identities hold in the field ideal before reweighting; shared blocks vanish after multiplying by $W$. Apply the earlier reduction lemmas. Thus, if blocks with $T_a>\tau$ have certified shared cost $\kappa_\tau$, another sufficient bound is $\min_\tau[\tau D+\kappa_\tau]$. *End of proof.*

## Limits of pointwise substitutions

<a id="lem-pointwisebarrier"></a>

### Lemma 4.6: The independent-input degree barrier

For inputs $g_j=y_j$ on $\mathbb F_p^R$, suppose coefficients $\beta_{u,j}(y)$ of degree at most $L$ make all companions vanish at every assignment. Then $$\boxed{L\ge\left\lceil\frac{(p-1)R}{h}\right\rceil-1.}$$ For independent Boolean inputs over any $\mathbb F_p$, the same argument gives $h(L+1)\ge R$.

**Proof.** Put $P(y)=\prod_u(1-\sum_j\beta_{u,j}y_j)$. The equations $y_jP=0$ force $P(0)=1$ and $P(y)=0$ for all nonzero inputs. Its unique reduced representative on $\mathbb F_p^R$ is $\prod_j(1-y_j^{p-1})$, of degree $(p-1)R$. Reduction cannot increase degree, whereas $\deg P\le h(L+1)$. On the Boolean cube the unique multilinear representative is $\prod_j(1-y_j)$, of degree $R$. *End of proof.*

<a id="lem-emptyrowsupport"></a>

### Lemma 4.7: Support on an empty row has full column degree

In the Boolean column-exclusive quotient $A=k[x]/J$, a nonzero function supported only on assignments where row $i$ is empty has minimum polynomial degree exactly $n$.

**Proof.** For each column use the basis $1,e_{j,a}$ for all column states $a\ne i$, including the empty state $a=0$. Every $e_{j,a}$ is affine-linear and vanishes at state $i$; conversely $x_{ij}=1-\sum_{a\ne i}e_{j,a}$. Thus the change of basis preserves the degree filtration. Tensoring these column bases gives a unique expansion whose terms select a set of columns.

Set a column $j$ to state $i$. Terms using a nonconstant factor there vanish; all other terms remain. Since the function is zero under this restriction, uniqueness forces every coefficient of a term omitting column $j$ to be zero. Repeat for all columns. Every surviving nonzero term uses all $n$ columns. Such terms have degree $n$, and no lower-degree expansion is possible. *End of proof.*

<a id="thm-columnbarrier"></a>

### Theorem 4.8: A barrier to weighted packing modulo column axioms alone

For each PHP row $i$ introduce a block with inputs $x_{i1},\ldots,x_{in}$ and common factor $$P_i=\prod_{u=1}^h(1-\sum_jr_{i,u,j}x_{ij}).$$ Suppose a polynomial $W$ nonzero in $A=k[x]/J$ and substitutions $\beta$ of maximum degree $L$ satisfy $Wx_{ij}P_i(x,\beta)=0$ in $A$ for all $i,j$. Then $$\deg W+h(L+1)\ge n.$$ For $D\ge2h+1$ and $T=\max\{1,L\}$, the previous advertised budget obeys $$\boxed{\deg W+TD\ge n+D-2h\ge n+1.}$$

**Proof.** Let $Q_i=\prod_j(1-x_{ij})$. The annihilation assumptions imply $WP_i=Q_iWP_i$, and $Q_iP_i=Q_i$ because $Q_ix_{ij}=0$. Hence $WP_i=WQ_i$ in $A$. Choose a column-exclusive assignment where $W\ne0$. Since there are $n+1$ rows and only $n$ columns, some row $i$ is empty there; then $WQ_i\ne0$. By [Lemma 4.7](04_packing.md#lem-emptyrowsupport), $n\le\deg(WP_i)\le\deg W+h(L+1)$. For $L\ge1$, add $DL-h(L+1)$ to this bound and use $D\ge2h+1$; the minimum occurs at $L=1$, giving $n+D-2h$. For $L=0$, the stronger bound $\deg W+D\ge n+D-h$ holds. *End of proof.*

<a id="cor-rowfree"></a>

### Corollary 4.9: The obstruction is representational, not intrinsic

The same family has a degree-preserving lifting when the row equations are used. Set $r_{i,1,j}=1$ for every $j$ and all other factors' coefficients to zero. Then $$E_{i,j}(x,\beta)=-x_{ij}(\rho_i-1).$$ Every degree-$D$ base design lifts by constant substitution.

**Proof.** The selected factor is $1-\rho_i$. Its product with $x_{ij}$ has a degree-two base-axiom certificate, below the companion's original degree $2h+1$. Every permitted multiple therefore lies within the original degree budget. This uses the row axiom, which was deliberately excluded from $J$ in [Theorem 4.8](04_packing.md#thm-columnbarrier). *End of proof.*

<a id="scope"></a>

##### Scope

The lower bound in [Theorem 4.8](04_packing.md#thm-columnbarrier) is sharp as a bound on that pointwise packing architecture. For $q=n-2h\ge0$, use $W=\prod_{j=1}^{q}x_{jj}$. On selected rows use $1-x_{ii}$. On each other row pair the remaining $2h$ columns, using coefficients $1$ and $1-x_{ia}$ on a pair $(a,b)$; their factor is $(1-x_{ia})(1-x_{ib})$. This gives $\deg W=n-2h$ and $T=1$. It does not promise $\lambda(W)\ne0$ for a prescribed design; it establishes sharpness of the algebraic degree constraint only.
