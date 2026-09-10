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

For an allowed cofactor $H$ of $E_{a,i}$, $\deg H<h$. It cannot supply all $h$ groups of a different block, so all cross-block corrections vanish. In its own block, a nonempty auxiliary support has $0<|S|<h$, and [Lemma 6.1](06_moments.md#lem-coefficient) contains both $g_{a,j}$ and $1-g_{a,j}$. Boolean reduction makes it zero. Empty support reduces to $qg_{a,i}g_{a,j}$, whose components cancel $\lambda(qg_{a,i})$ by [Equation eq:window-components](06_moments.md#eq-window-components). All reductions remain within $M$. Monomial cofactors span all allowed cofactors. *End of proof.*

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

**Proof.** Use components annihilating $\mathcal I_{M_a}$ with coupling equation $\sum_{j,\alpha\ne0}\mu_{a,j,\alpha}(G\chi_\alpha(g_{a,j}))=\lambda(G)$. A dual kernel condition and [Equation eq:selectorlinear](01_foundations.md#eq-selectorlinear) give $Gg_{a,j}\in\mathcal I_{M_a}$ for every $j$. Then $$G^p=\sum_iq_iG^{p-2}(Gg_{a,i})\in\mathcal I_{B_a}.$$ Since $B_a-ps_a=(h+p-1)\delta_a-\delta_{\min}\ge0$, $G^p-G$ also has a field-axiom certificate within $B_a$. The kernel condition is therefore annihilated by the input design, proving consistency.

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

**Proof.** Check a monomial cofactor. If it uses incompatible input indices within one selected block, every diagonal extraction kills it. A partial support in a block other than the axiom's block supplies too few auxiliary variables. A partial nonempty support in the axiom's own block produces both $g$ and $1-g$, hence vanishes after Boolean reduction. The remaining monomials consist of complete selected groups in a set of blocks. Their contributions are precisely [Equation eq:mixed-add](06_moments.md#eq-mixed-add) or [Equation eq:mixed-revisit](06_moments.md#eq-mixed-revisit). The degree limit accounts for the $h|S|$ new-variable factors. Old axioms and field equations are handled by the component conditions and auxiliary reductions, while normalization comes only from the root. *End of proof.*

## Supported corrections solve the full one-block problem

<a id="thm-supported"></a>

### Theorem 6.7: Moment-preserving supported lifting over $\mathbb F_2$

For one arbitrary block, put $\delta=\max_i\deg g_i$ and $$\Phi_\delta(D)=\max\{D,2D-h(\delta+2)\}.$$ Every degree-$\Phi_\delta(D)$ old design extends to a degree-$D$ design over the block, preserving all old moments. There is no restriction on cofactor support.

**Proof.** If no companion is active, zero specialization suffices. Otherwise put $a=h(\delta+1)$, $J=\{j:a+\delta_j\le D\}$, $N_j=D-h+\delta_j$, and $$V=\left\{G=\sum_{i\in J}q_ig_i:\deg q_i\le D-a-\delta_i\right\}.$$ Seek components $\nu_j$ through $N_j$ annihilating $\mathcal I_{N_j}(\mathcal F)$ with $\sum_{j\in J}\nu_j(Gg_j)=\lambda(G)$ for $G\in V$. All products fit these domains. For a dual obstruction $Gg_j\in\mathcal I_{N_j}$, write $G=\sum_iq_ig_i$. Then $$G^2=\sum_iq_i(Gg_i)\in\mathcal I_{B_0},\qquad
 B_0=N_i+(D-a-\delta_i)=2D-a-h.$$ Also $\deg(G^2-G)\le2(D-a)\le B_0$, so Boolean reduction gives $G\in\mathcal I_{B_0}$. Since the input domain covers $\max\{D,B_0\}$, the coupling equations are consistent by separation.

Define the supported correction $$\boxed{\Lambda(P)=\lambda(P(y,0))+\sum_{j\in J}\nu_j(g_jT_j(P)).}$$ It fits the domains and preserves old moments. By [Lemma 6.1](06_moments.md#lem-coefficient), a selected monomial cofactor gives $$g_jT_j(HE_i)=qg_i g_j(1-g_j)^{|S|}g_j^{h-|S|}.$$ Every nonempty $S$, including $S=[h]$, now contains the factor $g_j(1-g_j)$ and is annihilated by bounded-degree Boolean reduction. Empty support reduces to $qg_ig_j$ and cancels the base term by the coupling equation. Old-axiom multiples are old-axiom multiples in the component domains, and new Boolean equations vanish under auxiliary reduction. This covers all cofactors. *End of proof.*

<a id="lem-supported-p"></a>

### Lemma 6.8: Supported lifting over every fixed prime

With old Boolean or field equations, define $$\Phi_{p,\delta}(D)=\max\{D,
 pD-ph-((p-1)h-(p-2))\delta\}.$$ An old design through this degree gives a complete one-block degree-$D$ design preserving old moments. The bound is at most $pD$.

**Proof.** Use components indexed by active $j$ and $\alpha\ne0$, with domains $N_j=D-h+(p-1)\delta_j$, acting on $\chi_\alpha(g_j)[t_1\cdots t_h]P(r_{u,j}=t_u/\alpha)$. Give their sum sign $(-1)^{h+1}$. The coupling is $\sum_{j,\alpha}\nu_{j,\alpha}(G\chi_\alpha(g_j))=\lambda(G)$. A kernel condition yields $Gg_j\in\mathcal I_{N_j}$ by [Equation eq:selectorlinear](01_foundations.md#eq-selectorlinear). Writing $a=h(\delta+1)$ and $\deg G\le D-a$, use $$G^p=\sum_iq_iG^{p-2}(Gg_i).$$ A summand has consequence degree at most $pD-(p-1)a-h+(p-2)\delta_i$, bounded by the expression defining $\Phi_{p,\delta}$. This budget also covers $G^p-G$ and every component domain. Separation supplies the components. The support factor kills all nonempty auxiliary supports since $\chi_\alpha(g_j)(1-g_j/\alpha)\in J_{\mathrm{fld}}$. Empty support is canceled by the coupling. All old and new field equations satisfy the same reductions as before. *End of proof.*

<a id="cor-twoblocks"></a>

### Corollary 6.9: Two blocks and the first interaction boundary

Over $\mathbb F_2$, two blocks need input degree $$B=\Phi_{\delta_A}(\Phi_{\delta_B}(D))\le4D.$$ For equal input degree $\delta$ and $D=h(\delta+2)+\delta$, this is $D+3\delta$. Over $\mathbb F_p$, two blocks need at most $p^2D$. The construction permits dependencies on earlier block variables and all cross-block cofactors.

**Proof.** First lift block $A$ to the input degree needed to lift $B$. For the second application, include *all* axioms and field equations of the first block among the old system; its components may use general moments in those old variables. Thus the second old-axiom verification enforces the cross-block conditions. If $C=h(\delta+2)$ and $D=C+\delta$, two applications of $d\mapsto\max\{d,2d-C\}$ give $C+4\delta=D+3\delta$. *End of proof.*

<a id="scope"></a>

##### Scope

For $s$ equal-degree blocks and $D>C=h(\delta+2)$, this particular moment-preserving iteration costs $C+2^s(D-C)$. It solves finite-block compatibility but not affordable global lifting. It does not prove feasibility of every component system in [Lemma 6.6](06_moments.md#lem-mixedsystem); it uses a less restricted second-stage functional. The elimination method in the next chapter abandons unnecessary preservation of a prescribed base functional.
