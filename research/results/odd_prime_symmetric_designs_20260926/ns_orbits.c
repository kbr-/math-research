/* Nullstellensatz degree over F_3 of onto weak PHP and its controls, in orbit coordinates.

   Statement tested (conj:occupancy-pinned-php, at imbalance m - N = 3): the least total degree d
   at which the system below has a Nullstellensatz refutation over F_3, i.e. at which no design
   exists.  A design of degree d is a linear functional l on multilinear monomials of degree <= d
   with l(1) = 1 and l(q t) = 0 for every axiom q and monomial t with deg(q t) <= d.

   System on an m x N board (pigeons i < m, holes j < N), variables x_ij:
     Booleanity x^2 = x (monomials are multilinear), collisions x_ij x_i'j = 0 (monomials are
     column-injective partial maps), rows sum_j x_ij = 1;
     variant "onto" adds columns sum_i x_ij = 1;
     variant "func" adds functionality x_ij x_ik = 0 (monomials in which a pigeon holds two holes
     are zero);  "ontofunc" adds both.
   Designs may be averaged over any group G of board symmetries whose order is prime to 3, so a
   design exists iff a G-invariant one does.  G is a Sylow 2-subgroup of S_m x S_N (or trivial
   with sym = 0, for validation).  Unknowns are the G-orbits of monomials; equations are those of
   one representative monomial t per orbit with all pigeons i and holes j, since every orbit of
   pairs (axiom, t) meets such a pair.

   Usage: ns_orbits CASE...   with CASE = m,N,dmax,variant,sym ; one JSON line per case and degree.
   Rows are added by increasing deg t; after the rows of degree k the test "e_empty in row span"
   decides refutability at degree k+1, and the case stops at its first refutation. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <flint/nmod_mat.h>

static int m, N, dmax, onto, func;
static int nmask; static int masks[1 << 12]; static uint64_t off[1 << 12 + 1], total;
static int pw[16];

static uint64_t mpow(int e) { uint64_t r = 1; while (e--) r *= m; return r; }

/* f[j] = pigeon at hole j or -1 */
static uint64_t encode(const int *f) {
    int S = 0; for (int j = 0; j < N; j++) if (f[j] >= 0) S |= 1 << j;
    /* binary search mask S among masks[] (sorted ascending by value) */
    int lo = 0, hi = nmask - 1;
    while (lo < hi) { int mid = (lo + hi) / 2; if (masks[mid] < S) lo = mid + 1; else hi = mid; }
    uint64_t v = 0, b = 1;
    for (int j = 0; j < N; j++) if (f[j] >= 0) { v += b * (uint64_t) f[j]; b *= m; }
    return off[lo] + v;
}
static void decode(uint64_t idx, int *f) {
    int lo = 0, hi = nmask - 1;
    while (lo < hi) { int mid = (lo + hi + 1) / 2; if (off[mid] <= idx) lo = mid; else hi = mid - 1; }
    uint64_t v = idx - off[lo]; int S = masks[lo];
    for (int j = 0; j < N; j++) if (S >> j & 1) { f[j] = (int) (v % m); v /= m; } else f[j] = -1;
}
static int is_zero(const int *f) {
    if (!func) return 0;
    for (int j = 0; j < N; j++) if (f[j] >= 0) for (int k = j + 1; k < N; k++) if (f[k] == f[j]) return 1;
    return 0;
}
static int degree(const int *f) { int d = 0; for (int j = 0; j < N; j++) d += f[j] >= 0; return d; }

static int32_t *par;
static uint32_t find(uint32_t x) { while ((uint32_t) par[x] != x) { par[x] = par[par[x]]; x = par[x]; } return x; }
static void unite(uint32_t a, uint32_t b) { a = find(a); b = find(b); if (a == b) return; if (a < b) par[b] = a; else par[a] = b; }

/* Sylow 2-subgroup generators of S_k: for each binary block [s, s+2^a) and level b < a, swap the
   halves of [s, s+2^(b+1)). */
static int gens(int k, int (*g)[16]) {
    int ng = 0, s = 0;
    for (int a = 4; a >= 0; a--) if (k >> a & 1) {
        for (int b = 0; b < a; b++) {
            for (int t = 0; t < k; t++) g[ng][t] = t;
            for (int t = 0; t < (1 << b); t++) { g[ng][s + t] = s + (1 << b) + t; g[ng][s + (1 << b) + t] = s + t; }
            ng++;
        }
        s += 1 << a;
    }
    return ng;
}

typedef struct { int n; int32_t col[64]; int val[64]; } row_t;
static void addterm(row_t *r, int32_t c, int v) {
    v = ((v % 3) + 3) % 3; if (!v) return;
    for (int t = 0; t < r->n; t++) if (r->col[t] == c) { r->val[t] = (r->val[t] + v) % 3; return; }
    r->col[r->n] = c; r->val[r->n] = v; r->n++;
}

