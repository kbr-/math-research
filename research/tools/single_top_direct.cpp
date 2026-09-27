// Direct Taylor defect of a single top A^2 B with given coefficient groups (entry-2026-09-27-sharp-single-top).
//
// Validates research/tools/single_top_series.py: on one row of N = s1+s2+s3+s4 cells over F_3 with A = u1+u3+u4,
// B = u2+u3+2u4 (u_k the sum of group k), computes dim ann(A^2 B)_e - dim (A, B^2)_e by exact ranks for every
// multiplier degree e with e + 3 <= N.
// Exact linear algebra with FLINT nmod_mat.  Usage: single_top_direct OUT "s1:s2:s3:s4,..."
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <sstream>
#include <string>
#include <vector>

typedef std::vector<std::pair<int, int>> Poly;
static int NN;
static std::vector<int> idx;
static std::vector<std::vector<int>> byDeg;
static Poly mul(const Poly& a, const Poly& b) {
    static std::vector<int> buf; if (buf.size() < (size_t)(1 << NN)) buf.assign(1 << NN, 0);
    std::vector<int> touched;
    for (auto& [ca, xa] : a) for (auto& [cb, xb] : b) if (!(ca & cb)) {
        int c = ca | cb; if (!buf[c]) touched.push_back(c);
        buf[c] = (buf[c] + xa * xb) % 3; if (!buf[c]) buf[c] = 3;
    }
    Poly out; for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}
static long rankOf(const std::vector<Poly>& gens, int deg) {
    if (gens.empty()) return 0;
    long n = byDeg[deg].size(); nmod_mat_t M; nmod_mat_init(M, gens.size(), n, 3);
    for (size_t i = 0; i < gens.size(); i++) for (auto& [c, x] : gens[i]) nmod_mat_entry(M, i, idx[c]) = x;
    long r = nmod_mat_rank(M); nmod_mat_clear(M); return r;
}
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    FILE* out = fopen(argv[1], "w");
    std::stringstream ss(argv[2]); std::string item;
    while (std::getline(ss, item, ',')) {
        int s[4]; if (sscanf(item.c_str(), "%d:%d:%d:%d", &s[0], &s[1], &s[2], &s[3]) != 4) return 2;
        NN = s[0] + s[1] + s[2] + s[3]; if (NN > 22) return 2;
        idx.assign(1 << NN, 0); byDeg.assign(NN + 1, {});
        for (int c = 0; c < (1 << NN); c++) { int d = __builtin_popcount(c); idx[c] = byDeg[d].size(); byDeg[d].push_back(c); }
        int ca[4] = {1, 0, 1, 1}, cb[4] = {0, 1, 1, 2};
        Poly A, B; int cell = 0;
        for (int k = 0; k < 4; k++) for (int i = 0; i < s[k]; i++, cell++) { if (ca[k]) A.push_back({1 << cell, ca[k]}); if (cb[k]) B.push_back({1 << cell, cb[k]}); }
        Poly tau = mul(mul(A, A), B), B2 = mul(B, B);
        fprintf(out, "{\"sizes\": [%d, %d, %d, %d], \"tau_zero\": %s, \"series\": [", s[0], s[1], s[2], s[3], tau.empty() ? "true" : "false");
        for (int e = 0; e + 3 <= NN; e++) {
            // dim ann(tau)_e = dim S_e - rank(multiplication by tau from S_e)
            std::vector<Poly> img, T;
            for (int m : byDeg[e]) img.push_back(mul(tau, {{m, 1}}));
            long annDim = byDeg[e].size() - rankOf(img, e + 3);
            if (e >= 1) for (int m : byDeg[e - 1]) T.push_back(mul(A, {{m, 1}}));
            if (e >= 2) for (int m : byDeg[e - 2]) T.push_back(mul(B2, {{m, 1}}));
            long tDim = rankOf(T, e);
            fprintf(out, "%s%ld", e ? ", " : "", annDim - tDim);
        }
        fprintf(out, "]}\n"); fflush(out);
    }
    fclose(out); return 0;
}
