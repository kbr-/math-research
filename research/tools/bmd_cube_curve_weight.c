/* Weight test along moving-subset curves (lem:cube-moving-subset-curves), cycle bmd-20260930-zzh.
 *
 * V_a = <1, z, ((z-a_i)(z-a_j))^(1/2)>, n = 2 + N(N-1)/2.  Modulo p = 2^61-1:
 *   W^2(z0) = c * det(T(z0))^2 * prod_i (z0-a_i)^(N-1),  T = Taylor matrix of the functions normalized at z0,
 *   F(z) = W^2 prod (z-a_i)^E, a polynomial in (a, z) for E large; Q = F / prod (z-a_i)^(e_i) with the generic
 *   branch orders e_i; weights at non-branch points are half the root multiplicities of Q.
 *   Weight >= 3 somewhere  <=>  Q has a root of multiplicity >= 6 at a non-branch point.
 *
 * Usage:
 *   single N DB E b_1..b_N              (b as num/den)  -> degQ, deg R, Q = c R^2, R squarefree, e_i
 *   curve  N DB E mask s_start count e_1..e_N b_1..b_N
 *          a_i = b_i + s for i in mask; for s = s_start, s_start+1, ... prints
 *          "s A B lcQ" with A = Res_z(Q^(4), Q^(5)), B = Res_z(Q^(3), Q^(5)), lcQ = leading coeff, or "s skip".
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <flint/flint.h>
#include <flint/nmod_vec.h>
#include <flint/nmod_poly.h>
#include <flint/nmod_mat.h>
#include <flint/nmod_poly_factor.h>

static nmod_t MOD;
static mp_limb_t P = 2305843009213693951UL;

static mp_limb_t parse_frac(const char *s) {
    long num, den = 1;
    if (strchr(s, '/')) sscanf(s, "%ld/%ld", &num, &den); else sscanf(s, "%ld", &num);
    mp_limb_t n = num >= 0 ? n_mod2_preinv((mp_limb_t)(num), MOD.n, MOD.ninv) : nmod_neg(n_mod2_preinv((mp_limb_t)(-num), MOD.n, MOD.ninv), MOD);
    mp_limb_t d = den >= 0 ? n_mod2_preinv((mp_limb_t)(den), MOD.n, MOD.ninv) : nmod_neg(n_mod2_preinv((mp_limb_t)(-den), MOD.n, MOD.ninv), MOD);
    return nmod_div(n, d, MOD);
}

static mp_limb_t *HB; /* binom(1/2, k) */

/* F(z0) = det^2 prod (z0-a_i)^(N-1+E) */
static mp_limb_t Fval(int N, const mp_limb_t *a, mp_limb_t z0, int E, nmod_mat_t M, mp_limb_t *pu, mp_limb_t *pv) {
    int n = 2 + N * (N - 1) / 2, r = 2;
    nmod_mat_zero(M);
    nmod_mat_entry(M, 0, 0) = 1;
    nmod_mat_entry(M, 1, 0) = z0; nmod_mat_entry(M, 1, 1) = 1;
    mp_limb_t *inv = malloc(N * sizeof(mp_limb_t)), pr = 1;
    for (int i = 0; i < N; i++) {
        mp_limb_t d = nmod_sub(z0, a[i], MOD);
        if (d == 0) { free(inv); return 0; }
        inv[i] = nmod_inv(d, MOD);
        pr = nmod_mul(pr, nmod_pow_ui(d, N - 1 + E, MOD), MOD);
    }
    for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) {
        /* coefficients of (1 + u T)^(1/2) (1 + v T)^(1/2), u = 1/(z0-a_i) */
        pu[0] = 1; pv[0] = 1;
        for (int k = 1; k < n; k++) { pu[k] = nmod_mul(pu[k - 1], inv[i], MOD); pv[k] = nmod_mul(pv[k - 1], inv[j], MOD); }
        for (int k = 0; k < n; k++) {
            mp_limb_t s = 0;
            for (int l = 0; l <= k; l++)
                s = nmod_add(s, nmod_mul(nmod_mul(HB[l], pu[l], MOD), nmod_mul(HB[k - l], pv[k - l], MOD), MOD), MOD);
            nmod_mat_entry(M, r, k) = s;
        }
        r++;
    }
    free(inv);
    mp_limb_t d = nmod_mat_det(M);
    return nmod_mul(nmod_mul(d, d, MOD), pr, MOD);
}

