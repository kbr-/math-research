/* Check of thm:taylor-propagation for two-square product tops tau_b = l_b^2 l'_b^2 (degree 4) on the weak
   monomial algebra over F_3.  Multiplier degree e: Phi_e : A~_e^B -> A~_{e+4}, and the Taylor span
   T_e = sum_b (l_b A~_{e-1} + l'_b A~_{e-1}) e_b (no Koszul pairs for e < 4).  Taylor generation in degree e
   means dim ker Phi_e = sum_b dim(F_b A~_{e-1}).  The check draws B tops on q columns, verifies Taylor
   generation in degrees 0, 1, 2 on those q columns (degree 0: the tops are independent), then embeds the
   same forms into N columns with the extra columns random, and verifies degree-2 Taylor generation there,
   as the theorem predicts.  Exact ranks with FLINT.  Usage: taylor_check M Q N B SEED TRIALS */
#include <flint/nmod_mat.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int m;
static uint64_t sm(uint64_t *x) { uint64_t z = (*x += 0x9e3779b97f4a7c15ULL); z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
static int trit(uint64_t *s) { for (;;) { int v = sm(s) & 3; if (v < 3) return v; } }

/* monomials of degree d on n columns: (mask, digit per column); index = maskpos * m^d + code */
typedef struct { int n, d, count, pw; int *maskpos; int *masks; } deg_t;
static deg_t mkdeg(int n, int d) {
    deg_t g = {n, d, 0, 1, calloc(1 << n, sizeof(int)), malloc(sizeof(int) << n)};
    for (int i = 0; i < d; i++) g.pw *= m;
    int k = 0;
    for (int x = 0; x < (1 << n); x++) if (__builtin_popcount(x) == d) { g.maskpos[x] = k; g.masks[k++] = x; }
    g.count = k * g.pw; return g;
}
static int idx(const deg_t *g, int mask, const int *dig) {   /* dig[c] for c in mask */
    int code = 0, mul = 1;
    for (int c = 0; c < g->n; c++) if (mask >> c & 1) { code += dig[c] * mul; mul *= m; }
    return g->maskpos[mask] * g->pw + code;
}
static void unidx(const deg_t *g, int i, int *mask, int *dig) {
    *mask = g->masks[i / g->pw]; int code = i % g->pw;
    for (int c = 0; c < g->n; c++) if (*mask >> c & 1) { dig[c] = code % m; code /= m; }
}
/* tau as a dense vector on degree-4 monomials */
static void top(const deg_t *g4, const int *l, const int *lp, int *tau) {
    static const int sp[6][4] = {{0,1,2,3},{0,2,1,3},{0,3,1,2},{2,3,0,1},{1,3,0,2},{1,2,0,3}};
    int dig[32];
    for (int i = 0; i < g4->count; i++) {
        int mask; unidx(g4, i, &mask, dig);
        int cols[4], k = 0; for (int c = 0; c < g4->n; c++) if (mask >> c & 1) cols[k++] = c;
        int a[4], b[4]; for (int j = 0; j < 4; j++) { a[j] = l[cols[j] * m + dig[cols[j]]]; b[j] = lp[cols[j] * m + dig[cols[j]]]; }
        int s = 0; for (int q = 0; q < 6; q++) s += a[sp[q][0]] * a[sp[q][1]] * b[sp[q][2]] * b[sp[q][3]];
        tau[i] = s % 3;
    }
}
/* rank of Phi_e for B tops on n columns; tops given by their forms (n*m entries each) */
static long rank_phi(int n, int e, int B, int *L, int *LP) {
    deg_t ge = mkdeg(n, e), g4 = mkdeg(n, 4), gt = mkdeg(n, e + 4);
    nmod_mat_t M; nmod_mat_init(M, (long)B * ge.count, gt.count, 3);
    int *tau = malloc(sizeof(int) * g4.count), dx[32], dt[32], dd[32];
    for (int b = 0; b < B; b++) {
        top(&g4, L + b * n * m, LP + b * n * m, tau);
        for (int x = 0; x < ge.count; x++) {
            int mx; unidx(&ge, x, &mx, dx);
            for (int t = 0; t < g4.count; t++) if (tau[t]) {
                int mt; unidx(&g4, t, &mt, dt);
                if (mx & mt) continue;
                for (int c = 0; c < n; c++) dd[c] = (mx >> c & 1) ? dx[c] : dt[c];
                int j = idx(&gt, mx | mt, dd);
                long row = (long)b * ge.count + x;
                nmod_mat_entry(M, row, j) = (nmod_mat_entry(M, row, j) + tau[t]) % 3;
            }
        }
    }
    long r = nmod_mat_rank(M); nmod_mat_clear(M); free(tau);
    free(ge.maskpos); free(ge.masks); free(g4.maskpos); free(g4.masks); free(gt.maskpos); free(gt.masks);
    return r;
}
/* dim of F A~_{e-1} = rank of (x, y) -> l x + l' y on A~_{e-1}^2 into A~_e (e >= 1) */
static long rank_frob(int n, int e, const int *l, const int *lp) {
    if (e == 0) return 0;
    deg_t gx = mkdeg(n, e - 1), gy = mkdeg(n, e);
    nmod_mat_t M; nmod_mat_init(M, 2L * gx.count, gy.count, 3);
    int dx[32], dd[32];
    for (int f = 0; f < 2; f++) for (int x = 0; x < gx.count; x++) {
        int mx; unidx(&gx, x, &mx, dx);
        for (int c = 0; c < n; c++) if (!(mx >> c & 1)) for (int i = 0; i < m; i++) {
            int v = (f ? lp : l)[c * m + i]; if (!v) continue;
            memcpy(dd, dx, sizeof(dd)); dd[c] = i;
            int j = idx(&gy, mx | (1 << c), dd);
            nmod_mat_entry(M, (long)f * gx.count + x, j) = (nmod_mat_entry(M, (long)f * gx.count + x, j) + v) % 3;
        }
    }
    long r = nmod_mat_rank(M); nmod_mat_clear(M);
    free(gx.maskpos); free(gx.masks); free(gy.maskpos); free(gy.masks);
    return r;
}
static int taylor(int n, int e, int B, int *L, int *LP, long *excess) {
    deg_t ge = mkdeg(n, e); long dimE = ge.count; free(ge.maskpos); free(ge.masks);
    long frob = 0; for (int b = 0; b < B; b++) frob += rank_frob(n, e, L + b * n * m, LP + b * n * m);
    long ker = (long)B * dimE - rank_phi(n, e, B, L, LP);
    *excess = ker - frob; return *excess == 0;
}
int main(int argc, char **argv) {
    if (argc != 7) { fprintf(stderr, "usage: taylor_check M Q N B SEED TRIALS\n"); return 1; }
    m = atoi(argv[1]); int q = atoi(argv[2]), n = atoi(argv[3]), B = atoi(argv[4]), trials = atoi(argv[6]);
    uint64_t s = strtoull(argv[5], 0, 10);
    int *L = malloc(sizeof(int) * B * n * m), *LP = malloc(sizeof(int) * B * n * m);
    int *Lq = malloc(sizeof(int) * B * q * m), *LPq = malloc(sizeof(int) * B * q * m);
    int hyp = 0, concl = 0;
    for (int t = 0; t < trials; t++) {
        for (int i = 0; i < B * n * m; i++) { L[i] = trit(&s); LP[i] = trit(&s); }
        for (int b = 0; b < B; b++) for (int y = 0; y < q * m; y++) { Lq[b * q * m + y] = L[b * n * m + y]; LPq[b * q * m + y] = LP[b * n * m + y]; }
        long ex0, ex1, ex2, exN;
        int h0 = taylor(q, 0, B, Lq, LPq, &ex0), h1 = taylor(q, 1, B, Lq, LPq, &ex1), h2 = taylor(q, 2, B, Lq, LPq, &ex2);
        int hq = h0 && h1 && h2;
        taylor(n, 2, B, L, LP, &exN);
        printf("trial %d: block q=%d excess (deg0, deg1, deg2) = (%ld, %ld, %ld); board N=%d degree-2 excess %ld\n", t, q, ex0, ex1, ex2, n, exN);
        fflush(stdout);
        if (hq) { hyp++; if (exN == 0) concl++; }
    }
    printf("hypothesis held in %d trials; conclusion held in %d of them\n", hyp, concl);
    return (hyp == concl) ? 0 : 3;
}
