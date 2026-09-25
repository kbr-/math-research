/* One-top equidistribution test for random product tops on the weak monomial algebra over F_3.

   Statement under test (conj:one-top-equidistribution, degree h+1 = 5 of product tops):
   A~ = tensor over columns c < N of (F_3 + V_c), dim V_c = m.  A random top is tau = l^2 l'^2 in A~_4
   with l, l' uniform in A~_1; E is the event that l, l' are independent and Ann_{A~_1}(tau) = span(l, l').
   For chi in A~_5^*, u(chi) is the rank of y -> chi(y .), A~_1 -> A~_4^*, and
       pi_E(chi) = Pr[tau in E and chi(y tau) = 0 for all y in A~_1].
   The conjecture predicts pi_E(chi) <= 3^{-(u-2)} (1 + delta_u), delta_u bounded and small for large u.
   The kernel estimates the ratio pi_E(chi) 3^{u-2} for several classes of chi, estimates Pr[not E],
   and computes exactly, over the scalars s_c = phi_c(l_c), s'_c = phi_c(l'_c), the probability for
   divided powers chi = phi^[5] of support w, where the event is P_{-c}(s,s') = 0 for all c in the
   support, P_{-c} = [X^2 Y^2] prod_{d != c} (1 + s_d X + s'_d Y).

   In A~ the square l^2 = 2 e_2(l) and tau = 4 e_2(l) e_2(l') = e_2(l) e_2(l') (mod 3), where e_2 is
   the sum of products of column parts over pairs of distinct columns; tau's coefficient on a
   degree-4 monomial (4 columns S with one cell each) is the sum over the 6 ways to give two
   columns of S to l and the other two to l'.

   Usage: one_top M N_LIST SEED TARGET_HITS NOT_E_SAMPLES SAMPLE_CAP W_MAX OUT.json (N_LIST like 7,8)
   Ranks use FLINT's nmod_mat_rank. */
#include <flint/nmod_mat.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

static int m, N, D4, D5, mN;
static int *mask4, *mask5, nm4, nm5, pw4, pw5;
static long sample_cap = 200000000L;
static int *T;            /* T[t * mN + y] = index5 of monomial t times cell y, or -1 */
static int (*cols4)[4];   /* sorted columns of each degree-4 mask */

