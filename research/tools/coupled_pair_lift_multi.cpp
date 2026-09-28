// Multi-row lift defect of a coupled pair on the weak base (odd-prime-lift-class).
//
// Statement tested.  On the weak base P (m rows, N columns, column-injective, occupancy = m mod 3), with
// rho_i = r_i - 1 for i = 1..m-1 (r_m is fixed by the occupancy) and N_e = sum_i rho_i F_{<=e-1}, the lift
// defect is lambda_X(D) = dim(N_D cap F_{D-1}) - dim N_{D-1}.  The product lift rule of the entry predicts,
// for the coupled pair Q = {L != 0, L_2 != 0} with L + L_2 + r_1 = x_{1,0} + c0 (L dense, normal form, no
// cells of column 0), that the value-space failure at degree 3 (c0 = 0, 2) transfers to lambda_Q(D) > 0 in
// the degrees where the base lifts, and that c0 = 1 lifts there.  Ranks are exact over F_3 (fflas-ffpack);
// evaluation ranks of Q at d = 2 are validated against FLINT nmod_mat.
//
// Usage: coupled_pair_lift_multi m N dmax seed
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <functional>

typedef std::vector<std::pair<int,int>> Mono;  // cells (row 1..m, column)
static int m;

static bool on(const std::vector<int>& p, const Mono& mo) {
    for (auto& cell : mo) if (p[cell.second] != cell.first) return false;
    return true;
}
static long rankOf(std::vector<double>& A, size_t R, size_t C) {
    if (R == 0 || C == 0) return 0;
    Givaro::Modular<double> F(3.0);
    return (long)FFPACK::Rank(F, R, C, A.data(), C);
}
static std::vector<int> rhos(const std::vector<int>& p) {  // rho_i = r_i - 1 mod 3, i = 1..m-1
    std::vector<int> r(m + 1, 0);
    for (int v : p) if (v) r[v]++;
    std::vector<int> out;
    for (int i = 1; i < m; i++) out.push_back(((r[i] - 1) % 3 + 3) % 3);
    return out;
}
// columns: for each row equation i and monomial of degree <= e-1, rho_i * monomial
static long rankN(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& mons) {
    size_t R = pts.size(), C = (m - 1) * mons.size();
    if (!R || !C) return 0;
    std::vector<double> A(R * C);
    for (size_t i = 0; i < R; i++) {
        auto rh = rhos(pts[i]);
        for (size_t j = 0; j < mons.size(); j++) {
            double v = on(pts[i], mons[j]) ? 1.0 : 0.0;
            for (int k = 0; k < m - 1; k++) A[i * C + k * mons.size() + j] = v * rh[k];
        }
    }
    return rankOf(A, R, C);
}
static long rankF(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& mons) {
    size_t R = pts.size(), C = mons.size();
    if (!R || !C) return 0;
    std::vector<double> A(R * C);
    for (size_t i = 0; i < R; i++) for (size_t j = 0; j < C; j++) A[i * C + j] = on(pts[i], mons[j]) ? 1.0 : 0.0;
    return rankOf(A, R, C);
}
static long rankNF(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& nm, const std::vector<Mono>& fm) {
    size_t R = pts.size(), C1 = (m - 1) * nm.size(), C = C1 + fm.size();
    if (!R || !C) return 0;
    std::vector<double> A(R * C);
    for (size_t i = 0; i < R; i++) {
        auto rh = rhos(pts[i]);
        for (size_t j = 0; j < nm.size(); j++) {
            double v = on(pts[i], nm[j]) ? 1.0 : 0.0;
            for (int k = 0; k < m - 1; k++) A[i * C + k * nm.size() + j] = v * rh[k];
        }
        for (size_t j = 0; j < fm.size(); j++) A[i * C + C1 + j] = on(pts[i], fm[j]) ? 1.0 : 0.0;
    }
    return rankOf(A, R, C);
}
static long liftDefect(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& upToDm1,
                       const std::vector<Mono>& upToDm2) {
    long nD = rankN(pts, upToDm1), f = rankF(pts, upToDm1), both = rankNF(pts, upToDm1, upToDm1);
    return nD + f - both - rankN(pts, upToDm2);
}
static long rankFlint(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& mons) {
    if (pts.empty() || mons.empty()) return 0;
    nmod_mat_t M; nmod_mat_init(M, pts.size(), mons.size(), 3);
    for (size_t i = 0; i < pts.size(); i++) for (size_t j = 0; j < mons.size(); j++)
        nmod_mat_entry(M, i, j) = on(pts[i], mons[j]) ? 1 : 0;
    long r = nmod_mat_rank(M); nmod_mat_clear(M); return r;
}

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: m N dmax seed\n"); return 1; }
    m = atoi(argv[1]); int N = atoi(argv[2]), dmax = atoi(argv[3]); unsigned seed = atoi(argv[4]);
    std::mt19937 rng(seed);
    std::vector<std::vector<int>> cL(m + 1, std::vector<int>(N, 0));
    for (int r = 1; r <= m; r++) for (int c = 1; c < N; c++) cL[r][c] = rng() % 3;
    int kL = rng() % 3;
    std::vector<std::vector<Mono>> upTo(dmax + 1);
    {
        std::vector<std::vector<Mono>> byDeg(dmax + 1);
        std::function<void(int, Mono&)> gen = [&](int col, Mono& cur) {
            byDeg[cur.size()].push_back(cur);
            if ((int)cur.size() == dmax) return;
            for (int c = col; c < N; c++) for (int r = 1; r <= m; r++) { cur.push_back({r, c}); gen(c + 1, cur); cur.pop_back(); }
        };
        Mono e0; gen(0, e0);
        for (int d = 0; d <= dmax; d++) { if (d) upTo[d] = upTo[d - 1]; upTo[d].insert(upTo[d].end(), byDeg[d].begin(), byDeg[d].end()); }
    }
    long total = 1; for (int c = 0; c < N; c++) total *= (m + 1);
    std::vector<std::vector<int>> P;
    {
        std::vector<int> s(N);
        for (long code = 0; code < total; code++) {
            long x = code; int occ = 0;
            for (int c = 0; c < N; c++) { s[c] = x % (m + 1); x /= (m + 1); if (s[c]) occ++; }
            if (occ % 3 == m % 3) P.push_back(s);
        }
    }
    printf("# m=%d N=%d dmax=%d seed=%u kL=%d |P|=%zu\n", m, N, dmax, seed, kL, P.size());
    std::vector<Mono> none;
    for (int D = 1; D <= dmax + 1; D++)
        printf("P D=%d lift defect %ld\n", D, liftDefect(P, upTo[D - 1], D >= 2 ? upTo[D - 2] : none));
    for (int c0 = 0; c0 < 3; c0++) {
        std::vector<std::vector<int>> Q;
        for (auto& s : P) {
            int L = kL, row1rest = 0;
            for (int c = 1; c < N; c++) if (s[c]) { L += cL[s[c]][c]; if (s[c] == 1) row1rest++; }
            L %= 3;
            int L2 = ((-L - row1rest + c0) % 3 + 6) % 3;
            if (L != 0 && L2 != 0) Q.push_back(s);
        }
        if (dmax >= 2) {
            long a = rankF(Q, upTo[2]), b = rankFlint(Q, upTo[2]);
            printf("# validation c0=%d d=2: fflas %ld FLINT %ld%s\n", c0, a, b, a == b ? "" : "  MISMATCH");
        }
        printf("c0=%d |Q|=%zu\n", c0, Q.size());
        for (int D = 1; D <= dmax + 1; D++)
            printf("  D=%d lift defect %ld\n", D, liftDefect(Q, upTo[D - 1], D >= 2 ? upTo[D - 2] : none));
    }
    return 0;
}
