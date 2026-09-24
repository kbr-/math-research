// Exact per-order minimum degrees delta(n,k,l) via origin jets, for larger k than bmd_min_degree.
//
// Statement computed.  delta(n,k,l) is the least total degree of P in F_2[x_1..x_n] (formal
// polynomials) with Hasse multiplicity >= k at every nonzero point of F_2^n and multiplicity exactly
// l at the origin, for each 0 <= l < k.  The tested conjecture is delta(n,k,l) = n+2k-2-s_2(k-l-1)
// for n >= floor(log2 k)+2.
//
// Reduction.  With y_i = x_i^2 + x_i, every polynomial is uniquely sum c_{eps,e} x^eps y^e with
// eps in {0,1}^n, and its degree is max(|eps| + 2|e|) over nonzero terms (the top forms x^(eps+2e)
// are distinct monomials).  Terms with |e| >= k lie in (y)^k, contained in every m_a^k, so deleting
// them keeps every multiplicity condition below order k and does not raise the degree.  The span of
// the terms with |e| < k maps isomorphically onto the product of the jet spaces O_a/m_a^k (Chinese
// remainder theorem with (y)^k = intersection of the m_a^k).  Hence the admissible P correspond to
// origin jets v = sum_{|beta|<k} v_beta x^beta, via P(v) = sum_beta v_beta prod_i g_{beta_i}(x_i)
// mod (y)^k, where g_b = x^b (1 + x^(2^K)) with 2^K >= k equals x^b mod x^k and 0 mod (1+x)^k.
// The origin order of P(v) is the order of v.
//
// Linear algebra.  Columns are the jets beta with |beta| < k, in descending |beta|, so the jets of
// order >= l form a prefix.  The row of a basis term (eps,e) with |e| < k lists its coefficient in
// P(x^beta).  P(v) has degree <= d iff v is orthogonal to every row of degree > d.  With rows added
// in descending degree, leftmost-pivot echelon form gives the rank of every column prefix, and a
// jet of order exactly l exists in the kernel iff the pivots in the |beta| = l columns number fewer
// than those columns.  One elimination yields delta(n,k,l) for every l.
//
// Usage: bmd_jet_orders n k [--out PATH]
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
using Poly = std::vector<uint8_t>;  // coefficients over F_2, index = exponent

static Poly mul(const Poly& a, const Poly& b) {
    Poly r(a.size() + b.size() - 1, 0);
    for (size_t i = 0; i < a.size(); ++i) if (a[i])
        for (size_t j = 0; j < b.size(); ++j) r[i + j] ^= b[j];
    return r;
}

