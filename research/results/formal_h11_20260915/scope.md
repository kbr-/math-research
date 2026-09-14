# H11 assignment and statement map

Assignment: execute Spin-formalize restricted to H11 of
formalization/BIT_PHP_FORMALIZATION_ROUTE.md. Other workers own H01–H10;
H12/H13 and the R route remain outside this assignment.

Source: whitepaper sections/08-topology.tex, theorem thm:chessboard proof,
and notebook whitepaper-chessboard-homology-expansion. This extracts the
arithmetic component of the classical star-cover proof as one new indexed
claim, third-party:chessboard-parameter-arithmetic; it does not prove homology.

Proposed API: chessboardNu a b = min a (min b ((a+b+1)/3)), symmetry,
bounds, positivity and zero/one board boundaries, ordered bound nu<=b-1,
intersection inequality nu(a,b)+1<=nu(a-1,b-t)+t for 2<=a<=b and 2<=t<b,
and min(a-1,b-t)<min(a,b) in either transpose order.
Integer-degree corollaries express the required nu-t-1 bound without Nat
truncation. Generic k-cell degree conversion handles degrees below -1 as
vacuous and nu=0/1 explicitly. Narrow-range specialization nu(s,N)=s is
arithmetic support for eventual H13, not a formalization of H13/H.

Dependencies: Lean's checked natural/integer arithmetic and omega tactic;
no topology, chain infrastructure, external theorem, axiom, or assumption of H.
The generic arithmetic helpers stay in this claim file.

Pre-proof boundary review: t=b gives an empty-face-only intersection, so
induction on nonempty boards uses t<b. For t>nu the integer required degree
is below -1 and vacuous; Nat (nu-t)+1 would incorrectly demand one.
The additive inequality stays valid without this truncation error. A board
with zero side has nu=0, and a one-row positive board has nu=1.

Initial rule/source reading preceded timing start; subsequent reading and
work use formal_h11_20260915. No computations preceded instrumentation.
