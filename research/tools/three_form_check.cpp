// Three-form relations against conj:two-form-wilson-taylor (entry-2026-09-27-three-form-relations).
//
// Tested statement (conj:two-form-wilson-taylor at small size): on one row of N cells over F_3, three tops
// tau_i = A_i^2 B_i below the fill point whose linear parts have every nonzero combination of at most two forms
// supported on at least 2 emax + 2 cells are Taylor-generated (Frobenius syzygies and Koszul pairs) at every
// multiplier degree e <= emax.  The bold part is the restriction to two forms, so the related families have a short
// three-form combination: A_3 = A_1 + A_2 + delta with delta supported on `short` cells; the control families draw
// A_3 at random.  Both are rejection-sampled (seed, seed+1, ...) until the two-form condition holds, and the program
// reports the Taylor defect dim Syz_e - rank T_e for e = 1..emax.  Positive control (related = 2): A_3 = A_1 + delta, a
// near-shared squared form (prop:near-shared-syzygies), drawn without the two-form condition, which it violates.
// Pair mode (related = 3): two tops A^2 B, C^2 E with E = -(A + B + C) + delta, delta on `short` cells, so the four-form
// combination A + B + C + E is short while the two-form condition is enforced (entry-2026-09-27-pair-relations);
// related = 4 is its control, a random pair under the same two-form condition.
// Exact linear algebra with FLINT nmod_mat.  Usage: three_form_check OUT "N:emax:short:related(0/1):seed,..."
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <sstream>
#include <string>
#include <vector>

typedef std::vector<std::pair<int, int>> Poly;
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
static Poly form(const std::vector<int>& cf) { Poly p; for (int i = 0; i < NN; i++) if (cf[i]) p.push_back({1 << i, cf[i]}); return p; }