// Write f = sum_j (p_j + q_j x) y^j with y = x^2 + x (exact; f has finite degree).
static void ybasis(Poly f, std::vector<uint8_t>& p, std::vector<uint8_t>& q, int jmax) {
    p.assign(jmax, 0); q.assign(jmax, 0);
    int j = 0;
    while (true) {
        while (!f.empty() && !f.back()) f.pop_back();
        if (f.empty()) break;
        // remainder mod y is f(0) + (sum of all coefficients + f(0)) x, since y vanishes at 0 and 1
        uint8_t f0 = f[0], f1 = 0;
        for (uint8_t c : f) f1 ^= c;
        if (j < jmax) { p[j] = f0; q[j] = f0 ^ f1; }
        // f <- (f - r) / y, with r = f0 + (f0^f1) x
        Poly g = f; g[0] ^= f0; if (g.size() > 1) g[1] ^= (f0 ^ f1);
        // divide g by x^2 + x: g = x(x+1) h; divide by x then by (x+1)
        Poly h1(g.begin() + 1, g.end());  // g/x (g[0] = 0)
        // divide h1 by (x+1): synthetic division at root 1
        int m = (int)h1.size() - 1;
        Poly h(std::max(m, 0), 0);
        uint8_t carry = 0;
        for (int i = m; i >= 1; --i) { carry ^= h1[i]; h[i - 1] = carry; }
        f = h; ++j;
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: bmd_jet_orders n k [--out PATH]\n"); return 2; }
    int n = std::atoi(argv[1]), k = std::atoi(argv[2]);
    std::string out;
    int wl = -1, wd = -1;  // --witness L D: print a jet of order L with deg P(v) <= D, if one exists
    std::string jetFile;
    for (int i = 3; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--jet") && i + 1 < argc) { jetFile = argv[++i]; continue; }
        if (!std::strcmp(argv[i], "--out") && i + 1 < argc) out = argv[++i];
        else if (!std::strcmp(argv[i], "--witness") && i + 2 < argc) { wl = std::atoi(argv[++i]); wd = std::atoi(argv[++i]); }
    }
    auto t0 = std::chrono::steady_clock::now();
    int K = 0; while ((1 << K) < k) ++K;
    // per-variable tables T[eps][b][j] for b < k, j < k
    std::vector<std::vector<uint8_t>> P(k), Q(k);
    Poly idem(1 + (1 << K), 0); idem[0] = 1; idem[1 << K] = 1;
    for (int b = 0; b < k; ++b) {
        Poly xb(b + 1, 0); xb[b] = 1;
        ybasis(mul(xb, idem), P[b], Q[b], k);
    }
    // columns: beta with |beta| < k, descending |beta|
    std::vector<std::vector<int>> cols;
    { std::vector<int> cur(n, 0);
      std::vector<std::vector<int>> all;
      struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
          if (i == n) { o.push_back(cur); return; }
          for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
      R::go(0, k - 1, n, cur, all);
      std::stable_sort(all.begin(), all.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
          int sa = 0, sb = 0; for (int x : a) sa += x; for (int x : b) sb += x; return sa > sb; });
      cols = all; }
    long C = cols.size(); int W = (C + 63) / 64;
    if (!jetFile.empty()) {
        // --jet FILE: lines of n exponents; print deg P(v) for the jet v = sum of these monomials (mod m^k)
        std::vector<long> supp;
        FILE* f = std::fopen(jetFile.c_str(), "r");
        std::vector<int> b(n);
        while (true) {
            bool ok = true;
            for (int i = 0; i < n && ok; ++i) ok = std::fscanf(f, "%d", &b[i]) == 1;
            if (!ok) break;
            int s = 0; for (int x : b) s += x;
            if (s >= k) continue;
            for (long c = 0; c < C; ++c) if (cols[c] == b) { supp.push_back(c); break; }
        }
        std::fclose(f);
        std::vector<std::vector<int>> es2;
        { std::vector<int> cur(n, 0);
          struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
              if (i == n) { o.push_back(cur); return; }
              for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
          R::go(0, k - 1, n, cur, es2); }
        int top = -1;
        for (unsigned eps = 0; eps < (1u << n); ++eps)
            for (const auto& e : es2) {
                uint8_t s = 0;
                for (long c : supp) {
                    bool t = true;
                    for (int i = 0; i < n && t; ++i) t = ((eps >> i) & 1u) ? Q[cols[c][i]][e[i]] : P[cols[c][i]][e[i]];
                    s ^= t;
                }
                if (s) { int dg = __builtin_popcount(eps); for (int x : e) dg += 2 * x; top = std::max(top, dg); }
            }
        std::printf("{\"n\": %d, \"k\": %d, \"jet_terms\": %zu, \"degree\": %d}\n", n, k, supp.size(), top);
        return 0;
    }
    std::vector<int> lev(C); std::vector<long> N(k, 0);
    for (long c = 0; c < C; ++c) { int s = 0; for (int x : cols[c]) s += x; lev[c] = s; N[s]++; }
    // rows: (eps, e) with |e| < k, grouped by degree |eps| + 2|e|, descending
    int maxdeg = n + 2 * (k - 1);
    std::vector<std::vector<int>> es;
    { std::vector<int> cur(n, 0);
      struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
          if (i == n) { o.push_back(cur); return; }
          for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
      R::go(0, k - 1, n, cur, es); }
    std::vector<long> pivrow(C, -1);
    std::vector<u64> basis;  // rows of W words
    long rank = 0;
    std::vector<long> pivcount(k, 0);
    std::vector<int> delta(k, -1);
    int remaining = k;
    long rowsUsed = 0;
    for (int D = maxdeg; D >= 0 && remaining > 0; --D) {
        // generate rows of degree exactly D
        std::vector<std::pair<unsigned, int>> ids;  // (eps mask, index into es)
        for (unsigned eps = 0; eps < (1u << n); ++eps) {
            int pe = __builtin_popcount(eps);
            if ((D - pe) % 2 != 0 || D - pe < 0) continue;
            int se = (D - pe) / 2;
            for (int t = 0; t < (int)es.size(); ++t) {
                int s = 0; for (int x : es[t]) s += x;
                if (s == se) ids.push_back({eps, t});
            }
        }
        long B = ids.size();
        std::vector<u64> rows((size_t)B * W, 0);
        #pragma omp parallel for schedule(dynamic, 64)
        for (long r = 0; r < B; ++r) {
            unsigned eps = ids[r].first; const std::vector<int>& e = es[ids[r].second];
            u64* row = &rows[(size_t)r * W];
            for (long c = 0; c < C; ++c) {
                const std::vector<int>& beta = cols[c];
                bool v = true;
                for (int i = 0; i < n && v; ++i)
                    v = ((eps >> i) & 1u) ? Q[beta[i]][e[i]] : P[beta[i]][e[i]];
                if (v) row[c >> 6] |= (u64)1 << (c & 63);
            }
        }
        rowsUsed += B;
        // reduce the batch against the current basis in parallel, then insert sequentially
        auto reduce = [&](u64* row, long upto) {
            for (int w = 0; w < W; ++w) {
                while (row[w]) {
                    int bit = __builtin_ctzll(row[w]); long c = (long)w * 64 + bit;
                    long pr = pivrow[c];
                    if (pr < 0 || pr >= upto) return c;
                    const u64* br = &basis[(size_t)pr * W];
                    for (int u = w; u < W; ++u) row[u] ^= br[u];
                }
            }
            return (long)-1;
        };
        long upto = rank;
        #pragma omp parallel for schedule(dynamic, 16)
        for (long r = 0; r < B; ++r) reduce(&rows[(size_t)r * W], upto);
        for (long r = 0; r < B; ++r) {
            u64* row = &rows[(size_t)r * W];
            long c = reduce(row, rank);
            if (c < 0) continue;
            basis.insert(basis.end(), row, row + W);
            pivrow[c] = rank++;
            pivcount[lev[c]]++;
        }
        // condition at d = D - 1
        for (int l = 0; l < k; ++l)
            if (delta[l] < 0 && !(pivcount[l] < N[l])) { delta[l] = D; --remaining; }
        std::fprintf(stderr, "n=%d k=%d degree %d: %ld rows, rank %ld, open orders %d\n", n, k, D, B, rank, remaining);
        std::fflush(stderr);
        if (D == wd + 1) {
            // Back-substitute: one free column of level wl set to 1, other free columns 0.
            long freeCol = -1;
            for (long c = 0; c < C && freeCol < 0; ++c) if (lev[c] == wl && pivrow[c] < 0) freeCol = c;
            if (freeCol < 0) { std::printf("witness: none of order %d with degree <= %d\n", wl, wd); return 0; }
            std::vector<uint8_t> v(C, 0); v[freeCol] = 1;
            for (long c = C - 1; c >= 0; --c) {
                if (pivrow[c] < 0) continue;
                const u64* br = &basis[(size_t)pivrow[c] * W];
                uint8_t s = 0;
                for (long d = c + 1; d < C; ++d) if (v[d] && ((br[d >> 6] >> (d & 63)) & 1)) s ^= 1;
                v[c] = s;
            }
            // P(v) in the basis x^eps y^e, |e| < k
            std::printf("witness n=%d k=%d order %d degree<=%d; jet:", n, k, wl, wd);
            for (long c = 0; c < C; ++c) if (v[c]) { std::printf(" x^("); for (int i = 0; i < n; ++i) std::printf("%s%d", i ? "," : "", cols[c][i]); std::printf(")"); }
            std::printf("\nP(v) terms [eps | e | degree]:\n");
            int top = 0;
            for (unsigned eps = 0; eps < (1u << n); ++eps)
                for (const auto& e : es) {
                    uint8_t s = 0;
                    for (long c = 0; c < C; ++c) if (v[c]) {
                        bool t = true;
                        for (int i = 0; i < n && t; ++i) t = ((eps >> i) & 1u) ? Q[cols[c][i]][e[i]] : P[cols[c][i]][e[i]];
                        s ^= t;
                    }
                    if (!s) continue;
                    int dg = __builtin_popcount(eps); for (int x : e) dg += 2 * x;
                    top = std::max(top, dg);
                    std::printf("  ");
                    for (int i = 0; i < n; ++i) std::printf("%d", (eps >> i) & 1u);
                    std::printf(" | "); for (int i = 0; i < n; ++i) std::printf("%s%d", i ? "," : "", e[i]);
                    std::printf(" | %d\n", dg);
                }
            std::printf("witness degree %d\n", top);
            return 0;
        }
    }
    double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::string js = "{\"n\": " + std::to_string(n) + ", \"k\": " + std::to_string(k) + ", \"columns\": " +
        std::to_string(C) + ", \"rows_used\": " + std::to_string(rowsUsed) + ", \"rank\": " + std::to_string(rank) +
        ", \"seconds\": " + std::to_string(secs) + ", \"delta\": [";
    for (int l = 0; l < k; ++l) js += (l ? ", " : "") + std::to_string(delta[l]);
    js += "]}\n";
    if (!out.empty()) { FILE* f = std::fopen(out.c_str(), "w"); std::fputs(js.c_str(), f); std::fclose(f); }
    std::fputs(js.c_str(), stdout);
    return 0;
}
