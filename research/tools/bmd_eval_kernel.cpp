// Evaluation kernel for graded pieces of the dimension-four bounded operator kernel (6 October 2026; cycles
// bmd-20261006-a and -b).  Tested statement, for each excess exc in the series: is there a kernel element of order
// exactly ord and excess exc, i.e. polynomials W_c (c <= ord; W_0 = W_1 = 0 are forced) of weighted degree exc + ord - c
// in e_1..e_4 (weights 1,2,3,4) with W_ord != 0 and sum_c phi_rc W_c = 0 for every row r?
//
// Reparametrization.  The rows (q, s) = (0, 1) are the first column of sqrt(I + T Z), Z the companion matrix of
// chi(a) = a^4 - e1 a^3 + e2 a^2 - e3 a + e4, so they say that sum_c gamma_c W_c a^c, gamma_c = binom(1/2, c), is
// divisible by chi.  With W_0 = W_1 = 0 this holds exactly when W_c = (chi Q)_c / gamma_c for Q = sum_{k=2}^{ord-4}
// Q_k a^k, Q_k of weighted degree exc + ord - 4 - k.  The unknowns are the coefficients of the Q_k; the (0, 1) rows are
// asserted to vanish at every point (a check of the convention) and dropped.  W_ord = Q_{ord-4} / gamma_ord.
//
// Certification.  Each random point e gives exact linear equations sum_c phi_rc(e) W_c(e) = 0, so the true kernel K lies
// in the evaluated kernel K_N.  Q_{ord-4} = 0 on all of K_N certifies the negative answer; a vector of K_N with
// Q_{ord-4} != 0 is written out and must be verified symbolically (research/tools/bmd_cube_verify_kernel_vector.m2)
// before it certifies the positive one.  Row r's equation lies in polynomials of weighted degree exc + ord - q_r - w_r,
// of dimension M_r; it uses only the first M_r + MARGIN points.  When there are more than U + 200 evaluated rows, each is
// added with random nonzero coefficients into 6 of U + 200 rows; too few points and compression only enlarge K_N.
// Series: excesses are processed in the given order.  A descending series stops after the first one with no order-ord
// direction; an ascending one stops at the first with one.  Matrices above 8.2 GB are refused.  For a descending series:
// (multiplying by e_1 shows that a negative answer at exc is negative at every lower excess).
// Input: the file written by research/tools/bmd_cube_phi_evals.m2.
// Usage: bmd_eval_kernel EVALS MARGIN OUTPREFIX EXC [EXC ...]; writes OUTPREFIX-e<EXC>.txt.
// Build: research/tools/build_bmd_eval_kernel.sh.  Linear algebra: fflas-ffpack over Givaro::Modular<double>; single
// precision was measured 9x slower at p = 4093, where products cannot accumulate before reduction.
#include <fflas-ffpack/fflas-ffpack.h>
#include <givaro/modular.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include <sys/resource.h>

typedef Givaro::Modular<double> Field;

// Matrix size cap: with Winograd multiplication an 8.0 GB matrix exceeded the 10 GB budget and a 4.56 GB one peaked at
// 7.67 GB (6 October 2026); the build disables Winograd, leaving the matrix and small workspace.
static const double kMaxMatrixBytes = 8.2e9;

static std::vector<std::vector<int>> monomials(int k) {
    std::vector<std::vector<int>> out;
    if (k < 0) return out;
    for (int d4 = 0; 4 * d4 <= k; ++d4)
        for (int c3 = 0; 4 * d4 + 3 * c3 <= k; ++c3)
            for (int b2 = 0; 4 * d4 + 3 * c3 + 2 * b2 <= k; ++b2)
                out.push_back({k - 4 * d4 - 3 * c3 - 2 * b2, b2, c3, d4});
    return out;
}

static long powmod(long b, long e, long p) {
    long r = 1;
    b %= p;
    if (b < 0) b += p;
    while (e) { if (e & 1) r = r * b % p; b = b * b % p; e >>= 1; }
    return r;
}

static long md(long x, long p) { x %= p; return x < 0 ? x + p : x; }

