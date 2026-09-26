// Order-zero solvability of the threshold system restricted to a plane of P^{n-1} (bmd-r125).
//
// Statement computed.  As in bmd_cube_line_order_zero.cpp, but restricted to the 3-dimensional subspace
// y = s v1 + t v2 + v3 of F^n (a plane of P^{n-1}), dehomogenized at the third coordinate: W_c(s,t) of total
// degree <= m - c, W_m = 1, and for every basis element f = T^Q w^r of V_{n,d} the polynomial
// sum_c W_c(s,t) A_{f,c}(s,t) (degree <= m - Q) vanishes.  Unsolvability of the restricted system implies that of
// the global order-zero system at that m.  The scan starts at MSTART: use it only when every m < MSTART is already
// excluded globally, for example by a line (any line) whose restricted system is unsolvable at every m < MSTART.
// Linear algebra: consistency by two ranks with fflas-ffpack (Givaro::Modular<double>, p < 2^26).
// Usage: bmd_cube_plane_order_zero p n d MSTART MMAX PLANE [PLANE ...]   PLANE = "rand" or a1..an:b1..bn:c1..cn
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <random>
#include <chrono>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 mulm(u64 a, u64 b) { return (unsigned __int128)a * b % P; }
static u64 addm(u64 a, u64 b) { u64 c = a + b; return c >= P ? c - P : c; }
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = mulm(r, a); a = mulm(a, a); e >>= 1; } return r; }
static vector<string> split(const string &s, char c) { vector<string> v; string x; stringstream ss(s); while (getline(ss, x, c)) v.push_back(x); return v; }

// bivariate polynomial of total degree <= D: coefficient of s^i t^j at index idx(i,j)
static int DEG;  // global cap
static inline int idx(int i, int j) { int k = i + j; return k * (k + 1) / 2 + j; }
typedef vector<u64> BP;  // size idx(DEG,0)+... = (DEG+1)(DEG+2)/2
static int bsize(int D) { return (D + 1) * (D + 2) / 2; }
static BP bmul(const BP &a, int da, const BP &b, int db, int cap) {
    int dc = min(da + db, cap); BP c(bsize(dc), 0);
    for (int ka = 0; ka <= da; ka++) for (int ja = 0; ja <= ka; ja++) { u64 x = a[idx(ka - ja, ja)]; if (!x) continue;
        for (int kb = 0; kb <= db && ka + kb <= dc; kb++) for (int jb = 0; jb <= kb; jb++) { u64 y = b[idx(kb - jb, jb)]; if (!y) continue;
            int i = ka - ja + kb - jb, j = ja + jb; c[idx(i, j)] = addm(c[idx(i, j)], mulm(x, y)); } }
    return c;
}

