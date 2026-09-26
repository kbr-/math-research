/* Nullstellensatz designs of functional PHP plus random pinned linear equations, over F_3.

   Statement tested (Nullstellensatz pinning capacity): for FPHP^m_n (Booleanity, collisions,
   functionality, rows sum_j x_ij = 1) and h uniformly random dense linear equations
   L_k = sum_{i,j} a^k_{ij} x_ij = q_k with q_k uniform in {1,2}, a degree-d design exists
   (no Nullstellensatz refutation of total degree d) for h below a threshold h*.  The count
   heuristic predicts h* ~ dim(designs of FPHP at degree d) / |T_{d-1}|, since each equation adds
   at most |T_{d-1}| linear conditions (its multiples by monomials of degree <= d-1).

   Monomials are partial injective maps holes -> pigeons of size <= d (f[j] = pigeon or -1).
   A design is a functional l on them with l(1) = 1 and l(q t) = 0 for every axiom q and
   monomial t with deg t <= d-1.  Rows are added incrementally: all FPHP rows, then the multiples of
   one equation at a time; after each equation the program tests whether e_empty is in the row span
   (FLINT rref), i.e. whether a refutation of degree d exists, and stops at the first refutation.

   Usage: ns_pins NSEEDS m,n,d ...   one JSON line per (case, seed, h) and a summary per seed.
   The FPHP basis of a case is computed once and copied for every seed. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <flint/nmod_mat.h>

static int m, N, d;
static int nmask, masks[1 << 12]; static long off[1 << 12], total;
static long *colof; static long ncol;

static long mpow(int e) { long r = 1; while (e--) r *= m; return r; }
static long encode(const int *f) {
    int S = 0; for (int j = 0; j < N; j++) if (f[j] >= 0) S |= 1 << j;
    int lo = 0, hi = nmask - 1;
    while (lo < hi) { int mid = (lo + hi) / 2; if (masks[mid] < S) lo = mid + 1; else hi = mid; }
    long v = 0, b = 1;
    for (int j = 0; j < N; j++) if (f[j] >= 0) { v += b * f[j]; b *= m; }
    return off[lo] + v;
}
static void decode(long idx, int *f) {
    int lo = 0, hi = nmask - 1;
    while (lo < hi) { int mid = (lo + hi + 1) / 2; if (off[mid] <= idx) lo = mid; else hi = mid - 1; }
    long v = idx - off[lo]; int S = masks[lo];
    for (int j = 0; j < N; j++) if (S >> j & 1) { f[j] = (int) (v % m); v /= m; } else f[j] = -1;
}
static int injective(const int *f) {
    for (int j = 0; j < N; j++) if (f[j] >= 0) for (int k = j + 1; k < N; k++) if (f[k] == f[j]) return 0;
    return 1;
}
static int deg(const int *f) { int s = 0; for (int j = 0; j < N; j++) s += f[j] >= 0; return s; }

static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

/* Row buffer and incremental reduced echelon basis.  Bfull holds the basis rows 0..rank-1 in
   reduced form (each pivot column is zero in every other row).  A batch R of new rows is reduced
   against the basis by one product R - R[:,piv] B, its residual is put in rref, and the basis is
   updated by B - B[:,newpiv] R' in row chunks: only new rows are eliminated, never the old basis. */
