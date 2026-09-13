# Coherent moments for affine-bit families

The [full notebook theorem](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-affine-coherent-band)
extends every Ann(J_D) functional over any one-level affine-bit ENS family when
D=3h+u, 1<=u<=h, h+u+1<ell, n=2^ell, and n>=2D-1.
All original nonconstant-affine companions have degree 2h+1.
There is no family-count or input-span separation hypothesis.

A common full Boolean functional prescribes low moments using first-success
input selectors. Low-degree rigidity makes the coupled singleton prescriptions
consistent; stability then extends the prescribed pair moments independently.
The theorem concerns ordinary NS designs and old consequences landing in J_D.
It does not transfer augmented PC proofs or cover the completed source degree
and later extension levels.

## Finite model and coverage

<code>coherent-moments.jsonl</code> retains the full exact model, component
tables, all companion checks, and both negative controls.

The model has six old Boolean variables and three blocks, with h=2, u=2, D=8:

- A: (y0,y1,y2,y3,y4).
- B: (1+y0,y1,y2,y3,y5).
- C: (y0+y1,y1,y2,y3,y4).

Each input space has affine rank five, above 2h=4. A and C have the same span
in different bases. B intersects them. The old base is Booleanity only, a
satisfiable finite model, not compact PHP. The root functional is
evaluation at 0 plus evaluation at e0 plus evaluation at e1 over F2.
It is normalized and not multiplicative.

Start with pointwise first-success singleton and pair values. Perturb the
supported precursor nu at the degree-six monomial y0*y1*...*y5 when block
index plus input index is odd. Root coupling uses products of degree at most
five, so it is unchanged. Define mu(P)=nu(g*P).

Perturb each pair functional at y0*y1*y2*y3 when the sum of its block and
input indices is odd. The prescribed pair products have degree at most
three. Thirteen actual singleton and 38 pair moments change.

There are 36 joint variables and 15 companions. Every squarefree cofactor of
degree at most 8-5=3 is checked, giving 7,807 cofactors and 117,105 equations.
All moments vanish. The functional factors through the full Boolean quotient,
so every field-axiom multiple vanishes identically. Powered cofactors reduce
to the enumerated squarefree cofactors without increasing degree.
This quotient evaluation does not lower the original companion budget of five.

The deliberately changed low value phi[0,1][1,0](1) gives a saved companion
violation. With unperturbed singletons/pairs and zero triples, five of 375
two-foreign-block controls fail at original degree 4h+1=9. The finite model
still admits satisfying extensions; this only detects missing components
in the truncated construction.

## Complete encoding

All arithmetic is in F2. Monomials are uint64 bit masks and all polynomial
lists are XOR sums of their masks in the Boolean quotient.
Old variables have IDs 0..5. A fresh variable has ID
6 + (block*2 + factor_row)*5 + input, with all indices zero based.

The root record lists all 64 old squarefree moments in mask order.
Each singleton record identifies its input polynomial and complete Boolean
companion, then lists nu, mu, and unperturbed mu at all 64 old masks.
This covers the required domains L+1=7 and L=6, since the old algebra has
only six variables. Pair records give the complete mask list through
H=4, with perturbed and unperturbed values.

For a Boolean joint monomial, the diagonal construction returns:

1. The root old moment if it has no fresh variables.
2. The appropriate singleton if exactly one block has all its factor rows
   on one selected input and no other fresh variable occurs.
3. The appropriate pair if exactly two blocks have this form.
4. Zero for all other fresh supports, including three complete blocks.

Every companion-check record gives its block, input, cofactor mask, and
resulting zero moment. A separate record gives the corrupted-pair witness.
All 375 missing-triple controls are saved, including their zero values.
The final summary records all counts and verifies nonvacuous perturbations
and controls.

## Reproduction

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_coherent_affine_moments.cpp \
  -o /tmp/math-coherent-affine-moments
./compute.sh run TURN --threads 1 -- \
  /tmp/math-coherent-affine-moments --out NEW_OUTPUT.jsonl
~~~

The program refuses existing output paths and uses no random choices or
external dependency. An initial compiler indentation warning was corrected;
the final compile was warning-free and the sole numerical run passed.
Source, description, and complete data are pinned by <code>provenance.json</code>.
The timing note discloses that initial source review also included construction
planning. Full command outputs and the journal are archived with the session.