// Returns the rank of the W_ord block of the evaluated kernel (0 means no element of order exactly ord), or -1 on error.
static long solve(const char *evalsPath, int exc, int margin, const std::string &outPath) {
    std::ifstream in(evalsPath);
    std::string tag;
    int d, m, ord, rows, npts;
    long p;
    in >> tag >> d >> m >> ord >> p >> rows >> npts;
    if (tag != "HEADER" || p >= 4096) { std::fprintf(stderr, "bad header or modulus\n"); return -1; }
    std::vector<int> rowPts(rows), dropRow(rows);
    for (int r = 0; r < rows; ++r) {
        int q, s, j, w;
        in >> tag >> q >> s >> j >> w;
        if (tag != "ROW") { std::fprintf(stderr, "bad row record\n"); return -1; }
        dropRow[r] = (q == 0 && s == 1);
        rowPts[r] = dropRow[r] ? 0 : (int)monomials(exc + ord - q - w).size() + margin;
        if (rowPts[r] > npts) { std::fprintf(stderr, "row %d needs %d points, file has %d\n", r, rowPts[r], npts); return -1; }
    }
    // gamma_c = binom(1/2, c) mod p and its inverse
    const long half = (p + 1) / 2;
    std::vector<long> gammaInv(ord + 1);
    {
        long num = 1, fact = 1;
        for (int c = 0; c <= ord; ++c) {
            if (c > 0) { num = num * md(half - (c - 1), p) % p; fact = fact * c % p; }
            const long g = num * powmod(fact, p - 2, p) % p;
            if (g == 0) { std::fprintf(stderr, "gamma_%d vanishes mod p\n", c); return -1; }
            gammaInv[c] = powmod(g, p - 2, p);
        }
    }
    // unknowns: (k, monomial) for k = 2..ord-4, monomials of weighted degree exc + ord - 4 - k
    const int kmax = ord - 4;
    std::vector<std::vector<std::vector<int>>> mons;
    std::vector<size_t> offset;
    size_t U = 0;
    for (int k = 2; k <= kmax; ++k) {
        offset.push_back(U);
        mons.push_back(monomials(exc + ord - 4 - k));
        U += mons.back().size();
    }
    const size_t topCount = mons.back().size(), topOffset = offset.back();
    size_t M = 0;
    for (int r = 0; r < rows; ++r) M += rowPts[r];
    std::printf("d=%d m=%d order<=%d excess=%d p=%ld rows/point=%d points=%d unknowns=%zu equations=%zu W_ord unknowns=%zu\n",
                d, m, ord, exc, p, rows, npts, U, M, topCount);
    Field F(p);
    const bool compress = M > U + 200;
    const size_t R = compress ? U + 200 : M;
    std::printf("matrix rows=%zu (%s), %.2f GB\n", R, compress ? "compressed" : "direct", (double)R * U * 8 / 1e9);
    std::fflush(stdout);
    if ((double)R * U * 8 > kMaxMatrixBytes) { std::fprintf(stderr, "matrix exceeds the %.1f GB cap\n", kMaxMatrixBytes / 1e9); return -1; }
    // Backend: fflas-ffpack (default) or FLINT (BMD_BACKEND=flint), whose in-place LU needs almost no workspace;
    // fflas's NullSpaceBasis peaked about 3 GB above the matrix (cycle bmd-20261006-b).
    const char *be = std::getenv("BMD_BACKEND");
    const bool useFlint = be && std::string(be) == "flint";
    double *A = nullptr;
    nmod_mat_t FA;
    if (useFlint) { nmod_mat_init(FA, R, U, (mp_limb_t)p); nmod_mat_zero(FA); }  // 2.8 does not zero on init
    else { A = FFLAS::fflas_new<double>(R * U); std::fill(A, A + R * U, 0.0); }
    auto cell = [&](size_t i, size_t u) -> long { return useFlint ? (long)nmod_mat_entry(FA, i, u) : (long)A[i * U + u]; };
    auto setCell = [&](size_t i, size_t u, long v) { if (useFlint) nmod_mat_entry(FA, i, u) = (mp_limb_t)v; else A[i * U + u] = (double)v; };
    std::printf("backend: %s\n", useFlint ? "FLINT nmod_mat_lu (in place)" : "fflas-ffpack NullSpaceBasis");
    std::vector<long> rowBuf(U);
    std::mt19937_64 rng(20261006);
    std::vector<long> phiRow(ord + 1, 0);
    size_t nextRow = 0, droppedChecks = 0;
    for (int k = 0; k < npts; ++k) {
        long e[4];
        in >> tag >> e[0] >> e[1] >> e[2] >> e[3];
        // Macaulay2 lifts residues to balanced representatives; reduce every input to [0, p) (6 October 2026).
        for (int i = 0; i < 4; ++i) e[i] = md(e[i], p);
        if (tag != "P") { std::fprintf(stderr, "bad point record %d\n", k); return -1; }
        const long chi[5] = {e[3] % p, md(-e[2], p), e[1] % p, md(-e[0], p), 1};
        std::vector<std::vector<long>> monVal(mons.size());
        bool needed = false;
        for (int r = 0; r < rows; ++r) needed = needed || k < rowPts[r];
        if (needed)
            for (size_t b = 0; b < mons.size(); ++b)
                for (auto &mu : mons[b]) {
                    long v = 1;
                    for (int i = 0; i < 4; ++i) v = v * powmod(e[i], mu[i], p) % p;
                    monVal[b].push_back(v);
                }
        for (int r = 0; r < rows; ++r) {
            for (int c = 2; c <= ord; ++c) { in >> phiRow[c]; phiRow[c] = md(phiRow[c], p); }
            // kappa_k = sum_i phi_{r,k+i} chi_i / gamma_{k+i}: the coefficient of Q_k in row r
            std::vector<long> kappa(kmax + 1, 0);
            for (int kk = 2; kk <= kmax; ++kk) {
                long s = 0;
                for (int i = 0; i <= 4; ++i) s = (s + phiRow[kk + i] * chi[i] % p * gammaInv[kk + i]) % p;
                kappa[kk] = s;
            }
            if (dropRow[r]) {
                if (k < 20) {
                    for (int kk = 2; kk <= kmax; ++kk)
                        if (kappa[kk] != 0) { std::fprintf(stderr, "reparametrization check failed: row %d point %d k %d\n", r, k, kk); return -1; }
                    ++droppedChecks;
                }
                continue;
            }
            if (k >= rowPts[r]) continue;
            for (size_t b = 0; b < mons.size(); ++b)
                for (size_t t = 0; t < mons[b].size(); ++t) rowBuf[offset[b] + t] = kappa[b + 2] * monVal[b][t] % p;
            if (!compress) {
                const size_t i = nextRow++;
                for (size_t u = 0; u < U; ++u) setCell(i, u, rowBuf[u]);
            } else {
                for (int rep = 0; rep < 6; ++rep) {
                    const size_t i = rng() % R;
                    const long coef = 1 + (long)(rng() % (p - 1));
                    for (size_t u = 0; u < U; ++u)
                        if (rowBuf[u]) setCell(i, u, (cell(i, u) + coef * rowBuf[u]) % p);
                }
            }
        }
    }
    std::printf("reparametrization check: dropped (q,s)=(0,1) rows vanish identically in Q at %zu row-points\n", droppedChecks);
    std::fflush(stdout);
    double *NS = nullptr;
    size_t ldn = 0, nsdim = 0;
    if (useFlint) {
        // reduced row echelon form in place; the nullspace basis has one vector per free column f:
        // x_f = 1, x_{pivot(i)} = -A[i][f]
        // FLINT 2.8's nmod_mat_rref exited with status 1 on these matrices (6 October 2026), so use the in-place LU:
        // the first `rank` rows hold an echelon form whose row i has its pivot at the first nonzero entry after row
        // i-1's pivot (multipliers sit only in earlier pivot columns).  Back-substitution gives one nullspace vector
        // per free column.
        std::vector<slong> perm(R);
        size_t bad = 0;
        for (size_t i = 0; i < R; ++i) for (size_t u = 0; u < U; ++u) bad += nmod_mat_entry(FA, i, u) >= (mp_limb_t)p;
        if (bad) { std::fprintf(stderr, "%zu matrix entries outside [0, p)\n", bad); return -1; }
        std::fflush(stdout);
        const size_t rank = (size_t)nmod_mat_lu(perm.data(), FA, 0);
        std::printf("LU rank %zu\n", rank); std::fflush(stdout);
        std::vector<long> pivotOf(rank);
        std::vector<char> isPivot(U, 0);
        for (size_t i = 0; i < rank; ++i) {
            size_t c = i == 0 ? 0 : (size_t)pivotOf[i - 1] + 1;
            while (c < U && nmod_mat_entry(FA, i, c) == 0) ++c;
            if (c == U) { std::fprintf(stderr, "LU pivot scan failed at row %zu\n", i); return -1; }
            pivotOf[i] = (long)c; isPivot[c] = 1;
        }
        nsdim = U - rank; ldn = nsdim;
        NS = FFLAS::fflas_new<double>(U * (nsdim ? nsdim : 1));
        std::fill(NS, NS + U * (nsdim ? nsdim : 1), 0.0);
        std::vector<long> x(U);
        for (size_t f = 0, j = 0; f < U; ++f) {
            if (isPivot[f]) continue;
            std::fill(x.begin(), x.end(), 0);
            x[f] = 1;
            for (size_t ii = rank; ii-- > 0;) {
                const size_t c = (size_t)pivotOf[ii];
                long s = 0;
                for (size_t u = c + 1; u < U; ++u)
                    if (x[u]) s = (s + (long)nmod_mat_entry(FA, ii, u) * x[u]) % p;
                const long piv = (long)nmod_mat_entry(FA, ii, c);
                x[c] = md(-s, p) * powmod(piv, p - 2, p) % p;
            }
            for (size_t u = 0; u < U; ++u) NS[u * ldn + j] = (double)x[u];
            ++j;
        }
        nmod_mat_clear(FA);
    } else {
        FFPACK::NullSpaceBasis(F, FFLAS::FflasRight, R, U, A, U, NS, ldn, nsdim);
        FFLAS::fflas_delete(A);
    }
    std::printf("RANK=%zu EVALUATED_KERNEL_DIM=%zu\n", U - nsdim, nsdim);
    size_t topRank = 0;
    std::vector<double> top(topCount * (nsdim ? nsdim : 1));
    if (nsdim) {
        for (size_t t = 0; t < topCount; ++t)
            for (size_t j = 0; j < nsdim; ++j) top[t * nsdim + j] = NS[(topOffset + t) * ldn + j];
        std::vector<double> topCopy(top);
        topRank = FFPACK::Rank(F, topCount, nsdim, topCopy.data(), nsdim);
    }
    std::printf("TOP_COLUMN_RANK=%zu\n", topRank);
    std::ofstream out(outPath);
    out << "UNKNOWNS " << U << " ORDER " << ord << " EXCESS " << exc << " P " << p << " KERNEL_DIM " << nsdim
        << " TOP_COLUMN_RANK " << topRank << "\n";
    // write the basis vectors with nonzero top block (at most 20) as Q vectors for symbolic verification
    size_t written = 0;
    for (size_t j = 0; j < nsdim && written < 20; ++j) {
        bool nz = false;
        for (size_t t = 0; t < topCount; ++t) if (top[t * nsdim + j] != 0) { nz = true; break; }
        if (!nz) continue;
        out << "QVECTOR";
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
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    std::printf("PEAK_RSS_GB=%.2f\n", ru.ru_maxrss / 1e6);
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
        // descending series: stop at the first negative answer; ascending: stop at the first positive one
        const bool ascending = argc > 5 && std::atoi(argv[5]) > std::atoi(argv[4]);
        if (!ascending && topRank == 0) { std::printf("STOP: no order-exactly-ord element at excess %d\n", exc); break; }
        if (ascending && topRank > 0) { std::printf("STOP: first order-exactly-ord element at excess %d\n", exc); break; }
    }
    return 0;
}
