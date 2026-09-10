AFFINE CORE/RESIDUAL DECOMPOSITION: EXACT OPTIMIZATION AND AN OBSTRUCTION

Scope
-----
This package checks finite-field linear algebra and optimization of the degree
BOUND supplied by the core/residual batching criterion in the conversation.
It does not compute a PHP design, find an ENS refutation, prove the published
PC lower bound, or claim a lower bound on every possible elimination method.

Exact ordering
--------------
For subspaces V_a and S nonempty, write I(S)=intersection_{a in S} V_a.
For a fixed order the maximal nested cores are its suffix intersections.
The residual radius R*(S) is minimized by ordering spaces by nondecreasing
dimension. Equivalently:
  R*(S) = max_{empty != A subset S} [min_{a in A} dim(V_a)-dim(I(A))].
This follows from the earliest element of A in any order, and greedy peeling
of a currently smallest-dimensional space.

Exact degree bound within the specified rule
-------------------------------------------
Assume all inputs are nonzero affine forms and no input span contains a
nonzero constant modulo the supplied old affine consequences. Fix prime p,
common accuracy h, and T(r)=max(1,ceil((p-1)*r/h)-1).
The best batch bound from this rule is
  C_S(d) = min(T(R*(S))*d+(p-1), T(max_{a in S}dim(V_a))*d).
The two options are maximal cores versus all cores zero. Any nonzero core
has generator degree one. For an entire one-level family the exact optimum
of these certified bounds is the subset dynamic program
  B(empty)=D,
  B(S)=min_{empty != A subset S} C_A(B(S minus A)).
This optimization is exponential in the number of blocks; it is not asserted
to be a polynomial-time decomposition algorithm for large proof outputs.

Explicit obstruction
--------------------
Let d=ceil(log_p n), q=floor((n^2-1)/(2d)), r=qd. Let K=F_(p^d), and choose
n distinct alpha in K. In K^q direct_sum K^q take
  V_alpha={(u,alpha*u):u in K^q}.
Every space has F_p-dimension r, and different spaces have intersection zero.
Embed the 2r coordinates among the PHP variables in all but the last column.
These coordinates, together with 1, are linearly independent modulo the
row equations rho_i-1. A basis of each V_alpha is a permissible linear ENS
input tuple. All blocks are in one level and all companions are included.
For any subset with two or more blocks, R*=r. The optimum of the specified
bound over all orders, cores, partitions and batch orders is exactly
  min(D+(p-1)*n, T(r)*D).
For fixed p, h=Theta(log n), and 2h+1 <= D=polylog(n), this is
D+(p-1)*n for sufficiently large n, and exceeds n/2.
This is an obstruction to the current static decomposition criterion, not
to arbitrary refutation-sensitive rewriting or the Frege lower-bound goal.

Additional theoretical claim (not computationally checked here)
---------------------------------------------------------------
Using the published PC degree lower bound for PHP as input, one obtains
C_b(F_n) intersect affine = span{rho_i-1} for
1 <= b <= floor((n-2)/2).
Proof sketch: restrict any derived affine f to two matchings swapping the
images of two pigeons while leaving the same residual PHP. A nonzero constant
difference would refute that residual PHP. All coefficient rectangles thus
vanish, so coefficients have the form u_i+v_j. Unequal v_j would, by permuting
columns and restricting one matched pigeon, derive every remaining column's
empty indicator. Summing these with the residual row equations yields -1.
Hence all v_j agree, and f is a row-equation combination plus a constant;
the constant must be zero by the base lower bound.

Tests
-----
The script uses NumPy-vectorized exact modular elimination, batched field
multiplication matrices, and four process workers. It checks:
* every field-multiplication difference in seven graph-space families;
* explicit quotient ranks modulo the PHP row equations in small families;
* greedy optimality against all orders of all nonempty subfamilies for nine
  six-space examples over F_2,F_3,F_5;
* exact subset-DP optima for seven spread subfamilies of at most eight blocks.
The large-family optimality formula is proved algebraically, not by exhaustive
enumeration of all partitions of 256 blocks.

Run
---
python check_decomposition.py
Requires NumPy. The run in this conversation had 16 passing cases, no retries.
Results and measured suite runtime are in results.json. Worker elapsed times
are overlapping and must NOT be added to get wall-clock time.
