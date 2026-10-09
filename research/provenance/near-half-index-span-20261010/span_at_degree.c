/* Codimension of the Boolean static span of a random parity-clause system at one degree.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-10-degree-six): for rows
f_i = prod_{t<k} (l_it + c_it), i < m, generated exactly as in
research/provenance/near-half-regularity-test-20261009/clause_regularity.c, and a degree D:
  codim = dim B_{<=D}/K_D,  B = F_2[x]/(x_i^2 - x_i),  K_D = span{ x_T f_i : |T| <= D-k },
and whether 1 lies in K_D.  Only this degree is computed; the systems of one call run in parallel.
Validation: at D = 5 for (18, 99, 3, seeds 1-3) the recorded values are 639, 638, 638 with 1 outside.
Arguments: D, then groups of four: n m k seed.  n <= 32, k <= 4.  Exact arithmetic over F_2.
Output: one JSON line per system, with the elimination time in seconds.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

typedef struct { uint64_t s; } rng_t;
static unsigned rnd(rng_t *r){ r->s = r->s*6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(r->s>>33); }
static int cmp32(const void *p, const void *q){ uint32_t a = *(const uint32_t*)p, b = *(const uint32_t*)q; return a < b ? -1 : a > b; }
typedef struct { uint32_t *m; long len, cap; } poly;
static void push(poly *p, uint32_t x){ if (p->len == p->cap){ p->cap = p->cap ? 2*p->cap : 64; p->m = realloc(p->m, 4*p->cap); } p->m[p->len++] = x; }
static void normalize(poly *p){
    qsort(p->m, p->len, 4, cmp32); long w = 0;
    for (long i = 0; i < p->len; ){ long j = i; while (j < p->len && p->m[j] == p->m[i]) j++; if ((j-i)&1) p->m[w++] = p->m[i]; i = j; }
    p->len = w;
}
static void mul(const poly *p, uint32_t form, int c, poly *q){      /* q = p (form + c) in B */
    q->len = 0;
    for (long i = 0; i < p->len; i++){ uint32_t M = p->m[i]; if (c) push(q, M); for (uint32_t f = form; f; f &= f-1) push(q, M | (f & -f)); }
    normalize(q);
}
static long binom(int n, int r){ if (r < 0 || r > n) return 0; long v = 1; for (int i = 1; i <= r; i++) v = v*(n-r+i)/i; return v; }
static uint32_t gosper(uint32_t x){ uint32_t t = x | (x-1); return (t+1) | (((~t & -~t) - 1) >> (__builtin_ctz(x) + 1)); }
static long lookup(const uint32_t *tab, long N, uint32_t key){ long lo = 0, hi = N-1; while (lo < hi){ long mid = (lo+hi)/2; if (tab[mid] < key) lo = mid+1; else hi = mid; } return lo; }

