// Single-row lift defect of a coupled pair on the two-row weak base (odd-prime-full-set-lift).
//
// Statement tested.  On the weak base P (m = 2 rows, N columns, column-injective, occupancy = m mod 3) the
// row equations reduce to rho = r_1 - 1 (r_2 = m - r_1 on P).  For a point set X in P with levels
// X_a = X cap {r_1 = a}, the degree-D lift N_D cap F_{D-1} in N_{D-1} (N_e = rho F_{<=e-1}) holds iff
//     Delta_X(D) = H_X(D-1) - H_{X_1}(D-1) - H_{X_0 u X_2}(D-2) = 0,   H_Z(e) = dim F_{<=e}(Z).
// Take a dense normal-form form L (no cells of column 0) and L2 = -L - sum_{c>=1} x_{1c} + c0, so that
// L + L2 + r_1 = x_{10} + c0 (the coupled pair), Q = {L != 0, L2 != 0}.  Under the global pullback
// hypothesis for the value map v = (L, L2, state of column 0), H_{v^{-1}Z} = b * H_Z for every value set Z,
// so Delta_Q(D) = sum_e b_e Delta_Y(D - e) with Y = {y != 0, y' != 0} x all states.  The kernel prints
// Delta_P, Delta_Q and that prediction, with b solved from H_P = b * H_Omega.  The value-space computation
// predicts Delta_Y = 0 for c0 = 1 and nonzero low-degree defects for c0 = 0, 2.  It also prints the exact lift
// defect dim(N_D cap F_{D-1}) - dim N_{D-1} on Q and on P, since Delta = 0 implies the lift at D, and a
// positive Delta(D) only shows failure at D or D + 1.  Ranks are exact over F_3
// (fflas-ffpack), validated against FLINT nmod_mat at d = 2.
//
// Usage: coupled_pair_lift N dmax seed
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <functional>
#include <cmath>

typedef std::vector<std::pair<int,int>> Mono;  // cells (row 1..m, column)
static const int m = 2;

static std::vector<double> evalMat(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& monos) {
    std::vector<double> A(pts.size() * monos.size(), 0.0);
    for (size_t i = 0; i < pts.size(); i++)
        for (size_t j = 0; j < monos.size(); j++) {
            bool on = true;
            for (auto& cell : monos[j]) if (pts[i][cell.second] != cell.first) { on = false; break; }
            A[i * monos.size() + j] = on ? 1.0 : 0.0;
        }
    return A;
}
static long rankF3(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& monos) {
    if (pts.empty() || monos.empty()) return 0;
    Givaro::Modular<double> F(3.0);
    auto A = evalMat(pts, monos);
    return (long)FFPACK::Rank(F, pts.size(), monos.size(), A.data(), monos.size());
}
static long rankFlint(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& monos) {
    if (pts.empty() || monos.empty()) return 0;
    auto A = evalMat(pts, monos);
    nmod_mat_t M; nmod_mat_init(M, pts.size(), monos.size(), 3);
    for (size_t i = 0; i < pts.size(); i++) for (size_t j = 0; j < monos.size(); j++)
        nmod_mat_entry(M, i, j) = (mp_limb_t)A[i * monos.size() + j];
    long r = nmod_mat_rank(M); nmod_mat_clear(M); return r;
}

// Exact lift defect dim(N_D cap F_{D-1}) - dim N_{D-1} on a point set, N_e = rho * F_{<=e-1}, rho = r_1 - 1.
static long rankRows(std::vector<double>& A, size_t R, size_t C) {
    if (R == 0 || C == 0) return 0;
    Givaro::Modular<double> F(3.0);
    return (long)FFPACK::Rank(F, R, C, A.data(), C);
}
static long liftDefect(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& upToDm1,
                       const std::vector<Mono>& upToDm2) {
    size_t R = pts.size(), C1 = upToDm1.size(), C2 = upToDm2.size();
    std::vector<double> ND(R * C1), F(R * C1), both(R * 2 * C1), NDm1(R * C2);
    for (size_t i = 0; i < R; i++) {
        int r1 = 0; for (int v : pts[i]) if (v == 1) r1++;
        double rho = (double)(((r1 - 1) % 3 + 3) % 3);
        for (size_t j = 0; j < C1; j++) {
            bool on = true;
            for (auto& cell : upToDm1[j]) if (pts[i][cell.second] != cell.first) { on = false; break; }
            double v = on ? 1.0 : 0.0;
            ND[i * C1 + j] = fmod(rho * v, 3.0); F[i * C1 + j] = v;
            both[i * 2 * C1 + j] = fmod(rho * v, 3.0); both[i * 2 * C1 + C1 + j] = v;
        }
        for (size_t j = 0; j < C2; j++) {
            bool on = true;
            for (auto& cell : upToDm2[j]) if (pts[i][cell.second] != cell.first) { on = false; break; }
            NDm1[i * C2 + j] = on ? rho : 0.0;
        }
    }
    long rN = rankRows(ND, R, C1), rF = rankRows(F, R, C1), rB = rankRows(both, R, 2 * C1), rN1 = rankRows(NDm1, R, C2);
    return rN + rF - rB - rN1;
}

