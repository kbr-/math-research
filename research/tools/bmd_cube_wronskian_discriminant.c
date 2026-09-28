/* Discriminant of the quadratic-series Wronskian covariant along a line of configurations.
 *
 * Tested statement (conj:cube-wronskian-discriminant-squarefree, finite instance).  Work over
 * F_p, p = 2^61 - 1, with N >= 5 finite branch points a_1..a_N and the mark at infinity.  Put
 * R = C(N,2), lambda = 3 C(N,4), theta = 4 lambda / N, and
 *     H_k(X,Y) = [T^k] ((1+XT)(1+YT))^{-3/2},   A(a) = (H_k(a_i,a_j))_{i<j, 0<=k<R}  (R x R).
 * The boundary polynomial is F(a) = det A(a) / prod_{i<j}(a_i-a_j)^{N-2}, of degree lambda
 * (checked below by interpolation, not assumed).  Moving the mark to z by b_i = 1/(a_i - z)
 * gives the base Wronskian polynomial W_a(z) = F(b) prod_i (a_i - z)^theta, expected of exact
 * degree 2 lambda in z with no root at any a_i (both checked).  Along the affine line
 * a_i(u) = alpha_i + u beta_i the discriminant D(u) = Disc_z W_{a(u)}(z) has degree at most
 * 4 lambda (2 lambda - 1).  The program removes every collision factor (u - u_ij), u_ij the root
 * of a_i(u) = a_j(u), to its full multiplicity, and tests whether the remaining part D_nc has
 * full degree and is squarefree.  Full degree and squarefreeness over F_p imply that the part of
 * the characteristic-zero discriminant invariant prime to the collision forms is squarefree.
 *
 * The squarefree decomposition of D_nc is reported, and repeated factors are dumped.
 *
 * Controls: F(a(u)) must interpolate to degree <= lambda and be squarefree (proved boundary
 * squarefreeness); each W row must have degree exactly 2 lambda; the coefficient of z^k must have
 * u-degree <= 3 lambda - k; the leading coefficient of W must be a constant multiple of F(a);
 * W must not vanish at z = a_i; D must interpolate to degree <= 4 lambda (2 lambda - 1).
 *
 * Usage: bmd_cube_wronskian_discriminant N seed OUT.json
 */
#include <flint/flint.h>
#include <flint/nmod_vec.h>
#include <flint/nmod_poly.h>
#include <flint/nmod_mat.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static nmod_t MOD;
static mp_limb_t P;
static int N, R, LAM, THETA;
static mp_limb_t *BETA; /* BETA[m] = binom(-3/2, m) mod p */

static unsigned long long rng_state;
static mp_limb_t rnd(void)
{
    /* splitmix64, reduced mod p; deterministic from the seed */
    unsigned long long z = (rng_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    z ^= z >> 31;
    return (mp_limb_t)(z % P);
}

/* F(b) = det(H_k(b_i,b_j)) / prod (b_i - b_j)^{N-2}; px, py scratch of length R. */
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
                for (int m = 0; m <= k; m++)
                    acc += (unsigned __int128)px[m] * py[k - m];
                nmod_mat_entry(M, row, k) = (mp_limb_t)(acc % P);
            }
            row++;
        }
    mp_limb_t d = nmod_mat_det(M);
    mp_limb_t den = 1;
    for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++)
            den = nmod_mul(den, nmod_sub(b[i], b[j], MOD), MOD);
    den = nmod_pow_ui(den, N - 2, MOD);
    return nmod_mul(d, nmod_inv(den, MOD), MOD);
}

