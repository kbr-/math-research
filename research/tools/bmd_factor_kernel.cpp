// Compiled solver for symmetric power-of-two factors (dimension-free conditions).
//
// Statement tested.  For K (a power of two, or any K >= 1) and degree bound D, is there a symmetric
// Q = sum_{|lambda| <= D} c_lambda m_lambda with c_() = 1 whose Hasse multiplicity is >= K - |a| at
// every point of weight 1 <= |a| < K, in every dimension?  (Dimension-free certificate lemma.)
//
// Rows.  A condition is (w, b, c): weight w, beta-values b on the w one-positions (multiset, entries
// may be 0) and positive beta-values c on zero-positions, with sum(b) + sum(c) < K - w.  The parity for
// lambda is the coefficient of t^lambda (t_v marks a part of value v) in
//   G_b(t) * prod_l t_{c_l},   G_b = prod_i ( [b_i = 0] + sum_{v >= 1, b_i bit-submask of v} t_v ),
// truncated at total size D.  G_b is built once per b by depth-first search over b with shared prefixes;
// the c-factor is a shift, so lambda's parity is G_b[lambda minus c] when c is a sub-multiset of lambda.
// Columns: all partitions of size <= D, the empty partition last.  Existence of a solution with
// c_() = 1: rank(A) == rank(A without the constant column).  Reports the kernel dimension too, and
// writes one solution (Gauss-Jordan, constant column last) for independent checking.
//
// Usage: bmd_factor_kernel K D [--out PATH]
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <chrono>
#include <omp.h>
using u64 = uint64_t;
using Part = std::vector<int>;   // non-increasing positive parts

static int K, Dg;
static std::vector<Part> parts;                 // all partitions of size <= Dg
static std::map<Part, int> index_of;
static std::vector<std::vector<int>> addv;      // addv[p][v] = index of p + {v}, or -1

static void gen(Part& cur, int left, int maxp) {
    parts.push_back(cur);
    for (int v = std::min(left, maxp); v >= 1; --v) { cur.push_back(v); gen(cur, left - v, v); cur.pop_back(); }
}
static int size_of(const Part& p) { int s = 0; for (int x : p) s += x; return s; }

// multiply bitset-like vector G (indexed by partitions) by the factor for one one-position with value b
static std::vector<char> times_factor(const std::vector<char>& G, int b) {
    std::vector<char> R(parts.size(), 0);
    for (size_t p = 0; p < parts.size(); ++p) {
        if (!G[p]) continue;
        if (b == 0) R[p] ^= 1;
        for (int v = std::max(b, 1); v <= Dg; ++v) {
            if ((b & ~v) != 0) continue;
            int q = addv[p][v];
            if (q >= 0) R[q] ^= 1;
        }
    }
    return R;
}

static std::vector<std::vector<int>> rowcols;   // for each condition row, list of column indices with odd parity

// enumerate c (partitions with sum < budget, positive parts) and emit rows for fixed G
static void emit_rows(const std::vector<char>& G, int budget) {
    // c ranges over partitions of size < budget (including empty)
    std::vector<Part> cs;
    Part cur;
    struct R { static void go(Part& cur, int left, int maxp, std::vector<Part>& out) {
        out.push_back(cur);
        for (int v = std::min(left, maxp); v >= 1; --v) { cur.push_back(v); go(cur, left - v, v, out); cur.pop_back(); }
    } };
    if (budget <= 0) return;
    R::go(cur, budget - 1, budget - 1, cs);
    for (const Part& c : cs) {
        // columns lambda = mu + c for mu in supp(G)
        std::vector<int> cols;
        for (size_t p = 0; p < parts.size(); ++p) {
            if (!G[p]) continue;
            int q = (int)p;
            for (int v : c) { q = addv[q][v]; if (q < 0) break; }
            if (q >= 0) cols.push_back(q);
        }
        // parity: a lambda can arise from only one mu (mu = lambda minus c), so no duplicates
        rowcols.push_back(cols);
    }
}

static void dfs_b(int w, int pos, int maxb, int sumb, std::vector<char>& G) {
    if (pos == w) { emit_rows(G, K - w - sumb); return; }
    for (int b = std::min(maxb, K - w - 1 - sumb); b >= 0; --b) {
        auto G2 = times_factor(G, b);
        dfs_b(w, pos + 1, b, sumb + b, G2);
    }
}

int main(int argc, char** argv) {
    if (argc < 3) { std::fprintf(stderr, "usage: bmd_factor_kernel K D [--out PATH]\n"); return 2; }
    K = std::atoi(argv[1]); Dg = std::atoi(argv[2]);
    const char* out = (argc >= 5 && !std::strcmp(argv[3], "--out")) ? argv[4] : nullptr;
    auto t0 = std::chrono::steady_clock::now();
    Part cur; gen(cur, Dg, Dg);
    // put the empty partition last (constant column)
    std::rotate(parts.begin(), parts.begin() + 1, parts.end());
    for (size_t i = 0; i < parts.size(); ++i) index_of[parts[i]] = (int)i;
    addv.assign(parts.size(), std::vector<int>(Dg + 1, -1));
    for (size_t i = 0; i < parts.size(); ++i) {
        int s = size_of(parts[i]);
        for (int v = 1; v + s <= Dg; ++v) {
            Part q = parts[i]; q.push_back(v); std::sort(q.rbegin(), q.rend());
            addv[i][v] = index_of[q];
        }
    }
    int empty = (int)parts.size() - 1;
    for (int w = 1; w < K; ++w) {
        std::vector<char> G(parts.size(), 0); G[empty] = 1;
        dfs_b(w, 0, K - w - 1, 0, G);
    }
    long R = (long)rowcols.size(), C = (long)parts.size(), W = (C + 63) / 64;
    std::printf("K=%d D=%d partitions=%ld rows=%ld build %.1fs\n", K, Dg, C, R,
                std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
    std::fflush(stdout);
    std::vector<u64> M((size_t)R * W, 0);
    for (long r = 0; r < R; ++r) for (int c : rowcols[r]) M[(size_t)r * W + (c >> 6)] ^= (1ULL << (c & 63));
    // Gauss-Jordan, columns in order (constant column last)
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
    bool constPivot = !pivcol.empty() && pivcol.back() == C - 1;
    bool exists = !constPivot;
    long kernel = C - rank;
    std::printf("rank=%ld kernel_dim=%ld exists_with_constant_1=%d total %.1fs\n", rank, kernel, (int)exists,
                std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count());
    if (out) {
        FILE* f = std::fopen(out, "w");
        std::fprintf(f, "{\"K\":%d,\"D\":%d,\"partitions\":%ld,\"rows\":%ld,\"rank\":%ld,\"kernel_dim\":%ld,\"exists\":%s",
                     K, Dg, C, R, rank, kernel, exists ? "true" : "false");
        if (exists) {
            // solution: free constant column = 1, other free = 0; pivot x_p = row[p] bit at constant column
            std::fprintf(f, ",\"Q\":[");
            bool first = true;
            auto emit = [&](long c) {
                std::fprintf(f, "%s[", first ? "" : ","); first = false;
                for (size_t i = 0; i < parts[c].size(); ++i) std::fprintf(f, "%s%d", i ? "," : "", parts[c][i]);
                std::fprintf(f, "]");
            };
            emit(C - 1);
            for (long i = 0; i < rank; ++i) if (M[(size_t)i * W + ((C - 1) >> 6)] & (1ULL << ((C - 1) & 63))) emit(pivcol[i]);
            std::fprintf(f, "]");
        }
        std::fprintf(f, "}\n"); std::fclose(f);
    }
    return 0;
}
