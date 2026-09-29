/* Order of the Wronskian discriminant across a collision hyperplane at the neck merging loci
 * (30 September 2026).
 *
 * Tested statement (merging-locus theorem): at a generic point p of Z_k = H cap {Hank_k(1/c) = 0},
 * H = {a_1 = a_2}, 1 <= k <= M-2, M = N-2, the discriminant Delta_W = Disc_z W has, near p, local
 * factors (s^(2M+1) - K eps^(2M-2k)) and (s^(2M-1) - K' eps^(2M-2k-2)) beyond its generic behaviour,
 * with s = Hank_k and eps the half-separation of the pair. Consequence tested here: on a line
 * a(u) = a0 + u gamma crossing H at a0 (gamma_1 != gamma_2, gamma generic), the order of u = 0 in
 * D(u) = Disc_z W(a(u); z) exceeds its value at a generic a0 in H by exactly 4M - 4k - 2.
 * (A symmetric trinomial edge without splitting would give a multiple of 2M instead.)
 * Also reported at p: Hank_(k-1), Hank_(k+1) and the shifted minor det[p_(i+j) (j<k), p_(i+k+1)]
 * (conjectured leading coefficient of the vertex S' = W_k with its top column raised), which the
 * theorem needs nonzero.
 *
 * Kernel functions (Fval, Wval, line_disc, hank) copied unchanged from
 * bmd_cube_restricted_discriminant.c; computation over F_p, p = 2^61 - 1.
 * Usage: bmd_cube_merging_order seed OUT.txt N1 [N2 ...]
 */
#include <flint/flint.h>
#include <flint/nmod_vec.h>
#include <flint/nmod_poly.h>
#include <flint/nmod_poly_factor.h>
#include <flint/nmod_mat.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>

static nmod_t MOD;
static mp_limb_t P;
static int N, R, LAM, THETA;
static mp_limb_t *BETA;
static unsigned long long rng_state;

static mp_limb_t rnd(void)
{
    unsigned long long z = (rng_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    z ^= z >> 31;
    return (mp_limb_t)(z % P);
}

static mp_limb_t Fval(const mp_limb_t *b, nmod_mat_t M, mp_limb_t *px, mp_limb_t *py)
{
    int row = 0;
    for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++) {
            px[0] = BETA[0];
            py[0] = BETA[0];
            mp_limb_t xi = 1, yj = 1;
            for (int m = 1; m < R; m++) {
                xi = nmod_mul(xi, b[i], MOD);
                yj = nmod_mul(yj, b[j], MOD);
                px[m] = nmod_mul(BETA[m], xi, MOD);
                py[m] = nmod_mul(BETA[m], yj, MOD);
            }
            for (int k = 0; k < R; k++) {
                unsigned __int128 acc = 0;
                for (int m = 0; m <= k; m++) acc += (unsigned __int128)px[m] * py[k - m];
                nmod_mat_entry(M, row, k) = (mp_limb_t)(acc % P);
            }
            row++;
        }
    mp_limb_t d = nmod_mat_det(M);
    mp_limb_t den = 1;
    for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++) den = nmod_mul(den, nmod_sub(b[i], b[j], MOD), MOD);
    den = nmod_pow_ui(den, N - 2, MOD);
    return nmod_mul(d, nmod_inv(den, MOD), MOD);
}

static mp_limb_t Wval(const mp_limb_t *a, mp_limb_t z, nmod_mat_t M, mp_limb_t *px, mp_limb_t *py,
                      mp_limb_t *b)
{
    mp_limb_t prod = 1;
    for (int i = 0; i < N; i++) {
        mp_limb_t d = nmod_sub(a[i], z, MOD);
        b[i] = nmod_inv(d, MOD);
        prod = nmod_mul(prod, d, MOD);
    }
    return nmod_mul(Fval(b, M, px, py), nmod_pow_ui(prod, THETA, MOD), MOD);
}

static long binom_small(long n, long k)
{
    long r = 1;
    for (long i = 1; i <= k; i++) r = r * (n - k + i) / i;
    return r;
}

