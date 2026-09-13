# The first transported bit relation layer

The [notebook proof](https://kbr-.github.io/math-research/#entry-2026-09-13-bit-first-layer-classification)
identifies J_ell with I_ell(Q_n): bit Booleanity consequences plus the
independent span of compact pair-equality axioms, for n=2^ell and ell>=2.
For ell<=B<=n/2, compact-base NS and PC through B have no additional
consequences of degree at most ell.

The proof removes terms involving at least three rows using disjoint
coordinate cubes, then identifies the two-row coefficient kernel by a
degree argument for functions supported on the diagonal.
It extends the earlier four-label quadratic classification.
It does not prove full intrinsic stability above the first collision degree.

The entry also derives the exact collision-weighted residual in the
coherent-singleton construction at h+u+1=ell. Its vanishing on actual
retained source inputs remains an application question.

## Critical cube data

<code>critical-cubes-complete.jsonl</code> checks every ordered nonempty
family of nonempty coordinate-axis sets with total dimension exactly ell,
for ell=2..5.

| ell | Packable families | Complementary obstructions | Product tuples | Forced intersections |
| --- | ---: | ---: | ---: | ---: |
| 2 | 3 | 2 | 12 | 8 |
| 3 | 40 | 6 | 320 | 48 |
| 4 | 599 | 14 | 9,584 | 224 |
| 5 | 10,596 | 30 | 339,072 | 960 |
| Total | 11,238 | 52 | 348,988 | 1,240 |

All packable families pass the distinct-label, leading-monomial, and
missing-row-potential parity checks. The 52 obstructions are exactly the
ordered complementary pairs of axes. Every pair of their cosets is checked
to intersect once.

The program places larger-dimensional cubes first. The three unit-axis
cubes at ell=3 use the explicit placements from the proof; all other
positive cases use greedy placement. Cube arrays remain in the original
axis-family order, independently of placement order.

The schema is version 2. Labels and axis sets are integer bit masks, with
coordinate zero least significant. Family records save all axes, dimensions,
coset representatives, cube points, and complete missing-row parity arrays
as in the earlier strict-degree check. Each obstruction record identifies
its two axes; every intersection record saves both representatives and the
unique common point. Summaries include the count of obstruction families.

<code>critical-cubes.jsonl</code> is the preserved incomplete first attempt.
It ends before axes [1,1,4] at ell=3: naive greedy placement chose cubes
[0,1] and [2,3], leaving no coset of axis 4 disjoint from both.
Disjoint cubes do exist after a different placement. The corrected complete
run uses a fresh output path; the failed output was not overwritten.
The old strict-inequality suite was not rerun.

## Complete two-row coefficient quotients

<code>pair-potentials.jsonl</code> computes exact F2 quotients of functions
on ordered unequal labels (z,w), by the span of all row and column potentials.
Every mixed squarefree bit monomial of degree at most ell is mapped into
that quotient.

| ell | Unequal-label coordinates | Potential rank | Mixed source dimension | Image rank | Kernel |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 | 12 | 7 | 4 | 3 | 1 |
| 3 | 56 | 15 | 27 | 26 | 1 |
| 4 | 240 | 31 | 132 | 131 | 1 |
| 5 | 992 | 63 | 575 | 574 | 1 |
| 6 | 4,032 | 127 | 2,383 | 2,382 | 1 |
| 3, row potentials only | 56 | 8 | 27 | 27 | 0 |

Every positive kernel is exactly the mixed part of the compact equality
indicator. In mask form, it consists of all source monomials whose first-row
and second-row axis sets are disjoint. The row-only control is injective.

Each case record supplies the entire unequal-label coordinate list and
source-monomial list. In a monomial mask, the lower ell bits belong to z,
and the next ell bits to w. All vectors are sorted lists of nonzero
coordinates, over F2.

Potential records save the raw indicator vector, its reduction trace,
new pivot (or -1), and reduced vector. Source records save the raw image,
potential-basis and preceding image-basis traces, reduced image, and its
complete source combination. XOR the named preceding basis rows to replay
each reduction. Image combinations are tracked in the same way; a zero
image yields the complete kernel relation. These are coefficient-space
certificates, not whole PHP NS quotient computations.

## Reproduction and run status

Use fresh output paths:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_coordinate_cubes.cpp -o /tmp/math-bit-coordinate-cubes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-coordinate-cubes --critical --min-ell 2 --max-ell 5 \
  --out NEW_CRITICAL_CUBES.jsonl
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_bit_pair_potentials.cpp -o /tmp/math-bit-pair-potentials
./compute.sh run TURN --threads 1 -- \
  /tmp/math-bit-pair-potentials --out NEW_PAIR_POTENTIALS.jsonl
~~~

Both tools refuse existing output paths, use exact compiled F2 arithmetic,
and install no dependencies. The cube mode's initial compile failed on a
stream-expression typo; its first numerical attempt exposed the greedy
placement issue above. Both final compilations and numerical checks passed.
A separate indentation warning was removed before the quotient run.

The source files, shared binary linear algebra header, this description,
and all three output files are pinned by <code>provenance.json</code>.
Timing and complete command output are archived with the session.
An initial approval rejection of the preceding checkpoint's push was
resolved after reviewing concurrent navigation commits and citing the
standing Spin authorization.