/* W at (a, z): F(b) prod (a_i - z)^theta with b_i = 1/(a_i - z). */
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

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "usage: %s N seed OUT.json\n", argv[0]);
        return 2;
    }
    N = atoi(argv[1]);
    rng_state = strtoull(argv[2], NULL, 10);
    const char *out = argv[3];
    P = 2305843009213693951UL; /* 2^61 - 1, prime */
    nmod_init(&MOD, P);
    R = (int)binom_small(N, 2);
    LAM = 3 * (int)binom_small(N, 4);
    if ((4 * LAM) % N) { fprintf(stderr, "theta not integral\n"); return 1; }
    THETA = 4 * LAM / N;
    const long DW = 2L * LAM;                 /* z-degree of W */
    const long DU = 3L * LAM;                 /* u-degree bound of W */
    const long DD = 4L * LAM * (2L * LAM - 1); /* u-degree bound of D */
    const int SL = 4;                         /* slack points for degree checks */
    printf("N=%d R=%d lambda=%d theta=%d degW=%ld degU<=%ld degD<=%ld threads=%d\n", N, R, LAM,
           THETA, DW, DU, DD, omp_get_max_threads());
    fflush(stdout);

    BETA = malloc(sizeof(mp_limb_t) * (R + 1));
    {
        mp_limb_t inv2 = nmod_inv(2, MOD), c = 1;
        mp_limb_t mh = nmod_neg(nmod_mul(3, inv2, MOD), MOD); /* -3/2 */
        BETA[0] = 1;
        for (int m = 1; m <= R; m++) {
            mp_limb_t num = nmod_sub(mh, (mp_limb_t)(m - 1), MOD);
            c = nmod_mul(c, nmod_mul(num, nmod_inv((mp_limb_t)m, MOD), MOD), MOD);
            BETA[m] = c;
        }
    }

    mp_limb_t *alpha = malloc(sizeof(mp_limb_t) * N), *beta = malloc(sizeof(mp_limb_t) * N);
    for (int i = 0; i < N; i++) { alpha[i] = rnd(); beta[i] = rnd(); }
    int NPAIR = R;
    mp_limb_t *uij = malloc(sizeof(mp_limb_t) * NPAIR);
    {
        int t = 0;
        for (int i = 0; i < N; i++)
            for (int j = i + 1; j < N; j++, t++) {
                mp_limb_t db = nmod_sub(beta[i], beta[j], MOD);
                if (!db) { fprintf(stderr, "degenerate line\n"); return 1; }
                uij[t] = nmod_neg(nmod_mul(nmod_sub(alpha[i], alpha[j], MOD),
                                           nmod_inv(db, MOD), MOD), MOD);
            }
    }

    /* ---- control: F(a(u)) degree <= lambda and squarefree ---- */
    long NF = LAM + 1 + SL;
    mp_limb_t *fu = malloc(sizeof(mp_limb_t) * NF), *fv = malloc(sizeof(mp_limb_t) * NF);
    for (long g = 0; g < NF; g++) fu[g] = rnd();
#pragma omp parallel
    {
        nmod_mat_t M; nmod_mat_init(M, R, R, P);
        mp_limb_t *px = malloc(sizeof(mp_limb_t) * R), *py = malloc(sizeof(mp_limb_t) * R);
        mp_limb_t *a = malloc(sizeof(mp_limb_t) * N);
#pragma omp for schedule(dynamic)
        for (long g = 0; g < NF; g++) {
            for (int i = 0; i < N; i++) a[i] = nmod_add(alpha[i], nmod_mul(fu[g], beta[i], MOD), MOD);
            fv[g] = Fval(a, M, px, py);
        }
        nmod_mat_clear(M); free(px); free(py); free(a);
    }
    nmod_poly_t Fpol, Fd, Fg;
    nmod_poly_init(Fpol, P); nmod_poly_init(Fd, P); nmod_poly_init(Fg, P);
    nmod_poly_interpolate_nmod_vec_fast(Fpol, fu, fv, NF);
    long degF = nmod_poly_degree(Fpol);
    nmod_poly_derivative(Fd, Fpol);
    nmod_poly_gcd(Fg, Fpol, Fd);
    long degFg = nmod_poly_degree(Fg);
    printf("control F: deg=%ld (expect %d) gcd(F,F')deg=%ld\n", degF, LAM, degFg);
    fflush(stdout);

    /* ---- W on a grid ---- */
    long GU = DU + 1 + SL, GZ = DW + 1 + SL;
    mp_limb_t *U = malloc(sizeof(mp_limb_t) * GU), *Z = malloc(sizeof(mp_limb_t) * GZ);
    for (long g = 0; g < GU; g++) U[g] = rnd();
    for (long h = 0; h < GZ; h++) Z[h] = rnd();
    mp_limb_t *Wg = malloc(sizeof(mp_limb_t) * GU * GZ);