/* D(u) along the line a(u) = a0 + u g; returns multiplicity c of u = 0 and E = (D/u^c)(0);
 * also the multiplicity at every collision root uij (for the per-pair multiplicity). */
static int line_disc(const mp_limb_t *a0, const mp_limb_t *g, long *cmult, mp_limb_t *E,
                     long *pairmult, int *degfull)
{
    const long DW = 2L * LAM, DU = 3L * LAM, DD = 4L * LAM * (2L * LAM - 1);
    const int SL = 4;
    long GU = DU + 1 + SL, GZ = DW + 1 + SL;
    mp_limb_t *U = malloc(sizeof(mp_limb_t) * GU), *Z = malloc(sizeof(mp_limb_t) * GZ);
    for (long q = 0; q < GU; q++) U[q] = nmod_add(1000 + q, 0, MOD);
    for (long h = 0; h < GZ; h++) Z[h] = nmod_add(7777777 + 13 * h, 0, MOD);
    nmod_mat_t M; nmod_mat_init(M, R, R, P);
    mp_limb_t *px = malloc(sizeof(mp_limb_t) * R), *py = malloc(sizeof(mp_limb_t) * R);
    mp_limb_t *a = malloc(sizeof(mp_limb_t) * N), *b = malloc(sizeof(mp_limb_t) * N);
    mp_limb_t *row = malloc(sizeof(mp_limb_t) * GZ), *col = malloc(sizeof(mp_limb_t) * GU);
    mp_limb_t *coef = malloc(sizeof(mp_limb_t) * GU * (DW + 1));
    nmod_poly_t w, wd; nmod_poly_init(w, P); nmod_poly_init(wd, P);
    for (long q = 0; q < GU; q++) {
        for (int i = 0; i < N; i++) a[i] = nmod_add(a0[i], nmod_mul(U[q], g[i], MOD), MOD);
        for (long h = 0; h < GZ; h++) row[h] = Wval(a, Z[h], M, px, py, b);
        nmod_poly_interpolate_nmod_vec_fast(w, Z, row, GZ);
        for (long k = 0; k <= DW; k++) coef[q * (DW + 1) + k] = nmod_poly_get_coeff_ui(w, k);
    }
    nmod_poly_struct *ck = malloc(sizeof(nmod_poly_struct) * (DW + 1));
    for (long k = 0; k <= DW; k++) {
        for (long q = 0; q < GU; q++) col[q] = coef[q * (DW + 1) + k];
        nmod_poly_init(ck + k, P);
        nmod_poly_interpolate_nmod_vec_fast(ck + k, U, col, GU);
    }
    long ND = DD + 1 + SL, NC = ND + ND / 8 + 64, got = 0;
    mp_limb_t *cu = malloc(sizeof(mp_limb_t) * NC), *cv = malloc(sizeof(mp_limb_t) * NC);
    for (long t = 0; t < NC && got < ND; t++) {
        mp_limb_t uu = nmod_add(5000000 + 3 * t, 0, MOD);
        nmod_poly_zero(w);
        for (long k = 0; k <= DW; k++) nmod_poly_set_coeff_ui(w, k, nmod_poly_evaluate_nmod(ck + k, uu));
        if (nmod_poly_degree(w) != DW) continue;
        nmod_poly_derivative(wd, w);
        mp_limb_t res = nmod_poly_resultant(w, wd);
        cu[got] = uu;
        cv[got] = nmod_mul(res, nmod_inv(*nmod_poly_lead(w), MOD), MOD);
        got++;
    }
    int ok = (got == ND);
    if (ok) {
        nmod_poly_t D, lin, qq, rr;
        nmod_poly_init(D, P); nmod_poly_init(lin, P); nmod_poly_init(qq, P); nmod_poly_init(rr, P);
        nmod_poly_interpolate_nmod_vec_fast(D, cu, cv, ND);
        *degfull = (nmod_poly_degree(D) == DD);
        long c = 0;
        while (nmod_poly_degree(D) > 0 && nmod_poly_get_coeff_ui(D, 0) == 0) { nmod_poly_shift_right(D, D, 1); c++; }
        *cmult = c;
        *E = nmod_poly_get_coeff_ui(D, 0);
        /* per-pair multiplicity at the other collision roots on this line */
        int t = 0;
        for (int i = 0; i < N; i++)
            for (int j = i + 1; j < N; j++, t++) {
                mp_limb_t dg = nmod_sub(g[i], g[j], MOD);
                pairmult[t] = -1;
                if (!dg) continue;
                mp_limb_t uij = nmod_neg(nmod_mul(nmod_sub(a0[i], a0[j], MOD), nmod_inv(dg, MOD), MOD), MOD);
                if (uij == 0) continue;
                nmod_poly_zero(lin); nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(uij, MOD));
                nmod_poly_t Dc; nmod_poly_init(Dc, P); nmod_poly_set(Dc, D);
                long m = 0;
                while (nmod_poly_degree(Dc) > 0 && nmod_poly_evaluate_nmod(Dc, uij) == 0) { nmod_poly_divrem(qq, rr, Dc, lin); nmod_poly_set(Dc, qq); m++; }
                pairmult[t] = m;
                nmod_poly_clear(Dc);
            }
        nmod_poly_clear(D); nmod_poly_clear(lin); nmod_poly_clear(qq); nmod_poly_clear(rr);
    }
    for (long k = 0; k <= DW; k++) nmod_poly_clear(ck + k);
    free(ck); free(cu); free(cv); free(U); free(Z); free(px); free(py); free(a); free(b); free(row);
    free(col); free(coef); nmod_poly_clear(w); nmod_poly_clear(wd); nmod_mat_clear(M);
    return ok;
}

