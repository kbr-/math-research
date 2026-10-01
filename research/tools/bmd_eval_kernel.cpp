// Evaluation kernel for graded pieces of the dimension-four bounded operator kernel (6 October 2026; cycle
// bmd-20261006-a).  Tested statement, for each excess exc in the series: is there a kernel element of order exactly ord
// and excess exc, i.e. polynomials W_c (2 <= c <= ord; W_0 = W_1 = 0 are forced) of weighted degree exc + ord - c in
// e_1..e_4 (weights 1,2,3,4) with W_ord != 0 and sum_c phi_rc W_c = 0 for every row r?  Each random point e gives the
// exact linear equations sum_c phi_rc(e) W_c(e) = 0 in the coefficients of the W_c, so the true kernel K lies in the
// evaluated kernel K_N.  W_ord = 0 on all of K_N certifies the negative answer; a vector of K_N with W_ord != 0 is
// written out and must be verified symbolically (research/tools/bmd_cube_verify_kernel_vector.m2) before it certifies
// the positive one.  Row r's equation lies in the space of polynomials of weighted degree exc + ord - q_r - w_r, of
// dimension M_r; it uses only the first M_r + MARGIN points (unisolvent with high probability; certification does not
// depend on it).  Series: the excesses are processed in the given order and the run stops after the first one with no
// order-ord direction (multiplying by e_1 shows that a negative answer at exc is negative at every lower excess).
// Input: the file written by research/tools/bmd_cube_phi_evals.m2.
// Usage: bmd_eval_kernel EVALS MARGIN OUTPREFIX EXC [EXC ...]; writes OUTPREFIX-e<EXC>.txt.
// Build: research/tools/build_bmd_eval_kernel.sh.  Linear algebra: fflas-ffpack over Givaro::Modular<float> (p < 4096).
#include <fflas-ffpack/fflas-ffpack.h>
#include <givaro/modular.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

typedef Givaro::Modular<float> Field;

static std::vector<std::vector<int>> monomials(int k) {
    std::vector<std::vector<int>> out;
    for (int d4 = 0; 4 * d4 <= k; ++d4)
        for (int c3 = 0; 4 * d4 + 3 * c3 <= k; ++c3)
            for (int b2 = 0; 4 * d4 + 3 * c3 + 2 * b2 <= k; ++b2)
                out.push_back({k - 4 * d4 - 3 * c3 - 2 * b2, b2, c3, d4});
    return out;
}

static long powmod(long b, int e, long p) {
    long r = 1;
    b %= p;
    while (e) { if (e & 1) r = r * b % p; b = b * b % p; e >>= 1; }
    return r;
}

