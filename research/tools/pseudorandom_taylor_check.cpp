// Pseudorandom Taylor check (entry-2026-09-27-pseudorandom-check).
//
// Statement tested: conj:pseudorandom-taylor at width k = 1.  On the monomial algebra A~ of an m x N board (basis
// the sets of cells in distinct columns, every square zero, two cells of one column multiply to 0) over F_3, take
// tops tau_b = L_{b,0}^2 L_{b,1} (h = 3) of random dense linear forms.  Below the fill point the conjecture predicts
// that the top syzygies of multiplier degree e = s - 3 are spanned by the Frobenius syzygies L_{b,0} x e_b
// (x in A~_{e-1}) and L_{b,1}^2 x e_b (x in A~_{e-2}) and the Koszul pairs tau_c x e_b - tau_b x e_c
// (x in A~_{e-3}).  The kernel prints, per family, dim Syz = M |A~_e| - rank(multiplication map) and the rank of
// those generators; defect = difference.  Negative control ("control"): two blocks whose forms each differ by one
// cell of column 0, so their tops agree outside that column and have the syzygies v(e_1 - e_2), v a cell of
// column 0 (thm:taylor-propagation), a positive defect unless they fall in the Taylor span.
// Also printed: the least support of a combination, with coefficients not both zero, of at most two of the
// family's linear forms (the weight condition at t = 2).
//
// Ranks: fflas-ffpack FFPACK::Rank over Givaro::Modular<float>; cases whose matrices are small are recomputed with
// FLINT nmod_mat_rank as a second library.  Every generator of the Taylor span is checked to be a syzygy on a
// random sample.  Usage: pseudorandom_taylor_check OUT "m N s M kind seed; ..." with kind random or control.
#include <fflas-ffpack/ffpack/ffpack.h>
#include <givaro/modular.h>
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <random>
#include <chrono>
#include <cassert>

typedef std::vector<std::pair<int, int>> Poly;  // (monomial code, coefficient in 1..2)

struct Board {
    int m, N, base;
    std::vector<int> mask, deg, index;           // per code
    std::vector<std::vector<int>> byDeg;         // codes of each degree
    Board(int m_, int N_) : m(m_), N(N_), base(m_ + 1) {
        int total = 1;
        for (int c = 0; c < N; c++) total *= base;
        mask.assign(total, 0); deg.assign(total, 0); index.assign(total, -1); byDeg.assign(N + 1, {});
        for (int code = 0; code < total; code++) {
            int x = code, mk = 0, d = 0;
            for (int c = 0; c < N; c++) { if (x % base) { mk |= 1 << c; d++; } x /= base; }
            mask[code] = mk; deg[code] = d; index[code] = (int)byDeg[d].size(); byDeg[d].push_back(code);
        }
    }
    int cell(int row, int col) const { int p = 1; for (int c = 0; c < col; c++) p *= base; return (row + 1) * p; }
};

static Poly mul(const Board& B, const Poly& a, const Poly& b) {
    std::vector<int> acc;
    std::vector<int> touched;
    static std::vector<int> buf;
    if (buf.size() < B.mask.size()) buf.assign(B.mask.size(), 0);
    for (auto& [ca, xa] : a)
        for (auto& [cb, xb] : b)
            if (!(B.mask[ca] & B.mask[cb])) {
                int c = ca + cb;
                if (buf[c] == 0) touched.push_back(c);
                buf[c] = (buf[c] + xa * xb) % 3;
                if (buf[c] == 0) buf[c] = 3;  // mark touched even when it cancels
            }
    Poly out;
    for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}

static long rankFflas(std::vector<float>& A, long r, long c) {
    if (r == 0 || c == 0) return 0;
    Givaro::Modular<float> F(3.0f);
    return (long)FFPACK::Rank(F, r, c, A.data(), c);
}

