// Order-zero solvability on {0,1}^n: sparse row generation, then LinBox sparse elimination or a
// randomly compressed dense column rank profile (fflas-ffpack).
//
// Statement computed (the same system as bmd_cube_order_zero_sym.cpp).  By lem:cube-dual-polynomial-form
// at l = 0, the savings at (k, 0) on {0,1}^n are >= d+1 with m = k-1 iff some Phi(u_1..u_n) with
// Phi(0) = 1 and deg Phi <= m satisfies [Phi * z^a(u)]_{m-Q} = 0 for every a in {0,1}^n and Q >= 0
// with 2Q + |a| <= d, where z^a = prod_{a_i=1} r_0(u_i) and r_0(u) = sum_{j>=1} (-1)^j C_{j-1} u^j.
// Averaging over S_n (n! invertible) reduces to symmetric Phi = 1 + sum_lambda x_lambda m_lambda, with
// the equations for a = (1^k, 0^(n-k)) at monomials u^g, g sorted within the first k and within the
// last n-k coordinates.
//
// Exact reductions.  (1) The equations with k = 0 say that the coefficients of Phi in degrees
// m - Q (0 <= Q <= d/2) vanish, so those unknowns are dropped with their rows.  (2) The coefficient of
// u^g in m_lambda * z^a collects the exponents e (a permutation of lambda) with e_i = g_i for i >= k and
// g_i - e_i >= 1 for i < k, weighted by prod_{i<k} kappa[g_i - e_i]; the program enumerates that box
// of e directly.  e = 0 is the constant term and goes to the right-hand side b.
//
// Modes.  "sparse": rank(A) == rank([A | b]) by LinBox's sparse elimination (any odd p < 2^31).
// "compress": C = R [A | b] with R a pseudo-random (nu+3) x E matrix over GF(p), then the column rank
// profile of C by fflas-ffpack in float storage (p < 2^11); b is in the column span of A iff the last
// column is not in the profile.  For uniform R with three extra rows the chance that the profile
// differs from that of [A | b] is below 1/((p-1) p^3).
//
// Reduction every 1000 rows keeps sums below 2047 + 1000 * 2046^2 < 2^32.
// Usage: bmd_cube_order_zero_sparse MODE p n d m1 [m2 ...]   prints "solvable" / "not solvable" per m.
#include <linbox/linbox-config.h>
#include <givaro/modular.h>
#include <linbox/matrix/sparse-matrix.h>
#include <linbox/solutions/rank.h>
#include <fflas-ffpack/ffpack/ffpack.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <vector>
#include <map>
#include <unordered_map>
#include <string>
#include <algorithm>
#include <chrono>
#include <omp.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = r * a % P; a = a * a % P; e >>= 1; } return r; }

static void partitions(int n, int total, int maxpart, vector<int> &cur, vector<vector<int>> &out) {
    if (total == 0) { vector<int> v = cur; v.resize(n, 0); out.push_back(v); return; }
    if ((int)cur.size() == n) return;
    for (int x = min(total, maxpart); x >= 1; x--) { cur.push_back(x); partitions(n, total - x, x, cur, out); cur.pop_back(); }
}
static void parts_all(int n, int total, vector<vector<int>> &out) {  // sorted descending, zeros allowed
    if (total == 0) { out.push_back(vector<int>(n, 0)); return; }
    vector<int> cur; partitions(n, total, total, cur, out);
}
// compositions g of D into n parts, sorted descending within [0,k) and within [k,n)
static void blocks(int n, int k, int D, vector<vector<int>> &out) {
    for (int D1 = 0; D1 <= D; D1++) {
        vector<vector<int>> A, B;
        if (k == 0) { if (D1) continue; A.push_back({}); } else parts_all(k, D1, A);
        if (n - k == 0) { if (D - D1) continue; B.push_back({}); } else parts_all(n - k, D - D1, B);
        for (auto &a : A) for (auto &b : B) { vector<int> g = a; g.insert(g.end(), b.begin(), b.end()); out.push_back(g); }
    }
}
static u64 key(vector<int> e) { sort(e.begin(), e.end()); u64 h = 0; for (int x : e) h = h * 256 + (u64)x; return h; }

struct System { int nu = 0; vector<vector<pair<int, uint32_t>>> rows; vector<uint32_t> rhs; size_t nnz = 0; };

static System build(int n, int d, int m) {
    System S;
    vector<u64> cat(m + 2, 0), kap(m + 2, 0); cat[0] = 1;
    for (int j = 1; j <= m + 1; j++) cat[j] = cat[j - 1] * 2 % P * ((2 * j - 1) % P) % P * pw(j + 1, P - 2) % P;
    for (int j = 1; j <= m + 1; j++) kap[j] = (j % 2) ? (P - cat[j - 1]) % P : cat[j - 1];
    int top = m - d / 2;  // unknowns of degree >= top are zero by the k = 0 equations
    unordered_map<u64, int> idx;
    for (int j = 1; j < top; j++) { vector<vector<int>> t; parts_all(n, j, t); for (auto &v : t) idx[key(v)] = S.nu++; }
    for (int Q = 0; 2 * Q <= d; Q++) for (int k = 1; k <= n && 2 * Q + k <= d; k++) {
        int D = m - Q; if (D < 0) continue;
        vector<vector<int>> gs; blocks(n, k, D, gs);
        vector<vector<pair<int, uint32_t>>> part(gs.size()); vector<uint32_t> pb(gs.size(), 0);
        #pragma omp parallel for schedule(dynamic, 16)
        for (size_t gi = 0; gi < gs.size(); gi++) {
            const vector<int> &g = gs[gi];
            bool okk = true; for (int i = 0; i < k; i++) if (g[i] < 1) okk = false;
            if (!okk) continue;  // z^a has order >= 1 in each of the first k variables
            map<int, u64> row; u64 b = 0;
            vector<int> e(g); for (int i = 0; i < k; i++) e[i] = 0;
            while (true) {
                u64 c = 1; for (int i = 0; i < k; i++) c = c * kap[g[i] - e[i]] % P;
                bool zero = true; for (int x : e) if (x) { zero = false; break; }
                if (zero) b = (b + P - c) % P;
                else { auto it = idx.find(key(e)); if (it != idx.end()) { u64 &r = row[it->second]; r = (r + c) % P; } }
                int i = 0; while (i < k) { if (++e[i] < g[i]) break; e[i] = 0; i++; }
                if (i == k) break;
            }
            for (auto &kv : row) if (kv.second) part[gi].push_back({kv.first, (uint32_t)kv.second});
            pb[gi] = (uint32_t)b;
        }
        for (size_t gi = 0; gi < gs.size(); gi++) {
            if (part[gi].empty() && pb[gi] == 0) continue;
            S.nnz += part[gi].size(); S.rows.push_back(move(part[gi])); S.rhs.push_back(pb[gi]);
        }
    }
    return S;
}

