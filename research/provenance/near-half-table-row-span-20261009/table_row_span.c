/* Static row span of random half-table systems over F_2.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-09-table-row-span): v Boolean
variables, m rows; row a has a scope of k variables and an allowed set R_a of exactly 2^(k-1)
assignments, uniformly random.  J_a is the set of multilinear polynomials vanishing on the cylinder
R_a x {0,1}^(v-k), and K_D = sum_a (J_a intersected with degree <= D).  By prop:table-row-span,
dim (J_a, degree <= D) = sum_i (binom(k,i) - b_i(R_a)) N_{v-k}(D-i), b_i the level sizes of R_a, and
K_D lies in the degree-max(k,D) polynomial-calculus closure.  For each D in the given range the
program reports dim B_{<=D}, the sum of the row dimensions (the count), the rank of K_D, and whether
1 lies in K_D.  Prediction tested: K_D is all of B_{<=D} from the least D at which the count reaches
the dimension (rows in general position); the alternative is 1 outside K_D up to about v/2.

Hypotheses asserted: |R_a| = 2^(k-1); the system is unsatisfiable (brute force over 2^v points); the
generated row basis has the dimension given by the formula.
Each output line also lists the rows: the scope and the allowed table as a 0/1 string indexed by the
assignment (bit s of the index is the value of the s-th scope variable).
Arguments, in groups of six: v k m seed Dmin Dmax.   Exact arithmetic over F_2, bitset elimination.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint64_t rng;
static unsigned rnd(void){ rng = rng*6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(rng>>33); }
static double binom(int n, int j){ if (j < 0 || j > n) return 0; double b = 1; for (int i = 0; i < j; i++) b = b*(n-i)/(i+1); return b; }

int main(int argc, char **argv){
    for (int g = 1; g + 5 < argc; g += 6){
        int v = atoi(argv[g]), k = atoi(argv[g+1]), m = atoi(argv[g+2]); long seed = atol(argv[g+3]);
        int Dmin = atoi(argv[g+4]), Dmax = atoi(argv[g+5]);
        if (v > 24 || k > 10 || k > v || m > 64){ fprintf(stderr, "parameters out of range\n"); return 2; }
        rng = 0x9E3779B97F4A7C15ULL ^ (uint64_t)(seed*1000003L + v*131 + k*31 + m);
        for (int i = 0; i < 8; i++) rnd();
        int K = 1<<k, half = K/2;
        static int scope[64][10]; static uint8_t allowed[64][1024];
        for (int a = 0; a < m; a++){
            int used[32] = {0};
            for (int s = 0; s < k; s++){ int x; do x = rnd()%v; while (used[x]); used[x] = 1; scope[a][s] = x; }
            int perm[1024]; for (int i = 0; i < K; i++) perm[i] = i;
            for (int i = K-1; i > 0; i--){ int j = rnd()%(i+1); int t = perm[i]; perm[i] = perm[j]; perm[j] = t; }
            memset(allowed[a], 0, K); for (int i = 0; i < half; i++) allowed[a][perm[i]] = 1;
        }
        /* unsatisfiable? */
        long sat = 0;
        for (long x = 0; x < (1L<<v) && !sat; x++){
            int ok = 1;
            for (int a = 0; a < m && ok; a++){ int idx = 0; for (int s = 0; s < k; s++) idx |= (int)((x>>scope[a][s])&1)<<s; ok = allowed[a][idx]; }
            sat += ok;
        }
        if (sat){ fprintf(stderr, "satisfiable instance, seed %ld\n", seed); return 3; }
        /* local kernels: for each row, elements u + (earlier monomials) vanishing on R, by degree order */
        int order[1024], nord = 0;
        for (int d = 0; d <= k; d++) for (int u = 0; u < K; u++) if (__builtin_popcount(u) == d) order[nord++] = u;
        static uint64_t ker[64][1024][16]; static int kerdeg[64][1024], nker[64]; static long levels[64][12];
        int W = (K+63)/64;
        for (int a = 0; a < m; a++){
            int pts[1024], np = 0; for (int i = 0; i < K; i++) if (allowed[a][i]) pts[np++] = i;
            /* evaluation vectors over points (np bits) with combination tracking (K bits) */
            static uint64_t ev[1024][16], comb[1024][16]; static int pivot[1024]; int nb = 0;
            int PW = (np+63)/64; nker[a] = 0; memset(levels[a], 0, sizeof levels[a]);
            for (int t = 0; t < K; t++){
                int u = order[t]; uint64_t e[16] = {0}, c[16] = {0};
                for (int p = 0; p < np; p++) if ((pts[p] & u) == u) e[p>>6] |= 1ULL<<(p&63);
                c[u>>6] |= 1ULL<<(u&63);
                for (int b = 0; b < nb; b++) if ((e[pivot[b]>>6]>>(pivot[b]&63))&1){ for (int w = 0; w < PW; w++) e[w] ^= ev[b][w]; for (int w = 0; w < W; w++) c[w] ^= comb[b][w]; }
                int pv = -1; for (int p = 0; p < np && pv < 0; p++) if ((e[p>>6]>>(p&63))&1) pv = p;
                if (pv >= 0){ memcpy(ev[nb], e, sizeof e); memcpy(comb[nb], c, sizeof c); pivot[nb++] = pv; levels[a][__builtin_popcount(u)]++; }
                else { memcpy(ker[a][nker[a]], c, sizeof c); kerdeg[a][nker[a]++] = __builtin_popcount(u); }
            }
            if (nb != np){ fprintf(stderr, "rank defect\n"); return 4; }
        }
        printf("{\"v\":%d,\"k\":%d,\"m\":%d,\"seed\":%ld,\"levels_first_row\":[", v, k, m, seed);
        for (int d = 0; d <= k; d++) printf("%s%ld", d?",":"", levels[0][d]);
        printf("],\"rows\":[");
        for (int a = 0; a < m; a++){ printf("%s[[", a?",":""); for (int s = 0; s < k; s++) printf("%s%d", s?",":"", scope[a][s]); printf("],\""); for (int i = 0; i < K; i++) putchar('0'+allowed[a][i]); printf("\"]"); }
        printf("],\"by_degree\":[");
        int *index = malloc(sizeof(int)<<v);
        for (int D = Dmin; D <= Dmax; D++){
            long N = 0; for (long x = 0; x < (1L<<v); x++) index[x] = __builtin_popcountl(x) <= D ? (int)N++ : -1;
            long NW = (N+63)/64; double count = 0;
            for (int a = 0; a < m; a++) for (int i = 0; i <= k && i <= D; i++){ double tail = 0; for (int j = 0; j <= D-i; j++) tail += binom(v-k, j); count += (binom(k,i) - levels[a][i])*tail; }
            uint64_t **basis = calloc(N, sizeof(uint64_t*)); long rank = 0, gens = 0; int full = 0;
            uint64_t *vec = malloc(8*NW);
            for (int a = 0; a < m && !full; a++){
                int rest[32], nr = 0, in[32] = {0}; for (int s = 0; s < k; s++) in[scope[a][s]] = 1;
                for (int x = 0; x < v; x++) if (!in[x]) rest[nr++] = x;
                for (int q = 0; q < nker[a] && !full; q++){
                    int room = D - kerdeg[a][q]; if (room < 0) continue;
                    /* global masks of the kernel element's monomials */
                    long mons[1024]; int nm = 0;
                    for (int u = 0; u < K; u++) if ((ker[a][q][u>>6]>>(u&63))&1){ long gm = 0; for (int s = 0; s < k; s++) if ((u>>s)&1) gm |= 1L<<scope[a][s]; mons[nm++] = gm; }
                    for (long T = 0; T < (1L<<nr) && !full; T++){
                        if (__builtin_popcountl(T) > room) continue;
                        long tm = 0; for (int s = 0; s < nr; s++) if ((T>>s)&1) tm |= 1L<<rest[s];
                        memset(vec, 0, 8*NW);
                        for (int i = 0; i < nm; i++){ int ix = index[mons[i]|tm]; vec[ix>>6] ^= 1ULL<<(ix&63); }
                        gens++;
                        /* reduce: pivots are highest set bits */
                        long p = N-1;
                        for (;;){
                            long w = p>>6; while (w >= 0 && !vec[w]) w--;
                            if (w < 0){ p = -1; break; }
                            p = (w<<6) + 63 - __builtin_clzll(vec[w]);
                            if (!basis[p]) break;
                            uint64_t *b = basis[p]; for (long i = 0; i <= w; i++) vec[i] ^= b[i];
                        }
                        if (p >= 0){ basis[p] = malloc(8*NW); memcpy(basis[p], vec, 8*NW); rank++; if (rank == N) full = 1; }
                    }
                }
            }
            /* is 1 in the span?  reduce the vector of the constant monomial (index of mask 0) */
            memset(vec, 0, 8*NW); vec[index[0]>>6] |= 1ULL<<(index[0]&63);
            int one = 0;
            { long p = N-1; for (;;){ long w = p>>6; while (w >= 0 && !vec[w]) w--; if (w < 0){ one = 1; break; } p = (w<<6) + 63 - __builtin_clzll(vec[w]); if (!basis[p]) break; uint64_t *b = basis[p]; for (long i = 0; i <= w; i++) vec[i] ^= b[i]; } }
            printf("%s{\"D\":%d,\"dim\":%ld,\"count\":%.0f,\"generators_used\":%ld,\"rank\":%ld,\"full\":%d,\"one_in_span\":%d}", D > Dmin ? "," : "", D, N, count, gens, rank, full, one);
            fflush(stdout);
            for (long i = 0; i < N; i++) free(basis[i]);
            free(basis); free(vec);
        }
        printf("]}\n"); fflush(stdout); free(index);
    }
    return 0;
}
