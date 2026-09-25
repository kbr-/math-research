/* Near-fill test of conj:product-top-killer-moment at degree 5: B independent random product tops
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

static void run_one(long S, uint64_t seed, FILE *out, int first) {
    int Bmax = 100000;
    build();
    int r = mN - 2;
    if (Bmax * r > D5) Bmax = D5 / r;
    printf("m=%d N=%d dimA1=%d dimA5=%d r=%d fill=%.1f F=%.1f Bmax=%d\n", m, N, mN, D5, r, (double)D5 / r,
           (double)D5 / m / N, Bmax); fflush(stdout);
    long *allE = calloc(Bmax + 1, sizeof(long)), *notdirect = calloc(Bmax + 1, sizeof(long)), hist[16] = {0};
    double *excess_sum = calloc(Bmax + 1, sizeof(double)), *moment = calloc(Bmax + 1, sizeof(double));
    long rows = (long)Bmax * mN;
    #pragma omp parallel
    {
        rng_t g = {seed + 7777 * (omp_get_thread_num() + 1), 0, 0};
        int *l = malloc(sizeof(int) * mN), *lp = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
        float *A = malloc(sizeof(float) * rows * D5);
        long *prof = malloc(sizeof(long) * (rows + 1));
        int *goodE = malloc(sizeof(int) * (Bmax + 1));
        long lE[1024] = {0}, lnd[1024] = {0}, lhist[16] = {0}; double lex[1024] = {0}, lmo[1024] = {0};
        #pragma omp for schedule(dynamic, 1)
        for (long s = 0; s < S; s++) {
            memset(A, 0, sizeof(float) * rows * D5);
            for (int b = 0; b < Bmax; b++) {
                rand_form(&g, l); rand_form(&g, lp); top(l, lp, tau);
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
            long rk = gf3_row_rank_profile(rows, D5, A, prof);
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
            for (int b = 1; b <= Bmax; b++) { allE[b] += lE[b]; notdirect[b] += lnd[b]; excess_sum[b] += lex[b]; moment[b] += lmo[b]; }
        }
        free(l); free(lp); free(tau); free(A); free(prof); free(goodE);
    }
    fprintf(out, "%s  {\"N\": %d, \"samples\": %ld, \"dim_A5\": %d, \"r\": %d, \"fill\": %.3f, \"F\": %.3f,\n   \"by_B\": [\n",
            first ? "" : ",\n", N, S, D5, r, (double)D5 / r, (double)D5 / m / N);
    for (int b = 1; b <= Bmax; b++) {
        fprintf(out, "  {\"B\": %d, \"all_E\": %ld, \"not_direct\": %ld, \"mean_excess\": %.6f, \"moment_3_excess\": %.6f}%s\n",
                b, allE[b], notdirect[b], allE[b] ? excess_sum[b] / allE[b] : 0, allE[b] ? moment[b] / S : 0, b < Bmax ? "," : "");
        if (b % 4 == 0 || b >= Bmax - 3) printf("B=%d allE=%ld notdirect=%ld mean_excess=%.4f moment=%.4f\n", b, allE[b], notdirect[b],
               allE[b] ? excess_sum[b] / allE[b] : 0, allE[b] ? moment[b] / S : 0);
    }
    fprintf(out, "   ],\n   \"excess_histogram_at_B_max\": [");
    for (int j = 0; j < 16; j++) fprintf(out, "%s%ld", j ? ", " : "", hist[j]);
    fprintf(out, "]}"); fflush(out);
    free(allE); free(notdirect); free(excess_sum); free(moment); free(mask4); free(mask5); free(cols4); free(T);
    printf("excess histogram at B_max:"); for (int j = 0; j < 6; j++) printf(" %ld", hist[j]); printf("\n");
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: near_fill M N_LIST SEED SAMPLES_LIST OUT.json\n"); return 1; }
    m = atoi(argv[1]); uint64_t seed = strtoull(argv[3], 0, 10);
    FILE *out = fopen(argv[5], "w");
    fprintf(out, "{\n \"statement\": \"degree-5 directness of B random product tops up to the fill point\",\n \"m\": %d, \"seed\": %llu,\n \"runs\": [\n", m, (unsigned long long)seed);
    char *nl = strdup(argv[2]), *sl = strdup(argv[4]), *sp1, *sp2;
    char *tn = strtok_r(nl, ",", &sp1), *ts = strtok_r(sl, ",", &sp2);
    int first = 1;
    while (tn && ts) { N = atoi(tn); run_one(atol(ts), seed + 131 * N, out, first); first = 0; tn = strtok_r(0, ",", &sp1); ts = strtok_r(0, ",", &sp2); }
    fprintf(out, "\n ]\n}\n"); fclose(out);
    return 0;
}
