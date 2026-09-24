// Exact minimum degree of binary polynomials with prescribed Hasse multiplicities.
//
// Statement computed.  For n, k and each origin order l in {0,...,k-1}, D_l(n,k) is the least d
// such that some P in F_2[x_1..x_n] of total degree <= d has Hasse multiplicity >= k at every
// nonzero point of F_2^n and multiplicity exactly l at the origin (formal polynomials; no reduction
// modulo x_i^2 - x_i).  D(n,k) = min_l D_l(n,k) is the thread's quantity.
//
// Method.  mult_a(P) >= k iff for all |beta| < k the coefficient of z^beta in P(a+z) vanishes:
//   sum_alpha c_alpha * binom(alpha,beta) * a^(alpha-beta) = 0 over F_2,
// with binom(alpha,beta) odd iff beta_i is a bit-submask of alpha_i (Lucas), and a^(alpha-beta) = 1
// iff alpha_i = beta_i whenever a_i = 0.  At the origin the conditions say c_beta = 0 for |beta| < l,
// i.e. delete those columns.  Order the columns with |alpha| = l last; after Gauss-Jordan
// elimination of the nonzero-point rows, a P with origin order exactly l and degree <= d exists iff
// some degree-l column is free.  The witness sets that free variable to 1 and all other free
// variables to 0.  Every witness is re-checked by direct evaluation of its Hasse coefficients.
//
// Search.  Equivalently, such P exists iff r(l,d) < r(l+1,d) + N_l, where r(lo,d) is the rank of the
// columns with lo <= |alpha| <= d and N_l the number of degree-l monomials.  One forward elimination
// with columns in ascending degree yields r(lo,d) for every d, so k+1 passes give all minima; the
// direct solver then produces each witness, and --check also confirms nonexistence one degree lower.
//
// Usage: bmd_min_degree n k dcap [--out PATH] [--check]
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>
#include <omp.h>

using u64 = uint64_t;
using Mono = std::vector<int>;

static void monomials(int n, int maxdeg, std::vector<Mono>& out) {
    Mono cur(n, 0);
    struct R { static void go(int i, int left, int n, Mono& cur, std::vector<Mono>& out) {
        if (i == n) { out.push_back(cur); return; }
        for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, out); }
        cur[i] = 0; } };
    R::go(0, maxdeg, n, cur, out);
}
static int deg(const Mono& m) { int s = 0; for (int x : m) s += x; return s; }

// Hasse coefficient entry for row (a, beta) and column alpha.
static inline bool entry(int n, unsigned a, const Mono& beta, const Mono& alpha) {
    for (int i = 0; i < n; ++i) {
        if (beta[i] > alpha[i]) return false;
        if ((beta[i] & ~alpha[i]) != 0) return false;          // binom(alpha_i, beta_i) even
        if (!((a >> i) & 1u) && alpha[i] != beta[i]) return false;  // a_i = 0 kills alpha_i > beta_i
    }
    return true;
}

struct Result { bool exists; std::vector<Mono> witness; long rank; long rows; long cols; double secs; };

