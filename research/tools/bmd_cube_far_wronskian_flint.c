/* Exact far Wronskian determinant of the peeling degeneration over Z (cycle bmd-20260930-zzw).
 *
 * Same space and recursion as research/tools/bmd_cube_far_wronskian.gp: basis functions
 * x^al (1+x)^be p(x), with f^(m) = x^(al-m) (1+x)^(be-m) p_m and
 *   p_{m+1} = (al-m)(1+x) p_m + (be-m) x p_m + x(1+x) p_m'.
 * With q_m = 2^m p_m the recursion is integral:
 *   q_{m+1} = 2(al-m)(1+x) q_m + 2(be-m) x q_m + 2 x(1+x) q_m',
 * and det[q_{i,m}] = 2^(binom(R,2)) det[p_{i,m}].  The program prints det[q] as a PARI/GP polynomial
 * in x, for W_k = primitive part after removing the factors x and 1+x (done in gp).
 * Usage: bmd_cube_far_wronskian_flint OUTDIR e1 l1 [e2 l2 ...]   (writes OUTDIR/det_e_l.gp)
 */
#include <flint/flint.h>
#include <flint/fmpz_poly.h>
#include <flint/fmpz_poly_mat.h>
#include <stdio.h>
#include <stdlib.h>

static int Rn(int n) { return n * (2 * n - 1); }

static int one(int e, int l, const char *outdir);

int main(int argc, char **argv)
{
    if (argc < 4 || argc % 2) { fprintf(stderr, "usage: %s OUTDIR e1 l1 [e2 l2 ...]\n", argv[0]); return 1; }
    for (int a = 2; a + 1 < argc; a += 2)
        if (one(atoi(argv[a]), atoi(argv[a + 1]), argv[1])) return 1;
    return 0;
}

static int one(int e, int l, const char *outdir)
{
    int R = Rn(e + l + 1);
    /* functions: (2*al, 2*be, j) meaning x^al (1+x)^be x^j */
    int (*F)[3] = malloc(sizeof(int[3]) * R), n = 0;
    for (int j = 0; j < Rn(e); j++) { F[n][0] = 0; F[n][1] = 0; F[n][2] = j; n++; }
    F[n][0] = 0; F[n][1] = -6; F[n][2] = 0; n++;
    for (int j = 0; j < Rn(l); j++) { F[n][0] = -2 * (Rn(l) + 2); F[n][1] = 0; F[n][2] = j; n++; }
    for (int j = 0; j < 4 * e; j++) { F[n][0] = 0; F[n][1] = -7; F[n][2] = j; n++; }
    for (int j = 0; j < 4 * l; j++) { F[n][0] = 1 - 8 * l; F[n][1] = -5; F[n][2] = j; n++; }
    for (int j = 0; j < 4 * e * l; j++) { F[n][0] = -7 + 8 * e - 8 * e * l; F[n][1] = 0; F[n][2] = j; n++; }
    if (n != R) { fprintf(stderr, "dimension %d != %d\n", n, R); return 1; }

    fmpz_poly_mat_t M;
    fmpz_poly_mat_init(M, R, R);
    fmpz_poly_t q, t, u, onepx, x, xonepx;
    fmpz_poly_init(q); fmpz_poly_init(t); fmpz_poly_init(u);
    fmpz_poly_init(onepx); fmpz_poly_init(x); fmpz_poly_init(xonepx);
    fmpz_poly_set_coeff_si(onepx, 0, 1); fmpz_poly_set_coeff_si(onepx, 1, 1);
    fmpz_poly_set_coeff_si(x, 1, 1);
    fmpz_poly_mul(xonepx, x, onepx);
    for (int i = 0; i < R; i++) {
        fmpz_poly_zero(q);
        fmpz_poly_set_coeff_si(q, F[i][2], 1);
        for (int m = 0; m < R; m++) {
            fmpz_poly_set(fmpz_poly_mat_entry(M, i, m), q);
            /* q <- (2al - 2m)(1+x) q + (2be - 2m) x q + 2 x(1+x) q' */
            fmpz_poly_mul(t, onepx, q); fmpz_poly_scalar_mul_si(t, t, F[i][0] - 2 * m);
            fmpz_poly_mul(u, x, q); fmpz_poly_scalar_mul_si(u, u, F[i][1] - 2 * m);
            fmpz_poly_add(t, t, u);
            fmpz_poly_derivative(u, q); fmpz_poly_mul(u, u, xonepx); fmpz_poly_scalar_mul_si(u, u, 2);
            fmpz_poly_add(q, t, u);
        }
    }
    fmpz_poly_t D;
    fmpz_poly_init(D);
    fmpz_poly_mat_det(D, M);
    char path[4096];
    snprintf(path, sizeof path, "%s/det_%d_%d.gp", outdir, e, l);
    FILE *fo = fopen(path, "w");
    char *s = fmpz_poly_get_str_pretty(D, "x");
    fprintf(fo, "%s\n", s);
    fclose(fo);
    printf("e = %d, l = %d, R = %d, deg det = %ld\n", e, l, R, fmpz_poly_degree(D));
    fflush(stdout);
    flint_free(s);
    fmpz_poly_mat_clear(M); fmpz_poly_clear(D); free(F);
    fmpz_poly_clear(q); fmpz_poly_clear(t); fmpz_poly_clear(u);
    fmpz_poly_clear(onepx); fmpz_poly_clear(x); fmpz_poly_clear(xonepx);
    return 0;
}
