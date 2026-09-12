# Moment-rank growth obstructs the unrestricted pseudo-solution rate

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-moment-rank-query-obstruction)
contains the full proofs, source comparison, parameter accounting, and scope.

For an unsatisfiable Boolean system with generators of degree at most two,
the moment matrices of any ordinary degree-D design cannot be flat at an
adjacent pair of degrees through floor(D/2). Flatness would give commuting
idempotent multiplication operators satisfying every generator, and hence a
Boolean solution. Moment rank is therefore at least t+1 at degree t; over F2
it is at least 2t+1 by the parity of the centered alternating form.

Applying the covariance probe to all degree-t polynomials, rather than just
variables, gives a universal distributional obstruction. For S>=2, h>=1,
D>=2h, no design distribution over any prime field can meet the sufficient
ENS rate gamma>S*(1-1/p)^h at height h+ceil(log2 S).
For F2, D>=h+1 already suffices.

This covers the weak PHP base directly. It rules out an unrestricted query
guarantee in this regime; it proves neither an ENS upper bound nor a Frege
lower bound. A guarantee for a genuinely smaller, source-justified query class
would require a separate argument.

## Exact finite evidence

moment-rank-checks.jsonl preserves every matching moment, every row-set filling
summary, and complete XOR rank-elimination traces.

| Case | Degree | Moments | Row multiples checked | Gram ranks at t=0,1,2 |
| --- | ---: | ---: | ---: | --- |
| Seven holes, eight pigeons | 4 | 71793 | 103944 | 1, 3, 505 |
| Five holes, six pigeons, two collisions | 2 | 331 | 186 | 1, 3 |
| Three-hole satisfiable injection | 4 | 34 | 102 | 1, 1, 1 |

The corresponding centered ranks are 0,2,504; 0,2; and 0,0,0.
The first case starts with the preceding rank-two quadratic prototype and
fills cubic and quartic moments separately on each row set. The second gives
an explicit rank-two mean outside the one-collision promise: destinations
(0,0,1,1,3,4), leaving column 2 empty. The earlier search selects that empty
column on this mean. Its displayed search answers also follow directly from
the complete saved first moments; the checker verifies the moment constraints
and rank. The third is a point evaluation for a satisfiable, equally sized
board, demonstrating why unsatisfiability is essential to rank growth.

Indices are zero-based; variable (i,j) is bit i*n+j. Matching masks are
hexadecimal 64-bit words. Products combine masks by OR; a union containing
a row or column collision has moment zero. Repeated cells reduce by Booleanity.
Monomials are enumerated by degree, then increasing cell choices.
The rank_step rows refer to the prefix of this enumeration of degree at most t.
Each trace lists prior pivot rows XORed into the original Gram/centered row,
and its final reduced support. The initial matrix is reconstructed exactly
from the saved moments. No floating-point arithmetic or PC closure is used.

Fillings use normalized augmented right-hand-side coordinate zero and set
all other free coordinates to zero. All original boundary equations and all
global NS row multiples were checked. The row and column exclusion/Boolean
multiples hold by the proper matching normal form. No randomness is used.

## Reproduction

Use a fresh session and output path for replay; the checker refuses overwrites.

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_design_moment_rank.cpp -o /tmp/check_design_moment_rank
./compute.sh run TURN --threads 1 -- \
  /tmp/check_design_moment_rank --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded under the existing resource controls.
No dependencies were installed. The new ranks are finite examples, not the
proof of the universal theorem. provenance.json pins the source, helper,
complete output, source locators, and dependency evidence.

## Source and process scope

The source's query definition and Theorem 3.2 were reread in Krajicek's
arXiv:2301.10617v3, pages 6-7. They impose a degree and height bound, with no
sparsity or circuit-size bound on query polynomials. Weighted finite laws
are covered by the same averaging argument; uniform sets are a special case.

The flat-matrix technique has prior literature: Laurent and Mourrain,
A Sparse Flat Extension Theorem for Moment Matrices, arXiv:0812.2563v1,
later published as A generalized flat extension theorem for moment matrices,
Archiv der Mathematik 93 (2009), 87-98. The initial general-field convention
and Theorem 1.4 were checked in the arXiv copy. The notebook supplies its own
complete finite-field operator proof for the quadratic Boolean setting;
it does not claim a new general flat-extension theorem.

The author-PDF request timed out and the Tilburg copy returned 403; the
arXiv fallback succeeded. No unavailable-paper request was necessary.
sources.json preserves the exact URLs and reading scope. No new third-party
full text is included in this checkpoint.

Initial preparation includes the preceding checkpoint, the renewed push
authorization, the public-history check, and the successful publication.
One initial source read used a wrong local basename, then found the existing
Krajicek.txt; that was an access error, not a mathematical failure.
The source and coding phases were marked; a brief publication-status update
remained in the mathematics phase. No retrospective timing split was invented.

The decisive improvement was mathematical: testing the full permitted query
space closed a candidate route before further rank-two classifications.
The existing task-selection rule already asks for the actual method obligation,
so no additional framework rule was added.