// Value space Omega: (y, y', pi), y, y' in F_3 with exponents <= 2, pi in {0..m} with cells of degree 1.
struct VPt { int y, yp, pi; };
static long valueHF(const std::vector<VPt>& Z, int e) {
    if (e < 0 || Z.empty()) return 0;
    std::vector<std::vector<int>> mons;
    for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) for (int cell = 0; cell <= m; cell++)
        if (a + b + (cell ? 1 : 0) <= e) mons.push_back({a, b, cell});
    Givaro::Modular<double> F(3.0);
    std::vector<double> A(Z.size() * mons.size());
    for (size_t i = 0; i < Z.size(); i++)
        for (size_t j = 0; j < mons.size(); j++) {
            long v = 1;
            for (int p = 0; p < mons[j][0]; p++) v = v * Z[i].y % 3;
            for (int p = 0; p < mons[j][1]; p++) v = v * Z[i].yp % 3;
            if (mons[j][2] && Z[i].pi != mons[j][2]) v = 0;
            A[i * mons.size() + j] = (double)v;
        }
    return (long)FFPACK::Rank(F, Z.size(), mons.size(), A.data(), mons.size());
}

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: N dmax seed\n"); return 1; }
    int N = atoi(argv[1]), dmax = atoi(argv[2]); unsigned seed = atoi(argv[3]);
    std::mt19937 rng(seed);
    std::vector<std::vector<int>> cL(m + 1, std::vector<int>(N, 0));
    for (int r = 1; r <= m; r++) for (int c = 1; c < N; c++) cL[r][c] = rng() % 3;
    int kL = rng() % 3;
    std::vector<std::vector<Mono>> byDeg(dmax + 1);
    std::function<void(int, Mono&)> gen = [&](int col, Mono& cur) {
        byDeg[cur.size()].push_back(cur);
        if ((int)cur.size() == dmax) return;
        for (int c = col; c < N; c++) for (int r = 1; r <= m; r++) { cur.push_back({r, c}); gen(c + 1, cur); cur.pop_back(); }
    };
    Mono e0; gen(0, e0);
    long total = 1; for (int c = 0; c < N; c++) total *= (m + 1);
    printf("# m=%d N=%d dmax=%d seed=%u kL=%d\n", m, N, dmax, seed, kL);
    // Omega and its Hilbert function
    std::vector<VPt> Omega;
    for (int y = 0; y < 3; y++) for (int yp = 0; yp < 3; yp++) for (int pi = 0; pi <= m; pi++) Omega.push_back({y, yp, pi});
    // the base and its levels do not depend on c0
    std::vector<std::vector<int>> P, P1, Pp;
    {
        std::vector<int> s(N);
        for (long code = 0; code < total; code++) {
            long x = code; int occ = 0, r1 = 0;
            for (int c = 0; c < N; c++) { s[c] = x % (m + 1); x /= (m + 1); if (s[c]) occ++; if (s[c] == 1) r1++; }
            if (occ % 3 != m % 3) continue;
            P.push_back(s); (r1 % 3 == 1 ? P1 : Pp).push_back(s);
        }
    }
    std::vector<long> hP(dmax + 1), hP1(dmax + 1), hPp(dmax + 1);
    {
        std::vector<Mono> cols;
        for (int d = 0; d <= dmax; d++) {
            cols.insert(cols.end(), byDeg[d].begin(), byDeg[d].end());
            hP[d] = rankF3(P, cols); hP1[d] = rankF3(P1, cols); hPp[d] = rankF3(Pp, cols);
        }
    }
    for (int c0 = 0; c0 < 3; c0++) {
        std::vector<std::vector<int>> Q, Q1, Qp;
        for (auto& s : P) {
            int L = kL, row1rest = 0, r1 = 0;
            for (int c = 0; c < N; c++) if (s[c] == 1) r1++;
            for (int c = 1; c < N; c++) if (s[c]) { L += cL[s[c]][c]; if (s[c] == 1) row1rest++; }
            L %= 3;
            int L2 = ((-L - row1rest + c0) % 3 + 6) % 3;
            if (L != 0 && L2 != 0) { Q.push_back(s); (r1 % 3 == 1 ? Q1 : Qp).push_back(s); }
        }
        std::vector<long> hQ(dmax + 1), hQ1(dmax + 1), hQp(dmax + 1);
        std::vector<Mono> cols;
        for (int d = 0; d <= dmax; d++) {
            cols.insert(cols.end(), byDeg[d].begin(), byDeg[d].end());
            hQ[d] = rankF3(Q, cols); hQ1[d] = rankF3(Q1, cols); hQp[d] = rankF3(Qp, cols);
            if (d == 2) {
                long a = rankFlint(Q, cols), b = rankFlint(Q1, cols), c = rankFlint(Qp, cols);
                printf("# validation c0=%d d=2: fflas %ld %ld %ld, FLINT %ld %ld %ld%s\n", c0, hQ[d], hQ1[d], hQp[d], a, b, c,
                       (a == hQ[d] && b == hQ1[d] && c == hQp[d]) ? "" : "  MISMATCH");
            }
        }
        // value sets and their defects; r_1 = c0 + [pi = 1] - y - y'
        std::vector<VPt> Y, Y1, Yp;
        for (auto& w : Omega) if (w.y && w.yp) {
            int r = ((c0 + (w.pi == 1) - w.y - w.yp) % 3 + 6) % 3;
            Y.push_back(w); (r == 1 ? Y1 : Yp).push_back(w);
        }
        auto dY = [&](int D) { return valueHF(Y, D - 1) - valueHF(Y1, D - 1) - valueHF(Yp, D - 2); };
        std::vector<long> b(dmax + 1);
        for (int d = 0; d <= dmax; d++) {
            long acc = hP[d];
            for (int e = 0; e < d; e++) acc -= b[e] * valueHF(Omega, d - e);
            b[d] = acc;  // H_P(d) = sum_{e<=d} b_e * H_Omega(d - e), cumulative H_Omega, H_Omega(0) = 1
        }
        printf("c0=%d |P|=%zu |P_1|=%zu |Q|=%zu |Q_1|=%zu |Q'|=%zu\n", c0, P.size(), P1.size(), Q.size(), Q1.size(), Qp.size());
        std::vector<std::vector<Mono>> upTo(dmax + 1);
        for (int d = 0; d <= dmax; d++) { if (d) upTo[d] = upTo[d - 1]; upTo[d].insert(upTo[d].end(), byDeg[d].begin(), byDeg[d].end()); }
        std::vector<Mono> none;
        for (int D = 1; D <= dmax + 1; D++) {
            long lQ = liftDefect(Q, upTo[D - 1], D >= 2 ? upTo[D - 2] : none);
            long lP = c0 == 0 ? liftDefect(P, upTo[D - 1], D >= 2 ? upTo[D - 2] : none) : -1;
            printf("  D=%d exact lift defect: Q %ld%s", D, lQ, c0 == 0 ? "" : "\n");
            if (c0 == 0) printf(", P %ld\n", lP);
        }
        for (int D = 1; D <= dmax + 1; D++) {
            long dP = hP[D - 1] - hP1[D - 1] - (D >= 2 ? hPp[D - 2] : 0);
            long dQ = hQ[D - 1] - hQ1[D - 1] - (D >= 2 ? hQp[D - 2] : 0);
            long pred = 0;
            for (int e = 0; e <= D; e++) if (e <= dmax) pred += b[e] * dY(D - e);
            printf("  D=%d H_P=%ld H_Q=%ld Delta_P=%ld Delta_Q=%ld predicted=%ld Delta_Y=%ld\n", D, hP[D - 1], hQ[D - 1], dP, dQ,
                   pred, dY(D));
        }
    }
    return 0;
}
