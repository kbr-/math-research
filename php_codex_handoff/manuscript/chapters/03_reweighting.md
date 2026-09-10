<!-- Generated from ../latex/03_reweighting.tex. Do not silently edit this reading copy. -->

<a id="ch-reweighting"></a>

# 3. Exact reweighting and shared conditioning

> These constructions produce actual normalized functionals for nonlinear extension data. They may change the original moments. Their limitations are the degree of the conditioning weight, not a genericity assumption.

## A single nonlinear block

Let $k=\mathbb F_p$, and let the old system $\mathcal F\subseteq k[y]$ contain the appropriate Boolean or field equation for every old variable. Fix a target degree $D$. For a block of accuracy $h$ use $e_i=\deg E_i$, $\delta_i=\deg g_i$, and define <a id="eq-repaircost"></a>

$$\label{eq:repaircost}
 c(D)=\max\left(\{0\}\cup
 \{D-e_i+(p-1)\delta_i:e_i\le D\}\right).$$

<a id="lem-repair"></a>

### Lemma 3.1: Exact scalar reweighting

Every degree-$(D+c(D))$ design $\lambda$ for $\mathcal F$ gives a degree-$D$ design for $\mathcal F\cup\mathcal E\cup\mathcal R$ of the form $$\boxed{\Lambda(P)=\frac{\lambda(WP(y,\beta))}{\lambda(W)},\qquad
 \deg W\le c(D),\quad\lambda(W)\ne0,\quad\beta\in\mathbb F_p^{|r|}.}$$ The block's inputs are arbitrary polynomials.

**Proof.** If $\lambda(qg_i)=0$ for every active $i$ and every monomial $q$ of degree at most $D-e_i$, take $W=1$ and $\beta=0$. Each extension image is $g_i$, and every allowed cofactor specializes to a linear combination of the tested monomials. All required extension moments vanish.

