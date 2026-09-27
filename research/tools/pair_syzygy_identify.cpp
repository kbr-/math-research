// Identify the non-Taylor pair syzygy of random dense tops (entry-2026-09-27-pair-syzygy).
//
// Question: ex:pseudorandom-taylor-check found, for two random dense tops tau = A^2 B and sigma = C^2 D on the
// square-free algebra S of N cells over F_3 (one row of the board), top syzygies in multiplier degree 4 (target
// degree 7) outside the span T of the Frobenius syzygies (A x, B^2 x in slot 1; C x, D^2 x in slot 2) and the
// Koszul pairs.  Hypothesis tested: such syzygies have both components in the span Gamma of the degree-4 elements
// built from the four forms with divided powers X^[k] = sum over k-sets of the products of coefficients: monomials
// A^a B^b C^c D^d (exponents <= 2), X^[3] Y and X^[4] for X, Y in {A, B, C, D}.  The program reproduces the forms of
// pseudorandom_taylor_check (same generator and order), computes dim Syz, rank T, the syzygies inside Gamma x Gamma,
// and how many of them lie outside T, and prints those syzygies' coefficient vectors on the Gamma labels.
// Exact linear algebra with FLINT nmod_mat.  Usage: pair_syzygy_identify OUT N seed.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <random>
#include <cassert>

typedef std::vector<std::pair<int, int>> Poly;

struct Board {
    int N; std::vector<int> deg, index; std::vector<std::vector<int>> byDeg;
    Board(int N_) : N(N_) {
        int total = 1 << N; deg.assign(total, 0); index.assign(total, -1); byDeg.assign(N + 1, {});
        for (int c = 0; c < total; c++) { deg[c] = __builtin_popcount(c); index[c] = byDeg[deg[c]].size(); byDeg[deg[c]].push_back(c); }
    }
};

static Poly mul(const Board& B, const Poly& a, const Poly& b) {
    static std::vector<int> buf; if (buf.size() < (size_t)(1 << B.N)) buf.assign(1 << B.N, 0);
    std::vector<int> touched;
    for (auto& [ca, xa] : a) for (auto& [cb, xb] : b) if (!(ca & cb)) {
        int c = ca | cb; if (!buf[c]) touched.push_back(c);
        buf[c] = (buf[c] + xa * xb) % 3; if (!buf[c]) buf[c] = 3;
    }
    Poly out; for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}

static Poly divpow(const Board& B, const std::vector<int>& x, int k) {  // X^[k]
    Poly out;
    for (int c : B.byDeg[k]) { int v = 1; for (int i = 0; i < B.N; i++) if (c >> i & 1) v = v * x[i] % 3; if (v) out.push_back({c, v}); }
    return out;
}

