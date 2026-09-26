// Graded kernel dimensions of the threshold system on {0,1}^n and their hyperplane defects (bmd-r128).
//
// Statement computed.  For the (d+1)-system at m, K = ker A with W_c homogeneous of degree l + m - c in degree l, and
// K_L the kernel of the same system restricted to a random hyperplane L of F^n (n - 1 variables).  By
// lem:cube-restriction-exactness, if L avoids the associated primes of C = coker A other than the irrelevant ideal,
//     defect(l) := dim (K_L)_l - dim K_l + dim K_{l-1} = dim (0 :_C lambda)_{l-1} >= 0,
// and depth K >= 3 iff every defect vanishes.  lem:cube-zero-free-criterion predicts depth K_16 = depth K_17 = 2 on
// {0,1}^4 at d = 2 (over F_32003), so some defect must be positive there.
// Rows: (Q, r), r in {0,1}^n, 2Q + |r| <= d; the row polynomial is sum_c W_c A_{r, c-Q}, A_{r,j} = [T^j] prod_{i in r} w_i,
// w_i = sum_j C_j lambda_i^j T^j, C_j = binom(1/2, j) 4^j, lambda_i = y_i (full space) or a random linear form in n-1
// variables (hyperplane).  Every polynomial is homogeneous; dimension of a degree-l part is (unknowns - rank), with
// the rank by fflas-ffpack (FFPACK::Rank over Givaro::Modular<double>).  One run: all l in [LMIN, LMAX] for each m.
// Usage: bmd_cube_graded_defect p n d m1,m2,... LMIN LMAX
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
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

// homogeneous monomials of degree D in k variables, with a rank map
struct Mono { int k; vector<vector<vector<int>>> list; vector<map<vector<int>, int>> idx;
    void build(int kk, int Dmax) { k = kk; list.assign(Dmax + 1, {}); idx.assign(Dmax + 1, {});
        for (int D = 0; D <= Dmax; D++) { vector<int> e(k, 0); gen(D, 0, e); } }
    void gen(int D, int pos, vector<int> &e) {
        if (pos == k - 1) { e[pos] = D - sumof(e, pos); int s = D; idx[s][e] = list[s].size(); list[s].push_back(e); return; }
        int rem = D - sumof(e, pos); for (int a = rem; a >= 0; a--) { e[pos] = a; gen(D, pos + 1, e); } e[pos] = 0; }
    static int sumof(const vector<int> &e, int upto) { int s = 0; for (int i = 0; i < upto; i++) s += e[i]; return s; }
    int size(int D) const { return D < 0 ? 0 : (int)list[D].size(); } };

typedef vector<u64> HP;  // homogeneous polynomial: coefficients over Mono.list[D]

static HP hmul(const Mono &M, const HP &a, int da, const HP &b, int db) {
    HP c(M.size(da + db), 0);
    for (size_t i = 0; i < a.size(); i++) if (a[i]) for (size_t j = 0; j < b.size(); j++) if (b[j]) {
        vector<int> e = M.list[da][i]; for (int t = 0; t < M.k; t++) e[t] += M.list[db][j][t];
        int id = M.idx[da + db].at(e); c[id] = addm(c[id], mulm(a[i], b[j])); }
    return c;
}

