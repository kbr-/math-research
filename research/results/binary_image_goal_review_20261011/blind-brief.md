# Independent architecture comparison

Read the canonical reviewer instructions in `.claude/agents/medium-reviewer.md`.
This is stage one of the same reviewer's staged architecture review. The current
preferred approach and recent cycle conclusions are deliberately withheld.
Do not inspect notebook living sections or other research records yet. Do not
edit files, run computations, request escalations or send external messages.

## Goal and constraints

For every fixed depth d, prove a superpolynomial proof-symbol-size lower bound
for AC0[2]-Frege on some family of unsatisfiable CNFs or tautologies of encoding
length N. The family may depend on d but must be fixed independently of the
proposed polynomial size exponent A. Any family is allowed. A binary result is
an accepted milestone toward the separate all-prime goal. Restricted-source
theorems, new representations and stronger sufficient criteria are not themselves
the lower bound.

## Available proved results, as optional black boxes

These statements orient the independent search. Full proofs will be supplied
for any actual reliance in the correctness stage; do not silently strengthen them.

1. **Binary PC simulation.** In the audited coherent flat-clause presentation,
   an unsatisfiable CNF of width w and a bounded-depth modular Frege proof give a
   PC refutation of its old CNF axioms plus complete binary ENS blocks. Choose
   accuracy h >= max(1,w). The ceiling is c L, where c is a fixed presentation
   constant and L <= (d+1) h^d for the structural depth. There is no proof-height
   factor. Retain every dependency level and the original source degrees. The
   source inventory is O(S) whole product objects and at most O(S^2) coefficient
   slots for proof symbol size S. Inputs are affine expressions in old literals,
   boundary predicates and earlier whole products, with arbitrary sharing.
   Sources: cor:binary-unbalanced-CNF-source; the presentation inventory proof
   in entry-2026-10-09-pullback-iteration.

2. **Complete blocks and paid replay.** A block retains g_i P, all r^2-r, and
   P=product_{u<=h}(1-sum_j r_{u,j} g_j). If original input degrees are d_i and
   delta=max d_i, the product costs h(delta+1), companion h(delta+1)+d_i.
   Cancellation/zero padding do not reset these costs. A single fixed old-variable
   substitution of degree T and surviving multiplier of degree b preserve an
   original degree-B PC replay through b+T B. Constant substitutions have T=1.
   Raw coefficients may occur in proof lines; complete fields cannot be omitted.

3. **Old hard systems.** Charged modulo-three Tseitin over F2 has proper old
   degree-D pseudoideals in the recorded expander window, with D linear in
   variable count on fixed-degree families. A specific character construction
   over F4 descends to F2 without degree loss. For a graph with n vertices,
   m edges, expansion epsilon and max degree Delta, its window includes
   max(4,2Delta)<=D<epsilon*n/8. It counts cut-code cosets meeting support balls.
   Growing Delta=ceil(log n)^2 gives m=Theta(n Delta), D=Theta(n Delta) in the
   specified smaller constant range, and log N=Theta(Delta) for the literal CNF
   encoding. It is a truncated pseudoideal, not a global satisfying-point algebra.

4. **Weighted free coordinates.** If a proper Boolean J_D contains an
   unsatisfiable base Gamma and w survives, degree w <=b,
   D-b>=max(2,max degree Gamma), there are D-b-1 old coordinates whose entire
   Boolean monomial family has independent weighted images. Their pins survive
   at their paid degree. This does not preserve arbitrary multiplication outside
   the window or promise that source inputs use only those coordinates.
   Source: cor:weighted-restriction-cube.

5. **Known limited lower bound.** For the audited presentation with ell>=2
   coherent source levels, the fixed bounded-degree Tseitin family requires more
   than n^(1+rho) symbols for each rho<1/(2^(ell-1)-1). Its symbol encoding is
   Theta(n), ordinary bit encoding O(n log n). The missing larger exponents are
   essential; this is not a proof-line result or the superpolynomial goal.
   Source: cor:presentation-polynomial-size-bound.

6. **Different size route.** The recorded Grochow–Pitassi depth-preserving
   simulation, in its audited binary sequent/3CNF scope, gives polynomial-size
   Hilbert-like IPS certificates of depth d+2 from depth-d modular Frege. It keeps
   all Boolean correction terms. A lower bound must cover every relevant formal
   certificate, not only one representative or its values on Boolean points.
   Source: imp:depth-preserving-IPS-simulation (Theorem 2.3, April 2014 manuscript).

## Explicitly missing statements

- The binary lower bound above: open, with no unrestricted source construction.
- The all-prime goal: open; binary first is permitted.
- A complete ordinary-PHP source-exclusion route: optional and open.
- The parallel Near-half PC notebook reports no qualifying family; none is
  supplied here as a theorem. Generic regularity/counting conjectures from that
  work may not be used as proved premises.

## Request

Propose a materially different, concrete architecture using these facts or a
clearly named additional theorem, or explain that you found none in this bounded
pass. State the weakest missing implication, actual quantifiers and degree/size
budget. Distinguish an existential endpoint from extra demands on every choice,
all classes, literal functions or a chosen representation. A reduction merely
renaming the original problem is not progress. Do not invent confidence numbers.

Return a brief stage-one assessment. The current route and full cycle evidence
will then be revealed to this same reviewer for comparison and correctness.