/* Hank_k(b) = det[p_(i+j)(b)]_(0<=i,j<=k), b_j = 1/c_j over the N-2 roots other than the pair. */
static mp_limb_t hank(const mp_limb_t *c, int m, int k)
{
    mp_limb_t *pw = malloc(sizeof(mp_limb_t) * (2 * k + 1));
    for (int e = 0; e <= 2 * k; e++) {
        mp_limb_t s = 0;
        for (int j = 0; j < m; j++) s = nmod_add(s, nmod_pow_ui(nmod_inv(c[j], MOD), e, MOD), MOD);
        pw[e] = s;
    }
    nmod_mat_t H; nmod_mat_init(H, k + 1, k + 1, P);
    for (int i = 0; i <= k; i++) for (int j = 0; j <= k; j++) nmod_mat_entry(H, i, j) = pw[i + j];
    mp_limb_t d = nmod_mat_det(H);
    nmod_mat_clear(H); free(pw);
    return d;
}


/* The neck window blocks at the cluster polynomial P = prod_j (x - b_j), b_j = 1/c_j:
 * det of [G(m,D+1) - G(m-1,D) - G(m,M) G(M-1,D)] for rows m = M-k..M-1 and columns D in Dset,
 * with G(m,n) = beta_n / beta_m [x^m](x^n mod P) (the neck window theorem's Gamma_k). Dset is
 * M..M+k-1 (Gamma_k) or M..M+k-2, M+k (Gamma'_k, the block of S' = W_k with its top column raised). */
static mp_limb_t gamma_det(const mp_limb_t *c, int m, int k, int shifted)
{
    nmod_poly_t Pp, xp, r; nmod_poly_init(Pp, P); nmod_poly_init(xp, P); nmod_poly_init(r, P);
    nmod_poly_one(Pp);
    for (int j = 0; j < m; j++) {
        nmod_poly_t lin; nmod_poly_init(lin, P);
        nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(nmod_inv(c[j], MOD), MOD));
        nmod_poly_mul(Pp, Pp, lin); nmod_poly_clear(lin);
    }
    int nmax = m + k + 2;
    mp_limb_t *Gt = calloc((size_t)(nmax + 1) * m, sizeof(mp_limb_t));  /* [x^i](x^n mod P) */
    nmod_poly_zero(xp); nmod_poly_set_coeff_ui(xp, 1, 1);
    for (int n = 0; n <= nmax; n++) {
        nmod_poly_powmod_ui_binexp(r, xp, n, Pp);
        for (int i = 0; i < m; i++) Gt[n * m + i] = nmod_poly_get_coeff_ui(r, i);
    }
