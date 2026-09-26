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
// With first argument "series", it decides for each prime in a comma-separated list and each case d:rho:lmin:lmax
// whether a witness of origin order exactly l exists (the dimension of the space of degree-l parts of the witnesses of
// origin order >= l), which is exact over F_p with no random point; savings >= d+1 at (k, l) holds exactly when it
// is positive, so l_0(d+1, m) is the least such l.  Face division is valid over every field (prop:cube-face-divisibility).
//
// With the environment variable YPTS="a,b,c/..." (or ; as separator), the solutions are also evaluated at these fixed points (entries taken
// mod P, negative allowed), and the cumulative value rank at each is reported; in series mode YPTS switches from the order
// test to this evaluation (SYM=1 in the environment selects the S_3 parts).
//
// Usage: bmd_cube_solution_cones prime seed d rho j lmin lmax [sym] [val]
//        bmd_cube_solution_cones series p1,p2,... d:rho:lmin:lmax ...
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
static vector<array<u64, 3>> EXTRA_PTS;  // fixed evaluation points from YPTS="a,b,c;a,b,c" (env), mod P
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

static bool ORDERONLY = false;
static int run(unsigned seed, int d, int rho, int j, int lmin, int lmax);
static void parse_pts() {
    const char *e = getenv("YPTS"); if (!e) return;
    string s = e; size_t a = 0;
    while (a < s.size()) {
        size_t b = s.find_first_of(";/", a); if (b == string::npos) b = s.size();
        long long v[3]; if (sscanf(s.substr(a, b - a).c_str(), "%lld,%lld,%lld", &v[0], &v[1], &v[2]) == 3) {
            array<u64, 3> p; for (int i = 0; i < 3; i++) p[i] = (u64)((v[i] % (long long)P + (long long)P) % (long long)P); EXTRA_PTS.push_back(p);
        }
        a = b + 1;
    }
}
int main(int argc, char **argv) {
    if (argc >= 4 && string(argv[1]) == "series") {
        ORDERONLY = true;
        vector<u64> primes; { string ps = argv[2]; size_t a = 0; while (a < ps.size()) { size_t b = ps.find(',', a); if (b == string::npos) b = ps.size(); primes.push_back(atoll(ps.substr(a, b - a).c_str())); a = b + 1; } }
        for (int ai = 3; ai < argc; ai++) {
            int d, rho, lmin, lmax; if (sscanf(argv[ai], "%d:%d:%d:%d", &d, &rho, &lmin, &lmax) != 4) { fprintf(stderr, "bad case %s\n", argv[ai]); return 2; }
            for (u64 p : primes) {
                P = p; EXTRA_PTS.clear(); parse_pts();
                if (!EXTRA_PTS.empty()) { ORDERONLY = false; VAL = true; SYM = getenv("SYM") != nullptr; }
                printf("prime %llu ", (unsigned long long)p); run(1, d, rho, EXTRA_PTS.empty() ? 0 : 2, lmin, lmax);
            }
        }
        return 0;
    }
    if (argc < 8) { fprintf(stderr, "usage: prime seed d rho j lmin lmax [sym]\n"); return 2; }
    for (int ai = 8; ai < argc; ai++) { if (string(argv[ai]) == "sym") SYM = true; if (string(argv[ai]) == "val") VAL = true; }
    P = atoll(argv[1]); unsigned seed = atoi(argv[2]);
    parse_pts();
    return run(seed, atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), atoi(argv[6]), atoi(argv[7]));
}
static int run(unsigned seed, int d, int rho, int j, int lmin, int lmax) {
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    int m = 4 * d + rho - 1, e = d;  // face exponent h + 2 - n = d
    int kmax = lmax + m + 1, Dmax = 2 * kmax - d;
    C.assign(Dmax + 2, vector<u64>(Dmax + 2, 0));
    for (int n = 0; n <= Dmax + 1; n++) { C[n][0] = 1; for (int r = 1; r <= n; r++) C[n][r] = addm(C[n - 1][r - 1], r <= n - 1 ? C[n - 1][r] : 0); }
    mt19937_64 rng(seed);
    u64 tau = rng() % P, sig = rng() % P;
    u64 y0[3] = {rng() % P, rng() % P, rng() % P};  // random point for the value rank
    vector<vector<u64>> valRows;
    vector<vector<vector<u64>>> extraRows(EXTRA_PTS.size());
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
        // Conditions (vertex, Hasse index alpha) are generated in chunks, in parallel, and eliminated against a
        // running reduced echelon form, so peak memory is about (U + CH) x U entries rather than all rows x U plus a
        // U x U nullspace.  The kernel is then read off the reduced form: one vector per free column.
        vector<pair<int, array<int, 3>>> conds;
        for (size_t vi = 0; vi < verts.size(); vi++) {
            auto &vv = verts[vi];
            int w = vv[0] + vv[1] + vv[2], K = k - e * w;
            for (int s = 0; s < K; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--)
                conds.push_back({(int)vi, {a0, a1, s - a0 - a1}});
        }
        const long CH = 4096;
        nmod_mat_t M; nmod_mat_init(M, U + CH, U, P);
        long R = 0;
        for (size_t c0 = 0; c0 < conds.size(); c0 += CH) {
            long c = min((long)CH, (long)(conds.size() - c0));
            #pragma omp parallel for schedule(dynamic, 16)
            for (long ci = 0; ci < c; ci++) {
                auto &vv = verts[conds[c0 + ci].first];
                auto &al = conds[c0 + ci].second;
                for (int u = 0; u < U; u++) {
                    u64 acc = 0;
                    for (auto &te : basis[u]) {
                        u64 cc = 1; bool ok = true;
                        for (int ii = 0; ii < 3 && ok; ii++) {
                            int bi = te.first[ii];
                            if (bi < al[ii] || (!vv[ii] && bi != al[ii])) { ok = false; break; }
                            cc = mulm(cc, binom(bi, al[ii]));
                        }
                        if (ok) acc = te.second > 0 ? addm(acc, cc) : subm(acc, cc);
                    }
                    nmod_mat_entry(M, R + ci, u) = acc;
                }
            }
            // FLINT 2.8 rref does not accept windows: reduce a fresh copy of the R echelon rows and the chunk
            nmod_mat_t T; nmod_mat_init(T, R + c, U, P);
            for (long r = 0; r < R + c; r++) for (int u = 0; u < U; u++) nmod_mat_entry(T, r, u) = nmod_mat_entry(M, r, u);
            long R2 = nmod_mat_rref(T);
            for (long r = 0; r < R + c; r++) for (int u = 0; u < U; u++) nmod_mat_entry(M, r, u) = r < R2 ? nmod_mat_entry(T, r, u) : 0;
            nmod_mat_clear(T);
            R = R2;
        }
        long nul = U - R;
        nmod_mat_t X; nmod_mat_init(X, U, nul > 0 ? nul : 1, P);
        {
            vector<long> piv(R); vector<char> isPiv(U, 0);
            for (long r = 0; r < R; r++) { long cc = 0; while (!nmod_mat_entry(M, r, cc)) cc++; piv[r] = cc; isPiv[cc] = 1; }
            long t = 0;
            for (int f = 0; f < U; f++) if (!isPiv[f]) {
                nmod_mat_entry(X, f, t) = 1;
                for (long r = 0; r < R; r++) { u64 v = nmod_mat_entry(M, r, f); if (v) nmod_mat_entry(X, piv[r], t) = (P - v) % P; }
                t++;
            }
        }
        nmod_mat_clear(M);
        if (ORDERONLY) {
            // rank of the degree-l rows of the nullspace basis = dimension of the degree-l parts
            vector<long> lrows; for (int u = 0; u < U; u++) { auto &mo = basis[u][0].first; if (mo[0] + mo[1] + mo[2] == l) lrows.push_back(u); }
            nmod_mat_t Y; nmod_mat_init(Y, lrows.size(), nul > 0 ? nul : 1, P);
            for (size_t r = 0; r < lrows.size(); r++) for (long c = 0; c < nul; c++) nmod_mat_entry(Y, r, c) = nmod_mat_entry(X, lrows[r], c);
            long lr = nul > 0 ? nmod_mat_rank(Y) : 0; nmod_mat_clear(Y); nmod_mat_clear(X);
            printf("(d,rho)=(%d,%d) m=%d l=%d: k=%d D=%d unknowns %d, witness space dim %ld, degree-l parts dim %ld\n", d, rho, m, l, k, D, U, nul, lr);
            fflush(stdout); continue;
        }
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
            if (VAL) for (int pi = -1; pi < (int)EXTRA_PTS.size(); pi++) {
                const u64 *yv = pi < 0 ? y0 : EXTRA_PTS[pi].data();
                // value of the solution at yv: W_c(yv) = [w~(t yv)]_{l+m-c}, w~ = P(r0(y))/prod L'(r0(y_i))
                int NV = l + m + 1, Nsave = N; N = NV;
                Ser lamv(N, 0); if (N > 1) lamv[1] = 1;
                Ser rr(N, 0);
                for (int it = 0; it < N + 1; it++) { Ser sq = smul(rr, rr); for (int i = 0; i < N; i++) rr[i] = subm(sq[i], lamv[i]); }
                vector<vector<Ser>> pows(3);
                Ser den(N, 0); den[0] = 1;
                for (int i = 0; i < 3; i++) {
                    Ser xi(N, 0); u64 yp = 1;
                    for (int n = 0; n < N; n++) { xi[n] = mulm(rr[n], yp); yp = mulm(yp, yv[i]); }  // r0(yv_i t)
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
                (pi < 0 ? valRows : extraRows[pi]).push_back(vr);
                N = Nsave;
            }
        }
        nmod_mat_clear(X);
        long rk = rank_mod(coneRows);
        long vrk = VAL ? rank_mod(valRows) : -1;
        printf("l=%d%s: k=%d D=%d unknowns %d, witness space dim %ld (%d with a nonzero degree-l part), %d with jet outside J^%d + m^k;"
               " cumulative cone rank %ld; cumulative value rank at a random point %ld\n", l, chi < 0 ? "" : (chi ? " (sign part)" : " (trivial part)"), k, D, U, nul, exactOrder, lowViol, j, rk, vrk);
        for (size_t pi = 0; pi < EXTRA_PTS.size(); pi++)
            printf("  cumulative value rank at fixed point %zu (%llu,%llu,%llu): %ld\n", pi, (unsigned long long)EXTRA_PTS[pi][0],
                   (unsigned long long)EXTRA_PTS[pi][1], (unsigned long long)EXTRA_PTS[pi][2], rank_mod(extraRows[pi]));
        fflush(stdout);
      }
    }
    return 0;
}
