# Disjoint leading pairs with shared quadratic tails

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-leading-pair-unbounded-sums)
proves a working all-prime criterion for complete one-level quadratic sources
and applies it to actual two-level unbounded sums. The inputs retain their
shared tails: a reduction only needs disjoint leading quadratic monomials,
not disjoint full probe groups. For R=Theta(v), polynomial inventory and
polylogarithmic source degree, the old degree is sqrt(n) times polylog(n).

The actual family has inputs u_i*v_i+Q_i(w), with private pairs and arbitrary
shared quadratic tails. An explicit tail is the cyclic sum of a_j*b_(j+i).
There can be linearly many inputs and summands per input. This does not prove
the leading-pair property for arbitrary Frege sources or remove later levels.

## Reproduce

From the repository root, with resource controls and an active timing session:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_leading_pair_source.cpp -o /tmp/math-leading-pair-source
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-leading-pair-source --out NEW_OUTPUT_PATH
~~~

The checker refuses existing output paths. No dependencies were installed.
The small shared graded_reduction.hpp preserves full ordinary ideal witnesses;
it is extracted from the preceding bounded-probe checker.

## Full exact output

`leading-pair-source-checks.jsonl` stores polynomial terms as
`[coefficient,[variable IDs with repetitions]]`. Arithmetic is exact over
F2, F3, and F5; large parameter integers are decimal strings.

In each field the twelve old variables are:

- u_i: IDs 0,1,2; v_i: IDs 3,4,5;
- a_j: IDs 6,7,8; b_j: IDs 9,10,11.

The three actual inputs are u_i*v_i + sum_(j=0)^2 a_j*b_((j+i) mod 3).
Graded lexicographic order prioritizes lower variable IDs. Reduction uses
the twelve Boolean divisors, then the actual inputs, in that order.
Its kernel-construction generators are not added to the old PHP base.

The 1,569 ordinary NS certificates comprise, in each of three fields:

- 455 reductions of every ordinary monomial through degree three;
- one kernel membership for f=u_1*g_0, with degree-three ordinary accounting;
- one Booleanization certificate for F=f^(p-1);
- 66 complete weighted source images: twelve old Boolean equations,
  24 bottom companions, 24 bottom fields, three parent companions, and
  three parent fields.

All targets and cofactors are retained and reconstructed. The normal space
has 266 monomials; no exact functional quotient dimension is asserted.
The extracted kernel cofactors, rather than an unrelated hand-chosen map,
give the parent coefficients c_i*f^(p-2).

The actual source includes twelve reused rank-two bottoms and a three-input
parent, on 39 variables. Every old input sum, complete block, coefficient
map, original source axiom, image budget, and NS witness is saved. Bottom
coefficients are (1,x), giving the literal product xy. The parent product
maps to 1-F. The weighted replay ceiling uses the actual coefficient degrees
1,4,10 and multiplier degrees 3,6,12 for the three respective fields.

All 3,664 conditional source assignments are saved: 960, 1,304, and 1,400
for p=2,3,5. At each nonzero-f old point, F=1 and every source companion
and genuine coefficient field equation holds. At old point 9 the weight
is zero and an unweighted companion has value one, in every field.
At old point 587 the first parent coefficient is two over F3 and three
over F5; its Boolean equation fails although its prime-field equation holds.

A saved row partition gives f row cap two. The Booleanized powers have
total degrees 3,5,9 and maximum row degrees 2,3,5. Thus retaining row cap
two after taking the odd-prime power would be incorrect; the theorem uses
the valid cap 2(p-1).

## Exact finite parameters

The nine parameter cases have p=2,3,5 and ell=40,64,128, with
n=2^ell, v=(n+1)*ell, M=n^2, D=ell^3, R=floor(v/4). Use the integer upper
bound H=3*ell+ceil(log2(ell))+4 on ln(8*M*(v+1)) and
k=ceil(sqrt(ceil(v^2*H/R))). All calculations use arbitrary-precision
integers, including the exact rational row-cap loss and both cube bounds.

All sufficient conditions hold at ell=64 and 128. At ell=40 the range,
image and domain conditions pass, but the old-degree room fails in every
field; cube packing also fails for p=5. Both positive and negative cases
retain full numbers and flags. These parameter checks are separate from
the local algebra fixture, which is not itself a PHP instance.

Compilation and the exact run passed. `check-metadata.json` records the
focused artifact and touched-link review; `provenance.json` records hashes.
Timing and complete command output are archived under this session name
in `research/provenance/session-records/`.
