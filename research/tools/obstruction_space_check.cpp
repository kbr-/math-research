// Obstruction spaces of the non-Taylor classes of a base board (entry-2026-09-27-obstruction-weights).
//
// For M random dense tops tau_b = L_{b,0}^2 L_{b,1} on the square-free algebra S of N cells over F_3 (one row,
// generated as in pseudorandom_taylor_check), in multiplier degree e, with I = sum_b tau_b S, Q = Syz_e / T_e and
// components phi_{b,0}(x) = 2 x_b L_{b,0} L_{b,1}, phi_{b,1}(x) = x_b L_{b,0}^2 in V = (S/I)_{e+2}, the obstruction
// space of a class x is P(x) = {(lambda(phi_{b,j}(x)))_{b,j} : lambda in V^*}, a subspace of F_3^{2M}.  A class
// survives an extension only if P(x) lies in the relations Rel of the forms off the base (prop:relation-avoidance),
// so by the Singleton bound its least weight is at most n_x - dim P(x) + 1, n_x the number of nonzero components.
// The program reports:
//   rank-one scan: for every nonzero mu in F_3^{2M} up to sign, dim R(mu), R(mu) = {x in Q : Phi(x) in mu (x) V};
//   classes: for every class (all of Q if 3^dim Q <= 200000, else a fixed-seed random sample of 20000), the
//   distribution of (n_x, dim P(x)) and of the least weight of P(x).
// Exact linear algebra with FLINT nmod_mat.  Usage: obstruction_space_check OUT CASES, CASES = N:M:seed:e,...
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <vector>

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

// rref of rows; returns rank, basis rows and pivot columns
static long rref(const std::vector<Vec>& rows, long cols, std::vector<Vec>& basis, std::vector<long>& piv) {
    basis.clear(); piv.clear(); if (rows.empty()) return 0;
    nmod_mat_t A; nmod_mat_init(A, rows.size(), cols, 3);
    for (size_t i = 0; i < rows.size(); i++) for (long j = 0; j < cols; j++) nmod_mat_entry(A, i, j) = rows[i][j];
    long r = nmod_mat_rref(A);
    for (long i = 0; i < r; i++) { Vec v(cols); long p = -1; for (long j = 0; j < cols; j++) { v[j] = nmod_mat_entry(A, i, j); if (p < 0 && v[j]) p = j; } basis.push_back(v); piv.push_back(p); }
    nmod_mat_clear(A); return r;
}
static long rankOf(const std::vector<Vec>& rows, long cols) { std::vector<Vec> b; std::vector<long> p; return rref(rows, cols, b, p); }
static long nullity(const std::vector<Vec>& rows, long cols) { return cols - rankOf(rows, cols); }

