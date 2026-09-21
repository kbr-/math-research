/* Bit-sliced GF(3) row reduction.  A row of `cols` entries is stored as two bit-planes of W
   64-bit words: plane A holds [v==1], plane B holds [v==2].  Addition (derived from the truth
   table, verified exhaustively by gf3.py):
     sa = (xb&yb) | (xa&~ya&~yb) | (ya&~xa&~xb)
     sb = (xa&ya) | (xb&~ya&~yb) | (yb&~xa&~xb)
   Multiplication by 2 swaps the planes. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static inline void addrow(uint64_t *X, const uint64_t *R, int W, int w0, int neg) {
    uint64_t *xa = X, *xb = X + W;
    const uint64_t *ya = neg ? R + W : R, *yb = neg ? R : R + W;
    for (int j = w0; j < W; j++) {
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

void gf3_set_threads(int n) {
#ifdef _OPENMP
    omp_set_num_threads(n);
#endif
}

/* In-place row echelon form (reduced if full) of a rows x cols matrix with W words per plane.
   Writes pivot columns to piv and returns the rank. */
int gf3_rref(uint64_t *M, int rows, int W, int cols, int full, int *piv) {
    size_t stride = 2 * (size_t)W;
    uint64_t *tmp = malloc(stride * sizeof(uint64_t));
    int r = 0;
    for (int c = 0; c < cols && r < rows; c++) {
        int p = -1;
        for (int i = r; i < rows; i++) if (get(M + i * stride, W, c)) { p = i; break; }
        if (p < 0) continue;
        if (p != r) {
            memcpy(tmp, M + p * stride, stride * 8);
            memcpy(M + p * stride, M + r * stride, stride * 8);
            memcpy(M + r * stride, tmp, stride * 8);
        }
        uint64_t *R = M + r * stride;
        if (get(R, W, c) == 2) {            /* scale by 2: swap planes */
            memcpy(tmp, R, W * 8); memcpy(R, R + W, W * 8); memcpy(R + W, tmp, W * 8);
        }
        int w0 = c >> 6, lo = full ? 0 : r + 1;
        #pragma omp parallel for schedule(dynamic, 32)
        for (int i = lo; i < rows; i++) {
            if (i == r) continue;
            uint64_t *X = M + i * stride;
            int f = get(X, W, c);
            if (f) addrow(X, R, W, w0, f == 1);   /* X - f*R: f=1 adds -R, f=2 adds R */
        }
        piv[r++] = c;
    }
    free(tmp);
    return r;
}
