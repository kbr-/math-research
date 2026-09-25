/* Certificates for the directness propagation theorem (thm:directness-propagation), K = 2, degree 5.
   For q columns and B tops tau_b = l_b^2 l'_b^2 on A~(q), a certificate is an explicit list of forms with
   (H1) the images direct modulo the forced annihilators: rank of (y, b) -> y tau_b equals B (mq - 2), which
   (with each l_b, l'_b independent) means every syzygy has y_b in span(l_b, l'_b); and
   (H2) the tops tau_1..tau_B linearly independent in A~(q)_4.
   Both hypotheses pass to every prefix of the list, so one certificate at B serves every B' <= B.
   Ranks are exact over F_3 (FLINT nmod_mat_rank).  Usage: certificate M Q B SEED MAX_TRIES OUT.json */
#define main one_top_main_unused
#include "one_top.c"
#undef main
int main(int argc, char **argv) {
    if (argc != 7) { fprintf(stderr, "usage: certificate M Q B SEED MAX_TRIES OUT.json\n"); return 1; }
    m = atoi(argv[1]); N = atoi(argv[2]); int B = atoi(argv[3]); uint64_t seed = strtoull(argv[4], 0, 10);
    int tries = atoi(argv[5]); build();
    if (B * (mN - 2) > D5 || B > D4) { fprintf(stderr, "B too large for q\n"); return 1; }
    int *L = malloc(sizeof(int) * B * mN), *LP = malloc(sizeof(int) * B * mN), *tau = malloc(sizeof(int) * D4);
    rng_t g = {seed, 0, 0};
    for (int t = 1; t <= tries; t++) {
        nmod_mat_t Phi, Tops; nmod_mat_init(Phi, (long)B * mN, D5, 3); nmod_mat_init(Tops, B, D4, 3);
        int pairs_ok = 1;
        for (int b = 0; b < B; b++) {
            rand_form(&g, L + b * mN); rand_form(&g, LP + b * mN); top(L + b * mN, LP + b * mN, tau);
            nmod_mat_t P2; nmod_mat_init(P2, 2, mN, 3);
            for (int y = 0; y < mN; y++) { nmod_mat_entry(P2, 0, y) = L[b * mN + y]; nmod_mat_entry(P2, 1, y) = LP[b * mN + y]; }
            pairs_ok &= nmod_mat_rank(P2) == 2; nmod_mat_clear(P2);
            for (int t4 = 0; t4 < D4; t4++) if (tau[t4]) {
                nmod_mat_entry(Tops, b, t4) = tau[t4];
                for (int y = 0; y < mN; y++) { int i5 = T[(size_t)t4 * mN + y]; if (i5 >= 0) nmod_mat_entry(Phi, (long)b * mN + y, i5) = tau[t4]; }
            }
        }
        long r1 = nmod_mat_rank(Phi), r2 = nmod_mat_rank(Tops);
        nmod_mat_clear(Phi); nmod_mat_clear(Tops);
        printf("try %d: pairs independent %d, rank Phi %ld (need %d), rank tops %ld (need %d)\n", t, pairs_ok, r1, B * (mN - 2), r2, B);
        fflush(stdout);
        if (pairs_ok && r1 == (long)B * (mN - 2) && r2 == B) {
            FILE *out = fopen(argv[6], "w");
            fprintf(out, "{\n \"theorem\": \"thm:directness-propagation\", \"m\": %d, \"q\": %d, \"B\": %d, \"seed\": %llu, \"try\": %d,\n"
                         " \"rank_Phi\": %ld, \"rank_tops\": %ld, \"dim_A4\": %d, \"dim_A5\": %d,\n"
                         " \"cell_order\": \"cell (c, i) has index c*m + i\",\n \"forms\": [\n", m, N, B, (unsigned long long)seed, t, r1, r2, D4, D5);
            for (int b = 0; b < B; b++) {
                fprintf(out, "  {\"l\": [");
                for (int y = 0; y < mN; y++) fprintf(out, "%s%d", y ? "," : "", L[b * mN + y]);
                fprintf(out, "], \"l_prime\": [");
                for (int y = 0; y < mN; y++) fprintf(out, "%s%d", y ? "," : "", LP[b * mN + y]);
                fprintf(out, "]}%s\n", b < B - 1 ? "," : "");
            }
            fprintf(out, " ]\n}\n"); fclose(out);
            printf("certificate written after %d tries\n", t);
            return 0;
        }
    }
    printf("no certificate in %d tries\n", tries);
    return 2;
}
