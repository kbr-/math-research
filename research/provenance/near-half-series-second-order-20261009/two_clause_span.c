/* Static span of random parity two-clause systems over F_2, to test the product series beyond
first order.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-09-series-block-review): m rows,
row i the product f_i of two distinct nonzero random affine forms on n variables (a clause forbidding
one pair of values of two forms).  The degree-D part of the row's ideal is f_i * B_{<=D-2}, so
K_D = span{ x_T f_i : |T| <= D-2 }, multilinear.  For each D the program reports dim B_{<=D}, the rank
of K_D, whether 1 lies in K_D, and the cumulative coefficient sum of the product series
(1+z)^(n-2m) (1+2z)^m through degree D, which the model predicts to equal dim B_{<=D} - rank K_D
while its coefficients are positive.  Prediction tested: at (n,m) = (30,75) and (28,70) the series'
coefficient at degree 4 is positive (second-order term included) while the first-order count is
negative, so the model says 1 is not in K_4 and the first-order count says it is.

Arguments, in groups of five: n m seed Dmin Dmax.  Exact arithmetic over F_2.  Satisfiability is not
checked: if 1 is in K_D the system is unsatisfiable, and if not, nothing is claimed about it.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint64_t rng;
static unsigned rnd(void){ rng = rng*6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(rng>>33); }

int main(int argc, char **argv){
    for (int g = 1; g + 4 < argc; g += 5){
        int n = atoi(argv[g]), m = atoi(argv[g+1]); long seed = atol(argv[g+2]);
        int Dmin = atoi(argv[g+3]), Dmax = atoi(argv[g+4]);
        if (n > 32 || m > 256 || Dmax > 5){ fprintf(stderr, "parameters out of range\n"); return 2; }
        rng = 0x9E3779B97F4A7C15ULL ^ (uint64_t)(seed*1000003L + n*131 + m);
        for (int i = 0; i < 8; i++) rnd();
        /* affine forms: mask over variables (bits 0..n-1) and a constant bit n */
        static uint64_t A[256], B[256];
        uint64_t full = (n == 64) ? ~0ULL : ((1ULL<<n) - 1);
        for (int i = 0; i < m; i++){
            do { A[i] = (((uint64_t)rnd()<<32) | rnd()) & full; } while (!A[i]);
            do { B[i] = (((uint64_t)rnd()<<32) | rnd()) & full; } while (!B[i] || B[i] == A[i]);
            A[i] |= (uint64_t)(rnd()&1)<<n; B[i] |= (uint64_t)(rnd()&1)<<n;
        }
        printf("{\"n\":%d,\"m\":%d,\"seed\":%ld,\"by_degree\":[", n, m, seed);
        for (int D = Dmin; D <= Dmax; D++){
            /* index monomials of degree <= D by enumeration; map via sorted table of masks */
            long N = 0; double binom[8] = {1,0,0,0,0,0,0,0};
            for (int d = 1; d <= D; d++) binom[d] = binom[d-1]*(n-d+1)/d;
            for (int d = 0; d <= D; d++) N += (long)(binom[d] + 0.5);
            uint32_t *mono = malloc(4*N); long c = 0;
            /* enumerate masks in increasing order of value among weight <= D: generate by degree then sort */
            for (int d = 0; d <= D; d++){
                if (d == 0){ mono[c++] = 0; continue; }
                uint32_t x = (1U<<d) - 1;
                for (;;){ mono[c++] = x; if (x >= (((1ULL<<d)-1) << (n-d))) break; uint32_t t = x | (x-1); x = (t+1) | (((~t & -~t) - 1) >> (__builtin_ctz(x) + 1)); }
            }
            /* sort masks for binary search */
            int cmp(const void *p, const void *q){ uint32_t a = *(const uint32_t*)p, b = *(const uint32_t*)q; return a < b ? -1 : a > b; }
            qsort(mono, N, 4, cmp);
            long NW = (N+63)/64;
            uint64_t **basis = calloc(N, sizeof(uint64_t*)); long rank = 0, gens = 0;
            uint64_t *vec = malloc(8*NW);
            /* multipliers: monomials of degree <= D-2, taken from the same table */
            for (int i = 0; i < m; i++){
                /* f = (a0 + sum a_j x_j)(b0 + sum b_j x_j), multilinear: list of monomial masks with coefficient 1 */
                int na = 0, nb = 0; uint32_t ta[40], tb[40]; int ca = (A[i]>>n)&1, cb = (B[i]>>n)&1;
                for (int j = 0; j < n; j++){ if ((A[i]>>j)&1) ta[na++] = 1U<<j; if ((B[i]>>j)&1) tb[nb++] = 1U<<j; }
                for (long t = 0; t < N; t++){
                    uint32_t T = mono[t]; if (__builtin_popcount(T) > D-2) continue;
                    memset(vec, 0, 8*NW);
                    #define FLIP(mask) { uint32_t key = (mask); long lo = 0, hi = N-1; while (lo < hi){ long mid = (lo+hi)/2; if (mono[mid] < key) lo = mid+1; else hi = mid; } vec[lo>>6] ^= 1ULL<<(lo&63); }
                    if (ca && cb) FLIP(T);
                    if (cb) for (int u = 0; u < na; u++) FLIP(T | ta[u]);
                    if (ca) for (int w = 0; w < nb; w++) FLIP(T | tb[w]);
                    for (int u = 0; u < na; u++) for (int w = 0; w < nb; w++) FLIP(T | ta[u] | tb[w]);
                    gens++;
                    long p = N-1;
                    for (;;){
                        long w = p>>6; while (w >= 0 && !vec[w]) w--;
                        if (w < 0){ p = -1; break; }
                        p = (w<<6) + 63 - __builtin_clzll(vec[w]);
                        if (!basis[p]) break;
                        uint64_t *b = basis[p]; for (long q = 0; q <= w; q++) vec[q] ^= b[q];
                    }
                    if (p >= 0){ basis[p] = malloc(8*NW); memcpy(basis[p], vec, 8*NW); rank++; }
                }
            }
            memset(vec, 0, 8*NW); vec[0] |= 1ULL;        /* mono[0] = 0 is the constant */
            int one = 0;
            { long p = N-1; for (;;){ long w = p>>6; while (w >= 0 && !vec[w]) w--; if (w < 0){ one = 1; break; } p = (w<<6) + 63 - __builtin_clzll(vec[w]); if (!basis[p]) break; uint64_t *b = basis[p]; for (long q = 0; q <= w; q++) vec[q] ^= b[q]; } }
            /* cumulative coefficients of (1+z)^(n-2m) (1+2z)^m through degree D, in long double */
            long double co[8] = {0}, a[8], bb[8]; int e = n - 2*m;
            for (int j = 0; j <= D; j++){ long double v = 1; for (int q = 0; q < j; q++) v = v*(e-q)/(q+1); a[j] = v; long double u = 1; for (int q = 0; q < j; q++) u = u*(m-q)/(q+1)*2; bb[j] = u; }
            long double cum = 0; for (int j = 0; j <= D; j++){ for (int q = 0; q <= j; q++) co[j] += a[q]*bb[j-q]; cum += co[j]; }
            printf("%s{\"D\":%d,\"dim\":%ld,\"generators\":%ld,\"rank\":%ld,\"quotient\":%ld,\"one_in_span\":%d,\"series_top_coefficient\":%.0Lf,\"series_cumulative\":%.0Lf}", D > Dmin ? "," : "", D, N, gens, rank, N-rank, one, co[D], cum);
            fflush(stdout);
            for (long q = 0; q < N; q++) free(basis[q]);
            free(basis); free(vec); free(mono);
        }
        printf("]}\n"); fflush(stdout);
    }
    return 0;
}
