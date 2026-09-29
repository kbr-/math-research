/* The non-collision Wronskian discriminant restricted to a collision hyperplane (30 Sept 2026).
 *
 * Tested statement (restriction lead of the discriminant descent review): for a collision
 * hyperplane H = {a_1 = a_2}, compute Delta_W^nc restricted to a random line in H, report its
 * squarefree decomposition, and test the neck merging factors Hank_k(1/c) (power-sum Hankel
 * determinants of b_j = 1/(a_j - x), x = a_1 = a_2, k = 1..M-1, M = N-2) against it.
 * If the restricted polynomial is reduced, every component of Delta_W^nc meeting H (all of them,
 * since the projective configuration space has dimension N-3 >= 2) is reduced.
 *
 * Method, over F_p, p = 2^61 - 1, with W(a;z) = F(b) prod_i (a_i - z)^theta, b_i = 1/(a_i - z),
 * of z-degree 2 lambda (as in bmd_cube_wronskian_discriminant.c, which checks the controls):
 * the plane a(u,s) = alpha + s beta + u gamma with alpha_1 = alpha_2, beta_1 = beta_2 and
 * gamma_1 != gamma_2, so u = 0 is H. For each s, D_s(u) = Disc_z W(a(u,s);z) is interpolated in u
 * (degree <= 4 lambda (2 lambda - 1)); the factor u^c (c = multiplicity of the collision a_1 = a_2)
 * is removed and E(s) = (D_s / u^c)(0) recorded. E is interpolated in s (two checks), and the
 * collision forms of H, (x - a_j)^(2 c') and (a_j - a_l)^(c'), with c' the per-pair multiplicity
 * found on the generic lines, are removed to their full multiplicity. The rest is Delta_W^nc|_H
 * on the line, up to a constant.
 *
 * Usage: bmd_cube_restricted_discriminant N seed OUT.txt
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

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: %s N seed OUT.txt\n", argv[0]); return 2; }
    N = atoi(argv[1]);
    rng_state = strtoull(argv[2], NULL, 10);
    FILE *fo = fopen(argv[3], "w");
    if (!fo) { perror(argv[3]); return 1; }
    P = 2305843009213693951UL;
    nmod_init(&MOD, P);
    R = (int)binom_small(N, 2);
    LAM = 3 * (int)binom_small(N, 4);
    if ((4 * LAM) % N) { fprintf(stderr, "theta not integral\n"); return 1; }
    THETA = 4 * LAM / N;
    BETA = malloc(sizeof(mp_limb_t) * (R + 1));
    {
        mp_limb_t inv2 = nmod_inv(2, MOD), c = 1, mh = nmod_neg(nmod_mul(3, inv2, MOD), MOD);
        BETA[0] = 1;
        for (int m = 1; m <= R; m++) {
            c = nmod_mul(c, nmod_mul(nmod_sub(mh, (mp_limb_t)(m - 1), MOD), nmod_inv((mp_limb_t)m, MOD), MOD), MOD);
            BETA[m] = c;
        }
    }
    int M2 = N - 2;
    mp_limb_t *alpha = malloc(sizeof(mp_limb_t) * N), *beta = malloc(sizeof(mp_limb_t) * N), *gam = malloc(sizeof(mp_limb_t) * N);
    for (int i = 0; i < N; i++) { alpha[i] = rnd(); beta[i] = rnd(); gam[i] = rnd(); }
    alpha[1] = alpha[0]; beta[1] = beta[0];
    const long DD = 4L * LAM * (2L * LAM - 1);
    long NS = DD + 8;
    int NPAIR = R;
    mp_limb_t *S = malloc(sizeof(mp_limb_t) * NS), *EV = malloc(sizeof(mp_limb_t) * NS), *HV = malloc(sizeof(mp_limb_t) * NS * M2);
    long *CM = malloc(sizeof(long) * NS), *PM = malloc(sizeof(long) * NS * NPAIR);
    int *OK = calloc(NS, sizeof(int)), *DF = calloc(NS, sizeof(int));
    for (long t = 0; t < NS; t++) S[t] = rnd();
    fprintf(fo, "N=%d lambda=%d theta=%d s-values=%ld u-degree bound=%ld threads=%d\n", N, LAM, THETA, NS, DD, omp_get_max_threads());
    fflush(fo);
#pragma omp parallel for schedule(dynamic)
    for (long t = 0; t < NS; t++) {
        mp_limb_t a0[64], cc[64];
        for (int i = 0; i < N; i++) a0[i] = nmod_add(alpha[i], nmod_mul(S[t], beta[i], MOD), MOD);
        OK[t] = line_disc(a0, gam, CM + t, EV + t, PM + t * NPAIR, DF + t);
        for (int j = 2; j < N; j++) cc[j - 2] = nmod_sub(a0[j], a0[0], MOD);
        for (int k = 1; k <= M2 - 1; k++) HV[t * M2 + k] = hank(cc, M2, k);
    }
    long nok = 0, cmin = 1L << 40, cmax = -1, pmin = 1L << 40, pmax = -1, nfull = 0;
    for (long t = 0; t < NS; t++) {
        if (!OK[t]) continue;
        nok++; nfull += DF[t];
        if (CM[t] < cmin) cmin = CM[t];
        if (CM[t] > cmax) cmax = CM[t];
        for (int q = 0; q < NPAIR; q++) if (PM[t * NPAIR + q] >= 0) {
            if (PM[t * NPAIR + q] < pmin) pmin = PM[t * NPAIR + q];
            if (PM[t * NPAIR + q] > pmax) pmax = PM[t * NPAIR + q];
        }
    }
    fprintf(fo, "lines ok=%ld of %ld, full u-degree on %ld; multiplicity of H on the lines: min=%ld max=%ld; other pairs: min=%ld max=%ld\n",
            nok, NS, nfull, cmin, cmax, pmin, pmax);
    fflush(fo);
    if (nok != NS || cmin != cmax || pmin != pmax) { fprintf(fo, "inconsistent lines; stop\n"); fclose(fo); return 1; }
    long cp = pmin;
    nmod_poly_t Epol, lin, qq, rr, Ed, Eg;
    nmod_poly_init(Epol, P); nmod_poly_init(lin, P); nmod_poly_init(qq, P); nmod_poly_init(rr, P);
    nmod_poly_init(Ed, P); nmod_poly_init(Eg, P);
    nmod_poly_interpolate_nmod_vec_fast(Epol, S, EV, NS - 2);
    int check = nmod_poly_evaluate_nmod(Epol, S[NS - 2]) == EV[NS - 2] && nmod_poly_evaluate_nmod(Epol, S[NS - 1]) == EV[NS - 1];
    fprintf(fo, "E(s): degree %ld, interpolation checks %s\n", nmod_poly_degree(Epol), check ? "pass" : "FAIL");
    if (!check) { fclose(fo); return 1; }
    /* collision forms of H along the s-line: x - a_j (pairs (1,j), (2,j) coincide) and a_j - a_l */
    long removed = 0;
    for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++) {
            if (i == 0 && j == 1) continue;
            if (i == 1) continue; /* (2,j) coincides with (1,j) on H; counted through the exponent below */
            mp_limb_t db = nmod_sub(beta[i], beta[j], MOD);
            mp_limb_t sij = nmod_neg(nmod_mul(nmod_sub(alpha[i], alpha[j], MOD), nmod_inv(db, MOD), MOD), MOD);
            long target = (i == 0) ? 2 * cp : cp, m = 0;
            nmod_poly_zero(lin); nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(sij, MOD));
            while (nmod_poly_degree(Epol) > 0 && nmod_poly_evaluate_nmod(Epol, sij) == 0) { nmod_poly_divrem(qq, rr, Epol, lin); nmod_poly_set(Epol, qq); m++; }
            fprintf(fo, "collision form (%d,%d) on H: multiplicity %ld (full %ld)\n", i + 1, j + 1, m, target);
            removed += m;
        }
    long degR = nmod_poly_degree(Epol);
    nmod_poly_derivative(Ed, Epol);
    nmod_poly_gcd(Eg, Epol, Ed);
    fprintf(fo, "Delta_nc|_H on the line: degree %ld, gcd with derivative degree %ld, squarefree %s\n", degR,
            nmod_poly_degree(Eg), nmod_poly_degree(Eg) == 0 ? "yes" : "NO");
    nmod_poly_factor_t sqf; nmod_poly_factor_init(sqf);
    nmod_poly_factor_squarefree(sqf, Epol);
    for (long f = 0; f < sqf->num; f++)
        fprintf(fo, "squarefree part: exponent=%ld degree=%ld\n", sqf->exp[f], nmod_poly_degree(sqf->p + f));
    /* Hankel merging factors: numerator polynomials in s, interpolated from the values times prod c^(2k) */
    for (int k = 1; k <= M2 - 1; k++) {
        mp_limb_t *hv = malloc(sizeof(mp_limb_t) * NS);
        for (long t = 0; t < NS; t++) {
            mp_limb_t pr = 1;
            for (int j = 2; j < N; j++) {
                mp_limb_t cj = nmod_sub(nmod_add(alpha[j], nmod_mul(S[t], beta[j], MOD), MOD),
                                        nmod_add(alpha[0], nmod_mul(S[t], beta[0], MOD), MOD), MOD);
                pr = nmod_mul(pr, nmod_pow_ui(cj, 2 * k, MOD), MOD);
            }
            hv[t] = nmod_mul(HV[t * M2 + k], pr, MOD);
        }
        nmod_poly_t Hp, G, Hq; nmod_poly_init(Hp, P); nmod_poly_init(G, P); nmod_poly_init(Hq, P);
        nmod_poly_interpolate_nmod_vec_fast(Hp, S, hv, NS);
        /* remove collision-form factors from Hp */
        nmod_poly_gcd(G, Hp, Epol);
        long e = 0;
        if (nmod_poly_degree(G) > 0) {
            nmod_poly_set(Hq, Epol);
            while (1) { nmod_poly_divrem(qq, rr, Hq, G); if (!nmod_poly_is_zero(rr)) break; nmod_poly_set(Hq, qq); e++; }
        }
        fprintf(fo, "Hank_%d numerator: degree %ld; gcd with Delta_nc|_H degree %ld; that gcd divides it to exponent %ld\n",
                k, nmod_poly_degree(Hp), nmod_poly_degree(G), e);
        nmod_poly_clear(Hp); nmod_poly_clear(G); nmod_poly_clear(Hq); free(hv);
    }
    fclose(fo);
    return 0;
}
