// Graded freeness over the forms' truncated algebra (entry-2026-09-27-graded-dade).
//
// Tested statement (conjecture): on the square-free algebra Lambda of N cells over F_3 (one row), for linear forms
// L_1..L_F, the first degree at which dim(Lambda / (L_1..L_F) Lambda)_d differs from the free prediction
// W_d = [t^d] (1+t)^N / (1+t+t^2)^F (prop:syzygies-as-tor's freeness test) is floor((s+3)/2), s the least support of a
// nonzero F_3-combination of the forms (conj:graded-dade; conj:worst-direction-freeness without the row sum).  The
// output field min_floor_half (floor(s/2)) is kept for reference; the tested formula uses min_support.
// Cases: random forms, or forms with a planted combination of `short` cells (L_F = -(L_1 + ... + L_{F-1}) + delta).
// For each case the program prints the first degree of discrepancy and the minimum over all nonzero combinations of
// floor(|l|/2).  Exact ranks with FLINT nmod_mat.
// Usage: graded_dade_check OUT "N:F:short:seed,..."   (short = 0: random forms; -1, -2: the recorded AG(2,3) pairs;
// -3: one cell at each point of the projective space P^{F-1}(F_3), N = (3^F - 1)/2)
// The field capacity is the least degree with a negative free prediction W_d (-1 if none): no module is free there
// (entry-2026-09-27-pencil-graded-dade).
#include <flint/nmod_mat.h>
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
        int N, F, sh; unsigned seed;
        if (sscanf(item.c_str(), "%d:%d:%d:%u", &N, &F, &sh, &seed) != 4 || N > 20) return 2;
        std::mt19937 rng(seed);
        std::vector<std::vector<int>> cf(F, std::vector<int>(N));
        for (int f = 0; f < F; f++) for (int i = 0; i < N; i++) cf[f][i] = rng() % 3;
        if (sh == -3) {
            // one cell per projective point: nonzero vectors of F_3^F whose first nonzero coordinate is 1
            int k = 0; long tot = 1; for (int f = 0; f < F; f++) tot *= 3;
            for (long c = 1; c < tot; c++) { long x = c; std::vector<int> v(F); int lead = 0;
                for (int f = 0; f < F; f++) { v[f] = x % 3; x /= 3; if (!lead && v[f]) lead = v[f]; }
                if (lead != 1) continue;
                if (k >= N) return 3;
                for (int f = 0; f < F; f++) cf[f][k] = v[f];
                k++; }
            if (k != N) return 3;
        }
        if (sh == -1 || sh == -2) {
            // recorded occupancy pairs (ex:occupancy-pair-non-pointwise-defect): cells carry the points of AG(2,3),
            // minus p = (1,2) for short = -1 (N = 8), all nine for short = -2 (N = 9); F must be 2
            int k = 0;
            for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) { if (sh == -1 && a == 1 && b == 2) continue; if (k < N) { cf[0][k] = a; cf[1][k] = b; } k++; }
        }
        if (sh > 0) {
            std::vector<int> delta(N, 0);
            for (int k = 0; k < sh; k++) delta[rng() % N] = 1 + rng() % 2;
            for (int i = 0; i < N; i++) { int s = 0; for (int f = 0; f < F - 1; f++) s += cf[f][i]; cf[F - 1][i] = ((delta[i] - s) % 3 + 3) % 3; }
        }
        // minimum over nonzero combinations of floor(|l|/2)
        long ncomb = 1; for (int f = 0; f < F; f++) ncomb *= 3;
        int minHalf = N, minSupp = N;
        for (long c = 1; c < ncomb; c++) { long x = c; std::vector<int> mu(F); for (int f = 0; f < F; f++) { mu[f] = x % 3; x /= 3; }
            int s = 0; for (int i = 0; i < N; i++) { int v = 0; for (int f = 0; f < F; f++) v += mu[f] * cf[f][i]; s += v % 3 != 0; }
            if (s < minSupp) minSupp = s; if (s / 2 < minHalf) minHalf = s / 2; }
        // degrees: index masks
        std::vector<std::vector<int>> byDeg(N + 1); std::vector<int> idx(1 << N);
        for (int m = 0; m < (1 << N); m++) { int d = __builtin_popcount(m); idx[m] = byDeg[d].size(); byDeg[d].push_back(m); }
        // free prediction W_d = [t^d] (1+t)^N / (1+t+t^2)^F, as exact integers
        std::vector<long long> h(N + 1, 0); h[0] = 1;
        for (int i = 0; i < N; i++) for (int d = N; d >= 1; d--) h[d] += h[d - 1];
        std::vector<long long> w = h;
        for (int f = 0; f < F; f++) { std::vector<long long> q(N + 1, 0); for (int d = 0; d <= N; d++) { long long v = w[d]; if (d >= 1) v -= q[d - 1]; if (d >= 2) v -= q[d - 2]; q[d] = v; } w = q; }
        int capacity = -1; for (int d = 0; d <= N; d++) if (w[d] < 0) { capacity = d; break; }
        int first = -1; std::vector<long> quo(N + 1);
        for (int d = 0; d <= N; d++) {
            long rk = 0;
            if (d >= 1) {
                long rows = (long)F * byDeg[d - 1].size();
                nmod_mat_t M; nmod_mat_init(M, rows, byDeg[d].size(), 3);
                long r = 0;
                for (int f = 0; f < F; f++) for (int m : byDeg[d - 1]) {
                    for (int i = 0; i < N; i++) if (cf[f][i] && !(m >> i & 1)) nmod_mat_entry(M, r, idx[m | (1 << i)]) = cf[f][i];
                    r++; }
                rk = nmod_mat_rank(M); nmod_mat_clear(M);
            }
            quo[d] = byDeg[d].size() - rk;
            if (first < 0 && quo[d] != w[d]) first = d;
            if (first >= 0 && d > first + 1) break;
        }
        fprintf(out, "{\"N\": %d, \"F\": %d, \"short\": %d, \"seed\": %u, \"min_support\": %d, \"min_floor_half\": %d, \"first_discrepancy\": %d, \"capacity\": %d}\n",
                N, F, sh, seed, minSupp, minHalf, first, capacity);
        printf("N=%d F=%d short=%d seed=%u: min support %d, min floor half %d, first discrepancy %d\n", N, F, sh, seed, minSupp, minHalf, first);
        fflush(out); fflush(stdout);
    }
    fclose(out); return 0;
}
