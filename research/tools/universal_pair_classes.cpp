// Universally liftable pair classes (entry-2026-09-27-universal-classes).
//
// Statement tested (prop:lift-obstruction applied to one pair): for tau = A^2 B and sigma = C^2 D on the square-free
// algebra S of N cells over F_3 (one row), with I = tau S + sigma S, a top syzygy z = (z_tau, z_sigma) of
// multiplier degree e survives the addition of a cell for every choice of the new coefficients exactly when
// z_tau AB, z_tau A^2, z_sigma CD, z_sigma C^2 lie in I (degree e + 2).  Let W_0 be that subspace of Syz_e.  It
// contains the Taylor span T_e, and when Def_{e-1} = 0 the classes surviving any added cell are W_0 / T_e.  The
// program reproduces the forms of pseudorandom_taylor_check (m = 1, M = 2, same generator order) and prints
// Def_{e-1}, dim Syz_e, rank T_e, dim W_0 and dim(W_0 + T_e).  Exact linear algebra with FLINT nmod_mat.
// Usage: universal_pair_classes OUT N seed e.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <cassert>

typedef std::vector<std::pair<int, int>> Poly;
static int NN;
static std::vector<int> dg, idx;
static std::vector<std::vector<int>> byDeg;

static Poly mul(const Poly& a, const Poly& b) {
    static std::vector<int> buf; if (buf.size() < (size_t)(1 << NN)) buf.assign(1 << NN, 0);
    std::vector<int> touched;
    for (auto& [ca, xa] : a) for (auto& [cb, xb] : b) if (!(ca & cb)) {
        int c = ca | cb; if (!buf[c]) touched.push_back(c);
        buf[c] = (buf[c] + xa * xb) % 3; if (!buf[c]) buf[c] = 3;
    }
    Poly out; for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}

// rank of the multiplication map (x_1..x_k) -> sum x_i g_i from S_d^k to S_{d + deg g}
static long mapRank(const std::vector<Poly>& g, int d, int dt) {
    long nd = byDeg[d].size(), nt = byDeg[dt].size();
    nmod_mat_t M; nmod_mat_init(M, nt, g.size() * nd, 3);
    for (size_t i = 0; i < g.size(); i++) for (long r = 0; r < nd; r++) for (auto& [c, x] : g[i]) {
        int m = byDeg[d][r]; if (m & c) continue; long row = idx[m | c];
        nmod_mat_entry(M, row, i * nd + r) = (nmod_mat_entry(M, row, i * nd + r) + x) % 3;
    }
    long rk = nmod_mat_rank(M); nmod_mat_clear(M); return rk;
}