static uint64_t sm(uint64_t *x) {
    uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
typedef struct { uint64_t s, buf; int left; } rng_t;
static int trit(rng_t *r) {
    for (;;) {
        if (r->left == 0) { r->buf = sm(&r->s); r->left = 32; }
        int v = r->buf & 3; r->buf >>= 2; r->left--;
        if (v < 3) return v;
    }
}

static int popc(int x) { return __builtin_popcount(x); }
static int maskpos5(int mask) {
    for (int i = 0; i < nm5; i++) if (mask5[i] == mask) return i;
    return -1;
}

static void build(void) {
    mN = m * N;
    nm4 = nm5 = 0;
    mask4 = malloc(sizeof(int) << N); mask5 = malloc(sizeof(int) << N);
    for (int x = 0; x < (1 << N); x++) {
        if (popc(x) == 4) mask4[nm4++] = x;
        if (popc(x) == 5) mask5[nm5++] = x;
    }
    pw4 = m * m * m * m; pw5 = pw4 * m;
    D4 = nm4 * pw4; D5 = nm5 * pw5;
    cols4 = malloc(sizeof(*cols4) * nm4);
    for (int k = 0; k < nm4; k++) {
        int j = 0;
        for (int c = 0; c < N; c++) if (mask4[k] >> c & 1) cols4[k][j++] = c;
    }
    T = malloc(sizeof(int) * (size_t)D4 * mN);
    for (int k = 0; k < nm4; k++)
        for (int code = 0; code < pw4; code++) {
            int dig[4], cc = code;
            for (int j = 0; j < 4; j++) { dig[j] = cc % m; cc /= m; }
            int t = k * pw4 + code;
            for (int c0 = 0; c0 < N; c0++)
                for (int i0 = 0; i0 < m; i0++) {
                    int y = c0 * m + i0;
                    if (mask4[k] >> c0 & 1) { T[(size_t)t * mN + y] = -1; continue; }
                    int mk = mask4[k] | (1 << c0), pos = maskpos5(mk);
                    /* digits of the 5-monomial in sorted column order */
                    int code5 = 0, mul = 1, j = 0;
                    for (int c = 0; c < N; c++) if (mk >> c & 1) {
                        int d = (c == c0) ? i0 : dig[j++];
                        code5 += d * mul; mul *= m;
                    }
                    T[(size_t)t * mN + y] = pos * pw5 + code5;
                }
        }
}

/* tau = e_2(l) e_2(l') on degree-4 monomials */
static void top(const int *l, const int *lp, int *tau) {
    static const int split[6][4] = {{0,1,2,3},{0,2,1,3},{0,3,1,2},{2,3,0,1},{1,3,0,2},{1,2,0,3}};
    for (int k = 0; k < nm4; k++)
        for (int code = 0; code < pw4; code++) {
            int dig[4], cc = code;
            for (int j = 0; j < 4; j++) { dig[j] = cc % m; cc /= m; }
            int a[4], b[4];
            for (int j = 0; j < 4; j++) { int c = cols4[k][j]; a[j] = l[c * m + dig[j]]; b[j] = lp[c * m + dig[j]]; }
            int s = 0;
            for (int q = 0; q < 6; q++) s += a[split[q][0]] * a[split[q][1]] * b[split[q][2]] * b[split[q][3]];
            tau[k * pw4 + code] = s % 3;
        }
}

static long rank_of(nmod_mat_t A) { return nmod_mat_rank(A); }

/* rank of y -> y tau, and whether l, l' are independent */
static int in_E(const int *l, const int *lp, const int *tau) {
    nmod_mat_t R; nmod_mat_init(R, mN, D5, 3);
    for (int t = 0; t < D4; t++) if (tau[t])
        for (int y = 0; y < mN; y++) { int i5 = T[(size_t)t * mN + y]; if (i5 >= 0) nmod_mat_entry(R, y, i5) = tau[t]; }
    long r = rank_of(R); nmod_mat_clear(R);
    nmod_mat_t L; nmod_mat_init(L, 2, mN, 3);
    for (int y = 0; y < mN; y++) { nmod_mat_entry(L, 0, y) = l[y]; nmod_mat_entry(L, 1, y) = lp[y]; }
    long r2 = rank_of(L); nmod_mat_clear(L);
    return r == mN - 2 && r2 == 2;
}

static void rand_form(rng_t *r, int *l) { for (int y = 0; y < mN; y++) l[y] = trit(r); }

typedef struct { const char *name; int u; long samples, hits, hitsE; double ratio, lo, hi; } res_t;

static res_t test_chi(const char *name, const int *chi, long target_hits, uint64_t seed) {
    res_t R = {name, 0, 0, 0, 0, 0, 0, 0};
    /* M[y][t] = chi(y * mono_t) */
    uint8_t *M = calloc((size_t)mN * D4, 1);
    nmod_mat_t K; nmod_mat_init(K, mN, D4, 3);
    for (int t = 0; t < D4; t++) for (int y = 0; y < mN; y++) {
        int i5 = T[(size_t)t * mN + y];
        if (i5 >= 0 && chi[i5]) { M[(size_t)y * D4 + t] = chi[i5]; nmod_mat_entry(K, y, t) = chi[i5]; }
    }
    R.u = (int)rank_of(K); nmod_mat_clear(K);
    double pred = pow(3.0, -(R.u - 2));
    long S = (long)(target_hits / (pred < 1 ? pred : 1));
    if (S > sample_cap) {
        printf("%-10s u=%2d skipped: needs %ld samples, cap %ld\n", name, R.u, S, sample_cap); fflush(stdout);
        free(M); R.samples = 0; return R;
    }
    long hits = 0, hitsE = 0;
    #pragma omp parallel reduction(+:hits,hitsE)
    {
        rng_t r = {seed ^ (0x1234567ULL * (omp_get_thread_num() + 1)), 0, 0};
        int *l = malloc(sizeof(int) * mN), *lp = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
        #pragma omp for schedule(static)
        for (long s = 0; s < S; s++) {
            rand_form(&r, l); rand_form(&r, lp); top(l, lp, tau);
            int zero = 1;
            for (int y = 0; y < mN && zero; y++) {
                int acc = 0; const uint8_t *row = M + (size_t)y * D4;
                for (int t = 0; t < D4; t++) acc += row[t] * tau[t];
                if (acc % 3) zero = 0;
            }
            if (zero) { hits++; if (in_E(l, lp, tau)) hitsE++; }
        }
        free(l); free(lp); free(tau);
    }
    free(M);
    R.samples = S; R.hits = hits; R.hitsE = hitsE;
    double mean = (double)hitsE / S, se = sqrt((double)(hitsE > 0 ? hitsE : 1)) / S;
    R.ratio = mean / pred; R.lo = (mean - 2 * se) / pred; R.hi = (mean + 2 * se) / pred;
    printf("%-10s u=%2d samples=%ld hits=%ld hitsE=%ld ratio=%.3f [%.3f, %.3f]\n",
           name, R.u, S, hits, hitsE, R.ratio, R.lo, R.hi);
    fflush(stdout);
    return R;
}

/* exact probability, over s, s' in F_3^w, that P_{-c}(s,s') = 0 for every c */
static double divpow_exact(int w) {
    long total = 1; for (int i = 0; i < 2 * w; i++) total *= 3;
    long good = 0;
    #pragma omp parallel for reduction(+:good) schedule(static)
    for (long x = 0; x < total; x++) {
        int s[16], sp[16]; long z = x;
        for (int c = 0; c < w; c++) { s[c] = z % 3; z /= 3; sp[c] = z % 3; z /= 3; }
        int P[3][3] = {{1,0,0},{0,0,0},{0,0,0}};
        for (int d = 0; d < w; d++)
            for (int i = 2; i >= 0; i--) for (int j = 2; j >= 0; j--) {
                int v = P[i][j];
                if (i) v += s[d] * P[i-1][j];
                if (j) v += sp[d] * P[i][j-1];
                P[i][j] = v % 3;
            }
        int ok = 1;
        for (int c = 0; c < w && ok; c++) {
            int Q[3][3];
            for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) {
                int v = P[i][j];
                if (i) v -= s[c] * Q[i-1][j];
                if (j) v -= sp[c] * Q[i][j-1];
                Q[i][j] = ((v % 3) + 3) % 3;
            }
            if (Q[2][2]) ok = 0;
        }
        good += ok;
    }
    return (double)good / total;
}

