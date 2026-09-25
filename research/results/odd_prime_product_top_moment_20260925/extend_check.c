/* Check of thm:directness-propagation: embed a certificate on q columns into N > q columns, with the
   extra columns' parts of every form uniform random (and, as a second test, all zero or all equal),
   and verify by an exact FLINT rank that the images stay direct: rank = B (mN - 2).
   Input: text file "q B" then B lines of 2*m*q trits (l then l').  Usage: extend_check M N FORMS.txt SEED TRIALS */
#define main one_top_main_unused
#include "one_top.c"
#undef main
int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: extend_check M N FORMS.txt SEED TRIALS\n"); return 1; }
    m = atoi(argv[1]); N = atoi(argv[2]); build();
    FILE *f = fopen(argv[3], "r"); int q, B; if (fscanf(f, "%d %d", &q, &B) != 2) return 1;
    int *cert = malloc(sizeof(int) * B * 2 * m * q);
    for (int i = 0; i < B * 2 * m * q; i++) if (fscanf(f, "%d", &cert[i]) != 1) return 1;
    fclose(f);
    rng_t g = {strtoull(argv[4], 0, 10), 0, 0}; int trials = atoi(argv[5]), passed = 0;
    int *L = malloc(sizeof(int) * mN), *LP = malloc(sizeof(int) * mN), *tau = malloc(sizeof(int) * D4);
    for (int t = 0; t < trials; t++) {
        nmod_mat_t Phi; nmod_mat_init(Phi, (long)B * mN, D5, 3);
        for (int b = 0; b < B; b++) {
            for (int y = 0; y < mN; y++) {
                int inside = y < m * q;
                int mode = t % 3;   /* 0 random extra columns, 1 zero, 2 copy of column 0 */
                L[y]  = inside ? cert[b * 2 * m * q + y] : (mode == 0 ? trit(&g) : mode == 1 ? 0 : cert[b * 2 * m * q + y % m]);
                LP[y] = inside ? cert[b * 2 * m * q + m * q + y] : (mode == 0 ? trit(&g) : mode == 1 ? 0 : cert[b * 2 * m * q + m * q + y % m]);
            }
            top(L, LP, tau);
            for (int t4 = 0; t4 < D4; t4++) if (tau[t4])
                for (int y = 0; y < mN; y++) { int i5 = T[(size_t)t4 * mN + y]; if (i5 >= 0) nmod_mat_entry(Phi, (long)b * mN + y, i5) = tau[t4]; }
        }
        long r = nmod_mat_rank(Phi); nmod_mat_clear(Phi);
        printf("trial %d (extra columns %s): rank %ld, direct needs %d\n", t, t % 3 == 0 ? "random" : t % 3 == 1 ? "zero" : "copied", r, B * (mN - 2));
        passed += r == (long)B * (mN - 2);
    }
    printf("passed %d of %d\n", passed, trials);
    return passed == trials ? 0 : 3;
}