// Returns the rank of the W_ord block of the evaluated kernel (0 means no element of order exactly ord), or -1 on error.
static long solve(const char *evalsPath, int exc, int margin, const std::string &outPath) {
    std::ifstream in(evalsPath);
    std::string tag;
    int d, m, ord, rows, npts;
    long p;
    in >> tag >> d >> m >> ord >> p >> rows >> npts;
    if (tag != "HEADER" || p >= 4096) { std::fprintf(stderr, "bad header or modulus\n"); return -1; }
    std::vector<int> rowPts(rows);
    for (int r = 0; r < rows; ++r) {
        int q, s, j, w;
        in >> tag >> q >> s >> j >> w;
        if (tag != "ROW") { std::fprintf(stderr, "bad row record\n"); return -1; }
        rowPts[r] = (int)monomials(exc + ord - q - w).size() + margin;
        if (rowPts[r] > npts) { std::fprintf(stderr, "row %d needs %d points, file has %d\n", r, rowPts[r], npts); return -1; }
    }
    // unknowns: (c, monomial) for c = 2..ord, monomials of weighted degree exc + ord - c
    std::vector<std::vector<std::vector<int>>> mons;
    std::vector<size_t> offset;
    size_t U = 0;
    for (int c = 2; c <= ord; ++c) {
        offset.push_back(U);
        mons.push_back(monomials(exc + ord - c));
        U += mons.back().size();
    }
    const size_t topCount = mons.back().size(), topOffset = offset.back();
    size_t M = 0;
    std::vector<size_t> rowStart(rows);
    for (int r = 0; r < rows; ++r) { rowStart[r] = M; M += rowPts[r]; }
    std::printf("d=%d m=%d order<=%d excess=%d p=%ld rows/point=%d points=%d unknowns=%zu equations=%zu W_ord unknowns=%zu\n",
                d, m, ord, exc, p, rows, npts, U, M, topCount);
    std::fflush(stdout);
    Field F(p);
    float *A = FFLAS::fflas_new<float>(M * U);
    std::vector<long> phiRow(ord - 1);
    for (int k = 0; k < npts; ++k) {
        long e[4];
        in >> tag >> e[0] >> e[1] >> e[2] >> e[3];
        if (tag != "P") { std::fprintf(stderr, "bad point record %d\n", k); return -1; }
        std::vector<std::vector<long>> monVal(mons.size());
        for (size_t b = 0; b < mons.size(); ++b)
            for (auto &mu : mons[b]) {
                long v = 1;
                for (int i = 0; i < 4; ++i) v = v * powmod(e[i], mu[i], p) % p;
                monVal[b].push_back(v);
            }
        for (int r = 0; r < rows; ++r) {
            for (int c = 2; c <= ord; ++c) in >> phiRow[c - 2];
            if (k >= rowPts[r]) continue;
            float *row = A + (rowStart[r] + k) * U;
            for (size_t b = 0; b < mons.size(); ++b)
                for (size_t t = 0; t < mons[b].size(); ++t)
                    row[offset[b] + t] = (float)(phiRow[b] * monVal[b][t] % p);
        }
    }
    float *NS = nullptr;
    size_t ldn = 0, nsdim = 0;
    FFPACK::NullSpaceBasis(F, FFLAS::FflasRight, M, U, A, U, NS, ldn, nsdim);
    FFLAS::fflas_delete(A);
    std::printf("RANK=%zu EVALUATED_KERNEL_DIM=%zu\n", U - nsdim, nsdim);
    size_t topRank = 0;
    std::vector<float> top(topCount * (nsdim ? nsdim : 1));
    if (nsdim) {
        for (size_t t = 0; t < topCount; ++t)
            for (size_t j = 0; j < nsdim; ++j) top[t * nsdim + j] = NS[(topOffset + t) * ldn + j];
        std::vector<float> topCopy(top);
        topRank = FFPACK::Rank(F, topCount, nsdim, topCopy.data(), nsdim);
    }
    std::printf("TOP_COLUMN_RANK=%zu\n", topRank);
    std::ofstream out(outPath);
    out << "UNKNOWNS " << U << " ORDER " << ord << " EXCESS " << exc << " P " << p << " KERNEL_DIM " << nsdim
        << " TOP_COLUMN_RANK " << topRank << "\n";
    // write the basis vectors with nonzero top column (at most 20) for symbolic verification
    size_t written = 0;
    for (size_t j = 0; j < nsdim && written < 20; ++j) {
        bool nz = false;
        for (size_t t = 0; t < topCount; ++t) if (top[t * nsdim + j] != 0) { nz = true; break; }
        if (!nz) continue;
        out << "VECTOR";
        for (size_t b = 0; b < mons.size(); ++b)
            for (size_t t = 0; t < mons[b].size(); ++t) {
                long v = (long)NS[(offset[b] + t) * ldn + j];
                if (v) out << " " << (b + 2) << ":" << mons[b][t][0] << "," << mons[b][t][1] << "," << mons[b][t][2] << ","
                           << mons[b][t][3] << ":" << v;
            }
        out << "\n";
        ++written;
    }
    std::printf("VECTORS_WRITTEN=%zu\n", written);
    std::fflush(stdout);
    if (NS) FFLAS::fflas_delete(NS);
    return (long)topRank;
}

int main(int argc, char **argv) {
    if (argc < 5) { std::fprintf(stderr, "usage: %s EVALS MARGIN OUTPREFIX EXC [EXC ...]\n", argv[0]); return 2; }
    const int margin = std::atoi(argv[2]);
    const std::string prefix = argv[3];
    for (int a = 4; a < argc; ++a) {
        const int exc = std::atoi(argv[a]);
        const long topRank = solve(argv[1], exc, margin, prefix + "-e" + std::to_string(exc) + ".txt");
        if (topRank < 0) return 2;
        if (topRank == 0) { std::printf("STOP: no order-exactly-ord element at excess %d\n", exc); break; }
    }
    return 0;
}