/* interpolate F with degree bound DB; returns 1 if the 3 check points agree */
static int Fpoly(nmod_poly_t F, int N, const mp_limb_t *a, int DB, int E) {
    int n = 2 + N * (N - 1) / 2;
    nmod_mat_t M; nmod_mat_init(M, n, n, P);
    mp_limb_t *pu = malloc(n * sizeof(mp_limb_t)), *pv = malloc(n * sizeof(mp_limb_t));
    int m = DB + 1;
    mp_limb_t *xs = malloc((m + 3) * sizeof(mp_limb_t)), *ys = malloc((m + 3) * sizeof(mp_limb_t));
    for (int k = 0; k < m + 3; k++) {
        xs[k] = n_mod2_preinv(7919UL * (k + 1) + 13, MOD.n, MOD.ninv);
        ys[k] = Fval(N, a, xs[k], E, M, pu, pv);
    }
    nmod_poly_interpolate_nmod_vec_fast(F, xs, ys, m);
    int ok = 1;
    for (int k = m; k < m + 3; k++) if (nmod_poly_evaluate_nmod(F, xs[k]) != ys[k]) ok = 0;
    free(xs); free(ys); free(pu); free(pv); nmod_mat_clear(M);
    return ok;
}

static int strip(nmod_poly_t Q, mp_limb_t root) {
    int c = 0; nmod_poly_t q, r, lin; nmod_poly_init(q, P); nmod_poly_init(r, P); nmod_poly_init(lin, P);
    nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(root, MOD));
    while (!nmod_poly_is_zero(Q)) {
        nmod_poly_divrem(q, r, Q, lin);
        if (!nmod_poly_is_zero(r)) break;
        nmod_poly_swap(Q, q); c++;
    }
    nmod_poly_clear(q); nmod_poly_clear(r); nmod_poly_clear(lin);
    return c;
}

static void strip_fixed(nmod_poly_t Q, mp_limb_t root, int e) {
    nmod_poly_t lin, q, r; nmod_poly_init(lin, P); nmod_poly_init(q, P); nmod_poly_init(r, P);
    nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(root, MOD));
    for (int k = 0; k < e; k++) {
        nmod_poly_divrem(q, r, Q, lin);
        if (!nmod_poly_is_zero(r)) { fprintf(stderr, "fixed strip failed\n"); exit(2); }
        nmod_poly_swap(Q, q);
    }
    nmod_poly_clear(q); nmod_poly_clear(r); nmod_poly_clear(lin);
}