static long rankFlint(const std::vector<float>& A, long r, long c) {
    nmod_mat_t M; nmod_mat_init(M, r, c, 3);
    for (long i = 0; i < r; i++) for (long j = 0; j < c; j++) nmod_mat_entry(M, i, j) = (mp_limb_t)A[i * c + j];
    long rk = nmod_mat_rank(M); nmod_mat_clear(M); return rk;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s OUT CASES\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w");
    std::stringstream all(argv[2]);
    std::string item;
    while (std::getline(all, item, ';')) {
        std::stringstream ss(item);
        int m, N, s, M; std::string kind; unsigned seed;
        if (!(ss >> m >> N >> s >> M >> kind >> seed)) continue;
        auto t0 = std::chrono::steady_clock::now();
        Board B(m, N);
        int e = s - 3;
        assert(e >= 0 && s <= N);
        std::mt19937 rng(seed);
        std::vector<Poly> L0(M), L1(M), tau(M);
        for (int b = 0; b < M; b++)
            for (int which = 0; which < 2; which++) {
                Poly& L = which ? L1[b] : L0[b];
                for (int col = 0; col < N; col++) for (int row = 0; row < m; row++) {
                    int v = rng() % 3; if (v) L.push_back({B.cell(row, col), v});
                }
            }
        if (kind == "control") {  // block 1 = block 0 with one cell of column 0 added to L_0 and another to L_1,
            assert(M >= 2);  // so the two tops agree outside column 0 and share no form (one row: the same cell)
            L1[1] = L1[0]; L0[1] = L0[0];
            for (int w = 0; w < 2; w++) {
                Poly& L = w ? L1[1] : L0[1];
                int cc = B.cell(w % m, 0); bool found = false;
                for (auto& [c, v] : L) if (c == cc) { v = (v + 1) % 3; found = true; }
                if (!found) L.push_back({cc, 1});
                Poly clean; for (auto& t : L) if (t.second) clean.push_back(t); L = clean;
            }
        }
        // weight: least support of a*L_i + c*L_j over the family's forms, (a, c) not both zero
        std::vector<std::vector<int>> vecs;
        for (int b = 0; b < M; b++) for (int w = 0; w < 2; w++) {
            std::vector<int> v(m * N, 0);
            for (auto& [c, x] : (w ? L1[b] : L0[b])) {
                int col = __builtin_ctz(B.mask[c]); int p = 1; for (int q = 0; q < col; q++) p *= B.base;
                v[(c / p - 1) * N + col] = x;
            }
            vecs.push_back(v);
        }
        int minw = m * N;
        for (size_t i = 0; i < vecs.size(); i++) for (size_t j = i; j < vecs.size(); j++)
            for (int a = 0; a < 3; a++) for (int c = 0; c < 3; c++) {
                if (i == j && c) continue;
                if (!a && !c) continue;
                int w = 0; for (int q = 0; q < m * N; q++) w += ((a * vecs[i][q] + c * vecs[j][q]) % 3) != 0;
                if (w < minw) minw = w;
            }
        for (int b = 0; b < M; b++) tau[b] = mul(B, mul(B, L0[b], L0[b]), L1[b]);
        const auto& Re = B.byDeg[e];
        const auto& Rs = B.byDeg[s];
        long ne = Re.size(), ns = Rs.size(), cols = (long)M * ne;
        // multiplication map: rows = A~_s, columns = (b, r)
        std::vector<float> A((size_t)ns * cols, 0.0f);
        for (int b = 0; b < M; b++)
            for (long ri = 0; ri < ne; ri++) {
                int r = Re[ri];
                for (auto& [t, x] : tau[b]) if (!(B.mask[r] & B.mask[t])) {
                    float& a = A[(size_t)B.index[r + t] * cols + (long)b * ne + ri];
                    a = (float)(((int)a + x) % 3);
                }
            }
        // Taylor generators as rows over the columns (b, r)
        std::vector<std::vector<std::pair<long, int>>> gens;
        auto addSlot = [&](std::vector<std::pair<long, int>>& g, int b, const Poly& p, int sign) {
            for (auto& [c, x] : p) { assert(B.deg[c] == e); g.push_back({(long)b * ne + B.index[c], (x * sign % 3 + 3) % 3}); }
        };
        std::vector<Poly> L1sqs(M);
        for (int b = 0; b < M; b++) L1sqs[b] = mul(B, L1[b], L1[b]);
        for (int b = 0; b < M; b++) {
            if (e >= 1) for (int x : B.byDeg[e - 1]) { std::vector<std::pair<long, int>> g; addSlot(g, b, mul(B, L0[b], {{x, 1}}), 1); gens.push_back(g); }
            if (e >= 2) for (int x : B.byDeg[e - 2]) { std::vector<std::pair<long, int>> g; addSlot(g, b, mul(B, L1sqs[b], {{x, 1}}), 1); gens.push_back(g); }
        }
        if (e >= 3)
            for (int b = 0; b < M; b++) for (int c = b + 1; c < M; c++)
                for (int x : B.byDeg[e - 3]) {
                    std::vector<std::pair<long, int>> g;
                    addSlot(g, b, mul(B, tau[c], {{x, 1}}), 1);
                    addSlot(g, c, mul(B, tau[b], {{x, 1}}), -1);
                    gens.push_back(g);
                }
        // check a random sample of generators against the map
        std::uniform_int_distribution<size_t> pick(0, gens.empty() ? 0 : gens.size() - 1);
        for (int trial = 0; trial < 40 && !gens.empty(); trial++) {
            const auto& g = gens[pick(rng)];
            std::vector<int> img(ns, 0);
            for (auto& [col, x] : g) for (long row = 0; row < ns; row++) {
                float a = A[(size_t)row * cols + col]; if (a != 0.0f) img[row] = (img[row] + x * (int)a) % 3;
            }
            for (long row = 0; row < ns; row++) if (img[row]) { fprintf(stderr, "generator is not a syzygy\n"); return 1; }
        }
        long ng = gens.size();
        std::vector<float> G((size_t)ng * cols, 0.0f);
        for (long i = 0; i < ng; i++) for (auto& [col, x] : gens[i]) {
            float& a = G[(size_t)i * cols + col]; a = (float)(((int)a + x) % 3);
        }
        bool small = (double)ns * cols < 4e6 && (double)ng * cols < 4e6;
        long rkAflint = small ? rankFlint(A, ns, cols) : -1, rkGflint = small ? rankFlint(G, ng, cols) : -1;
        long rkA = rankFflas(A, ns, cols), rkG = rankFflas(G, ng, cols);
        if (small && (rkA != rkAflint || rkG != rkGflint)) { fprintf(stderr, "fflas and FLINT ranks differ\n"); return 1; }
        long syz = cols - rkA;
        double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        fprintf(out, "{\"m\": %d, \"N\": %d, \"s\": %d, \"M\": %d, \"kind\": \"%s\", \"seed\": %u, \"dim_Ae\": %ld, "
                     "\"dim_As\": %ld, \"fill_ratio\": %.4f, \"min_weight_t2\": %d, \"rank_map\": %ld, \"dim_syz\": %ld, "
                     "\"rank_taylor\": %ld, \"defect\": %ld, \"flint_checked\": %s, \"seconds\": %.2f}\n",
                m, N, s, M, kind.c_str(), seed, ne, ns, (double)cols / ns, minw, rkA, syz, rkG, syz - rkG,
                small ? "true" : "false", secs);
        fflush(out);
        printf("m=%d N=%d s=%d M=%d %s: syz=%ld taylor=%ld defect=%ld minw=%d (%.1fs)\n", m, N, s, M, kind.c_str(), syz, rkG,
               syz - rkG, minw, secs);
        fflush(stdout);
    }
    fclose(out);
    return 0;
}
