# Affine rank resistance on every square-root residual

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-affine-residual-rank-obstruction)
contains the full proof and scope. It refines the earlier resistant-family
template to restrictions leaving a square-root board, using uniform rank of
linear parts on retained vertex sets. The matching-dependent constants need
no separate union bound.

For M=n and residual N=floor(sqrt(n)/4), input ranks
r=floor((N*N-1)/4) survive on every residual. All pairs remain disjoint modulo
row equations and expose no constant-one span. The functional auxiliary base
has the same affine-consequence rigidity in the stated low-degree range.
The existing affine core criterion consequently has optimized ceiling
min(D+M, T(r)*D)=Omega(n), exceeding the square-root residual budget.

This is a criterion-specific control on polynomial-size MOD2-compatible
inventories. It supplies no augmented refutation, no proof-essentiality
statement, and no lower bound against other normalization or proof-dependent
methods. The literal-family coverage theorem remains valid.

## Complete finite witness

The accepted rank-witness.jsonl is 2,206,666 bytes. It contains:

- The metadata and full source matrix from the first draw.
- Every one of the 4,704 retained 6-by-5 subboards of a 9-by-8 board.
- All restricted input linear parts for eight blocks of rank three.
- All 37,632 block ranks and 131,712 pair ranks modulo row-sum linear parts.
- A rejected duplicated-block control and the accepted-draw summary.

The linear-part certificate covers all 28,224 size-three partial matchings
through the proof's constant-shift argument. Their constant terms were not
enumerated separately. This fixture checks the algebraic conditions, not the
large-n asymptotics. The exact existence union bound here is
8,297,856 / 16,777,216 < 1.

Source inputs have zero constant term. Each input is stored as nine byte-valued
row masks; bit j in row i is the coefficient of x_ij. Residual linear parts use
bit 5*i+j in the increasing retained row/column order. Pair ranks are in
lexicographic (a,b) order with a<b. All arithmetic is exact F2 XOR elimination.
The generator is std::mt19937_64, seed 20260912; its low eight output bits
produce each row mask. The first draw passed every condition.

Reproduce from the repository root, with a new output:

~~~bash
./compute.sh --threads 1 --category local_processing \
  g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_affine_residual_rank_family.cpp \
  -o /tmp/math-affine-residual-ranks
./compute.sh --threads 1 /tmp/math-affine-residual-ranks \
  --out research/results/affine-residual-recheck.jsonl --seed 20260912
~~~

The single strict-warning build and run passed. Both used the shared resource
limits and one thread; no dependency was installed.

## Dependencies and measurement

The earlier notebook resistance argument was read at resistant-counting,
resistant-existence, and resistant-scope. The historical chapter
php_codex_handoff/manuscript/chapters/09_decomposition.md supplies the precise
affine-consequence rigidity proof and Theorem 9.6's optimized criterion argument.
The preceding functional-auxiliary result supplies the matching-preserved
lower-bound interface. The manifest identifies sources, code, and full output.

Initial preparation includes the preceding research and framework checkpoints.
Reading includes comparison with the earlier resistance template. Mathematics
also includes the initial finite-fixture design before the coding marker; this
mixing is not retrospectively split. Coding, compilation, and the exact run
are recorded separately. Proof review and notebook drafting remain in
mathematics, with complete command evidence in the archived timing session.

The claim-index lookup prevented treating the resistance template as unrelated
new work. No additional framework change was warranted.
