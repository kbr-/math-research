# Common vanishing polynomials for affine ENS families

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-affine-common-vanishing)
contains the complete proofs, original-degree accounting, parameter application,
and remaining gap.

Over F2, the audited chessboard connectivity theorem lets every degree-k
functional-PHP design extend through B when N>=2B-1. Annihilator duality and
induction on PC multiplication then give C_B=I_B and C_B intersect P_<=k = I_k.
This is a base-system theorem with an explicit range, not augmented PC closure.

For a one-level affine ENS family, let Z_b be the common-zero affine space of
block b after removing zero and unit-span blocks. Every degree-k polynomial f
vanishing on all Z_b has a degree-k Boolean-ideal representation in each input
tuple. Specialize the first coefficient row to that representation and all
other rows to zero; multiply the entire specialized proof by f. All companions
become Boolean consequences. An augmented degree-D refutation therefore learns
f from the old base through B=max(1,k-1)*D+k, with no additive block-count charge.
The notebook proves both PC and NS versions, assuming D>=2h+1.

The common restriction kernel has codimension at most sum_b b_k(v-r_b),
where v=N(N+1), r_b is the affine codimension, and b_k(w)=sum_{j<=k} choose(w,j).
The functional-PHP quotient has dimension at least

    sum_{j=0}^k m_j - sum_{j=0}^{k-1} (N+1-j)*m_j,
    m_j = choose(N+1,j)*choose(N,j)*j!.

If this lower bound exceeds sum_b b_k(v-r_b), and N>=2B-1, the learned kernel
would be larger than the available base consequence space: no augmented
degree-D PC refutation exists. The weak-base conclusion follows by explicit
functional strengthening.

For r_b>=rho*v with fixed rho>0, polynomial block count M, polynomial residual
size N, and polylogarithmic D, k=O_rho(log(M+1)) suffices. This covers the earlier
resistant rank/core family on every specified square-root residual. Intermediate
affine ranks, odd-prime MOD inputs, and multilevel propagation remain open.
This is not a full PHP/Frege lower bound or a proof-size upper bound.

## Exact parameter evidence

dimension-checks.jsonl retains all counts, including every degree term, using
arbitrary-precision integers. Large integers are decimal strings; parameters
are ordinary JSON integers. No floating-point arithmetic or randomness is used.
The schema and summary records describe the format.

| Case | k | B | Dimension condition | Stable degree condition |
| --- | ---: | ---: | --- | --- |
| N=200, M=1000, r=36000, h=2, D=10 | 6 | 56 | Pass | Pass |
| Same parameters, insufficient k | 1 | 11 | Fail | Pass |
| N=40, M=1000, r=1476, h=2, D=10 | 6 | 56 | Pass | Fail |
| Resistant scale q=16 | 60 | 15164 | Fail | Fail |
| q=24 | 84 | 47892 | Pass | Fail |
| q=32 | 109 | 110701 | Pass | Fail |
| q=40 | 134 | 212934 | Pass | Fail |
| q=42 | 140 | 245336 | Pass | Pass |
| q=44 | 146 | 280866 | Pass | Pass |
| q=48 | 159 | 364191 | Pass | Pass |
| q=56 | 184 | 574072 | Pass | Pass |
| q=60 | 196 | 702196 | Pass | Pass |

The scaled parameters are n=2^q, M=n, N=2^(q/2-2),
r=floor((N^2-1)/4), h=q, D=q^2. The checker chooses the smallest k satisfying
8*M*4^k<=5^k by exact integer multiplication. Six cases satisfy both conditions.
The two explicit failure controls verify different necessary hypotheses of
this sufficient criterion. Failure is not a refutation or a converse theorem.

These computations instantiate numerical hypotheses for any family with the
specified ranks. They do not construct large affine matrices, run a PHP
proof search, or check the separate existence union bound for the recorded
resistant construction. That construction's asymptotic proof is unchanged.
The representative D=q^2 is not a claim about every source-depth exponent.

## Reproduction and provenance

Use a fresh session and output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_affine_vanishing_dimensions.cpp \
  -o /tmp/check_affine_vanishing_dimensions
./compute.sh run TURN --threads 1 -- \
  /tmp/check_affine_vanishing_dimensions --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded under the shared resource boundary.
Boost multiprecision headers were already installed; no dependencies were added.
All finite arithmetic is in the compiled checker. No historical suite was rerun.
provenance.json pins the checker, complete output, this record, the prior
connectivity/resistant-family provenance, and the reused historical arguments.

The topology input is Björner, Lovász, Vrećica, and Živaljević,
*Chessboard Complexes and Matching Complexes*, JLMS 49 (1994), 25–39,
Theorem 1.1, DOI 10.1112/jlms/49.1.25. Its exact source audit and acquisition
record remain in the preceding chessboard-marginal entry. No new paper was
needed or acquired for this cycle, and no third-party full text is published.

The opening window/pebbling review reused historical results rather than
producing new claims; the new work is the extension/filtration consequence,
common-vanishing learning, and family-wide dimension exclusion. The clock
includes restoration after compaction and the preceding checkpoint work.
One short source/tool read overlapped the coding window. No retrospective
timing split was invented.

The process assessment is recorded in the notebook: the new theorem covers
the resistant class, and index-guided reuse avoided presenting the older
window/pebbling controls as new results. No extra framework rule was needed.
