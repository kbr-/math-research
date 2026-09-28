// Level-set losses of a coupled pair of form constraints on the weak unary base (odd-prime-union-relation).
//
// Statement tested.  On the weak base P (m rows, N columns, column-injective, occupancy = m mod 3) take a
// dense normal-form affine form L (no cells of column 1) and a second form L2, and Q = {L != 0, L2 != 0}.
// Mode "coupled": L2 = -L - sum_{c>=2} x_{1c} + c0, so L + L2 + r_1 = x_{11} + c0 (a one-column coupling).
// Mode "control": L2 an independent random dense normal-form form.  For each level a of the row sum
// r_1 (mod 3) and each d <= dmax the kernel prints the loss L_a(d) = dim F_{<=d}(P_a) - dim F_{<=d}(Q_a),
// with P_a = P cap {r_1 = a}, and the value-space prediction of prop:coupled-pair-imbalance under the
// pullback hypotheses on P_a: with value map (L, [L2 in control], column-1 state), B_a's Hilbert function is
// solved from dim F_{<=d}(P_a), and the predicted loss is sum_e b_e dim I(Y_a)_{<= d-e}.  The claim predicts
// losses that depend on a in the coupled mode (value sets {y != 0} are unbalanced) and equal losses in the
// control.  Ranks are exact over F_3 (fflas-ffpack), validated against FLINT nmod_mat on the d = 2 matrices.
//
// Usage: coupled_pair_levels m N dmax seed
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <functional>

typedef std::vector<std::pair<int,int>> Mono;  // cells (row 1..m, column 0..N-1)

static long rankF3(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& monos) {
    size_t R = pts.size(), C = monos.size();
    if (R == 0 || C == 0) return 0;
    Givaro::Modular<double> F(3.0);
    std::vector<double> A(R * C, 0.0);
    for (size_t i = 0; i < R; i++)
        for (size_t j = 0; j < C; j++) {
            bool on = true;
            for (auto& cell : monos[j]) if (pts[i][cell.second] != cell.first) { on = false; break; }
            A[i * C + j] = on ? 1.0 : 0.0;
        }
    return (long)FFPACK::Rank(F, R, C, A.data(), C);
}

static long rankFlint(const std::vector<std::vector<int>>& pts, const std::vector<Mono>& monos) {
    size_t R = pts.size(), C = monos.size();
    if (R == 0 || C == 0) return 0;
    nmod_mat_t A; nmod_mat_init(A, R, C, 3);
    for (size_t i = 0; i < R; i++)
        for (size_t j = 0; j < C; j++) {
            bool on = true;
            for (auto& cell : monos[j]) if (pts[i][cell.second] != cell.first) { on = false; break; }
            nmod_mat_entry(A, i, j) = on ? 1 : 0;
        }
    long r = nmod_mat_rank(A); nmod_mat_clear(A); return r;
}

// Value space: coordinates y in F_3^k and column-1 state pi in {0..m}; monomials y^alpha (alpha_i <= 2)
// times 1 or x_{i1}; degree |alpha| + [cell].  Returns dim of functions of degree <= e vanishing on Y.
static long valueIdeal(int k, int m, const std::vector<std::vector<int>>& Y, int e) {
    std::vector<std::pair<std::vector<int>,int>> mons;  // (alpha, cell row or 0)
    int tot = 1; for (int i = 0; i < k; i++) tot *= 3;
    for (int code = 0; code < tot; code++) {
        std::vector<int> al(k); int c = code, deg = 0;
        for (int i = 0; i < k; i++) { al[i] = c % 3; c /= 3; deg += al[i]; }
        for (int cell = 0; cell <= m; cell++) if (deg + (cell ? 1 : 0) <= e) mons.push_back({al, cell});
    }
    long nm = mons.size();
    if (Y.empty()) return nm;
    Givaro::Modular<double> F(3.0);
    std::vector<double> A(Y.size() * nm);
    for (size_t i = 0; i < Y.size(); i++)
        for (long j = 0; j < nm; j++) {
            long v = 1;
            for (int t = 0; t < k; t++) for (int p = 0; p < mons[j].first[t]; p++) v = v * Y[i][t] % 3;
            if (mons[j].second && Y[i][k] != mons[j].second) v = 0;
            A[i * nm + j] = (double)v;
        }
    long rk = (long)FFPACK::Rank(F, Y.size(), nm, A.data(), nm);
    return nm - rk;
}