Otherwise choose $i,q$ with $\lambda(qg_i)\ne0$. By [Equation eq:selectorlinear](01_foundations.md#eq-selectorlinear), some $\alpha\ne0$ has $\lambda(q\chi_\alpha(g_i))\ne0$. Set $$W=q\chi_\alpha(g_i),\qquad \beta_{1,i}=\alpha^{-1},
 \qquad \beta_{u,j}=0\text{ otherwise}.$$ Its degree is at most $c(D)$. Every companion becomes $g_j(1-\alpha^{-1}g_i)$, and [Equation eq:selectorproduct](01_foundations.md#eq-selectorproduct) gives $$WE_j(y,\beta)=\alpha^{-1}qg_j(g_i^p-g_i)\in J_{\mathrm{fld}}.$$ This is ideal membership before applying a functional, so it remains true after every allowed multiplier. The entire weighted substituted axiom multiple has degree at most $D+c(D)$ and is annihilated by [Lemma 1.5](01_foundations.md#lem-fieldreduction). Old-axiom multiples are annihilated directly within that budget. New field equations vanish at $\beta$, and dividing by $\lambda(W)$ normalizes the result. *End of proof.*

<a id="lem-levelrepair"></a>

### Lemma 3.2: A whole level with exact simultaneous repair

For same-level blocks $a$, define $c_a(D)$ by [Equation eq:repaircost](03_reweighting.md#eq-repaircost). A degree $$\boxed{B=D+\sum_a c_a(D)}$$ old design suffices for a degree-$D$ design of the complete level. The final weight has degree at most the sum of the costs of the blocks actually repaired.

**Proof.** Start with $W=1$ and no committed blocks. Test the moments $\lambda(Wqg_{a,i})$ for all uncommitted blocks and their allowed monomials. If all are zero, assign all uncommitted new variables zero and stop. Otherwise choose a nonzero moment. As in [Lemma 3.1](03_reweighting.md#lem-repair), choose $\alpha\ne0$ preserving nonzero value and replace $$W\leftarrow Wq\chi_\alpha(g_{a,i}).$$ Assign the selected coefficient in block $a$ the value $\alpha^{-1}$, all its others zero, and commit that block. Recheck every uncommitted block after this change.

A committed block has acquired an actual field-ideal identity, so multiplying $W$ later cannot invalidate it. An uncommitted zero specialization is used only after checking its moments against the *final* weight. Each repair commits a new block, so the procedure terminates. The selector identity guarantees $\lambda(W)\ne0$ at every update. Degrees add by at most $c_a(D)$ at the unique repair of block $a$. The proof of [Lemma 3.1](03_reweighting.md#lem-repair) then verifies all final design equations. *End of proof.*

<a id="cor-repairbudget"></a>

### Corollary 3.3: Simple budgets and level composition

If $h\ge p-2$, then $c_a(D)\le\max\{0,D-h\}$. A level of $s$ blocks costs at most $$D+s\max\{0,D-h\}\le (s+1)D.$$ For several levels, choose budgets backwards: $$D_\ell=D,\qquad D_{j-1}=D_j+\sum_{a\text{ in level }j}c_a(D_j).$$ A degree-$D_0$ base design lifts through all levels. A rough bound is $D_0\le D\prod_j(1+s_j)$ under the displayed accuracy condition.

**Proof.** For active $i$, $D-e_{a,i}+(p-1)\delta_{a,i}
=D-h-h\delta_a+(p-2)\delta_{a,i}\le D-h$. The one-level result then applies successively. At every new level all preceding axioms, including their field equations, are old axioms with their original degrees. *End of proof.*

## One shared weight for every block and level

<a id="lem-sharedfeatures"></a>

### Lemma 3.4: Common-feature conditioning

Suppose every input in a leveled system satisfies $$g_{a,i}(x,r_{<a})\equiv
 G_{a,i}(f_1(x),\ldots,f_R(x),r_{<a})\pmod J,$$ where $J$ is either the old Boolean/field ideal or the Boolean column-exclusive ideal of [Lemma 1.7](01_foundations.md#lem-columnnf). Put $\kappa=(p-1)\sum_{\nu=1}^R\deg f_\nu$. A degree-$(D+\kappa)$ base design lifts to the entire leveled system at degree $D$, using one weight and scalar values for every extension variable.

**Proof.** For $\alpha\in\mathbb F_p^R$ put $W_\alpha=\prod_\nu\chi_{\alpha_\nu}(f_\nu)$. Their sum is one by [Equation eq:selectorpartition](01_foundations.md#eq-selectorpartition), and their degrees are at most $\kappa$. Some $W=W_\alpha$ has $\lambda(W)\ne0$.

On its selected cell all $f_\nu$ are constants. Proceed level by level. After earlier variables have scalar values, every input in a new block has a scalar value $b_i$ on this cell. If all $b_i=0$, set the block's variables to zero. Otherwise choose $b_j\ne0$, set $r_{1,j}=b_j^{-1}$ and the rest zero. Every companion vanishes on that same cell. Thus $WE_{a,i}(x,\beta)\in J$ for every block, at every level.

Use $\Lambda(P)=\lambda(WP(x,\beta))/\lambda(W)$. Its weighted images have degree at most $D+\kappa$. The degree-bounded reduction lemma for $J$ proves annihilation of all extension multiples. Old axioms and new field equations are handled as in [Lemma 3.1](03_reweighting.md#lem-repair). The weight never changes between levels. *End of proof.*

<a id="cor-greedycell"></a>

### Corollary 3.5: Greedy selection of a nonzero cell

With oracle access to $\lambda$, a nonzero shared cell can be selected with at most $pR$ value queries; enumeration of all $p^R$ cells is unnecessary.

**Proof.** If a prefix weight $W'$ has nonzero value, then $\sum_{\alpha\in\mathbb F_p}\lambda(W'\chi_\alpha(f_\nu))=\lambda(W')\ne0$. At least one of the $p$ possible next values preserves it. Repeat for all features. *End of proof.*

<a id="lem-columnconditioning"></a>

### Lemma 3.6: A whole PHP column costs one degree

In the Boolean column-exclusive ring define $$e_{j,0}=1-\sum_i x_{ij},\qquad e_{j,i}=x_{ij}\ (i\ge1).$$ These are the indicators of the empty and occupied states of column $j$. If every extension input depends on original variables only through a common set of $q$ columns, a degree-$(D+q)$ base design lifts to every level at degree $D$.

**Proof.** The indicators partition one and have degree one. For a state choice on the $q$ columns, take the product of its $q$ indicators. These weights partition one and have degree at most $q$. A weight of nonzero design value fixes the complete states of all those columns. Apply the proof of [Lemma 3.4](03_reweighting.md#lem-sharedfeatures) with these weights. No row-exclusion equation is used. *End of proof.*

<a id="scope"></a>

##### Scope

Conditioning on all $n$ columns always determines the old assignment, but costs $D+n$. This is outside the available $\lfloor n/2\rfloor$ starting budget and is not a solution of the payoff problem. Small shared-feature descriptions are sufficient hypotheses, not properties proved for arbitrary extension data.
