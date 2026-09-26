// Point-supported certificates of order-zero unsolvability on {0,1}^n (bmd-r129).
//
// Statement computed.  The order-zero system at m asks for W_0..W_{m-1} (W_c homogeneous of degree m - c) with
// A_{m-1} W = -a_m, where a_m is the column of W_m = 1 (row (Q, r): [T^{m-Q}] prod_{i in r} w_i, a form of degree
// m - Q).  It is unsolvable iff some linear functional y on the target forms (row (Q, r): forms of degree m - Q)
// vanishes on the image of A_{m-1} and not on a_m.  This program restricts y to functionals supported on a finite
// point set Z: linear combinations of the jets of order <= k of each row component at each point of Z.  It reports
// whether such a certificate exists: rank [E A | E a] > rank [E A], with E the jet functionals.
//   A certificate supported on one point is a point window (lem:cube-point-window-membership, via arcs); on
//   {0,1}^4 at d = 2, m = 17, 18 no single point carries one (V(I_m) is empty), so a certificate supported on an
//   orbit would be a collective (Cayley-Bacharach type) obstruction.
// Point sets: "springer" = S_5-orbit of the pentagon point y_i = zeta^i - 1 (24 points, n = 4, p = 1 mod 5);
// "springer1" = its first point; "double3" = (1,1,0), (1,0,1), (0,1,1) (n = 3); "random:N" = N random points.
// Usage: bmd_cube_orbit_certificate p n d m KMAX POINTSET   (reports k = 0..KMAX)
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <set>
#include <string>
#include <random>
#include <algorithm>
#include <chrono>
#include <functional>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 mulm(u64 a, u64 b) { return (unsigned __int128)a * b % P; }
static u64 addm(u64 a, u64 b) { u64 c = a + b; return c >= P ? c - P : c; }
static u64 subm(u64 a, u64 b) { return a >= b ? a - b : a + P - b; }
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = mulm(r, a); a = mulm(a, a); e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }

static int n;
// monomials of degree exactly D in n variables, and of degree <= k (jets)
static vector<vector<int>> monos(int D) { vector<vector<int>> out; vector<int> e(n, 0);
    function<void(int, int)> rec = [&](int pos, int rem) { if (pos == n - 1) { e[pos] = rem; out.push_back(e); return; }
        for (int a = rem; a >= 0; a--) { e[pos] = a; rec(pos + 1, rem - a); } };
    rec(0, D); return out; }