static nmod_mat_t Bfull; static long rank; static long *piv, *rowof;
static long *rbuf_col; static int *rbuf_val; static long *rstart; static long nrows, nterms, cap_rows, cap_terms;
static void row_begin(void) { if (nrows + 2 >= cap_rows) { cap_rows *= 2; rstart = realloc(rstart, sizeof(long) * cap_rows); } rstart[nrows] = nterms; }
static void row_add(long c, int v) {
    v = ((v % 3) + 3) % 3; if (!v) return;
    for (long k = rstart[nrows]; k < nterms; k++) if (rbuf_col[k] == c) { rbuf_val[k] = (rbuf_val[k] + v) % 3; return; }
    if (nterms + 1 >= cap_terms) { cap_terms *= 2; rbuf_col = realloc(rbuf_col, sizeof(long) * cap_terms); rbuf_val = realloc(rbuf_val, sizeof(int) * cap_terms); }
    rbuf_col[nterms] = c; rbuf_val[nterms] = v; nterms++;
}
static void row_end(void) { nrows++; rstart[nrows] = nterms; }
static void flush(void) {
    if (!nrows) return;
    long nr = nrows;
    nmod_mat_t R; nmod_mat_init(R, nr, ncol, 3);
    for (long r = 0; r < nr; r++) for (long k = rstart[r]; k < rstart[r + 1]; k++) {
        long c = rbuf_col[k]; nmod_mat_entry(R, r, c) = (nmod_mat_entry(R, r, c) + rbuf_val[k]) % 3; }
    nrows = 0; nterms = 0; rstart[0] = 0;
    if (rank > 0) {
        nmod_mat_t P, B, PB; nmod_mat_init(P, nr, rank, 3); nmod_mat_init(PB, nr, ncol, 3);
        nmod_mat_window_init(B, Bfull, 0, 0, rank, ncol);
        for (long r = 0; r < nr; r++) for (long k = 0; k < rank; k++) nmod_mat_entry(P, r, k) = nmod_mat_entry(R, r, piv[k]);
        nmod_mat_mul(PB, P, B); nmod_mat_sub(R, R, PB);
        nmod_mat_window_clear(B); nmod_mat_clear(P); nmod_mat_clear(PB);
    }
    long rk = nmod_mat_rref(R);
    if (rk > 0) {
        long *np = malloc(sizeof(long) * rk);
        for (long k = 0; k < rk; k++) { long c = 0; while (nmod_mat_entry(R, k, c) == 0) c++; np[k] = c; }
        nmod_mat_t Rw; nmod_mat_window_init(Rw, R, 0, 0, rk, ncol);
        for (long r0 = 0; r0 < rank; r0 += 2048) {
            long r1 = r0 + 2048 < rank ? r0 + 2048 : rank;
            nmod_mat_t Q, QR, Bw; nmod_mat_init(Q, r1 - r0, rk, 3); nmod_mat_init(QR, r1 - r0, ncol, 3);
            nmod_mat_window_init(Bw, Bfull, r0, 0, r1, ncol);
            for (long r = r0; r < r1; r++) for (long k = 0; k < rk; k++) nmod_mat_entry(Q, r - r0, k) = nmod_mat_entry(Bfull, r, np[k]);
            nmod_mat_mul(QR, Q, Rw); nmod_mat_sub(Bw, Bw, QR);
            nmod_mat_window_clear(Bw); nmod_mat_clear(Q); nmod_mat_clear(QR);
        }
        for (long k = 0; k < rk; k++) {
            for (long c = 0; c < ncol; c++) nmod_mat_entry(Bfull, rank, c) = nmod_mat_entry(R, k, c);
            piv[rank] = np[k]; rowof[np[k]] = rank; rank++;
        }
        nmod_mat_window_clear(Rw); free(np);
    }
    nmod_mat_clear(R);
}
static int refuted(void) {
    long r = rowof[0]; if (r < 0) return 0;
    for (long c = 1; c < ncol; c++) if (nmod_mat_entry(Bfull, r, c)) return 0;
    return 1;
}

