// Absorbable lower-degree Taylor classes of a pair of product tops (entry-2026-09-28-absorbable-classes).
//
// Setting (prop:exact-taylor-propagation): the square-free algebra R on N cells over F_3 (one row of a board), tops
// tau = A^2 B and sigma = C^2 D for random dense forms A, B, C, D drawn as in pseudorandom_taylor_check (m = 1),
// Frobenius elements A, B^2 (slot tau) and C, D^2 (slot sigma), Koszul pair K = sigma e_tau - tau e_sigma.
// Adding a cell with coefficients l = (l_A, l_B, l_C, l_D) differentiates each lifted Taylor generator linearly in l:
//   Frob A x -> l_A x e_tau;  Frob B^2 x -> 2 l_B B x e_tau;  Frob C x -> l_C x e_sigma;  Frob D^2 x -> 2 l_D D x e_sigma;
//   K x -> (2 l_C CD + l_D C^2) x e_tau - (2 l_A AB + l_B A^2) x e_sigma.
// For relations r among Taylor generators at multiplier degree E, Psi_f(r) are the l_f-components of delta(r), which
// must be syzygies at degree E-1 (asserted).  calA = span(Psi) mod T_{E-1}; the persistent part of the lower defect is
// dim Syz_{E-1} / (T_{E-1} + calA), and prop:exact-taylor-propagation (2) says every added cell adds that many
// non-Taylor classes at degree E.
// Mode "check": for a random extra cell, verifies Def_E(R') = dim ker ob + Def_{E-1}(R) - rank deltabar directly on
// N+1 cells.  Mode "absorb": prints Def_{E-1}, dim calA, persistent part.
// Exact linear algebra with FLINT nmod_mat.  Usage: absorbable_classes MODE N seed E
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <cassert>
#include <algorithm>
#include <string>

typedef std::vector<std::pair<int, int>> Poly;

struct Board {
    int N; std::vector<int> deg, index; std::vector<std::vector<int>> byDeg;
    Board(int N_) : N(N_) {
        int total = 1 << N; deg.assign(total, 0); index.assign(total, -1); byDeg.assign(N + 1, {});
        for (int c = 0; c < total; c++) { deg[c] = __builtin_popcount(c); index[c] = byDeg[deg[c]].size(); byDeg[deg[c]].push_back(c); }
    }
};

static Poly mul(const Poly& a, const Poly& b) {
    std::vector<std::pair<int, int>> acc;
    for (auto& [ca, xa] : a) for (auto& [cb, xb] : b) if (!(ca & cb)) acc.push_back({ca | cb, xa * xb % 3});
    std::sort(acc.begin(), acc.end());
    Poly out;
    for (size_t i = 0; i < acc.size();) {
        size_t j = i; int s = 0; while (j < acc.size() && acc[j].first == acc[i].first) s += acc[j++].second;
        if (s % 3) out.push_back({acc[i].first, s % 3}); i = j;
    }
    return out;
}
static Poly scale(const Poly& p, int s) { Poly o; s = ((s % 3) + 3) % 3; if (!s) return o; for (auto& [c, x] : p) o.push_back({c, x * s % 3}); return o; }
static Poly mono(int c) { return {{c, 1}}; }

typedef std::vector<long> Vec;  // two slots of degree d: size 2 * |R_d|

static long rankRows(const std::vector<Vec>& rows, long n) {
    if (rows.empty()) return 0;
    nmod_mat_t M; nmod_mat_init(M, rows.size(), n, 3);
    for (size_t i = 0; i < rows.size(); i++) for (long j = 0; j < n; j++) nmod_mat_entry(M, i, j) = rows[i][j];
    long r = nmod_mat_rank(M); nmod_mat_clear(M); return r;
}

