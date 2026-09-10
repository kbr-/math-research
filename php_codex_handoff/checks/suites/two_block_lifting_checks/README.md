# Supported-coefficient lifting: exact two-block checks

## What is proved in the accompanying argument

Let F contain Boolean equations for every old variable, over F_2. For one ENS
block of accuracy h with nonzero input polynomials g_i of degrees delta_i, let
delta=max_i delta_i and retain the original joint-variable companion degrees

    e_i = delta_i + h(delta+1).

For any target D, a sufficient input-design degree is

    Phi_delta(D) = max(D, 2D-h(delta+2)).

A design of this degree lifts to a normalized degree-D design for F plus the
entire block and all its Boolean field equations. All old moments through D
are preserved. There is no restriction on which factor groups occur in the
cofactors.

For two blocks with maximum input degrees delta_A, delta_B, the sufficient
base degree for order A then B is

    Phi_delta_A(Phi_delta_B(D)).

When all inputs in both blocks have degree delta and

    D = e+h = h(delta+2)+delta,

the bound is D+3delta. Thus same-block and cross-block cofactors touching all h
factor groups are genuinely active in this test regime.

## Construction

Define T_j(P) by setting the new variables r_(u,j)=t_u for every u, every other
new variable to zero, reducing t_u^2=t_u, and taking the coefficient of the
product of all h auxiliary variables.

The output is

    Lambda(P) = lambda(P(y,0)) + sum_j nu_j(g_j T_j(P)).

Only active indices e_j<=D are needed. Put N_j=D-h+delta_j. Components nu_j
are unnormalized functionals through degree N_j annihilating all bounded-degree
old consequences there. They solve

    sum_j nu_j(G g_j) = lambda(G),

where G ranges over the span of q g_i, deg(q)<=D-e_i.

For consistency: if Gg_j is an old consequence through N_j for every active j,
then, writing G=sum_i q_i g_i,

    G^2 = sum_i q_i (Gg_i)

is an old consequence through B0=2D-h(delta+2). Boolean reduction of G^2-G
uses no greater degree. Thus lambda(G)=0, proving the finite-dimensional dual
consistency criterion.

The extra g_j multiplying T_j is essential. For a multiplier touching a
nonempty set A of the selected factor groups, its contribution has a factor

    g_j (1-g_j)^|A| g_j^(h-|A|),

which vanishes modulo the old Boolean equations even when |A|=h. Two blocks
are handled in order: the first block, including its axioms and field
equations, is part of the old system in the second consistency argument.
This is a construction of one joint functional, not a claim that arbitrary
independent local solutions can be glued.

## Scope of the computations

checks.py implements the actual component construction at both steps. It
solves the component equations, assembles the joint moment functional, and
checks ALL allowed squarefree monomial cofactors of every old and extension
axiom through the specified target degree. Squarefree cofactors suffice after
including the Boolean equations. Each axiom retains its ORIGINAL ordinary
degree, even if its Boolean normal form has lower degree.

The implementation uses NumPy-vectorized exact GF(2) elimination, with four
parallel worker processes. No floating-point rank routines are used. Free
coordinates in the component solutions are randomized.

The 23 cases include arbitrary linear and quadratic tuples, fan-ins 2 and 3,
accuracies 1 and 2, and same-block and cross-block complete-group cofactors.
Four cases have genuinely unsatisfiable four-variable Horn-chain base systems
with degree-2 designs. Those four use constant-input extension blocks; the
nonconstant-input cases use satisfiable base systems. Thus these checks do
NOT computationally establish general PHP feasibility or the many-block
lower-bound target. They test identities and the constructive linear algebra.
The F_p generalization in the written argument is not computationally tested
by this GF(2)-only script.

The boundary control explicitly rejects the earlier sum-of-single-block
corrections without a mixed correction: it evaluates R_A E_B to 1 for two
constant blocks of accuracy 2.

## Remaining limitation

For s equal-degree blocks, iterating this moment-preserving construction can
cost

    C + 2^s (D-C),   C=h(delta+2),   D>C.

This is NOT an affordable bound for polynomially many blocks. The argument
proves the two-block step, but not block-count-independent global lifting,
and does not prove the desired Frege lower bound. It also does not assert
that the more restricted set-indexed component ansatz from earlier messages
is always feasible; the second-step components may use general moments of
the first block's variables.

## Run

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python checks.py

Requirements: Python 3.10+ and NumPy. results.json records every test instance,
component-system dimensions/ranks, annihilation counts, and runtimes.

## General-prime extension (proof, not exercised by checks.py)

For a prime p, replace the support factor g_j by

    chi_a(g_j) = 1-(g_j-a)^(p-1),   a in F_p nonzero,

and use r_(u,j)=t_u/a in the coefficient operator. Multiply the sum of
corrections by (-1)^(h+1). The component domains are

    N_j = D-h+(p-1)delta_j.

Their coupling equation is sum_(j,a) nu_(j,a)(G chi_a(g_j))=lambda(G).
If every coordinate of a G lies in the corresponding old consequence space,
then g_j=sum_(a nonzero) a chi_a(g_j) implies Gg_j does too. The identity

    G^p = sum_i q_i G^(p-2)(Gg_i)

and degree-nonincreasing reduction of G^p-G give the sufficient input bound

    Phi_(p,delta)(D)
      = max(D, pD-ph-((p-1)h-(p-2))delta).

The old system must contain the appropriate Boolean or F_p field equation for
every old variable. Every new field equation reduces to zero under the
auxiliary Boolean t substitution. Partial AND complete nonempty group
supports vanish because chi_a(g_j)(1-g_j/a)=0 modulo the old field equations.
Thus two arbitrary blocks need at most p^2 D input degree by composition.
Again this is a fixed-number-of-blocks result, not a cheap polynomially-many-
blocks theorem.