static inline uint32_t rnd(u64 i, u64 j) {  // splitmix64 of (i, j), reduced mod P
    u64 z = (i * 0x9E3779B97F4A7C15ULL) ^ (j + 0xD1B54A32D192ED03ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; z ^= z >> 31;
    return (uint32_t)(z % P);
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: MODE p n d m1 [m2 ...]\n"); return 2; }
    string mode = argv[1];
    P = atoll(argv[2]); int n = atoi(argv[3]), d = atoi(argv[4]);
    if (n > 8 || (mode != "sparse" && mode != "compress")) { fprintf(stderr, "MODE sparse|compress, n <= 8\n"); return 2; }
    if (mode == "compress" && P >= 2048) { fprintf(stderr, "compress mode needs p < 2048 (float storage)\n"); return 2; }
    for (int ai = 5; ai < argc; ai++) {
        int m = atoi(argv[ai]);
        if (P % 2 == 0 || P <= (u64)m + 2 || m > 250) { fprintf(stderr, "need odd p > m + 2 and m <= 250\n"); return 2; }
        auto t0 = chrono::steady_clock::now();
        System S = build(n, d, m);
        size_t E = S.rows.size(); int nu = S.nu;
        double tb = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
        printf("n=%d d=%d m=%d: unknowns %d, equations %zu, nonzeros %zu (built in %.1f s)\n", n, d, m, nu, E, S.nnz, tb);
        fflush(stdout);
        bool sol; size_t rank;
        if (mode == "sparse") {
            typedef Givaro::Modular<uint32_t, uint64_t> Field;  // 64-bit products: p up to 2^31
            Field F(P);
            LinBox::SparseMatrix<Field> A(F, E, nu), Ab(F, E, nu + 1);
            for (size_t r = 0; r < E; r++) {
                for (auto &kv : S.rows[r]) { A.setEntry(r, kv.first, kv.second); Ab.setEntry(r, kv.first, kv.second); }
                if (S.rhs[r]) Ab.setEntry(r, nu, S.rhs[r]);
            }
            S.rows.clear(); S.rows.shrink_to_fit();
            size_t r1, r2;
            LinBox::rank(r1, A, LinBox::Method::SparseElimination());
            LinBox::rank(r2, Ab, LinBox::Method::SparseElimination());
            sol = r1 == r2; rank = r1;
        } else {
            size_t M = (size_t)nu + 3, N = (size_t)nu + 1;
            vector<uint32_t> C(M * N, 0);
            // C = R [A | b]: each thread owns a range of rows of C and streams all rows of [A | b].
            #pragma omp parallel for schedule(static)
            for (size_t i = 0; i < M; i++) {
                uint32_t *Ci = &C[i * N]; int pending = 0;
                for (size_t r = 0; r < E; r++) {
                    uint32_t c = rnd(i, r); if (!c) continue;
                    for (auto &kv : S.rows[r]) Ci[kv.first] += c * kv.second;
                    if (S.rhs[r]) Ci[nu] += c * S.rhs[r];
                    if (++pending == 1000) { for (size_t j = 0; j < N; j++) Ci[j] %= (uint32_t)P; pending = 0; }
                }
                for (size_t j = 0; j < N; j++) Ci[j] %= (uint32_t)P;
            }
            S.rows.clear(); S.rows.shrink_to_fit();
            // entries < p < 2048 are exact in float; convert in place (same width)
            static_assert(sizeof(float) == sizeof(uint32_t), "float width");
            float *Cf = reinterpret_cast<float *>(C.data());
            #pragma omp parallel for schedule(static)
            for (size_t t = 0; t < M * N; t++) { uint32_t v; memcpy(&v, &C[t], 4); float f = (float)v; memcpy(&Cf[t], &f, 4); }
            Givaro::Modular<float> F((float)P);
            size_t *prof = nullptr;
            rank = FFPACK::pColumnRankProfile(F, M, N, Cf, N, prof, omp_get_max_threads());
            sol = true; for (size_t t = 0; t < rank; t++) if (prof[t] == (size_t)nu) sol = false;
            if (!sol) rank -= 1;  // rank of A alone
            delete[] prof;
        }
        double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
        printf("n=%d d=%d m=%d: rank(A) %zu of %d unknowns: %s (%.1f s)\n", n, d, m, rank, nu, sol ? "solvable" : "not solvable", secs);
        fflush(stdout);
    }
    return 0;
}
