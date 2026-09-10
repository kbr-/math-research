# Mathematical handoff: PHP designs and extension elimination

**Snapshot:** 10 September 2026.  
**Goal:** superpolynomial lower bounds for **ordinary** pigeonhole principle in fixed-depth $AC^0[p]$-Frege, for each fixed prime $p$.  
**Current endpoint:** exact static affine decomposition is optimized and can exceed the available degree budget. The next missing theorem is **affordable, refutation-sensitive extension elimination for PHP**, or an equivalent joint-design construction. **The payoff is not proved.**

This is the entry point for continuing a long mathematical research conversation in a new local session. It does not assume access to the original chat. The complete proofs, definitions, limitations, source citations, and historical computational artifacts are in this directory.

## 0. Instructions for the first local session

When the user says **“read HANDOFF.md and import all references”**, do the following.

1. Read this file, `AGENTS.md`, and `notes/STATUS_AND_AUDIT.md`. Do not start another historical test suite just to import context.
2. Read the complete local mathematical record: `manuscript/00_reading_guide.md` followed by `manuscript/chapters/01_foundations.md` through `11_appendices.md`. Read it in bounded chunks, record coverage in `notes/IMPORT_LOG.md`, and do not claim a full read when only excerpts were processed. `manuscript/FULL_RESEARCH.md` is the same material in one file, not an extra body of research.
3. Use `manuscript/CLAIM_INDEX.md` and `manuscript/claims.json` to locate statements and proof dependencies. Stable source labels such as `thm:additive` are more durable than page numbers. All original `.tex` files are in `manuscript/latex/`.
4. Read `references/README.md`, then run `python tools/import_references.py --fetch --extract`. This requests the **four direct mathematical references in the compendium**, not an uncontrolled recursive crawl of every paper's bibliography. It uses public source locations, caches bytes, records hashes and elapsed times, and reports download/extraction failures. It does not bypass access controls. The papers themselves were **not downloaded successfully in the export environment**; absence is recorded, not concealed. Use the manifest's alternate/publication records to resolve failed imports with available browsing tools. Obtain legitimate copies and log the actual source/version. Never mark a failed retrieval as imported.
5. Inspect the imported sources at the precise locations listed in `references/README.md`. In particular, match the PHP equations and the BIKPRS simulation parameters. Downloading a paper, extracting its text, and verifying its theorem are three distinct operations; record each separately.
6. Read the scopes of the relevant computational supplements in `checks/README.md`. For the present endpoint, prioritize A09--A11. The historical outputs are archived reports, not new results obtained by the current session.
7. Write a short import report and a one-page mathematical checkpoint. Preserve unresolved encoding/audit obligations. Then pursue the next research task in Section 8 below, rather than rediscovering a one-block lifting or searching for a better static affine ordering.

Useful initial commands (from this directory):

```bash
python tools/verify_bundle.py
python tools/import_references.py --list
python tools/import_references.py --fetch --extract
python tools/run_check.py --list
```

No mathematics requires PDF extraction for this import: the full raw-LaTeX Markdown and original TeX are local. The PDF is an optional visual reading copy. Run the reference importer only when network access is available/approved.

## 1. Source hierarchy and epistemic status

The source of this handoff is the consolidated research manuscript and the preserved computational exports. The original pre-investigation report is retained only in `archive/initial_research_report.pdf`; the independent investigation superseded important parts of it. It is **not** an additional set of established theorems to silently merge into the current record.

- **Working proof:** the compendium states a claim and provides an argument developed in the conversation. This is not a claim of independent refereeing, novelty, or general machine verification.
- **Imported input:** an external theorem cited by the manuscript. Check its exact hypotheses, encoding, and version in the source.
- **Conditional working proof:** an argument depending on an explicit unverified match or further hypothesis, notably affine-consequence rigidity and the final payoff implication.
- **Finite check:** an actual archived finite computation with a restricted scope. Its passing does not prove the general theorem.
- **Open obligation:** not established. Do not convert it into a theorem by dropping a quantifier, replacing an encoding, or hiding degree growth.