int main(int argc, char **argv){
    if (argc < 6){ fprintf(stderr, "usage: D then n m k seed ...\n"); return 2; }
    int D = atoi(argv[1]), G = (argc - 2)/4;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int g = 0; g < G; g++){
        int n = atoi(argv[2+4*g]), m = atoi(argv[3+4*g]), k = atoi(argv[4+4*g]); long seed = atol(argv[5+4*g]);
        if (n > 32 || n < 2 || k < 1 || k > 4 || m > 1024 || seed < 0 || D < k || D > 8){ fprintf(stderr, "parameters out of range\n"); continue; }
        double t0 = omp_get_wtime();
        uint32_t full = n == 32 ? 0xFFFFFFFFu : ((1u<<n) - 1);
        uint32_t (*form)[4] = malloc(sizeof(uint32_t[4])*m); int (*cst)[4] = malloc(sizeof(int[4])*m);
        rng_t R; R.s = 0x9E3779B97F4A7C15ULL ^ (uint64_t)(seed*1000003L + n*131 + m*7 + k);
        for (int i = 0; i < 8; i++) rnd(&R);
        for (int i = 0; i < m; i++) for (int t = 0; t < k; t++){
            for (;;){
                uint32_t a = (uint32_t)(((uint64_t)rnd(&R)<<16) ^ rnd(&R)) & full; int ok = a != 0;
                for (int s = 1; ok && s < (1<<t); s++){ uint32_t c = 0; for (int u = 0; u < t; u++) if ((s>>u)&1) c ^= form[i][u]; if (c == a) ok = 0; }
                if (ok){ form[i][t] = a; break; }
            }
            cst[i][t] = rnd(&R) & 1;
        }
        poly *row = calloc(m, sizeof(poly)), tmp = {0}, tmp2 = {0};
        for (int i = 0; i < m; i++){
            tmp.len = 0; push(&tmp, 0);
            for (int t = 0; t < k; t++){ mul(&tmp, form[i][t], cst[i][t], &tmp2); poly sw = tmp; tmp = tmp2; tmp2 = sw; }
            for (long q = 0; q < tmp.len; q++) push(&row[i], tmp.m[q]);
        }
        long N = 0; for (int e = 0; e <= D; e++) N += binom(n, e);
        uint32_t *bt = malloc(4*N); long c = 0;
        for (int e = 0; e <= D; e++){ if (e == 0){ bt[c++] = 0; continue; } long Ne = binom(n, e); uint32_t x = (1u<<e) - 1; for (long q = 0; q < Ne; q++){ bt[c++] = x; if (q + 1 < Ne) x = gosper(x); } }
        qsort(bt, N, 4, cmp32);
        long NW = (N+63)/64, rank = 0; uint64_t **basis = calloc(N, sizeof(uint64_t*)), *vec = malloc(8*NW);
        for (int e = 0; e + k <= D && rank < N; e++){
            long NT = binom(n, e); uint32_t T = e == 0 ? 0 : (1u<<e) - 1;
            for (long cc = 0; cc < NT && rank < N; cc++){
                for (int i = 0; i < m; i++){
                    memset(vec, 0, 8*NW);
                    for (long q = 0; q < row[i].len; q++){ long col = lookup(bt, N, row[i].m[q] | T); vec[col>>6] ^= 1ULL<<(col&63); }
                    long w = NW - 1;
                    for (;;){
                        while (w >= 0 && !vec[w]) w--;
                        if (w < 0) break;
                        long p = (w<<6) + 63 - __builtin_clzll(vec[w]);
                        if (!basis[p]){ basis[p] = malloc(8*(w+1)); memcpy(basis[p], vec, 8*(w+1)); rank++; break; }
                        uint64_t *b = basis[p]; for (long q = 0; q <= w; q++) vec[q] ^= b[q];
                    }
                }
                if (cc + 1 < NT) T = gosper(T);
            }
        }
        memset(vec, 0, 8*NW); vec[0] = 1ULL; int one = 0;      /* bt[0] = 0 is the constant monomial */
        { long w = 0; for (;;){ while (w >= 0 && !vec[w]) w--; if (w < 0){ one = 1; break; } long p = (w<<6) + 63 - __builtin_clzll(vec[w]); if (!basis[p]) break; uint64_t *b = basis[p]; for (long q = 0; q <= w; q++) vec[q] ^= b[q]; } }
        #pragma omp critical
        { printf("{\"n\":%d,\"m\":%d,\"k\":%d,\"seed\":%ld,\"D\":%d,\"columns\":%ld,\"rank\":%ld,\"codim\":%ld,\"one\":%d,\"seconds\":%.1f}\n", n, m, k, seed, D, N, rank, N - rank, one, omp_get_wtime() - t0); fflush(stdout); }
        for (long q = 0; q < N; q++) free(basis[q]); free(basis); free(vec); free(bt);
        for (int i = 0; i < m; i++) free(row[i].m); free(row); free(tmp.m); free(tmp2.m); free(form); free(cst);
    }
    return 0;
}
