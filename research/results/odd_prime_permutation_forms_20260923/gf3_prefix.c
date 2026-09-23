/* Prefix ranks over GF(3): rows arrive in blocks; after each block, report the rank of all rows so far.
   Bit-sliced rows as in the recorded gf3.c (plane A = [v==1], plane B = [v==2]).  The basis is kept fully
   reduced (each basis row is zero at every other basis row's pivot, pivot entry 1), so a new row is reduced
   by one pass over the basis, in parallel over the rows of a block.  One elimination gives every prefix rank. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static inline void addrow(uint64_t *X, const uint64_t *R, int W, int neg) {
    uint64_t *xa = X, *xb = X + W;
    const uint64_t *ya = neg ? R + W : R, *yb = neg ? R : R + W;
    for (int j = 0; j < W; j++) {
        uint64_t a = xa[j], b = xb[j], c = ya[j], d = yb[j];
        uint64_t nc = ~(c | d), nx = ~(a | b);
        xa[j] = (b & d) | (a & nc) | (c & nx);
        xb[j] = (a & c) | (b & nc) | (d & nx);
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
/* M: rows x (2W) words, rows grouped into nblocks blocks ending at block_end[b] (exclusive).
   basis: caller-provided buffer of at least min(rows, cols) rows.  ranks[b] receives the rank after block b. */
int gf3_prefix_ranks(uint64_t *M, int rows, int W, int cols, const int *block_end, int nblocks,
                     uint64_t *basis, int *piv, int *ranks, int threads) {
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    size_t st = 2 * (size_t)W; int r = 0, s = 0;
    for (int b = 0; b < nblocks; b++) {
        int e = block_end[b];
        #pragma omp parallel for schedule(dynamic, 4)
        for (int i = s; i < e; i++) {                 /* reduce each new row against the current basis */
            uint64_t *X = M + i * st;
            for (int k = 0; k < r; k++) { int f = get(X, W, piv[k]); if (f) addrow(X, basis + k * st, W, f == 1); }
        }
        for (int i = s; i < e; i++) {                 /* absorb the block's rows one by one */
            uint64_t *X = M + i * st;
            int c = first_nonzero(X, W);
            if (c < 0 || r >= cols) continue;
            if (get(X, W, c) == 2) { for (int j = 0; j < W; j++) { uint64_t t = X[j]; X[j] = X[W + j]; X[W + j] = t; } }
            uint64_t *R = basis + (size_t)r * st; memcpy(R, X, st * 8);
            #pragma omp parallel for schedule(dynamic, 64)
            for (int k = 0; k < r; k++) { uint64_t *Y = basis + k * st; int f = get(Y, W, c); if (f) addrow(Y, R, W, f == 1); }
            #pragma omp parallel for schedule(dynamic, 4)
            for (int j = i + 1; j < e; j++) { uint64_t *Y = M + j * st; int f = get(Y, W, c); if (f) addrow(Y, R, W, f == 1); }
            piv[r++] = c;
        }
        ranks[b] = r; s = e;
    }
    return r;
}
