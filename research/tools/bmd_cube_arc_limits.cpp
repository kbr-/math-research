// Limits of the 3-cube's constraint lattice along arcs through a point, and the span they generate.
//
// Statement tested.  Let E_m be the sheaf of solutions W (sum_c W_c [T^c] f = 0 for the basis
// f = T^Q z^r, 2Q+|r| <= d, of V_{3,d}, with z_i = r_0(y_i T) = sum_{j>=1} (-1)^j C_{j-1} y_i^j T^j)
// and P a point of P^2.  For an arc gamma: Spec F[[e]] -> P^2 with gamma(0) = P, every local section
// W of E_m at P restricts to a solution over F[[e]], which kills the saturation S_gamma of the
// lattice tau(V) (truncation mod T^(m+1)) over F[[e]].  So the value W(P) kills the reduction
// S_gamma(0) for every arc, and hence the span Sigma of the S_gamma(0) over any set of arcs.  If the
// jet e_m = T^m lies in Sigma, then W_m(P) = 0 for every local section: P lies in the zero scheme
// Z_m of lem:cube-threshold-zero-scheme.  (The values W(P) of a basis of E_m need not be
// independent, since E_m need not be a subbundle at P; Sigma may be all of F^(m+1).)
//
// For each arc (polynomials y_1(e), y_2(e), y_3(e)) the program saturates tau(V) over F_p[[e]]
// truncated at e^PREC, by repeatedly replacing a generator by (reduced dependency)/e, and records
// S_gamma(0) (dimension 4d when tau(V) has rank 4d over F_p((e))) and its orders at T = 0.  It prints
// dim(S_1 + S_i), dim Sigma and whether e_m lies in Sigma.  Arcs of one case run in parallel.
//
// First-order mode (CASE suffix ':first', chart y_2 = 1): with W(P) = 0, W = s A + t B + O(m_P^2), s = y_3,
// t = y_1 - y_2; each arc's leading vector (sigma A, tau B or sigma A + tau B by the valuations of s, t)
// kills S_gamma(0), and the program reports whether A_m and B_m are forced to vanish.
//
// Direction-bundle mode (CASE = d:m:PREC:bundle:K:J[:X:Y], chart y_2 = 1 at P = (1:1:0)); with weights (X, Y) the arcs
// are (s, t) = (sigma e^X, tau e^Y), forms are weighted-homogeneous of weighted degree k (sigma of weight X, tau of
// weight Y), and the bound reads: weighted order of a local solution >= least weighted degree of a section. Default X = Y = 1: a local solution W of order k
// at P has a tangent cone W_k(sigma, tau), a vector of degree-k forms, and along the line y = (1 + tau e, 1, sigma e)
// its leading vector W_k(sigma, tau) kills S_gamma(0). So W_k is a section of N(k), where N is the bundle on the
// exceptional line of directions whose fibre is the annihilator of tau_m(S_gamma(0)); hence k >= e_min(N). The
// program samples J random directions, computes each S_gamma(0), and for k = 0..K reports the dimension of the
// degree-k vector forms whose values kill S_gamma(0) at every sample (h^0(N(k)) once J is large enough), both
// for the first J/2 samples and for all J, so that stability can be read off. Ranks use FLINT nmod_mat.
//
// Usage: bmd_cube_arc_limits p CASE [CASE ...], CASE = d:m:PREC:ARC+ARC+...[:first | :bundle:K:J], ARC = c,c,../c,../c,..
// (coefficients of y_1, y_2, y_3 in powers of e; '1,1/1/0,1' is y = (1+e, 1, e)).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <sstream>
#include <omp.h>
#include <flint/nmod_mat.h>
#include <random>
using namespace std;
typedef uint64_t u64;
typedef vector<u64> Vec;
static u64 P;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = r * a % P; a = a * a % P; e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }

