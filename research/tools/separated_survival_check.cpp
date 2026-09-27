// Hypotheses of the separated survival theorem on a base board (entry-2026-09-27-separated-survival).
//
// For M random dense tops tau_b = L_{b,0}^2 L_{b,1} on the square-free algebra S of N cells over F_3 (one row,
// generated as in pseudorandom_taylor_check), in multiplier degree e, with I = sum_b tau_b S and
// Phi_{b,0}(z) = 2 z_b L_{b,0} L_{b,1}, Phi_{b,1}(z) = z_b L_{b,0}^2 (degree e + 2), the program computes:
//   pair generation: dim Syz_e, rank T_e, rank (T_e + all pair syzygies);
//   per pair p = {b, c}: dim Q_p = rank(T_e + P_p) - rank T_e (its non-Taylor classes), the rank of
//   y -> (Phi_{b,j}(y) mod I)_{b in p, j} on P_p (the classes have no universally liftable part iff it equals
//   dim Q_p), and r_p = dim V_p, V_p = span{Phi_{b,j}(y) mod I : y in P_p, b in p, j};
//   separation: whether dim(sum_p V_p) = sum_p r_p.
// Exact linear algebra with FLINT nmod_mat.  Usage: separated_survival_check OUT N M seed e.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>

typedef std::vector<std::pair<int, int>> Poly;
typedef std::vector<long> Vec;
static int NN;
static std::vector<int> idx;
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

static long rankRows(const std::vector<Vec>& rows, long cols, std::vector<Vec>* basis = nullptr) {
    if (rows.empty()) return 0;
    nmod_mat_t M; nmod_mat_init(M, rows.size(), cols, 3);
    for (size_t i = 0; i < rows.size(); i++) for (long j = 0; j < cols; j++) nmod_mat_entry(M, i, j) = rows[i][j];
    long r = nmod_mat_rref(M);
    if (basis) { basis->clear(); for (long i = 0; i < r; i++) { Vec v(cols); for (long j = 0; j < cols; j++) v[j] = nmod_mat_entry(M, i, j); basis->push_back(v); } }
    nmod_mat_clear(M); return r;
}

