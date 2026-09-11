# Copy agreement, signed proof boundaries, and an exact NS/PC separation

11 September 2026. Session: `proof_core_boundaries_20260911_11`.
Full statements, proofs, and remaining obligations are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-copy-aware-cores).

## Mathematical outcome

Independent, internally coherent proof-line scopes make each line's signed
disjunction boundary fresh for the nonboundary extension system. Copy agreement,
weighted PC replay, and the earlier one-block target transfer eliminate these
boundaries through K0+2HL. The ordinary PHP endpoint then gives a PC refutation
over the exact weak base using only remaining nonboundary blocks. The degree is
polylogarithmic for polynomial-size, fixed-depth proofs at logarithmic accuracy.
The remaining proper-subformula blocks need not have smaller ENS depth, and
their elimination is open. No polynomial bound on the resulting PC proof length
is claimed or needed.

Sharing canonical proper evaluations while keeping the line boundaries private
removes the copy-agreement term from this bound. The construction shares identical
syntactic subformulas only, and does not merge distinct nodes merely because
their input polynomials coincide. Levels are assigned before cancellation.
Proper evaluations of the same formulas as deleted private boundaries may remain,
so no strict decrease in the number of distinct source gate constraints is claimed.

Additional results give explicit COPY and copy-aware MP identities, a uniform
formula-copy agreement bound, matched-core NS and PC transfer criteria, and the
height bound for proof-line occurrence chains. The fixed PC ceiling avoids the
extra NS image-certificate charge by reusing final derived polynomials.
Boolean-domain degree padding is recorded only as a possible, unused construction.

## Multi-prime identity checks

`copy-agreement-01.jsonl` retains 16 COPY identities and eight copy-aware MP
identities over p=2,3,5,7 and h=1,2. All reconstruct exactly through degree 6h.
The 16 omitted-agreement controls fail as expected. These are symbolic identity
fixtures, not complete Frege proofs or a formal verification of the full
boundary-elimination construction.

The old coordinates are 0 through 7. Input tuples are
g=(x0*x1, 1-x2), f=(g0+x3, g1+x4); the antecedent is a=x5*x6 and its implication
copy is alpha=a+x7. Literal COPY cases use f=g instead. Fresh coefficient IDs
start at eight, and every block stores its complete inputs, product, prefixes,
companions, and coefficient-variable arrays.

Each certificate records its target, ordered axiom array, cofactor array, and
actual/allowed degree. COPY axiom order is both left companions, both right
companions, and both input differences g-f. MP order is the implication product,
antecedent premise, both conclusion companions, all three implication companions,
alpha-a, and the two differences f-g. The antecedent companion remains explicitly
present with zero coefficient in the local MP certificate.

## Certified nine-variable separation

`copy-pc-ns-01.jsonl` proves minimum PC degree four and minimum ordinary NS degree
six for the target in the notebook's (COPY-gap) example. It is satisfiable binary
ENS data, not a PHP instance. The variable order is
`(x,y,z,r,s,t,w,u,v)`, all Boolean, corresponding to IDs 0 through 8.

The six nondomain axioms are x*g, y*g, x*f, y*f, f*Q, z*Q, with original ordinary
degrees 3,3,3,3,5,4. The file stores their polynomials, the input blocks, and the
target. Its complete 15-line PC trace derives g+f through degree four, multiplies
that final degree-two line by u and z, and adds z*Q. Every operation and line-degree
bound is checked by the generator.

For each NS degree, rows enumerate every nondomain axiom times every squarefree
multiplier within its ORIGINAL degree allowance, followed by Boolean reduction.
Field/Boolean multiples reduce to zero. Boolean reduction of other multipliers
does not enlarge their degree, so these rows cover all possible NS summands at
the stated degree. The original axiom degrees are not replaced by reduced degrees.

The quotient coordinates are bit masks of monomials in the nine variables;
coordinate m denotes the product of variables whose bits are set in m. All 512
coordinates are available, with unused high-degree columns zero. The complete
rows, exact ranks, separating functionals, and a lifted ordinary NS certificate
are retained:

| NS degree | Rows | Rank | Target belongs |
| --- | ---: | ---: | --- |
| 4 | 41 | 32 | No |
| 5 | 195 | 112 | No |
| 6 | 576 | 234 | Yes |

The degree-five dual has support masks 167,198,260,295,324,326,388,454. It annihilates
every row and evaluates the target to one; its eight monomials are written fully
in the notebook. A nontrivial positive control checks that the input difference
already belongs to the degree-four NS span. Corruption of either dual is rejected.
The degree-six membership certificate includes nondomain cofactors and explicit
degree-nonincreasing Boolean-domain cofactors; the notebook also gives a simpler
closed-form degree-six identity.

The notebook derives a further exact corollary: after adding 1-T, the system has
a degree-four PC refutation and an ordinary degree-four design. The latter is
the saved degree-four dual (support masks 198,260) plus evaluation at the old
system's model u=1, all other variables zero. This follows from the displayed
identities; no additional run or minimum-NS-degree claim for that augmented
system is made.

## Reproduction

With shared resource controls active, from the repository root:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_copy_pc_ns.cpp -o .resource-runtime/bin/check_copy_pc_ns
./compute.sh --threads 1 .resource-runtime/bin/check_copy_pc_ns \
  --out research/results/proof_core_boundaries_20260911_11/copy-pc-ns-REPRO.jsonl
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_copy_agreement.cpp -o .resource-runtime/bin/check_copy_agreement
./compute.sh --threads 1 .resource-runtime/bin/check_copy_agreement \
  --out research/results/proof_core_boundaries_20260911_11/copy-agreement-REPRO.jsonl
```

Use new output paths. The run used GCC 11.4.0, C++17, one thread, and the existing
sparse-polynomial, ENS, domain-reduction, and binary-linear-algebra kernels.
Only the generic linear algebra from `binary_php.hpp` is used; no PHP-specific
normal form or board restriction is applied. No dependencies were installed.

## Provenance and timing

`provenance.json` hashes both checkers, shared kernels, complete outputs, and the
same locally supplied BIKPRS source identified in SOURCE_AUDIT.md. Targeted reading
covered Definition 6.8, Lemma 6.9, and the previously audited simulation and leaf
lemmas. The earlier boundary-target proof and PC reuse conventions were reread.
No historical computation suite or rendering build was rerun merely for context.

`timing.html` is the measured notebook export. The interval includes completing
the preceding checkpoint and renewing publication authorization. The initial
source-review phase included interpretation and preliminary derivations before
the mathematics phase was marked. Computation design included correctness and
degree analysis. These recorded windows are not retrospective estimates of pure
internal cognition. Full command output and phase evidence are archived.
