// Supports of the piece directions of entry-2026-09-27-split-obstructions (entry-2026-09-27-aligned-extension).
//
// Tested statement: every rank-one piece mu of the recorded random families (one row, N cells, forms drawn as in
// pseudorandom_taylor_check) has a short combination l_mu = sum_f mu_f L_f, with at most 2e+1 cells at multiplier
// degree e, the length at which column Wilson fails.  Prints, for each case N:M:seed and each direction string mu
// (coordinate f = 2b + j), the number of cells of l_mu, and the supports of all 2M forms.
// Usage: piece_direction_supports OUT "N:M:seed:mu1/mu2/...,..."
#include <cstdio>
#include <cstdlib>
#include <random>
#include <sstream>
#include <string>
#include <vector>
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    FILE* out = fopen(argv[1], "w");
    std::stringstream ss(argv[2]); std::string item;
    while (std::getline(ss, item, ',')) {
        int N, M; unsigned seed; char rest[512];
        if (sscanf(item.c_str(), "%d:%d:%u:%511s", &N, &M, &seed, rest) != 4) return 2;
        std::mt19937 rng(seed);
        std::vector<std::vector<int>> cf(2 * M, std::vector<int>(N));
        for (int b = 0; b < M; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < N; col++) cf[2 * b + w][col] = rng() % 3;
        fprintf(out, "{\"N\": %d, \"M\": %d, \"seed\": %u, \"form_supports\": [", N, M, seed);
        for (int f = 0; f < 2 * M; f++) { int s = 0; for (int c = 0; c < N; c++) s += cf[f][c] != 0; fprintf(out, "%s%d", f ? ", " : "", s); }
        fprintf(out, "], \"directions\": [");
        std::stringstream ms(rest); std::string mu; bool first = true;
        while (std::getline(ms, mu, '/')) {
            int s = 0; for (int c = 0; c < N; c++) { int v = 0; for (int f = 0; f < 2 * M; f++) v += (mu[f] - '0') * cf[f][c]; s += v % 3 != 0; }
            fprintf(out, "%s{\"mu\": \"%s\", \"support\": %d}", first ? "" : ", ", mu.c_str(), s); first = false;
            printf("N=%d M=%d seed=%u mu=%s: support %d\n", N, M, seed, mu.c_str(), s);
        }
        fprintf(out, "]}\n");
    }
    fclose(out); return 0;
}