// Existence of P with degree <= d, mult >= k off the origin, origin order exactly l.
static Result solve(int n, int k, int d, int l) {
    auto t0 = std::chrono::steady_clock::now();
    std::vector<Mono> all, cols, betas;
    monomials(n, d, all);
    for (auto& m : all) if (deg(m) >= l && deg(m) != l) cols.push_back(m);
    long nfirst = (long)cols.size();
    for (auto& m : all) if (deg(m) == l) cols.push_back(m);   // degree-l columns last
    monomials(n, k - 1, betas);
    long C = (long)cols.size(), W = (C + 63) / 64;
    std::vector<unsigned> pts;
    for (unsigned a = 1; a < (1u << n); ++a) pts.push_back(a);
    long R = (long)(pts.size() * betas.size());
    std::vector<u64> M((size_t)R * W, 0);
    #pragma omp parallel for schedule(dynamic, 16)
    for (long r = 0; r < R; ++r) {
        unsigned a = pts[r / betas.size()]; const Mono& b = betas[r % betas.size()];
        u64* row = &M[(size_t)r * W];
        for (long c = 0; c < C; ++c) if (entry(n, a, b, cols[c])) row[c >> 6] |= (1ULL << (c & 63));
    }
    // Gauss-Jordan elimination, columns in order.
    std::vector<long> pivcol; long rank = 0;
    for (long c = 0; c < C && rank < R; ++c) {
        long w = c >> 6; u64 bit = 1ULL << (c & 63); long p = -1;
        for (long r = rank; r < R; ++r) if (M[(size_t)r * W + w] & bit) { p = r; break; }
        if (p < 0) continue;
        if (p != rank) for (long j = 0; j < W; ++j) std::swap(M[(size_t)p * W + j], M[(size_t)rank * W + j]);
        const u64* prow = &M[(size_t)rank * W];
        #pragma omp parallel for schedule(static)
        for (long r = 0; r < R; ++r) {
            if (r == rank) continue;
            u64* row = &M[(size_t)r * W];
            if (row[w] & bit) for (long j = w; j < W; ++j) row[j] ^= prow[j];
        }
        pivcol.push_back(c); ++rank;
    }
    std::vector<char> isPivot(C, 0);
    for (long c : pivcol) isPivot[c] = 1;
    Result res{false, {}, rank, R, C, 0};
    for (long f = nfirst; f < C; ++f) {
        if (isPivot[f]) continue;
        res.exists = true;
        res.witness.push_back(cols[f]);
        for (long i = 0; i < rank; ++i)
            if (M[(size_t)i * W + (f >> 6)] & (1ULL << (f & 63))) res.witness.push_back(cols[pivcol[i]]);
        break;
    }
    res.secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    return res;
}

// One incremental pass: columns with lo <= |alpha| <= dcap in ascending degree; forward elimination
// processes columns in order, so the rank after the degree-<=d block equals rank(M[lo..d]).
// Returns rank[d] for d = lo..dcap (index d).
static std::vector<long> rank_profile(int n, int k, int lo, int dcap, double& secs) {
    auto t0 = std::chrono::steady_clock::now();
    std::vector<Mono> all, cols, betas;
    monomials(n, dcap, all);
    std::stable_sort(all.begin(), all.end(), [](const Mono& x, const Mono& y) { return deg(x) < deg(y); });
    for (auto& m : all) if (deg(m) >= lo) cols.push_back(m);
    monomials(n, k - 1, betas);
    long C = (long)cols.size(), W = (C + 63) / 64;
    std::vector<unsigned> pts;
    for (unsigned a = 1; a < (1u << n); ++a) pts.push_back(a);
    long R = (long)(pts.size() * betas.size());
    std::vector<u64> M((size_t)R * W, 0);
    #pragma omp parallel for schedule(dynamic, 16)
    for (long r = 0; r < R; ++r) {
        unsigned a = pts[r / betas.size()]; const Mono& b = betas[r % betas.size()];
        u64* row = &M[(size_t)r * W];
        for (long c = 0; c < C; ++c) if (entry(n, a, b, cols[c])) row[c >> 6] |= (1ULL << (c & 63));
    }
    std::vector<long> out(dcap + 1, -1);
    long rank = 0;
    for (long c = 0; c < C; ++c) {
        if (rank < R) {
            long w = c >> 6; u64 bit = 1ULL << (c & 63); long p = -1;
            for (long r = rank; r < R; ++r) if (M[(size_t)r * W + w] & bit) { p = r; break; }
            if (p >= 0) {
                if (p != rank) for (long j = 0; j < W; ++j) std::swap(M[(size_t)p * W + j], M[(size_t)rank * W + j]);
                const u64* prow = &M[(size_t)rank * W];
                #pragma omp parallel for schedule(static)
                for (long r = rank + 1; r < R; ++r) {
                    u64* row = &M[(size_t)r * W];
                    if (row[w] & bit) for (long j = w; j < W; ++j) row[j] ^= prow[j];
                }
                ++rank;
            }
        }
        if (c + 1 == C || deg(cols[c + 1]) != deg(cols[c])) out[deg(cols[c])] = rank;
    }
    for (int d = lo; d <= dcap; ++d) if (out[d] < 0) out[d] = (d > lo ? out[d - 1] : 0);  // empty degree block
    secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    return out;
}