#define GG(mm, nn) ((mm) < 0 ? 0 : ((nn) < m ? ((mm) == (nn)) : nmod_mul(nmod_mul(BETA[nn], nmod_inv(BETA[mm], MOD), MOD), Gt[(nn) * m + (mm)], MOD)))
    nmod_mat_t Gm; nmod_mat_init(Gm, k, k, P);
    for (int i = 0; i < k; i++)
        for (int jj = 0; jj < k; jj++) {
            int mm = m - k + i, D = m + jj + (shifted && jj == k - 1);
            mp_limb_t v = nmod_sub(GG(mm, D + 1), GG(mm - 1, D), MOD);
            v = nmod_sub(v, nmod_mul(GG(mm, m), GG(m - 1, D), MOD), MOD);
            nmod_mat_entry(Gm, i, jj) = v;
        }
#undef GG
    mp_limb_t d = nmod_mat_det(Gm);
    nmod_mat_clear(Gm); free(Gt); nmod_poly_clear(Pp); nmod_poly_clear(xp); nmod_poly_clear(r);
    return d;
}

/* det[p_(i+j) (j < k), p_(i+k+1) (j = k)]_(0<=i,j<=k), p_e the power sums of b_j = 1/c_j. */
static mp_limb_t hank_shift(const mp_limb_t *c, int m, int k)
{
    mp_limb_t *pw = malloc(sizeof(mp_limb_t) * (2 * k + 2));
    for (int e = 0; e <= 2 * k + 1; e++) {
        mp_limb_t s = 0;
        for (int j = 0; j < m; j++) s = nmod_add(s, nmod_pow_ui(nmod_inv(c[j], MOD), e, MOD), MOD);
        pw[e] = s;
    }
    nmod_mat_t H; nmod_mat_init(H, k + 1, k + 1, P);
    for (int i = 0; i <= k; i++) for (int j = 0; j <= k; j++) nmod_mat_entry(H, i, j) = pw[i + j + (j == k)];
    mp_limb_t d = nmod_mat_det(H);
    nmod_mat_clear(H); free(pw);
    return d;
}

/* A root y in F_p of y -> Hank_k(b_1..b_(m-1), y) (degree <= 2k in y), by interpolation; 0 if none. */
static mp_limb_t hank_root(const mp_limb_t *bfix, int m, int k)
{
    int n = 2 * k + 1;
    mp_limb_t *xs = malloc(sizeof(mp_limb_t) * n), *ys = malloc(sizeof(mp_limb_t) * n), c[64];
    for (int t = 0; t < n; t++) {
        xs[t] = nmod_add(101 + 7 * t, 0, MOD);
        for (int j = 0; j < m - 1; j++) c[j] = nmod_inv(bfix[j], MOD);
        c[m - 1] = nmod_inv(xs[t], MOD);
        ys[t] = hank(c, m, k);
    }
    nmod_poly_t h; nmod_poly_init(h, P);
    nmod_poly_interpolate_nmod_vec_fast(h, xs, ys, n);
    nmod_poly_factor_t f; nmod_poly_factor_init(f);
    mp_limb_t root = 0;
    if (nmod_poly_degree(h) > 0) {
        nmod_poly_roots(f, h, 0);
        for (long i = 0; i < f->num && !root; i++) {
            mp_limb_t r = nmod_neg(nmod_poly_get_coeff_ui(f->p + i, 0), MOD);
            int bad = (r == 0);
            for (int j = 0; j < m - 1; j++) if (r == bfix[j]) bad = 1;
            if (!bad) root = r;
        }
    }
    nmod_poly_factor_clear(f); nmod_poly_clear(h); free(xs); free(ys);
    return root;
}