static long defect(const std::vector<std::vector<int>>& cf, int M, int e) {
    std::vector<Poly> L0(M), L1(M), tops(M);
    for (int b = 0; b < M; b++) { L0[b] = form(cf[2 * b]); L1[b] = form(cf[2 * b + 1]); tops[b] = mul(mul(L0[b], L0[b]), L1[b]); }
    long ne = byDeg[e].size(), ns = byDeg[e + 3].size(), cols = (long)M * ne;
    nmod_mat_t A; nmod_mat_init(A, ns, cols, 3);
    for (int s = 0; s < M; s++) for (long r = 0; r < ne; r++) for (auto& [c, x] : tops[s]) {
        int m = byDeg[e][r]; if (m & c) continue; long row = idx[m | c];
        nmod_mat_entry(A, row, s * ne + r) = (nmod_mat_entry(A, row, s * ne + r) + x) % 3; }
    long rk = nmod_mat_rank(A); nmod_mat_clear(A);
    long dimSyz = cols - rk;
    std::vector<std::vector<long>> T;
    auto addTo = [&](std::vector<long>& v, int slot, const Poly& p, int sign) { for (auto& [c, x] : p) v[slot * ne + idx[c]] = ((v[slot * ne + idx[c]] + sign * x) % 3 + 3) % 3; };
    for (int b = 0; b < M; b++) {
        Poly B2 = mul(L1[b], L1[b]);
        if (e >= 1) for (int x : byDeg[e - 1]) { std::vector<long> v(cols, 0); addTo(v, b, mul(L0[b], {{x, 1}}), 1); T.push_back(v); }
        if (e >= 2) for (int x : byDeg[e - 2]) { std::vector<long> v(cols, 0); addTo(v, b, mul(B2, {{x, 1}}), 1); T.push_back(v); }
    }
    if (e >= 3) for (int b = 0; b < M; b++) for (int c = b + 1; c < M; c++) for (int x : byDeg[e - 3]) {
        std::vector<long> v(cols, 0); addTo(v, b, mul(tops[c], {{x, 1}}), 1); addTo(v, c, mul(tops[b], {{x, 1}}), -1); T.push_back(v); }
    long rkT = 0;
    if (!T.empty()) { nmod_mat_t TM; nmod_mat_init(TM, T.size(), cols, 3);
        for (size_t i = 0; i < T.size(); i++) for (long j = 0; j < cols; j++) nmod_mat_entry(TM, i, j) = T[i][j];
        rkT = nmod_mat_rank(TM); nmod_mat_clear(TM); }
    return dimSyz - rkT;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s OUT N:emax:short:related:seed,...\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w");
    std::stringstream ss(argv[2]); std::string item;
    while (std::getline(ss, item, ',')) {
        int N, emax, sh, related; unsigned seed;
        if (sscanf(item.c_str(), "%d:%d:%d:%d:%u", &N, &emax, &sh, &related, &seed) != 5) return 2;
        NN = N; idx.assign(1 << N, 0); byDeg.assign(N + 1, {});
        for (int c = 0; c < (1 << N); c++) { int d = __builtin_popcount(c); idx[c] = byDeg[d].size(); byDeg[d].push_back(c); }
        int M = related >= 3 ? 2 : 3, F = 2 * M, need = 2 * emax + 2; long tries = 0; unsigned s = seed;
        std::vector<std::vector<int>> cf(F, std::vector<int>(N));
        std::vector<int> delta(N, 0);
        while (true) {
            std::mt19937 rng(s++); tries++;
            for (int f = 0; f < F; f++) for (int i = 0; i < N; i++) cf[f][i] = rng() % 3;
            if (related && related != 4) { std::fill(delta.begin(), delta.end(), 0);
                for (int k = 0; k < sh; k++) { int i = rng() % N; delta[i] = 1 + rng() % 2; }
                if (related == 3) { for (int i = 0; i < N; i++) cf[3][i] = (6 - cf[0][i] - cf[1][i] - cf[2][i] + delta[i]) % 3; }
                else for (int i = 0; i < N; i++) cf[4][i] = (cf[0][i] + (related == 1 ? cf[2][i] : 0) + delta[i]) % 3; }
            if (related == 2) break;
            // every nonzero combination of at most two forms has at least `need` cells
            bool ok = true;
            for (int f = 0; f < F && ok; f++) for (int g = f; g < F && ok; g++) for (int a = 1; a < 3 && ok; a++) for (int b = 0; b < 3 && ok; b++) {
                if (g == f && b) continue;
                int sup = 0; for (int i = 0; i < N; i++) sup += (a * cf[f][i] + (g == f ? 0 : b * cf[g][i])) % 3 != 0;
                if (sup < need) ok = false; }
            if (ok) break;
            if (tries > 2000000) { fprintf(stderr, "no family found\n"); return 4; }
        }
        int sup3 = 0;
        if (related >= 3) { for (int i = 0; i < N; i++) sup3 += (cf[0][i] + cf[1][i] + cf[2][i] + cf[3][i]) % 3 != 0; }
        else for (int i = 0; i < N; i++) sup3 += (cf[0][i] + cf[2][i] + 2 * cf[4][i]) % 3 != 0;
        fprintf(out, "{\"N\": %d, \"emax\": %d, \"related\": %d, \"short\": %d, \"seed_found\": %u, \"tries\": %ld, \"two_form_min\": %d, \"A1+A2-A3_support\": %d, \"defects\": [",
                N, emax, related, sh, s - 1, tries, need, sup3);
        printf("N=%d emax=%d related=%d: seed %u after %ld tries, A1+A2-A3 on %d cells; defects", N, emax, related, s - 1, tries, sup3);
        for (int e = 1; e <= emax; e++) { long d = defect(cf, M, e); fprintf(out, "%s%ld", e > 1 ? ", " : "", d); printf(" %ld", d); fflush(stdout); }
        fprintf(out, "]}\n"); fflush(out); printf("\n");
    }
    fclose(out); return 0;
}
