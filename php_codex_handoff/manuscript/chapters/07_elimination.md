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

For the pebbling encoding above, NS degree equals reversible pebbling space, over every field [Pebbling Theorem 3.1](../../references/README.md#pebbling). The Carlson--Savage constructions provide bounded-indegree single-sink families with polynomially growing pebbling price; the conversation used a family with $N=\Theta(r^3)$ and price $\Omega(r)$. These are published combinatorial inputs, not results proved in this document.

<a id="cor-genericbatchfalse"></a>

### Corollary 7.3: Plain high-degree designs do not justify universal batching

There is no theorem valid for every Boolean base system asserting that a base design through $(D+h+\log M)^C$, for a fixed constant $C$, always yields an augmented degree-$D$ design for one-level ENS systems with $M$ companions.

**Proof.** Use a family from Imported Input [Imported input 7.2](07_elimination.md#imp-pebbling). Its base has ordinary designs through polynomially growing degree below its NS threshold. The prefix construction has $M=N(N+1)/2$ companions and degree-$D$ refutations for $D=4h+2$. Take $h=\Theta(\log N)$, so the putative sufficient starting degree is only polylogarithmic and is eventually below the base NS threshold. The asserted augmented design would contradict [Lemma 7.1](07_elimination.md#lem-prefixcertificate). Each certificate summand still uses at most two adjacent blocks, so sparse local interaction alone does not rescue that theorem. *End of proof.*

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

**Proof.** Repeat the supported construction of [Lemma 6.8](06_moments.md#lem-supported-p), but require components on degree $N_j=D-h+(p-1)\delta_j$ to annihilate $\mathcal C_{N_j}(\mathcal F)$ instead of $\mathcal I_{N_j}$. In the dual kernel condition, every $Gg_j$ is already derivable through $N_j$. Write $a=h(\delta+1)$ and $G=\sum_iq_ig_i$ with $\deg G\le D-a$. By [Lemma 1.3](01_foundations.md#lem-reuse), $$G^p=\sum_iq_iG^{p-2}(Gg_i)$$ can be derived through $\max\{\max_iN_i,p(D-a)\}$: multiply the derived polynomials, not their flattened certificates. Field reduction derives $G^p-G$ within $p(D-a)$. Thus the input functional annihilates every dual kernel element, giving component consistency. The full cofactor verification is unchanged from [Lemma 6.8](06_moments.md#lem-supported-p), and yields an ordinary design. Nothing in that verification establishes closure under reuse of augmented derived polynomials, so the stronger output property is not inferred. *End of proof.*

For $p=2$, this gives $\Psi_\delta(D)=\max\{D,D-h+\delta,2D-2h(\delta+1)\}$. It is degree-preserving when $\delta\le h$ and $D\le2h(\delta+1)$. This intermediate lemma exposed the useful closure distinction; the following proof transformation handles composition directly.

## Eliminate one arbitrary block

<a id="thm-one-elimination"></a>

### Theorem 7.6: One-block additive elimination

Let $\mathcal G\subseteq\mathbb F_p[y]$ contain Boolean or field equations for every old variable. Suppose an accuracy-$h$ block has fresh variables absent from $\mathcal G$, and maximum input degree $\delta$. A degree-$d$ PC refutation of $\mathcal G\cup\mathcal E\cup\mathcal R$ yields a PC refutation of $\mathcal G$ of degree at most $$\boxed{d+(p-1)\delta.}$$ There is no fan-in factor.

**Proof.** Keep the original refutation $\pi$. Fix an input $g_j$ and $\alpha\ne0$. Set $r_{1,j}=\alpha^{-1}$ and every other new variable zero. Multiply each specialized proof line by $\chi_\alpha(g_j)$. An extension axiom maps to $$\chi_\alpha(g_j)g_i(1-\alpha^{-1}g_j)
 =\alpha^{-1}g_i(g_j^p-g_j),$$ a field-ideal polynomial. Its actual degree is bounded by the degree of the transformed original axiom line, hence by $d+(p-1)\delta$. [Lemma 1.5](01_foundations.md#lem-fieldreduction) supplies a derivation in that budget. Old axioms become old-axiom multiples, and new field equations vanish.

By [Lemma 1.4](01_foundations.md#lem-substitution), all weighted specialized inference lines can be derived within the same degree. Since the last line is one, this gives a derivation of $\chi_\alpha(g_j)$ from $\mathcal G$. Repeat over $\alpha\ne0$ and use [Equation eq:selectorlinear](01_foundations.md#eq-selectorlinear) to derive $g_j$. Do this for every input. Multiple derivations increase length, not the maximum degree.

Now specialize the original $\pi$ with all new variables zero. Every extension axiom becomes $g_i$, already derived. Reuse these final polynomials as the required starting lines. The specialized inference sequence has degree at most $d$, and the inserted input derivations have degree at most $d+(p-1)\delta$. This refutes $\mathcal G$ within the claimed budget. *End of proof.*

<a id="thm-additive"></a>

### Theorem 7.7: Additive elimination through all levels

For a leveled system with block input degrees $\delta_1,\ldots,\delta_s$, $$\boxed{\deg_{\mathrm{PC}}(\mathcal F\cup\mathcal E\cup\mathcal R)
 \ge\deg_{\mathrm{PC}}(\mathcal F)-(p-1)\sum_{a=1}^s\delta_a.}$$ Equivalently, a degree-$D$ augmented PC refutation yields a base refutation of degree at most $D+(p-1)\sum_a\delta_a$.

**Proof.** Eliminate blocks in reverse level order. Later blocks have already disappeared, so the fresh variables of the block being removed occur only in that block and its own field equations. Take all remaining axioms as the old system and apply [Theorem 7.6](07_elimination.md#thm-one-elimination). Its output is an actual PC refutation, exactly the object required for the next step. Add the degree increments. *End of proof.*

<a id="cor-pcdesign"></a>

### Corollary 7.8: Existence of a PC-annihilating joint functional

If the base has no PC refutation through degree $D+(p-1)\sum_a\delta_a$, then a normalized functional on joint polynomials of degree at most $D$ annihilates $\mathcal C_{D}(\mathcal F\cup\mathcal E\cup\mathcal R)$. In particular it is an ordinary augmented design.

**Proof.** Otherwise [Theorem 7.7](07_elimination.md#thm-additive) would yield a forbidden base refutation. Apply [Lemma 1.2](01_foundations.md#lem-duality) to the augmented PC consequence space. This is existence of a suitable functional, not extension of every preassigned base functional. *End of proof.*

<a id="lem-equalspan"></a>

### Lemma 7.9: Equal-span batches

Suppose several same-level blocks have identical polynomial input span $V$, with a basis of degree at most $\delta_V$. They can be eliminated simultaneously at degree cost $(p-1)\delta_V$. If $1\in V$, scalar specialization eliminates the whole batch at zero degree cost.

**Proof.** For each basis polynomial $f\in V$ and each block, express $f$ as a constant linear combination of that block's inputs. For a fixed $\alpha\ne0$, put the scaled coefficients into the first extension factor of every block, making the selected factor $1-\alpha^{-1}f$ everywhere. Weight the specialized original proof by $\chi_\alpha(f)$. All selected extension axioms become field consequences simultaneously. Derive the basis inputs as in [Theorem 7.6](07_elimination.md#thm-one-elimination), then derive every block input by constant linear combination. Zero-specialize the original proof and reuse them. If $1\in V$, choose coefficients making the first factor identically zero in every block, with no weight. *End of proof.*

<a id="scope"></a>

##### Scope

For $p=2$, linear inputs, $h=16$, $D=49$, ten unrelated blocks cost at most $59$ by additive elimination; ten blocks of a common span cost $50$. The earlier moment-preserving recurrence gave $48+2^{10}=1072$ for ten sequential blocks at this boundary. These are different sufficient bounds, not statements that the higher cost is necessary.
