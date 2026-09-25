/* Structured families (structured_fill.c): the same test with the forms of the tops constrained.
   FAMILY 0 random, 1 hub (every top l_0^2 l_b^2 with one shared l_0), 2 chain (tops l_b^2 l_{b+1}^2),
   3 span (all forms uniform in a random t-dimensional subspace of A~_1, t = SPAN_DIM).
   Tested statement (relative universality): the images are direct until the structure's own capacity,
   and no syzygy appears that the structure does not force.
   Near-fill test of conj:product-top-killer-moment at degree 5: B independent random product tops
   tau_b = l_b^2 l'_b^2 on the weak monomial algebra (m cells per column, N columns).  For every prefix
   B = 1..B_MAX of one random sequence of tops, the rank of sum_b A~_1 tau_b in A~_5 is read off one
   row-rank-profile factorization (fflas-ffpack).  Reported per B: samples with every top in E, those among
   them whose images are not direct (rank < B(mN-2)), the mean excess, and E[3^(C-C_0) 1_E], with
   C_0 = dim A~_5 - B(mN-2).  The conjecture predicts no excess for B <= (1-eps) C(N,5) m^4 / N as N grows.
   Usage: near_fill M N_LIST SEED SAMPLES_LIST OUT.json (B runs from 1 to the fill point) */
#define main one_top_main_unused
#include "one_top.c"
#undef main
long gf3_row_rank_profile(long rows, long cols, float *A, long *profile);

