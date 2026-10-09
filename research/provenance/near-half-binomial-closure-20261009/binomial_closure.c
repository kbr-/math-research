/* Degree-D closures of block-field binomial systems, on exponent vectors.

Statement computed (side notebook near-half-pc-degree, entry-2026-10-09-binomial-closure-levels):
for m blocks of k bits read as elements of F_{2^k}, q = 2^k - 1, and rows (T_r, c_r, lambda_r)
meaning prod_{i in T_r} y_i^{c_{r,i}} = g^{lambda_r} with all y_i nonzero, the degree-D
polynomial-calculus closure (D at least the width w = k*t) is spanned by binomials and monomials,
and on normal forms a in Z_q^m of binary weight at most D it is the least labelled equivalence with
  row steps      a + j c_r ~ a, label j*lambda_r, when both weights are at most D;
  translation    a ~ b with both weights at most D-1 gives a + e ~ b + e, e a power of two in a block;
a class with two different labels is dead (its monomials lie in the closure), and a dead node of
weight at most D-1 makes its translates dead.  The system is refuted in degree D iff 0 is dead.
Dead classes are not merged with each other under translation (they may be fragmented); this does
not affect whether 0 is dead or the count of live classes.  Comment added after the recorded run.

Output, one JSON line per system: the rows, the least D >= w refuting it, and at the largest
proper D >= w (if any) the number of live classes by least weight (level sizes b_j), the number
of residue vectors of each weight, and the least X with binom(X,j) >= b_j.
Hypotheses asserted: every block lies in a row; the linear system is inconsistent (brute force).
Arguments, in groups of seven: mode k m t R seed count  (count systems with seeds seed, seed+1, ...).
mode 0: R random rows of t distinct blocks with random nonzero exponents and random right sides.
mode 1: flow conservation on a random simple t-regular graph with m vertices (R is ignored): blocks
are the edges, one row per vertex with exponent +1 or -1 by orientation, right sides random with
nonzero total; the graph is connected (asserted), so the sum of all rows is the only dependency.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int k, m, t, R, q, n, w;
static long N;
static int rowT[64][8], rowc[64][8], rowlam[64];
static long pw[18];
static uint8_t *wt; static int32_t *par; static uint8_t *pot, *dead; static int32_t *lowrep;
static int wres[64];
static uint64_t rng;
static unsigned rnd(void){ rng = rng*6364136223846793005ULL + 1442695040888963407ULL; return (unsigned)(rng>>33); }

static int digit(long a, int i){ return (int)((a/pw[i])%q); }
static long setdigit(long a, int i, int d){ return a + ((long)d - digit(a,i))*pw[i]; }

static long find(long a, int *val){           /* y^a ~ g^val y^root */
    long r = a; int v = 0;
    while (par[r] != r){ v += pot[r]; r = par[r]; }
    v %= q;
    long x = a; int acc = v;                  /* path compression */
    while (par[x] != x){ long nx = par[x]; int px = pot[x]; par[x] = (int32_t)r; pot[x] = (uint8_t)acc; acc = ((acc - px)%q + q)%q; x = nx; }
    *val = v; return r;
}
static int unite(long a, long b, int lam){    /* y^a ~ g^lam y^b; returns 1 if something changed */
    int va, vb; long ra = find(a,&va), rb = find(b,&vb);
    if (ra == rb){
        if (((va - vb - lam)%q + q)%q != 0 && !dead[ra]){ dead[ra] = 1; return 1; }
        return 0;
    }
    par[ra] = (int32_t)rb; pot[ra] = (uint8_t)((((lam + vb - va)%q)+q)%q);
    if (dead[ra]) dead[rb] = 1;
    return 1;
}
static int closure(int D){                    /* returns 1 if 0 is dead */
    for (long a = 0; a < N; a++){ par[a] = (int32_t)a; pot[a] = 0; dead[a] = 0; }
    for (int r = 0; r < R; r++)
        for (int j = 1; j < q; j++)
            for (long a = 0; a < N; a++){
                if (wt[a] > D) continue;
                long b = a;
                for (int s = 0; s < t; s++){ int i = rowT[r][s]; b = setdigit(b, i, (digit(a,i) + j*rowc[r][s])%q); }
                if (wt[b] > D) continue;
                unite(b, a, (j*rowlam[r])%q);
            }
    for (;;){
        long changed = 0;
        memset(lowrep, 0xff, sizeof(int32_t)*N);
        for (long a = 0; a < N; a++){
            if (wt[a] > D-1) continue;
            int va; long r = find(a,&va);
            if (lowrep[r] < 0) lowrep[r] = (int32_t)a;
        }
        for (long a = 0; a < N; a++){
            if (wt[a] > D-1) continue;
            int va, vp; long r = find(a,&va); long p = lowrep[r];
            int isdead = dead[r];
            if (p < 0 || (p == a && !isdead)) continue;   /* p < 0: class merged in this pass; next pass */
            if (find(p,&vp) != r) continue;
            int lam = ((va - vp)%q + q)%q;
            for (int i = 0; i < m; i++) for (int l = 0; l < k; l++){
                long ae = setdigit(a, i, (digit(a,i) + (1<<l))%q);
                if (isdead){ int v; long ra = find(ae,&v); if (!dead[ra]){ dead[ra] = 1; changed++; } continue; }
                long pe = setdigit(p, i, (digit(p,i) + (1<<l))%q);
                changed += unite(ae, pe, lam);
            }
        }
        int v; long r0 = find(0,&v);
        if (dead[r0]) return 1;
        if (!changed) return 0;
    }
}
static double binom(int X, int j){ double b = 1; for (int i = 0; i < j; i++) b = b*(X-i)/(i+1); return b; }

