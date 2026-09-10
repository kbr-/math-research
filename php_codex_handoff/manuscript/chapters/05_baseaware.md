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

Fix $2q\le n$ and one block with inputs $g_a=x_{a,2a-1}$, $a\le q$. Suppose substitutions of maximum degree $T$ make every companion a consequence of $\mathcal F_n$ with an original-axiom certificate of degree at most $C$. Assuming the degree-$C$ residual PHP designs supplied by Imported Input [Imported input 10.1](10_route.md#imp-php), if $$C\le\left\lfloor\frac{n-q}{2}\right\rfloor,$$ then $q\le h(T+1)$.

**Proof.** Expose independent Boolean choices $t_a$: assign pigeon $a$ to hole $2a-1$ when $t_a=1$, and to hole $2a$ when $t_a=0$. For each remaining pigeon $i>q$ use common residual variables $z_{i,a}$ and set $$x_{a,2a-1}=t_a,\quad x_{a,2a}=1-t_a,\qquad
 x_{i,2a-1}=(1-t_a)z_{i,a},\quad x_{i,2a}=t_a z_{i,a}.$$ All other variables are set or relabeled in the usual partial-matching restriction. For each fixed Boolean $t$, the base system becomes the same labeled PHP with $n-q$ holes. Choose one degree-$C$ design $\mu$ for that residual system.

Let $P(x)=\prod_u(1-\sum_a\beta_{u,a}(x)x_{a,2a-1})$. Since each nonzero $x_{a,2a-1}P$ has a degree-$C$ certificate, $\deg P\le C-1$. The parameterized substitution does not increase degree in the residual variables, so $$R(t)=\mu(P(x(t,z)))$$ is defined. Each original variable has $t$-degree at most one, hence $\deg R\le h(T+1)$.

Apply $\mu$ to the restricted certificates. For every Boolean $t$, they imply $t_aR(t)=0$ for all $a$. At $t=0$, all inputs are zero, so $P=1$ and $R(0)=1$. The unique multilinear representative of this Boolean function is $\prod_a(1-t_a)$, of degree $q$. Multilinear reduction cannot increase degree, proving the inequality. *End of proof.*

<a id="scope"></a>

##### Scope

Taking $q$ proportional to $n$ and $h=O(\log n)$ forces $T=\Omega(n/\log n)$ in this unconditioned substitution-and-certificate model. A single selected cell can nevertheless be fixed to one to kill this block after changing the base moments. Thus the obstruction is not to every conditional or joint-functional construction.
