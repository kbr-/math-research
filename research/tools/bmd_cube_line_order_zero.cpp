// Order-zero solvability of the threshold system restricted to a line of P^{n-1} (bmd-r125).
//
// Statement computed.  An order-zero solution on {0,1}^n at m is W = (W_0..W_m), W_c in F[y] homogeneous of degree
// m - c, W_m = 1, with sum_c W_c(y) [T^c] f(y,T) = 0 for the basis f = T^Q w^r (r in {0,1}^n, 2Q+|r| <= d) of
// V_{n,d}, w_i = (1 + 4 y_i T)^{1/2}.  Restricting to the plane y = s v1 + t v2 (a line of P^{n-1}) and
// dehomogenizing t = 1 gives a solution of the restricted system: W_c(s) of degree <= m - c, W_m = 1, and for every
// f the polynomial sum_c W_c(s) A_{f,c}(s) (degree <= m - Q) vanishes.  If the restricted system has no solution,
// neither has the global one, so the least m at which the restricted system is solvable is a lower bound for the
// order-zero threshold M_n(d).  Linear algebra over F_p with FLINT nmod_mat; one run takes a list of lines and d.
// Coefficients: [T^c](T^Q w^r) = sum over j with |j| = c - Q of prod_{i in r} C_{j_i} y_i^{j_i}, C_j = binom(1/2,j)4^j.
// Usage: bmd_cube_line_order_zero p n dlist mmax LINE [LINE ...]   LINE = a1,..,an:b1,..,bn ("rand" for random)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <random>
#include <flint/nmod_mat.h>
#include <flint/nmod_poly.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static nmod_t MOD;

static vector<string> split(const string &s, char c) { vector<string> v; string x; stringstream ss(s); while (getline(ss, x, c)) v.push_back(x); return v; }

// series in T with coefficients in F_p[s] (as nmod_poly), truncated at T^M
struct Ser { vector<vector<u64>> c; };  // c[k] = poly coefficients in s

static vector<u64> polymul(const vector<u64> &a, const vector<u64> &b) {
    if (a.empty() || b.empty()) return {};
    vector<u64> r(a.size() + b.size() - 1, 0);
    for (size_t i = 0; i < a.size(); i++) if (a[i]) for (size_t j = 0; j < b.size(); j++) r[i + j] = nmod_add(r[i + j], nmod_mul(a[i], b[j], MOD), MOD);
    return r;
}
static void polyadd(vector<u64> &a, const vector<u64> &b) { if (a.size() < b.size()) a.resize(b.size(), 0); for (size_t i = 0; i < b.size(); i++) a[i] = nmod_add(a[i], b[i], MOD); }