#pragma omp parallel
    {
        nmod_mat_t M; nmod_mat_init(M, R, R, P);
        mp_limb_t *px = malloc(sizeof(mp_limb_t) * R), *py = malloc(sizeof(mp_limb_t) * R);
        mp_limb_t *a = malloc(sizeof(mp_limb_t) * N), *b = malloc(sizeof(mp_limb_t) * N);
#pragma omp for schedule(dynamic) collapse(2)
        for (long g = 0; g < GU; g++)
            for (long h = 0; h < GZ; h++) {
                for (int i = 0; i < N; i++)
                    a[i] = nmod_add(alpha[i], nmod_mul(U[g], beta[i], MOD), MOD);
                Wg[g * GZ + h] = Wval(a, Z[h], M, px, py, b);
            }
        nmod_mat_clear(M); free(px); free(py); free(a); free(b);
    }
    printf("grid done: %ld x %ld evaluations\n", GU, GZ);
    fflush(stdout);

    /* rows: interpolate in z, check exact degree 2 lambda and no root at a_i */
    mp_limb_t *coef = malloc(sizeof(mp_limb_t) * GU * (DW + 1));
    long bad_row_deg = 0, root_at_branch = 0;
    double lc_ratio_bad = 0;
    mp_limb_t lc_ratio = 0;
    {
        nmod_poly_t w; nmod_poly_init(w, P);
        mp_limb_t *a = malloc(sizeof(mp_limb_t) * N);
        nmod_mat_t M; nmod_mat_init(M, R, R, P);
        mp_limb_t *px = malloc(sizeof(mp_limb_t) * R), *py = malloc(sizeof(mp_limb_t) * R);
        for (long g = 0; g < GU; g++) {
            nmod_poly_interpolate_nmod_vec_fast(w, Z, Wg + g * GZ, GZ);
            if (nmod_poly_degree(w) != DW) bad_row_deg++;
            for (long k = 0; k <= DW; k++) coef[g * (DW + 1) + k] = nmod_poly_get_coeff_ui(w, k);
            for (int i = 0; i < N; i++) {
                a[i] = nmod_add(alpha[i], nmod_mul(U[g], beta[i], MOD), MOD);
            }
            if (g < 8) {
                for (int i = 0; i < N; i++)
                    if (nmod_poly_evaluate_nmod(w, a[i]) == 0) root_at_branch++;
                mp_limb_t f = Fval(a, M, px, py);
                mp_limb_t r = nmod_mul(nmod_poly_get_coeff_ui(w, DW), nmod_inv(f, MOD), MOD);
                if (g == 0) lc_ratio = r;
                else if (r != lc_ratio) lc_ratio_bad += 1;
            }
        }
        nmod_poly_clear(w); free(a); nmod_mat_clear(M); free(px); free(py);
    }
    printf("rows: bad degree=%ld roots at branch points=%ld lc/F ratio constant=%s\n", bad_row_deg,
           root_at_branch, lc_ratio_bad == 0 ? "yes" : "NO");
    fflush(stdout);

    /* columns: interpolate each z-coefficient in u, check u-degree <= 3 lambda - k */
    nmod_poly_struct *ck = malloc(sizeof(nmod_poly_struct) * (DW + 1));
    long bad_col_deg = 0;
    {
        mp_limb_t *col = malloc(sizeof(mp_limb_t) * GU);
        for (long k = 0; k <= DW; k++) {
            for (long g = 0; g < GU; g++) col[g] = coef[g * (DW + 1) + k];
            nmod_poly_init(ck + k, P);
            nmod_poly_interpolate_nmod_vec_fast(ck + k, U, col, GU);
            if (nmod_poly_degree(ck + k) > DU - k) bad_col_deg++;
        }
        free(col);
    }
    printf("columns: coefficients exceeding u-degree 3lambda-k: %ld\n", bad_col_deg);
    fflush(stdout);

    /* ---- D(u) at DD + 1 + SL good points ---- */
    long ND = DD + 1 + SL, NC = ND + ND / 16 + 64;
    mp_limb_t *cu = malloc(sizeof(mp_limb_t) * NC), *cv = malloc(sizeof(mp_limb_t) * NC);
    char *ok = calloc(NC, 1);
    for (long t = 0; t < NC; t++) cu[t] = rnd();
