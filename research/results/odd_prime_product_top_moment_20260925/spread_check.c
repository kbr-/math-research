/* Test of the product-top spread lemma (K = 2): if at least 5 columns have l_c, l'_c independent in V_c,
   then Ann_{A~_1}(l^2 l'^2) = span(l, l').  Samples uniform l, l' and counts failures of the event E
   (Ann = span, l, l' independent) split by the number of good columns.  Prediction: no failure with
   5 or more good columns.  Reuses one_top.c's tables and rank routines.
   Usage: spread_check M N_LIST SEED SAMPLES OUT.json */
#define main one_top_main_unused
#include "one_top.c"
#undef main

static int good_columns(const int *l, const int *lp) {
    int g = 0;
    for (int c = 0; c < N; c++) {
        nmod_mat_t P; nmod_mat_init(P, 2, m, 3);
        for (int i = 0; i < m; i++) { nmod_mat_entry(P, 0, i) = l[c * m + i]; nmod_mat_entry(P, 1, i) = lp[c * m + i]; }
        g += nmod_mat_rank(P) == 2; nmod_mat_clear(P);
    }
    return g;
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: spread_check M N_LIST SEED SAMPLES OUT.json\n"); return 1; }
    m = atoi(argv[1]); uint64_t seed = strtoull(argv[3], 0, 10); long S = atol(argv[4]);
    FILE *out = fopen(argv[5], "w");
    fprintf(out, "{\n \"statement\": \"E fails only when fewer than 5 columns are good (K = 2)\",\n \"m\": %d, \"seed\": %llu, \"runs\": [", m, (unsigned long long)seed);
    char *list = strdup(argv[2]), *tok = strtok(list, ","); int first = 1;
    while (tok) {
        N = atoi(tok); tok = strtok(0, ","); build();
        long fail[65] = {0}, tot[65] = {0};
        #pragma omp parallel
        {
            rng_t r = {seed + 1000 * N + omp_get_thread_num() * 77 + 5, 0, 0};
            int *l = malloc(sizeof(int) * mN), *lp = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
            long f[65] = {0}, t[65] = {0};
            #pragma omp for schedule(static)
            for (long s = 0; s < S; s++) {
                rand_form(&r, l); rand_form(&r, lp); top(l, lp, tau);
                int g = good_columns(l, lp); t[g]++; if (!in_E(l, lp, tau)) f[g]++;
            }
            #pragma omp critical
            for (int g = 0; g <= N; g++) { fail[g] += f[g]; tot[g] += t[g]; }
            free(l); free(lp); free(tau);
        }
        fprintf(out, "%s\n  {\"N\": %d, \"samples\": %ld, \"by_good_columns\": [", first ? "" : ",", N, S); first = 0;
        long fail_ge5 = 0;
        for (int g = 0; g <= N; g++) {
            fprintf(out, "%s{\"good\": %d, \"tops\": %ld, \"not_E\": %ld}", g ? ", " : "", g, tot[g], fail[g]);
            if (g >= 5) fail_ge5 += fail[g];
            printf("N=%d good=%d tops=%ld notE=%ld\n", N, g, tot[g], fail[g]);
        }
        fprintf(out, "], \"not_E_with_at_least_5_good\": %ld}", fail_ge5);
        printf("N=%d failures with >=5 good columns: %ld\n", N, fail_ge5); fflush(stdout);
        free(mask4); free(mask5); free(cols4); free(T);
    }
    fprintf(out, "\n ]\n}\n"); fclose(out);
    return 0;
}