struct Pair {
    Board B; std::vector<Poly> F; Poly tau, sigma, A2, B2, C2, D2, AB, CD;
    Pair(int N, const std::vector<std::vector<int>>& coef) : B(N), F(4) {
        for (int f = 0; f < 4; f++) for (int i = 0; i < N; i++) if (coef[f][i]) F[f].push_back({1 << i, coef[f][i]});
        A2 = mul(F[0], F[0]); B2 = mul(F[1], F[1]); C2 = mul(F[2], F[2]); D2 = mul(F[3], F[3]);
        AB = mul(F[0], F[1]); CD = mul(F[2], F[3]); tau = mul(A2, F[1]); sigma = mul(C2, F[3]);
    }
    void add(Vec& v, const Poly& p, int slot, int d, int sign) const {
        long n = B.byDeg[d].size();
        for (auto& [c, x] : p) { assert(B.deg[c] == d); long k = slot * n + B.index[c]; v[k] = ((v[k] + sign * x) % 3 + 3) % 3; }
    }
    long nd(int d) const { return d >= 0 && d <= B.N ? (long)B.byDeg[d].size() : 0; }
    long dimSyz(int e) const {  // kernel of R^2_e -> R_{e+3}
        long ne = nd(e), ns = nd(e + 3); if (!ne) return 0; if (!ns) return 2 * ne;
        nmod_mat_t M; nmod_mat_init(M, ns, 2 * ne, 3);
        for (int s = 0; s < 2; s++) for (long ri = 0; ri < ne; ri++) for (auto& [t, x] : (s ? sigma : tau)) {
            int r = B.byDeg[e][ri]; if (r & t) continue; long row = B.index[r | t];
            nmod_mat_entry(M, row, s * ne + ri) = (nmod_mat_entry(M, row, s * ne + ri) + x) % 3;
        }
        long rk = nmod_mat_rank(M); nmod_mat_clear(M); return 2 * ne - rk;
    }
    // Taylor generator instances at multiplier degree e: (type, multiplier monomial)
    struct Item { int type; int x; };  // 0 FrobA, 1 FrobB2, 2 FrobC, 3 FrobD2, 4 Koszul
    std::vector<Item> items(int e) const {
        std::vector<Item> out;
        int dx[5] = {e - 1, e - 2, e - 1, e - 2, e - 3};
        for (int t = 0; t < 5; t++) if (dx[t] >= 0 && dx[t] <= B.N) for (int x : B.byDeg[dx[t]]) out.push_back({t, x});
        return out;
    }
    Vec value(const Item& it, int e) const {
        Vec v(2 * nd(e), 0); Poly x = mono(it.x);
        switch (it.type) {
            case 0: add(v, mul(F[0], x), 0, e, 1); break;
            case 1: add(v, mul(B2, x), 0, e, 1); break;
            case 2: add(v, mul(F[2], x), 1, e, 1); break;
            case 3: add(v, mul(D2, x), 1, e, 1); break;
            case 4: add(v, mul(sigma, x), 0, e, 1); add(v, mul(tau, x), 1, e, -1); break;
        }
        return v;
    }
    // Psi_f(item) at degree e-1, f in 0..3 (A, B, C, D)
    Vec psi(const Item& it, int f, int e) const {
        Vec v(2 * nd(e - 1), 0); Poly x = mono(it.x);
        switch (it.type) {
            case 0: if (f == 0) add(v, x, 0, e - 1, 1); break;
            case 1: if (f == 1) add(v, scale(mul(F[1], x), 2), 0, e - 1, 1); break;
            case 2: if (f == 2) add(v, x, 1, e - 1, 1); break;
            case 3: if (f == 3) add(v, scale(mul(F[3], x), 2), 1, e - 1, 1); break;
            case 4:
                if (f == 2) add(v, scale(mul(CD, x), 2), 0, e - 1, 1);
                if (f == 3) add(v, mul(C2, x), 0, e - 1, 1);
                if (f == 0) add(v, scale(mul(AB, x), 2), 1, e - 1, -1);
                if (f == 1) add(v, mul(A2, x), 1, e - 1, -1);
                break;
        }
        return v;
    }
    std::vector<Vec> taylor(int e) const { std::vector<Vec> T; for (auto& it : items(e)) T.push_back(value(it, e)); return T; }
    bool isSyz(const Vec& v, int e) const {
        long ne = nd(e); std::vector<int> acc(1 << B.N, 0);
        for (int s = 0; s < 2; s++) for (long i = 0; i < ne; i++) if (v[s * ne + i]) for (auto& [t, x] : (s ? sigma : tau)) {
            int r = B.byDeg[e][i]; if (r & t) continue; acc[r | t] = (acc[r | t] + v[s * ne + i] * x) % 3;
        }
        for (int a : acc) if (a) return false; return true;
    }
    // Relations at multiplier degree E (nullspace of the item-value matrix) and, for each form f, the matrix Q_f whose
    // columns are Psi_f of a basis of the relations.  Asserts that every column of Q_f is a syzygy at degree E-1.
    long relationsAndPsi(int E, const std::vector<Item>& its, std::vector<nmod_mat_struct>& Q) const {
        long rows = 2 * nd(E), cols = its.size(), n = 2 * nd(E - 1);
        nmod_mat_t M; nmod_mat_init(M, rows, cols, 3);
        for (long j = 0; j < cols; j++) { Vec v = value(its[j], E); for (long i = 0; i < rows; i++) if (v[i]) nmod_mat_entry(M, i, j) = v[i]; }
        nmod_mat_t K; nmod_mat_init(K, cols, cols, 3); long nul = nmod_mat_nullspace(K, M); nmod_mat_clear(M);
        nmod_mat_t Kb; nmod_mat_init(Kb, cols, nul > 0 ? nul : 1, 3);
        for (long i = 0; i < cols; i++) for (long j = 0; j < nul; j++) nmod_mat_entry(Kb, i, j) = nmod_mat_entry(K, i, j);
        nmod_mat_clear(K);
        // syzygy map at degree E-1: R^2_{E-1} -> R_{E+2}
        long ns = nd(E + 2); nmod_mat_t S; nmod_mat_init(S, ns > 0 ? ns : 1, n, 3);
        for (int s = 0; s < 2; s++) for (long ri = 0; ri < nd(E - 1); ri++) for (auto& [t, x] : (s ? sigma : tau)) {
            int r = B.byDeg[E - 1][ri]; if (r & t) continue;
            long row = B.index[r | t], col = s * nd(E - 1) + ri; nmod_mat_entry(S, row, col) = (nmod_mat_entry(S, row, col) + x) % 3;
        }
        Q.resize(4);
        for (int f = 0; f < 4; f++) {
            nmod_mat_t P; nmod_mat_init(P, n, cols, 3);
            for (long j = 0; j < cols; j++) { Vec v = psi(its[j], f, E); for (long i = 0; i < n; i++) if (v[i]) nmod_mat_entry(P, i, j) = v[i]; }
            nmod_mat_init(&Q[f], n, nul > 0 ? nul : 1, 3); nmod_mat_mul(&Q[f], P, Kb); nmod_mat_clear(P);
            if (nul == 0) nmod_mat_zero(&Q[f]);
            nmod_mat_t SQ; nmod_mat_init(SQ, ns > 0 ? ns : 1, nul > 0 ? nul : 1, 3); nmod_mat_mul(SQ, S, &Q[f]);
            assert(nmod_mat_is_zero(SQ)); nmod_mat_clear(SQ);
        }
        nmod_mat_clear(S); nmod_mat_clear(Kb); return nul;
    }
};