struct Poly { map<vector<int>, u64> c; };
static Poly pmul(const Poly &a, const Poly &b) { Poly r; for (auto &x : a.c) for (auto &y : b.c) { vector<int> e = x.first;
    for (int i = 0; i < n; i++) e[i] += y.first[i]; u64 &z = r.c[e]; z = addm(z, mulm(x.second, y.second)); } return r; }

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: p n d m KMAX POINTSET\n"); return 2; }
    P = atoll(argv[1]); n = atoi(argv[2]); int d = atoi(argv[3]), m = atoi(argv[4]), KMAX = atoi(argv[5]); string ps = argv[6];
    // binomials mod P
    vector<vector<u64>> B(m + 2, vector<u64>(m + 2, 0)); for (int i = 0; i <= m + 1; i++) { B[i][0] = 1; for (int j = 1; j <= i; j++) B[i][j] = addm(B[i - 1][j - 1], j < i ? B[i - 1][j] : 0); }
    // points
    vector<vector<u64>> Z; mt19937_64 rng(129);
    if (ps == "springer" || ps == "springer1") {
        if (n != 4 || (P - 1) % 5) { fprintf(stderr, "springer needs n = 4 and p = 1 mod 5\n"); return 2; }
        u64 zeta = 0; for (u64 g = 2; ; g++) { zeta = pw(g, (P - 1) / 5); if (zeta != 1) break; }
        vector<u64> r(5); for (int i = 0; i < 5; i++) r[i] = pw(zeta, i);
        vector<int> sg = {0, 1, 2, 3, 4}; set<vector<u64>> seen;
        do { vector<u64> y(4); for (int i = 0; i < 4; i++) y[i] = subm(r[sg[i + 1]], r[sg[0]]);
             int f = 0; while (y[f] == 0) f++; u64 s = inv(y[f]); for (auto &x : y) x = mulm(x, s);
             if (!seen.count(y)) { seen.insert(y); Z.push_back(y); } } while (next_permutation(sg.begin(), sg.end()));
        if (ps == "springer1") Z.resize(1);
    } else if (ps == "double3") { Z = {{1, 1, 0}, {1, 0, 1}, {0, 1, 1}}; }
    else if (ps.rfind("random:", 0) == 0) { int N = atoi(ps.c_str() + 7); for (int t = 0; t < N; t++) { vector<u64> y(n); for (auto &x : y) x = 1 + rng() % (P - 1); Z.push_back(y); } }
    else { fprintf(stderr, "unknown point set\n"); return 2; }
    printf("point set %s: %zu points\n", ps.c_str(), Z.size()); fflush(stdout);
    // rows (Q, r) and A_{r, j} = [T^j] prod_{i in r} w_i as polynomials
    vector<u64> C(m + 1); C[0] = 1; for (int j = 1; j <= m; j++) { long num = 6 - 4L * j; num %= (long)P; if (num < 0) num += P; C[j] = mulm(mulm(C[j - 1], (u64)num), inv(j)); }
    int S = 1 << n; vector<vector<Poly>> A(S, vector<Poly>(m + 1));
    for (int j = 0; j <= m; j++) A[0][j] = Poly(); { vector<int> z(n, 0); A[0][0].c[z] = 1; }
    for (int r = 1; r < S; r++) { int lo = __builtin_ctz(r), q = r & (r - 1);
        for (int a = 0; a <= m; a++) for (int b = 0; a + b <= m; b++) { Poly wb; vector<int> e(n, 0); e[lo] = b; wb.c[e] = C[b];
            Poly t = pmul(A[q][a], wb); for (auto &x : t.c) { u64 &z = A[r][a + b].c[x.first]; z = addm(z, x.second); } } }
    vector<pair<int, int>> rows; for (int r = 0; r < S; r++) for (int Q = 0; 2 * Q + __builtin_popcount(r) <= d; Q++) rows.push_back({Q, r});
    for (int k = 0; k <= KMAX; k++) {
        auto t0 = chrono::steady_clock::now();
        vector<vector<int>> J; for (int D = 0; D <= k; D++) for (auto &e : monos(D)) J.push_back(e);
        map<vector<int>, int> Jidx; for (size_t i = 0; i < J.size(); i++) Jidx[J[i]] = i;
        // jet of a polynomial at a point: coefficient of h^alpha in f(p + h) = sum_e c_e prod binom(e_i, a_i) p_i^(e_i - a_i)
        auto jet = [&](const Poly &f, const vector<u64> &p) { vector<u64> out(J.size(), 0);
            for (auto &x : f.c) for (size_t a = 0; a < J.size(); a++) { u64 v = x.second; bool ok = true;
                for (int i = 0; i < n && ok; i++) { if (J[a][i] > x.first[i]) { ok = false; break; } v = mulm(v, mulm(B[x.first[i]][J[a][i]], pw(p[i], x.first[i] - J[a][i]))); }
                if (ok) out[a] = addm(out[a], v); } return out; };
        auto jmul = [&](const vector<u64> &a, const vector<u64> &b) { vector<u64> out(J.size(), 0);
            for (size_t i = 0; i < J.size(); i++) if (a[i]) for (size_t j = 0; j < J.size(); j++) if (b[j]) { vector<int> e = J[i];
                int s = 0; for (int t = 0; t < n; t++) { e[t] += J[j][t]; s += e[t]; } if (s > k) continue; size_t id = Jidx[e]; out[id] = addm(out[id], mulm(a[i], b[j])); }
            return out; };
        // jets of A_{r, j} at each point
        size_t nz = Z.size(), nf = nz * rows.size() * J.size();
        vector<vector<vector<vector<u64>>>> JA(nz, vector<vector<vector<u64>>>(S, vector<vector<u64>>(m + 1)));
        for (size_t z = 0; z < nz; z++) for (int r = 0; r < S; r++) for (int j = 0; j <= m; j++) JA[z][r][j] = jet(A[r][j], Z[z]);
        // source basis: (c, u), c = 0..m-1, u monomial of degree m - c; plus the column a_m
        vector<pair<int, vector<int>>> src; for (int c = 0; c < m; c++) for (auto &u : monos(m - c)) src.push_back({c, u});
        size_t nr = src.size() + 1;
        vector<double> M(nr * nf, 0.0);
        for (size_t s = 0; s <= src.size(); s++) {
            bool isA = (s == src.size()); int c = isA ? m : src[s].first;
            for (size_t z = 0; z < nz; z++) {
                vector<u64> ju; if (!isA) { Poly pu; pu.c[src[s].second] = 1; ju = jet(pu, Z[z]); }
                for (size_t ro = 0; ro < rows.size(); ro++) { int Q = rows[ro].first, r = rows[ro].second; if (c < Q) continue;
                    vector<u64> v = isA ? JA[z][r][c - Q] : jmul(ju, JA[z][r][c - Q]);
                    for (size_t a = 0; a < J.size(); a++) M[s * nf + (z * rows.size() + ro) * J.size() + a] = (double)v[a]; } }
        }
        Givaro::Modular<double> F((double)P);
        vector<double> M2(M.begin(), M.begin() + (nr - 1) * nf);
        long rAll = (long)FFPACK::Rank(F, nr, nf, M.data(), nf), rA = (long)FFPACK::Rank(F, nr - 1, nf, M2.data(), nf);
        double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
        printf("n=%d d=%d m=%d %s k=%d: %zu functionals, %zu source columns, rank EA = %ld, with a_m = %ld: certificate %s  (%.1f s)\n",
               n, d, m, ps.c_str(), k, nf, nr - 1, rA, rAll, rAll > rA ? "EXISTS" : "none", secs);
        fflush(stdout);
    }
    return 0;
}