static int FAMILY = 0, SPAN_DIM = 0;
static void run_one(long S, uint64_t seed, FILE *out, int first) {
    int Bmax = 100000;
    build();
    int r = mN - 2;
    if (Bmax * r > D5) Bmax = D5 / r;
    printf("m=%d N=%d dimA1=%d dimA5=%d r=%d fill=%.1f F=%.1f Bmax=%d\n", m, N, mN, D5, r, (double)D5 / r,
           (double)D5 / m / N, Bmax); fflush(stdout);
    long *allE = calloc(Bmax + 1, sizeof(long)), *notdirect = calloc(Bmax + 1, sizeof(long)), hist[16] = {0}; double final_rank_sum = 0;
    double *excess_sum = calloc(Bmax + 1, sizeof(double)), *moment = calloc(Bmax + 1, sizeof(double));
    long rows = (long)Bmax * mN;
    #pragma omp parallel
    {
        rng_t g = {seed + 7777 * (omp_get_thread_num() + 1), 0, 0};
        int *l = malloc(sizeof(int) * mN), *lp = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
        float *A = malloc(sizeof(float) * rows * D5);
        long *prof = malloc(sizeof(long) * (rows + 1));
        int *goodE = malloc(sizeof(int) * (Bmax + 1));
        long lE[1024] = {0}, lnd[1024] = {0}, lhist[16] = {0}; double final_rank_sum_local = 0; double lex[1024] = {0}, lmo[1024] = {0};
        #pragma omp for schedule(dynamic, 1)
        for (long s = 0; s < S; s++) {
            memset(A, 0, sizeof(float) * rows * D5);
            int *hub = malloc(sizeof(int) * mN), *prev = malloc(sizeof(int) * mN), *basis = malloc(sizeof(int) * mN * (SPAN_DIM + 1));
            rand_form(&g, hub); rand_form(&g, prev);
            for (int k = 0; k < SPAN_DIM; k++) rand_form(&g, basis + k * mN);
            for (int b = 0; b < Bmax; b++) {
                if (FAMILY == 0) { rand_form(&g, l); rand_form(&g, lp); }
                if (FAMILY == 1) { memcpy(l, hub, sizeof(int) * mN); rand_form(&g, lp); }
                if (FAMILY == 2) { memcpy(l, prev, sizeof(int) * mN); rand_form(&g, lp); memcpy(prev, lp, sizeof(int) * mN); }
                if (FAMILY == 3) for (int f = 0; f < 2; f++) {
                    int *dst = f ? lp : l; memset(dst, 0, sizeof(int) * mN);
                    for (int k = 0; k < SPAN_DIM; k++) { int c = trit(&g); for (int y = 0; y < mN; y++) dst[y] = (dst[y] + c * basis[k * mN + y]) % 3; }
                }
                top(l, lp, tau);
                goodE[b] = in_E(l, lp, tau);
                for (int t = 0; t < D4; t++) if (tau[t])
                    for (int y = 0; y < mN; y++) {
                        int i5 = T[(size_t)t * mN + y];
                        if (i5 >= 0) A[((long)b * mN + y) * D5 + i5] = (float)tau[t];
                    }
            }
            long flint_rank = -1;
            if (s < 2) {   /* validation against FLINT on the first samples */
                nmod_mat_t Mv; nmod_mat_init(Mv, rows, D5, 3);
                for (long i = 0; i < rows * D5; i++) if (A[i] != 0) nmod_mat_entry(Mv, i / D5, i % D5) = (mp_limb_t)A[i];
                flint_rank = nmod_mat_rank(Mv); nmod_mat_clear(Mv);
            }
            free(hub); free(prev); free(basis);
            long rk = gf3_row_rank_profile(rows, D5, A, prof);
            final_rank_sum_local += rk;
            if (flint_rank >= 0) {
                #pragma omp critical
                { printf("validation sample %ld: fflas rank %ld, FLINT rank %ld\n", s, rk, flint_rank); fflush(stdout);
                  if (rk != flint_rank) { fprintf(stderr, "RANK MISMATCH\n"); exit(2); } }
            }
            long idx = 0, rank = 0; int all = 1;
            for (int b = 1; b <= Bmax; b++) {
                while (idx < rk && prof[idx] < (long)b * mN) { idx++; rank++; }
                all &= goodE[b - 1];
                if (!all) continue;
                lE[b]++;
                long ex = (long)b * r - rank;
                if (ex > 0) lnd[b]++;
                lex[b] += ex; lmo[b] += pow(3.0, ex);
                if (b == Bmax) lhist[ex < 15 ? ex : 15]++;
            }
        }
        #pragma omp critical
        {
            for (int j = 0; j < 16; j++) hist[j] += lhist[j];
            final_rank_sum += final_rank_sum_local;
            for (int b = 1; b <= Bmax; b++) { allE[b] += lE[b]; notdirect[b] += lnd[b]; excess_sum[b] += lex[b]; moment[b] += lmo[b]; }
        }
        free(l); free(lp); free(tau); free(A); free(prof); free(goodE);
    }
    fprintf(out, "%s  {\"family\": %d, \"span_dim\": %d, \"N\": %d, \"samples\": %ld, \"dim_A5\": %d, \"r\": %d, \"fill\": %.3f,\n   \"by_B\": [\n",
            first ? "" : ",\n", FAMILY, SPAN_DIM, N, S, D5, r, (double)D5 / r);
    for (int b = 1; b <= Bmax; b++) {
        double mo = allE[b] ? moment[b] / S : 0;
        if (isfinite(mo) && mo < 1e30)
            fprintf(out, "  {\"B\": %d, \"all_E\": %ld, \"not_direct\": %ld, \"mean_excess\": %.6f, \"moment_3_excess\": %.6f}%s\n",
                    b, allE[b], notdirect[b], allE[b] ? excess_sum[b] / allE[b] : 0, mo, b < Bmax ? "," : "");
        else   /* 3^excess overflows for structured families; the moment is then reported as null */
            fprintf(out, "  {\"B\": %d, \"all_E\": %ld, \"not_direct\": %ld, \"mean_excess\": %.6f, \"moment_3_excess\": null}%s\n",
                    b, allE[b], notdirect[b], allE[b] ? excess_sum[b] / allE[b] : 0, b < Bmax ? "," : "");
        if (b % 4 == 0 || b >= Bmax - 3) printf("B=%d allE=%ld notdirect=%ld mean_excess=%.4f moment=%.4f\n", b, allE[b], notdirect[b],
               allE[b] ? excess_sum[b] / allE[b] : 0, allE[b] ? moment[b] / S : 0);
    }
    fprintf(out, "   ],\n   \"excess_histogram_at_B_max\": [");
    for (int j = 0; j < 16; j++) fprintf(out, "%s%ld", j ? ", " : "", hist[j]);
    fprintf(out, "],\n   \"mean_rank_at_B_max\": %.3f}", final_rank_sum / S); fflush(out);
    printf("family %d span %d N=%d mean rank at B_max %.2f of dim %d\n", FAMILY, SPAN_DIM, N, final_rank_sum / S, D5);
    free(allE); free(notdirect); free(excess_sum); free(moment); free(mask4); free(mask5); free(cols4); free(T);
    printf("excess histogram at B_max:"); for (int j = 0; j < 6; j++) printf(" %ld", hist[j]); printf("\n");
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: structured_fill M SPECS SEED SAMPLES OUT.json  (SPECS like 7:1:0,7:3:6 = N:FAMILY:SPAN_DIM)\n"); return 1; }
    m = atoi(argv[1]); uint64_t seed = strtoull(argv[3], 0, 10); long S = atol(argv[4]);
    FILE *out = fopen(argv[5], "w");
    fprintf(out, "{\n \"statement\": \"relative universality of structured product-top families at degree 5\",\n \"m\": %d, \"seed\": %llu,\n \"runs\": [\n", m, (unsigned long long)seed);
    char *sl = strdup(argv[2]), *sp; int first = 1;
    for (char *tok = strtok_r(sl, ",", &sp); tok; tok = strtok_r(0, ",", &sp)) {
        N = atoi(tok); char *c1 = strchr(tok, ':'); FAMILY = atoi(c1 + 1); SPAN_DIM = atoi(strchr(c1 + 1, ':') + 1);
        run_one(S, seed + 131 * N + 17 * FAMILY + SPAN_DIM, out, first); first = 0;
    }
    fprintf(out, "\n ]\n}\n"); fclose(out);
    return 0;
}