static void run_case(int nseeds) {
    nmask = 0; total = 0;
    for (int S = 0; S < (1 << N); S++) if (__builtin_popcount(S) <= d) { masks[nmask] = S; off[nmask] = total; total += mpow(__builtin_popcount(S)); nmask++; }
    colof = malloc(sizeof(long) * total); ncol = 0;
    int f[16];
    long nlow = 0;   /* |T_{d-1}| */
    for (long i = 0; i < total; i++) { decode(i, f); colof[i] = injective(f) ? ncol++ : -1; if (colof[i] >= 0 && deg(f) <= d - 1) nlow++; }
    nmod_mat_init(Bfull, ncol, ncol, 3); piv = malloc(sizeof(long) * ncol); rowof = malloc(sizeof(long) * ncol);
    rank = 0; for (long c = 0; c < ncol; c++) rowof[c] = -1; nrows = 0; nterms = 0; rstart[0] = 0;
    /* FPHP rows, once per case: pigeon i absent from t gives -l(t) + sum_{free j} l(t + (j->i)) */
    for (long idx = 0; idx < total; idx++) {
        if (colof[idx] < 0) continue; decode(idx, f); if (deg(f) > d - 1) continue;
        for (int i = 0; i < m; i++) {
            int present = 0; for (int j = 0; j < N; j++) present |= f[j] == i;
            if (present) continue;
            row_begin(); row_add(colof[idx], -1);
            for (int j = 0; j < N; j++) if (f[j] < 0) { f[j] = i; row_add(colof[encode(f)], 1); f[j] = -1; }
            row_end();
            if (nrows >= 2048) flush();
        }
    }
    flush();
    long rank0 = rank; long dimD = ncol - rank0; int ref0 = refuted();
    printf("{\"m\":%d,\"n\":%d,\"d\":%d,\"h\":0,\"columns\":%ld,\"T_dminus1\":%ld,\"rank\":%ld,\"design_dim\":%ld,\"count_prediction\":%.3f,\"refuted\":%s}\n",
           m, N, d, ncol, nlow, rank, dimD, (double) dimD / nlow, ref0 ? "true" : "false");
    fflush(stdout);
    if (ref0) { nmod_mat_clear(Bfull); free(piv); free(rowof); free(colof); return; }
    nmod_mat_t B0; nmod_mat_init(B0, rank0, ncol, 3);
    for (long r = 0; r < rank0; r++) for (long c = 0; c < ncol; c++) nmod_mat_entry(B0, r, c) = nmod_mat_entry(Bfull, r, c);
    long *piv0 = malloc(sizeof(long) * ncol), *rowof0 = malloc(sizeof(long) * ncol);
    memcpy(piv0, piv, sizeof(long) * ncol); memcpy(rowof0, rowof, sizeof(long) * ncol);
    int *coef = malloc(sizeof(int) * m * N);
    for (int seed = 1; seed <= nseeds; seed++) {
        rs = (uint64_t) seed * 2654435761ULL + 1000003ULL * (m * 100 + N * 10 + d);
        for (int k = 0; k < 8; k++) rnd();
        for (long r = 0; r < rank0; r++) for (long c = 0; c < ncol; c++) nmod_mat_entry(Bfull, r, c) = nmod_mat_entry(B0, r, c);
        memcpy(piv, piv0, sizeof(long) * ncol); memcpy(rowof, rowof0, sizeof(long) * ncol); rank = rank0;
        long before = dimD; int h = 0;
        while (!refuted()) {
            h++; before = ncol - rank;
            for (int e = 0; e < m * N; e++) coef[e] = (int) (rnd() % 3);
            int q = 1 + (int) (rnd() % 2);
            for (long idx = 0; idx < total; idx++) {
                if (colof[idx] < 0) continue; decode(idx, f); if (deg(f) > d - 1) continue;
                row_begin(); row_add(colof[idx], -q);
                for (int i = 0; i < m; i++) for (int j = 0; j < N; j++) {
                    int c = coef[i * N + j]; if (!c) continue;
                    if (f[j] == i) { row_add(colof[idx], c); continue; }
                    if (f[j] >= 0) continue;                       /* collision */
                    int used = 0; for (int k = 0; k < N; k++) used |= f[k] == i;
                    if (used) continue;                            /* functionality */
                    f[j] = i; row_add(colof[encode(f)], c); f[j] = -1;
                }
                row_end();
            }
            flush();
            printf("{\"m\":%d,\"n\":%d,\"d\":%d,\"seed\":%d,\"h\":%d,\"design_dim\":%ld,\"refuted\":%s}\n",
                   m, N, d, seed, h, ncol - rank, refuted() ? "true" : "false");
            fflush(stdout);
        }
        printf("{\"m\":%d,\"n\":%d,\"d\":%d,\"seed\":%d,\"summary\":true,\"h_star\":%d,\"design_dim_before_last\":%ld,\"design_dim_at_refutation\":%ld,\"count_prediction\":%.3f}\n",
               m, N, d, seed, h, before, ncol - rank, (double) dimD / nlow);
        fflush(stdout);
    }
    free(coef); nmod_mat_clear(B0); free(piv0); free(rowof0);
    nmod_mat_clear(Bfull); free(piv); free(rowof); free(colof);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: ns_pins NSEEDS m,n,d ...\n"); return 2; }
    int nseeds = atoi(argv[1]);
    cap_rows = 1024; cap_terms = 1 << 16;
    rstart = malloc(sizeof(long) * cap_rows); rbuf_col = malloc(sizeof(long) * cap_terms); rbuf_val = malloc(sizeof(int) * cap_terms);
    for (int a = 2; a < argc; a++) {
        if (sscanf(argv[a], "%d,%d,%d", &m, &N, &d) != 3 || N > 12 || m > 15 || d > N) { fprintf(stderr, "bad case %s\n", argv[a]); return 2; }
        run_case(nseeds);
    }
    return 0;
}
