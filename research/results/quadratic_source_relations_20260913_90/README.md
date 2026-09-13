# Quadratic source relations in affine coefficient coordinates

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-quadratic-source-relations)
contains the complete working statements and proofs. The new results give
sufficient tests for a quadratic input space to embed in the bounded
functional-PHP NS quotient. They do not compute an actual Frege proof or
establish complete source coverage.

For input coefficient vectors A_(i,j), every old quadratic relation has
an alternating Hessian C satisfying

    (A_(i,j)+A_(i,k))^T C (A_(a,b)+A_(a,d)) = 0

when the two rows differ and the four columns are distinct. A zero kernel
for this system on the r*(r-1)/2 Hessian entries proves faithfulness,
provided the inputs are independent modulo row equations and constants.
Nonzero rectangle kernels are candidates, not necessarily old NS relations.

The notebook also proves that the image of C lies in the span of
coefficient directions localized, modulo rows and a constant, on one row
and two columns. Dimension zero or one for that localized space forces
C=0. A conclusion space surviving every two-row/four-column deletion
retains quadratic faithfulness after adjoining any independent affine
antecedent. This certifies a conditional original level-one MP-A edge;
other source edges and larger supports remain obligations.

## Saved input and outputs

- `ambient-inputs.txt` contains the six eleven-hole inputs inherited from
  the preceding ambient certificate, converted to coefficient words.
- `deletion-rank-checks.jsonl` contains all deletion-rank certificates and
  localization witnesses, including the strong conclusion-space test.
- `rectangle-checks.jsonl` contains the direct alternating-Hessian
  constraint certificates for seven fixtures.
- `provenance.json` pins the code, helper, input, outputs, this record, and
  the inherited ambient certificate and its provenance.
- `timing.html` and the archived session retain measured phases, exact
  generating commands, compilation output, and complete run output.

The inherited data are
`research/results/nested_pair_compatibility_20260913_89/ambient-certificate.json`.
Their earlier full quadratic quotient certificates were not recomputed.
The new code performs exact F2 coefficient-space elimination, using packed
words and the existing compiled binary linear-algebra helper.

## Results

The first five inherited inputs are the conclusion tuple. All 21,780
two-row/four-column deletions retain rank five. Their rectangle matrix
has rank ten out of ten. The additional cell antecedent is x_(0,0).

| Fixture | N | Input rank | Basic deletions | Minimum rank | Localized dimension | Rectangle kernel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Archived ambient inputs | 11 | 6 | 660 | 6 | 0 | 0 of 15 |
| Five inputs plus cell antecedent | 11 | 6 | 660 | 5 | 1 | 0 of 15 |
| Single cell | 4 | 1 | 30 | 0 | 1 | 0 of 0 |
| Column pair | 4 | 2 | 30 | 0 | 2 | 1 of 1 |
| Row pair | 4 | 2 | 30 | 0 | 2 | 1 of 1 |
| Matching pair | 4 | 2 | 30 | 0 | 2 | 0 of 1 |

There are 1,440 basic deletion cases in total. Every fixture is globally
independent modulo row equations. For each deficient deletion, every
dual basis vector is tested against every remaining difference and is
converted into an explicit localized affine polynomial using row equations.

The column and row pairs have the actual old quadratic relation
U_1*U_2=0. The matching pair does not: the rectangle on rows zero and one,
with column pairs {0,2} and {1,3}, forces its only Hessian entry to zero.
Thus two localized directions need not themselves imply a relation.
The single-cell case shows that demanding full rank after every basic
deletion is stronger than necessary.

These four-hole controls test quadratic faithfulness and localization.
They are not applications of a degree-four ENS lower bound on four holes.
The eleven-hole MP example supplies a first-boundary pair hypothesis at
h=1, D=4; it does not by itself supply all edges of a completed source
certificate. No new full old NS quotient or joint moment array was built.

## Certificate encoding

The input text starts with `N r constant_word`, followed by N+1 rows of
N coefficient words. Bit s of a word is the coefficient of input U_s.
Cells, input coordinates, and row indices are zero-based. The constant
word uses the same input-coordinate convention. The inherited sparse
input encoding instead uses index zero for one and 1+i*N+j for x_(i,j);
the conversion command is preserved in the session evidence.

Each deletion record specifies the omitted rows and columns and the
reference remaining column. Each independent generator records its row,
column, original coefficient-difference word, reduction trace, pivot, and
new basis word. A full-rank search stops after finding a basis, since the
ambient rank is an immediate upper bound. A deficient search scans all
generators and includes a complete dual basis, checked again against all
remaining differences. Its record also gives the row-equation coefficients,
remaining constant, and cell support of each localized input combination.

The strong test uses exactly two omitted rows and four columns. Full rank
there implies the same property for smaller deletions by containment.
Basic tests omit exactly one row and two columns. Their summaries retain
the complete rank histogram and a basis of the span of all localized
directions.

Rectangle words order Hessian coordinates lexicographically by (s,t),
s<t. Each independent constraint specifies its two rows and four columns,
original word, elimination trace, pivot, and reduced basis word. A
full-rank certificate needs only a subset of all possible constraints;
the search stops when it reaches the known ambient dimension. Deficient
systems include their full kernel basis, verified on every rectangle.
For r=1 the Hessian coordinate space has dimension zero.

## Reproduction

From the repository root, use the saved input and fresh output paths:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_quadratic_source_relations.cpp \
  -o /tmp/check_quadratic_source_relations
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_source_relations \
  --ambient research/results/quadratic_source_relations_20260913_90/ambient-inputs.txt \
  --out NEW_DELETIONS.jsonl
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_source_relations \
  --ambient research/results/quadratic_source_relations_20260913_90/ambient-inputs.txt \
  --out NEW_RECTANGLES.jsonl --rectangles
~~~

The initial build reported indentation warnings, which were corrected.
Both subsequent builds were warning-free; both exact runs passed within
the shared CPU/memory boundary. No commands failed and no dependencies
were installed. The optional rectangle mode leaves the earlier deletion
calculation unchanged; it does not rerun the 21,780-case strong test.