int main(int argc, char** argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s OUT N seed e\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w"); NN = atoi(argv[2]); unsigned seed = atoi(argv[3]); int e = atoi(argv[4]);
    int total = 1 << NN; dg.assign(total, 0); idx.assign(total, 0); byDeg.assign(NN + 1, {});
    for (int c = 0; c < total; c++) { dg[c] = __builtin_popcount(c); idx[c] = byDeg[dg[c]].size(); byDeg[dg[c]].push_back(c); }
    std::mt19937 rng(seed);
    std::vector<std::vector<int>> coef(4, std::vector<int>(NN, 0));
    for (int b = 0; b < 2; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < NN; col++) coef[2 * b + w][col] = rng() % 3;
    std::vector<Poly> F(4);
    for (int f = 0; f < 4; f++) for (int i = 0; i < NN; i++) if (coef[f][i]) F[f].push_back({1 << i, coef[f][i]});
    Poly A = F[0], B = F[1], C = F[2], D = F[3];
    Poly tau = mul(mul(A, A), B), sigma = mul(mul(C, C), D);
    std::vector<Poly> tops = {tau, sigma};
    // Taylor span dimension in multiplier degree d: rank of Frobenius and Koszul generators
    auto taylorRank = [&](int d) {
        long nd = byDeg[d].size();
        std::vector<std::vector<std::pair<long, int>>> gens;
        auto add = [&](int slot, const Poly& p, std::vector<std::pair<long, int>>& g, int sign) { for (auto& [c, x] : p) g.push_back({slot * nd + idx[c], ((sign * x) % 3 + 3) % 3}); };
        Poly B2 = mul(B, B), D2 = mul(D, D);
        if (d >= 1) for (int x : byDeg[d - 1]) { std::vector<std::pair<long, int>> g; add(0, mul(A, {{x, 1}}), g, 1); gens.push_back(g); g.clear(); add(1, mul(C, {{x, 1}}), g, 1); gens.push_back(g); }
        if (d >= 2) for (int x : byDeg[d - 2]) { std::vector<std::pair<long, int>> g; add(0, mul(B2, {{x, 1}}), g, 1); gens.push_back(g); g.clear(); add(1, mul(D2, {{x, 1}}), g, 1); gens.push_back(g); }
        if (d >= 3) for (int x : byDeg[d - 3]) { std::vector<std::pair<long, int>> g; add(0, mul(sigma, {{x, 1}}), g, 1); add(1, mul(tau, {{x, 1}}), g, -1); gens.push_back(g); }
        nmod_mat_t M; nmod_mat_init(M, gens.size(), 2 * nd, 3);
        for (size_t i = 0; i < gens.size(); i++) for (auto& [c, x] : gens[i]) nmod_mat_entry(M, i, c) = (nmod_mat_entry(M, i, c) + x) % 3;
        long rk = gens.empty() ? 0 : nmod_mat_rank(M); nmod_mat_clear(M); return std::make_pair(rk, gens);
    };
    // defect in multiplier degree e-1
    long nprev = byDeg[e - 1].size();
    long syzPrev = 2 * nprev - mapRank(tops, e - 1, e + 2);
    long defPrev = syzPrev - taylorRank(e - 1).first;
    // quotient of S_{e+2} by I_{e+2} = tau S_{e-1} + sigma S_{e-1}: rref of the generators
    long n6 = byDeg[e + 2].size();
    nmod_mat_t G; nmod_mat_init(G, 2 * nprev, n6, 3);
    for (int s = 0; s < 2; s++) for (long r = 0; r < nprev; r++) for (auto& [c, x] : tops[s]) {
        int m = byDeg[e - 1][r]; if (m & c) continue;
        nmod_mat_entry(G, s * nprev + r, idx[m | c]) = (nmod_mat_entry(G, s * nprev + r, idx[m | c]) + x) % 3;
    }
    long rI = nmod_mat_rref(G);
    std::vector<long> piv(rI); std::vector<char> isPiv(n6, 0);
    for (long i = 0; i < rI; i++) { long j = 0; while (nmod_mat_entry(G, i, j) == 0) j++; piv[i] = j; isPiv[j] = 1; }
    std::vector<long> npPos(n6, -1); long nq = 0;
    for (long j = 0; j < n6; j++) if (!isPiv[j]) npPos[j] = nq++;
    // rref rows restricted to non-pivot coordinates, sparse; the rows vanish at the other pivots
    std::vector<long> rowOf(n6, -1); for (long i = 0; i < rI; i++) rowOf[piv[i]] = i;
    std::vector<std::vector<std::pair<long, long>>> rowNp(rI);
    for (long i = 0; i < rI; i++) for (long j = 0; j < n6; j++) { long g = nmod_mat_entry(G, i, j); if (g && !isPiv[j]) rowNp[i].push_back({npPos[j], g}); }
    auto quot = [&](const Poly& p, std::vector<long>& q) {  // class of p in S_{e+2}/I, on non-pivot coordinates
        q.assign(nq, 0);
        for (auto& [c, v] : p) {
            long j = idx[c];
            if (!isPiv[j]) { q[npPos[j]] = (q[npPos[j]] + v) % 3; continue; }
            for (auto& [k, g] : rowNp[rowOf[j]]) q[k] = ((q[k] - v * g) % 3 + 3) % 3;
        }
    };
    // constraints on z in S_e^2: syzygy equations, and the four products in I
    long ne = byDeg[e].size(), ns = byDeg[e + 3].size();
    Poly AB = mul(A, B), A2 = mul(A, A), CD = mul(C, D), C2 = mul(C, C);
    nmod_mat_t K; nmod_mat_init(K, ns + 4 * nq, 2 * ne, 3);
    std::vector<long> q;
    for (long r = 0; r < ne; r++) {
        Poly mono = {{byDeg[e][r], 1}};
        for (int s = 0; s < 2; s++) for (auto& [c, x] : mul(mono, tops[s])) nmod_mat_entry(K, idx[c], s * ne + r) = (nmod_mat_entry(K, idx[c], s * ne + r) + x) % 3;
        const Poly* fac[4] = {&AB, &A2, &CD, &C2};
        for (int k = 0; k < 4; k++) {
            int slot = k < 2 ? 0 : 1;
            quot(mul(mono, *fac[k]), q);
            for (long j = 0; j < nq; j++) if (q[j]) nmod_mat_entry(K, ns + k * nq + j, slot * ne + r) = q[j];
        }
    }
    nmod_mat_t Z; nmod_mat_init(Z, 2 * ne, 2 * ne, 3);
    long dimW0 = nmod_mat_nullspace(Z, K);
    long syzE = 2 * ne - mapRank(tops, e, e + 3);
    auto tr = taylorRank(e); long rkT = tr.first;
    // dim(W_0 + T)
    nmod_mat_t U; nmod_mat_init(U, dimW0 + tr.second.size(), 2 * ne, 3);
    for (long j = 0; j < dimW0; j++) for (long i = 0; i < 2 * ne; i++) nmod_mat_entry(U, j, i) = nmod_mat_entry(Z, i, j);
    for (size_t g = 0; g < tr.second.size(); g++) for (auto& [c, x] : tr.second[g]) nmod_mat_entry(U, dimW0 + g, c) = (nmod_mat_entry(U, dimW0 + g, c) + x) % 3;
    long rkU = nmod_mat_rank(U);
    fprintf(out, "{\"N\": %d, \"seed\": %u, \"e\": %d, \"defect_e_minus_1\": %ld, \"dim_syz_e\": %ld, \"rank_taylor_e\": %ld, "
                 "\"defect_e\": %ld, \"dim_I\": %ld, \"dim_W0\": %ld, \"dim_W0_plus_T\": %ld, \"universal_classes\": %ld}\n",
            NN, seed, e, defPrev, syzE, rkT, syzE - rkT, rI, dimW0, rkU, dimW0 - rkT);
    printf("N=%d seed=%u e=%d: Def_{e-1}=%ld Def_e=%ld W0=%ld W0+T=%ld T=%ld\n", NN, seed, e, defPrev, syzE - rkT, dimW0, rkU, rkT);
    fclose(out);
    return 0;
}
