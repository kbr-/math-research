// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Degree-k Hilbert function of A / (P_1..P_M) for the weak unary PHP top algebra A over F_3 (n holes, n+1 pigeons,
// relations x^2, collisions x_ij x_i'j, row forms R_i = sum_j x_ij), with P_b = l_{2b}^2 l_{2b+1}^2 for linear forms given
// by row functions.  A_k splits into components by pigeon multiset; each component's row relations are sparse (n-k+1 terms)
// and are put in echelon form one component at a time, giving gamma_k.  The rank of the image of {P_b * m : m a monomial of
// degree e = k-4} in A_k equals, with high probability, the rank of the pairing matrix <P_b m, f_s> with S = (#rows + 64)
// random elements f_s of the dual of A_k (balanced functions), drawn per component by back-substitution and bit-sliced 64
// at a time, with free coordinates uniform on F_3 (so a rank falls short with probability at most about 3^-64).  The pairing is accumulated in one pass over degree-k monomials u, split as u = m + t with P_b[t] the
// coefficient of t in P_b.  Output: gamma_k, rank, H_k = gamma_k - rank.
// Input file: "n k NF" then NF families, each "M" followed by 2M forms, each (n+1) rows of n entries in {0,1,2}.  All
// families share the component eliminations and the random dual vectors; each gets its own pairing block and rank.
// Usage: board_degk INPUT [threads]
#include <bits/stdc++.h>
#include <omp.h>
using namespace std; typedef uint64_t u64;
int n, P, M, K, E;                       // holes, pigeons, constraints, target degree, multiplier degree
vector<vector<long long>> binom;
long long C(int a, int b) { return (b < 0 || b > a) ? 0 : binom[a][b]; }
long long pw(long long b, int e) { long long r = 1; while (e--) r *= b; return r; }
// rank of a monomial given as sorted (hole, pigeon) cells: subset rank (colex) * P^d + pigeon digits
long long mrank(const int* h, const int* p, int d) {
    long long s = 0; for (int i = 0; i < d; i++) s += C(h[i], i + 1);
    long long q = 0; for (int i = d - 1; i >= 0; i--) q = q * P + p[i];
    return s * pw(P, d) + q;
}
// bit-sliced F_3: value v as (a = [v==1], b = [v==2])
static inline void add3(u64& a, u64& b, u64 ya, u64 yb) {
    u64 za = (~a & ~b & ya) | (a & ~ya & ~yb) | (b & yb), zb = (~a & ~b & yb) | (b & ~ya & ~yb) | (a & ya); a = za; b = zb;
}
int main(int argc, char** argv) {
    FILE* fin = fopen(argv[1], "r"); int threads = argc > 2 ? atoi(argv[2]) : 1; omp_set_num_threads(threads);
    int NF; if (fscanf(fin, "%d %d %d", &n, &K, &NF) != 3) return 1; P = n + 1; E = K - 4;
    vector<int> famM(NF), famStart(NF); M = 0;
    vector<vector<vector<int>>> F;
    for (int fi = 0; fi < NF; fi++) { if (fscanf(fin, "%d", &famM[fi]) != 1) return 1; famStart[fi] = M; M += famM[fi];
        for (int j = 0; j < 2 * famM[fi]; j++) { vector<vector<int>> f(P, vector<int>(n)); for (auto& r : f) for (auto& x : r) if (fscanf(fin, "%d", &x) != 1) return 1; F.push_back(f); } }
    binom.assign(64, vector<long long>(64, 0)); for (int a = 0; a < 64; a++) { binom[a][0] = 1; for (int b = 1; b <= a; b++) binom[a][b] = binom[a - 1][b - 1] + binom[a - 1][b]; }
    // P_b coefficients on degree-4 monomials: sum over splits of the 4 cells into 2 for l_a^2 and 2 for l_b^2 (4 = 1 mod 3)
    long long N4 = C(n, 4) * pw(P, 4); vector<vector<uint8_t>> PB(M, vector<uint8_t>(N4, 0));
    {
        int h[4], p[4];
        for (h[0] = 0; h[0] < n; h[0]++) for (h[1] = h[0] + 1; h[1] < n; h[1]++) for (h[2] = h[1] + 1; h[2] < n; h[2]++) for (h[3] = h[2] + 1; h[3] < n; h[3]++)
        for (long long q = 0; q < pw(P, 4); q++) {
            long long qq = q; for (int i = 0; i < 4; i++) { p[i] = qq % P; qq /= P; }
            long long r = mrank(h, p, 4);
            for (int b = 0; b < M; b++) {
                auto& fa = F[2 * b]; auto& fb = F[2 * b + 1]; int s = 0;
                for (int A = 0; A < 16; A++) if (__builtin_popcount(A) == 2) {
                    int t = 1; for (int i = 0; i < 4; i++) t *= (A >> i & 1) ? fa[p[i]][h[i]] : fb[p[i]][h[i]]; s += t;
                }
                PB[b][r] = s % 3;
            }
        }
    }
    long long Nm = C(n, E) * pw(P, E); long long R = M * Nm; int maxM = *max_element(famM.begin(), famM.end()); int S = (int)(maxM * Nm) + 64; int W = (S + 63) / 64;
    // components: pigeon count vectors summing to K
    vector<vector<int>> comps; vector<int> cnt(P, 0);
    function<void(int, int)> gen = [&](int i, int left) { if (i == P) { if (!left) comps.push_back(cnt); return; } for (int c = 0; c <= left; c++) { cnt[i] = c; gen(i + 1, left - c); } cnt[i] = 0; };
    gen(0, K);
    long long gamma = 0; vector<vector<u64>> accA(threads, vector<u64>(R * W, 0)), accB(threads, vector<u64>(R * W, 0));
    long long maxfill = 0;
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:gamma) reduction(max:maxfill)
    for (size_t ci = 0; ci < comps.size(); ci++) {
        int tid = omp_get_thread_num(); auto& U = comps[ci];
        // monomials of U: hole subset (K holes) and a word of pigeons with counts U
        vector<int> word; for (int i = 0; i < P; i++) for (int c = 0; c < U[i]; c++) word.push_back(i);
        vector<vector<int>> perms; sort(word.begin(), word.end()); do perms.push_back(word); while (next_permutation(word.begin(), word.end()));
        vector<array<int, 8>> mh, mp; unordered_map<long long, int> idx;
        vector<int> hs(K); function<void(int, int)> subs = [&](int i, int start) {
            if (i == K) { for (auto& w : perms) { array<int, 8> a{}, b{}; for (int j = 0; j < K; j++) { a[j] = hs[j]; b[j] = w[j]; } idx[mrank(a.data(), b.data(), K)] = mh.size(); mh.push_back(a); mp.push_back(b); } return; }
            for (int h = start; h < n; h++) { hs[i] = h; subs(i + 1, h + 1); } };
        subs(0, 0); int d = mh.size();
        // relation rows: for each degree-(K-1) monomial m' in U - e_i: sum over free holes j of m' + (j, i)
        unordered_set<long long> seen; vector<vector<pair<int, uint8_t>>> piv(d); vector<int> pivlist;
        for (int u = 0; u < d; u++) for (int q = 0; q < K; q++) {
            int hh[8], pp[8], t = 0; for (int j = 0; j < K; j++) if (j != q) { hh[t] = mh[u][j]; pp[t] = mp[u][j]; t++; }
            long long key = mrank(hh, pp, K - 1) * P + mp[u][q]; if (!seen.insert(key).second) continue;
            vector<pair<int, uint8_t>> row; int i = mp[u][q];
            for (int j = 0; j < n; j++) {
                bool used = false; for (int x = 0; x < K - 1; x++) if (hh[x] == j) used = true; if (used) continue;
                int h2[8], p2[8], y = 0, placed = 0;
                for (int x = 0; x < K - 1; x++) { if (!placed && j < hh[x]) { h2[y] = j; p2[y] = i; y++; placed = 1; } h2[y] = hh[x]; p2[y] = pp[x]; y++; }
                if (!placed) { h2[y] = j; p2[y] = i; y++; }
                row.push_back({idx.at(mrank(h2, p2, K)), 1});
            }
            sort(row.begin(), row.end());
            // reduce against pivots (leading column = smallest index)
            while (!row.empty()) {
                int c = row[0].first;
                if (piv[c].empty()) { uint8_t inv = row[0].second; for (auto& e : row) e.second = (e.second * inv) % 3; piv[c] = row; pivlist.push_back(c); maxfill = max(maxfill, (long long)row.size()); break; }
                auto& pr = piv[c]; int f = (3 - row[0].second) % 3;   // row + f * pr kills column c (pr has leading 1)
                vector<pair<int, uint8_t>> nr; size_t a = 0, b = 0;
                while (a < row.size() || b < pr.size()) {
                    if (b == pr.size() || (a < row.size() && row[a].first < pr[b].first)) nr.push_back(row[a++]);
                    else if (a == row.size() || pr[b].first < row[a].first) { nr.push_back({pr[b].first, (uint8_t)(pr[b].second * f % 3)}); b++; }
                    else { int v = (row[a].second + f * pr[b].second) % 3; if (v) nr.push_back({row[a].first, (uint8_t)v}); a++; b++; }
                }
                row.swap(nr);
            }
        }
        gamma += d - (long long)pivlist.size();
        // random balanced functions: free coordinates random, pivot coordinates by back-substitution (decreasing pivot)
        vector<u64> fa((size_t)d * W), fb((size_t)d * W); mt19937_64 rng(1234567 + ci);
        vector<char> isp(d, 0); for (int c : pivlist) isp[c] = 1;
        for (int c = 0; c < d; c++) if (!isp[c]) for (int w = 0; w < W; w++) {   // uniform on F_3 per lane: resample lanes with (1,1)
            u64 x = rng(), y = rng(), bad = x & y;
            while (bad) { u64 x2 = rng(), y2 = rng(); x = (x & ~bad) | (x2 & bad); y = (y & ~bad) | (y2 & bad); bad = x & y; }
            fa[(size_t)c * W + w] = x; fb[(size_t)c * W + w] = y; }
        sort(pivlist.rbegin(), pivlist.rend());
        for (int p : pivlist) {
            auto& pr = piv[p]; u64* A = &fa[(size_t)p * W]; u64* B = &fb[(size_t)p * W];
            for (int w = 0; w < W; w++) { A[w] = 0; B[w] = 0; }
            for (size_t e = 1; e < pr.size(); e++) {   // f[p] = -sum_{c>p} pr[c] f[c]  (pr[p] = 1)
                int c = pr[e].first; u64* ca = &fa[(size_t)c * W]; u64* cb = &fb[(size_t)c * W];
                bool neg = (pr[e].second == 1);          // -1 * f[c] when coefficient 1, +f[c] when coefficient 2
                for (int w = 0; w < W; w++) add3(A[w], B[w], neg ? cb[w] : ca[w], neg ? ca[w] : cb[w]);
            }
        }
        // accumulate pairings: u = m + t over all splits
        auto& aA = accA[tid]; auto& aB = accB[tid];
        for (int u = 0; u < d; u++) {
            u64* ua = &fa[(size_t)u * W]; u64* ub = &fb[(size_t)u * W];
            for (int Amask = 0; Amask < (1 << K); Amask++) if (__builtin_popcount(Amask) == E) {
                int h1[8], p1[8], h2[8], p2[8], x = 0, y = 0;
                for (int j = 0; j < K; j++) if (Amask >> j & 1) { h1[x] = mh[u][j]; p1[x] = mp[u][j]; x++; } else { h2[y] = mh[u][j]; p2[y] = mp[u][j]; y++; }
                long long rm = mrank(h1, p1, E), rt = mrank(h2, p2, 4);
                for (int b = 0; b < M; b++) {
                    int c = PB[b][rt]; if (!c) continue;
                    u64* ta = &aA[(size_t)(b * Nm + rm) * W]; u64* tb = &aB[(size_t)(b * Nm + rm) * W];
                    if (c == 1) for (int w = 0; w < W; w++) add3(ta[w], tb[w], ua[w], ub[w]);
                    else for (int w = 0; w < W; w++) add3(ta[w], tb[w], ub[w], ua[w]);
                }
            }
        }
    }
    // combine thread accumulators
    vector<u64> A(R * W, 0), B(R * W, 0);
    for (int t = 0; t < threads; t++) for (size_t i = 0; i < (size_t)R * W; i++) add3(A[i], B[i], accA[t][i], accB[t][i]);
    accA.clear(); accB.clear();
    // rank of each family's pairing block over F_3 (bit-sliced Gaussian elimination)
    for (int fi = 0; fi < NF; fi++) {
    long long r0 = famStart[fi] * Nm, RF = famM[fi] * Nm, rank = 0;
    for (int col = 0; col < S && rank < RF; col++) {
        int w = col / 64; u64 bit = 1ULL << (col % 64); long long pr = -1;
        for (long long r = rank; r < RF; r++) if ((A[(r0 + r) * W + w] | B[(r0 + r) * W + w]) & bit) { pr = r; break; }
        if (pr < 0) continue;
        long long P0 = (r0 + rank) * W, PR = (r0 + pr) * W;
        if (pr != rank) for (int x = 0; x < W; x++) { swap(A[PR + x], A[P0 + x]); swap(B[PR + x], B[P0 + x]); }
        if (B[P0 + w] & bit) for (int x = 0; x < W; x++) swap(A[P0 + x], B[P0 + x]);
        #pragma omp parallel for schedule(static)
        for (long long r = rank + 1; r < RF; r++) {
            long long Q0 = (r0 + r) * W; bool one = A[Q0 + w] & bit, two = B[Q0 + w] & bit; if (!one && !two) continue;
            for (int x = w; x < W; x++) add3(A[Q0 + x], B[Q0 + x], one ? B[P0 + x] : A[P0 + x], one ? A[P0 + x] : B[P0 + x]);
        }
        rank++;
    }
    printf("family %d M %d n %d k %d gamma_k %lld rows %lld S %d rank %lld H_k %lld max_pivot_row %lld\n", fi, famM[fi], n, K, gamma, RF, S, rank, gamma - rank, maxfill);
    }
}