#pragma omp parallel
    {
        nmod_poly_t w, wd; nmod_poly_init(w, P); nmod_poly_init(wd, P);
#pragma omp for schedule(dynamic, 64)
        for (long t = 0; t < NC; t++) {
            int coll = 0;
            for (int q = 0; q < NPAIR; q++) if (cu[t] == uij[q]) coll = 1;
            if (coll) continue;
            nmod_poly_zero(w);
            for (long k = 0; k <= DW; k++)
                nmod_poly_set_coeff_ui(w, k, nmod_poly_evaluate_nmod(ck + k, cu[t]));
            if (nmod_poly_degree(w) != DW) continue; /* leading coefficient F(a) vanished */
            nmod_poly_derivative(wd, w);
            mp_limb_t res = nmod_poly_resultant(w, wd);
            cv[t] = nmod_mul(res, nmod_inv(*nmod_poly_lead(w), MOD), MOD);
            ok[t] = 1;
        }
        nmod_poly_clear(w); nmod_poly_clear(wd);
    }
    long got = 0;
    for (long t = 0; t < NC && got < ND; t++)
        if (ok[t]) { cu[got] = cu[t]; cv[got] = cv[t]; got++; }
    if (got < ND) { fprintf(stderr, "not enough good points\n"); return 1; }
    nmod_poly_t D; nmod_poly_init(D, P);
    nmod_poly_interpolate_nmod_vec_fast(D, cu, cv, ND);
    long degD = nmod_poly_degree(D);
    printf("D: deg=%ld (bound %ld)\n", degD, DD);
    fflush(stdout);

    /* remove collision factors */
    long *mult = calloc(NPAIR, sizeof(long));
    nmod_poly_t lin, qq, rr;
    nmod_poly_init(lin, P); nmod_poly_init(qq, P); nmod_poly_init(rr, P);
    long collsum = 0;
    for (int q = 0; q < NPAIR; q++) {
        nmod_poly_zero(lin);
        nmod_poly_set_coeff_ui(lin, 1, 1);
        nmod_poly_set_coeff_ui(lin, 0, nmod_neg(uij[q], MOD));
        while (nmod_poly_degree(D) > 0 && nmod_poly_evaluate_nmod(D, uij[q]) == 0) {
            nmod_poly_divrem(qq, rr, D, lin);
            nmod_poly_set(D, qq);
            mult[q]++;
        }
        collsum += mult[q];
    }
    long degDnc = nmod_poly_degree(D);
    nmod_poly_t Dd, Dg;
    nmod_poly_init(Dd, P); nmod_poly_init(Dg, P);
    nmod_poly_derivative(Dd, D);
    nmod_poly_gcd(Dg, D, Dd);
    long degDg = nmod_poly_degree(Dg);
    long mmin = mult[0], mmax = mult[0];
    for (int q = 1; q < NPAIR; q++) { if (mult[q] < mmin) mmin = mult[q]; if (mult[q] > mmax) mmax = mult[q]; }
    printf("collision multiplicity per pair: min=%ld max=%ld total=%ld\n", mmin, mmax, collsum);
    printf("D_nc: deg=%ld full_degree=%s gcd(D_nc,D_nc')deg=%ld squarefree=%s\n", degDnc,
           (degD == DD) ? "yes" : "no", degDg, degDg == 0 ? "yes" : "NO");
    /* squarefree decomposition of D_nc; repeated factors are dumped for identification */
    nmod_poly_factor_t sqf;
    nmod_poly_factor_init(sqf);
    nmod_poly_factor_squarefree(sqf, D);
    for (long f = 0; f < sqf->num; f++)
        printf("squarefree part: exponent=%ld degree=%ld\n", sqf->exp[f],
               nmod_poly_degree(sqf->p + f));
    fflush(stdout);

    FILE *fo = fopen(out, "w");
    if (!fo) { perror(out); return 1; }
    fprintf(fo, "{\n  \"program\": \"bmd_cube_wronskian_discriminant.c\",\n");
    fprintf(fo, "  \"N\": %d, \"seed\": \"%s\", \"p\": \"%lu\",\n", N, argv[2], P);
    fprintf(fo, "  \"R\": %d, \"lambda\": %d, \"theta\": %d,\n", R, LAM, THETA);
    fprintf(fo, "  \"control_F_degree\": %ld, \"control_F_gcd_degree\": %ld,\n", degF, degFg);
    fprintf(fo, "  \"grid\": [%ld, %ld], \"rows_with_wrong_z_degree\": %ld,\n", GU, GZ, bad_row_deg);
    fprintf(fo, "  \"W_roots_at_branch_points_first8rows\": %ld, \"lc_over_F_constant\": %s,\n",
            root_at_branch, lc_ratio_bad == 0 ? "true" : "false");
    fprintf(fo, "  \"coefficients_exceeding_u_degree\": %ld,\n", bad_col_deg);
    fprintf(fo, "  \"D_degree\": %ld, \"D_degree_bound\": %ld, \"D_points\": %ld,\n", degD, DD, ND);
    fprintf(fo, "  \"collision_multiplicity_min\": %ld, \"collision_multiplicity_max\": %ld,\n", mmin, mmax);
    fprintf(fo, "  \"D_nc_degree\": %ld, \"D_nc_gcd_with_derivative_degree\": %ld,\n", degDnc, degDg);
    fprintf(fo, "  \"D_nc_squarefree\": %s, \"D_full_degree\": %s,\n", degDg == 0 ? "true" : "false",
            degD == DD ? "true" : "false");
    fprintf(fo, "  \"squarefree_decomposition\": [");
    for (long f = 0; f < sqf->num; f++) {
        long df = nmod_poly_degree(sqf->p + f);
        fprintf(fo, "%s\n    {\"exponent\": %ld, \"degree\": %ld", f ? "," : "", sqf->exp[f], df);
        if (sqf->exp[f] > 1) {
            fprintf(fo, ", \"monic_coefficients_low_to_high\": [");
            for (long k = 0; k <= df; k++)
                fprintf(fo, "%s\"%lu\"", k ? ", " : "", nmod_poly_get_coeff_ui(sqf->p + f, k));
            fprintf(fo, "]");
        }
        fprintf(fo, "}");
    }
    fprintf(fo, "\n  ],\n");
    fprintf(fo, "  \"line_alpha\": [");
    for (int i = 0; i < N; i++) fprintf(fo, "%s\"%lu\"", i ? ", " : "", alpha[i]);
    fprintf(fo, "],\n  \"line_beta\": [");
    for (int i = 0; i < N; i++) fprintf(fo, "%s\"%lu\"", i ? ", " : "", beta[i]);
    fprintf(fo, "]\n}\n");
    fclose(fo);
    return 0;
}