/* Limit of divpow_exact(w) for w = w0 mod 3 when every one of the 9 column types (s_c, s'_c) occurs:
   the truncated product only sees the type counts mod 3, since (1+z)^3 = 1 in F_3[X,Y]/(X^3,Y^3).
   Returns the fraction of residue vectors (r_t), sum r_t = w0 mod 3, for which [X^2Y^2] G (1+z_t)^{-1} = 0
   for all 9 types t, G = prod_t (1+z_t)^{r_t}. */
static double residue_limit(int w0) {
    long good = 0, total = 0;
    for (int code = 0; code < 19683; code++) {
        int r[9], cc = code, sum = 0;
        for (int t = 0; t < 9; t++) { r[t] = cc % 3; cc /= 3; sum += r[t]; }
        if (sum % 3 != w0 % 3) continue;
        total++;
        int P[3][3] = {{1,0,0},{0,0,0},{0,0,0}};
        for (int t = 0; t < 9; t++) for (int k = 0; k < r[t]; k++) {
            int a = t % 3, b = t / 3;
            for (int i = 2; i >= 0; i--) for (int j = 2; j >= 0; j--) {
                int v = P[i][j];
                if (i) v += a * P[i-1][j];
                if (j) v += b * P[i][j-1];
                P[i][j] = v % 3;
            }
        }
        int ok = 1;
        for (int t = 0; t < 9 && ok; t++) {
            int a = t % 3, b = t / 3, Q[3][3];
            for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) {
                int v = P[i][j];
                if (i) v -= a * Q[i-1][j];
                if (j) v -= b * Q[i][j-1];
                Q[i][j] = ((v % 3) + 3) % 3;
            }
            if (Q[2][2]) ok = 0;
        }
        good += ok;
    }
    return (double)good / total;
}

/* Exact q(w) for all w <= wmax by dynamic programming over the state (type counts mod 3, set of types
   present) of w iid uniform column types in F_3^2: the event depends only on that state.  The event for
   state (r, P): [X^2Y^2] G (1+z_t)^{-1} = 0 for every present type t, G = prod_t (1+z_t)^{r_t}. */
