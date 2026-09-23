/* Degree-D PC closure over GF(3), entirely in C.  State: a persistent fully reduced basis (bit-sliced rows, plane A =
   [v==1], plane B = [v==2]) with pivots at first nonzero columns; columns are ordered by decreasing degree, so a
   row's pivot degree is its degree.  gf3_close repeatedly takes the unprocessed basis rows of degree <= D-1,
   multiplies each by every variable through the table mul[y*cols + c] (target column, or -1 for zero), inserts the
   products, and marks the rows processed, until no unprocessed low row remains.  A processed row later changed by
   reduction differs from its processed version by combinations of later rows, which are processed in turn, so the
   span of all products is closed (downward induction on insertion order). */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
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
int gf3_insert(uint64_t *basis, int *rank, int *piv, uint64_t *rows, int nrows, int W) {
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
/* products of basis rows idx[0..n-1] by all v variables into out (n*v rows, zeroed by caller) */
static void products(const uint64_t *basis, const int *idx, int n, int W, int cols, int v, const int32_t *mul,
                     uint64_t *out) {
    size_t st = 2 * (size_t)W;
    #pragma omp parallel
    {
        uint8_t *acc = calloc(cols, 1); int *touched = malloc(sizeof(int) * cols);
        #pragma omp for schedule(dynamic, 1)
        for (int i = 0; i < n; i++) {
            const uint64_t *R = basis + (size_t)idx[i] * st;
            for (int y = 0; y < v; y++) {
                int nt = 0; const int32_t *my = mul + (size_t)y * cols;
                for (int j = 0; j < W; j++) {
                    uint64_t m = R[j] | R[W + j];
                    while (m) {
                        int b = __builtin_ctzll(m); m &= m - 1; int c = j * 64 + b;
                        int t = my[c]; if (t < 0) continue;
                        int val = (R[j] >> b & 1) ? 1 : 2;
                        if (!acc[t]) touched[nt++] = t;              /* acc: 0 untouched, 1 or 2 value, 3 touched zero */
                        int cur = acc[t] == 3 ? 0 : acc[t], nv = (cur + val) % 3;
                        acc[t] = (uint8_t)(nv ? nv : 3);
                    }
                }
                uint64_t *P = out + ((size_t)i * v + y) * st;
                for (int q = 0; q < nt; q++) {
                    int t = touched[q], val = acc[t] == 3 ? 0 : acc[t]; acc[t] = 0;
                    if (val == 1) P[t >> 6] |= 1ULL << (t & 63); else if (val == 2) P[W + (t >> 6)] |= 1ULL << (t & 63);
                }
            }
        }
        free(acc); free(touched);
    }
}
/* close the basis: processed[k] marks rows already multiplied; returns the new rank */
int gf3_close(uint64_t *basis, int *rank, int *piv, uint8_t *processed, const int8_t *deg, int D,
              const int32_t *mul, int v, int W, int cols, int batch, int threads) {
#ifdef _OPENMP
    omp_set_num_threads(threads);
#endif
    size_t st = 2 * (size_t)W;
    int *idx = malloc(sizeof(int) * (size_t)batch);
    uint64_t *out = malloc((size_t)batch * v * st * 8);
    for (;;) {
        int n = 0;
        for (int k = 0; k < *rank && n < batch; k++) if (!processed[k] && deg[piv[k]] <= D - 1) idx[n++] = k;
        if (!n) break;
        memset(out, 0, (size_t)n * v * st * 8);
        products(basis, idx, n, W, cols, v, mul, out);
        for (int i = 0; i < n; i++) processed[idx[i]] = 1;
        gf3_insert(basis, rank, piv, out, n * v, W);
    }
    free(idx); free(out);
    return *rank;
}