static long valueDim(int k, int m, int e) {  // dim of value-space functions of degree <= e (all independent)
    long cnt = 0; int tot = 1; for (int i = 0; i < k; i++) tot *= 3;
    for (int code = 0; code < tot; code++) {
        int c = code, deg = 0; for (int i = 0; i < k; i++) { deg += c % 3; c /= 3; }
        for (int cell = 0; cell <= m; cell++) if (deg + (cell ? 1 : 0) <= e) cnt++;
    }
    return cnt;
}

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: m N dmax seed\n"); return 1; }
    int m = atoi(argv[1]), N = atoi(argv[2]), dmax = atoi(argv[3]); unsigned seed = atoi(argv[4]);
    std::mt19937 rng(seed);
    auto rnd3 = [&]() { return (int)(rng() % 3); };
    // dense normal-form forms: coefficients on cells (r, c), c >= 1 (column 0 is the normal-form column)
    std::vector<std::vector<int>> cL(m + 1, std::vector<int>(N, 0)), cM(m + 1, std::vector<int>(N, 0));
    for (int r = 1; r <= m; r++) for (int c = 1; c < N; c++) { cL[r][c] = rnd3(); cM[r][c] = rnd3(); }
    int kL = rnd3(), kM = rnd3(), c0 = rnd3();
    // monomials by degree
    std::vector<std::vector<Mono>> byDeg(dmax + 1);
    std::function<void(int, Mono&)> gen = [&](int col, Mono& cur) {
        if ((int)cur.size() <= dmax) byDeg[cur.size()].push_back(cur);
        if ((int)cur.size() == dmax) return;
        for (int c = col; c < N; c++) for (int r = 1; r <= m; r++) { cur.push_back({r, c}); gen(c + 1, cur); cur.pop_back(); }
    };
    Mono e0; gen(0, e0);
    long total = 1; for (int c = 0; c < N; c++) total *= (m + 1);
    printf("# m=%d N=%d dmax=%d seed=%u; points of the column-injective set: %ld\n", m, N, dmax, seed, total);
    for (int mode = 0; mode < 2; mode++) {
        const char* name = mode == 0 ? "coupled" : "control";
        int k = mode == 0 ? 1 : 2;  // value coordinates besides the column-1 state
        for (int a = 0; a < 3; a++) {
            std::vector<std::vector<int>> Pa, Qa, Ya;
            std::vector<int> s(N);
            for (long code = 0; code < total; code++) {
                long x = code; int occ = 0, r1 = 0;
                for (int c = 0; c < N; c++) { s[c] = x % (m + 1); x /= (m + 1); if (s[c]) occ++; if (s[c] == 1) r1++; }
                if (occ % 3 != m % 3 || r1 % 3 != a) continue;
                int L = kL, M2 = kM, row1rest = 0;
                for (int c = 1; c < N; c++) if (s[c]) { L += cL[s[c]][c]; M2 += cM[s[c]][c]; if (s[c] == 1) row1rest++; }
                L %= 3; M2 %= 3;
                int L2 = mode == 0 ? ((-L - row1rest + c0) % 3 + 6) % 3 : M2;
                Pa.push_back(s);
                if (L != 0 && L2 != 0) Qa.push_back(s);
            }
            // value-space image of the allowed set on this level: (L, [L2], state of column 0)
            {
                std::vector<std::vector<int>> seen;
                for (auto& p : Qa) {
                    int L = kL, M2 = kM;
                    for (int c = 1; c < N; c++) if (p[c]) { L += cL[p[c]][c]; M2 += cM[p[c]][c]; }
                    std::vector<int> v; v.push_back(L % 3); if (k == 2) v.push_back(M2 % 3); v.push_back(p[0]);
                    bool dup = false; for (auto& w : seen) if (w == v) { dup = true; break; }
                    if (!dup) seen.push_back(v);
                }
                Ya = seen;
            }
            std::vector<long> hfP(dmax + 1), hfQ(dmax + 1);
            std::vector<Mono> cols;
            for (int d = 0; d <= dmax; d++) {
                cols.insert(cols.end(), byDeg[d].begin(), byDeg[d].end());
                hfP[d] = rankF3(Pa, cols); hfQ[d] = rankF3(Qa, cols);
                if (d == 2 && a == 0) {
                    long f1 = rankFlint(Pa, cols), f2 = rankFlint(Qa, cols);
                    printf("# validation %s a=0 d=2: fflas %ld %ld, FLINT %ld %ld%s\n", name, hfP[d], hfQ[d], f1, f2,
                           (f1 == hfP[d] && f2 == hfQ[d]) ? "" : "  MISMATCH");
                }
            }
            // B_a Hilbert function from HF(P_a) = sum_e b_e valueDim(d - e); predicted loss
            std::vector<long> b(dmax + 1);
            for (int d = 0; d <= dmax; d++) {
                long acc = hfP[d];
                for (int e = 0; e < d; e++) acc -= b[e] * valueDim(k, m, d - e);
                b[d] = acc;
            }
            printf("%s a=%d |P_a|=%zu |Q_a|=%zu |Y_a|=%zu\n", name, a, Pa.size(), Qa.size(), Ya.size());
            for (int d = 0; d <= dmax; d++) {
                long pred = 0;
                for (int e = 0; e <= d; e++) pred += b[e] * valueIdeal(k, m, Ya, d - e);
                printf("  d=%d dimF(P_a)=%ld dimF(Q_a)=%ld loss=%ld predicted=%ld b_d=%ld\n", d, hfP[d], hfQ[d],
                       hfP[d] - hfQ[d], pred, b[d]);
            }
        }
    }
    return 0;
}
