"""Early-exit degree-D PC closure for weak unary PHP over F_3 (the chunked closure of occupancy_refute.py): columns are in
descending degree, so the constant monomial is the last column and 1 is in the span exactly when that column is a pivot.
Stopping there gives the same refutation verdict, since the full closure contains the current span; non-refuted closures
still run to the fixed point.  Validated against a closure run to the fixed point (n8_D3_early_exit_validation.json)."""
import numpy as np
from scipy import sparse
import gf3
from random_conditioning_fast import rref_stack
def close_early(space, P, W, piv, chunk=40):
    """close() of occupancy_refute.py with an early exit: columns are in descending degree, so the constant monomial is
    the last column and 1 is in the span exactly when that column is a pivot.  Stopping there gives the same refutation
    verdict, since the full closure contains the current span; non-refuted closures still run to the fixed point."""
    cols = space.cols; one = cols - 1
    while True:
        old = P.shape[0]; low = np.nonzero(space.deg[piv] <= space.D - 1)[0]; Pold = P
        for s in range(0, len(low), chunk):
            Lm = sparse.csr_matrix(gf3.unpack(Pold[low[s:s + chunk]], W, cols), dtype=np.int32)
            prod = np.vstack([((Lm @ My).toarray() % 3).astype(np.uint8) for My in space.mult])
            P, W, piv = rref_stack(P, W, cols, prod)
            if one in set(piv.tolist()): return P, W, piv
        if P.shape[0] == old: return P, W, piv
def closure_of_early(space, gens):
    M = np.array([space.vec(g) for g in gens], dtype=np.uint8)
    P, W, piv = gf3.rref(M, parallel=True)
    if space.cols - 1 in set(piv.tolist()): return P, W, piv
    return close_early(space, P, W, piv)
