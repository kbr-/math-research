/* Number of solutions of the random parity-clause systems of clause_regularity.c.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-10-index-span): for rows
f_i = prod_{t<k} (l_it + c_it), i < m, generated exactly as in
research/provenance/near-half-regularity-test-20261009/clause_regularity.c (same generator, same seed
mixing, forms of a row not in the span of the earlier ones), the number of points x in F_2^n with
f_i(x) = 0 for all i.  This is the codimension of the full ideal's part of degree <= D in B_{<=D} once D is
large, to be compared with dim B_{<=D}/K_D recorded in series.jsonl at the product index.
Arguments in groups of four: n m k seed (n <= 32, k <= 4).  Output: one JSON line per system.
*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static uint64_t rng;
static unsigned rnd(void){ rng = rng*6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(rng>>33); }

int main(int argc, char **argv){
    for (int g = 1; g + 3 < argc; g += 4){
        int n = atoi(argv[g]), m = atoi(argv[g+1]), k = atoi(argv[g+2]); long seed = atol(argv[g+3]);
        if (n > 32 || n < 2 || k < 1 || k > 4 || m > 1024 || seed < 0){ fprintf(stderr, "parameters out of range\n"); return 2; }
        uint32_t full = n == 32 ? 0xFFFFFFFFu : ((1u<<n) - 1);
        uint32_t (*form)[4] = malloc(sizeof(uint32_t[4])*m); int (*cst)[4] = malloc(sizeof(int[4])*m);
        rng = 0x9E3779B97F4A7C15ULL ^ (uint64_t)(seed*1000003L + n*131 + m*7 + k);
        for (int i = 0; i < 8; i++) rnd();
        for (int i = 0; i < m; i++){
            for (int t = 0; t < k; t++){
                for (;;){
                    uint32_t a = (uint32_t)(((uint64_t)rnd()<<16) ^ rnd()) & full; int ok = a != 0;
                    for (int s = 1; ok && s < (1<<t); s++){ uint32_t c = 0; for (int u = 0; u < t; u++) if ((s>>u)&1) c ^= form[i][u]; if (c == a) ok = 0; }
                    if (ok){ form[i][t] = a; break; }
                }
                cst[i][t] = rnd() & 1;
            }
        }
        long count = 0; uint64_t N = 1ULL << n;
        #pragma omp parallel for reduction(+:count) schedule(static)
        for (uint64_t x = 0; x < N; x++){
            int sol = 1;
            for (int i = 0; i < m && sol; i++){
                int v = 1;                       /* f_i(x) = prod (l(x) + c) */
                for (int t = 0; t < k && v; t++) v = (__builtin_parity(form[i][t] & (uint32_t)x) ^ cst[i][t]);
                if (v) sol = 0;
            }
            count += sol;
        }
        printf("{\"n\":%d,\"m\":%d,\"k\":%d,\"seed\":%ld,\"solutions\":%ld}\n", n, m, k, seed, count); fflush(stdout);
        free(form); free(cst);
    }
    return 0;
}
