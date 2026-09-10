# Factor-packed extension lifting: exact checks

The construction groups the factors `(1 - alpha^{-1} f_j)`, for each
nonzero field value alpha and each polynomial-basis element f_j, into h
ordered buckets. For a bucket, telescoping the product expresses its
complement as a polynomial linear combination of the f_j. Those
coefficients are substituted for the new extension variables.

Across all h buckets the product is exactly `product_j(1-f_j^(p-1))`.
It annihilates every companion in the linear span of the f_j modulo the
old field equations. Different blocks have fresh extension variables and
can be substituted simultaneously. There is no multiplication of weights
across blocks.

For rank r, maximum basis degree delta and accuracy h, each coefficient
has degree at most `delta * max(0, ceil((p-1)*r/h)-1)`. For a Boolean-valued
basis the same construction uses only the nonzero value 1, so `(p-1)*r`
is replaced by r.

Run:

    python checks.py --workers 6

The implementation uses NumPy int64 arithmetic modulo p, vectorized
operations over complete finite grids, and process-parallel independent
cases. It includes exact tensor-product interpolation (not floating-point
rank or interpolation) to check the reduced degrees of the substituted
polynomials.

The 76 cases over F_2, F_3, F_5, F_7 include nonlinear inputs,
linearly dependent extra companions, Boolean-valued bases, empty buckets,
and 36 independent-input controls attaining the sharp degree bound.
There are 125,706 companion/assignment checks and 1,824 multiplier-moment
checks with normalized, arbitrary finite-field signed functionals.

Scope: the checks verify the explicit substitution identities and their
degree bounds. They do not prove a general PHP lower bound, assert that
all extension blocks have low rank, or test the separate hybrid repair
algorithm. The lifting theorem and the hybrid degree estimate require
the algebraic arguments supplied in the accompanying response.