static int run_one(FILE *fo)
{
    P = 2305843009213693951UL;
    nmod_init(&MOD, P);
    R = (int)binom_small(N, 2);
    LAM = 3 * (int)binom_small(N, 4);
    if ((4 * LAM) % N) { fprintf(fo, "N=%d: theta not integral\n", N); return 1; }
    THETA = 4 * LAM / N;
    BETA = malloc(sizeof(mp_limb_t) * (R + 1));
    {
        mp_limb_t inv2 = nmod_inv(2, MOD), cc = 1, mh = nmod_neg(nmod_mul(3, inv2, MOD), MOD);
        BETA[0] = 1;
        for (int m = 1; m <= R; m++) {
            cc = nmod_mul(cc, nmod_mul(nmod_sub(mh, (mp_limb_t)(m - 1), MOD), nmod_inv((mp_limb_t)m, MOD), MOD), MOD);
            BETA[m] = cc;
        }
    }
    int M2 = N - 2;
    /* jobs: base points a0 in H, generic (k = 0) or on Z_k (1 <= k <= M-2); two directions each */
    int NJ = 2 * (M2 - 1);
    mp_limb_t A0[64][64], G[64][64];
    int KJ[64];
    for (int q = 0; q < NJ; q++) {
        int k = q / 2;
        KJ[q] = k;
        while (1) {
            mp_limb_t x = rnd(), bfix[64];
            A0[q][0] = x; A0[q][1] = x;
            for (int j = 2; j < N - 1; j++) A0[q][j] = rnd();
            if (k == 0) { A0[q][N - 1] = rnd(); break; }
            for (int j = 2; j < N - 1; j++) bfix[j - 2] = nmod_inv(nmod_sub(A0[q][j], x, MOD), MOD);
            mp_limb_t y = hank_root(bfix, M2, k);
            if (!y) continue;
            A0[q][N - 1] = nmod_add(x, nmod_inv(y, MOD), MOD);
            break;
        }
        for (int i = 0; i < N; i++) G[q][i] = rnd();
    }
    long CM[64]; mp_limb_t EV[64]; int OK[64], DF[64]; long PM[64][64];
#pragma omp parallel for schedule(dynamic)
    for (int q = 0; q < NJ; q++) OK[q] = line_disc(A0[q], G[q], CM + q, EV + q, PM[q], DF + q);
    long base = -1;
    for (int q = 0; q < NJ; q++) {
        int k = KJ[q];
        mp_limb_t cc[64];
        for (int j = 2; j < N; j++) cc[j - 2] = nmod_sub(A0[q][j], A0[q][0], MOD);
        if (k == 0 && OK[q]) base = CM[q];
        fprintf(fo, "N=%d M=%d base point %s: line ok %d, full degree %d, order of u=0: %ld", N, M2,
                k ? "on Z_k" : "generic in H", OK[q], DF[q], CM[q]);
        if (k) {
            fprintf(fo, " (k=%d; Hank_k=%s, det Gamma_k=%s, Hank_(k-1)=%s, Hank_(k+1)=%s, det Gamma'_k=%s,"
                    " shifted Hankel=%s; predicted excess %d)",
                    k, hank(cc, M2, k) ? "nonzero" : "0", gamma_det(cc, M2, k, 0) ? "nonzero" : "0",
                    (k == 1 || hank(cc, M2, k - 1)) ? "nonzero" : "0",
                    hank(cc, M2, k + 1) ? "nonzero" : "0", gamma_det(cc, M2, k, 1) ? "nonzero" : "0",
                    hank_shift(cc, M2, k) ? "nonzero" : "0", 4 * M2 - 4 * k - 2);
            if (base >= 0) fprintf(fo, "; observed excess %ld", CM[q] - base);
        }
        fprintf(fo, "\n");
        fflush(fo);
    }
    free(BETA);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 4) { fprintf(stderr, "usage: %s seed OUT.txt N1 [N2 ...]\n", argv[0]); return 2; }
    rng_state = strtoull(argv[1], NULL, 10);
    FILE *fo = fopen(argv[2], "w");
    if (!fo) { perror(argv[2]); return 1; }
    for (int i = 3; i < argc; i++) {
        N = atoi(argv[i]);
        if (run_one(fo)) { fclose(fo); return 1; }
    }
    fclose(fo);
    return 0;
}
