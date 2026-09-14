# Audit of the quadratic pair-consequence interface

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-quadratic-pair-interface-audit)
refines the earlier disjoint-sum span obstruction to the full Boolean
vanishing ideal. For disjoint q_i=a_i*b_i+c_i*d_i, its multilinear
degree-at-most-two part is exactly the constant span of the q_i.
All nonzero combinations have polar rank at least four, so no product of
two affine forms with independent linear parts is an ideal consequence,
at any degree.

The same family remains covered by the existing leading-pair reduction.
Thus this is an interface obstruction, not a new proof lower bound or an
obstruction to all kernel-compression methods. The notebook states the
weaker codimension condition that would suffice for the main route's
quadratic endpoint, without asserting it for arbitrary sources.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_quadratic_pair_obstruction.cpp \
  -o /tmp/math-quadratic-pair-obstruction
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-quadratic-pair-obstruction --out NEW_OUTPUT_PATH
~~~

The checker refuses existing outputs. No dependencies were installed.

## Complete exact data

`quadratic-pair-obstruction.jsonl` stores all common-zero assignments,
the complete degree-two evaluation matrices, RREFs, pivots, and recovered
kernel bases. Squarefree features are bitmasks; matrix rows are binary
strings in the listed feature order. Ordinary polynomial terms are
`[coefficient,[variable IDs with repetitions]]`, over F2.

| Input fixture | Variables | Common zeroes | Features | Rank | Kernel dimension |
| --- | ---: | ---: | ---: | ---: | ---: |
| Single product ab | 2 | 3 | 4 | 3 | 1 |
| One disjoint two-pair sum | 4 | 10 | 11 | 10 | 1 |
| Two disjoint two-pair sums | 8 | 100 | 37 | 35 | 2 |
| Three disjoint two-pair sums | 12 | 1000 | 79 | 76 | 3 |

Each full matrix kernel is verified to be precisely the original input
span. All eleven nonzero combinations of the two-pair sums have polar
rank four times their number of active groups. The single-product control
has polar rank two and genuinely supplies a pair consequence; the
obstruction flag correctly fails there.

Six complete ordinary NS certificates verify
a_i*b_i*(1-c_i)=(1-c_i)*q_i+d_i*(c_i^2-c_i), through degree three.
The targets, original generators, and every cofactor are retained, with
each generator multiple charged. These cubic products illustrate that
the obstruction is specifically about independent quadratic pairs.

Compilation and all exact checks passed. The fixtures concern the input
ideal over the Boolean cube; they are not PHP models. The universal
classification is proved directly in the notebook, and is not inferred
from these finite ranks.

`check-metadata.json` records the focused evidence and touched-link check;
`provenance.json` records code and evidence hashes. Timing and full command
output are archived under this session name in
`research/provenance/session-records/`.