static int run(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 1; }
    const char *mode = argv[1];
    int N = atoi(argv[2]), DB = atoi(argv[3]), E = atoi(argv[4]);
    int n = 2 + N * (N - 1) / 2;
    HB = malloc(n * sizeof(mp_limb_t)); HB[0] = 1;
    mp_limb_t half = nmod_inv(2, MOD);
    for (int k = 1; k < n; k++) {
        mp_limb_t f = nmod_sub(half, n_mod2_preinv((mp_limb_t)(k - 1), MOD.n, MOD.ninv), MOD);
        HB[k] = nmod_div(nmod_mul(HB[k - 1], f, MOD), n_mod2_preinv((mp_limb_t)(k), MOD.n, MOD.ninv), MOD);
    }
    mp_limb_t *b = malloc(N * sizeof(mp_limb_t)), *a = malloc(N * sizeof(mp_limb_t));
    nmod_poly_t F, D1, G, R2, Rs;
    nmod_poly_init(F, P); nmod_poly_init(D1, P); nmod_poly_init(G, P); nmod_poly_init(R2, P); nmod_poly_init(Rs, P);
    if (!strcmp(mode, "single")) {
        for (int i = 0; i < N; i++) b[i] = parse_frac(argv[5 + i]);
        if (!Fpoly(F, N, b, DB, E)) { printf("check points FAIL (raise DB)\n"); return 0; }
        printf("degF %ld\n", nmod_poly_degree(F));
        printf("e");
        for (int i = 0; i < N; i++) printf(" %d", strip(F, b[i]));
        printf("\n");
        /* F is now Q */
        nmod_poly_derivative(D1, F); nmod_poly_gcd(G, F, D1);
        nmod_poly_mul(R2, G, G);
        nmod_poly_scalar_mul_nmod(R2, R2, nmod_div(nmod_poly_get_coeff_ui(F, nmod_poly_degree(F)), nmod_poly_get_coeff_ui(R2, nmod_poly_degree(R2)), MOD));
        int sq = nmod_poly_equal(R2, F);
        nmod_poly_derivative(D1, G); nmod_poly_gcd(Rs, G, D1);
        printf("degQ %ld degR %ld Q=cR^2 %d Rsquarefree %d\n", nmod_poly_degree(F), nmod_poly_degree(G), sq, nmod_poly_degree(Rs) == 0);
        return 0;
    }
    if (!strcmp(mode, "sdeg")) {
        /* sdeg N DB E mask K e_1..e_N b_1..b_N : degree in s of Q(s, z*) at two fixed z*, from K+3 samples */
        const char *mask = argv[5];
        long K = atol(argv[6]);
        int *e = malloc(N * sizeof(int));
        for (int i = 0; i < N; i++) e[i] = atoi(argv[7 + i]);
        for (int i = 0; i < N; i++) b[i] = parse_frac(argv[7 + N + i]);
        for (int zi = 0; zi < 2; zi++) {
            mp_limb_t zs = n_mod2_preinv(zi ? 987654321UL : 55555UL, MOD.n, MOD.ninv);
            mp_limb_t *xs = malloc((K + 3) * sizeof(mp_limb_t)), *ys = malloc((K + 3) * sizeof(mp_limb_t));
            #pragma omp parallel for schedule(dynamic, 8)
            for (long t = 0; t < K + 3; t++) {
                mp_limb_t *aa = malloc(N * sizeof(mp_limb_t)), *pu = malloc(n * sizeof(mp_limb_t)), *pv = malloc(n * sizeof(mp_limb_t));
                nmod_mat_t M; nmod_mat_init(M, n, n, P);
                mp_limb_t s = n_mod2_preinv((mp_limb_t)(t + 1000), MOD.n, MOD.ninv), v;
                for (int i = 0; i < N; i++) aa[i] = mask[i] == '1' ? nmod_add(b[i], s, MOD) : b[i];
                v = Fval(N, aa, zs, E, M, pu, pv);
                for (int i = 0; i < N; i++) v = nmod_div(v, nmod_pow_ui(nmod_sub(zs, aa[i], MOD), e[i], MOD), MOD);
                xs[t] = s; ys[t] = v;
                nmod_mat_clear(M); free(aa); free(pu); free(pv);
            }
            nmod_poly_t PS; nmod_poly_init(PS, P);
            nmod_poly_interpolate_nmod_vec_fast(PS, xs, ys, K);
            int chk = 1;
            for (long k = K; k < K + 3; k++) if (nmod_poly_evaluate_nmod(PS, xs[k]) != ys[k]) chk = 0;
            printf("deg_s Q(s, z*) %ld (checks %s)\n", nmod_poly_degree(PS), chk ? "pass" : "FAIL");
            nmod_poly_clear(PS); free(xs); free(ys);
        }
        return 0;
    }
    if (!strcmp(mode, "at")) {
        /* at N DB E mask s0 b_1..b_N (s0 a residue mod p): Q, R at a = b + s0 mask; prints deg R, degrees of
           gcd(R, R') and gcd(R, R', R''), whether some pairing of the points into pairs is in involution
           (N = 6: the three quadratics (z-a_i)(z-a_j) linearly dependent), and deg Q drop. */
        const char *mask = argv[5];
        mp_limb_t s0 = n_mod2_preinv(strtoul(argv[6], 0, 10), MOD.n, MOD.ninv);
        for (int i = 0; i < N; i++) b[i] = parse_frac(argv[7 + i]);
        for (int i = 0; i < N; i++) a[i] = mask[i] == '1' ? nmod_add(b[i], s0, MOD) : b[i];
        if (!Fpoly(F, N, a, DB, E)) { printf("check points FAIL\n"); return 0; }
        int tot = 0;
        printf("e");
        for (int i = 0; i < N; i++) { int c = strip(F, a[i]); tot += c; printf(" %d", c); }
        printf("  degQ %ld\n", nmod_poly_degree(F));
        nmod_poly_derivative(D1, F); nmod_poly_gcd(G, F, D1);
        nmod_poly_derivative(D1, G); nmod_poly_gcd(Rs, G, D1);
        nmod_poly_t R3; nmod_poly_init(R3, P);
        nmod_poly_derivative(D1, D1); nmod_poly_gcd(R3, Rs, D1);
        printf("degR %ld deg gcd(R,R') %ld deg gcd(R,R',R'') %ld\n", nmod_poly_degree(G), nmod_poly_degree(Rs), nmod_poly_degree(R3));
        if (N == 6) {
            int found = 0;
            int pr[15][6] = {{0,1,2,3,4,5},{0,1,2,4,3,5},{0,1,2,5,3,4},{0,2,1,3,4,5},{0,2,1,4,3,5},{0,2,1,5,3,4},
                {0,3,1,2,4,5},{0,3,1,4,2,5},{0,3,1,5,2,4},{0,4,1,2,3,5},{0,4,1,3,2,5},{0,4,1,5,2,3},
                {0,5,1,2,3,4},{0,5,1,3,2,4},{0,5,1,4,2,3}};
            for (int k = 0; k < 15; k++) {
                nmod_mat_t M; nmod_mat_init(M, 3, 3, P);
                for (int r = 0; r < 3; r++) {
                    mp_limb_t x = a[pr[k][2*r]], y = a[pr[k][2*r+1]];
                    nmod_mat_entry(M, r, 0) = 1; nmod_mat_entry(M, r, 1) = nmod_add(x, y, MOD); nmod_mat_entry(M, r, 2) = nmod_mul(x, y, MOD);
                }
                if (nmod_mat_det(M) == 0) { found = 1; printf("involution pairing %d%d %d%d %d%d\n", pr[k][0]+1, pr[k][1]+1, pr[k][2]+1, pr[k][3]+1, pr[k][4]+1, pr[k][5]+1); }
                nmod_mat_clear(M);
            }
            if (!found) printf("no involution pairing\n");
        }
        return 0;
    }
    if (!strcmp(mode, "curve") || !strcmp(mode, "curveR")) {
        int useR = !strcmp(mode, "curveR");
        /* curveR: as curve, with the weight polynomial Rt (Q = c R^2) in place of Q; A = Res(Rt', Rt''),
           B = Res(Rt, Rt''); a sample where Q is not c R^2 with deg R = deg Q / 2 is skipped. */
        /* curve N DB E mask K e_1..e_N b_1..b_N : samples s = 1, 2, ... until K+3 valid samples, interpolates
           A(s) = Res_z(Q^(4), Q^(5)) and B(s) = Res_z(Q^(3), Q^(5)) (degree < K), checks 3 points, prints
           deg A, deg B and the factorization degrees of gcd(A, B). */
        const char *mask = argv[5];
        long K = atol(argv[6]);
        int *e = malloc(N * sizeof(int));
        for (int i = 0; i < N; i++) e[i] = atoi(argv[7 + i]);
        for (int i = 0; i < N; i++) b[i] = parse_frac(argv[7 + N + i]);
        long T = K + 3 + K / 20 + 100;
        mp_limb_t *As = malloc(T * sizeof(mp_limb_t)), *Bs = malloc(T * sizeof(mp_limb_t));
        char *ok = calloc(T, 1);
        long expdeg = -1;
        {   /* reference degree from s = 0 shifted sample */
            mp_limb_t *aa = malloc(N * sizeof(mp_limb_t));
            nmod_poly_t FF; nmod_poly_init(FF, P);
            mp_limb_t s = n_mod2_preinv(123456789UL, MOD.n, MOD.ninv);
            for (int i = 0; i < N; i++) aa[i] = mask[i] == '1' ? nmod_add(b[i], s, MOD) : b[i];
            if (!Fpoly(FF, N, aa, DB, E)) { printf("reference check points FAIL\n"); return 0; }
            for (int i = 0; i < N; i++) strip_fixed(FF, aa[i], e[i]);
            expdeg = nmod_poly_degree(FF);
            printf("deg_z Q %ld\n", expdeg); fflush(stdout);
            nmod_poly_clear(FF); free(aa);
        }
        #pragma omp parallel for schedule(dynamic, 16)
        for (long t = 0; t < T; t++) {
            mp_limb_t *aa = malloc(N * sizeof(mp_limb_t));
            nmod_poly_t FF, Q3, Q4, Q5; nmod_poly_init(FF, P); nmod_poly_init(Q3, P); nmod_poly_init(Q4, P); nmod_poly_init(Q5, P);
            mp_limb_t s = n_mod2_preinv((mp_limb_t)(t + 1), MOD.n, MOD.ninv);
            for (int i = 0; i < N; i++) aa[i] = mask[i] == '1' ? nmod_add(b[i], s, MOD) : b[i];
            int bad = 0;
            for (int i = 0; i < N && !bad; i++) for (int j = i + 1; j < N; j++) if (aa[i] == aa[j]) bad = 1;
            if (!bad && Fpoly(FF, N, aa, DB, E)) {
                for (int i = 0; i < N; i++) strip_fixed(FF, aa[i], e[i]);
                if (nmod_poly_degree(FF) == expdeg && !useR) {
                    nmod_poly_derivative(Q5, FF); nmod_poly_derivative(Q5, Q5); nmod_poly_derivative(Q3, Q5);
                    nmod_poly_derivative(Q4, Q3); nmod_poly_derivative(Q5, Q4);
                    As[t] = nmod_poly_resultant(Q4, Q5); Bs[t] = nmod_poly_resultant(Q3, Q5); ok[t] = 1;
                } else if (nmod_poly_degree(FF) == expdeg) {
                    /* Rt = lc(Q) * monic gcd(Q, Q'); Rt^2 = lc(Q) Q is polynomial in s; A = Res(Rt', Rt''), B = Res(Rt, Rt'') */
                    mp_limb_t lq = nmod_poly_get_coeff_ui(FF, nmod_poly_degree(FF));
                    nmod_poly_derivative(Q3, FF); nmod_poly_gcd(Q4, FF, Q3);
                    nmod_poly_make_monic(Q4, Q4);
                    nmod_poly_mul(Q5, Q4, Q4); nmod_poly_scalar_mul_nmod(Q5, Q5, lq);
                    if (nmod_poly_equal(Q5, FF) && 2 * nmod_poly_degree(Q4) == expdeg) {
                        nmod_poly_scalar_mul_nmod(Q4, Q4, lq);
                        nmod_poly_derivative(Q3, Q4); nmod_poly_derivative(Q5, Q3);
                        As[t] = nmod_poly_resultant(Q3, Q5); Bs[t] = nmod_poly_resultant(Q4, Q5); ok[t] = 1;
                    }
                }
            }
            nmod_poly_clear(FF); nmod_poly_clear(Q3); nmod_poly_clear(Q4); nmod_poly_clear(Q5); free(aa);
        }
        mp_limb_t *xs = malloc(T * sizeof(mp_limb_t)), *ya = malloc(T * sizeof(mp_limb_t)), *yb = malloc(T * sizeof(mp_limb_t));
        long m = 0, skipped = 0;
        for (long t = 0; t < T; t++) { if (ok[t]) { xs[m] = t + 1; ya[m] = As[t]; yb[m] = Bs[t]; m++; } else skipped++; }
        printf("valid samples %ld, skipped %ld\n", m, skipped);
        if (m < K + 3) { printf("too few samples\n"); return 0; }
        nmod_poly_t PA, PB, GG; nmod_poly_init(PA, P); nmod_poly_init(PB, P); nmod_poly_init(GG, P);
        nmod_poly_interpolate_nmod_vec_fast(PA, xs, ya, K);
        nmod_poly_interpolate_nmod_vec_fast(PB, xs, yb, K);
        int chk = 1;
        for (long k = K; k < K + 3; k++) {
            if (nmod_poly_evaluate_nmod(PA, xs[k]) != ya[k]) chk = 0;
            if (nmod_poly_evaluate_nmod(PB, xs[k]) != yb[k]) chk = 0;
        }
        printf("interpolation checks %s; deg A %ld, deg B %ld\n", chk ? "pass" : "FAIL", nmod_poly_degree(PA), nmod_poly_degree(PB));
        nmod_poly_gcd(GG, PA, PB);
        printf("deg gcd(A, B) %ld\n", nmod_poly_degree(GG));
        if (nmod_poly_degree(GG) > 0) {
            nmod_poly_factor_t fac; nmod_poly_factor_init(fac);
            nmod_poly_factor(fac, GG);
            printf("gcd factors (degree^multiplicity):");
            for (long i = 0; i < fac->num; i++) printf(" %ld^%ld", nmod_poly_degree(fac->p + i), fac->exp[i]);
            printf("\n");
            for (long i = 0; i < fac->num; i++) if (nmod_poly_degree(fac->p + i) == 1) {
                mp_limb_t c0 = nmod_poly_get_coeff_ui(fac->p + i, 0), c1 = nmod_poly_get_coeff_ui(fac->p + i, 1);
                printf("root s = %lu\n", nmod_neg(nmod_div(c0, c1, MOD), MOD));
            }
        }
        return 0;
    }
    return 1;
}

int main(int argc, char **argv) {
    nmod_init(&MOD, P);
    if (argc == 3 && !strcmp(argv[1], "batch")) {
        /* batch FILE: one argument list per line (mode first), run in order */
        FILE *f = fopen(argv[2], "r");
        if (!f) { perror("batch"); return 1; }
        char line[4096];
        while (fgets(line, sizeof line, f)) {
            if (line[0] == '#' || line[0] == '\n') continue;
            line[strcspn(line, "\n")] = 0;
            printf("== %s\n", line); fflush(stdout);
            char *av[256]; int ac = 0; av[ac++] = argv[0];
            for (char *tok = strtok(line, " "); tok && ac < 255; tok = strtok(NULL, " ")) av[ac++] = tok;
            run(ac, av); fflush(stdout);
        }
        fclose(f);
        return 0;
    }
    return run(argc, argv);
}
