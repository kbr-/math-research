// Socle product nonvanishing on one row (entry-2026-09-27-group-freeness).
//
// Tested statement (conjecture): over F_3, for linear forms L_1..L_F on the square-free algebra Lambda(S) =
// F_3[y_i : i in S]/(y_i^2), if every nonzero F_3-combination of the forms has at least 2F cells of S, then the socle
// product prod_f L_f^2 is nonzero in Lambda(S) (equivalently T = F_3[L]/(L^3) acts freely on 1).  By
// prop:group-freeness, k disjoint groups with nonzero socle product make Lambda free through k.
// For each configuration the program prints |S|, the least support s of a nonzero combination and whether the socle
// product is nonzero.  Configurations:
//   mode 0  "0:F:maxcells": every subset of the points of P^{F-1}(F_3) with at most maxcells points (distinct points);
//   mode 1  "1:F:cells:count:seed": count random configurations of `cells` uniform nonzero vectors of F_3^F;
//   mode 2  "2:F:cells:count:seed": random multisets of points with every multiplicity at most 2.
// Usage: socle_product_check OUT "mode:...;mode:..."
#include <cstdio>
#include <cstdlib>
#include <random>
#include <sstream>
#include <string>
#include <vector>

typedef std::vector<std::vector<int>> Vecs;  // cells x F

static int leastSupport(const Vecs& v, int F) {
    long tot = 1; for (int f = 0; f < F; f++) tot *= 3;
    int best = 1 << 30;
    for (long c = 1; c < tot; c++) {
        long x = c; std::vector<int> mu(F); for (int f = 0; f < F; f++) { mu[f] = x % 3; x /= 3; }
        int s = 0; for (auto& w : v) { int a = 0; for (int f = 0; f < F; f++) a += mu[f] * w[f]; s += a % 3 != 0; }
        if (s < best) best = s;
    }
    return best;
}

static bool socleNonzero(const Vecs& v, int F) {
    int n = v.size(); if (n < 2 * F) return false;
    std::vector<unsigned char> cur(1u << n, 0), nxt(1u << n);
    cur[0] = 1;
    for (int f = 0; f < F; f++) for (int rep = 0; rep < 2; rep++) {
        std::fill(nxt.begin(), nxt.end(), 0);
        for (unsigned m = 0; m < (1u << n); m++) if (cur[m])
            for (int i = 0; i < n; i++) if (!(m >> i & 1) && v[i][f]) nxt[m | (1u << i)] = (nxt[m | (1u << i)] + cur[m] * v[i][f]) % 3;
        cur.swap(nxt);
    }
    for (unsigned m = 0; m < (1u << n); m++) if (cur[m]) return true;
    return false;
}

static Vecs points(int F) {
    Vecs p; long tot = 1; for (int f = 0; f < F; f++) tot *= 3;
    for (long c = 1; c < tot; c++) { long x = c; std::vector<int> w(F); int lead = 0;
        for (int f = 0; f < F; f++) { w[f] = x % 3; x /= 3; if (!lead && w[f]) lead = w[f]; }
        if (lead == 1) p.push_back(w); }
    return p;
}

int main(int argc, char** argv) {
    if (argc < 3) return 2;
    FILE* out = fopen(argv[1], "w");
    std::stringstream ss(argv[2]); std::string item;
    while (std::getline(ss, item, ';')) {
        int mode = atoi(item.c_str());
        auto emit = [&](const Vecs& v, int F, const char* tag) {
            int s = leastSupport(v, F); bool nz = socleNonzero(v, F);
            fprintf(out, "{\"config\": \"%s\", \"F\": %d, \"cells\": %zu, \"least_support\": %d, \"socle_nonzero\": %s}\n",
                    tag, F, v.size(), s, nz ? "true" : "false");
        };
        if (mode == 0) {
            int F, maxc; if (sscanf(item.c_str(), "0:%d:%d", &F, &maxc) != 2) return 2;
            Vecs p = points(F); int P = p.size(); if (P > 26) return 3;
            for (long mask = 1; mask < (1L << P); mask++) {
                if (__builtin_popcountl(mask) > maxc) continue;
                Vecs v; for (int i = 0; i < P; i++) if (mask >> i & 1) v.push_back(p[i]);
                char tag[64]; snprintf(tag, sizeof tag, "subset:%ld", mask); emit(v, F, tag);
            }
        } else {
            int F, cells, count; unsigned seed;
            if (sscanf(item.c_str(), "%*d:%d:%d:%d:%u", &F, &cells, &count, &seed) != 4 || cells > 24) return 2;
            std::mt19937 rng(seed); Vecs p = points(F);
            for (int k = 0; k < count; k++) {
                Vecs v;
                if (mode == 1) {
                    while ((int)v.size() < cells) { std::vector<int> w(F); int nz = 0;
                        for (int f = 0; f < F; f++) { w[f] = rng() % 3; nz |= w[f]; }
                        if (nz) v.push_back(w); }
                } else {
                    std::vector<int> mult(p.size(), 0);
                    while ((int)v.size() < cells) { int i = rng() % p.size(); if (mult[i] < 2) { mult[i]++; v.push_back(p[i]); } }
                }
                char tag[64]; snprintf(tag, sizeof tag, "%s:%u:%d", mode == 1 ? "random" : "mult2", seed, k); emit(v, F, tag);
            }
        }
        fflush(out);
    }
    fclose(out); return 0;
}