static int state_ok(int rcode, int pres) {
    int r[9], cc = rcode;
    for (int t = 0; t < 9; t++) { r[t] = cc % 3; cc /= 3; }
    int P[3][3] = {{1,0,0},{0,0,0},{0,0,0}};
    for (int t = 0; t < 9; t++) for (int k = 0; k < r[t]; k++) {
        int a = t % 3, b = t / 3;
        for (int i = 2; i >= 0; i--) for (int j = 2; j >= 0; j--) {
            int v = P[i][j];
            if (i) v += a * P[i-1][j];
            if (j) v += b * P[i][j-1];
            P[i][j] = v % 3;
        }
    }
    for (int t = 0; t < 9; t++) if (pres >> t & 1) {
        int a = t % 3, b = t / 3, Q[3][3];
        for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) {
            int v = P[i][j];
            if (i) v -= a * Q[i-1][j];
            if (j) v -= b * Q[i][j-1];
            Q[i][j] = ((v % 3) + 3) % 3;
        }
        if (Q[2][2]) return 0;
    }
    return 1;
}

static void divpow_dp(int wmax, double *q) {
    const int R = 19683, S = R * 512;
    double *cur = calloc(S, sizeof(double)), *nxt = calloc(S, sizeof(double));
    char *ok = malloc(S);
    int pw3[9]; pw3[0] = 1; for (int t = 1; t < 9; t++) pw3[t] = pw3[t-1] * 3;
    #pragma omp parallel for schedule(static)
    for (int st = 0; st < S; st++) ok[st] = (char)state_ok(st % R, st / R);
    cur[0] = 1.0;
    for (int w = 1; w <= wmax; w++) {
        memset(nxt, 0, S * sizeof(double));
        #pragma omp parallel for schedule(static)
        for (int dst = 0; dst < S; dst++) {
            int rc = dst % R, pres = dst / R; double acc = 0;
            for (int t = 0; t < 9; t++) {
                if (!(pres >> t & 1)) continue;
                int digit = (rc / pw3[t]) % 3, prc = rc - digit * pw3[t] + ((digit + 2) % 3) * pw3[t];
                acc += cur[prc + R * pres] + cur[prc + R * (pres & ~(1 << t))];
            }
            nxt[dst] = acc / 9.0;
        }
        double *tmp = cur; cur = nxt; nxt = tmp;
        double good = 0;
        for (int st = 0; st < S; st++) if (ok[st]) good += cur[st];
        q[w] = good;
    }
    free(cur); free(nxt); free(ok);
}