static void runCase(FILE* out, int N, int M, unsigned seed, int e) {
    NN = N; int total = 1 << NN; idx.assign(total, 0); byDeg.assign(NN + 1, {});
    for (int c = 0; c < total; c++) { int d = __builtin_popcount(c); idx[c] = byDeg[d].size(); byDeg[d].push_back(c); }
    std::mt19937 rng(seed);
    std::vector<Poly> L0(M), L1(M), tops(M);
    for (int b = 0; b < M; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < NN; col++) { int v = rng() % 3; if (v) (w ? L1[b] : L0[b]).push_back({1 << col, v}); }
    for (int b = 0; b < M; b++) tops[b] = mul(mul(L0[b], L0[b]), L1[b]);
    long ne = byDeg[e].size(), ns = byDeg[e + 3].size(), cols = (long)M * ne;
    // syzygies
    nmod_mat_t A; nmod_mat_init(A, ns, cols, 3);
    for (int s = 0; s < M; s++) for (long r = 0; r < ne; r++) for (auto& [c, x] : tops[s]) {
        int m = byDeg[e][r]; if (m & c) continue; long row = idx[m | c];
        nmod_mat_entry(A, row, s * ne + r) = (nmod_mat_entry(A, row, s * ne + r) + x) % 3;
    }
    nmod_mat_t K; nmod_mat_init(K, cols, cols, 3);
    long dimSyz = nmod_mat_nullspace(K, A);
    std::vector<Vec> syz(dimSyz, Vec(cols));
    for (long j = 0; j < dimSyz; j++) for (long i = 0; i < cols; i++) syz[j][i] = nmod_mat_entry(K, i, j);
    nmod_mat_clear(A); nmod_mat_clear(K);
    // Taylor span
    std::vector<Vec> T;
    auto addTo = [&](Vec& v, int slot, const Poly& p, int sign) { for (auto& [c, x] : p) v[slot * ne + idx[c]] = ((v[slot * ne + idx[c]] + sign * x) % 3 + 3) % 3; };
    for (int b = 0; b < M; b++) {
        Poly B2 = mul(L1[b], L1[b]);
        for (int x : byDeg[e - 1]) { Vec v(cols, 0); addTo(v, b, mul(L0[b], {{x, 1}}), 1); T.push_back(v); }
        for (int x : byDeg[e - 2]) { Vec v(cols, 0); addTo(v, b, mul(B2, {{x, 1}}), 1); T.push_back(v); }
    }
    for (int b = 0; b < M; b++) for (int c = b + 1; c < M; c++) for (int x : byDeg[e - 3]) { Vec v(cols, 0); addTo(v, b, mul(tops[c], {{x, 1}}), 1); addTo(v, c, mul(tops[b], {{x, 1}}), -1); T.push_back(v); }
    std::vector<Vec> Tb; std::vector<long> Tp; long rkT = rref(T, cols, Tb, Tp);
    // class basis: syzygies raising the rank over T
    // residuals y - y[:, pivots] * Tb are syzygies (Taylor elements are syzygies); their row space is a complement
    std::vector<Vec> cls; {
        nmod_mat_t Y, Yp, TB, P; nmod_mat_init(Y, dimSyz, cols, 3); nmod_mat_init(Yp, dimSyz, rkT, 3); nmod_mat_init(TB, rkT, cols, 3); nmod_mat_init(P, dimSyz, cols, 3);
        for (long j = 0; j < dimSyz; j++) { for (long i = 0; i < cols; i++) nmod_mat_entry(Y, j, i) = syz[j][i]; for (long k = 0; k < rkT; k++) nmod_mat_entry(Yp, j, k) = syz[j][Tp[k]]; }
        for (long k = 0; k < rkT; k++) for (long i = 0; i < cols; i++) nmod_mat_entry(TB, k, i) = Tb[k][i];
        nmod_mat_mul(P, Yp, TB); nmod_mat_sub(Y, Y, P);
        long r = nmod_mat_rref(Y);
        for (long i = 0; i < r; i++) { Vec v(cols); for (long j = 0; j < cols; j++) v[j] = nmod_mat_entry(Y, i, j); cls.push_back(v); }
        nmod_mat_clear(Y); nmod_mat_clear(Yp); nmod_mat_clear(TB); nmod_mat_clear(P); }
    long q = cls.size();
    if (q != dimSyz - rkT) { fprintf(stderr, "class count mismatch %ld vs %ld\n", q, dimSyz - rkT); exit(3); }
    // quotient S_{e+2} / I_{e+2}
    long nprev = byDeg[e - 1].size(), n6 = byDeg[e + 2].size();
    nmod_mat_t G; nmod_mat_init(G, (long)M * nprev, n6, 3);
    for (int s = 0; s < M; s++) for (long r = 0; r < nprev; r++) for (auto& [c, x] : tops[s]) {
        int m = byDeg[e - 1][r]; if (m & c) continue;
        nmod_mat_entry(G, s * nprev + r, idx[m | c]) = (nmod_mat_entry(G, s * nprev + r, idx[m | c]) + x) % 3;
    }
    long rI = nmod_mat_rref(G);
    std::vector<long> rowOf(n6, -1), npPos(n6, -1); std::vector<char> isPiv(n6, 0);
    for (long i = 0; i < rI; i++) { long j = 0; while (nmod_mat_entry(G, i, j) == 0) j++; isPiv[j] = 1; rowOf[j] = i; }
    long nq = 0; for (long j = 0; j < n6; j++) if (!isPiv[j]) npPos[j] = nq++;
    std::vector<std::vector<std::pair<long, long>>> rowNp(rI);
    for (long i = 0; i < rI; i++) for (long j = 0; j < n6; j++) { long g = nmod_mat_entry(G, i, j); if (g && !isPiv[j]) rowNp[i].push_back({npPos[j], g}); }
    nmod_mat_clear(G);
    auto quot = [&](const Poly& p) {
        Vec v(nq, 0);
        for (auto& [c, x] : p) { long j = idx[c];
            if (!isPiv[j]) { v[npPos[j]] = (v[npPos[j]] + x) % 3; continue; }
            for (auto& [k, g] : rowNp[rowOf[j]]) v[k] = ((v[k] - x * g) % 3 + 3) % 3; }
        return v;
    };
    std::vector<Poly> F0(M), F1(M);
    for (int b = 0; b < M; b++) { F0[b] = mul(L0[b], L1[b]); for (auto& t : F0[b]) t.second = t.second * 2 % 3; F1[b] = mul(L0[b], L0[b]); }
    auto slotPoly = [&](const Vec& y, int b) { Poly p; for (long r = 0; r < ne; r++) if (y[b * ne + r]) p.push_back({byDeg[e][r], (int)y[b * ne + r]}); return p; };
    int F = 2 * M;
    // components of the basis classes in V, then coordinates in their span W
    std::vector<std::vector<Vec>> comp(q, std::vector<Vec>(F));
    std::vector<Vec> allc;
    for (long i = 0; i < q; i++) for (int b = 0; b < M; b++) { Poly ys = slotPoly(cls[i], b);
        comp[i][2 * b] = quot(mul(ys, F0[b])); comp[i][2 * b + 1] = quot(mul(ys, F1[b]));
        allc.push_back(comp[i][2 * b]); allc.push_back(comp[i][2 * b + 1]); }
    std::vector<Vec> Wb; std::vector<long> Wp; long w = rref(allc, nq, Wb, Wp);
    // coordinates: v = sum_k v[Wp[k]] * Wb[k] since Wb is reduced
    std::vector<std::vector<Vec>> cc(q, std::vector<Vec>(F, Vec(w)));
    for (long i = 0; i < q; i++) for (int f = 0; f < F; f++) for (long k = 0; k < w; k++) cc[i][f][k] = comp[i][f][Wp[k]];
    // injectivity of Phi on Q
    std::vector<Vec> phiRows(q, Vec((long)F * w));
    for (long i = 0; i < q; i++) for (int f = 0; f < F; f++) for (long k = 0; k < w; k++) phiRows[i][f * w + k] = cc[i][f][k];
    long rkPhi = rankOf(phiRows, (long)F * w);
    // rank-one scan
    std::map<int, long> byWeight; long nonzeroMu = 0; long maxDim = 0; int maxW = 0;
    std::vector<std::pair<std::vector<int>, long>> found;
    long nmu = 1; for (int f = 0; f < F; f++) nmu *= 3;
    for (long code = 1; code < nmu; code++) {
        std::vector<int> mu(F); long c = code; for (int f = 0; f < F; f++) { mu[f] = c % 3; c /= 3; }
        int lead = -1; for (int f = F - 1; f >= 0; f--) if (mu[f]) { lead = f; break; }
        if (mu[lead] != 1) continue;  // up to sign
        int p0 = -1; for (int f = 0; f < F; f++) if (mu[f]) { p0 = f; break; }
        // conditions on c in F_3^q: comp_f(c) = 0 if mu_f = 0; mu_{p0} comp_f(c) - mu_f comp_{p0}(c) = 0 otherwise
        std::vector<Vec> rows;
        for (int f = 0; f < F; f++) { if (f == p0) continue;
            for (long k = 0; k < w; k++) { Vec r(q); bool nz = false;
                for (long i = 0; i < q; i++) { long v = ((mu[p0] * cc[i][f][k] - mu[f] * cc[i][p0][k]) % 3 + 3) % 3; r[i] = v; nz |= v != 0; }
                if (nz) rows.push_back(r); } }
        long d = nullity(rows, q);
        // classes with Phi(x) = 0 lie in every R(mu); subtract them (rank of Phi deficiency)
        long dEff = d - (q - rkPhi);
        if (dEff > 0) { nonzeroMu++; int wt = 0; for (int f = 0; f < F; f++) wt += mu[f] != 0; byWeight[wt] += dEff; if (dEff > maxDim) maxDim = dEff; if (wt > maxW) maxW = wt; found.push_back({mu, dEff}); }
    }
    // class statistics
    std::map<std::pair<int, int>, long> nr; std::map<int, long> lw; long sample = 0;
    long full = 1; bool all = true; for (long i = 0; i < q; i++) { full *= 3; if (full > 200000) { all = false; break; } }
    std::mt19937 rs(12345);
    long count = all ? full - 1 : 20000;
    for (long t = 0; t < count; t++) {
        Vec c(q); if (all) { long x = t + 1; for (long i = 0; i < q; i++) { c[i] = x % 3; x /= 3; } } else { bool nz = false; while (!nz) for (long i = 0; i < q; i++) { c[i] = rs() % 3; nz |= c[i] != 0; } }
        std::vector<Vec> cm(F, Vec(w, 0));
        for (long i = 0; i < q; i++) if (c[i]) for (int f = 0; f < F; f++) for (long k = 0; k < w; k++) cm[f][k] = (cm[f][k] + c[i] * cc[i][f][k]) % 3;
        int nx = 0; for (int f = 0; f < F; f++) { bool nz = false; for (long v : cm[f]) nz |= v != 0; nx += nz; }
        // P(x) = column space of the F x w matrix cm: basis via rref of its transpose
        std::vector<Vec> colsT(w, Vec(F)); for (long k = 0; k < w; k++) for (int f = 0; f < F; f++) colsT[k][f] = cm[f][k];
        std::vector<Vec> Pb; std::vector<long> Pp; long r = rref(colsT, F, Pb, Pp);
        nr[{nx, (int)r}]++;
        if (r > 0 && (all ? t < 20000 : true)) {
            long lim = 1; for (long i = 0; i < r; i++) lim *= 3; int best = F + 1;
            for (long cd = 1; cd < lim; cd++) { long x = cd; Vec v(F, 0); for (long i = 0; i < r; i++) { long a = x % 3; x /= 3; if (a) for (int f = 0; f < F; f++) v[f] = (v[f] + a * Pb[i][f]) % 3; }
                int wt = 0; for (int f = 0; f < F; f++) wt += v[f] != 0; if (wt < best) best = wt; }
            lw[best]++; }
        sample++;
    }
    fprintf(out, "{\"N\": %d, \"M\": %d, \"seed\": %u, \"e\": %d, \"dim_syz\": %ld, \"rank_taylor\": %ld, \"dim_Q\": %ld, \"rank_Phi\": %ld, \"dim_W\": %ld, ",
            N, M, seed, e, dimSyz, rkT, q, rkPhi, w);
    fprintf(out, "\"rank_one\": {\"directions\": %ld, \"max_dim\": %ld, \"max_weight\": %d, \"dim_by_weight\": {", nonzeroMu, maxDim, maxW);
    bool first = true; for (auto& [k, v] : byWeight) { fprintf(out, "%s\"%d\": %ld", first ? "" : ", ", k, v); first = false; }
    fprintf(out, "}, \"list\": [");
    first = true; for (auto& [mu, d] : found) { fprintf(out, "%s{\"mu\": \"", first ? "" : ", "); for (int f = 0; f < F; f++) fprintf(out, "%d", mu[f]); fprintf(out, "\", \"dim\": %ld}", d); first = false; }
    fprintf(out, "]}, \"classes\": {\"exhaustive\": %s, \"count\": %ld, \"nx_dimP\": {", all ? "true" : "false", sample);
    first = true; for (auto& [k, v] : nr) { fprintf(out, "%s\"%d,%d\": %ld", first ? "" : ", ", k.first, k.second, v); first = false; }
    fprintf(out, "}, \"least_weight\": {");
    first = true; for (auto& [k, v] : lw) { fprintf(out, "%s\"%d\": %ld", first ? "" : ", ", k, v); first = false; }
    fprintf(out, "}}}\n"); fflush(out);
    printf("N=%d M=%d seed=%u e=%d: dim Q %ld, rank Phi %ld, dim W %ld; rank-one directions %ld (max dim %ld, max weight %d)\n",
           N, M, seed, e, q, rkPhi, w, nonzeroMu, maxDim, maxW); fflush(stdout);
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s OUT N:M:seed:e,...\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w");
    std::stringstream ss(argv[2]); std::string item;
    while (std::getline(ss, item, ',')) { int N, M, e; unsigned seed; if (sscanf(item.c_str(), "%d:%d:%u:%d", &N, &M, &seed, &e) != 4) return 2; runCase(out, N, M, seed, e); }
    fclose(out); return 0;
}
