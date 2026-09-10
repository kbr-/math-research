# Base-aware lifting checks

Run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python check.py`.

The script checks blocks with inputs g=(I+A)u, where A has affine entries and
A^2=0 formally. The source tuple u is either a complete row or a subset (here,
all entries) of one column. The substitutions are r_1 = 1^T(I-A), r_v=0 for
v>1. Every substituted r is maintained as an explicit affine polynomial in the
original variables, including through four levels.

Checks use exact modular NumPy arithmetic. Cases are process-parallel, with
BLAS thread counts fixed to one to avoid oversubscription. The finite test
boards have two rows and five or seven columns. They are deliberately
satisfiable, and most cases include assignments with multiple ones in a row
but row sum equal to one modulo p. Thus row-exclusivity is not assumed.

The script verifies the matrix and companion identities on every
column-exclusive Boolean assignment; vanishing on the row-normalized
assignments; new field equations; and mixed old/new multiplier moments with
normalized finite-field weights. These checks supplement, but do not replace,
the symbolic bounded-certificate proof. They neither construct designs for
unsatisfiable PHP boards nor establish a general ENS/Frege lower bound.