int main(int argc, char **argv) {
    if (argc != 9) { fprintf(stderr, "usage: one_top M N_LIST SEED TARGET_HITS NOT_E_SAMPLES SAMPLE_CAP W_MAX OUT.json\n"); return 1; }
    m = atoi(argv[1]);
    uint64_t seed = strtoull(argv[3], 0, 10);
    long target = atol(argv[4]), notE_samples = atol(argv[5]);
    sample_cap = atol(argv[6]);
    int wmax = atoi(argv[7]);
    FILE *out = fopen(argv[8], "w");
    fprintf(out, "{\n \"statement\": \"pi_E(chi) 3^(u-2) near 1 for random product tops in degree 5 (tested); "
                 "divided powers phi^[5] of support w: exact zero probability over the scalars\",\n"
                 " \"m\": %d, \"seed\": %llu, \"target_hits\": %ld, \"sample_cap\": %ld,\n \"runs\": [\n",
            m, (unsigned long long)seed, target, sample_cap);
    char *list = strdup(argv[2]), *tok = strtok(list, ",");
    int first = 1;
    while (tok) {
        N = atoi(tok); tok = strtok(0, ",");
        if (N < 7) { fprintf(stderr, "need N >= 2*5-3 = 7 for the degree-5 statement\n"); return 1; }
        build();
        printf("m=%d N=%d dimA1=%d dimA4=%d dimA5=%d fill=%.1f\n", m, N, mN, D4, D5, (double)D5 / (mN - 2));
        fflush(stdout);
        fprintf(out, "%s  {\"N\": %d, \"dim_A1\": %d, \"dim_A4\": %d, \"dim_A5\": %d,\n", first ? "" : ",\n", N, mN, D4, D5);
        first = 0;
        long bad = 0;
        #pragma omp parallel reduction(+:bad)
        {
            rng_t r = {seed * 7 + omp_get_thread_num() + 11 + 1000 * N, 0, 0};
            int *l = malloc(sizeof(int) * mN), *lp = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
            #pragma omp for schedule(static)
            for (long s = 0; s < notE_samples; s++) { rand_form(&r, l); rand_form(&r, lp); top(l, lp, tau); bad += !in_E(l, lp, tau); }
            free(l); free(lp); free(tau);
        }
        printf("Pr[not E] ~ %ld / %ld\n", bad, notE_samples); fflush(stdout);
        fprintf(out, "   \"not_E\": {\"samples\": %ld, \"failures\": %ld},\n   \"classes\": [\n", notE_samples, bad);
        rng_t g = {seed + 17 * N, 0, 0};
        int *chi = malloc(sizeof(int) * D5);
        const char *names[] = {"random", "row0", "cols0-5", "divpow", "divpow2", "divpow_w5"};
        for (int k = 0; k < 6; k++) {
            memset(chi, 0, sizeof(int) * D5);
            if (k == 0) for (int i = 0; i < D5; i++) chi[i] = trit(&g);
            if (k == 1) for (int p = 0; p < nm5; p++) chi[p * pw5] = trit(&g);           /* all digits 0 */
            if (k == 2) for (int p = 0; p < nm5; p++) if (!(mask5[p] >> 6)) for (int d = 0; d < pw5; d++) chi[p * pw5 + d] = trit(&g);
            if (k >= 3) {
                int reps = (k == 4) ? 2 : 1, w = (k == 5) ? 5 : N;
                for (int rep = 0; rep < reps; rep++) {
                    int phi[64];
                    for (int c = 0; c < N; c++) {
                        int nz = 0;
                        do { nz = 0; for (int i = 0; i < m; i++) { phi[c * m + i] = trit(&g); nz |= phi[c * m + i]; } } while (!nz);
                        if (c >= w) for (int i = 0; i < m; i++) phi[c * m + i] = 0;
                    }
                    for (int p = 0; p < nm5; p++) for (int d = 0; d < pw5; d++) {
                        int prod = 1, dd = d;
                        for (int c = 0; c < N; c++) if (mask5[p] >> c & 1) { prod *= phi[c * m + dd % m]; dd /= m; }
                        chi[p * pw5 + d] = (chi[p * pw5 + d] + prod) % 3;
                    }
                }
            }
            res_t R = test_chi(names[k], chi, target, seed + 101 * (k + 1) + 7919 * N);
            fprintf(out, "    {\"class\": \"%s\", \"u\": %d, \"samples\": %ld, \"zero_contractions\": %ld, \"zero_in_E\": %ld, "
                         "\"ratio\": %.5f, \"ratio_2se\": [%.5f, %.5f]}%s\n",
                    R.name, R.u, R.samples, R.hits, R.hitsE, R.ratio, R.lo, R.hi, k < 5 ? "," : "");
            fflush(out);
        }
        fprintf(out, "   ]}");
        fflush(out);
        free(chi); free(mask4); free(mask5); free(cols4); free(T);
    }
    fprintf(out, "\n ],\n \"divided_power_exact\": [\n");
    for (int w = 3; w <= wmax; w++) {
        double q = divpow_exact(w);
        printf("divpow exact w=%d q=%.6g q*3^(w-2)=%.5f\n", w, q, q * pow(3, w - 2)); fflush(stdout);
        fprintf(out, "  {\"w\": %d, \"prob\": %.10g, \"ratio\": %.6f},\n", w, q, q * pow(3, w - 2));
        fflush(out);
    }
    int wdp = 80; double qdp[81];
    divpow_dp(wdp, qdp);
    fprintf(out, "  null\n ],\n \"divided_power_dp\": [");
    for (int w = 5; w <= wdp; w++) {
        if (w <= 12 || w % 10 == 0) { printf("divpow dp w=%d q=%.10g\n", w, qdp[w]); fflush(stdout); }
        fprintf(out, "%s{\"w\": %d, \"prob\": %.12g}", w > 5 ? ", " : "", w, qdp[w]);
    }
    fprintf(out, "],\n \"residue_limit\": [");
    for (int w0 = 0; w0 < 3; w0++) {
        double q = residue_limit(w0);
        printf("residue limit w = %d mod 3: %.10g\n", w0, q); fflush(stdout);
        fprintf(out, "%s{\"w_mod_3\": %d, \"limit\": %.10g}", w0 ? ", " : "", w0, q);
    }
    fprintf(out, "]\n}\n");
    fclose(out);
    return 0;
}