// Row echelon; returns rank. If deps != nullptr, fills left-null-space vectors (combinations of the
// original rows that vanish).
static int echelon(vector<Vec> R, vector<Vec> *deps, vector<Vec> *basis) {
    int n = R.size(); if (!n) return 0;
    int cols = R[0].size();
    vector<Vec> C(n, Vec(n, 0));
    for (int i = 0; i < n; i++) C[i][i] = 1;
    int r = 0;
    for (int c = 0; c < cols && r < n; c++) {
        int k = -1;
        for (int i = r; i < n; i++) if (R[i][c]) { k = i; break; }
        if (k < 0) continue;
        swap(R[r], R[k]); swap(C[r], C[k]);
        u64 iv = inv(R[r][c]);
        for (auto &x : R[r]) x = x * iv % P;
        for (auto &x : C[r]) x = x * iv % P;
        for (int i = 0; i < n; i++) if (i != r && R[i][c]) {
            u64 f = R[i][c];
            for (int j = 0; j < cols; j++) R[i][j] = (R[i][j] + (P - f) * R[r][j]) % P;
            for (int j = 0; j < n; j++) C[i][j] = (C[i][j] + (P - f) * C[r][j]) % P;
        }
        r++;
    }
    if (deps) for (int i = r; i < n; i++) deps->push_back(C[i]);
    if (basis) for (int i = 0; i < r; i++) basis->push_back(R[i]);
    return r;
}