// returns least m in [1, mmax] where the restricted order-zero system is solvable, or -1
static int least_m(int n, int d, int mmax, const vector<u64> &va, const vector<u64> &vb) {
    int M = mmax + 1;
    vector<u64> C(M + 1); C[0] = 1;
    for (int j = 1; j <= M; j++) { long num = 6 - 4L * j; num %= (long)P; if (num < 0) num += P; C[j] = nmod_mul(nmod_mul(C[j - 1], num, MOD), n_invmod(j, P), MOD); }
    // w_i(y_i T), y_i = a_i s + b_i: coefficient of T^j is C_j (a_i s + b_i)^j
    vector<Ser> w(n);
    for (int i = 0; i < n; i++) {
        w[i].c.assign(M, {});
        vector<u64> lin = {va[i] % P, vb[i] % P};  // (b + a s): index 0 is s^0 -> b; careful: lin[0] = b, lin[1] = a
        lin = {vb[i] % P, va[i] % P};
        vector<u64> pw = {1};
        for (int j = 0; j < M; j++) {
            vector<u64> t = pw; for (auto &x : t) x = nmod_mul(x, C[j], MOD);
            w[i].c[j] = t;
            pw = polymul(pw, lin);
        }
    }
    // products w^r for all subsets r
    int S = 1 << n;
    vector<Ser> wr(S);
    wr[0].c.assign(M, {}); wr[0].c[0] = {1};
    for (int r = 1; r < S; r++) {
        int lo = __builtin_ctz(r); const Ser &a = wr[r & (r - 1)], &b = w[lo];
        wr[r].c.assign(M, {});
        for (int i = 0; i < M; i++) if (!a.c[i].empty()) for (int j = 0; i + j < M; j++) if (!b.c[j].empty()) { auto t = polymul(a.c[i], b.c[j]); polyadd(wr[r].c[i + j], t); }
    }
    for (int m = 1; m <= mmax; m++) {
        // unknowns: coefficients of W_c (c = 0..m-1), degree <= m - c; W_m = 1 moved to the right-hand side
        vector<int> off(m + 1, 0); int nu = 0;
        for (int c = 0; c < m; c++) { off[c] = nu; nu += m - c + 1; }
        vector<vector<u64>> rows;
        for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) {
            // equation polynomial in s of degree <= m - Q: sum_c W_c(s) A_c(s), A_c = coefficient of T^{c-Q} of w^r
            int D = m - Q;
            vector<vector<u64>> R(D + 1, vector<u64>(nu + 1, 0));
            for (int c = Q; c <= m; c++) {
                const vector<u64> &A = wr[r].c[c - Q];
                for (size_t k = 0; k < A.size(); k++) if (A[k]) {
                    if (c == m) { if ((int)k <= D) R[k][nu] = nmod_sub(R[k][nu], A[k], MOD); }  // W_m = 1
                    else for (int e = 0; e <= m - c; e++) if ((int)(k + e) <= D) R[k + e][off[c] + e] = nmod_add(R[k + e][off[c] + e], A[k], MOD);
                }
            }
            for (auto &row : R) rows.push_back(row);
        }
        nmod_mat_t Mt; nmod_mat_init(Mt, rows.size(), nu + 1, P);
        for (size_t i = 0; i < rows.size(); i++) for (int j = 0; j <= nu; j++) nmod_mat_entry(Mt, i, j) = rows[i][j];
        long rkAug = nmod_mat_rank(Mt);
        nmod_mat_t Ma; nmod_mat_init(Ma, rows.size(), nu, P);
        for (size_t i = 0; i < rows.size(); i++) for (int j = 0; j < nu; j++) nmod_mat_entry(Ma, i, j) = rows[i][j];
        long rkA = nmod_mat_rank(Ma);
        nmod_mat_clear(Mt); nmod_mat_clear(Ma);
        if (rkA == rkAug) return m;
    }
    return -1;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: p n dlist mmax LINE...\n"); return 2; }
    P = atoll(argv[1]); nmod_init(&MOD, P);
    int n = atoi(argv[2]); auto ds = split(argv[3], ','); int mmax = atoi(argv[4]);
    mt19937_64 rng(125);
    for (int ai = 5; ai < argc; ai++) {
        string L = argv[ai]; vector<u64> va(n), vb(n);
        if (L == "rand") { for (int i = 0; i < n; i++) { va[i] = 1 + rng() % (P - 1); vb[i] = 1 + rng() % (P - 1); } }
        else {
            auto ab = split(L, ':'); auto A = split(ab[0], ','), B = split(ab[1], ',');
            for (int i = 0; i < n; i++) { long x = atol(A[i].c_str()), y = atol(B[i].c_str()); va[i] = (u64)((x % (long)P + P) % P); vb[i] = (u64)((y % (long)P + P) % P); }
        }
        for (auto &dd : ds) {
            int d = atoi(dd.c_str());
            int m = least_m(n, d, mmax, va, vb);
            printf("n=%d d=%d line %s: least m with a restricted order-zero solution = %d\n", n, d, L.c_str(), m);
            fflush(stdout);
        }
    }
    return 0;
}
