# A common column restriction for a mixed affine ENS family

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-common-star-affine-coverage)
contains the complete affine row-replacement proof, common-support
restriction theorem, finite application, and remaining source gap.

The direct universal pair-cancellation question remains open. Pure
single-column tuples were already covered by the existing normalizer;
this cycle treats tuples that also contain dense affine inputs.

## The proved criterion

Suppose all one-level binary affine inputs are combinations of a common
affine core and localized terms, modulo constant combinations of row
equations. If one matching restriction makes all localized terms constant,
leaves the core's Boolean quadratic space injective in the residual old
NS quotient, and leaves N>=2D-1 holes for D=3h+1, then no degree-D augmented
NS refutation exists. There is no family-count degree charge. The cost is
the actual number of holes removed by the matching.

The notebook first proves that affine changes modulo row equations have
companion-difference certificates through original joint degree 2h+1.
After restriction and zero/unit-span cleanup, every pair is contained in
the faithful residual core, so the previous simultaneous moment theorem
applies. The final result is an NS exclusion, even though the preliminary
row replacement and restriction also preserve PC derivations.

Only one branch is needed to exclude an assumed refutation. This is not
an extension of every prescribed functional on the original board.

## Exact family and evidence

Use the first five U_0,...,U_4 from the preceding eleven-hole input file.
For every c in F2^5 and k=0,...,5, take

    (U_0+c_0,...,U_4+c_4,x_(2k,0),x_(2k+1,0)).

This defines 192 blocks of seven affine inputs, h=1, D=4. The original
linear parts have rank seven modulo rows for every pair k. Each block
contains a nonzero Boolean product x_(2k,0)*x_(2k+1,0) that is an old column
exclusion. Thus every original pair fails the faithful-map hypothesis.
The within-core product spaces all have dimension 15 inside a certified
16-dimensional unital quadratic space, so every two original full-block
product spaces intersect in dimension at least 14. This is an analytic
dimension conclusion, not a separate numerical audit of all 18,336 pairs.

The zero spaces of the block inputs cover the entire proper single-column
state domain: choose the translation equal to the core value, then choose
a column pair avoiding the at most one occupied cell. Consequently every
common Boolean vanishing polynomial is already an old consequence through
its own degree, by the existing degree-complete column reduction. This
does not assert that every full-base relative-membership method fails.

| Restriction | Residual holes | Unit blocks | Core-only blocks | Blocks retaining a collision |
| --- | ---: | ---: | ---: | ---: |
| Match row 11 to column 0 | 10 | 32 | 160 | 0 |
| Match row 11 to column 1 | 10 | 0 | 0 | 160 |

Both residual cores have linear rank five and rectangle rank ten out of
ten. The covering restriction leaves five copies of every translated core
tuple. It satisfies the theorem and excludes the original augmented NS
degree-four refutation. The wrong-column branch still has local variables
in every block; 160 retain two colliding cells, and 32 retain one cell.
It demonstrates failure of the support-removal hypothesis despite a
faithful residual core, not failure of the family's lower bound.

`column-family-checks.jsonl` preserves:

- The complete original and restricted coefficient words.
- Six original tuple-rank certificates and twelve residual tuple ranks.
- Both residual core ranks and complete rectangle certificates.
- Every original collision relation and its Boolean nonvanishing witness.
- All 384 block images across both restrictions, including translation,
  local-cell images, constant words, and cleanup status.

The computation is exact packed-word F2 linear algebra. It does not build
a full old NS quotient, an augmented joint moment array, or a Frege proof.
The analytic transfer supplies the degree-four exclusion from the checked
hypotheses. Compilation and the run passed, with no dependencies installed.

## Encoding and reproduction

Input words and rank traces use the preceding checker's conventions:
word bit s is the coefficient of input s, and cells are row-major with
zero-based indices. A matching deletes its row and column in order and
adds the selected cell's coefficient word to the constant word.

In `local_images`, -2 means one, -1 means zero, and a nonnegative value
is the residual row-major cell index. Core translation c changes only
the five-bit constant word. Rank certificates depend only on linear parts
and therefore cover all 32 translations for their pair. A record with
`unit_input=true` is removed by constant first-row ENS coefficients.

From the repository root, use a fresh output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_quadratic_source_relations.cpp \
  -o /tmp/check_quadratic_source_relations
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_source_relations \
  --ambient research/results/quadratic_source_relations_20260913_90/ambient-inputs.txt \
  --out NEW_COLUMN_FAMILY.jsonl --column-family
~~~

This optional mode reuses the coefficient and rectangle routines. It does
not rerun the preceding deletion suites. `provenance.json` pins the code,
helper, output, input, this record, and the inherited ambient/core evidence.
`timing.html` and the archived session preserve the measured work and
complete protected-command output. A preliminary notebook lookup used a
nonexistent anchor and was immediately corrected; it was not a failed
mathematical computation.

The next source obligation is the actual MP cofactor identity, including
the antecedent proof and its composition degrees. Neither a small common
support nor universal nonfaithful pair cancellation has been proved for
the complete source family.
