<!-- Generated from ../latex/01_foundations.tex. Do not silently edit this reading copy. -->

<a id="ch-foundations"></a>

# 1. Objects, degrees, and reusable tools

> This chapter fixes the exact rings and proof systems, then proves the elementary tools used by every later construction. The distinction between a truncated consequence space and an unrestricted ideal is essential.

## The base systems

Let $k$ be a field. For $m$ rows and $n$ columns define $$S_{m,n}=k[x_{ij}:i\in[m],j\in[n]]/
 (x_{ij}x_{i'j}:i\ne i').$$ Variables have degree one. Rows may repeat, and powers of variables are allowed. Only different rows in the same column are excluded. Put $\rho_i=\sum_jx_{ij}$. For $m=n+1$, write $$S=S_{n+1,n},\qquad
 \overline B=S/(\rho_i-\rho_1:2\le i\le n+1),\qquad z=\rho_1\in\overline B.$$

For fixed prime $p$, our Boolean linear-row base system over $k=\mathbb F_p$ is <a id="eq-base"></a>

$$\label{eq:base}
 \mathcal F_n=\{\rho_i-1\}_i\cup
 \{x_{ij}x_{i'j}:i\ne i'\}\cup\{x_{ij}^2-x_{ij}\}_{i,j}.$$ No same-row exclusion equations are assumed. A Boolean row with sum one modulo $p$ need not have exactly one occupied cell. The homogeneous Boolean ring relevant to [Equation eq:base](01_foundations.md#eq-base) is $$A_n=k[x,z]/(\rho_i-z,\ x_{ij}x_{i'j},\ x_{ij}^2-zx_{ij})
     \cong\overline B/(x_{ij}^2-zx_{ij}).$$ Results in $\overline B$ do not automatically descend to $A_n$.

<a id="lem-deletion"></a>

### Lemma 1.1: Axiom deletion

If $\mathcal F\subseteq\mathcal F^+$, every degree-$D$ design for $\mathcal F^+$ is one for $\mathcal F$. Every PC refutation of $\mathcal F$ is also a refutation of $\mathcal F^+$ with the same degree. Consequently a degree lower bound for the stronger axiom system transfers to the weaker one.

**Proof.** The design has fewer equations to annihilate after deletion. A proof using only the smaller axiom list is still a valid proof from the larger list. Taking the contrapositive gives the lower-bound assertion. *End of proof.*

## Designs and polynomial calculus

For a finite set $\mathcal F\subseteq k[y]$, define $$\mathcal I_{D}(\mathcal F)=\mathop{\mathrm{span}}_k\{qf:f\in\mathcal F,\ \deg(qf)\le D\}.$$ A degree-$D$ *design* is a linear map $\lambda:k[y]_{\le D}\to k$ with $$\lambda(1)=1,\qquad \lambda(\mathcal I_{D}(\mathcal F))=0.$$ A degree-$D$ Nullstellensatz refutation is an identity $1=\sum_fq_ff$ with every $\deg(q_ff)\le D$.

Polynomial calculus (PC) starts from the axioms, and permits field-linear combinations and multiplication of a previously derived polynomial by one variable. Its degree is the largest total degree of any line, after collecting like terms in the ordinary polynomial ring. Let $\mathcal C_{D}(\mathcal F)$ be the vector space of polynomials having PC derivations within degree $D$.

<a id="lem-duality"></a>

### Lemma 1.2: Finite-dimensional separation

A degree-$D$ design for $\mathcal F$ exists exactly when $1\notin\mathcal I_{D}(\mathcal F)$. A normalized functional annihilating $\mathcal C_{D}(\mathcal F)$ exists exactly when there is no degree-$D$ PC refutation. Moreover, $$\mathcal I_{D}(\mathcal F)\subseteq\mathcal C_{D}(\mathcal F).$$

**Proof.** A normalized functional vanishing on a subspace cannot exist if that subspace contains $1$. Conversely, extend a basis of the subspace by $1$ and then to a basis of $k[y]_{\le D}$; assign zero to the original basis, one to $1$, and arbitrary values to the remaining basis elements. For the inclusion, derive each monomial multiple of an original axiom by repeated variable multiplication and combine the results. All intermediate degrees are bounded by the final product degree. The set of PC-derivable polynomials of bounded degree is closed under linear combinations by concatenating derivations. *End of proof.*

<a id="lem-reuse"></a>

### Lemma 1.3: Reuse versus flattening

If $f\in\mathcal C_{c}(\mathcal F)$ and $q$ is a polynomial, then $$qf\in\mathcal C_{\max\{c,\deg q+\deg f\}}(\mathcal F).$$ In contrast, the immediate consequence for a truncated original-axiom representation is only $$q\mathcal I_{c}(\mathcal F)\subseteq\mathcal I_{c+\deg q}(\mathcal F).$$

**Proof.** For PC, keep the derivation of $f$, multiply its *final line* by each monomial of $q$, and form their linear combination. No old derivation line is multiplied by $q$. In a flattened certificate for $f$, multiplying each certificate summand by $q$ can raise the degree of every such summand by $\deg q$. These are different operations and yield the two bounds. *End of proof.*

<a id="lem-substitution"></a>

### Lemma 1.4: Polynomial substitutions in PC

Let $\Phi$ map variables to polynomials of degree at most $T\ge1$. A PC derivation of degree $D$ maps to a PC derivation of degree at most $TD$ from the substituted axioms. If every line is also multiplied by a fixed polynomial $W$, the ceiling becomes $TD+\deg W$, provided the weighted substituted axiom lines have derivations within that ceiling.

**Proof.** Linear combinations commute with substitution. A multiplication step $P\mapsto yP$ maps to $\Phi(P)\mapsto\Phi(y)\Phi(P)$. Expand $\Phi(y)$ into monomials and use repeated variable multiplication followed by linear combination. Since the original predecessor has degree at most $D-1$, all these intermediate products have degree at most $T(D-1)+T$. The same argument with the fixed factor $W$ proves the weighted version. Zero predecessors cause no difficulty. *End of proof.*

## Finite-field identities and bounded-degree reductions

Every old variable is assigned a domain, either $\{0,1\}$ or $\mathbb F_p$. Let $J_{\mathrm{fld}}$ be generated by $y^2-y$ or $y^p-y$, respectively.

<a id="lem-fieldreduction"></a>

### Lemma 1.5: Degree-nonincreasing field reduction

A polynomial $P$ that vanishes on the product of the specified old-variable domains belongs to $J_{\mathrm{fld}}$. If $\deg P\le B$, it has an ideal representation by the defining univariate equations in which every summand has degree at most $B$. In particular, a degree-$B$ design annihilates $P$. For every $g\in\mathbb F_p[y]$, $$g^p-g\in J_{\mathrm{fld}}.$$

**Proof.** Divide successively by the monic univariate generators. Each replacement lowers a power of one variable and never increases total degree; record each subtracted multiple. The remainder has individual degree below the size of the corresponding domain. A polynomial with those individual-degree bounds and zero values on the full product grid is zero: apply univariate interpolation in one coordinate and induct on the number of coordinates. Thus the remainder vanishes and the recorded representation has the stated degree bound. Finally, every old assignment makes $g$ an element of $\mathbb F_p$, so $g^p-g$ vanishes on the domain. *End of proof.*

<a id="lem-selectors"></a>

### Lemma 1.6: Finite-field selectors

For $\alpha\in\mathbb F_p$ put $\chi_\alpha(t)=1-(t-\alpha)^{p-1}$. Then <a id="eq-selectorpartition"></a>

<a id="eq-selectorlinear"></a>

<a id="eq-selectorproduct"></a>

<a id="eq-factorzero"></a>

$$\begin{aligned}
 \sum_{\alpha\in\mathbb F_p}\chi_\alpha(t)&=1,\label{eq:selectorpartition}\\
 t&=\sum_{\alpha\ne0}\alpha\chi_\alpha(t),\label{eq:selectorlinear}\\
 \chi_\alpha(t)(1-\alpha^{-1}t)&=\alpha^{-1}(t^p-t)
       \quad(\alpha\ne0),\label{eq:selectorproduct}\\
 1-t^{p-1}&=\prod_{\alpha\ne0}(1-\alpha^{-1}t).
 \label{eq:factorzero}
\end{aligned}$$ All are ordinary polynomial identities over $\mathbb F_p$.

**Proof.** The first two identities have degree at most $p-1$ and agree on $\mathbb F_p$: the $\chi_\alpha$ are its point indicators. This also covers $p=2$. For the third, write $1-\alpha^{-1}t=-\alpha^{-1}(t-\alpha)$ and use $(t-\alpha)^p=t^p-\alpha$. Both sides of the fourth have degree $p-1$, the same nonzero roots, and constant term one. *End of proof.*

<a id="lem-columnnf"></a>

### Lemma 1.7: Column-exclusive normal form

Let $$J=(x_{ij}^2-x_{ij},\ x_{ij}x_{i'j}:i\ne i').$$ Its quotient is the algebra of functions on assignments where every column is either empty or occupied by one row. Every polynomial in $J$ of degree at most $B$ has a representation by its displayed generators within degree $B$.

**Proof.** Reduce powers by $x_{ij}^2\mapsto x_{ij}$ and different-row products in a column to zero. The surviving monomials choose at most one variable per column. For a single column, $1,x_{1j},\ldots,x_{mj}$ are independent functions on its $m+1$ states; tensoring proves uniqueness on all columns. The reductions never increase degree and record the desired certificate. *End of proof.*

## Extension data and the actual quantifiers

An extension block $a$, of accuracy $h_a\ge1$, has old-variable inputs $g_{a,1},\ldots,g_{a,k_a}$, fresh variables $r_{a,u,j}$, and all companions <a id="eq-ens"></a>

$$\label{eq:ens}
 E_{a,i}=g_{a,i}\prod_{u=1}^{h_a}
 \left(1-\sum_jr_{a,u,j}g_{a,j}\right).$$ Within one level, new variables are disjoint across blocks. Inputs use only original variables and variables from earlier levels. The field axioms $\mathcal R=\{r^p-r\}$ are included. This definition and level convention follow [Krajicek Definition 2.1](../../references/README.md#krajicek).

With zero inputs omitted, put $$\delta_{a,i}=\deg g_{a,i},\quad \delta_a=\max_i\delta_{a,i},\quad
 e_{a,i}=\delta_{a,i}+h_a(\delta_a+1).$$ Fresh coefficient variables make this the original degree of a nonzero companion. A companion is *active at $D$* if $e_{a,i}\le D$.

<a id="lem-scalar-sufficient"></a>

### Lemma 1.8: Scalar lifting is sufficient, not necessary

Suppose $\beta\in\mathbb F_p^{|r|}$ and a normalized functional $\lambda$ on old polynomials annihilates the images of every allowed degree-$D$ axiom multiple under $r=\beta$. Then $$\Lambda(P)=\lambda(P(y,\beta))$$ is a degree-$D$ design for the original joint-variable system. An arbitrary joint design need not have this form.

**Proof.** Constant substitution preserves degree, commutes with multiplication, and makes $r^p-r$ zero. The assumed image equations are exactly the design equations. No assertion about representing an arbitrary linear functional by one evaluation follows from these facts. *End of proof.*

The desired existential statement is $\forall\mathcal E\ \exists\Lambda_{\mathcal E}$, for the extension data actually required by the simulation. The stronger version $\forall\mathcal E\ \exists\beta\ \exists\lambda$ is one sufficient route. Universal success of all scalar choices is false: for the input tuple $(1)$, the companion is $\prod_u(1-r_u)$, which becomes $1$ at $r=0$ and $0$ when $r_1=1$.

<a id="lem-homogenization"></a>

### Lemma 1.9: Homogenized separation

For the base system [Equation eq:base](01_foundations.md#eq-base) and additional old-variable polynomials $f$, homogenize each nonzero $f$ to its actual degree. There is a degree-$D$ design precisely when $$z^D\notin(f^{\mathrm h})A_n.$$ Membership is tested in homogeneous degree $D$.

**Proof.** Homogenizing a bounded-degree certificate $1=\sum q_ff$ to degree $D$ produces $z^D$ in the displayed ideal, including the homogenized base equations. Conversely, dehomogenize any homogeneous degree-$D$ representation by setting $z=1$; every certificate summand has degree at most $D$. Apply [Lemma 1.2](01_foundations.md#lem-duality). This equivalence concerns $A_n$, not the larger non-Boolean ring $\overline B$. *End of proof.*