The manuscript contains **68 working lemmas/theorems/corollaries with proof blocks**, three explicitly imported inputs, and three examples. Some results are superseded in strength, but remain useful for explaining failed methods. They are not all independent advances toward the goal.

`manuscript/latex/` is the exact preserved mathematical source; the Markdown is a generated reading copy with macros expanded and cross-references resolved. If any conversion or source conflict appears, expose it and record a correction instead of silently choosing a favorable interpretation. Neither representation is infallible mathematics.

## 2. The exact mathematical objects

### 2.1 Non-Boolean graded branch

For $m$ rows and $n$ columns,

$$
S_{m,n}=k[x_{ij}:i\in[m],j\in[n]]/(x_{ij}x_{i'j}:i\ne i').
$$

Only different rows in the same column are excluded. Repeated rows and variable powers are allowed. Put

$$
\rho_i=\sum_{j=1}^n x_{ij},\qquad
S=S_{n+1,n},\qquad
\overline B=S/(\rho_i-\rho_1:2\le i\le n+1),\qquad z=\rho_1.
$$

This is **not** the partial-matching/chessboard ring, and it is **not** the Boolean PHP quotient.

### 2.2 Boolean linear-row base system for the current route

Fix $k=\mathbb F_p$, with $p$ a fixed prime and $m=n+1$. The working base axioms are

$$
\mathcal F_n=
\{\rho_i-1:i\in[n+1]\}
\cup\{x_{ij}x_{i'j}:i\ne i'\}
\cup\{x_{ij}^2-x_{ij}\}.
$$

There are **no same-row exclusion equations**. A Boolean row satisfying $\rho_i=1\pmod p$ can have $p+1$ occupied cells. Do not reinterpret the equation as “exactly one.” Its implication to the ordinary nonempty-row clause is in the direction needed for a possible proof transfer, but the bounded-depth proof-level transfer remains an obligation.

The homogeneous Boolean ring is

$$
A_n=k[x,z]/(\rho_i-z,\ x_{ij}x_{i'j},\ x_{ij}^2-zx_{ij})
\cong\overline B/(x_{ij}^2-zx_{ij}).
$$

The generic results in $\overline B$ do not automatically pass to $A_n$.

### 2.3 Truncated consequences: do not confuse these spaces

For a finite polynomial axiom set $\mathcal F\subseteq k[y]$,

$$
\mathcal I_D(\mathcal F)
=\operatorname{span}_k\{qf:f\in\mathcal F,\ \deg(qf)\le D\}.
$$

A degree-$D$ design is a linear map $\lambda:k[y]_{\le D}\to k$ satisfying

$$
\lambda(1)=1,\qquad \lambda(\mathcal I_D(\mathcal F))=0.
$$

A degree-$D$ Nullstellensatz (NS) refutation is an identity

$$1=\sum_{f\in\mathcal F}q_f f,\qquad \deg(q_f f)\le D.$$

Polynomial calculus (PC) allows axiom introduction, field-linear combinations, and multiplication of a previously derived polynomial by one variable. Let $\mathcal C_D(\mathcal F)$ be the vector space of polynomials with PC derivations of maximum line degree at most $D$, after collecting like terms in the ordinary polynomial ring. Then

$$\mathcal I_D(\mathcal F)\subseteq\mathcal C_D(\mathcal F),$$

but equality is not assumed. A normalized functional annihilating $\mathcal C_D$ is a stronger object than an ordinary design. Neither truncated space is the unrestricted ideal.

The key reuse rule is

$$
f\in\mathcal C_c(\mathcal F)
\Longrightarrow
qf\in\mathcal C_{\max\{c,\deg q+\deg f\}}(\mathcal F).
$$

One reuses the final derived polynomial, rather than multiplying its whole proof by $q$. By contrast, flattening an axiom-multiple certificate generally gives only the additive ceiling $c+\deg q$.

### 2.4 Actual ENS data

Block $a$ has old-variable inputs $g_{a,1},\ldots,g_{a,k_a}$, accuracy $h_a\ge1$, fresh variables $r_{a,u,j}$, and **all** companions

$$
E_{a,i}=g_{a,i}\prod_{u=1}^{h_a}
\left(1-\sum_jr_{a,u,j}g_{a,j}\right).
$$

Fresh variables are shared among companions of one block and disjoint across blocks at one level. Inputs can be nonlinear and use earlier-level extension variables. Include the new field equations

$$\mathcal R=\{r^p-r\}.$$

After omitting zero inputs, define

$$
\delta_{a,i}=\deg g_{a,i},\qquad
\delta_a=\max_i\delta_{a,i},\qquad
 e_{a,i}=\delta_{a,i}+h_a(\delta_a+1).
$$

A companion is active at target degree $D$ if $e_{a,i}\le D$.

**Keep its original joint-variable degree.** Specializing extension variables or Boolean-reducing a polynomial does not retroactively enlarge the original degree-$D$ cofactor space. This convention recurs in nearly every proof and test.

## 3. Literature inputs and the payoff quantifiers

The compendium uses the following external inputs; see reference locators and the audit checklist rather than relying on their names alone.

**PHP base degree.** Razborov's published algebraic-PHP PC degree lower bound is recorded as at least $n/2+1$ over every field. Krajíček records degree-$n/2$ designs for a Boolean PHP system with row and column exclusions. Deleting extra axioms transfers a lower bound/design to a weaker system **only after the remaining equations are matched exactly**. The manuscript keeps this match as an explicit obligation, including for residual boards.

Write the sufficient contradiction budget as

$$b_n=\lfloor n/2\rfloor.$$

**Frege-to-ENS simulation.** As recorded in the compendium from BIKPRS via Krajíček Theorem 5.2: a size-$s$, fixed-depth modular-counting Frege refutation gives polynomially many companions $M=s^{O(1)}$, constantly many levels, and an augmented NS refutation with

$$D\le (O(1)+\log s)(h+1)^{O(\ell)}.$$

With polynomial $s$ and logarithmic accuracy, $D$ is polylogarithmic. Do not replace the full degree bound by $\Theta(\log s)$ without checking all depth/accuracy factors.

The final goal has quantifiers

$$
\forall\ell,K\ \exists n_0\ \forall n\ge n_0:
\operatorname{Size}_{\ell,p}(\mathrm{PHP}_n)>n^K
$$

for each fixed prime $p$.

A sufficient missing theorem transforms each **relevant translated NS certificate** into a base PC refutation of degree at most $b_n$. Another sufficient route constructs a suitable normalized joint degree-$D$ design for each relevant augmented system. We do not need to preserve a preassigned base functional or handle every arbitrary PC proof if those stronger requirements obstruct progress.

## 4. What the independent investigation established as working proofs

The full proofs and hypotheses are in the linked chapters. This section is a map, not a replacement for reading them.

### 4.1 Corrected graded algebra and generic witnesses

Read [Chapter 2](manuscript/chapters/02_graded.md).

The proposed Koszul-vanishing range $j<n$ is false: the manuscript gives an explicit characteristic-free strand counterexample at $n=4,j=3$. The corrected range is

$$2d-1\le n.$$

In that range,

$$
H_i(\rho;S)_d=0\ (i\ge1),\qquad
\dim_k\overline B_d=\binom nd n^d,
$$

and multiplication by $z$ is injective through the stated degrees. For arbitrary $t<n$ linear restrictions the elementary dimension bound leaves a nonzero degree-$d$ quotient, but **that alone does not imply survival of $z^d$**.

The generic witness theorem (`thm:generic`, Theorem 2.8) constructs a determinant functional satisfying

$$\lambda(z^d)=1,\qquad \lambda(L_su)=0$$

when $t+2d-1\le n$, on a nonempty coefficient-open chart with a specified rational point. The special column-sum restrictions achieve maximal relation rank via Koszul exactness. A generic statement over a finite field is not a success-probability estimate and does not imply that every constrained coefficient family meets the chart.

This branch is now optional for the PC-elimination route.

### 4.2 Exact nonlinear liftings and method barriers

Read [Chapters 3--6](manuscript/chapters/03_reweighting.md), with full budget summary in [Appendix C](manuscript/chapters/11_appendices.md#app-map).

The record contains scalar reweighting, repair of a whole level, factor-packed polynomial substitutions, shared-feature/whole-column conditioning, base-aware certificates and affine-inverse row/column tuples, and joint-moment constructions. Each has a precise input/output invariant and degree budget; do not combine formulas without their hypotheses.

Especially useful distinctions:

- Reweighted liftings can change base moments. Selected field indicators turn products into actual field-ideal identities, rather than merely assigning value zero to a factor.
- A whole level of polynomial substitutions costs a **maximum** substitution degree, not a sum. Across levels substitutions can compose and inflate degree.
- Supported coefficient-extraction corrections solve complete one-block and two-block multiplier conditions. Their naive repeated moment-preserving composition is not affordable for arbitrarily many blocks.
- Enforcing weighted pointwise vanishing modulo only Boolean/column equations can be inherently expensive even for blocks that are free once row equations are used.

The prefix-pebbling certificate in [Chapter 7](manuscript/chapters/07_elimination.md#lem-prefixcertificate) refutes universal cheap batching based only on high ordinary NS design degree. Long cumulative propagation can use only adjacent pairs of blocks. That base has PC degree at most three; high NS degree does not imply high PC degree.

### 4.3 Additive PC elimination: the main reusable tool

Read Theorems 7.6--7.7 (`thm:one-elimination`, `thm:additive`).

One arbitrary block can be removed from a degree-$D$ PC refutation at cost $(p-1)\delta$:

$$D\longmapsto D+(p-1)\delta.$$

The proof fixes the original refutation. For each input $g_j$ and $\alpha\ne0$, set the first-factor coefficients so its common factor is $1-\alpha^{-1}g_j$, and weight all specialized proof lines by

$$\chi_\alpha(g_j)=1-(g_j-\alpha)^{p-1}.$$

The exact identities

$$
\chi_\alpha(t)(1-\alpha^{-1}t)=\alpha^{-1}(t^p-t),
\qquad t=\sum_{\alpha\ne0}\alpha\chi_\alpha(t)
$$

derive $g_j$ from the old system. Then replay the original proof with all new variables zero, reusing the derived inputs. The field-ideal reductions are degree bounded, not unrestricted ideal-membership shortcuts.

Reverse-level elimination gives

$$B\le D+(p-1)\sum_a\delta_a.$$

Its output is a genuine PC refutation at every step. Hence the composition does not assume that an ordinary lifted design retains PC closure. Proof length may grow; the current lower-bound argument controls degree.

### 4.4 Nested spans and nested cores

Read [Chapter 8](manuscript/chapters/08_batching.md).

An arbitrary number of same-level blocks whose input spaces form one chain

$$V_1\subseteq\cdots\subseteq V_s$$

costs only

$$D+(p-1)\delta.$$

The argument keeps replaying the **original** degree-$D$ proof, while reusing previously derived inputs. Nestedness permits one selector to handle all remaining blocks simultaneously. A quotient variant uses explicitly supplied bounded-degree base consequences; equality modulo the unrestricted PHP ideal is not an admissible substitute.

More generally choose nested cores $U_a\subseteq V_a$, with core-generator degree at most $\gamma$, residual rank

$$r_a=\dim(V_a/U_a),$$

and residual representatives of degree at most $\eta_a$. Set

$$
T_a=\max\left\{1,\ \eta_a\left(\left\lceil\frac{(p-1)r_a}{h_a}\right\rceil-1\right)_+\right\},
\qquad T=\max_aT_a.
$$

The core--residual theorem (`thm:cores`, Theorem 8.4) gives

$$B\le TD+(p-1)\gamma.$$

It handles some arbitrarily large antichains cheaply. For example, affine inputs over $\mathbb F_2$ with a common core and residual ranks at most $2h$ have $T=1$ and charge one degree. **Antichain size alone is therefore not an obstruction.**

### 4.5 The latest result: optimize the criterion, then exhibit its limitation

Read all of [Chapter 9](manuscript/chapters/09_decomposition.md). This is the immediate stopping point before the export.

For a fixed affine order, maximal cores are suffix intersections. Ordering by nondecreasing dimension is optimal. Equivalently,

$$
R_*(S)=\max_{\varnothing\ne A\subseteq S}
\left[\min_{a\in A}\dim V_a-\dim\left(\bigcap_{a\in A}V_a\right)\right].
$$

With common accuracy $h$, define

$$T(r)=\max\left\{1,\left\lceil\frac{(p-1)r}{h}\right\rceil-1\right\}.$$

The optimal **certified bound within our static affine rule** for one batch is

$$
C_S(d)=\min\{T(R_*(S))d+(p-1),\ T(\max_{a\in S}\dim V_a)d\}.
$$

The exact partition/order optimum is

$$B(\varnothing)=D,\qquad B(S)=\min_{\varnothing\ne A\subseteq S}C_A(B(S\setminus A)).$$

This is generally exponential as an algorithm, but the obstruction below is algebraic and does not depend on an inability to search.

Let

$$H_0=\operatorname{span}_{\mathbb F_p}\{\rho_i-1\},\qquad
W=\operatorname{span}_{\mathbb F_p}\{x_{ij}:j<n\}.$$

The $n^2-1$ coordinates of $W$, together with $1$, are independent modulo $H_0$. Set

$$
d_0=\lceil\log_p n\rceil,\quad q=\left\lfloor\frac{n^2-1}{2d_0}\right\rfloor,\quad r=qd_0,\quad K=\mathbb F_{p^{d_0}}.
$$

Embed $K^q\oplus K^q$ into $W$ and choose $n$ distinct $\alpha\in K$. The graph spaces

$$V_\alpha=\{(u,\alpha u):u\in K^q\}$$

have dimension $r$ and pairwise zero intersection, including after the row quotient. Bases of these spaces are admissible one-level linear ENS input tuples.

Their exact optimal cost **in this criterion** is

$$
\boxed{B_{\mathrm{criterion}}^{\mathrm{opt}}
=\min\{D+(p-1)n,\ T(r)D\}.}
$$

For fixed $p$, $h=\Theta(\log n)$ and active polylogarithmic $D$, it is eventually $D+(p-1)n>n/2$.

The conditional affine-rigidity theorem (`thm:rigidity`, Theorem 9.8) further states

$$
\mathcal C_b(\mathcal F_n)\cap\mathbb F_p[x]_{\le1}=H_0,
\qquad 1\le b\le\left\lfloor\frac{n-2}{2}\right\rfloor,
$$

subject to matching the imported PC lower bound for the base and residual encodings. Thus low-degree **base affine** consequences do not repair this static quotient.

Crucial scope: the graph-space family is **admissible extension data, not an augmented PHP refutation**. It does not show those blocks occur essentially in any short translated proof. Its optimum is not a lower bound on every possible elimination method. Nonlinear consequences, relations involving surviving extensions, direct joint designs, and refutation-sensitive rewriting remain unexcluded.

## 5. Results that must not be accidentally resurrected

Read the full [corrections ledger](manuscript/chapters/11_appendices.md#app-ledger).

- Do not claim Koszul vanishing for all $d<n$; use $2d-1\le n$.
- Positive quotient dimension does not imply the target $z^d$ survives.
- Generic linear survival in $\overline B$ is not a Boolean ENS lower bound.
- A linear functional is not multiplicative: $\lambda(f)=0$ does not give $\lambda(qf)=0$.
- Field-ideal identities and finite evaluations are not automatically low-degree certificates in the full base ideal.
- One pointwise scalar choice need not work universally; existential choices or joint functionals suffice.
- Every old/new variable must have the stated domain equations. At odd primes, extension variables are generally field-valued, not Boolean.
- Reuse of derived PC polynomials is different from multiplying flattened NS certificates.
- One-block feasibility and separate block solutions do not imply cheap global compatibility.
- Sparse pairwise block interactions can propagate through a long chain.
- Neither large antichains nor the static spread counterexample lower-bound all elimination methods.
- No result restricted to $p>n$ supplies the desired fixed-$p$ asymptotics.
- No theorem about a stronger functional/chessboard encoding may be silently relabeled as a theorem about our weaker base.

## 6. The remaining route, by risk

**1. Highest: affordable refutation-sensitive elimination.** Prove, for every relevant translated certificate,

$$
\pi:\mathcal F_n\cup\mathcal E\cup\mathcal R\vdash_D^{\mathrm{NS}}1
\Longrightarrow
\mathcal F_n\vdash_{B(\pi)}^{\mathrm{PC}}1,
\qquad B(\pi)\le b_n.
$$

Alternatively construct the joint design directly. A bound polynomial in $D,h,\log M$ with exponents depending on fixed depth and $p$ would suffice, but is **unproved** and is stronger than necessary. Any bound below the linear base threshold is enough. The static criterion cannot provide it uniformly.

**2. High: coverage of real simulation outputs.** Prove that the mechanism in item 1 covers nonlinear inputs, all companions, earlier levels, and field axioms with the actual BIKPRS parameters. Syntax alone supplies no inexpensive decomposition. It may be advantageous to exploit the translated NS certificates rather than handle arbitrary PC proofs.

**3. Medium technical: audit the working transformations.** Independently check active-axiom bookkeeping, freshness, weighted substitutions, polynomial multiplication as primitive PC, reuse rather than flattening, and degree-nonincreasing reductions. Verify every consequence used in quotient batching has its own permitted derivation. Computational examples do not settle these universal points.

**4. Necessary encoding transfer.** Formalize a bounded-depth polynomial-overhead transformation from a hypothetical ordinary-PHP refutation to a refutation of our exact Boolean linear-row system. Only this direction is needed. Confirm the literature base lower bound applies after the legitimate axiom deletions, including residual systems used by rigidity arguments.

**5. Final parameter closure.** For every fixed $p,\ell,K$, match the simulation degree and all overheads and derive a contradiction below $b_n$ for all sufficiently large $n$. See Theorem 10.3 (`thm:conditionalpayoff`).

## 7. Computations and reproducibility

`checks/original_archives/` holds all **eleven byte-preserved historical ZIPs**. `checks/suites/` holds their unpacked contents. The scripts are not a single unified solver. Their archived results have different scopes, and some test only satisfiable finite domains. The source and output proof verifiers in A09/A10 and the finite-field optimization code in A11 are especially relevant now.

Use `python tools/run_check.py --list` for known entry points. The runner executes a selected suite in a **new disposable working copy**, preserves the archived reports, caps requested worker pools, adapts the three known obsolete absolute paths, and records every source adaptation and command result. This is not a mathematical change to the research source. Inspect `checks/README.md` before running a suite.

Dependencies for checks: Python 3.10+ and NumPy; A01 additionally uses Numba. The handoff, manifest verification, and timing tools use the standard library. Markdown regeneration uses Pandoc; PDF rebuilding is optional and requires the TeX packages listed in the source README.

Do not rerun all suites merely to create an impression of verification. Select checks capable of falsifying the proposed claim, include nonvacuous active axioms and negative controls, and report whether an instance is a full PHP system, a different unsatisfiable system, or a satisfiable test domain.

## 8. A concrete first research task after import

This is a **proposed next task**, not an established lemma.

1. Audit the one-block/additive/nested/core--residual elimination statements against their actual proofs, prioritizing the common reuse and substitution lemmas. Make a list of genuine gaps, not stylistic concerns.
2. Extract the exact form of the BIKPRS-translated NS certificate from the primary references: what data determine its blocks, levels, degrees, and cofactors? Record what is truly guaranteed and what is not.
3. Formulate a refutation-sensitive quantity that depends on the nonzero cofactors or actual proof organization, rather than solely the family of input spans. The candidate must explain why a family of irrelevant spread blocks need not be charged and must not falsely exclude the known prefix-pebbling certificate.
4. Attempt an elimination or pruning lemma for that quantity. State all parameters first. Test it on the prefix-pebbling chain and the static spread family as method controls, carefully noting that the spread data do not supply a refutation.
5. Record the outcome in a new `notes/RESEARCH_LOG.md` entry with the exact statement, proof attempt, actual obstruction or proof, dependencies, degree accounting, and measured tool/computation times. Amend the claim ledger only after identifying which prior claim is changed.

Do not assume “refutation-sensitive” automatically makes a charge small. That smallness is precisely the missing theorem. Conversely, failure of the current representation does not settle the desired lower bound negatively.

## 9. Workflow inherited from the user

The user prefers sustained mathematical work, self-contained statements, proofs, explicit counterexamples, and a short account of what changed toward the payoff. Do not replace an attempted argument by saying the problem is longstanding. Express uncertainty precisely when a proof is not checked.

For numerical work, use exact modular arithmetic and optimized/vectorized or compiled kernels; parallelize independent cases with a laptop-appropriate worker cap. Do not substitute floating-point rank for finite-field rank, and guard integer overflow. Prevent BLAS oversubscription when processes are parallel.

The user requests timing on **every research turn**, including failed attempts, reruns, tools, reading, and available latency. Use `tools/timing.py` as described in `notes/TIMING.md`. Mark reading/review windows separately. Those windows include interpretation; pure internal reasoning and pure network latency are not directly measurable. Report unseparated residual time honestly. Parallel elapsed time is the wall-clock union, not the sum of overlapping worker durations.

Keep originals immutable. Add corrected proofs, provenance, and status changes; do not rewrite historical reports to agree with a new claim. Maintain `notes/IMPORT_LOG.md`, `notes/RESEARCH_LOG.md`, and `notes/STATUS_AND_AUDIT.md` so later context resets can resume without re-reading the entire chat.

## 10. Directory map

```text
HANDOFF.md                         This entry point and current mathematical checkpoint
AGENTS.md                          Concise local-agent working instructions
README.md                          Human quick start
manuscript/FULL_RESEARCH.md         Full raw-LaTeX Markdown proof record
manuscript/chapters/                Same record split for bounded-context reading
manuscript/CLAIM_INDEX.md           Numbered statements linked to exact source labels
manuscript/claims.json              Statements, proofs, statuses, source ranges, dependencies
manuscript/labels.json              All source labels and cross-reference targets
manuscript/latex/                   Unchanged original TeX source
manuscript/*.pdf                    Final visual reference copy
checks/original_archives/           Eleven unchanged historical computation packages
checks/suites/                     Unpacked scripts, original reports, and scope notes
references/README.md                Four direct mathematical references and exact import targets
references/manifest.json            Canonical records, download candidates, version/status fields
references/references.bib           Portable BibTeX bibliography
tools/                             Import, timing, selected-check, conversion, integrity utilities
notes/                             Audit checklist, import log, research log, timing guidance
archive/                           Initial report and alternate/source exports, archival only
provenance/                        Original manifests plus export/conversion/integrity reports
logs/                              New measurements and command logs
```

**Resume here:** the static affine decomposition has been solved within its model and can be unaffordable. The next theorem must use the relevant refutation or richer PHP algebra. No general affordable elimination or superpolynomial Frege lower bound has been established.
