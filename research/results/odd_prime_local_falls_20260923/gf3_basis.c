/* Persistent fully reduced GF(3) basis with incremental insertion (bit-sliced rows as in the recorded gf3.c:
   plane A = [v==1], plane B = [v==2]).  gf3_insert reduces a batch of rows against the basis (OpenMP over the
   batch), then absorbs the survivors one by one, eliminating each new pivot from the basis and from the rest of
   the batch.  Pivots are first nonzero columns, so with columns ordered by decreasing degree a basis row's pivot
   degree is its degree.  Existing pivots never move.  Returns the number of rows added; their basis indices are
   r_old, ..., r_old + added - 1. */
#include <stdint.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static inline void addrow(uint64_t *X, const uint64_t *R, int W, int neg) {
    uint64_t *xa = X, *xb = X + W; const uint64_t *ya = neg ? R + W : R, *yb = neg ? R : R + W;
    for (int j = 0; j < W; j++) {
        uint64_t a = xa[j], b = xb[j], c = ya[j], d = yb[j], nc = ~(c | d), nx = ~(a | b);
        xa[j] = (b & d) | (a & nc) | (c & nx); xb[j] = (a & c) | (b & nc) | (d & nx);
    }
}
static inline int get(const uint64_t *X, int W, int c) {
    uint64_t m = 1ULL << (c & 63);
    return (X[c >> 6] & m) ? 1 : ((X[W + (c >> 6)] & m) ? 2 : 0);
}
static int first_nonzero(const uint64_t *X, int W) {
    for (int j = 0; j < W; j++) { uint64_t m = X[j] | X[W + j]; if (m) return j * 64 + __builtin_ctzll(m); }
    return -1;
}
int gf3_insert(uint64_t *basis, int *rank, int *piv, uint64_t *rows, int nrows, int W, int threads) {
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    size_t st = 2 * (size_t)W; int r = *rank, r0 = r;
    #pragma omp parallel for schedule(dynamic, 4)
    for (int i = 0; i < nrows; i++) {
        uint64_t *X = rows + i * st;
        for (int k = 0; k < r; k++) { int f = get(X, W, piv[k]); if (f) addrow(X, basis + k * st, W, f == 1); }
    }
    for (int i = 0; i < nrows; i++) {
        uint64_t *X = rows + i * st; int c = first_nonzero(X, W);
        if (c < 0) continue;
        if (get(X, W, c) == 2) for (int j = 0; j < W; j++) { uint64_t t = X[j]; X[j] = X[W + j]; X[W + j] = t; }
        uint64_t *R = basis + (size_t)r * st; memcpy(R, X, st * 8);
        #pragma omp parallel for schedule(dynamic, 64)
        for (int k = 0; k < r; k++) { uint64_t *Y = basis + k * st; int f = get(Y, W, c); if (f) addrow(Y, R, W, f == 1); }
        #pragma omp parallel for schedule(dynamic, 16)
        for (int j = i + 1; j < nrows; j++) { uint64_t *Y = rows + j * st; int f = get(Y, W, c); if (f) addrow(Y, R, W, f == 1); }
        piv[r++] = c;
    }
    *rank = r; return r - r0;
}