int main(int argc, char** argv) {
    if (argc < 6) { fprintf(stderr, "usage: %s OUT N M seed e\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w"); NN = atoi(argv[2]); int M = atoi(argv[3]); unsigned seed = atoi(argv[4]); int e = atoi(argv[5]);
    int total = 1 << NN; idx.assign(total, 0); byDeg.assign(NN + 1, {});
    for (int c = 0; c < total; c++) { int d = __builtin_popcount(c); idx[c] = byDeg[d].size(); byDeg[d].push_back(c); }
    std::mt19937 rng(seed);
    std::vector<Poly> L0(M), L1(M), tops(M);
    for (int b = 0; b < M; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < NN; col++) { int v = rng() % 3; if (v) (w ? L1[b] : L0[b]).push_back({1 << col, v}); }
    for (int b = 0; b < M; b++) tops[b] = mul(mul(L0[b], L0[b]), L1[b]);
    long ne = byDeg[e].size(), ns = byDeg[e + 3].size(), cols = (long)M * ne;
    // syzygies supported on given slots
    auto subSyz = [&](const std::vector<int>& slots) {
        long k = slots.size();
        nmod_mat_t A; nmod_mat_init(A, ns, k * ne, 3);
        for (long s = 0; s < k; s++) for (long r = 0; r < ne; r++) for (auto& [c, x] : tops[slots[s]]) {
            int m = byDeg[e][r]; if (m & c) continue; long row = idx[m | c];
            nmod_mat_entry(A, row, s * ne + r) = (nmod_mat_entry(A, row, s * ne + r) + x) % 3;
        }
        nmod_mat_t K; nmod_mat_init(K, k * ne, k * ne, 3);
        long nul = nmod_mat_nullspace(K, A);
        std::vector<Vec> outv(nul, Vec(cols, 0));
        for (long j = 0; j < nul; j++) for (long s = 0; s < k; s++) for (long r = 0; r < ne; r++) outv[j][slots[s] * ne + r] = nmod_mat_entry(K, s * ne + r, j);
        nmod_mat_clear(A); nmod_mat_clear(K); return outv;
    };
    std::vector<int> all(M); for (int b = 0; b < M; b++) all[b] = b;
    long dimSyz = subSyz(all).size();
    std::vector<Vec> T;
    auto addTo = [&](Vec& v, int slot, const Poly& p, int sign) { for (auto& [c, x] : p) v[slot * ne + idx[c]] = ((v[slot * ne + idx[c]] + sign * x) % 3 + 3) % 3; };
    for (int b = 0; b < M; b++) {
        Poly B2 = mul(L1[b], L1[b]);
        for (int x : byDeg[e - 1]) { Vec v(cols, 0); addTo(v, b, mul(L0[b], {{x, 1}}), 1); T.push_back(v); }
        for (int x : byDeg[e - 2]) { Vec v(cols, 0); addTo(v, b, mul(B2, {{x, 1}}), 1); T.push_back(v); }
    }
    for (int b = 0; b < M; b++) for (int c = b + 1; c < M; c++) for (int x : byDeg[e - 3]) { Vec v(cols, 0); addTo(v, b, mul(tops[c], {{x, 1}}), 1); addTo(v, c, mul(tops[b], {{x, 1}}), -1); T.push_back(v); }
    std::vector<Vec> Tb; long rkT = rankRows(T, cols, &Tb);
    // quotient of S_{e+2} by I_{e+2}
    long nprev = byDeg[e - 1].size(), n6 = byDeg[e + 2].size();
    nmod_mat_t G; nmod_mat_init(G, (long)M * nprev, n6, 3);
    for (int s = 0; s < M; s++) for (long r = 0; r < nprev; r++) for (auto& [c, x] : tops[s]) {
        int m = byDeg[e - 1][r]; if (m & c) continue;
        nmod_mat_entry(G, s * nprev + r, idx[m | c]) = (nmod_mat_entry(G, s * nprev + r, idx[m | c]) + x) % 3;
    }
    long rI = nmod_mat_rref(G);
    std::vector<long> piv(rI), rowOf(n6, -1), npPos(n6, -1); std::vector<char> isPiv(n6, 0);
    for (long i = 0; i < rI; i++) { long j = 0; while (nmod_mat_entry(G, i, j) == 0) j++; piv[i] = j; isPiv[j] = 1; rowOf[j] = i; }
    long nq = 0; for (long j = 0; j < n6; j++) if (!isPiv[j]) npPos[j] = nq++;
    std::vector<std::vector<std::pair<long, long>>> rowNp(rI);
    for (long i = 0; i < rI; i++) for (long j = 0; j < n6; j++) { long g = nmod_mat_entry(G, i, j); if (g && !isPiv[j]) rowNp[i].push_back({npPos[j], g}); }
    auto quot = [&](const Poly& p) {
        Vec q(nq, 0);
        for (auto& [c, v] : p) { long j = idx[c];
            if (!isPiv[j]) { q[npPos[j]] = (q[npPos[j]] + v) % 3; continue; }
            for (auto& [k, g] : rowNp[rowOf[j]]) q[k] = ((q[k] - v * g) % 3 + 3) % 3; }
        return q;
    };
    std::vector<Poly> F0(M), F1(M);  // Phi_{b,0} = z_b * 2 L0 L1, Phi_{b,1} = z_b * L0^2
    for (int b = 0; b < M; b++) { F0[b] = mul(L0[b], L1[b]); for (auto& t : F0[b]) t.second = t.second * 2 % 3; F1[b] = mul(L0[b], L0[b]); }
    auto slotPoly = [&](const Vec& y, int b) { Poly p; for (long r = 0; r < ne; r++) if (y[b * ne + r]) p.push_back({byDeg[e][r], (int)y[b * ne + r]}); return p; };
    std::vector<Vec> TP = T; std::vector<Vec> allVbases; long sumR = 0;
    fprintf(out, "{\"N\": %d, \"M\": %d, \"seed\": %u, \"e\": %d, \"dim_syz\": %ld, \"rank_taylor\": %ld, \"dim_quotient\": %ld, \"pairs\": [", NN, M, seed, e, dimSyz, rkT, nq);
    bool first = true, allInjective = true;
    for (int b = 0; b < M; b++) for (int c = b + 1; c < M; c++) {
        auto P = subSyz({b, c});
        TP.insert(TP.end(), P.begin(), P.end());
        std::vector<Vec> TPp = Tb; TPp.insert(TPp.end(), P.begin(), P.end());
        long dimQp = rankRows(TPp, cols) - rkT;
        std::vector<Vec> phiRows, compRows;
        for (auto& y : P) {
            Vec big; for (int s : {b, c}) { Poly ys = slotPoly(y, s);
                Vec q0 = quot(mul(ys, F0[s])), q1 = quot(mul(ys, F1[s]));
                big.insert(big.end(), q0.begin(), q0.end()); big.insert(big.end(), q1.begin(), q1.end());
                bool nz0 = false, nz1 = false; for (long v : q0) nz0 |= v != 0; for (long v : q1) nz1 |= v != 0;
                if (nz0) compRows.push_back(q0); if (nz1) compRows.push_back(q1); }
            phiRows.push_back(big);
        }
        long rkPhi = rankRows(phiRows, 4 * nq);
        std::vector<Vec> Vb; long rp = rankRows(compRows, nq, &Vb);
        sumR += rp; allVbases.insert(allVbases.end(), Vb.begin(), Vb.end());
        if (rkPhi != dimQp) allInjective = false;
        fprintf(out, "%s{\"pair\": [%d, %d], \"dim_Qp\": %ld, \"rank_phi\": %ld, \"dim_Vp\": %ld}", first ? "" : ", ", b, c, dimQp, rkPhi, rp);
        first = false; fflush(out);
        printf("pair %d,%d: dim Q_p %ld, rank Phi %ld, dim V_p %ld\n", b, c, dimQp, rkPhi, rp); fflush(stdout);
    }
    long rkTP = rankRows(TP, cols);
    long dimSumV = rankRows(allVbases, nq);
    fprintf(out, "], \"rank_taylor_plus_pairs\": %ld, \"sum_dim_Vp\": %ld, \"dim_sum_Vp\": %ld, \"separated\": %s, \"no_universal_pair_classes\": %s}\n",
            rkTP, sumR, dimSumV, dimSumV == sumR ? "true" : "false", allInjective ? "true" : "false");
    printf("pair generation %s; separation %s (%ld vs %ld); pair classes injective %s\n", rkTP == dimSyz ? "holds" : "fails", dimSumV == sumR ? "holds" : "fails", dimSumV, sumR, allInjective ? "yes" : "no");
    fclose(out);
    return 0;
}