static long rank_of(vector<double> &M, size_t rows, size_t cols) {
    Givaro::Modular<double> F((double)P);
    return (long)FFPACK::Rank(F, rows, cols, M.data(), cols);
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: p n d MSTART MMAX PLANE...\n"); return 2; }
    P = atoll(argv[1]); int n = atoi(argv[2]), d = atoi(argv[3]), MS = atoi(argv[4]), MX = atoi(argv[5]);
    mt19937_64 rng(125);
    for (int ai = 6; ai < argc; ai++) {
        string L = argv[ai]; vector<u64> va(n), vb(n), vc(n);
        if (L == "rand") for (int i = 0; i < n; i++) { va[i] = 1 + rng() % (P - 1); vb[i] = 1 + rng() % (P - 1); vc[i] = 1 + rng() % (P - 1); }
        else { auto abc = split(L, ':'); for (int k = 0; k < 3; k++) { auto X = split(abc[k], ','); for (int i = 0; i < n; i++) { long x = atol(X[i].c_str()); u64 v = (u64)((x % (long)P + (long)P) % (long)P); (k == 0 ? va : k == 1 ? vb : vc)[i] = v; } } }
        DEG = MX;
        int M = MX + 1;
        vector<u64> C(M + 1); C[0] = 1;
        for (int j = 1; j <= M; j++) { long num = 6 - 4L * j; num %= (long)P; if (num < 0) num += P; C[j] = mulm(mulm(C[j - 1], (u64)num), pw(j, P - 2)); }
        // w_i: coefficient of T^j is C_j (a_i s + b_i t + c_i)^j, a bivariate polynomial of degree j
        int S = 1 << n;
        vector<vector<BP>> wr(S, vector<BP>(M));
        vector<vector<BP>> w(n, vector<BP>(M));
        for (int i = 0; i < n; i++) {
            BP lin(bsize(1), 0); lin[idx(0, 0)] = vc[i]; lin[idx(1, 0)] = va[i]; lin[idx(0, 1)] = vb[i];
            BP p(bsize(0), 1);
            for (int j = 0; j < M; j++) { BP t = p; for (auto &x : t) x = mulm(x, C[j]); w[i][j] = t; p = bmul(p, j, lin, 1, M); }
        }
        for (int j = 0; j < M; j++) wr[0][j] = BP(bsize(j), 0);
        wr[0][0][0] = 1;
        for (int r = 1; r < S; r++) {
            int lo = __builtin_ctz(r); int q = r & (r - 1);
            for (int j = 0; j < M; j++) wr[r][j] = BP(bsize(j), 0);
            for (int a = 0; a < M; a++) for (int b = 0; a + b < M; b++) {
                BP t = bmul(wr[q][a], a, w[lo][b], b, a + b);
                for (size_t k = 0; k < t.size(); k++) wr[r][a + b][k] = addm(wr[r][a + b][k], t[k]);
            }
        }
        int found = -1;
        for (int m = MS; m <= MX; m++) {
            auto t0 = chrono::steady_clock::now();
            vector<long> off(m + 1); long nu = 0;
            for (int c = 0; c < m; c++) { off[c] = nu; nu += bsize(m - c); }
            long nrows = 0;
            for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) nrows += bsize(m - Q);
            vector<double> Mt((size_t)nrows * (nu + 1), 0.0);
            long row0 = 0;
            for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) {
                int D = m - Q;
                for (int c = Q; c <= m; c++) {
                    const BP &A = wr[r][c - Q]; int da = c - Q;
                    for (int ka = 0; ka <= da; ka++) for (int ja = 0; ja <= ka; ja++) {
                        u64 x = A[idx(ka - ja, ja)]; if (!x) continue;
                        if (c == m) { int row = row0 + idx(ka - ja, ja); double &e = Mt[(size_t)row * (nu + 1) + nu]; e = (double)addm((u64)e, P - x); }
                        else for (int ke = 0; ke <= m - c; ke++) for (int je = 0; je <= ke; je++) {
                            int i = ka - ja + ke - je, j = ja + je; if (i + j > D) continue;
                            size_t pos = (size_t)(row0 + idx(i, j)) * (nu + 1) + off[c] + idx(ke - je, je);
                            Mt[pos] = (double)addm((u64)Mt[pos], x);
                        }
                    }
                }
                row0 += bsize(D);
            }
            vector<double> Ma((size_t)nrows * nu);
            for (long i = 0; i < nrows; i++) for (long j = 0; j < nu; j++) Ma[(size_t)i * nu + j] = Mt[(size_t)i * (nu + 1) + j];
            long rAug = rank_of(Mt, nrows, nu + 1), rA = rank_of(Ma, nrows, nu);
            double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
            printf("  n=%d d=%d plane %s m=%d: %ld equations, %ld unknowns, %s (%.1f s)\n", n, d, L.c_str(), m, nrows, nu, rA == rAug ? "solvable" : "not solvable", secs);
            fflush(stdout);
            if (rA == rAug) { found = m; break; }
        }
        printf("n=%d d=%d plane %s: least m with a restricted order-zero solution = %d\n", n, d, L.c_str(), found);
        fflush(stdout);
    }
    return 0;
}
