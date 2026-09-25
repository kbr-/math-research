// Point windows for the order-zero problem on {0,1}^n: the union of arc-limit spaces at a point.
//
// Statement computed.  Let W be an order-zero solution at m (W_c in F[y] homogeneous of degree m - c, W_m = 1,
// sum_c W_c [T^c] f = 0 for the basis f = T^Q z^r, r in {0,1}^n, 2Q + |r| <= d, of V_{n,d}, with
// z_i = r_0(y_i T)).  For every arc gamma through a point P, W(gamma) kills the truncations of the full-series
// saturation Lambda_gamma, so the value W(P) kills the limit space S_gamma (as in the window lemma and the
// flat-limit order bound).  If the span Sigma_P of the S_gamma over a set of arcs has an element of T-order
// exactly m, then W_m(P) = 0, which contradicts W_m = 1: no order-zero solution exists at m.  So the least m
// that is not an order of Sigma_P, over all points P tried, bounds the order-zero threshold from below.
//
// Arcs.  y(e) = P + sum_{k=1}^{L} e^k v_k, where each v_k is constant on the blocks of a random partition of
// {0, 1, ..., n} (the block of 0 gets the value 0), so that the coordinates and their differences vanish along
// the arc to many different orders.  The last level uses the finest partition with random values, so the generic
// point of the arc has nonzero, pairwise distinct coordinates.  Pure random lines are included as well.
//
// Output: for each point, the number of arcs used (and failed for precision), the orders of Sigma_P below M, and
// the least m < M that is not an order; then the least m below M that is an order at no point, the lower bound.  Exact linear algebra modulo a prime p with FLINT nmod_mat; arcs run in
// parallel with OpenMP.
//
// Usage: bmd_cube_point_windows p n d M PREC L ARCS SEED P1,...,Pn [P1,...,Pn ...]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <random>
#include <algorithm>
#include <flint/nmod_mat.h>
using namespace std;
typedef uint64_t u64;
typedef vector<u64> Vec;
static u64 P;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = r * a % P; a = a * a % P; e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }

struct Ser {  // [T^c][e^k], c < M, k < K
    int M, K; Vec a;
    Ser(int M_, int K_) : M(M_), K(K_), a((size_t)M_ * K_, 0) {}
    u64 &at(int c, int k) { return a[(size_t)c * K + k]; }
    u64 at(int c, int k) const { return a[(size_t)c * K + k]; }
};
static Ser mul(const Ser &x, const Ser &y) {
    Ser z(x.M, x.K);
    for (int i = 0; i < x.M; i++) for (int k = 0; k < x.K; k++) if (x.at(i, k)) {
        u64 v = x.at(i, k);
        for (int j = 0; i + j < x.M; j++) for (int l = 0; k + l < x.K; l++) if (y.at(j, l))
            z.at(i + j, k + l) = (z.at(i + j, k + l) + v * y.at(j, l)) % P;
    }
    return z;
}

// Left null vectors of an n x M matrix (rows), via FLINT.
static vector<Vec> left_null(const vector<Vec> &R, int M) {
    int n = R.size();
    nmod_mat_t A, X; nmod_mat_init(A, M, n, P);
    for (int i = 0; i < n; i++) for (int c = 0; c < M; c++) nmod_mat_entry(A, c, i) = R[i][c];
    nmod_mat_init(X, n, n, P);
    long nul = nmod_mat_nullspace(X, A);
    vector<Vec> out;
    for (long j = 0; j < nul; j++) { Vec v(n); for (int i = 0; i < n; i++) v[i] = nmod_mat_entry(X, i, j); out.push_back(v); }
    nmod_mat_clear(A); nmod_mat_clear(X);
    return out;
}

// Limit space of V_{n,d} along the arc ys (n series in e): rows of length M (truncation at T^M).
static bool arc_limit(int n, int d, int M, int prec, const vector<Vec> &ys, vector<Vec> &red) {
    Vec cat(M + 2); cat[0] = 1;
    for (int j = 1; j < M + 2; j++) cat[j] = cat[j - 1] * (2 * (2 * j - 1) % P) % P * inv(j + 1) % P;
    vector<Ser> z;
    for (int i = 0; i < n; i++) {
        Ser s(M, prec);
        Vec yi(prec, 0); for (size_t k = 0; k < ys[i].size() && (int)k < prec; k++) yi[k] = ys[i][k] % P;
        Vec powv(prec, 0); powv[0] = 1;
        for (int j = 1; j < M; j++) {
            Vec nx(prec, 0);
            for (int a = 0; a < prec; a++) if (powv[a]) for (int b = 0; a + b < prec; b++) if (yi[b]) nx[a + b] = (nx[a + b] + powv[a] * yi[b]) % P;
            powv = nx;
            u64 c = cat[j - 1] % P; if (j & 1) c = (P - c) % P;
            for (int k = 0; k < prec; k++) s.at(j, k) = c * powv[k] % P;
        }
        z.push_back(s);
    }
    // products z^r for all subsets r, one multiplication each
    int S = 1 << n;
    vector<Ser> zr; zr.reserve(S);
    { Ser one(M, prec); one.at(0, 0) = 1; zr.push_back(one); }
    for (int r = 1; r < S; r++) { int lo = __builtin_ctz(r); zr.push_back(mul(zr[r & (r - 1)], z[lo])); }
    vector<Ser> G;
    for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) {
        Ser g(M, prec);
        for (int c = 0; c + Q < M; c++) for (int k = 0; k < prec; k++) g.at(c + Q, k) = zr[r].at(c, k);
        G.push_back(g);
    }
    int N = G.size();
    int steps = 0;
    while (true) {
        vector<Vec> R(N, Vec(M));
        for (int i = 0; i < N; i++) for (int c = 0; c < M; c++) R[i][c] = G[i].at(c, 0);
        auto deps = left_null(R, M);
        if (deps.empty()) break;
        Vec &cf = deps[0];
        int k = -1; for (int i = N - 1; i >= 0; i--) if (cf[i]) { k = i; break; }
        Ser nw(M, prec);
        for (int i = 0; i < N; i++) if (cf[i]) for (size_t t = 0; t < nw.a.size(); t++) nw.a[t] = (nw.a[t] + cf[i] * G[i].a[t]) % P;
        Ser sh(M, prec);
        for (int c = 0; c < M; c++) for (int kk = 0; kk + 1 < prec; kk++) sh.at(c, kk) = nw.at(c, kk + 1);
        G[k] = sh;
        if (++steps >= prec - 2) return false;
    }
    red.assign(N, Vec(M));
    for (int i = 0; i < N; i++) for (int c = 0; c < M; c++) red[i][c] = G[i].at(c, 0);
    return true;
}