static long rankOf(nmod_mat_t M) { nmod_mat_t C; nmod_mat_init_set(C, M); long r = nmod_mat_rank(C); nmod_mat_clear(C); return r; }

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s OUT N seed\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w"); int N = atoi(argv[2]); unsigned seed = atoi(argv[3]);
    Board B(N);
    std::mt19937 rng(seed);
    // same draw order as pseudorandom_taylor_check with m = 1: block 0 forms L0, L1, then block 1
    std::vector<std::vector<int>> coef(4, std::vector<int>(N, 0));
    for (int b = 0; b < 2; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < N; col++) coef[2 * b + w][col] = rng() % 3;
    std::vector<Poly> F(4);
    for (int f = 0; f < 4; f++) for (int i = 0; i < N; i++) if (coef[f][i]) F[f].push_back({1 << i, coef[f][i]});
    const char* nm = "ABCD";
    Poly tau = mul(B, mul(B, F[0], F[0]), F[1]), sigma = mul(B, mul(B, F[2], F[2]), F[3]);
    int e = 4; const auto& Re = B.byDeg[e]; const auto& Rs = B.byDeg[7];
    long ne = Re.size(), ns = Rs.size();
    auto vecOf = [&](const Poly& p, std::vector<long>& v, long off, int sign) { for (auto& [c, x] : p) { assert(B.deg[c] == e); v[off + B.index[c]] = ((v[off + B.index[c]] + sign * x) % 3 + 3) % 3; } };
    // full map and Taylor span
    nmod_mat_t Mfull; nmod_mat_init(Mfull, ns, 2 * ne, 3);
    for (int s = 0; s < 2; s++) for (long ri = 0; ri < ne; ri++) for (auto& [t, x] : (s ? sigma : tau)) {
        int r = Re[ri]; if (r & t) continue; long row = B.index[r | t];
        nmod_mat_entry(Mfull, row, s * ne + ri) = (nmod_mat_entry(Mfull, row, s * ne + ri) + x) % 3;
    }
    long rkMap = rankOf(Mfull), dimSyz = 2 * ne - rkMap;
    std::vector<std::vector<long>> T;
    auto addGen = [&](int slot, const Poly& p) { std::vector<long> v(2 * ne, 0); vecOf(p, v, slot * ne, 1); T.push_back(v); };
    Poly B2 = mul(B, F[1], F[1]), D2 = mul(B, F[3], F[3]);
    for (int x : B.byDeg[e - 1]) { addGen(0, mul(B, F[0], {{x, 1}})); addGen(1, mul(B, F[2], {{x, 1}})); }
    for (int x : B.byDeg[e - 2]) { addGen(0, mul(B, B2, {{x, 1}})); addGen(1, mul(B, D2, {{x, 1}})); }
    for (int x : B.byDeg[e - 3]) { std::vector<long> v(2 * ne, 0); vecOf(mul(B, sigma, {{x, 1}}), v, 0, 1); vecOf(mul(B, tau, {{x, 1}}), v, ne, -1); T.push_back(v); }
    auto rankRows = [&](const std::vector<std::vector<long>>& rows) {
        nmod_mat_t M; nmod_mat_init(M, rows.size(), 2 * ne, 3);
        for (size_t i = 0; i < rows.size(); i++) for (long j = 0; j < 2 * ne; j++) nmod_mat_entry(M, i, j) = rows[i][j];
        long r = rows.empty() ? 0 : nmod_mat_rank(M); nmod_mat_clear(M); return r;
    };
    long rkT = rankRows(T);
    // Gamma: degree-4 elements from the four forms with divided powers
    std::vector<Poly> G; std::vector<std::string> lab;
    for (int a = 0; a <= 2; a++) for (int b = 0; b <= 2; b++) for (int c = 0; c <= 2; c++) for (int d = 0; d <= 2; d++) {
        if (a + b + c + d != 4) continue;
        Poly p = {{0, 1}}; int ex[4] = {a, b, c, d}; std::string l;
        for (int f = 0; f < 4; f++) for (int k = 0; k < ex[f]; k++) { p = mul(B, p, F[f]); l += nm[f]; }
        G.push_back(p); lab.push_back(l);
    }
    for (int X = 0; X < 4; X++) {
        for (int Y = 0; Y < 4; Y++) { G.push_back(mul(B, divpow(B, coef[X], 3), F[Y])); lab.push_back(std::string(1, nm[X]) + "[3]" + nm[Y]); }
        G.push_back(divpow(B, coef[X], 4)); lab.push_back(std::string(1, nm[X]) + "[4]");
    }
    long ng = G.size();
    nmod_mat_t Mg; nmod_mat_init(Mg, ns, 2 * ng, 3);
    for (int s = 0; s < 2; s++) for (long i = 0; i < ng; i++) for (auto& [c, x] : mul(B, G[i], s ? sigma : tau))
        nmod_mat_entry(Mg, B.index[c], s * ng + i) = (nmod_mat_entry(Mg, B.index[c], s * ng + i) + x) % 3;
    nmod_mat_t K; nmod_mat_init(K, 2 * ng, 2 * ng, 3);
    long nul = nmod_mat_nullspace(K, Mg);
    std::vector<std::vector<long>> gsyz;
    for (long j = 0; j < nul; j++) {
        std::vector<long> v(2 * ne, 0);
        for (int s = 0; s < 2; s++) for (long i = 0; i < ng; i++) { long c = nmod_mat_entry(K, s * ng + i, j); if (c) vecOf(G[i], v, s * ne, (int)c); }
        gsyz.push_back(v);
    }
    std::vector<std::vector<long>> TG = T; TG.insert(TG.end(), gsyz.begin(), gsyz.end());
    long extra = rankRows(TG) - rkT;
    fprintf(out, "{\"N\": %d, \"seed\": %u, \"dim_syz\": %ld, \"rank_taylor\": %ld, \"defect\": %ld, \"gamma_size\": %ld, "
                 "\"gamma_syzygies\": %ld, \"gamma_non_taylor\": %ld}\n", N, seed, dimSyz, rkT, dimSyz - rkT, ng, nul, extra);
    printf("N=%d seed=%u: defect %ld; Gamma syzygies %ld, outside Taylor %ld\n", N, seed, dimSyz - rkT, nul, extra);
    // print each Gamma syzygy that is outside T on its own
    for (long j = 0; j < nul; j++) {
        std::vector<std::vector<long>> one = T; one.push_back(gsyz[j]);
        if (rankRows(one) == rkT) continue;
        fprintf(out, "non-Taylor Gamma syzygy %ld: slot tau:", j);
        for (long i = 0; i < ng; i++) { long c = nmod_mat_entry(K, i, j); if (c) fprintf(out, " %+ld*%s", c == 2 ? -1L : c, lab[i].c_str()); }
        fprintf(out, " | slot sigma:");
        for (long i = 0; i < ng; i++) { long c = nmod_mat_entry(K, ng + i, j); if (c) fprintf(out, " %+ld*%s", c == 2 ? -1L : c, lab[i].c_str()); }
        fprintf(out, "\n");
    }
    fclose(out);
    return 0;
}
