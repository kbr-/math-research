// Independent recheck of a symmetric factor certificate (placement dynamic program).
//
// Independent of bmd_factor_kernel.cpp: conditions are enumerated directly as (w, b, c) with b a
// non-increasing w-tuple (entries >= 0) and c a partition, sum(b) + sum(c) < K - w; for each condition
// and each partition lambda of the certificate, the number of distinct placements of lambda's nonzero
// parts (equal parts undistinguished) is counted mod 2 by recursion over positions: a one-position
// with value b takes nothing (only if b = 0) or a part p with b a bit-submask of p; a zero-position
// with value c takes exactly the part c.  The certificate passes if every condition sums to 0 mod 2,
// it contains the empty partition, and all sizes are <= D.
// Usage: bmd_recheck K D CERT_TXT   (CERT_TXT: one partition per line, parts space-separated;
//                                    an empty line is the empty partition)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
#include <omp.h>

struct Lam { std::vector<int> vals, cnt; int size; };

#include <unordered_map>
// Parity of placements of the remaining parts (counts cnt over values vals) onto one-positions
// pos[i..]: a position with value b takes nothing (only if b = 0) or a part p with b a bit-submask of
// p.  Memoized over (position, remaining counts).  Zero-positions are handled before the call: each
// takes exactly its value, in one way, so they are removed from the multiset.
static int ones_parity(const std::vector<int>& pos, size_t i, std::vector<int>& cnt, const std::vector<int>& vals,
                       int remaining, std::unordered_map<std::string, int>& memo) {
    if (remaining > (int)(pos.size() - i)) return 0;
    if (i == pos.size()) return remaining == 0 ? 1 : 0;
    std::string key(1, (char)i); for (int c : cnt) key.push_back((char)c);
    auto it = memo.find(key); if (it != memo.end()) return it->second;
    int b = pos[i], total = 0;
    if (b == 0) total ^= ones_parity(pos, i + 1, cnt, vals, remaining, memo);
    for (size_t j = 0; j < vals.size(); ++j) {
        if (!cnt[j]) continue;
        int v = vals[j];
        if (v < b || (b & ~v) != 0) continue;
        --cnt[j];
        total ^= ones_parity(pos, i + 1, cnt, vals, remaining - 1, memo);
        ++cnt[j];
    }
    memo.emplace(key, total);
    return total;
}

static int count_parity(const std::vector<std::pair<int,int>>& row, const Lam& L) {
    std::vector<int> cnt = L.cnt, ones;
    for (auto& pc : row) {
        if (pc.first == 1) { ones.push_back(pc.second); continue; }
        auto it = std::find(L.vals.begin(), L.vals.end(), pc.second);     // zero-position: exact part
        if (it == L.vals.end()) return 0;
        size_t j = it - L.vals.begin();
        if (cnt[j] == 0) return 0;
        --cnt[j];
    }
    int remaining = 0; for (int c : cnt) remaining += c;
    std::unordered_map<std::string, int> memo;
    return ones_parity(ones, 0, cnt, L.vals, remaining, memo);
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: bmd_recheck K D CERT_TXT\n"); return 2; }
    int K = std::atoi(argv[1]), D = std::atoi(argv[2]);
    FILE* f = std::fopen(argv[3], "r"); if (!f) { std::perror(argv[3]); return 2; }
    std::vector<Lam> Q; char line[4096]; bool hasEmpty = false; int maxSize = 0;
    while (std::fgets(line, sizeof line, f)) {
        std::vector<int> parts; char* s = line; char* e;
        while (true) { long v = std::strtol(s, &e, 10); if (e == s) break; parts.push_back((int)v); s = e; }
        Lam L; L.size = 0;
        std::sort(parts.rbegin(), parts.rend());
        for (int p : parts) {
            L.size += p;
            if (!L.vals.empty() && L.vals.back() == p) ++L.cnt.back(); else { L.vals.push_back(p); L.cnt.push_back(1); }
        }
        if (parts.empty()) hasEmpty = true;
        maxSize = std::max(maxSize, L.size);
        Q.push_back(L);
    }
    std::fclose(f);
    // enumerate conditions
    std::vector<std::vector<std::pair<int,int>>> rows;
    for (int w = 1; w < K; ++w) {
        int budget = K - w;                                       // sum(b) + sum(c) <= budget - 1
        std::vector<int> b(w, 0);
        // all non-increasing b with sum <= budget-1, via odometer over non-increasing tuples
        struct B { static void go(int i, int maxv, int left, std::vector<int>& b, int w, int budget,
                                   std::vector<std::vector<std::pair<int,int>>>& rows) {
            if (i == w) {
                int sb = 0; for (int x : b) sb += x;
                // all partitions c with sum <= budget-1-sb
                std::vector<int> c;
                struct C { static void go(int left, int maxp, std::vector<int>& c, const std::vector<int>& b,
                                           std::vector<std::vector<std::pair<int,int>>>& rows) {
                    std::vector<std::pair<int,int>> pos;
                    for (int x : b) pos.push_back({1, x});
                    for (int x : c) pos.push_back({0, x});
                    rows.push_back(pos);
                    for (int v = std::min(left, maxp); v >= 1; --v) { c.push_back(v); go(left - v, v, c, b, rows); c.pop_back(); }
                } };
                C::go(budget - 1 - sb, budget - 1 - sb, c, b, rows);
                return;
            }
            for (int v = std::min(maxv, left); v >= 0; --v) { b[i] = v; go(i + 1, v, left - v, b, w, budget, rows); }
        } };
        B::go(0, budget - 1, budget - 1, b, w, budget, rows);
    }
    long bad = 0;
    #pragma omp parallel for reduction(+:bad) schedule(dynamic, 8)
    for (long r = 0; r < (long)rows.size(); ++r) {
        int par = 0;
        for (const Lam& L : Q) {
            par ^= count_parity(rows[r], L);
        }
        if (par) ++bad;
    }
    bool ok = hasEmpty && maxSize <= D && bad == 0;
    std::printf("RECHECK K=%d D=%d terms=%zu rows=%zu violations=%ld has_constant=%d max_size=%d %s\n",
                K, D, Q.size(), rows.size(), bad, (int)hasEmpty, maxSize, ok ? "OK" : "FAIL");
    return ok ? 0 : 3;
}
