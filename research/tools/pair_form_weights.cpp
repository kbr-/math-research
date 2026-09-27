// Weights of the linear combinations of the four forms A, B, C, D of the pair of ex:pseudorandom-taylor-check
// (one row, N cells, seed as in pseudorandom_taylor_check with m = 1: block 0 forms L0, L1, then block 1).
// Tested statement (prop:row-inflation's application): the four forms are linearly independent over F_3, so every
// nonzero combination is nonzero; the program also reports the least number of cells (= columns on one row) in the
// support of a nonzero combination, which is the column weight of the inflated occupancy forms.
// Usage: pair_form_weights OUT N seed
#include <cstdio>
#include <cstdlib>
#include <random>
int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s OUT N seed\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w"); int N = atoi(argv[2]); unsigned seed = atoi(argv[3]);
    if (N > 64) { fprintf(stderr, "N at most 64\n"); return 2; }
    std::mt19937 rng(seed);
    int coef[4][64];
    for (int b = 0; b < 2; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < N; col++) coef[2 * b + w][col] = rng() % 3;
    int minw = N + 1, zero = 0, count = 0;
    for (int c = 1; c < 81; c++) {
        int mu[4], x = c; for (int j = 0; j < 4; j++) { mu[j] = x % 3; x /= 3; }
        int w = 0; for (int col = 0; col < N; col++) { int s = 0; for (int j = 0; j < 4; j++) s += mu[j] * coef[j][col]; if (s % 3) w++; }
        count++; if (w == 0) zero++; if (w < minw) minw = w;
    }
    fprintf(out, "{\"N\": %d, \"seed\": %u, \"forms\": [", N, seed);
    for (int j = 0; j < 4; j++) { fprintf(out, "%s\"", j ? ", " : ""); for (int col = 0; col < N; col++) fprintf(out, "%d", coef[j][col]); fprintf(out, "\""); }
    fprintf(out, "], \"nonzero_combinations\": %d, \"vanishing\": %d, \"min_weight\": %d}\n", count, zero, minw);
    printf("N=%d seed=%u: %d combinations, %d vanish, least weight %d\n", N, seed, count, zero, minw);
    return 0;
}
