# Pigeonhole Designs and Extension Elimination

Full raw-LaTeX Markdown reading copy. Source snapshot: 10 September 2026.

This conversion preserves the working status of the manuscript; it is not a new proof audit. The exact original source is in `latex/`.

# How to read this record

This is a mathematical consolidation, not a transcript and not a claim that the payoff has been achieved. It begins with the independent work undertaken after the initial uploaded research report. The report's older assertions are not silently imported as theorems; the corrections and changes of direction relevant to this conversation are recorded in Appendix [Chapter A](chapters/11_appendices.md#app-ledger).

Each lemma supplies its assumptions and a proof of the claim made here. Repeated arguments have been factored into reusable preliminary lemmas; references between chapters are internal to this document. Results inherited from the literature are explicitly marked *Imported input*. Their original proofs are not reproduced or claimed as our work. Statements involving the published PHP lower bound are conditional on the encoding match spelled out in Chapter [Chapter 10](chapters/10_route.md#ch-route).

**Status convention.** Unless marked imported or open, the results below are the *working derivations obtained in the conversation*. Typesetting them as lemmas records their mathematical content; it does not certify novelty, independent verification, or a machine-checked general proof. A complete audit of the proof transformations remains an explicit obligation. The computational supplements establish only the finite checks described in their scope notes.

**Three separations matter throughout.** The non-Boolean graded ring $\overline B$ is not the Boolean PHP ring. A design annihilating bounded-degree original-axiom multiples need not annihilate all bounded-degree polynomial-calculus consequences. Finally, generic linear restrictions are not the full leveled extension systems produced by a Frege simulation. None of these distinctions is erased by the notation.

**Degree convention.** An extension axiom retains its original degree in old and new variables. Specialization or Boolean reduction may lower the degree of its image, but does not retroactively enlarge the set of allowed multipliers in the original degree-$D$ design. Zero polynomials are omitted wherever a degree is used.

**Editorial changes.** Definitions, finite-dimensional duality, and degree-nonincreasing reductions are made explicit so the proofs can be followed without earlier messages. Conservative versus sharper degree bounds are identified. No missing global compatibility or simulation-transfer theorem has been supplied by assumption without being labeled.

# The argument at a glance {#the-argument-at-a-glance .unnumbered}

  Branch                 Endpoint and limitation
  ---------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------
  Graded algebra         Koszul vanishing and the initial Hilbert function hold in the proved range $2d-1\le n$. The originally proposed range $d<n$ is false.
  Generic restrictions   A determinant functional survives $t$ generic restrictions when $t+2d-1\le n$. This concerns the non-Boolean ring only.
  Exact liftings         Reweighting, factor packing, shared conditioning, base-aware substitutions, and supported moment corrections give explicit constructions with stated budgets.
  PC elimination         Blocks can be eliminated at additive degree cost. Equal spans, nested spans, and nested cores with low-rank residuals can be batched more cheaply.
  Decomposition          For affine data the current cost criterion is exactly optimizable. There are polynomial-size admissible families whose optimum still exceeds $n/2$.
  Remaining theorem      Use the actual translated Nullstellensatz refutation and PHP structure to obtain a base PC refutation below the available linear-degree threshold.

# Notation quick reference {#notation-quick-reference .unnumbered}

  ------------------ --------------------------------------------------------------------
  $\overline B$      Non-Boolean column-exclusive ring with equal row sums.
  $\mathcal F_n$     Boolean linear-row PHP axioms, without row exclusion.
  $\mathcal I_D$     Span of original-axiom multiples of total degree at most $D$.
  $\mathcal C_D$     Polynomial-calculus consequences derivable within degree $D$.
  $h,\ \delta,\ D$   Extension accuracy, maximum input degree, and target proof degree.
  $B,\ T$            Required base degree and polynomial-substitution degree inflation.
  ------------------ --------------------------------------------------------------------

**Reading paths.** Chapters 1--2 contain the graded-algebra branch. Chapters 3--6 develop explicit functionals and their limitations. Chapters 7--9 give the current proof-elimination route and its decomposition obstruction. Chapter 10 states the remaining goal and risk-ordered proof obligations; Appendix C provides a compact budget reference.




---

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
 \{x_{ij}x_{i'j}:i\ne i'\}\cup\{x_{ij}^2-x_{ij}\}_{i,j}.$$ No same-row exclusion equations are assumed. A Boolean row with sum one modulo $p$ need not have exactly one occupied cell. The homogeneous Boolean ring relevant to [Equation eq:base](chapters/01_foundations.md#eq-base) is $$A_n=k[x,z]/(\rho_i-z,\ x_{ij}x_{i'j},\ x_{ij}^2-zx_{ij})
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
 \left(1-\sum_jr_{a,u,j}g_{a,j}\right).$$ Within one level, new variables are disjoint across blocks. Inputs use only original variables and variables from earlier levels. The field axioms $\mathcal R=\{r^p-r\}$ are included. This definition and level convention follow [Krajicek Definition 2.1](../references/README.md#krajicek).

With zero inputs omitted, put $$\delta_{a,i}=\deg g_{a,i},\quad \delta_a=\max_i\delta_{a,i},\quad
 e_{a,i}=\delta_{a,i}+h_a(\delta_a+1).$$ Fresh coefficient variables make this the original degree of a nonzero companion. A companion is *active at $D$* if $e_{a,i}\le D$.

<a id="lem-scalar-sufficient"></a>

### Lemma 1.8: Scalar lifting is sufficient, not necessary

Suppose $\beta\in\mathbb F_p^{|r|}$ and a normalized functional $\lambda$ on old polynomials annihilates the images of every allowed degree-$D$ axiom multiple under $r=\beta$. Then $$\Lambda(P)=\lambda(P(y,\beta))$$ is a degree-$D$ design for the original joint-variable system. An arbitrary joint design need not have this form.

**Proof.** Constant substitution preserves degree, commutes with multiplication, and makes $r^p-r$ zero. The assumed image equations are exactly the design equations. No assertion about representing an arbitrary linear functional by one evaluation follows from these facts. *End of proof.*

The desired existential statement is $\forall\mathcal E\ \exists\Lambda_{\mathcal E}$, for the extension data actually required by the simulation. The stronger version $\forall\mathcal E\ \exists\beta\ \exists\lambda$ is one sufficient route. Universal success of all scalar choices is false: for the input tuple $(1)$, the companion is $\prod_u(1-r_u)$, which becomes $1$ at $r=0$ and $0$ when $r_1=1$.

<a id="lem-homogenization"></a>

### Lemma 1.9: Homogenized separation

For the base system [Equation eq:base](chapters/01_foundations.md#eq-base) and additional old-variable polynomials $f$, homogenize each nonzero $f$ to its actual degree. There is a degree-$D$ design precisely when $$z^D\notin(f^{\mathrm h})A_n.$$ Membership is tested in homogeneous degree $D$.

**Proof.** Homogenizing a bounded-degree certificate $1=\sum q_ff$ to degree $D$ produces $z^D$ in the displayed ideal, including the homogenized base equations. Conversely, dehomogenize any homogeneous degree-$D$ representation by setting $z=1$; every certificate summand has degree at most $D$. Apply [Lemma 1.2](chapters/01_foundations.md#lem-duality). This equivalence concerns $A_n$, not the larger non-Boolean ring $\overline B$. *End of proof.*


---

<!-- Generated from ../latex/02_graded.tex. Do not silently edit this reading copy. -->

<a id="ch-graded"></a>

# 2. The graded branch: corrected vanishing and generic survival

> This branch is a result about $\overline B$, before Boolean equations are imposed. It supplies the corrected form of item (a), a weak restriction count, and an explicit generic annihilator. It does not by itself solve the extension-system problem.

## The original range fails

For linear forms $\rho_1,\ldots,\rho_m$ in $S_{m,n}$, grade the Koszul complex by $$K_i(\rho;S)_j=S_{j-i}\otimes_k\bigwedge^i k^m.$$ Give $x_{ab}$ and the $a$th exterior generator row degree $\varepsilon_a$. Its differential preserves this finer grading.

<a id="lem-koszul-counter"></a>

### Lemma 2.1: A characteristic-free counterexample

For $n=4,m=5$, the row multidegree $\alpha=(1,1,1,0,0)$ satisfies $$H_1(\rho_1,\ldots,\rho_5;S_{5,4})_\alpha\ne0.$$ Thus the statement $H_i(\rho;S)_j=0$ for every $i\ge1$ and $j<n$ is false over every field.

**Proof.** The strand has dimensions $$0\longrightarrow k\xrightarrow{\partial_3}k^{12}
 \xrightarrow{\partial_2}k^{36}
 \xrightarrow{\partial_1}k^{24}\longrightarrow0.$$ The counts are respectively $1$, $3\cdot4$, $3\cdot4\cdot3$, and $4\cdot3\cdot2$: active rows remaining in the coefficient monomial must use distinct columns. The image of the unique top exterior basis element is $\rho_1e_2\wedge e_3-\rho_2e_1\wedge e_3+\rho_3e_1\wedge e_2$, which is nonzero. Hence $\mathop{\mathrm{rank}}\partial_3=1$ and $\mathop{\mathrm{rank}}\partial_2\le11$. But $\dim\ker\partial_1\ge36-24=12$, giving $\dim H_1\ge1$. The internal degree is $3<4$. *End of proof.*

## A multigraded vanishing lemma

<a id="lem-multigraded"></a>

### Lemma 2.2: Vanishing with active-row control

Let $S_{r,N}$ have $r$ rows and $N$ columns, let $\sigma_a$ be its row sums, and suppose $\alpha_a>0$ for all $a$. Put $q=\sum_a\alpha_a$. For $i\ge1$, $$\boxed{N\ge q+r-i\quad\Longrightarrow\quad
 H_i(\sigma;S_{r,N})_\alpha=0.}$$

**Proof.** Write $T=S_{r,N-1}$ and $C_r=k[y_1,\ldots,y_r]/(y_ay_b:a\ne b)$ for the final column. There is an exact sequence <a id="eq-axis-exact"></a>

$$\label{eq:axis-exact}
 0\longrightarrow C_r\longrightarrow\bigoplus_{a=1}^r k[y_a]
 \longrightarrow k^{r-1}\longrightarrow0.$$ The first map restricts to the coordinate axes; its image consists of tuples with equal constant terms. The last map takes differences of those constants.

Tensor with $T$. Let $\sigma'_b$ be a row sum on the first $N-1$ columns. On the middle summand $T[y_a]$, the full row sum acts as $\sigma'_b+\delta_{ab}y_a$; on the final $T^{r-1}$ it acts as $\sigma'_b$. Thus [Equation eq:axis-exact](chapters/02_graded.md#eq-axis-exact) induces an exact sequence of Koszul complexes.

On $T[y_a]$, the element $\sigma'_a+y_a$ is monic in $y_a$ and is a nonzerodivisor. Its two-term Koszul complex resolves the quotient $T[y_a]/(\sigma'_a+y_a)\cong T$. Tensoring the other, free Koszul factors and taking homology identifies this middle summand with the Koszul complex on $\sigma'_b$, $b\ne a$, over $T$.

Abbreviate $H_i^{r,N}(\alpha)=H_i(\sigma;S_{r,N})_\alpha$. The resulting long exact sequence contains <a id="eq-rowinduction"></a>

$$\label{eq:rowinduction}
 (H_{i+1}^{r,N-1}(\alpha))^{r-1}
 \longrightarrow H_i^{r,N}(\alpha)
 \longrightarrow\bigoplus_a H_i(\sigma'_b:b\ne a;T)_\alpha.$$ Fix a row $a$ in the right-hand term. Its row sum has been omitted, so the differential does not change the row-$a$ part $\mu$ of a coefficient monomial. This monomial has degree $\alpha_a$ and occupies $s(\mu)\le\alpha_a$ columns. All other rows must avoid those columns. Consequently $$H_i(\sigma'_b:b\ne a;T)_\alpha
 \cong\bigoplus_{\deg\mu=\alpha_a}
 H_i^{r-1,N-1-s(\mu)}(\alpha_{\widehat a}).$$ Repeated powers and repeated use of a row are allowed in this decomposition.

Induct on $r$, and, at fixed $r$, downwards on $i$. For one row the ring is a polynomial ring and its nonzero row sum is a nonzerodivisor; homology above index one is automatically zero. Zero-row strands also have no positive homology. If $N\ge q+r-i$, the left term of [Equation eq:rowinduction](chapters/02_graded.md#eq-rowinduction) vanishes by downward induction since $N-1\ge q+r-(i+1)$. Each right summand vanishes because $$N-1-s(\mu)\ge(q-\alpha_a)+(r-1)-i.$$ Exactness forces the middle term to vanish. *End of proof.*

<a id="cor-koszul"></a>

### Corollary 2.3: Corrected item (a): Koszul range

For any number of rows and $n$ columns, $$H_i(\rho;S_{m,n})_j=0
 \quad\text{if }i\ge1\text{ and }2j-1\le n.$$

**Proof.** A row multidegree of total degree $j$ has at most $r\le j$ positive coordinates. Rows with zero coordinate cannot occur in a coefficient monomial or an exterior generator, so the strand is the $r$-row strand of [Lemma 2.2](chapters/02_graded.md#lem-multigraded). Since $j+r-i\le2j-1$, that lemma applies. Sum over all row multidegrees. *End of proof.*

<a id="lem-hilbert"></a>

### Lemma 2.4: Initial Hilbert function and $z$-injectivity

For $m=n+1$ and $0\le d\le\lfloor(n+1)/2\rfloor$, $$\boxed{\dim_k\overline B_d=\binom nd n^d.}$$ For $1\le d\le\lfloor(n+1)/2\rfloor$, multiplication by $z$ maps $\overline B_{d-1}$ injectively into $\overline B_d$. In particular, $z^d\ne0$ in this range. No characteristic restriction is needed.

**Proof.** Put $\ell_i=\rho_i-\rho_1$ for $i\ge2$. An invertible change of generators identifies $K(\rho;S)$ with $K(\ell,z;S)$. Appending $z$ is the mapping cone of multiplication by $z$ on $K(\ell;S)$. Its long exact sequence contains $$H_i(\ell;S)_{d-1}\xrightarrow{z}H_i(\ell;S)_d
 \longrightarrow H_i(\rho;S)_d
 \longrightarrow H_{i-1}(\ell;S)_{d-1}.$$ Starting at internal degree zero, [Corollary 2.3](chapters/02_graded.md#cor-koszul) and induction on $d$ give $H_i(\ell;S)_d=0$ for every $i\ge1$ in the stated range.

One column has Hilbert series $1+mt/(1-t)=(1+(m-1)t)/(1-t)$. Independent columns tensor, hence $$\mathop{\mathrm{Hilb}}_S(t)=\frac{(1+nt)^n}{(1-t)^n}.$$ The Euler series for the Koszul complex on the $n$ row differences is $(1-t)^n\mathop{\mathrm{Hilb}}_S(t)=(1+nt)^n$. Positive homology vanishes in the range under consideration, so its coefficients there equal those of $H_0=\overline B$. This gives the Hilbert function. Finally the long exact sequence has $H_1(\rho;S)_d\to\overline B_{d-1}\xrightarrow{z}\overline B_d$; its first term is zero. Since $\overline B_0=k$, repeated injectivity proves $z^d\ne0$. *End of proof.*

<a id="lem-weakcount"></a>

### Lemma 2.5: The weak restriction count is automatic

Let $L_1,\ldots,L_t$ be arbitrary linear forms in $\overline B$. In the range of [Lemma 2.4](chapters/02_graded.md#lem-hilbert), $$\dim(\overline B/(L_1,\ldots,L_t))_d
 \ge \binom n{d-1}n^{d-1}
 \left(\frac{n(n-d+1)}d-t\right).$$ In particular this dimension is positive for $t<n$ and $1\le d\le\lfloor(n+1)/2\rfloor$.

**Proof.** The generated degree-$d$ subspace is the image of $\overline B_{d-1}^{\oplus t}\to\overline B_d$, $(h_s)\mapsto\sum_sL_sh_s$. Its rank is at most $t\dim\overline B_{d-1}$. Subtract and use the ratio $\dim\overline B_d/\dim\overline B_{d-1}=n(n-d+1)/d\ge n$. *End of proof.*

<a id="lem-affinefeasibility"></a>

### Lemma 2.6: Affine feasibility and its quadratic form

For linear forms $L_1,\ldots,L_t$, the following are equivalent: $$z^d\notin(L_1,\ldots,L_t)\overline B,\qquad
 \exists\lambda:\overline B_d\to k:\ 
 \lambda(z^d)=1,\quad \lambda(L_s\overline B_{d-1})=0.$$ At $d=2$, this is equivalent to a symmetric bilinear form $B$ on $\overline B_1$ such that $$B(x_{ij},x_{i'j})=0\ (i\ne i'),\qquad
 L_s\in\mathop{\mathrm{rad}}B,\qquad B(z,z)=1.$$

**Proof.** The first equivalence is finite-dimensional separation of the degree-$d$ relation image from $z^d$. At degree two, a functional on the symmetric square of $\overline B_1$ is the same as a symmetric bilinear form via $B(v,w)=\lambda(vw)$, including in characteristic two. It descends to $\overline B_2$ exactly when it kills the column-exclusion quadratics. Killing the $L_s$ multiples is exactly the radical condition, and normalization is $B(z,z)=1$. *End of proof.*

## The generic annihilating functional

<a id="lem-special-columns"></a>

### Lemma 2.7: A special maximal-rank restriction family

Suppose $t+2d-1\le n$. Let $\sigma_s=\sum_i x_{is}$ be the sums of the first $t$ columns. Then $$H_i(\ell_2,\ldots,\ell_{n+1},\sigma_1,\ldots,\sigma_t;S)_j=0
 \quad(i\ge1,\ j\le d),$$ and $z^d$ survives the quotient by these linear forms.

**Proof.** In one column $C_m$, multiplication by $\sigma=\sum_i y_i$ is injective: write an element uniquely as a constant plus $\sum_i f_i(y_i)$ with $f_i(0)=0$ and compare the separate-axis monomials in its product with $\sigma$. Moreover $$C_m/(\sigma)\cong k\oplus V,\qquad \dim V=m-1,\qquad V^2=0,$$ because $\sigma y_i=0$ forces $y_i^2=0$. The different $\sigma_s$ are in separate tensor factors and form a regular sequence. The quotient is $$T=S_{m,n-t}\otimes Q,\qquad Q=(k\oplus V)^{\otimes t}.$$ In $T$, a full row sum is $\rho'_i+u_i$ with $\rho'_i$ on the remaining columns and $u_i\in Q_1$. Filter its Koszul complex by $Q$-degree. The part preserving that degree is the row-sum complex on $S_{m,n-t}$, tensored with a graded piece of $Q$. By [Corollary 2.3](chapters/02_graded.md#cor-koszul) it has zero positive homology through degree $d$.

For completeness, a positive-index cycle can be killed by taking its lowest $Q$-degree part, writing that part as a boundary in the associated graded complex, subtracting the corresponding full boundary, and repeating. At fixed total degree the filtration is finite. This proves positive homology vanishing for the full row sums in $T$, equivalently for $(\rho,\sigma)$ in $S$.

Replace $\rho$ by $(\ell,z)$ and use the mapping-cone argument from [Lemma 2.4](chapters/02_graded.md#lem-hilbert). It proves both vanishing for $(\ell,\sigma)$ and injectivity of $z$ in its quotient through degree $d$. The degree-zero quotient is $k$, so $z^d$ survives. *End of proof.*

<a id="thm-generic"></a>

### Theorem 2.8: Generic survival with an explicit determinant

For $t+2d-1\le n$, there is a nonzero polynomial $\Delta$ in the coefficients of $t$ linear forms $L_s$ such that, whenever $\Delta\ne0$, a functional $\lambda:\overline B_d\to k$ satisfies $$\lambda(z^d)=1,\qquad
 \lambda(L_su)=0\quad(s\le t,\ u\in\overline B_{d-1}).$$ The nonvanishing locus contains a specified $k$-rational point: the first $t$ column sums.

**Proof.** In the monomial basis of $S_d$, let $A(C)$ have columns $\ell_i\mu$ and $L_s(C)\mu$, for every degree-$(d-1)$ basis monomial $\mu$. Let $v$ be the coordinate vector of $\rho_1^d$. At the column-sum array $C_0$, put $r=\mathop{\mathrm{rank}}A(C_0)$. By [Lemma 2.7](chapters/02_graded.md#lem-special-columns), $v\notin\mathop{\mathrm{im}}A(C_0)$.

Let $B(C)$ be the preceding Koszul differential into the domain of $A(C)$. The chain identity gives $A(C)B(C)=0$. At $C_0$, exactness at this domain gives $$\mathop{\mathrm{rank}}A(C_0)+\mathop{\mathrm{rank}}B(C_0)=\dim K_{1,d}.$$ Over $k(C)$ both ranks are at least their specialized values, because a minor nonzero at $C_0$ is a nonzero polynomial. Their sum can never exceed $\dim K_{1,d}$. Neither can increase, so the generic rank of $A$ is $r$, and every specialization has rank at most $r$.

Choose $r$ columns $J$ of $A(C_0)$ that are independent, then $r+1$ row positions $R$ such that $$\Delta(C)=\det[\,A(C)_{R,J}\mid v_R\,]$$ is nonzero at $C_0$. For a degree-$d$ polynomial $f$ define <a id="eq-detfunctional"></a>

$$\label{eq:detfunctional}
 \lambda_C([f])=
 \frac{\det[\,A(C)_{R,J}\mid [f]_R\,]}{\Delta(C)}.$$ It is linear in $f$ and takes value one on $v$. When $\Delta(C)\ne0$, the selected $r$ columns span the entire relation image, since its rank is at most $r$. Substituting any relation into the last column makes the numerator zero. Thus the functional descends through all the required relations. *End of proof.*

<a id="cor-affinegeneric"></a>

### Corollary 2.9: Affine design from the homogeneous witness

For $f=\sum_{e=0}^df_e$ with homogeneous $f_e$, the formula $$\Lambda_C(f)=\lambda_C\left(\sum_{e=0}^dz^{d-e}f_e\right)$$ is normalized and annihilates all degree-at-most-$d$ multiples of column exclusion, $\rho_i-1$, and the chosen $L_s=0$ equations.

**Proof.** Homogenize to degree $d$. A row-normalization multiple contains $\rho_i-z$, zero in $\overline B$; a restriction multiple lies in the relation image of [Theorem 2.8](chapters/02_graded.md#thm-generic); column products are already zero. The constant one homogenizes to $z^d$. *End of proof.*

<a id="lem-linearobstructions"></a>

### Lemma 2.10: Why genericity and dimension are insufficient

One unrestricted form can kill the target: $L_1=z$ implies $z^d=0$ in the quotient. Even excluding $z$ from the linear span of the restrictions does not suffice. For $n\ge2$, take $$L_1=z-x_{11},\qquad L_2=z-x_{21}.$$ Their span does not contain $z$, but $z^2\in(L_1,L_2)\overline B$.

**Proof.** The first assertion is $z^d=L_1z^{d-1}$. For the second, $$zL_1+x_{11}L_2=z^2-x_{11}x_{21}=z^2.$$ To check the linear-span claim, compare coefficients modulo the row-difference subspace: within each row a combination of row sums has equal coefficients in every column. A combination $a(z-x_{11})+b(z-x_{21})=z$ would force the column-1 coefficient deviations in the first two rows to be zero, hence $a=b=0$, after which $z=0$ would be required in degree one. But [Lemma 2.4](chapters/02_graded.md#lem-hilbert) gives $z\ne0$. *End of proof.*

<a id="scope"></a>

##### Scope

A nonzero $\Delta$ over $\mathbb F_p$ need not be nonzero on every constrained family of $\mathbb F_p$-points. The known good point $C_0$ need not lie in the coefficient family arising from an extension construction. The surviving quotient can be large while its distinguished element has already died. These facts are why the later chapters change the object being constructed.


---

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

Otherwise choose $i,q$ with $\lambda(qg_i)\ne0$. By [Equation eq:selectorlinear](chapters/01_foundations.md#eq-selectorlinear), some $\alpha\ne0$ has $\lambda(q\chi_\alpha(g_i))\ne0$. Set $$W=q\chi_\alpha(g_i),\qquad \beta_{1,i}=\alpha^{-1},
 \qquad \beta_{u,j}=0\text{ otherwise}.$$ Its degree is at most $c(D)$. Every companion becomes $g_j(1-\alpha^{-1}g_i)$, and [Equation eq:selectorproduct](chapters/01_foundations.md#eq-selectorproduct) gives $$WE_j(y,\beta)=\alpha^{-1}qg_j(g_i^p-g_i)\in J_{\mathrm{fld}}.$$ This is ideal membership before applying a functional, so it remains true after every allowed multiplier. The entire weighted substituted axiom multiple has degree at most $D+c(D)$ and is annihilated by [Lemma 1.5](chapters/01_foundations.md#lem-fieldreduction). Old-axiom multiples are annihilated directly within that budget. New field equations vanish at $\beta$, and dividing by $\lambda(W)$ normalizes the result. *End of proof.*

<a id="lem-levelrepair"></a>

### Lemma 3.2: A whole level with exact simultaneous repair

For same-level blocks $a$, define $c_a(D)$ by [Equation eq:repaircost](chapters/03_reweighting.md#eq-repaircost). A degree $$\boxed{B=D+\sum_a c_a(D)}$$ old design suffices for a degree-$D$ design of the complete level. The final weight has degree at most the sum of the costs of the blocks actually repaired.

**Proof.** Start with $W=1$ and no committed blocks. Test the moments $\lambda(Wqg_{a,i})$ for all uncommitted blocks and their allowed monomials. If all are zero, assign all uncommitted new variables zero and stop. Otherwise choose a nonzero moment. As in [Lemma 3.1](chapters/03_reweighting.md#lem-repair), choose $\alpha\ne0$ preserving nonzero value and replace $$W\leftarrow Wq\chi_\alpha(g_{a,i}).$$ Assign the selected coefficient in block $a$ the value $\alpha^{-1}$, all its others zero, and commit that block. Recheck every uncommitted block after this change.

A committed block has acquired an actual field-ideal identity, so multiplying $W$ later cannot invalidate it. An uncommitted zero specialization is used only after checking its moments against the *final* weight. Each repair commits a new block, so the procedure terminates. The selector identity guarantees $\lambda(W)\ne0$ at every update. Degrees add by at most $c_a(D)$ at the unique repair of block $a$. The proof of [Lemma 3.1](chapters/03_reweighting.md#lem-repair) then verifies all final design equations. *End of proof.*

<a id="cor-repairbudget"></a>

### Corollary 3.3: Simple budgets and level composition

If $h\ge p-2$, then $c_a(D)\le\max\{0,D-h\}$. A level of $s$ blocks costs at most $$D+s\max\{0,D-h\}\le (s+1)D.$$ For several levels, choose budgets backwards: $$D_\ell=D,\qquad D_{j-1}=D_j+\sum_{a\text{ in level }j}c_a(D_j).$$ A degree-$D_0$ base design lifts through all levels. A rough bound is $D_0\le D\prod_j(1+s_j)$ under the displayed accuracy condition.

**Proof.** For active $i$, $D-e_{a,i}+(p-1)\delta_{a,i}
=D-h-h\delta_a+(p-2)\delta_{a,i}\le D-h$. The one-level result then applies successively. At every new level all preceding axioms, including their field equations, are old axioms with their original degrees. *End of proof.*

## One shared weight for every block and level

<a id="lem-sharedfeatures"></a>

### Lemma 3.4: Common-feature conditioning

Suppose every input in a leveled system satisfies $$g_{a,i}(x,r_{<a})\equiv
 G_{a,i}(f_1(x),\ldots,f_R(x),r_{<a})\pmod J,$$ where $J$ is either the old Boolean/field ideal or the Boolean column-exclusive ideal of [Lemma 1.7](chapters/01_foundations.md#lem-columnnf). Put $\kappa=(p-1)\sum_{\nu=1}^R\deg f_\nu$. A degree-$(D+\kappa)$ base design lifts to the entire leveled system at degree $D$, using one weight and scalar values for every extension variable.

**Proof.** For $\alpha\in\mathbb F_p^R$ put $W_\alpha=\prod_\nu\chi_{\alpha_\nu}(f_\nu)$. Their sum is one by [Equation eq:selectorpartition](chapters/01_foundations.md#eq-selectorpartition), and their degrees are at most $\kappa$. Some $W=W_\alpha$ has $\lambda(W)\ne0$.

On its selected cell all $f_\nu$ are constants. Proceed level by level. After earlier variables have scalar values, every input in a new block has a scalar value $b_i$ on this cell. If all $b_i=0$, set the block's variables to zero. Otherwise choose $b_j\ne0$, set $r_{1,j}=b_j^{-1}$ and the rest zero. Every companion vanishes on that same cell. Thus $WE_{a,i}(x,\beta)\in J$ for every block, at every level.

Use $\Lambda(P)=\lambda(WP(x,\beta))/\lambda(W)$. Its weighted images have degree at most $D+\kappa$. The degree-bounded reduction lemma for $J$ proves annihilation of all extension multiples. Old axioms and new field equations are handled as in [Lemma 3.1](chapters/03_reweighting.md#lem-repair). The weight never changes between levels. *End of proof.*

<a id="cor-greedycell"></a>

### Corollary 3.5: Greedy selection of a nonzero cell

With oracle access to $\lambda$, a nonzero shared cell can be selected with at most $pR$ value queries; enumeration of all $p^R$ cells is unnecessary.

**Proof.** If a prefix weight $W'$ has nonzero value, then $\sum_{\alpha\in\mathbb F_p}\lambda(W'\chi_\alpha(f_\nu))=\lambda(W')\ne0$. At least one of the $p$ possible next values preserves it. Repeat for all features. *End of proof.*

<a id="lem-columnconditioning"></a>

### Lemma 3.6: A whole PHP column costs one degree

In the Boolean column-exclusive ring define $$e_{j,0}=1-\sum_i x_{ij},\qquad e_{j,i}=x_{ij}\ (i\ge1).$$ These are the indicators of the empty and occupied states of column $j$. If every extension input depends on original variables only through a common set of $q$ columns, a degree-$(D+q)$ base design lifts to every level at degree $D$.

**Proof.** The indicators partition one and have degree one. For a state choice on the $q$ columns, take the product of its $q$ indicators. These weights partition one and have degree at most $q$. A weight of nonzero design value fixes the complete states of all those columns. Apply the proof of [Lemma 3.4](chapters/03_reweighting.md#lem-sharedfeatures) with these weights. No row-exclusion equation is used. *End of proof.*

<a id="scope"></a>

##### Scope

Conditioning on all $n$ columns always determines the old assignment, but costs $D+n$. This is outside the available $\lfloor n/2\rfloor$ starting budget and is not a solution of the payoff problem. Small shared-feature descriptions are sufficient hypotheses, not properties proved for arbitrary extension data.


---

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

**Proof.** By [Equation eq:factorzero](chapters/01_foundations.md#eq-factorzero), $Z$ is a product of $(p-1)R$ factors $1-\alpha^{-1}f_\nu$. Partition them into $h$ groups of at most $Q=\lceil(p-1)R/h\rceil$ factors. For a group ordered as $(\alpha_\ell,\nu_\ell)$, define the coefficient of $f_\nu$ by $$\beta_{u,\nu}=
 \sum_{\ell:\nu_\ell=\nu}\alpha_\ell^{-1}
 \prod_{v<\ell}(1-\alpha_v^{-1}f_{\nu_v}).$$ The identity $1-\prod_{\ell=1}^b(1-a_\ell)=\sum_{\ell=1}^b a_\ell\prod_{v<\ell}(1-a_v)$ proves the group formula, and the largest coefficient uses at most $Q-1$ inputs. An empty group uses zero coefficients. Convert the chosen basis back to original input coordinates by constants. Finally, $f_\nu Z=(f_\nu-f_\nu^p)\prod_{\mu\ne\nu}(1-f_\mu^{p-1})\in J_{\mathrm{fld}}$; linearity gives the assertion for every $g_i$. *End of proof.*

<a id="lem-packedlift"></a>

### Lemma 4.2: A level costs a maximum, not a sum

For blocks $a$ let $R_a$ and $\delta_a$ be their input ranks and degree bounds, and put $$T_a=\max\left\{1,\delta_a
 \left(\left\lceil\frac{(p-1)R_a}{h_a}\right\rceil-1\right)_+\right\},
 \qquad T=\max_aT_a.$$ A degree-$TD$ old design lifts to a degree-$D$ design for the entire level via $$\Lambda(P)=\lambda(P(y,\beta(y))).$$ It preserves all old moments through degree $D$.

**Proof.** Use [Lemma 4.1](chapters/04_packing.md#lem-packedcoeff) in every block simultaneously. All substituted variables depend only on old variables, so no within-level nesting occurs and a degree-$D$ polynomial has image degree at most $TD$. Extension images belong to $J_{\mathrm{fld}}$, and a new field equation has image $\beta^p-\beta\in J_{\mathrm{fld}}$. Degree-bounded reduction handles their multiples. Old axioms remain old-axiom multiples. Substitution fixes old polynomials and one. *End of proof.*

<a id="cor-packingvariants"></a>

### Corollary 4.3: Variants and level composition

If the basis inputs are Boolean-valued modulo $J_{\mathrm{fld}}$, replace $(p-1)R_a$ by $R_a$. Only active companions need be spanned when constructing a degree-$D$ design. Across levels the sufficient degree is $D\prod_jT_j$. For affine inputs over $\mathbb F_2$, rank $R_a\le2h_a$ gives $T_a=1$, regardless of the number of blocks.

**Proof.** For a Boolean-valued $f$, use $1-f$ instead of $1-f^{p-1}$. Inactive companions have no permitted multipliers, so a zero test for the active inputs suffices. Compose degree inflation one level at a time, retaining the original axiom degrees. For affine inputs and $R_a\le2h_a$, $\lceil R_a/h_a\rceil-1\le1$. *End of proof.*

<a id="lem-hybrid"></a>

### Lemma 4.4: Packing plus repair

Fix $\tau\ge1$. Pack all blocks with $T_a\le\tau$, and reserve the others for scalar repair. Define $$c_a^{(\tau)}(D)=\max\left(\{0\}\cup
 \{\tau(D-e_{a,i})+(p-1)\delta_{a,i}:e_{a,i}\le D\}\right).$$ A sufficient old-design degree is $$\boxed{B_{\rm hybrid}(D)=
 \min_{\tau\ge1}\left[\tau D+\sum_{a:T_a>\tau}c_a^{(\tau)}(D)\right].}$$ In particular it is no worse than either $D+\sum_ac_a(D)$ or $D\max_aT_a$.

**Proof.** After packed substitutions an allowed cofactor of $E_{a,i}$ has old-variable degree at most $\tau(D-e_{a,i})$. In the repair procedure of [Lemma 3.2](chapters/03_reweighting.md#lem-levelrepair), test all moments $\lambda(Wqg_{a,i})$ up to that enlarged degree. Each repair costs at most $c_a^{(\tau)}(D)$. Packed blocks already vanish modulo $J_{\mathrm{fld}}$, so reweighting cannot spoil them. The final weighted substituted polynomial has degree at most $\deg W+\tau D$. At $\tau=1$ this only deletes costs from the old repair bound; at $\tau=\max T_a$ no repaired blocks remain. Between consecutive $T_a$ values the displayed cost is nondecreasing, so only those thresholds and $1$ need be tested. *End of proof.*

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

**Proof.** Let $Q_i=\prod_j(1-x_{ij})$. The annihilation assumptions imply $WP_i=Q_iWP_i$, and $Q_iP_i=Q_i$ because $Q_ix_{ij}=0$. Hence $WP_i=WQ_i$ in $A$. Choose a column-exclusive assignment where $W\ne0$. Since there are $n+1$ rows and only $n$ columns, some row $i$ is empty there; then $WQ_i\ne0$. By [Lemma 4.7](chapters/04_packing.md#lem-emptyrowsupport), $n\le\deg(WP_i)\le\deg W+h(L+1)$. For $L\ge1$, add $DL-h(L+1)$ to this bound and use $D\ge2h+1$; the minimum occurs at $L=1$, giving $n+D-2h$. For $L=0$, the stronger bound $\deg W+D\ge n+D-h$ holds. *End of proof.*

<a id="cor-rowfree"></a>

### Corollary 4.9: The obstruction is representational, not intrinsic

The same family has a degree-preserving lifting when the row equations are used. Set $r_{i,1,j}=1$ for every $j$ and all other factors' coefficients to zero. Then $$E_{i,j}(x,\beta)=-x_{ij}(\rho_i-1).$$ Every degree-$D$ base design lifts by constant substitution.

**Proof.** The selected factor is $1-\rho_i$. Its product with $x_{ij}$ has a degree-two base-axiom certificate, below the companion's original degree $2h+1$. Every permitted multiple therefore lies within the original degree budget. This uses the row axiom, which was deliberately excluded from $J$ in [Theorem 4.8](chapters/04_packing.md#thm-columnbarrier). *End of proof.*

<a id="scope"></a>

##### Scope

The lower bound in [Theorem 4.8](chapters/04_packing.md#thm-columnbarrier) is sharp as a bound on that pointwise packing architecture. For $q=n-2h\ge0$, use $W=\prod_{j=1}^{q}x_{jj}$. On selected rows use $1-x_{ii}$. On each other row pair the remaining $2h$ columns, using coefficients $1$ and $1-x_{ia}$ on a pair $(a,b)$; their factor is $(1-x_{ia})(1-x_{ib})$. This gives $\deg W=n-2h$ and $T=1$. It does not promise $\lambda(W)\ne0$ for a prescribed design; it establishes sharpness of the algebraic degree constraint only.


---

<!-- Generated from ../latex/05_baseaware.tex. Do not silently edit this reading copy. -->

<a id="ch-baseaware"></a>

# 5. Low-degree certificates using the base axioms

> Vanishing modulo field equations alone is stronger than necessary. A short certificate using a row or column axiom can make an otherwise expensive block free. The results here explain both the gain and the limits of this substitution-based route.

<a id="lem-certificate-scalar"></a>

### Lemma 5.1: Certificate-based scalar lifting

Let $\lambda$ be a degree-$D$ design for $\mathcal F$. Suppose a scalar assignment $\beta$ has, for every active extension axiom of original degree $e_E$, a certificate $$E(y,\beta)=\sum_{f\in\mathcal F}A_{E,f}(y)f(y),
 \qquad\deg(A_{E,f}f)\le e_E.$$ Then $\Lambda(P)=\lambda(P(y,\beta))$ is a degree-$D$ design for the augmented system.

**Proof.** For $\deg(HE)\le D$, the specialized cofactor has degree at most $D-e_E$. Multiply the displayed certificate by that cofactor. Each resulting summand is an old-axiom multiple of degree at most $D$. Old axioms are preserved, new field equations vanish, and normalization is unchanged. *End of proof.*

<a id="lem-affineinverse"></a>

### Lemma 5.2: An affine change of generators makes a block free

Let $v$ be either all variables of one PHP row or a nonempty subset of variables from one column. Suppose the input tuple satisfies $$g=M(y)v,\qquad N(y)M(y)=I,$$ where both $M,N$ have affine-linear entries in old variables. A degree-$D$ design for the old system extends at the same degree over the block, preserving all old moments. This can be done simultaneously for any number of eligible same-level blocks and iterated through levels.

**Proof.** Set $b^{\mathsf T}=\mathbf1^{\mathsf T}N$, substitute $r_{1,a}=b_a(y)$, and set all other factor coefficients to zero. Then $$\sum_ab_ag_a=\mathbf1^{\mathsf T}NMv=\sum_jv_j,
 \qquad E_a(y,b)=g_a\left(1-\sum_jv_j\right).$$ For a row source this is $-g_a(\rho_i-1)$, a certificate of degree at most three. For a column source, put $s=\sum_jv_j$. Then $$v_j(1-s)=-(v_j^2-v_j)-\sum_{k\ne j}v_jv_k,$$ so $$E_a(y,b)=-\sum_jM_{aj}(v_j^2-v_j)
          -\sum_j\sum_{k\ne j}M_{aj}v_jv_k.$$ All summands have degree at most three. Every nonzero $g_a$ has positive degree, and its original companion degree is at least three, so all permitted cofactor multiples remain within $D$.

The substitution is affine, hence does not increase degrees. For a new field equation, if $b=c+\sum_j a_jy_j$ then $$b^p-b=\sum_j a_j(y_j^p-y_j).$$ For a Boolean old variable, $y^p-y=(y^2-y)(1+y+\cdots+y^{p-2})$; for an old field variable it is already an axiom. These certificates fit degree $p$, the degree of the new field axiom.

Thus $\Lambda(P)=\lambda(P(y,b(y)))$ is a design and fixes old moments. Same-level substitutions depend only on old variables. Across levels, compositions of affine substitutions remain affine, and preceding axioms are included among the old axioms, proving the simultaneous and iterative statements. *End of proof.*

<a id="example-5-3"></a>

### Example 5.3: Globally nonlinear tuples with a free lifting

Take $M=I+A(y)$ with affine entries and $A^2=0$, so $N=I-A$. One way to ensure $A^2=0$ is to allow entries only from one index class into a disjoint class. For a complete row, an elementary example is $$g_1=x_{i1}+L(y)x_{i2},\quad g_2=x_{i2},\quad g_j=x_{ij}\ (j\ge3),$$ with arbitrary affine $L$, possibly involving all old variables. Choose coefficients $1$, $1-L$, and $1$ for the remaining inputs in the first factor. The selected linear combination of inputs is exactly $\rho_i$, so every companion is $-g_a(\rho_i-1)$. Polynomially many such blocks can be eliminated at no degree cost. The conclusion is conditional on the displayed algebraic structure, not a normal-form theorem for arbitrary tuples.

<a id="lem-certificatebarrier"></a>

### Lemma 5.4: A low-degree base-certificate obstruction to universal selectors

Fix $2q\le n$ and one block with inputs $g_a=x_{a,2a-1}$, $a\le q$. Suppose substitutions of maximum degree $T$ make every companion a consequence of $\mathcal F_n$ with an original-axiom certificate of degree at most $C$. Assuming the degree-$C$ residual PHP designs supplied by Imported Input [Imported input 10.1](chapters/10_route.md#imp-php), if $$C\le\left\lfloor\frac{n-q}{2}\right\rfloor,$$ then $q\le h(T+1)$.

**Proof.** Expose independent Boolean choices $t_a$: assign pigeon $a$ to hole $2a-1$ when $t_a=1$, and to hole $2a$ when $t_a=0$. For each remaining pigeon $i>q$ use common residual variables $z_{i,a}$ and set $$x_{a,2a-1}=t_a,\quad x_{a,2a}=1-t_a,\qquad
 x_{i,2a-1}=(1-t_a)z_{i,a},\quad x_{i,2a}=t_a z_{i,a}.$$ All other variables are set or relabeled in the usual partial-matching restriction. For each fixed Boolean $t$, the base system becomes the same labeled PHP with $n-q$ holes. Choose one degree-$C$ design $\mu$ for that residual system.

Let $P(x)=\prod_u(1-\sum_a\beta_{u,a}(x)x_{a,2a-1})$. Since each nonzero $x_{a,2a-1}P$ has a degree-$C$ certificate, $\deg P\le C-1$. The parameterized substitution does not increase degree in the residual variables, so $$R(t)=\mu(P(x(t,z)))$$ is defined. Each original variable has $t$-degree at most one, hence $\deg R\le h(T+1)$.

Apply $\mu$ to the restricted certificates. For every Boolean $t$, they imply $t_aR(t)=0$ for all $a$. At $t=0$, all inputs are zero, so $P=1$ and $R(0)=1$. The unique multilinear representative of this Boolean function is $\prod_a(1-t_a)$, of degree $q$. Multilinear reduction cannot increase degree, proving the inequality. *End of proof.*

<a id="scope"></a>

##### Scope

Taking $q$ proportional to $n$ and $h=O(\log n)$ forces $T=\Omega(n/\log n)$ in this unconditioned substitution-and-certificate model. A single selected cell can nevertheless be fixed to one to kill this block after changing the base moments. Thus the obstruction is not to every conditional or joint-functional construction.


---

<!-- Generated from ../latex/06_moments.tex. Do not silently edit this reading copy. -->

<a id="ch-moments"></a>

# 6. Joint moments and full-group interactions

> Unnormalized component functionals can combine to a normalized design. The first construction handles arbitrary numbers of blocks in a degree window. Adding a support factor handles all cofactors for a fixed number of blocks, at a larger compositional cost.

## Diagonal coefficient operators

Work first over $\mathbb F_2$, and assume Boolean equations for every old variable. For block $a$ and input index $j$, define $$T_{a,j}(P)=[t_1\cdots t_h]\,
 P(y,r_{a,u,j}=t_u,\ r_{\rm other}=0),$$ where the auxiliary $t$ variables are reduced by $t_u^2=t_u$ before coefficient extraction. Old variables are not substituted. This is a linear operator, not a ring homomorphism.

<a id="lem-coefficient"></a>

### Lemma 6.1: Degree removal and the coefficient formula

The operator $T_{a,j}$ vanishes on old-only polynomials and maps degree $D$ to old-variable degree at most $D-h$. If a monomial cofactor specializes to $q(y)t_S$, then $$T_{a,j}(HE_{a,i})=
 qg_{a,i}(1-g_{a,j})^{|S|}(-g_{a,j})^{h-|S|}.$$ If the cofactor specializes to zero, so does the displayed coefficient.

**Proof.** Every contributing monomial must supply at least one new variable from each of the $h$ groups, removing at least $h$ degrees. In a group already present in $t_S$, the coefficient of $t_u$ in $t_u(1-t_ug)$ after reduction is $1-g$; in an absent group it is $-g$. Multiply these $h$ contributions. *End of proof.*

<a id="thm-window"></a>

### Theorem 6.2: Degree-window lifting over $\mathbb F_2$

Let one level have arbitrary input tuples and common accuracy $h$. Suppose every active nonzero companion satisfies $$D-h<e_{a,i}\le D.$$ Every degree-$D$ old design extends to a degree-$D$ design of the complete level, preserving all old moments. The number of blocks and their fan-ins are unrestricted.

**Proof.** Set $M=D-h$. In block $a$, put $\delta_a=\max_j\deg g_{a,j}$, $s_a=D-h(\delta_a+1)$, and let $V_a$ consist of $$G=\sum_{i\ {
m active}}q_i g_{a,i},\qquad\deg q_i\le D-e_{a,i}.$$ Then $\deg G\le s_a$ and $Gg_{a,j}$ fits degree $M$.

Seek unnormalized functionals $\mu_{a,j}$ on $\mathbb F_2[y]_{\le M}$ annihilating $\mathcal I_{M}(\mathcal F)$ and satisfying <a id="eq-window-components"></a>

$$\label{eq:window-components}
 \sum_j\mu_{a,j}(Gg_{a,j})=\lambda(G)\quad(G\in V_a).$$ Here and below, $\mathcal I_{M}$ abbreviates $\mathcal I_M$. These equations are consistent exactly when $Gg_{a,j}\in\mathcal I_{M}(\mathcal F)$ for every $j$ implies $\lambda(G)=0$: this is linear separation on the image of $G\mapsto([Gg_{a,j}])_j$ in the direct sum of quotient spaces.

Write $G=\sum_iq_ig_{a,i}$ and put $k_a=\max_{i\ {
m active}}(D-e_{a,i})<h$. The kernel condition gives $$G^2=\sum_iq_i(Gg_{a,i})\in\mathcal I_{M+k_a}(\mathcal F).$$ Also $G^2-G$ is an old Boolean consequence in that degree. Explicitly, if $\delta_{\min}$ is the minimum active input degree, then $k_a=s_a-\delta_{\min}$ and $M+k_a-2s_a=h\delta_a-\delta_{\min}\ge0$. Degree-nonincreasing Boolean reduction therefore gives $G\in\mathcal I_{M+k_a}$, and $M+k_a<D$ yields $\lambda(G)=0$. This proves component existence.

Define $$\Lambda(P)=\lambda(P(y,0))+\sum_{a,j}\mu_{a,j}(T_{a,j}(P)).$$ It preserves old moments and normalization. An old-axiom multiple remains such a multiple after coefficient extraction within degree $M$. New Boolean equations reduce to zero in the auxiliary variables.

For an allowed cofactor $H$ of $E_{a,i}$, $\deg H<h$. It cannot supply all $h$ groups of a different block, so all cross-block corrections vanish. In its own block, a nonempty auxiliary support has $0<|S|<h$, and [Lemma 6.1](chapters/06_moments.md#lem-coefficient) contains both $g_{a,j}$ and $1-g_{a,j}$. Boolean reduction makes it zero. Empty support reduces to $qg_{a,i}g_{a,j}$, whose components cancel $\lambda(qg_{a,i})$ by [Equation eq:window-components](chapters/06_moments.md#eq-window-components). All reductions remain within $M$. Monomial cofactors span all allowed cofactors. *End of proof.*

<a id="cor-cofactor"></a>

### Corollary 6.3: Cofactor-sensitive lifting outside the window

Put $k=\max_{a,i\ {
m active}}(D-e_{a,i})$ and $B=\max\{D,D-h+k\}\le2D$. A degree-$B$ old design gives the same functional, annihilating every allowed extension multiple whose cofactor monomials each miss at least one factor group in every block. Consequently, if the old system has a degree-$2D$ design, every degree-$D$ augmented NS refutation must use a cofactor monomial touching all $h$ groups of some block.

**Proof.** The consistency proof above only needs an input domain through $M+k$. The stated support condition, instead of $\deg H<h$, ensures that cross-block extractions vanish and that nonempty within-block support is proper. If every cofactor in a refutation had this property, applying the constructed normalized functional to the certificate would give $1=0$. *End of proof.*

<a id="lem-oddwindow"></a>

### Lemma 6.4: The odd-characteristic window version

For $\mathbb F_p$, replace $T_{a,j}$ by $$T_{a,j,\alpha}(P)=\chi_\alpha(g_{a,j})[t_1\cdots t_h]
 P(y,r_{a,u,j}=t_u/\alpha,r_{\rm other}=0),\qquad\alpha\ne0.$$ Suppose $k_a=\max_i(D-e_{a,i})<h$ for all active blocks. Set $$M_a=D-h+(p-1)\delta_a,\quad s_a=D-h(\delta_a+1),\quad
 B_a=M_a+k_a+(p-2)s_a.$$ An old design through $\max\{D,\max_aB_a\}$ suffices for a complete degree-$D$ lifting. If $k_a\le k$ and $\delta_a\le\delta$, the simpler sufficient budget is $$D+\max\{0,(p-1)k+(2p-3)\delta-h\}.$$

**Proof.** Use components annihilating $\mathcal I_{M_a}$ with coupling equation $\sum_{j,\alpha\ne0}\mu_{a,j,\alpha}(G\chi_\alpha(g_{a,j}))=\lambda(G)$. A dual kernel condition and [Equation eq:selectorlinear](chapters/01_foundations.md#eq-selectorlinear) give $Gg_{a,j}\in\mathcal I_{M_a}$ for every $j$. Then $$G^p=\sum_iq_iG^{p-2}(Gg_{a,i})\in\mathcal I_{B_a}.$$ Since $B_a-ps_a=(h+p-1)\delta_a-\delta_{\min}\ge0$, $G^p-G$ also has a field-axiom certificate within $B_a$. The kernel condition is therefore annihilated by the input design, proving consistency.

Set $\Lambda(P)=\lambda(P(y,0))+(-1)^{h+1}\sum\mu(T_{a,j,\alpha}(P))$. On the support of $\chi_\alpha(g)$, the selected $g$ equals $\alpha$. Every nonempty proper auxiliary support thus vanishes, while empty support contributes $(-1)^hG\chi_\alpha(g)$. Cross-block terms vanish by $k_a<h$. Auxiliary Boolean values lie in $\mathbb F_p$, so new field equations also vanish. The stated simple bound uses $s_a=k_a+\delta_{\min}\le k+\delta$. *End of proof.*

## The mixed hierarchy: a sufficient open construction

<a id="ex-mixedfailure"></a>

### Example 6.5: Independent block corrections can conflict

Take two constant-input blocks $(1)$ with $h=2$ over $\mathbb F_2$. Write $R_A=r_{A,1}r_{A,2}$ and $R_B=r_{B,1}r_{B,2}$. Single-block corrections can force $\Lambda(R_A)=\Lambda(R_B)=1$ but leave $\Lambda(R_AR_B)=0$. Then $$\Lambda\bigl(R_A(1-r_{B,1})(1-r_{B,2})\bigr)=1,$$ violating the other block's annihilation equation. A mixed moment assigning $\Lambda(R_AR_B)=1$ repairs this example. Separate block feasibility does not itself supply a joint solution.

For a set $S$ of blocks and a selected input index $j_a$ for every $a\in S$, let $T_{S,J}$ extract the coefficient of all $h|S|$ corresponding auxiliary Boolean variables, setting other new variables to zero. Let $\mu_{S,J}$ be old-system functionals through degree $D-h|S|$, annihilating bounded-degree old consequences, with normalized root $\mu_\varnothing$.

<a id="lem-mixedsystem"></a>

### Lemma 6.6: A sufficient mixed-moment system

The formula $$\Lambda(P)=\sum_{S,J}\mu_{S,J}(T_{S,J}(P))$$ gives a degree-$D$ design if, throughout $\deg q\le D-e_{b,i}-h|S|$, the components satisfy <a id="eq-mixed-add"></a>

<a id="eq-mixed-revisit"></a>

$$\begin{aligned}
 \mu_{S,J}(qg_{b,i})&=\sum_j
 \mu_{S\cup\{b\},J\cup\{b\mapsto j\}}(qg_{b,i}g_{b,j})
 &&(b\notin S),\label{eq:mixed-add}\\
 \mu_{S,J}(qg_{b,i}(1-g_{b,j_b}))&=0
 &&(b\in S).\label{eq:mixed-revisit}
\end{aligned}$$ An empty multiplier range imposes no condition. Simultaneous feasibility of this full system was not established in the conversation.

**Proof.** Check a monomial cofactor. If it uses incompatible input indices within one selected block, every diagonal extraction kills it. A partial support in a block other than the axiom's block supplies too few auxiliary variables. A partial nonempty support in the axiom's own block produces both $g$ and $1-g$, hence vanishes after Boolean reduction. The remaining monomials consist of complete selected groups in a set of blocks. Their contributions are precisely [Equation eq:mixed-add](chapters/06_moments.md#eq-mixed-add) or [Equation eq:mixed-revisit](chapters/06_moments.md#eq-mixed-revisit). The degree limit accounts for the $h|S|$ new-variable factors. Old axioms and field equations are handled by the component conditions and auxiliary reductions, while normalization comes only from the root. *End of proof.*

## Supported corrections solve the full one-block problem

<a id="thm-supported"></a>

### Theorem 6.7: Moment-preserving supported lifting over $\mathbb F_2$

For one arbitrary block, put $\delta=\max_i\deg g_i$ and $$\Phi_\delta(D)=\max\{D,2D-h(\delta+2)\}.$$ Every degree-$\Phi_\delta(D)$ old design extends to a degree-$D$ design over the block, preserving all old moments. There is no restriction on cofactor support.

**Proof.** If no companion is active, zero specialization suffices. Otherwise put $a=h(\delta+1)$, $J=\{j:a+\delta_j\le D\}$, $N_j=D-h+\delta_j$, and $$V=\left\{G=\sum_{i\in J}q_ig_i:\deg q_i\le D-a-\delta_i\right\}.$$ Seek components $\nu_j$ through $N_j$ annihilating $\mathcal I_{N_j}(\mathcal F)$ with $\sum_{j\in J}\nu_j(Gg_j)=\lambda(G)$ for $G\in V$. All products fit these domains. For a dual obstruction $Gg_j\in\mathcal I_{N_j}$, write $G=\sum_iq_ig_i$. Then $$G^2=\sum_iq_i(Gg_i)\in\mathcal I_{B_0},\qquad
 B_0=N_i+(D-a-\delta_i)=2D-a-h.$$ Also $\deg(G^2-G)\le2(D-a)\le B_0$, so Boolean reduction gives $G\in\mathcal I_{B_0}$. Since the input domain covers $\max\{D,B_0\}$, the coupling equations are consistent by separation.

Define the supported correction $$\boxed{\Lambda(P)=\lambda(P(y,0))+\sum_{j\in J}\nu_j(g_jT_j(P)).}$$ It fits the domains and preserves old moments. By [Lemma 6.1](chapters/06_moments.md#lem-coefficient), a selected monomial cofactor gives $$g_jT_j(HE_i)=qg_i g_j(1-g_j)^{|S|}g_j^{h-|S|}.$$ Every nonempty $S$, including $S=[h]$, now contains the factor $g_j(1-g_j)$ and is annihilated by bounded-degree Boolean reduction. Empty support reduces to $qg_ig_j$ and cancels the base term by the coupling equation. Old-axiom multiples are old-axiom multiples in the component domains, and new Boolean equations vanish under auxiliary reduction. This covers all cofactors. *End of proof.*

<a id="lem-supported-p"></a>

### Lemma 6.8: Supported lifting over every fixed prime

With old Boolean or field equations, define $$\Phi_{p,\delta}(D)=\max\{D,
 pD-ph-((p-1)h-(p-2))\delta\}.$$ An old design through this degree gives a complete one-block degree-$D$ design preserving old moments. The bound is at most $pD$.

**Proof.** Use components indexed by active $j$ and $\alpha\ne0$, with domains $N_j=D-h+(p-1)\delta_j$, acting on $\chi_\alpha(g_j)[t_1\cdots t_h]P(r_{u,j}=t_u/\alpha)$. Give their sum sign $(-1)^{h+1}$. The coupling is $\sum_{j,\alpha}\nu_{j,\alpha}(G\chi_\alpha(g_j))=\lambda(G)$. A kernel condition yields $Gg_j\in\mathcal I_{N_j}$ by [Equation eq:selectorlinear](chapters/01_foundations.md#eq-selectorlinear). Writing $a=h(\delta+1)$ and $\deg G\le D-a$, use $$G^p=\sum_iq_iG^{p-2}(Gg_i).$$ A summand has consequence degree at most $pD-(p-1)a-h+(p-2)\delta_i$, bounded by the expression defining $\Phi_{p,\delta}$. This budget also covers $G^p-G$ and every component domain. Separation supplies the components. The support factor kills all nonempty auxiliary supports since $\chi_\alpha(g_j)(1-g_j/\alpha)\in J_{\mathrm{fld}}$. Empty support is canceled by the coupling. All old and new field equations satisfy the same reductions as before. *End of proof.*

<a id="cor-twoblocks"></a>

### Corollary 6.9: Two blocks and the first interaction boundary

Over $\mathbb F_2$, two blocks need input degree $$B=\Phi_{\delta_A}(\Phi_{\delta_B}(D))\le4D.$$ For equal input degree $\delta$ and $D=h(\delta+2)+\delta$, this is $D+3\delta$. Over $\mathbb F_p$, two blocks need at most $p^2D$. The construction permits dependencies on earlier block variables and all cross-block cofactors.

**Proof.** First lift block $A$ to the input degree needed to lift $B$. For the second application, include *all* axioms and field equations of the first block among the old system; its components may use general moments in those old variables. Thus the second old-axiom verification enforces the cross-block conditions. If $C=h(\delta+2)$ and $D=C+\delta$, two applications of $d\mapsto\max\{d,2d-C\}$ give $C+4\delta=D+3\delta$. *End of proof.*

<a id="scope"></a>

##### Scope

For $s$ equal-degree blocks and $D>C=h(\delta+2)$, this particular moment-preserving iteration costs $C+2^s(D-C)$. It solves finite-block compatibility but not affordable global lifting. It does not prove feasibility of every component system in [Lemma 6.6](chapters/06_moments.md#lem-mixedsystem); it uses a less restricted second-stage functional. The elimination method in the next chapter abandons unnecessary preservation of a prescribed base functional.


---

<!-- Generated from ../latex/07_elimination.tex. Do not silently edit this reading copy. -->

<a id="ch-elimination"></a>

# 7. Why PC closure matters, and additive elimination

> A long chain of locally simple extension blocks can defeat generic batching from ordinary designs. Polynomial-calculus closure excludes that particular obstruction and leads to an additive proof-elimination theorem. Unlike the preceding moment-preserving constructions, this argument seeks existence of a suitable joint functional, not preservation of a prescribed one.

## An explicit obstruction to batching ordinary designs

Let $G$ be a DAG with vertices $1,\ldots,N$ in topological order, a unique sink $N$, and indegree at most two. Put $$b_i=1-x_i,\quad f_i=b_i\prod_{j\in\operatorname{pred}(i)}x_j,
 \quad\mathcal F_G=\{f_i\}_i\cup\{x_N\}\cup\{x_i^2-x_i\}_i.$$ For every prefix $[k]$ add one block with inputs $b_1,\ldots,b_k$, accuracy $h$, and notation $$A_k=\prod_{u=1}^h(1-\sum_{j\le k}r_{k,u,j}b_j),\qquad
 E_{k,j}=b_jA_k,\qquad A_0=1.$$ All blocks are in one level.

<a id="lem-prefixcertificate"></a>

### Lemma 7.1: A degree-$(4h+2)$ prefix certificate

The augmented pebbling system has an exact NS refutation of degree at most $4h+2$, over every field. Each certificate summand uses variables from at most two consecutive blocks. Boolean and extension field equations are not needed in the certificate.

**Proof.** Define $$U_{k,j}=\sum_{u=1}^h r_{k,u,j}
 \prod_{v<u}(1-\sum_{\ell\le k}r_{k,v,\ell}b_\ell).$$ Product telescoping gives $1-A_k=\sum_{j\le k}U_{k,j}b_j$ and $\deg U_{k,j}\le2h-1$. Thus $$\begin{aligned}
 A_{k-1}-A_k={}&\sum_{j<k}U_{k,j}E_{k-1,j}
 +U_{k,k}b_kA_{k-1}
 -\sum_{j<k}U_{k-1,j}E_{k,j}.
\end{aligned}$$ Order the at most two predecessors of $k$ as $p_1,\ldots,p_t$. The local identity $$b_kA_{k-1}=A_{k-1}f_k+
 b_k\sum_{\ell=1}^t\left(\prod_{v<\ell}x_{p_v}\right)E_{k-1,p_\ell}$$ follows by expanding $1-\prod_{\ell=1}^tx_{p_\ell}$. Substitution expresses every consecutive difference as an axiom combination. Its largest summand degree is $(2h-1)+2h+3=4h+2$.

The differences telescope to $1-A_N$, while $A_N=A_Nx_N+E_{N,N}$. Therefore $$1=\sum_{k=1}^N(A_{k-1}-A_k)+A_Nx_N+E_{N,N}$$ is the required certificate after substituting the local expansions. The formulas show the adjacent-block support and do not use field reduction. *End of proof.*

<a id="imp-pebbling"></a>

### Imported input 7.2: Pebbling degree input

For the pebbling encoding above, NS degree equals reversible pebbling space, over every field [Pebbling Theorem 3.1](../references/README.md#pebbling). The Carlson--Savage constructions provide bounded-indegree single-sink families with polynomially growing pebbling price; the conversation used a family with $N=\Theta(r^3)$ and price $\Omega(r)$. These are published combinatorial inputs, not results proved in this document.

<a id="cor-genericbatchfalse"></a>

### Corollary 7.3: Plain high-degree designs do not justify universal batching

There is no theorem valid for every Boolean base system asserting that a base design through $(D+h+\log M)^C$, for a fixed constant $C$, always yields an augmented degree-$D$ design for one-level ENS systems with $M$ companions.

**Proof.** Use a family from Imported Input [Imported input 7.2](chapters/07_elimination.md#imp-pebbling). Its base has ordinary designs through polynomially growing degree below its NS threshold. The prefix construction has $M=N(N+1)/2$ companions and degree-$D$ refutations for $D=4h+2$. Take $h=\Theta(\log N)$, so the putative sufficient starting degree is only polylogarithmic and is eventually below the base NS threshold. The asserted augmented design would contradict [Lemma 7.1](chapters/07_elimination.md#lem-prefixcertificate). Each certificate summand still uses at most two adjacent blocks, so sparse local interaction alone does not rescue that theorem. *End of proof.*

<a id="lem-pebblingpc"></a>

### Lemma 7.4: The same pebbling base has PC degree at most three

The base system $\mathcal F_G$ has a PC refutation in degree at most three.

**Proof.** For sources, $b_i=f_i$ is an axiom. In topological order use $$b_k=f_k+b_k\sum_{\ell=1}^t b_{p_\ell}
              \prod_{v<\ell}x_{p_v}.$$ The predecessor $b_{p_\ell}$ are already derived. Multiplying their final lines as displayed costs degree at most three since $t\le2$. This derives every $b_k$, and $b_N+x_N=1$ finishes. Thus the high NS degree of the example does not imply high PC degree. *End of proof.*

## A stronger input functional

<a id="lem-pcbased"></a>

### Lemma 7.5: PC-based supported lifting

For a block of maximum input degree $\delta$ over $\mathbb F_p$, put $$\Psi_{p,\delta}(D)=\max\{D,\ D-h+(p-1)\delta,
                      \ p(D-h(\delta+1))\}.$$ A normalized functional annihilating $\mathcal C_{\Psi_{p,\delta}(D)}(\mathcal F)$ gives an ordinary degree-$D$ augmented design, preserving old moments. The output is not asserted to annihilate all augmented PC consequences.

**Proof.** Repeat the supported construction of [Lemma 6.8](chapters/06_moments.md#lem-supported-p), but require components on degree $N_j=D-h+(p-1)\delta_j$ to annihilate $\mathcal C_{N_j}(\mathcal F)$ instead of $\mathcal I_{N_j}$. In the dual kernel condition, every $Gg_j$ is already derivable through $N_j$. Write $a=h(\delta+1)$ and $G=\sum_iq_ig_i$ with $\deg G\le D-a$. By [Lemma 1.3](chapters/01_foundations.md#lem-reuse), $$G^p=\sum_iq_iG^{p-2}(Gg_i)$$ can be derived through $\max\{\max_iN_i,p(D-a)\}$: multiply the derived polynomials, not their flattened certificates. Field reduction derives $G^p-G$ within $p(D-a)$. Thus the input functional annihilates every dual kernel element, giving component consistency. The full cofactor verification is unchanged from [Lemma 6.8](chapters/06_moments.md#lem-supported-p), and yields an ordinary design. Nothing in that verification establishes closure under reuse of augmented derived polynomials, so the stronger output property is not inferred. *End of proof.*

For $p=2$, this gives $\Psi_\delta(D)=\max\{D,D-h+\delta,2D-2h(\delta+1)\}$. It is degree-preserving when $\delta\le h$ and $D\le2h(\delta+1)$. This intermediate lemma exposed the useful closure distinction; the following proof transformation handles composition directly.

## Eliminate one arbitrary block

<a id="thm-one-elimination"></a>

### Theorem 7.6: One-block additive elimination

Let $\mathcal G\subseteq\mathbb F_p[y]$ contain Boolean or field equations for every old variable. Suppose an accuracy-$h$ block has fresh variables absent from $\mathcal G$, and maximum input degree $\delta$. A degree-$d$ PC refutation of $\mathcal G\cup\mathcal E\cup\mathcal R$ yields a PC refutation of $\mathcal G$ of degree at most $$\boxed{d+(p-1)\delta.}$$ There is no fan-in factor.

**Proof.** Keep the original refutation $\pi$. Fix an input $g_j$ and $\alpha\ne0$. Set $r_{1,j}=\alpha^{-1}$ and every other new variable zero. Multiply each specialized proof line by $\chi_\alpha(g_j)$. An extension axiom maps to $$\chi_\alpha(g_j)g_i(1-\alpha^{-1}g_j)
 =\alpha^{-1}g_i(g_j^p-g_j),$$ a field-ideal polynomial. Its actual degree is bounded by the degree of the transformed original axiom line, hence by $d+(p-1)\delta$. [Lemma 1.5](chapters/01_foundations.md#lem-fieldreduction) supplies a derivation in that budget. Old axioms become old-axiom multiples, and new field equations vanish.

By [Lemma 1.4](chapters/01_foundations.md#lem-substitution), all weighted specialized inference lines can be derived within the same degree. Since the last line is one, this gives a derivation of $\chi_\alpha(g_j)$ from $\mathcal G$. Repeat over $\alpha\ne0$ and use [Equation eq:selectorlinear](chapters/01_foundations.md#eq-selectorlinear) to derive $g_j$. Do this for every input. Multiple derivations increase length, not the maximum degree.

Now specialize the original $\pi$ with all new variables zero. Every extension axiom becomes $g_i$, already derived. Reuse these final polynomials as the required starting lines. The specialized inference sequence has degree at most $d$, and the inserted input derivations have degree at most $d+(p-1)\delta$. This refutes $\mathcal G$ within the claimed budget. *End of proof.*

<a id="thm-additive"></a>

### Theorem 7.7: Additive elimination through all levels

For a leveled system with block input degrees $\delta_1,\ldots,\delta_s$, $$\boxed{\deg_{\mathrm{PC}}(\mathcal F\cup\mathcal E\cup\mathcal R)
 \ge\deg_{\mathrm{PC}}(\mathcal F)-(p-1)\sum_{a=1}^s\delta_a.}$$ Equivalently, a degree-$D$ augmented PC refutation yields a base refutation of degree at most $D+(p-1)\sum_a\delta_a$.

**Proof.** Eliminate blocks in reverse level order. Later blocks have already disappeared, so the fresh variables of the block being removed occur only in that block and its own field equations. Take all remaining axioms as the old system and apply [Theorem 7.6](chapters/07_elimination.md#thm-one-elimination). Its output is an actual PC refutation, exactly the object required for the next step. Add the degree increments. *End of proof.*

<a id="cor-pcdesign"></a>

### Corollary 7.8: Existence of a PC-annihilating joint functional

If the base has no PC refutation through degree $D+(p-1)\sum_a\delta_a$, then a normalized functional on joint polynomials of degree at most $D$ annihilates $\mathcal C_{D}(\mathcal F\cup\mathcal E\cup\mathcal R)$. In particular it is an ordinary augmented design.

**Proof.** Otherwise [Theorem 7.7](chapters/07_elimination.md#thm-additive) would yield a forbidden base refutation. Apply [Lemma 1.2](chapters/01_foundations.md#lem-duality) to the augmented PC consequence space. This is existence of a suitable functional, not extension of every preassigned base functional. *End of proof.*

<a id="lem-equalspan"></a>

### Lemma 7.9: Equal-span batches

Suppose several same-level blocks have identical polynomial input span $V$, with a basis of degree at most $\delta_V$. They can be eliminated simultaneously at degree cost $(p-1)\delta_V$. If $1\in V$, scalar specialization eliminates the whole batch at zero degree cost.

**Proof.** For each basis polynomial $f\in V$ and each block, express $f$ as a constant linear combination of that block's inputs. For a fixed $\alpha\ne0$, put the scaled coefficients into the first extension factor of every block, making the selected factor $1-\alpha^{-1}f$ everywhere. Weight the specialized original proof by $\chi_\alpha(f)$. All selected extension axioms become field consequences simultaneously. Derive the basis inputs as in [Theorem 7.6](chapters/07_elimination.md#thm-one-elimination), then derive every block input by constant linear combination. Zero-specialize the original proof and reuse them. If $1\in V$, choose coefficients making the first factor identically zero in every block, with no weight. *End of proof.*

<a id="scope"></a>

##### Scope

For $p=2$, linear inputs, $h=16$, $D=49$, ten unrelated blocks cost at most $59$ by additive elimination; ten blocks of a common span cost $50$. The earlier moment-preserving recurrence gave $48+2^{10}=1072$ for ten sequential blocks at this boundary. These are different sufficient bounds, not statements that the higher cost is necessary.


---

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

A current or later extension axiom becomes $\alpha^{-1}g_{b,i}(f^p-f)$, an old-field consequence within the weighted-line degree ceiling $B$. An earlier axiom becomes $\chi_\alpha(f)g_{b,i}$, where $g_{b,i}$ is already derived. Reuse its final polynomial and multiply it by the selector; the product degree is at most $B$ for every axiom line occurring in $\pi$. The earlier derivation itself is not multiplied. Old axioms, new field axioms, and inferences are handled by [Lemma 1.4](chapters/01_foundations.md#lem-substitution), [Lemma 1.5](chapters/01_foundations.md#lem-fieldreduction).

The transformed conclusion is $\chi_\alpha(f)$. Combining these derivations over $\alpha\ne0$ derives $f$ within $B$. Repeat for the current inputs and move on. The same original proof and the same ceiling $B$ are used at every learning stage.

Finally zero-specialize all new variables in $\pi$. Every extension axiom is now an already derived input. Reuse the derivations to get a base refutation within $B$. Unused axioms need no substitution certificate; a block absent from the used extension axioms can simply be zero-specialized. *End of proof.*

<a id="lem-nestedquotient"></a>

### Lemma 8.2: Nested modulo supplied base consequences

Let $H\subseteq k[y]_{\le\delta}$ be a vector space whose elements have supplied PC derivations from $\mathcal G$ within degree $c$. Suppose $$(V_1+H)/H\subseteq\cdots\subseteq(V_s+H)/H.$$ The batch can be eliminated within degree $$\boxed{B_H=\max\{c,D+(p-1)\delta,(p+1)\delta\}.}$$ If $c\le D$ and $D\ge2\delta$, this is $D+(p-1)\delta$.

**Proof.** A selected input now has $f=\sum_i c_{b,i}g_{b,i}+u_b$ with $u_b\in H$. The same first-factor specialization gives $$\chi_\alpha(f)E_{b,i}(y,\beta)
 =\alpha^{-1}g_{b,i}(f^p-f)
  +\alpha^{-1}\chi_\alpha(f)g_{b,i}u_b.$$ The first term is a field consequence, the second a multiple of an already derived $u_b$. Both have degree at most $(p+1)\delta$. Reuse their derivations within $B_H$; the rest of [Theorem 8.1](chapters/08_batching.md#thm-nested) is unchanged. The quotient here is a vector-space quotient backed by low-degree derivations, not the full ideal of the unsatisfiable base. *End of proof.*

<a id="cor-chaincharge"></a>

### Corollary 8.3: Global chain charge

Partition every level into nested chains $C$, with maximum input degree $\delta_C$. Eliminating in reverse level order yields $$\boxed{D_{\rm base}\le D+(p-1)\sum_C\delta_C.}$$ The quotient version uses the extra ceilings in [Lemma 8.2](chapters/08_batching.md#lem-nestedquotient). Literal equality of all spaces is the special case of a constant chain.

**Proof.** After later levels have been removed, a chosen chain is fresh for all other remaining axioms. Apply [Theorem 8.1](chapters/08_batching.md#thm-nested), treating those axioms as old. Scalar substitutions do not increase the degrees of surviving blocks. Add the increments. *End of proof.*

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

All substituted variables have degree at most $T$. Thus every transformed line has degree at most $TD+(p-1)\gamma$. Current and later extension images are old-field consequences by [Equation eq:selectorproduct](chapters/01_foundations.md#eq-selectorproduct). Earlier images are already derived and their final polynomials can be multiplied by the selector. Old axioms and field equations map to bounded-degree consequences. For an original multiplication step, the transformed predecessor has degree at most $T(D-1)+(p-1)\gamma$; multiplication by an image of degree at most $T$ stays within $B$. This explicitly validates the use of polynomial, rather than scalar, substitutions.

As before, the transformed conclusion derives $\chi_\alpha(f)$, and combining the nonzero field values derives $f$ within $B$. Learn generators of the core this way.

To finish the block, use [Equation eq:coreabsorb](chapters/08_batching.md#eq-coreabsorb). The polynomial $u_{a,i}$ is now derived and has degree at most $\gamma$. For an extension axiom actually used in $\pi$, $\deg E_{a,i}\le D$, hence $\deg(g_{a,i}Z_a)\le TD$. If $Z_a=0$ the image is zero. Otherwise the ordinary polynomial ring is a domain, so $\deg Z_a\le TD$. Therefore both $u_{a,i}Z_a$ and $(g_{a,i}-u_{a,i})Z_a$ have degree at most $TD+\gamma\le B$. The former is derived by reuse, the latter by bounded-degree field reduction. This derives the specialized extension image within the same ceiling.

Continue through all cores and finally substitute all residual coefficients into the original $\pi$. Every extension image has a supplied derivation and every inference is simulated within $B$, yielding the extension-free refutation. *End of proof.*

<a id="cor-cheapantichain"></a>

### Corollary 8.5: Cheap incomparable families

For affine-linear inputs, residual rank $r_a\le\lfloor2h_a/(p-1)\rfloor$ gives $T=1$. Thus nonzero affine cores cost only $p-1$ degrees per batch. For arbitrary nonlinear residual inputs, the stronger rank condition $r_a\le\lfloor h_a/(p-1)\rfloor$ also gives $T=1$, and the cost is $(p-1)\gamma$ regardless of their degrees.

**Proof.** In the affine case $\eta_a\le1$ and the ceiling in [Theorem 8.4](chapters/08_batching.md#thm-cores) is at most two. In the nonlinear case it is at most one, so every residual substitution is scalar. Apply the theorem. *End of proof.*

An example is $V_a=U+P_a$ with the same arbitrarily large affine core $U$ and different residual subspaces of dimension at most $2h$ over $\mathbb F_2$. The full spaces can form an arbitrarily large antichain, yet the entire batch costs at most $D+1$. At $h=16,D=49$, residual rank $32$ is allowed while full-group interactions are already active.

<a id="lem-corequotient"></a>

### Lemma 8.6: Affine cores modulo base consequences

Let $H\subseteq k[y]_{\le1}$ have supplied derivations within degree $c$. Form affine input spaces modulo $H$, and suppose they have nested cores and residual representatives as above. For $D\ge2$ a sufficient budget is $$\boxed{\max\{c,TD+p-1\}.}$$

**Proof.** Lift each quotient core generator $f$ to an affine representative. In a later block write $f=\sum_i c_i g_i+u$ with $u\in H$. The weighted image of a selected companion is the sum of $\alpha^{-1}g_i(f^p-f)$ and $\alpha^{-1}\chi_\alpha(f)g_i u$. Their degrees are at most $p+1\le TD+p-1$; the second uses the supplied derivation of $u$. For residual absorption, the discrepancy between an input and its residual combination belongs to the learned core plus $H$, so it is already derivable within the stated ceiling. The rest is [Theorem 8.4](chapters/08_batching.md#thm-cores). *End of proof.*

For PHP one may take $H=\mathop{\mathrm{span}}\{\rho_i-1\}$, whose generators are degree-one axioms. Larger supplied consequence spaces are allowed only when their derivations are genuinely available within the asserted degree.

<a id="lem-maxcores"></a>

### Lemma 8.7: Maximal cores for a fixed order

For an order $a_1,\ldots,a_t$, the maximal possible nested cores are $$U_{a_i}=\bigcap_{j=i}^tV_{a_j}.$$ Every other nested core choice satisfying $U_{a_i}\subseteq V_{a_i}$ is contained in these suffix intersections.

**Proof.** If $U_{a_i}$ is nested, it lies in $U_{a_j}\subseteq V_{a_j}$ for every $j\ge i$, so it is contained in the intersection. The suffix intersections themselves form an increasing chain and lie in the corresponding spaces. *End of proof.*

<a id="scope"></a>

##### Scope

A batch transforms a degree budget as $d\mapsto T_{\mathcal B}d+(p-1)\gamma_{\mathcal B}$. For $T_{\mathcal B}=1$, charges add; otherwise they compose as affine functions and can multiply earlier budgets. A constant number of levels with polylogarithmic $T$ and core degree would be affordable. No such uniform decomposition was proved. The next chapter determines the exact optimum of this criterion for affine data and shows it can exceed the PHP budget.


---

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

**Proof.** Every nonzero affine core has generator degree one and therefore charge $p-1$. Maximal suffix cores minimize every residual for a fixed order, and [Lemma 9.1](chapters/09_decomposition.md#lem-ordering) minimizes their maximum. Shrinking some but not all cores cannot lower that charge and cannot improve the residual maximum. If all cores are zero, there is no core charge but each residual rank is the whole input rank. These give the two displayed alternatives. *End of proof.*

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

**Proof.** Let $K=\mathbb F_{p^d}$ and choose $n$ distinct scalars $\alpha\in K$. Embed the $2r$-dimensional $\mathbb F_p$-space $K^q\oplus K^q$ into $W$. Define $$V_\alpha=\{(u,\alpha u):u\in K^q\}.$$ Each has $\mathbb F_p$-dimension $r$. If $(u,\alpha u)=(v,\beta v)$ and $\alpha\ne\beta$, then $u=v$ and $(\alpha-\beta)u=0$, forcing $u=0$. [Lemma 9.4](chapters/09_decomposition.md#lem-coordinatequotient) preserves this intersection property after the row quotient.

Choose a basis of each space as its homogeneous linear input tuple and introduce a fresh accuracy-$h$ block with all its companions. This is valid ENS syntax. There are $n$ blocks, $nr=O(n^3)$ companions, and $hnr$ new variables. Each companion has original degree $2h+1$. *End of proof.*

<a id="thm-spreadcost"></a>

### Theorem 9.6: The exact best decomposition bound for the spread

For the family in [Lemma 9.5](chapters/09_decomposition.md#lem-spread), the best degree bound supplied by the current affine criterion is $$\boxed{B_{\rm criterion}^{\rm opt}
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

Using Imported Input [Imported input 10.1](chapters/10_route.md#imp-php) for the base and the residual PHP systems, for $1\le b\le\lfloor(n-2)/2\rfloor$, $$\boxed{\mathcal C_{b}(\mathcal F_n)\cap\mathbb F_p[x]_{\le1}=H_0.}$$

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


---

<!-- Generated from ../latex/10_route.tex. Do not silently edit this reading copy. -->

<a id="ch-route"></a>

# 10. The remaining route to the payoff

> The payoff is a superpolynomial size lower bound for ordinary PHP in $AC^{0}[p]$-Frege, at every fixed depth and fixed prime. The static decomposition work does not establish that theorem. This chapter isolates the published inputs, gives the conditional final implication, and ranks the remaining obligations.

## Published inputs, not new proofs

<a id="imp-php"></a>

### Imported input 10.1: The PHP algebraic degree budget

Razborov's polynomial-calculus lower bound for the algebraic pigeonhole principle is at least $n/2+1$ over every field [Razborov](../references/README.md#razborov). Krajíček records degree-$n/2$ designs for the Boolean PHP system containing both row and column exclusions [Krajicek Lemma 4.1](../references/README.md#krajicek). Deleting the extra row exclusions preserves these lower bounds and designs whenever the remaining equations coincide with [Equation eq:base](chapters/01_foundations.md#eq-base).

The exact identification of the polynomial encoding is an application obligation, not something to obtain merely by recognizing the name "PHP." The uses of this imported input in the manuscript, including the residual-system argument for affine rigidity, are explicitly subject to that match. For the sufficient contradiction calculations, write $b_n=\lfloor n/2\rfloor$.

<a id="imp-simulation"></a>

### Imported input 10.2: The Frege-to-ENS simulation

For fixed depth $\ell$ and a size-$s$ bounded-depth modular-counting Frege refutation of the appropriate Boolean polynomial axioms, the BIKPRS simulation produces a leveled ENS system with $M=s^{O(1)}$ companions, $\ell+O(1)$ levels, and an NS refutation of degree $$D\le (O(1)+\log s)(h+1)^{O(\ell)}.$$ The accuracy $h$ is a parameter. For polynomial $s$, taking $h=O(\log n)$ gives polylogarithmic $D$. This is the published simulation, cited through [Krajicek Theorem 5.2](../references/README.md#krajicek) and [BIKPRS](../references/README.md#bikprs), not a result proved here.

The earlier informal regime $d=\Theta(\log s)$ was too narrow as a substitute for the full simulation budget. The actual growing degree above, including its depth dependence, must be covered.

## The exact conditional implication

<a id="thm-conditionalpayoff"></a>

### Theorem 10.3: A sufficient payoff theorem

Fix a prime $p$. Assume the following three statements.

1.  An ordinary-PHP depth-$\ell$, size-$n^K$ refutation can be converted to a refutation of [Equation eq:base](chapters/01_foundations.md#eq-base) with polynomial size and bounded depth overhead.

2.  Imported Inputs [Imported input 10.1](chapters/10_route.md#imp-php) and [Imported input 10.2](chapters/10_route.md#imp-simulation) apply to that exact encoding.

3.  Every translated NS certificate arising from those hypothetical proofs has an elimination to a base PC refutation of degree at most $b_n$, for all sufficiently large $n$ (with the threshold permitted to depend on $p,\ell,K$).

Then ordinary PHP has superpolynomial $AC^{0}[p]$-Frege proof size at every fixed depth: $$\forall\ell,K\ \exists n_0\ \forall n\ge n_0:
 \operatorname{Size}_{\ell,p}(\mathrm{PHP}_n)>n^K.$$

**Proof.** Fix $\ell,K$ and suppose such a size bound holds for some sufficiently large $n$. The first assumption converts the proof to the exact Boolean polynomial system. The simulation gives its augmented NS certificate in the required parameter range. NS certificates are PC refutations of no larger degree by [Lemma 1.2](chapters/01_foundations.md#lem-duality). The third assumption eliminates the relevant extension data and produces a base PC refutation within $b_n$, contradicting Imported Input [Imported input 10.1](chapters/10_route.md#imp-php). Since $\ell,K$ were arbitrary, the displayed quantifiers follow. *End of proof.*

Equivalently, instead of an elimination one could construct a normalized degree-$D$ joint design for every relevant translated system. Applying it to $1=\sum_fq_ff$ gives $1=0$. Preserving a prescribed old functional, finding a universal specialization, or handling all degree-$D$ PC proofs are stronger requirements than this final implication needs.

## Remaining obligations, riskiest first

<a id="refutation-sensitive-elimination-beyond-static-input-spaces"></a>

### 1. Refutation-sensitive elimination beyond static input spaces

**Highest risk.** Prove that each relevant translated NS certificate can be converted to a base PC refutation at degree at most $b_n$, or construct a suitable joint design directly. Existing sufficient costs include $$D+(p-1)\sum_a\delta_a,\qquad
 D+(p-1)\sum_C\delta_C,$$ and compositions of $d\mapsto T_{\mathcal B}d+(p-1)\gamma_{\mathcal B}$. None is uniformly affordable on all admissible data. [Theorem 9.6](chapters/09_decomposition.md#thm-spreadcost) proves that optimizing the current static affine criterion cannot by itself repair this.

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

Results restricted to $p>n$ cannot establish the fixed-$p$ asymptotic goal. A result for one selected polynomial proof bound is not yet superpolynomial. Once all hypotheses of [Theorem 10.3](chapters/10_route.md#thm-conditionalpayoff) are supplied, the last contradiction is straightforward.

## What no longer needs to be the main target

The exact erosion formula, a stronger generic survival threshold, and survival-until-complete-dimension-exhaustion are not necessary separate objectives for the current PC-elimination route. Generic linear survival has a proved range in the non-Boolean branch, but the route may bypass it entirely. Likewise, one-block feasibility is not the decisive remaining issue: there are multiple exact constructions and a compatible additive elimination. The central unknown is the *total affordable cost for the complete relevant certificate*.

<a id="status"></a>

##### Status

**Current research endpoint.** The decomposition has been solved within the stated affine criterion and can be too expensive even at its optimum. The next substantive advance must exploit the refutation or richer PHP algebra, rather than search for a better ordering of those same affine spaces. This is the remaining route, not an announcement that the payoff theorem has been proved.


---

<!-- Generated from ../latex/11_appendices.tex. Do not silently edit this reading copy. -->

<a id="app-ledger"></a>

# A. Corrections, superseded claims, and scope

This ledger preserves the changes of position made in the conversation. It is not a list of additional theorems asserted without proof.

  Earlier formulation                                                     Retained conclusion
  ----------------------------------------------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Koszul vanishing for every $j<n$.                                       False. [Lemma 2.1](chapters/02_graded.md#lem-koszul-counter) gives a field-independent counterexample at $n=4,j=3$. The proved replacement is $2j-1\le n$ in [Corollary 2.3](chapters/02_graded.md#cor-koszul).
  The initial Hilbert formula holds for every $d<n$.                      Only the corrected low-degree range is proved here. An earlier reported computation at $n=5,d=4$ over $\mathbb F_{1009}$ gave $3150$ rather than $3125$; it is retained as a historical observation, not a reverified theorem or a step in a proof.
  A sharp generic exhaustion threshold was settled.                       The proposed survival-until-exhaustion law and $\Theta(n^2/d)$ threshold were not proved. The proved generic range is $t\le n-2d+1$.
  Positive dimension should establish affine feasibility.                 False for a distinguished vector. [Lemma 2.5](chapters/02_graded.md#lem-weakcount) leaves positive dimension under many arbitrary restrictions, while [Lemma 2.10](chapters/02_graded.md#lem-linearobstructions) kills $z$ or $z^2$ with one or two.
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

The generic rank calculation has a Hilbert-series byproduct. At the column-sum point of [Lemma 2.7](chapters/02_graded.md#lem-special-columns), the $n+t$ linear forms have vanishing positive Koszul homology through degree $d$. Their quotient therefore has degree-$d$ dimension $$[u^d](1+nu)^n(1-u)^t.$$ The maximal-rank argument in [Theorem 2.8](chapters/02_graded.md#thm-generic) shows that this is also the generic degree-$d$ dimension. Thus the relation matrix rank in that proof is $$\dim_k S_d-[u^d](1+nu)^n(1-u)^t.$$ This is a truncated low-degree statement in the non-Boolean ring under $t+2d-1\le n$, not the original all-range erosion claim.

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
  Reweight a level                           $D+\sum_ac_a(D)$, with $c_a$ from [Equation eq:repaircost](chapters/03_reweighting.md#eq-repaircost).
  Packed substitutions                       $TD$, with $T$ from [Lemma 4.2](chapters/04_packing.md#lem-packedlift).
  Shared features across levels              $D+(p-1)\sum_\nu\deg f_\nu$.
  Shared columns across levels               $D+q$ for $q$ determining columns.
  Packing plus shared conditioning           $TD+\kappa$.
  Affine-inverse row/column tuples           $D$, under the exact matrix hypotheses.
  Degree-window joint moments, $p=2$         $D$ if all active $e_i>D-h$.
  Supported one-block moments, $p=2$         $\max\{D,2D-h(\delta+2)\}$.
  Supported one-block moments, general $p$   $\Phi_{p,\delta}(D)$ in [Lemma 6.8](chapters/06_moments.md#lem-supported-p).
  PC-based one-block functional              $\Psi_{p,\delta}(D)$ in [Lemma 7.5](chapters/07_elimination.md#lem-pcbased); stronger input invariant, ordinary output.
  Additive PC elimination                    $D+(p-1)\sum_a\delta_a$.
  One nested-span chain                      $D+(p-1)\delta$.
  Nested cores plus residual directions      $TD+(p-1)\gamma$.
  Exact affine batch criterion               $C_S(d)$ of [Lemma 9.2](chapters/09_decomposition.md#lem-batchcost), composed by [Lemma 9.3](chapters/09_decomposition.md#lem-subsetdp).
  Spread-family optimum in that criterion    $\min\{D+(p-1)n,T(r)D\}$, eventually $D+(p-1)n$.

These bounds have different hypotheses. Retain the original axiom degrees and the specified input/output invariants; a bound for a subclass is not a uniform theorem for every simulation output.