static vector<string> split(const string &s, char c) {
    vector<string> v; string cur; stringstream ss(s);
    while (getline(ss, cur, c)) v.push_back(cur);
    return v;
}

int main(int argc, char **argv) {
    if (argc < 10) { fprintf(stderr, "usage: p n d M PREC L ARCS SEED point [point ...]\n"); return 2; }
    P = atoll(argv[1]); int n = atoi(argv[2]), d = atoi(argv[3]), M = atoi(argv[4]), prec = atoi(argv[5]);
    int L = atoi(argv[6]), A = atoi(argv[7]); u64 seed = atoll(argv[8]);
    if (P % 2 == 0 || P <= (u64)M + 2) { fprintf(stderr, "need odd p > M + 2\n"); return 2; }
    printf("n=%d d=%d M=%d prec=%d L=%d arcs=%d p=%llu\n", n, d, M, prec, L, A, (unsigned long long)P);
    vector<char> excl(M, 0);
    for (int ai = 9; ai < argc; ai++) {
        auto parts = split(argv[ai], ',');
        if ((int)parts.size() != n) { fprintf(stderr, "point needs n coordinates\n"); return 2; }
        Vec pt(n); for (int i = 0; i < n; i++) { long long q = atoll(parts[i].c_str()); pt[i] = (u64)((q % (long long)P + (long long)P) % (long long)P); }
        vector<vector<Vec>> reds(A); vector<int> ok(A);
        #pragma omp parallel for schedule(dynamic)
        for (int a = 0; a < A; a++) {
            mt19937_64 rng(seed * 1000003 + ai * 7919 + a);
            vector<Vec> ys(n, Vec(L + 1, 0));
            for (int i = 0; i < n; i++) ys[i][0] = pt[i];
            bool line = a % 5 == 0;  // every fifth arc a random line
            for (int k = 1; k <= L; k++) {
                if (line && k > 1) break;
                vector<int> block(n + 1);
                int nb;
                if (line || k == L) { nb = n + 1; for (int i = 0; i <= n; i++) block[i] = i; }
                else { nb = 1 + rng() % (n + 1); for (int i = 0; i <= n; i++) block[i] = rng() % nb; }
                vector<u64> val(nb); for (auto &v : val) v = 1 + rng() % (P - 1);
                // coordinates in the block of index 0 get value 0 at this level
                for (int i = 0; i < n; i++) ys[i][k] = block[i + 1] == block[0] ? 0 : val[block[i + 1]];
            }
            ok[a] = arc_limit(n, d, M, prec, ys, reds[a]);
        }
        vector<Vec> rows; int failed = 0, used = 0;
        for (int a = 0; a < A; a++) { if (!ok[a]) { failed++; continue; } used++; rows.insert(rows.end(), reds[a].begin(), reds[a].end()); }
        nmod_mat_t S; nmod_mat_init(S, rows.size(), M, P);
        for (size_t i = 0; i < rows.size(); i++) for (int c = 0; c < M; c++) nmod_mat_entry(S, i, c) = rows[i][c];
        long rk = nmod_mat_rref(S);
        vector<int> ords;
        for (long i = 0; i < rk; i++) for (int c = 0; c < M; c++) if (nmod_mat_entry(S, i, c)) { ords.push_back(c); break; }
        nmod_mat_clear(S);
        int first_gap = 0; while (first_gap < M && binary_search(ords.begin(), ords.end(), first_gap)) first_gap++;
        printf("point %s: arcs used %d, failed %d; dim Sigma %ld; orders:", argv[ai], used, failed, rk);
        for (int o : ords) printf(" %d", o);
        printf("\n  first m not excluded at this point: %d\n", first_gap);
        fflush(stdout);
        for (int o : ords) excl[o] = 1;
    }
    int g = 0; while (g < M && excl[g]) g++;
    printf("union over points: least m not excluded = %d (lower bound for the order-zero threshold)\n", g);
    printf("done\n");
    return 0;
}