static std::vector<std::vector<int>> draw(int N, unsigned seed) {
    std::mt19937 rng(seed); std::vector<std::vector<int>> coef(4, std::vector<int>(N, 0));
    for (int b = 0; b < 2; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < N; col++) coef[2 * b + w][col] = rng() % 3;
    return coef;
}

static int run(const std::string& mode, int N, unsigned seed, int E);

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s check|absorb N seed E  |  series Nlo Nhi seeds Emax\n", argv[0]); return 2; }
    std::string mode = argv[1];
    if (mode == "series") {  // validation series of the exact formula: every (N, seed, E) in range, one JSON line each
        int lo = atoi(argv[2]), hi = atoi(argv[3]), seeds = atoi(argv[4]), Emax = atoi(argv[5]);
        for (int N = lo; N <= hi; N++) for (int sd = 1; sd <= seeds; sd++) for (int E = 2; E <= Emax && E + 3 <= N + 1; E++) run("check", N, sd, E);
        return 0;
    }
    return run(mode, atoi(argv[2]), atoi(argv[3]), atoi(argv[4]));
}

static int run(const std::string& mode, int N, unsigned seed, int E) {
    auto coef = draw(N, seed); Pair R(N, coef);
    long syzLow = R.dimSyz(E - 1), nLow = 2 * R.nd(E - 1);
    auto TLow = R.taylor(E - 1); long rkTLow = rankRows(TLow, nLow), defLow = syzLow - rkTLow;
    auto its = R.items(E); std::vector<nmod_mat_struct> Q; long nrel = R.relationsAndPsi(E, its, Q);
    std::vector<Vec> TA = TLow;
    for (int f = 0; f < 4; f++) for (long j = 0; j < nrel; j++) { Vec v(nLow); for (long k = 0; k < nLow; k++) v[k] = nmod_mat_entry(&Q[f], k, j); TA.push_back(v); }
    long absorbed = rankRows(TA, nLow) - rkTLow;
    if (mode == "absorb") {
        printf("{\"N\": %d, \"seed\": %u, \"E\": %d, \"def_lower\": %ld, \"relations\": %ld, \"dim_calA\": %ld, \"persistent\": %ld}\n",
               N, seed, E, defLow, nrel, absorbed, defLow - absorbed);
        return 0;
    }
    // check: random extra cell
    std::mt19937 rng(seed * 7919u + E); std::vector<int> l(4); for (int f = 0; f < 4; f++) l[f] = rng() % 3;
    auto coef2 = coef; for (int f = 0; f < 4; f++) coef2[f].push_back(l[f]);
    if (getenv("DUMP")) { printf("{\"coef\": ["); for (int f = 0; f < 4; f++) { printf("%s[", f ? "," : ""); for (int i = 0; i < N; i++) printf("%s%d", i ? "," : "", coef[f][i]); printf("]"); } printf("]}\n"); }
    Pair R2(N + 1, coef2);
    long defNew = R2.dimSyz(E) - rankRows(R2.taylor(E), 2 * R2.nd(E));
    long defHere = R.dimSyz(E) - rankRows(R.taylor(E), 2 * R.nd(E));
    // rank deltabar: delta(r) = sum_f l_f Psi_f(r)
    std::vector<Vec> TD = TLow;
    for (long j = 0; j < nrel; j++) { Vec v(nLow, 0); for (int f = 0; f < 4; f++) for (long k = 0; k < nLow; k++) v[k] = (v[k] + l[f] * (long)nmod_mat_entry(&Q[f], k, j)) % 3; TD.push_back(v); }
    long rankDelta = rankRows(TD, nLow) - rkTLow;
    // dim ker ob: syzygies z of R at degree E with z_tau dtau' + z_sigma dsigma' in I_R (degree E+2), modulo T_E
    // dtau' = 2 l_A AB + l_B A^2 ; dsigma' = 2 l_C CD + l_D C^2 ; I_R in degree E+2 = tau R_{E-1} + sigma R_{E-1}
    Poly dt; for (auto& [c, x] : scale(R.AB, 2 * l[0])) dt.push_back({c, x}); for (auto& [c, x] : scale(R.A2, l[1])) dt.push_back({c, x});
    Poly ds; for (auto& [c, x] : scale(R.CD, 2 * l[2])) ds.push_back({c, x}); for (auto& [c, x] : scale(R.C2, l[3])) ds.push_back({c, x});
    dt = mul(dt, mono(0)); ds = mul(ds, mono(0));  // combine like terms
    long nE = R.nd(E), nI = R.nd(E + 2), nS = R.nd(E + 3), nL = R.nd(E - 1);
    // unknowns: z (2 nE) and w (2 nL) with: z.(tau, sigma) = 0 in degree E+3 and z.(dt, ds) - w.(tau, sigma) = 0 in degree E+2
    long cols = 2 * nE + 2 * nL, rows = nS + nI;
    nmod_mat_t M; nmod_mat_init(M, rows, cols, 3);
    // nmod_mat entries are unsigned: add a signed coefficient through a signed long, or -1 wraps to +0 mod 3
    auto put = [&](long row, long col, int x) { long v = (long)nmod_mat_entry(M, row, col) + x; nmod_mat_entry(M, row, col) = ((v % 3) + 3) % 3; };
    for (int s = 0; s < 2; s++) for (long i = 0; i < nE; i++) {
        int r = R.B.byDeg[E][i];
        for (auto& [t, x] : (s ? R.sigma : R.tau)) if (!(r & t)) put(R.B.index[r | t], s * nE + i, x);
        for (auto& [t, x] : (s ? ds : dt)) if (!(r & t)) put(nS + R.B.index[r | t], s * nE + i, x);
    }
    for (int s = 0; s < 2; s++) for (long i = 0; i < nL; i++) {
        int r = R.B.byDeg[E - 1][i];
        for (auto& [t, x] : (s ? R.sigma : R.tau)) if (!(r & t)) put(nS + R.B.index[r | t], 2 * nE + s * nL + i, -x);
    }
    nmod_mat_t K; nmod_mat_init(K, cols, cols, 3); long nul = nmod_mat_nullspace(K, M);
    std::vector<Vec> Z = R.taylor(E); long rkTE = rankRows(Z, 2 * nE);
    for (long j = 0; j < nul; j++) { Vec v(2 * nE); for (long i = 0; i < 2 * nE; i++) v[i] = nmod_mat_entry(K, i, j); Z.push_back(v); }
    long liftable = rankRows(Z, 2 * nE);
    long kerOb = liftable - rkTE;
    printf("{\"debug\": 1, \"syz_E_ext\": %ld, \"syz_E_R\": %ld, \"syz_low_R\": %ld, \"liftable_span\": %ld, \"rank_T_E_R\": %ld, \"rank_T_E_ext\": %ld, \"null_zw\": %ld}\n",
           R2.dimSyz(E), R.dimSyz(E), syzLow, liftable, rkTE, rankRows(R2.taylor(E), 2 * R2.nd(E)), nul);
    long predicted = kerOb + defLow - rankDelta;
    printf("{\"N\": %d, \"seed\": %u, \"E\": %d, \"l\": [%d,%d,%d,%d], \"def_E_R\": %ld, \"def_lower\": %ld, \"ker_ob\": %ld, "
           "\"rank_deltabar\": %ld, \"predicted\": %ld, \"def_E_extension\": %ld, \"dim_calA\": %ld}\n",
           N, seed, E, l[0], l[1], l[2], l[3], defHere, defLow, kerOb, rankDelta, predicted, defNew, absorbed);
    fflush(stdout);
    assert(predicted == defNew);
    assert(defNew >= defLow - absorbed);
    return 0;
}
