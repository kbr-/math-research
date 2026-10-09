// Static span test over F_2 for parity 2-clause systems.
//
// Statement computed: for the system read from the instance file (m products of two
// affine forms on n <= 32 Boolean variables), the least D in [2, maxD] such that 1 lies in
// the F_2-span of the multilinear products x_T * f_i with |T| <= D-2 (the convention of the
// Python check; the value can exceed the true static degree, never fall below it).
// Output: one JSON line with n, m, the degree or "none", columns, products and pivots.
//
// Exact arithmetic: rows are bit vectors over the multilinear monomials of degree <= D;
// incremental elimination keeps one pivot row per leading column.
// Build: g++ -O3 -march=native -o span_kernel span_kernel.cpp
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <unordered_map>
#include <vector>

typedef uint64_t u64;
typedef uint32_t u32;

static int n, m;
static std::vector<std::vector<u32>> polys;  // monomial masks of each row polynomial

static void enumerate(int maxdeg, std::vector<u32>& out) {
    // all masks with popcount <= maxdeg, by degree, then lexicographic in the index tuples
    for (int d = 0; d <= maxdeg; d++) {
        if (d == 0) { out.push_back(0); continue; }
        std::vector<int> c(d);
        for (int i = 0; i < d; i++) c[i] = i;
        while (true) {
            u32 mask = 0;
            for (int i = 0; i < d; i++) mask |= (u32)1 << c[i];
            out.push_back(mask);
            int i = d - 1;
            while (i >= 0 && c[i] == n - d + i) i--;
            if (i < 0) break;
            c[i]++;
            for (int j = i + 1; j < d; j++) c[j] = c[j - 1] + 1;
        }
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: span_kernel INSTANCE MAXD\n"); return 2; }
    FILE* fh = fopen(argv[1], "r");
    if (!fh) { perror("instance"); return 2; }
    int maxD = atoi(argv[2]);
    if (fscanf(fh, "%d %d", &n, &m) != 2 || n < 2 || n > 32) { fprintf(stderr, "bad header\n"); return 2; }
    for (int r = 0; r < m; r++) {
        unsigned long a, b; int ca, cb;
        if (fscanf(fh, "%lu %d %lu %d", &a, &ca, &b, &cb) != 4) { fprintf(stderr, "bad row\n"); return 2; }
        if (a == 0 || b == 0 || a == b) { fprintf(stderr, "hypothesis violated: forms\n"); return 2; }
        std::vector<u32> ta, tb;
        for (int i = 0; i < n; i++) { if (a >> i & 1) ta.push_back((u32)1 << i); if (b >> i & 1) tb.push_back((u32)1 << i); }
        if (ca) ta.push_back(0);
        if (cb) tb.push_back(0);
        std::unordered_map<u32, int> par;
        for (u32 x : ta) for (u32 y : tb) par[x | y] ^= 1;
        std::vector<u32> poly;
        for (auto& kv : par) if (kv.second) poly.push_back(kv.first);
        polys.push_back(poly);
    }
    fclose(fh);
    for (int D = 2; D <= maxD; D++) {
        std::vector<u32> monos;
        enumerate(D, monos);
        size_t cols = monos.size();
        std::unordered_map<u32, u32> index;
        index.reserve(cols * 2);
        for (size_t j = 0; j < cols; j++) index[monos[j]] = (u32)j;
        size_t W = (cols + 63) / 64;
        std::vector<u64*> pivot(cols, nullptr);
        std::vector<u32> mult;
        enumerate(D - 2, mult);
        std::vector<u64> row(W);
        size_t npiv = 0, nprod = 0;
        for (int r = 0; r < m; r++) {
            for (u32 T : mult) {
                nprod++;
                for (size_t w = 0; w < W; w++) row[w] = 0;
                for (u32 t : polys[r]) { u32 j = index[t | T]; row[j >> 6] ^= (u64)1 << (j & 63); }
                long w = (long)W - 1;
                while (true) {
                    while (w >= 0 && row[w] == 0) w--;
                    if (w < 0) break;
                    int b = 63 - __builtin_clzll(row[w]);
                    size_t h = (size_t)w * 64 + b;
                    u64* p = pivot[h];
                    if (!p) {
                        p = (u64*)malloc((w + 1) * sizeof(u64));
                        for (long i = 0; i <= w; i++) p[i] = row[i];
                        pivot[h] = p; npiv++;
                        break;
                    }
                    for (long i = 0; i <= w; i++) row[i] ^= p[i];
                }
            }
            if ((r & 15) == 15) { fprintf(stderr, "D=%d rows %d/%d pivots %zu\n", D, r + 1, m, npiv); fflush(stderr); }
        }
        // reduce the constant 1
        for (size_t w = 0; w < W; w++) row[w] = 0;
        { u32 j = index[0]; row[j >> 6] ^= (u64)1 << (j & 63); }
        long w = (long)W - 1; bool zero = false;
        while (true) {
            while (w >= 0 && row[w] == 0) w--;
            if (w < 0) { zero = true; break; }
            int b = 63 - __builtin_clzll(row[w]);
            u64* p = pivot[(size_t)w * 64 + b];
            if (!p) break;
            for (long i = 0; i <= w; i++) row[i] ^= p[i];
        }
        for (u64* p : pivot) free(p);
        if (zero) {
            printf("{\"n\": %d, \"m\": %d, \"static_degree\": %d, \"columns\": %zu, \"products\": %zu, \"pivots\": %zu}\n", n, m, D, cols, nprod, npiv);
            return 0;
        }
        fprintf(stderr, "D=%d: 1 not in span (columns %zu, products %zu, pivots %zu)\n", D, cols, nprod, npiv);
    }
    printf("{\"n\": %d, \"m\": %d, \"static_degree\": \"none<=%d\"}\n", n, m, maxD);
    return 0;
}
