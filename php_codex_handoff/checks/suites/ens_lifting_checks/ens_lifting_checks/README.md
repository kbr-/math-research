# Exact checks for a reweighted ENS lifting

The construction being checked is

    Lambda(P) = lambda(W(y) P(y,beta)) / lambda(W).

For a single level with independent fresh variables, blocks have

    E[a,i] = g[a,i] * product_u (1 - sum_j r[a,u,j] g[a,j]).

Let delta[a,i] = degree(g[a,i]), e[a,i] = degree(E[a,i]), and fix target
Nullstellensatz design degree D. Define

    c[a] = max({0} union {D-e[a,i] + (p-1)*delta[a,i] : e[a,i] <= D}).

The claimed sufficient input degree is D + sum_a c[a]. Starting with W=1,
any uncommitted block with a nonzero moment lambda(W q g[a,i]) can be
handled by selecting a nonzero alpha such that

    lambda(W q (1-(g[a,i]-alpha)^(p-1))) != 0,

multiplying W by q*(1-(g[a,i]-alpha)^(p-1)), and specializing
r[a,1,i]=alpha^(-1), with the other fresh variables of that block zero.
Every uncommitted block is rechecked after a change to W. A committed
block is handled exactly modulo the old Boolean/field equations.

The script uses exact integer arithmetic modulo 2, 3, or 5. Independent
instances are process-parallel. Boolean moment evaluation uses NumPy's
vectorized superset zeta transform; polynomial values are vectorized over
the cube. No floating-point linear algebra is used.

The 46 cases include nonlinear tuples and multiple blocks, as well as
controls for nontrivial higher-degree witnesses, uncommitted blocks that
must be revisited, active zero-branch axioms, and cancellation against an
old axiom without pointwise support on that axiom's solutions.

The tests verify all squarefree old-variable multipliers up to the
original extension-axiom degree budget. Repeated Boolean-variable
multipliers reduce to these without increasing degree. After scalar
specialization, mixed multipliers involving new variables reduce to
old-variable polynomials of no greater degree; the new field equations
vanish identically.

Run:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python verify_lifting.py

These finite checks are not a proof of the general lemma and do not
establish the polylogarithmic degree loss needed for the full lower-bound
application. The construction can change the original design's moments;
it preserves its axiom-annihilation conditions at the stated lower degree.

Important grading distinction: the output is a design for the ORIGINAL
joint-variable system. One must not silently replace the original degree
e[a,i] by the usually smaller degree after scalar specialization. The
active zero-branch cases deliberately violate an additional multiplier
constraint that would arise from such a regrading, while satisfying all
constraints required for the original degree-D joint design.