int main(int argc, char **argv){
    for (int g = 1; g + 6 < argc; g += 7){
        int mode = atoi(argv[g]), V = 0; g++;
        k = atoi(argv[g]); m = atoi(argv[g+1]); t = atoi(argv[g+2]); R = atoi(argv[g+3]);
        long seed0 = atol(argv[g+4]); int count = atoi(argv[g+5]); g--;
        if (mode == 1){ V = m; m = V*t/2; R = V; if (V*t%2 || V > 64){ fprintf(stderr, "bad graph\n"); return 2; } }
        q = (1<<k) - 1; n = m*k; w = k*t;
        if (m > 16 || R > 64 || t > 8 || k > 6 || k < 2){ fprintf(stderr, "parameters out of range\n"); return 2; }
        N = 1; for (int i = 0; i <= m; i++){ pw[i] = N; if (i < m) N *= q; }
        if (N > 50000000){ fprintf(stderr, "refusing q^m = %ld nodes\n", N); return 2; }
        for (int a = 0; a < q; a++) wres[a] = __builtin_popcount(a);
        wt = malloc(N); par = malloc(4*N); pot = malloc(N); dead = malloc(N); lowrep = malloc(4*N);
        for (long a = 0; a < N; a++){ int s = 0; for (int i = 0; i < m; i++) s += wres[digit(a,i)]; wt[a] = (uint8_t)s; }
        for (int c = 0; c < count; c++){
            long seed = seed0 + c; int attempt = 0, ok = 0;
            while (!ok && attempt < 2000){
                rng = 88172645463325252ULL ^ (uint64_t)(seed*1000003L + attempt*7919L + k*31 + m*131 + t*17 + R);
                for (int i = 0; i < 8; i++) rnd();
                int cover[17] = {0};
                if (mode == 1){
                    int stub[512], ns = V*t, fill[64] = {0}, good = 1, ne = 0, eu[256], ev[256];
                    for (int i = 0; i < ns; i++) stub[i] = i/t;
                    for (int i = ns-1; i > 0; i--){ int j = rnd()%(i+1); int x = stub[i]; stub[i] = stub[j]; stub[j] = x; }
                    for (int i = 0; i < ns && good; i += 2){
                        int u = stub[i], v = stub[i+1]; if (u == v) good = 0;
                        for (int e = 0; e < ne; e++) if ((eu[e]==u&&ev[e]==v)||(eu[e]==v&&ev[e]==u)) good = 0;
                        eu[ne] = u; ev[ne] = v; ne++;
                    }
                    if (good){ int comp[64]; for (int v = 0; v < V; v++) comp[v] = v;
                        for (int it = 0; it < V; it++) for (int e = 0; e < ne; e++){ int c = comp[eu[e]] < comp[ev[e]] ? comp[eu[e]] : comp[ev[e]]; comp[eu[e]] = comp[ev[e]] = c; }
                        for (int v = 0; v < V; v++) if (comp[v]) good = 0; }   /* connected */
                    if (!good){ attempt++; continue; }
                    int tot = 0;
                    for (int e = 0; e < ne; e++){
                        rowT[eu[e]][fill[eu[e]]] = e; rowc[eu[e]][fill[eu[e]]++] = 1;
                        rowT[ev[e]][fill[ev[e]]] = e; rowc[ev[e]][fill[ev[e]]++] = q-1; cover[e] = 1;
                    }
                    for (int r = 0; r < R; r++){ rowlam[r] = rnd()%q; tot += rowlam[r]; }
                    if (tot%q == 0) rowlam[0] = (rowlam[0]+1)%q;
                } else
                for (int r = 0; r < R; r++){
                    for (int s = 0; s < t; s++){
                        int i, dup;
                        do { i = rnd()%m; dup = 0; for (int u = 0; u < s; u++) if (rowT[r][u] == i) dup = 1; } while (dup);
                        rowT[r][s] = i; rowc[r][s] = 1 + rnd()%(q-1); cover[i] = 1;
                    }
                    rowlam[r] = rnd()%q;
                }
                ok = 1; for (int i = 0; i < m; i++) if (!cover[i]) ok = 0;
                if (ok){                       /* inconsistent over Z_q? brute force */
                    for (long x = 0; x < N && ok; x++){
                        int sat = 1;
                        for (int r = 0; r < R && sat; r++){ int s2 = 0; for (int s = 0; s < t; s++) s2 += rowc[r][s]*digit(x,rowT[r][s]); if (s2%q != rowlam[r]) sat = 0; }
                        if (sat) ok = 0;
                    }
                }
                attempt++;
            }
            if (!ok){ fprintf(stderr, "no inconsistent covering system found\n"); return 3; }
            int deg = -1;
            for (int D = w; D <= n; D++) if (closure(D)){ deg = D; break; }
            printf("{\"mode\":%d,\"k\":%d,\"m\":%d,\"t\":%d,\"R\":%d,\"seed\":%ld,\"attempt\":%d,\"n\":%d,\"w\":%d,\"rows\":[", mode, k, m, t, R, seed, attempt-1, n, w);
            for (int r = 0; r < R; r++){ printf("%s[[", r?",":""); for (int s = 0; s < t; s++) printf("%s%d", s?",":"", rowT[r][s]); printf("],["); for (int s = 0; s < t; s++) printf("%s%d", s?",":"", rowc[r][s]); printf("],%d]", rowlam[r]); }
            printf("],\"degree\":%d", deg);
            if (deg > w){
                int D = deg - 1; closure(D);
                int32_t *minw = malloc(4*N); for (long a = 0; a < N; a++) minw[a] = 255;
                long tot[64] = {0}, lev[64] = {0};
                for (long a = 0; a < N; a++){ if (wt[a] > D) continue; tot[wt[a]]++; int v; long r = find(a,&v); if (wt[a] < minw[r]) minw[r] = wt[a]; }
                for (long a = 0; a < N; a++) if (par[a] == a && wt[a] <= D && !dead[a]) lev[minw[a]]++;
                printf(",\"proper_D\":%d,\"levels\":[", D);
                for (int j = 0; j <= D; j++) printf("%s%ld", j?",":"", lev[j]);
                printf("],\"vectors\":["); for (int j = 0; j <= D; j++) printf("%s%ld", j?",":"", tot[j]);
                printf("],\"X\":[");
                for (int j = 0; j <= D; j++){ int X = j; while (binom(X,j) < (double)lev[j]) X++; printf("%s%d", j?",":"", lev[j]?X:0); }
                printf("]"); free(minw);
            }
            printf("}\n"); fflush(stdout);
        }
        free(wt); free(par); free(pot); free(dead); free(lowrep);
    }
    return 0;
}