struct Ser {  // [T^c][e^k], c <= m, k < prec
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

// Returns reduction matrix (4d rows of length m+1), divisions, and orders.
static bool arc_limit(int d, int m, int prec, const vector<Vec> &ys, vector<Vec> &red, int &steps, vector<int> &orders) {
    int M = m + 1;
    Vec cat(M + 2); cat[0] = 1;
    for (int j = 1; j < M + 2; j++) cat[j] = cat[j - 1] * (2 * (2 * j - 1) % P) % P * inv(j + 1) % P;
    vector<Ser> z;
    for (int i = 0; i < 3; i++) {
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
    vector<Ser> G;
    for (int Q = 0; 2 * Q <= d; Q++) for (int r = 0; r < 8; r++) {
        int w = 2 * Q + __builtin_popcount(r);
        if (w > d) continue;
        Ser g(M, prec);
        if (Q < M) g.at(Q, 0) = 1;
        for (int i = 0; i < 3; i++) if (r >> i & 1) g = mul(g, z[i]);
        G.push_back(g);
    }
    int n = G.size();
    if (n != 4 * d) return false;
    steps = 0;
    while (true) {
        vector<Vec> R(n, Vec(M));
        for (int i = 0; i < n; i++) for (int c = 0; c < M; c++) R[i][c] = G[i].at(c, 0);
        vector<Vec> deps;
        int rk = echelon(R, &deps, nullptr);
        if (rk == n) break;
        Vec &cf = deps[0];
        int k = -1; for (int i = n - 1; i >= 0; i--) if (cf[i]) { k = i; break; }
        Ser nw(M, prec);
        for (int i = 0; i < n; i++) if (cf[i]) for (size_t t = 0; t < nw.a.size(); t++) nw.a[t] = (nw.a[t] + cf[i] * G[i].a[t]) % P;
        for (int c = 0; c < M; c++) if (nw.at(c, 0)) { fprintf(stderr, "dependency not divisible\n"); exit(3); }
        Ser sh(M, prec);
        for (int c = 0; c < M; c++) for (int kk = 0; kk + 1 < prec; kk++) sh.at(c, kk) = nw.at(c, kk + 1);
        G[k] = sh;
        if (++steps >= prec - 2) return false;
    }
    red.assign(n, Vec(M));
    for (int i = 0; i < n; i++) for (int c = 0; c < M; c++) red[i][c] = G[i].at(c, 0);
    vector<Vec> B; echelon(red, nullptr, &B);
    orders.clear();
    for (auto &row : B) for (int c = 0; c < M; c++) if (row[c]) { orders.push_back(c); break; }
    return true;
}

static vector<string> split(const string &s, char c) {
    vector<string> v; string cur; stringstream ss(s);
    while (getline(ss, cur, c)) v.push_back(cur);
    return v;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: p CASE [CASE ...]\n"); return 2; }
    P = atoll(argv[1]);
    for (int ai = 2; ai < argc; ai++) {
        auto f = split(argv[ai], ':');
        int d = atoi(f[0].c_str()), m = atoi(f[1].c_str()), prec = atoi(f[2].c_str());
        if (f[3] == "bundle") {
            int K = atoi(f[4].c_str()), J = atoi(f[5].c_str());
            int X = f.size() > 7 ? atoi(f[6].c_str()) : 1, Y = f.size() > 7 ? atoi(f[7].c_str()) : 1;
            int M = m + 1;
            if (P % 2 == 0 || P <= (u64)m + 2) { fprintf(stderr, "need odd p > m + 2\n"); return 2; }
            printf("bundle d=%d m=%d rho=%d prec=%d K=%d J=%d weights=(%d,%d)\n", d, m, M - 4 * d, prec, K, J, X, Y); fflush(stdout);
            mt19937_64 rng(12345 + 1000 * d + m);
            vector<u64> sg(J), ta(J);
            for (int j = 0; j < J; j++) { sg[j] = 1 + rng() % (P - 1); ta[j] = 1 + rng() % (P - 1); }
            vector<vector<Vec>> reds(J); vector<int> ok(J), st(J); vector<vector<int>> ords(J);
            #pragma omp parallel for schedule(dynamic)
            for (int j = 0; j < J; j++) {
                Vec y1(Y + 1, 0), y3(X + 1, 0); y1[0] = 1; y1[Y] = ta[j]; y3[X] = sg[j];
                vector<Vec> ys = {y1, Vec{1}, y3};
                ok[j] = arc_limit(d, m, prec, ys, reds[j], st[j], ords[j]);
            }
            int maxsteps = 0;
            for (int j = 0; j < J; j++) {
                if (!ok[j]) { printf("  direction %d: FAILED (precision or basis size)\n", j); return 3; }
                maxsteps = max(maxsteps, st[j]);
            }
            printf("  max divisions %d (prec %d)\n", maxsteps, prec);
            for (int half = 0; half < 2; half++) {
                int Jh = half ? J : J / 2;
                printf("  samples %d: h0(N(k)) for k = 0..%d:", Jh, K);
                for (int k = 0; k <= K; k++) {
                    vector<pair<int,int>> mons;  // sigma^a tau^b with X a + Y b = k
                    for (int a = 0; X * a <= k; a++) if ((k - X * a) % Y == 0) mons.push_back({a, (k - X * a) / Y});
                    int nm = mons.size();
                    if (!nm) { printf(" 0"); continue; }
                    int cols = nm * M, rows = Jh * 4 * d;
                    nmod_mat_t A; nmod_mat_init(A, rows, cols, P);
                    int r = 0;
                    for (int j = 0; j < Jh; j++) {
                        vector<u64> cf(nm);
                        for (int i = 0; i < nm; i++) cf[i] = pw(sg[j], mons[i].first) * pw(ta[j], mons[i].second) % P;
                        for (auto &row : reds[j]) {
                            for (int i = 0; i < nm; i++) for (int c = 0; c < M; c++)
                                nmod_mat_entry(A, r, i * M + c) = cf[i] * row[c] % P;
                            r++;
                        }
                    }
                    long rk = nmod_mat_rank(A);
                    nmod_mat_clear(A);
                    printf(" %ld", (long)cols - rk);
                    fflush(stdout);
                }
                printf("\n");
            }
            fflush(stdout);
            continue;
        }
        auto arcs = split(f[3], '+');
        if (m + 1 - 4 * d < 1) { fprintf(stderr, "need rho >= 1\n"); return 2; }
        // Catalan numbers and the binomial series divide by j+1 <= m+2 through Fermat inverses.
        if (P % 2 == 0 || P <= (u64)m + 2) { fprintf(stderr, "need odd p > m + 2\n"); return 2; }
        printf("case d=%d m=%d rho=%d prec=%d\n", d, m, m + 1 - 4 * d, prec); fflush(stdout);
        int na = arcs.size();
        vector<vector<Vec>> reds(na); vector<int> st(na); vector<vector<int>> ords(na); vector<int> ok(na);
        #pragma omp parallel for schedule(dynamic)
        for (int a = 0; a < na; a++) {
            vector<Vec> ys;
            for (auto &part : split(arcs[a], '/')) { Vec v; for (auto &x : split(part, ',')) { long long q = atoll(x.c_str()); v.push_back((u64)((q % (long long)P + (long long)P) % (long long)P)); } ys.push_back(v); }
            ok[a] = arc_limit(d, m, prec, ys, reds[a], st[a], ords[a]);
        }
        for (int a = 0; a < na; a++) {
            if (!ok[a]) { printf("  arc %s: FAILED (precision or basis size)\n", arcs[a].c_str()); return 3; }
            printf("  arc %s: divisions %d; orders:", arcs[a].c_str(), st[a]);
            for (int o : ords[a]) printf(" %d", o);
            printf("\n");
            // which jets of w^i, w = (1 + 4 y_2(0) T)^(1/2) (the coordinate of the component
            // through p_0 at a double point with y_1 = y_2), lie in S_gamma(0)
            vector<Vec> B; int rk0 = echelon(reds[a], nullptr, &B);
            u64 a4 = 4 * (atoll(split(split(arcs[a], '/')[1], ',')[0].c_str()) % (long long)P) % P;
            printf("    w^i in S for i:");
            for (int i = -6 * d; i <= 6 * d; i++) {
                Vec jet(m + 1); u64 half = (u64)((i % (long long)P + (long long)P) % (long long)P) * inv(2) % P, c = 1;
                for (int k = 0; k <= m; k++) { jet[k] = c * pw(a4, k) % P; c = c * ((half + P - k) % P) % P * inv(k + 1) % P; }
                vector<Vec> S2 = B; S2.push_back(jet);
                if (echelon(S2, nullptr, nullptr) == rk0) printf(" %d", i);
            }
            printf("\n");
        }
        for (int a = 1; a < na; a++) {
            vector<Vec> S = reds[0]; S.insert(S.end(), reds[a].begin(), reds[a].end());
            printf("  dim(S_1 + S_%d) = %d\n", a + 1, echelon(S, nullptr, nullptr));
        }
        vector<Vec> S;
        for (auto &r : reds) S.insert(S.end(), r.begin(), r.end());
        int rk = echelon(S, nullptr, nullptr);
        Vec em(m + 1, 0); em[m] = 1; S.push_back(em);
        int rk2 = echelon(S, nullptr, nullptr);
        printf("d=%d m=%d rho=%d: dim Sigma = %d of %d; e_m in Sigma: %s\n", d, m, m + 1 - 4 * d, rk, m + 1, rk2 == rk ? "yes" : "no");
        if (f.size() > 4 && f[4] == "first") {
            // First order at P = (y_1, y_2, y_3)(0) with y_2 = 1: if every solution vanishes at P, write
            // W = s A + t B + O(m_P^2) with s = y_3, t = y_1 - y_2. Along an arc with v(s) = a, v(t) = b and
            // leading coefficients sigma, tau, W(gamma) = e^min(a,b) (sigma[a<=b] A + tau[b<=a] B) + ...,
            // and the leading vector kills S_gamma(0). Solve for (A, B) and report whether A_m, B_m are forced.
            int M = m + 1;
            vector<Vec> rows;
            for (int a = 0; a < na; a++) {
                auto parts = split(arcs[a], '/');
                auto co = [&](const string &s) { vector<long long> v; for (auto &x : split(s, ',')) v.push_back(atoll(x.c_str())); return v; };
                auto y1 = co(parts[0]), y2 = co(parts[1]), y3 = co(parts[2]);
                size_t L = max(y1.size(), y2.size()); vector<long long> tt(L, 0);
                for (size_t k = 0; k < L; k++) tt[k] = (k < y1.size() ? y1[k] : 0) - (k < y2.size() ? y2[k] : 0);
                int va = -1, vb = -1; long long sg = 0, ta = 0;
                for (size_t k = 1; k < y3.size(); k++) if (y3[k]) { va = k; sg = y3[k]; break; }
                for (size_t k = 1; k < L; k++) if (tt[k]) { vb = k; ta = tt[k]; break; }
                if (y3[0] || tt[0] || va < 0 || vb < 0) { printf("  first order: arc %s must pass through P with s, t != 0\n", arcs[a].c_str()); return 3; }
                u64 cA = va <= vb ? (u64)((sg % (long long)P + (long long)P) % (long long)P) : 0;
                u64 cB = vb <= va ? (u64)((ta % (long long)P + (long long)P) % (long long)P) : 0;
                for (auto &v : reds[a]) {
                    Vec r(2 * M, 0);
                    for (int c = 0; c < M; c++) { r[c] = cA * v[c] % P; r[M + c] = cB * v[c] % P; }
                    rows.push_back(r);
                }
            }
            int r0 = echelon(rows, nullptr, nullptr);
            Vec eA(2 * M, 0), eB(2 * M, 0); eA[m] = 1; eB[M + m] = 1;
            auto rA = rows; rA.push_back(eA); auto rB = rows; rB.push_back(eB);
            printf("first order: rank %d of %d; A_m forced 0: %s; B_m forced 0: %s\n", r0, 2 * M,
                   echelon(rA, nullptr, nullptr) == r0 ? "yes" : "no", echelon(rB, nullptr, nullptr) == r0 ? "yes" : "no");
        }
        fflush(stdout);
    }
    return 0;
}