static void run_case(int mm, int NN, int dd, const char *variant, int sym, FILE *out) {
    m = mm; N = NN; dmax = dd;
    onto = strstr(variant, "onto") != NULL; func = strstr(variant, "func") != NULL;
    nmask = 0; total = 0;
    for (int S = 0; S < (1 << N); S++) if (__builtin_popcount(S) <= dmax) {
        masks[nmask] = S; off[nmask] = total; total += mpow(__builtin_popcount(S)); nmask++; }
    if (total >= 0x7fffffffULL) { fprintf(out, "{\"m\":%d,\"N\":%d,\"error\":\"too large\"}\n", m, N); return; }
    par = malloc(sizeof(int32_t) * total);
    for (uint64_t i = 0; i < total; i++) par[i] = (int32_t) i;
    int gp[40][16], gh[40][16], ngp = 0, ngh = 0;
    if (sym) { ngp = gens(m, gp); ngh = gens(N, gh); }
    int f[16], h[16];
    if (ngp + ngh) for (uint64_t i = 0; i < total; i++) {
        decode(i, f);
        for (int g = 0; g < ngp; g++) { for (int j = 0; j < N; j++) h[j] = f[j] < 0 ? -1 : gp[g][f[j]]; unite(i, encode(h)); }
        for (int g = 0; g < ngh; g++) { for (int j = 0; j < N; j++) h[gh[g][j]] = f[j]; unite(i, encode(h)); }
    }
    /* compress: roots are orbit minima */
    int32_t norb = 0;
    for (uint64_t i = 0; i < total; i++) {
        if ((uint64_t) par[i] == i) { par[i] = -(++norb); }
        else par[i] = par[par[i]];   /* par[i] < i was already relabelled */
    }
    /* orbit data */
    uint64_t *rep = malloc(sizeof(uint64_t) * norb); int *odeg = malloc(sizeof(int) * norb); char *ozero = malloc(norb);
    for (int32_t o = 0; o < norb; o++) rep[o] = UINT64_MAX;
    for (uint64_t i = 0; i < total; i++) { int32_t o = -par[i] - 1; if (rep[o] == UINT64_MAX) rep[o] = i; }
    int32_t ncol = 0; int32_t *colof = malloc(sizeof(int32_t) * norb);
    for (int32_t o = 0; o < norb; o++) { decode(rep[o], f); odeg[o] = degree(f); ozero[o] = (char) is_zero(f); colof[o] = ozero[o] ? -1 : ncol++; }
    /* incremental elimination by level */
    nmod_mat_t B; nmod_mat_init(B, 0, ncol, 3); long rank = 0;
    int refuted_at = -1;
    long chunkmax = ncol > 2000 ? ncol : 2000;
    row_t *buf = malloc(sizeof(row_t) * chunkmax); long nbuf = 0;
    for (int k = 0; k < dmax && refuted_at < 0; k++) {
        long nrows = 0;
        for (int32_t o = 0; o <= norb; o++) {
            int flush = (o == norb) || nbuf + m + N > chunkmax;
            if (flush && nbuf) {
                nmod_mat_t A; nmod_mat_init(A, rank + nbuf, ncol, 3);
                for (long r = 0; r < rank; r++) for (long c = 0; c < ncol; c++) nmod_mat_entry(A, r, c) = nmod_mat_entry(B, r, c);
                for (long r = 0; r < nbuf; r++) for (int t = 0; t < buf[r].n; t++) nmod_mat_entry(A, rank + r, buf[r].col[t]) = buf[r].val[t];
                long rk = nmod_mat_rref(A);
                nmod_mat_clear(B); nmod_mat_init(B, rk, ncol, 3);
                for (long r = 0; r < rk; r++) for (long c = 0; c < ncol; c++) nmod_mat_entry(B, r, c) = nmod_mat_entry(A, r, c);
                nmod_mat_clear(A); rank = rk; nbuf = 0;
            }
            if (o == norb) break;
            if (odeg[o] != k || ozero[o]) continue;
            decode(rep[o], f);
            for (int i = 0; i < m; i++) {            /* row axiom of pigeon i times t */
                row_t *r = &buf[nbuf]; r->n = 0; int a = 0;
                for (int j = 0; j < N; j++) a += f[j] == i;
                addterm(r, colof[o], a - 1);
                for (int j = 0; j < N; j++) if (f[j] < 0) {
                    f[j] = i; if (!is_zero(f)) addterm(r, colof[-par[encode(f)] - 1], 1); f[j] = -1; }
                if (r->n) { nbuf++; nrows++; }
            }
            if (onto) for (int j = 0; j < N; j++) if (f[j] < 0) {   /* column axiom of free hole j times t */
                row_t *r = &buf[nbuf]; r->n = 0;
                addterm(r, colof[o], -1);
                for (int i = 0; i < m; i++) { f[j] = i; if (!is_zero(f)) addterm(r, colof[-par[encode(f)] - 1], 1); }
                f[j] = -1;
                if (r->n) { nbuf++; nrows++; }
            }
        }
        /* e_empty (column 0) in the row span of the rref basis? */
        int in_span = 0;
        for (long r = 0; r < rank; r++) {
            long c = 0; while (c < ncol && nmod_mat_entry(B, r, c) == 0) c++;
            if (c == 0) { in_span = 1; for (long c2 = 1; c2 < ncol; c2++) if (nmod_mat_entry(B, r, c2)) { in_span = 0; break; } }
            if (c >= 0) break;
        }
        if (in_span) refuted_at = k + 1;
        fprintf(out, "{\"m\":%d,\"N\":%d,\"variant\":\"%s\",\"sym\":%d,\"monomials\":%llu,\"orbits\":%d,\"columns\":%d,"
                "\"degree\":%d,\"rows_added\":%ld,\"rank\":%ld,\"refuted\":%s}\n", m, N, variant, sym,
                (unsigned long long) total, norb, ncol, k + 1, nrows, rank, in_span ? "true" : "false");
        fflush(out);
    }
    nmod_mat_clear(B); free(buf); free(rep); free(odeg); free(ozero); free(colof); free(par);
}

int main(int argc, char **argv) {
    for (int a = 1; a < argc; a++) {
        int mm, NN, dd, sym; char variant[32];
        if (sscanf(argv[a], "%d,%d,%d,%31[a-z],%d", &mm, &NN, &dd, variant, &sym) != 5 || NN > 12 || mm > 15 || dd > NN) {
            fprintf(stderr, "bad case %s\n", argv[a]); return 2; }
        run_case(mm, NN, dd, variant, sym, stdout);
    }
    return 0;
}