// A[r][j]: homogeneous of degree j
static vector<vector<HP>> build_rows(const Mono &M, int n, int J, const vector<vector<u64>> &lam) {
    vector<u64> C(J + 1); C[0] = 1;
    for (int j = 1; j <= J; j++) { long num = 6 - 4L * j; num %= (long)P; if (num < 0) num += P; C[j] = mulm(mulm(C[j - 1], (u64)num), pw(j, P - 2)); }
    vector<vector<HP>> w(n, vector<HP>(J + 1));
    for (int i = 0; i < n; i++) { HP lin(M.size(1)); for (int t = 0; t < M.k; t++) lin[t] = lam[i][t];
        // Mono.list[1] order: generated with first variable highest; map explicitly
        HP l1(M.size(1), 0); for (int t = 0; t < M.k; t++) { vector<int> e(M.k, 0); e[t] = 1; l1[M.idx[1].at(e)] = lam[i][t]; }
        HP p(1, 1); for (int j = 0; j <= J; j++) { HP q = p; for (auto &x : q) x = mulm(x, C[j]); w[i][j] = q; if (j < J) p = hmul(M, p, j, l1, 1); } }
    int S = 1 << n; vector<vector<HP>> A(S, vector<HP>(J + 1));
    for (int j = 0; j <= J; j++) A[0][j] = HP(M.size(j), 0); A[0][0][0] = 1;
    for (int r = 1; r < S; r++) { int lo = __builtin_ctz(r), q = r & (r - 1);
        for (int j = 0; j <= J; j++) A[r][j] = HP(M.size(j), 0);
        for (int a = 0; a <= J; a++) for (int b = 0; a + b <= J; b++) { HP t = hmul(M, A[q][a], a, w[lo][b], b);
            for (size_t x = 0; x < t.size(); x++) A[r][a + b][x] = addm(A[r][a + b][x], t[x]); } }
    return A;
}

static long kernel_dim(const Mono &M, int n, int d, int m, int l, const vector<vector<HP>> &A, double &secs) {
    auto t0 = chrono::steady_clock::now();
    vector<long> off(m + 1); long nu = 0;
    for (int c = 0; c <= m; c++) { off[c] = nu; nu += M.size(l + m - c); }
    if (nu == 0) { secs = 0; return 0; }
    long nrows = 0; int S = 1 << n;
    for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) nrows += M.size(l + m - Q);
    vector<double> Mt((size_t)nrows * nu, 0.0);
    long row0 = 0;
    for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) {
        int D = l + m - Q; if (D < 0) continue;
        for (int c = Q; c <= m; c++) { int dw = l + m - c; if (dw < 0) continue; const HP &a = A[r][c - Q]; int da = c - Q;
            for (size_t i = 0; i < a.size(); i++) if (a[i]) for (int u = 0; u < M.size(dw); u++) {
                vector<int> e = M.list[da][i]; for (int t = 0; t < M.k; t++) e[t] += M.list[dw][u][t];
                size_t pos = (size_t)(row0 + M.idx[D].at(e)) * nu + off[c] + u; Mt[pos] = (double)addm((u64)Mt[pos], a[i]); } }
        row0 += M.size(D);
    }
    Givaro::Modular<double> F((double)P);
    long rk = (long)FFPACK::Rank(F, nrows, nu, Mt.data(), nu);
    secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
    return nu - rk;
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: p n d m1,m2,... LMIN LMAX\n"); return 2; }
    P = atoll(argv[1]); int n = atoi(argv[2]), d = atoi(argv[3]); int lmin = atoi(argv[5]), lmax = atoi(argv[6]);
    vector<int> ms; { string s = argv[4], x; stringstream ss(s); while (getline(ss, x, ',')) ms.push_back(atoi(x.c_str())); }
    mt19937_64 rng(128);
    vector<vector<u64>> lamF(n, vector<u64>(n, 0)), lamL(n, vector<u64>(n - 1));
    for (int i = 0; i < n; i++) lamF[i][i] = 1;
    for (int i = 0; i < n; i++) for (int t = 0; t < n - 1; t++) lamL[i][t] = 1 + rng() % (P - 1);
    for (int m : ms) {
        int Dmax = lmax + m + 1; int J = m;
        Mono MF, ML; MF.build(n, Dmax); ML.build(n - 1, Dmax);
        auto AF = build_rows(MF, n, J, lamF); auto AL = build_rows(ML, n, J, lamL);
        double s1, s2; long prev = (lmin - 1 + m >= 0) ? kernel_dim(MF, n, d, m, lmin - 1, AF, s1) : 0;
        for (int l = lmin; l <= lmax; l++) {
            long kl = kernel_dim(MF, n, d, m, l, AF, s1), kL = kernel_dim(ML, n, d, m, l, AL, s2);
            printf("n=%d d=%d m=%d l=%d: dim K_l = %ld, dim (K_L)_l = %ld, defect = %ld  (%.1f s, %.1f s)\n", n, d, m, l, kl, kL, kL - kl + prev, s1, s2);
            fflush(stdout); prev = kl;
        }
    }
    return 0;
}