static long binom(long a, long b) { long x = 1; for (long t = 0; t < b; ++t) x = x * (a - t) / (t + 1); return x; }

// Independent check: Hasse multiplicity of a witness at point a, by direct coefficient evaluation.
static int multiplicity(int n, unsigned a, const std::vector<Mono>& P, int upto) {
    std::vector<Mono> betas; monomials(n, upto, betas);
    std::sort(betas.begin(), betas.end(), [](const Mono& x, const Mono& y) { return deg(x) < deg(y); });
    for (auto& b : betas) {
        int coef = 0;
        for (auto& al : P) {
            bool ok = true;
            for (int i = 0; i < n && ok; ++i) {
                if (b[i] > al[i]) ok = false;
                else {
                    // binom(al_i, b_i) mod 2 by direct Pascal parity, not Lucas
                    long x = 1, top = al[i], bot = b[i];
                    for (long t = 0; t < bot; ++t) x = x * (top - t) / (t + 1);
                    if (x % 2 == 0) ok = false;
                    else if (!((a >> i) & 1u) && al[i] != b[i]) ok = false;
                }
            }
            if (ok) coef ^= 1;
        }
        if (coef) return deg(b);
    }
    return upto + 1;
}

// One Gauss-Jordan pass at degree D with columns in DESCENDING degree.  In reduced echelon form a
// row's entries lie in its pivot column and later free columns, so setting one free column f to 1
// (others 0) gives a kernel vector vanishing on every column after f, i.e. on all lower degrees.
// Hence a free degree-l column is a witness of origin order exactly l, and conversely (degree-l
// columns are last among the columns of degree >= l).  Returns witnesses for every attaining l.
static std::vector<std::vector<Mono>> witnesses_desc(int n, int k, int D, double& secs) {
    auto t0 = std::chrono::steady_clock::now();
    std::vector<Mono> cols, betas;
    monomials(n, D, cols);
    std::stable_sort(cols.begin(), cols.end(), [](const Mono& x, const Mono& y) { return deg(x) > deg(y); });
    monomials(n, k - 1, betas);
    long C = (long)cols.size(), W = (C + 63) / 64;
    long R = (long)(((1u << n) - 1) * betas.size());
    std::vector<u64> M((size_t)R * W, 0);
    #pragma omp parallel for schedule(dynamic, 16)
    for (long r = 0; r < R; ++r) {
        unsigned a = 1 + (unsigned)(r / betas.size()); const Mono& b = betas[r % betas.size()];
        u64* row = &M[(size_t)r * W];
        for (long c = 0; c < C; ++c) if (entry(n, a, b, cols[c])) row[c >> 6] |= (1ULL << (c & 63));
    }
    std::vector<long> pivcol; long rank = 0;
    for (long c = 0; c < C && rank < R; ++c) {
        long w = c >> 6; u64 bit = 1ULL << (c & 63); long p = -1;
        for (long r = rank; r < R; ++r) if (M[(size_t)r * W + w] & bit) { p = r; break; }
        if (p < 0) continue;
        if (p != rank) for (long j = 0; j < W; ++j) std::swap(M[(size_t)p * W + j], M[(size_t)rank * W + j]);
        const u64* prow = &M[(size_t)rank * W];
        #pragma omp parallel for schedule(static)
        for (long r = 0; r < R; ++r) {
            if (r == rank) continue;
            u64* row = &M[(size_t)r * W];
            if (row[w] & bit) for (long j = w; j < W; ++j) row[j] ^= prow[j];
        }
        pivcol.push_back(c); ++rank;
    }
    std::vector<char> isPivot(C, 0);
    for (long c : pivcol) isPivot[c] = 1;
    std::vector<std::vector<Mono>> wit(k);
    for (long f = 0; f < C; ++f) {
        int l = deg(cols[f]);
        if (l >= k || isPivot[f] || !wit[l].empty()) continue;
        wit[l].push_back(cols[f]);
        for (long i = 0; i < rank; ++i)
            if (pivcol[i] < f && (M[(size_t)i * W + (f >> 6)] & (1ULL << (f & 63)))) wit[l].push_back(cols[pivcol[i]]);
    }
    secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    return wit;
}

