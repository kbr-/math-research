// Cones at (1:1:0) of all global solutions of excess l at (d, rho) on {0,1}^3, for a range of l.
//
// Statement tested.  At (d, rho), m = 4d + rho - 1, savings h = d + 1, a solution of excess l is given by a witness P
// of degree <= 2k - d (k = l + m + 1) with multiplicity >= k at the seven nonzero vertices and origin order >= l
// (threshold-ideal lemma).  By face divisibility P = prod (x_i - 1)^d P'.  If the jet of P below degree k lies in
// J^j + m^k (J = (x1 - x2, x3)), the degree-j parts at (1:1:0) of its solution W_c are the lambda^{l+m-c-j} coefficients
// of sum_{a+b=j} R_ab(r0(lambda)) r0'(lambda)^a (-1)^b U^a S^b / delta(lambda) (lem:cube-product-cone-formula, part 1,
// which uses only the jet).  The kernel computes the whole witness space for each l, reports elements whose jet is not
// in J^j + m^k (multiplicity < j), and the rank over F(sigma, tau) of the degree-j cones of all solutions of excess
// <= l, by evaluation at a random point.  Rank rho with j = mu(d, rho) is what the squeeze lemma needs in tight cases.
//
// With a final argument "sym", the witness spaces are computed in their S_3-trivial and sign parts separately (orbit
// sums, conditions at the vertex representatives (1,0,0), (1,1,0), (1,1,1)); the standard part is not computed.
//
// With "val", it also evaluates every solution at a random point y0 (its coordinates are the coefficients of the one-
// variable series w~(t y0)) and reports the cumulative rank of the values, a lower bound for the rank over F(y).
//
// Usage: bmd_cube_solution_cones prime seed d rho j lmin lmax [sym] [val]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <array>
#include <random>
#include <string>
#include <flint/flint.h>
#include <flint/nmod_mat.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 mulm(u64 a, u64 b) { return (unsigned __int128)a * b % P; }
static u64 addm(u64 a, u64 b) { return (a + b) % P; }
static u64 subm(u64 a, u64 b) { return (a + P - b) % P; }
static u64 pw(u64 b, u64 e) { u64 r = 1; b %= P; while (e) { if (e & 1) r = mulm(r, b); b = mulm(b, b); e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }
static vector<vector<u64>> C;
static u64 binom(int n, int k) { return (k < 0 || k > n) ? 0 : C[n][k]; }
typedef vector<u64> Ser;
static bool SYM = false, VAL = false;
static const int PERMS[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
static const int PSIGN[6] = {1, -1, -1, 1, 1, -1};
static int N;
static Ser smul(const Ser &a, const Ser &b) {
    Ser r(N, 0);
    for (int i = 0; i < N; i++) if (a[i]) for (int j = 0; i + j < N; j++) r[i + j] = addm(r[i + j], mulm(a[i], b[j]));
    return r;
}
static Ser sinv(const Ser &a) {
    Ser r(N, 0); u64 i0 = inv(a[0]); r[0] = i0;
    for (int n = 1; n < N; n++) { u64 s = 0; for (int i = 1; i <= n; i++) s = addm(s, mulm(a[i], r[n - i])); r[n] = mulm((P - s) % P, i0); }
    return r;
}
static long rank_mod(vector<vector<u64>> M) {
    long r = 0; size_t rows = M.size(), cols = rows ? M[0].size() : 0;
    for (size_t c = 0; c < cols && r < (long)rows; c++) {
        size_t piv = r; while (piv < rows && !M[piv][c]) piv++;
        if (piv == rows) continue;
        swap(M[piv], M[r]); u64 iv = inv(M[r][c]);
        for (size_t i = 0; i < rows; i++) if (i != (size_t)r && M[i][c]) {
            u64 f = mulm(M[i][c], iv); for (size_t k = 0; k < cols; k++) M[i][k] = subm(M[i][k], mulm(f, M[r][k]));
        }
        r++;
    }
    return r;
}

int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage: prime seed d rho j lmin lmax [sym]\n"); return 2; }
    for (int ai = 8; ai < argc; ai++) { if (string(argv[ai]) == "sym") SYM = true; if (string(argv[ai]) == "val") VAL = true; }
    P = atoll(argv[1]); unsigned seed = atoi(argv[2]);
    int d = atoi(argv[3]), rho = atoi(argv[4]), j = atoi(argv[5]), lmin = atoi(argv[6]), lmax = atoi(argv[7]);
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    int m = 4 * d + rho - 1, e = d;  // face exponent h + 2 - n = d
    int kmax = lmax + m + 1, Dmax = 2 * kmax - d;
    C.assign(Dmax + 2, vector<u64>(Dmax + 2, 0));
    for (int n = 0; n <= Dmax + 1; n++) { C[n][0] = 1; for (int r = 1; r <= n; r++) C[n][r] = addm(C[n - 1][r - 1], r <= n - 1 ? C[n - 1][r] : 0); }
    mt19937_64 rng(seed);
    u64 tau = rng() % P, sig = rng() % P;
    u64 y0[3] = {rng() % P, rng() % P, rng() % P};  // random point for the value rank
    vector<vector<u64>> valRows;
    vector<vector<u64>> coneRows;  // evaluated cone vectors, c = 0..m
    printf("(d,rho)=(%d,%d) m=%d j=%d face exponent %d; evaluation point tau=%llu sigma=%llu\n", d, rho, m, j, e,
           (unsigned long long)tau, (unsigned long long)sig); fflush(stdout);
    if (VAL) { printf("value point y0 = (%llu, %llu, %llu)\n", (unsigned long long)y0[0], (unsigned long long)y0[1], (unsigned long long)y0[2]); fflush(stdout); }
    for (int l = lmin; l <= lmax; l++) {
      int k = l + m + 1, D = 2 * k - d, Dp = D - 3 * e;
      for (int chi = SYM ? 0 : -1; chi <= (SYM ? 1 : -1); chi++) {
        // basis of P': single monomials (dense), or S_3 orbit sums for the character chi (0 trivial, 1 sign)
        vector<vector<pair<array<int, 3>, int>>> basis;
        for (int t = l; t <= Dp; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) {
            int c = t - a - b;
            if (chi < 0) { basis.push_back({{{a, b, c}, 1}}); continue; }
            if (b > a || c > b) continue;
            array<int, 3> al = {a, b, c};
            map<array<int, 3>, int> terms;
            for (int s = 0; s < 6; s++) { array<int, 3> g; for (int i = 0; i < 3; i++) g[PERMS[s][i]] = al[i]; terms[g] += chi ? PSIGN[s] : 1; }
            vector<pair<array<int, 3>, int>> el;
            for (auto &kv : terms) if (kv.second) el.push_back({kv.first, kv.second > 0 ? 1 : -1});
            if (!el.empty()) basis.push_back(el);
        }
        int U = basis.size();
        vector<array<int, 3>> verts;
        if (chi < 0) { for (int v = 1; v < 8; v++) verts.push_back({v & 1, (v >> 1) & 1, (v >> 2) & 1}); }
        else verts = {{1, 0, 0}, {1, 1, 0}, {1, 1, 1}};
        vector<vector<pair<int, u64>>> rows;
        for (auto &vv : verts) {
            int w = vv[0] + vv[1] + vv[2], K = k - e * w;
            for (int s = 0; s < K; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--) {
                int al[3] = {a0, a1, s - a0 - a1};
                vector<pair<int, u64>> row;
                for (int u = 0; u < U; u++) {
                    u64 acc = 0;
                    for (auto &te : basis[u]) {
                        u64 c = 1; bool ok = true;
                        for (int i = 0; i < 3 && ok; i++) {
                            int bi = te.first[i];
                            if (bi < al[i] || (!vv[i] && bi != al[i])) { ok = false; break; }
                            c = mulm(c, binom(bi, al[i]));
                        }
                        if (ok) acc = te.second > 0 ? addm(acc, c) : subm(acc, c);
                    }
                    if (acc) row.push_back({u, acc});
                }
                rows.push_back(row);
            }
        }
        nmod_mat_t A, X; nmod_mat_init(A, rows.size(), U, P);
        for (size_t r = 0; r < rows.size(); r++) for (auto &en : rows[r]) nmod_mat_entry(A, r, en.first) = en.second;
        nmod_mat_init(X, U, U, P);
        long nul = nmod_mat_nullspace(X, A);
        nmod_mat_clear(A);
        // series
        N = l + m - j + 2; if (N < 2) N = 2;
        Ser lam(N, 0); lam[1] = 1;
        Ser r0(N, 0);
        for (int it = 0; it < N + 1; it++) { Ser sq = smul(r0, r0); for (int i = 0; i < N; i++) r0[i] = subm(sq[i], lam[i]); }
        Ser Lp(N, 0); for (int i = 0; i < N; i++) Lp[i] = mulm(2, r0[i]); Lp[0] = subm(Lp[0], 1);
        Ser r0p = sinv(Lp);
        Ser Delta = smul(Lp, Lp); for (auto &x : Delta) x = (P - x) % P;
        Ser Dinv = sinv(Delta);
        vector<u64> f(e + 1); for (int i = 0; i <= e; i++) { f[i] = binom(e, i); if ((e - i) & 1) f[i] = (P - f[i]) % P; }
        int lowViol = 0, exactOrder = 0;
        for (long col = 0; col < nul; col++) {
            // jet of P = Phi * P' below degree k
            map<array<int, 3>, u64> Pl;
            bool hasL = false;
            for (int u = 0; u < U; u++) {
                u64 x0 = nmod_mat_entry(X, u, col); if (!x0) continue;
                for (auto &te : basis[u]) {
                    u64 x = te.second > 0 ? x0 : (P - x0) % P;
                    auto &mo = te.first;
                    if (mo[0] + mo[1] + mo[2] == l) hasL = true;
                    for (int a = 0; a <= e; a++) for (int b = 0; b <= e; b++) for (int c = 0; c <= e; c++) {
                        array<int, 3> g = {mo[0] + a, mo[1] + b, mo[2] + c};
                        if (g[0] + g[1] + g[2] >= k) continue;
                        Pl[g] = addm(Pl[g], mulm(x, mulm(f[a], mulm(f[b], f[c]))));
                    }
                }
            }
            exactOrder += hasL;
            // normal form at order j, degrees < k
            vector<vector<u64>> R(j + 1, vector<u64>(k + 1, 0));
            map<array<int, 3>, u64> low;
            for (auto &kv : Pl) {
                u64 cf = kv.second; if (!cf) continue;
                int b1 = kv.first[0], b2 = kv.first[1], b3 = kv.first[2];
                for (int b = 0; b <= b2; b++) {
                    if (b + b3 > j) continue;
                    u64 c = mulm(cf, binom(b2, b)); if (b & 1) c = (P - c) % P;
                    if (b + b3 < j) { auto key = array<int, 3>{b1 + b2 - b, b, b3}; low[key] = addm(low[key], c); continue; }
                    R[b][b1 + b2 - b] = addm(R[b][b1 + b2 - b], c);
                }
            }
            bool viol = false; for (auto &kv : low) if (kv.second) viol = true;
            lowViol += viol;
            // G = sum_a R_a(r0) r0'^a (-1)^(j-a) U^a S^(j-a) / delta, evaluated at U = tau, S = sigma
            Ser G(N, 0);
            for (int a = 0; a <= j; a++) {
                Ser acc(N, 0);
                for (int t = k; t >= 0; t--) { acc = smul(acc, r0); acc[0] = addm(acc[0], R[a][t]); }
                for (int i = 0; i < a; i++) acc = smul(acc, r0p);
                u64 w = mulm(pw(tau, a), pw(sig, j - a)); if ((j - a) & 1) w = (P - w) % P;
                for (int i = 0; i < N; i++) G[i] = addm(G[i], mulm(acc[i], w));
            }
            G = smul(G, Dinv);
            vector<u64> row(m + 1, 0);
            for (int c = 0; c <= m; c++) { int o = l + m - c - j; if (o >= 0 && o < N) row[c] = G[o]; }
            coneRows.push_back(row);
            if (VAL) {
                // value of the solution at y0: W_c(y0) = [w~(t y0)]_{l+m-c}, w~ = P(r0(y))/prod L'(r0(y_i))
                int NV = l + m + 1, Nsave = N; N = NV;
                Ser lamv(N, 0); if (N > 1) lamv[1] = 1;
                Ser rr(N, 0);
                for (int it = 0; it < N + 1; it++) { Ser sq = smul(rr, rr); for (int i = 0; i < N; i++) rr[i] = subm(sq[i], lamv[i]); }
                vector<vector<Ser>> pows(3);
                Ser den(N, 0); den[0] = 1;
                for (int i = 0; i < 3; i++) {
                    Ser xi(N, 0); u64 yp = 1;
                    for (int n = 0; n < N; n++) { xi[n] = mulm(rr[n], yp); yp = mulm(yp, y0[i]); }  // r0(y0_i t)
                    pows[i].assign(k + 1, Ser(N, 0)); pows[i][0][0] = 1;
                    for (int a = 1; a <= k; a++) pows[i][a] = smul(pows[i][a - 1], xi);
                    Ser Lpi(N, 0); for (int n = 0; n < N; n++) Lpi[n] = mulm(2, xi[n]); Lpi[0] = subm(Lpi[0], 1);
                    den = smul(den, Lpi);
                }
                Ser val(N, 0);
                for (auto &kv : Pl) {
                    if (!kv.second) continue;
                    Ser term = smul(smul(pows[0][kv.first[0]], pows[1][kv.first[1]]), pows[2][kv.first[2]]);
                    for (int n = 0; n < N; n++) val[n] = addm(val[n], mulm(kv.second, term[n]));
                }
                val = smul(val, sinv(den));
                vector<u64> vr(m + 1, 0);
                for (int c = 0; c <= m; c++) { int o = l + m - c; if (o >= 0 && o < N) vr[c] = val[o]; }
                valRows.push_back(vr);
                N = Nsave;
            }
        }
        nmod_mat_clear(X);
        long rk = rank_mod(coneRows);
        long vrk = VAL ? rank_mod(valRows) : -1;
        printf("l=%d%s: k=%d D=%d unknowns %d, witness space dim %ld (%d with a nonzero degree-l part), %d with jet outside J^%d + m^k;"
               " cumulative cone rank %ld; cumulative value rank at a random point %ld\n", l, chi < 0 ? "" : (chi ? " (sign part)" : " (trivial part)"), k, D, U, nul, exactOrder, lowViol, j, rk, vrk);
        fflush(stdout);
      }
    }
    return 0;
}
