// Exact rank of a sparse integer matrix modulo a small prime p (p < 40), by dense Gaussian
// elimination on uint8 entries with OpenMP row updates.
// Input file (binary, little-endian int32): rows, cols, p, then for each row: nnz, then nnz pairs
// (col, val). Output on stdout: the rank. Built and called by research/tools/rank_modp.py.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <omp.h>

int main(int argc, char** argv) {
    if (argc != 2) { std::fprintf(stderr, "usage: rank_modp FILE\n"); return 2; }
    FILE* f = std::fopen(argv[1], "rb");
    if (!f) { std::perror("open"); return 2; }
    int32_t hdr[3];
    if (std::fread(hdr, 4, 3, f) != 3) return 2;
    const int64_t R = hdr[0], C = hdr[1]; const uint32_t p = hdr[2];
    if (p < 2 || p >= 40) { std::fprintf(stderr, "p out of range\n"); return 2; }
    const uint32_t m = (65536u + p - 1) / p;  // x % p = x - p*((x*m)>>16), exact for x < p*p
    std::vector<uint8_t> A((size_t)R * C, 0);
    for (int64_t r = 0; r < R; ++r) {
        int32_t nnz; if (std::fread(&nnz, 4, 1, f) != 1) return 2;
        for (int32_t k = 0; k < nnz; ++k) {
            int32_t cv[2]; if (std::fread(cv, 4, 2, f) != 2) return 2;
            if (cv[0] < 0 || cv[0] >= C) { std::fprintf(stderr, "bad column\n"); return 2; }
            int64_t v = ((int64_t)cv[1] % (int64_t)p + p) % p;
            uint8_t& a = A[(size_t)r * C + cv[0]]; a = (uint8_t)((a + v) % p);
        }
    }
    std::fclose(f);
    std::vector<uint32_t> inv(p, 0);
    for (uint32_t a = 1; a < p; ++a) for (uint32_t b = 1; b < p; ++b) if (a * b % p == 1) inv[a] = b;
    int64_t rank = 0;
    for (int64_t c = 0; c < C && rank < R; ++c) {
        int64_t piv = -1;
        for (int64_t r = rank; r < R; ++r) if (A[(size_t)r * C + c]) { piv = r; break; }
        if (piv < 0) continue;
        uint8_t* P = &A[(size_t)piv * C];
        if (piv != rank) {
            uint8_t* Q = &A[(size_t)rank * C];
            for (int64_t j = 0; j < C; ++j) { uint8_t t = P[j]; P[j] = Q[j]; Q[j] = t; }
            P = Q;
        }
        const uint32_t s = inv[P[c]];
        for (int64_t j = c; j < C; ++j) { uint32_t x = P[j] * s; P[j] = (uint8_t)(x - p * ((x * m) >> 16)); }
        #pragma omp parallel for schedule(dynamic, 64)
        for (int64_t r = rank + 1; r < R; ++r) {
            uint8_t* X = &A[(size_t)r * C];
            const uint32_t v = X[c];
            if (!v) continue;
            const uint32_t fct = p - v;
            for (int64_t j = c; j < C; ++j) {
                uint32_t x = X[j] + fct * P[j];
                X[j] = (uint8_t)(x - p * ((x * m) >> 16));
            }
        }
        ++rank;
    }
    std::printf("%lld\n", (long long)rank);
    return 0;
}