static bool verify(int n, int k, int d, int l, const std::vector<Mono>& P) {
    int dP = 0; for (auto& m : P) dP = std::max(dP, deg(m));
    int m0 = multiplicity(n, 0, P, k), mmin = k + 1;
    for (unsigned a = 1; a < (1u << n); ++a) mmin = std::min(mmin, multiplicity(n, a, P, k - 1));
    bool ok = (dP <= d) && (m0 == l) && (mmin >= k);
    std::printf("  witness l=%d: %zu monomials, degree %d, origin mult %d, min nonzero mult >= %d: %s\n",
                l, P.size(), dP, m0, std::min(mmin, k), ok ? "verified" : "FAILED");
    return ok;
}

static std::string poly_json(int n, const std::vector<Mono>& P) {
    std::string s = "[";
    for (size_t i = 0; i < P.size(); ++i) {
        s += (i ? ",[" : "[");
        for (int j = 0; j < n; ++j) s += (j ? "," : "") + std::to_string(P[i][j]);
        s += "]";
    }
    return s + "]";
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: bmd_min_degree n k dcap [--out PATH] [--check] [--per-order]\n"); return 2; }
    int n = std::atoi(argv[1]), k = std::atoi(argv[2]), dcap = std::atoi(argv[3]);
    const char* out = nullptr; bool check = false, perOrder = false;
    for (int i = 4; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--out") && i + 1 < argc) out = argv[i + 1];
        if (!std::strcmp(argv[i], "--check")) check = true;
        if (!std::strcmp(argv[i], "--per-order")) perOrder = true;
    }
    int lower = 2 * k - k / (1 << (n - 1));          // multiplicity Schwartz-Zippel bound
    std::string json = "{\"n\":" + std::to_string(n) + ",\"k\":" + std::to_string(k) +
                       ",\"msz_lower\":" + std::to_string(lower) + ",\"dcap\":" + std::to_string(dcap) + ",\"orders\":[";
    if (!perOrder) {
        // Default: two ascending passes give D; one descending pass gives witnesses for every attaining l.
        double s0, s1, s2;
        auto r0 = rank_profile(n, k, 0, dcap, s0);
        auto rk = rank_profile(n, k, k, dcap, s1);
        long low = binom(k - 1 + n, n);               // monomials of degree < k
        int D = -1;
        for (int d = lower; d <= dcap && D < 0; ++d)
            if (r0[d] < (d < k ? 0 : rk[d]) + low) D = d;
        std::printf("passes %.1fs %.1fs; D=%d\n", s0, s1, D); std::fflush(stdout);
        std::vector<int> attaining;
        if (D >= 0) {
            auto wit = witnesses_desc(n, k, D, s2);
            std::printf("witness pass %.1fs\n", s2);
            for (int l = 0; l < k; ++l) {
                if (wit[l].empty()) continue;
                if (!verify(n, k, D, l, wit[l])) return 3;
                json += std::string(attaining.empty() ? "" : ",") + "{\"l\":" + std::to_string(l) +
                        ",\"min_degree\":" + std::to_string(D) + ",\"witness\":" + poly_json(n, wit[l]) + "}";
                attaining.push_back(l);
            }
            if (attaining.empty()) { std::printf("  INCONSISTENT: rank test says D=%d, no witness column\n", D); return 4; }
        }
        json += "],\"orders_scope\":\"attaining orders only\",\"D\":" + (D >= 0 ? std::to_string(D) : std::string("null")) + "}\n";
        std::printf("RESULT n=%d k=%d D=%d (msz lower %d)\n", n, k, D, lower);
        if (out) { FILE* f = std::fopen(out, "w"); std::fputs(json.c_str(), f); std::fclose(f); }
        return 0;
    }
    // One ascending-degree pass per lower cutoff lo = 0..k gives rank(M[lo..d]) for every d.
    std::vector<std::vector<long>> prof(k + 1);
    for (int lo = 0; lo <= k; ++lo) {
        double s; prof[lo] = rank_profile(n, k, lo, dcap, s);
        std::printf("profile lo=%d dcap=%d %.1fs\n", lo, dcap, s); std::fflush(stdout);
    }
    auto r_at = [&](int lo, int d) -> long { return d < lo ? 0 : prof[lo][d]; };
    int best = -1;
    for (int l = 0; l < k; ++l) {
        long Nl = binom(l + n - 1, n - 1);
        int found = -1;
        for (int d = std::max(lower, l); d <= dcap; ++d)
            if (r_at(l, d) < r_at(l + 1, d) + Nl) { found = d; break; }
        std::printf("n=%d k=%d l=%d min_degree=%d\n", n, k, l, found); std::fflush(stdout);
        Result r{};
        if (found >= 0) {
            r = solve(n, k, found, l);
            if (!r.exists) { std::printf("  INCONSISTENT: profile says exists at d=%d, solver disagrees\n", found); return 4; }
            if (check && found - 1 >= std::max(lower, l) && solve(n, k, found - 1, l).exists) {
                std::printf("  INCONSISTENT: solver finds d=%d below profile minimum\n", found - 1); return 4;
            }
        }
        std::string wit = "[]";
        if (found >= 0) {
            // independent verification of the witness
            int dP = 0; for (auto& m : r.witness) dP = std::max(dP, deg(m));
            int m0 = multiplicity(n, 0, r.witness, k);
            int mmin = k + 1;
            for (unsigned a = 1; a < (1u << n); ++a) mmin = std::min(mmin, multiplicity(n, a, r.witness, k - 1));
            bool ok = (dP <= found) && (m0 == l) && (mmin >= k);
            std::printf("  witness l=%d: %zu monomials, degree %d, origin mult %d, min nonzero mult >= %d: %s\n",
                        l, r.witness.size(), dP, m0, std::min(mmin, k), ok ? "verified" : "FAILED");
            if (!ok) return 3;
            wit = "[";
            for (size_t i = 0; i < r.witness.size(); ++i) {
                wit += (i ? ",[" : "[");
                for (int j = 0; j < n; ++j) wit += (j ? "," : "") + std::to_string(r.witness[i][j]);
                wit += "]";
            }
            wit += "]";
            if (best < 0 || found < best) best = found;
        }
        json += std::string(l ? "," : "") + "{\"l\":" + std::to_string(l) + ",\"min_degree\":" +
                (found >= 0 ? std::to_string(found) : std::string("null")) + ",\"witness\":" + wit + "}";
    }
    json += "],\"D\":" + (best >= 0 ? std::to_string(best) : std::string("null")) + "}\n";
    std::printf("RESULT n=%d k=%d D=%d (msz lower %d)\n", n, k, best, lower);
    if (out) { FILE* f = std::fopen(out, "w"); std::fputs(json.c_str(), f); std::fclose(f); }
    return 0;
}
