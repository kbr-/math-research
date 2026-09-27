// Aligned extension of the defect-1 pair (entry-2026-09-27-aligned-extension).
//
// Statement tested.  The pair tau = A^2 B, sigma = C^2 E of ex:pseudorandom-taylor-check (one row, 16 cells, seed 23;
// E is the record's fourth form D) has Taylor defect 1 at multiplier degree 4 and none below, and its obstruction
// image is the single piece e_A (x) w (entry-2026-09-27-split-obstructions).  Add cells 16, 17, ... one at a time,
// with A zero on every added cell (aligned) or random there (control), and B, C, E random there.  Since the lower
// degrees stay clean, prop:lift-obstruction makes the defect after each added cell the dimension of the classes of
// the previous board whose obstruction lies in the ideal, and lem:class-survival embeds the classes of every later
// board into the base's one class.  So the program tracks one representative syzygy z: at each new cell v it tests
// whether ob_v(z) = z_tau d_v tau' + z_sigma d_v sigma' lies in I_6 = tau S_3 + sigma S_3 of the current board; if so
// it lifts z to z + y_v w (tau w_tau + sigma w_sigma = -ob_v(z)), checks that the lift is a syzygy of the extended
// tops, and continues; if not, the defect is 0 from that cell on.
// Exact linear algebra with FLINT nmod_mat.  Usage: aligned_extension_check OUT K seed2 [control], K cells added.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>

typedef std::vector<std::pair<int, int>> Poly;  // (cell mask, coefficient in 1..2)
static int NMAX;
static std::vector<int> idxOf;
static std::vector<std::vector<int>> byDeg;  // masks of each degree within the first n cells, rebuilt per board

static Poly mul(const Poly& a, const Poly& b) {
    static std::vector<int> buf; if (buf.size() < (size_t)(1 << NMAX)) buf.assign(1 << NMAX, 0);
    std::vector<int> touched;
    for (auto& [ca, xa] : a) for (auto& [cb, xb] : b) if (!(ca & cb)) {
        int c = ca | cb; if (!buf[c]) touched.push_back(c);
        buf[c] = (buf[c] + xa * xb) % 3; if (!buf[c]) buf[c] = 3;
    }
    Poly out; for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}
static Poly add(const Poly& a, const Poly& b, int sb) {
    static std::vector<int> buf; if (buf.size() < (size_t)(1 << NMAX)) buf.assign(1 << NMAX, 0);
    std::vector<int> touched;
    for (auto& [c, x] : a) { if (!buf[c]) touched.push_back(c); buf[c] = (buf[c] + x) % 3; if (!buf[c]) buf[c] = 3; }
    for (auto& [c, x] : b) { if (!buf[c]) touched.push_back(c); buf[c] = (buf[c] + sb * x) % 3; if (!buf[c]) buf[c] = 3; }
    Poly out; for (int c : touched) { int v = buf[c] % 3; if (v) out.push_back({c, v}); buf[c] = 0; }
    return out;
}
static Poly restrictTo(const Poly& p, int n) { Poly o; for (auto& t : p) if (!(t.first >> n)) o.push_back(t); return o; }
static Poly form(const std::vector<int>& cf, int n) { Poly p; for (int i = 0; i < n; i++) if (cf[i]) p.push_back({1 << i, cf[i]}); return p; }
static void buildDeg(int n) {
    byDeg.assign(n + 1, {}); idxOf.assign(1 << n, -1);
    for (int c = 0; c < (1 << n); c++) { int d = __builtin_popcount(c); idxOf[c] = byDeg[d].size(); byDeg[d].push_back(c); }
}

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s OUT K seed2 [control]\n", argv[0]); return 2; }
    FILE* out = fopen(argv[1], "w"); int K = atoi(argv[2]); unsigned seed2 = atoi(argv[3]); bool control = argc > 4 && !strcmp(argv[4], "control");
    const int N0 = 16, e = 4; NMAX = N0 + K;
    if (NMAX > 23) { fprintf(stderr, "at most 7 added cells\n"); return 2; }
    std::vector<std::vector<int>> cf(4, std::vector<int>(NMAX, 0));  // A, B, C, E
    std::mt19937 rng(23);
    for (int b = 0; b < 2; b++) for (int w = 0; w < 2; w++) for (int col = 0; col < N0; col++) cf[2 * b + w][col] = rng() % 3;
    std::mt19937 rng2(seed2);
    for (int col = N0; col < NMAX; col++) for (int f = 0; f < 4; f++) { int v = rng2() % 3; cf[f][col] = (f == 0 && !control) ? 0 : v; }
    // base board: syzygies at multiplier degree e, Taylor span, class representative
    int n = N0; buildDeg(n);
    auto tops = [&](int nn, Poly& tau, Poly& sig) {
        Poly A = form(cf[0], nn), B = form(cf[1], nn), C = form(cf[2], nn), E = form(cf[3], nn);
        tau = mul(mul(A, A), B); sig = mul(mul(C, C), E);
    };
    Poly tau, sig; tops(n, tau, sig);
    long ne = byDeg[e].size(), ns = byDeg[e + 3].size(), cols = 2 * ne;
    nmod_mat_t Mm; nmod_mat_init(Mm, ns, cols, 3);
    for (int s = 0; s < 2; s++) for (long r = 0; r < ne; r++) for (auto& [c, x] : (s ? sig : tau)) {
        int m = byDeg[e][r]; if (m & c) continue; long row = idxOf[m | c];
        nmod_mat_entry(Mm, row, s * ne + r) = (nmod_mat_entry(Mm, row, s * ne + r) + x) % 3; }
    nmod_mat_t Kn; nmod_mat_init(Kn, cols, cols, 3); long dimSyz = nmod_mat_nullspace(Kn, Mm); nmod_mat_clear(Mm);
    // Taylor generators
    Poly A0 = form(cf[0], n), B0 = form(cf[1], n), C0 = form(cf[2], n), E0 = form(cf[3], n);
    Poly B2 = mul(B0, B0), E2 = mul(E0, E0);
    std::vector<std::vector<long>> T;
    auto push = [&](int slot, const Poly& p, int slot2, const Poly& p2) { std::vector<long> v(cols, 0);
        for (auto& [c, x] : p) v[slot * ne + idxOf[c]] = (v[slot * ne + idxOf[c]] + x) % 3;
        if (slot2 >= 0) for (auto& [c, x] : p2) v[slot2 * ne + idxOf[c]] = (v[slot2 * ne + idxOf[c]] + 3 - x) % 3;
        T.push_back(v); };
    for (int x : byDeg[e - 1]) { push(0, mul(A0, {{x, 1}}), -1, {}); push(1, mul(C0, {{x, 1}}), -1, {}); }
    for (int x : byDeg[e - 2]) { push(0, mul(B2, {{x, 1}}), -1, {}); push(1, mul(E2, {{x, 1}}), -1, {}); }
    for (int x : byDeg[e - 3]) push(0, mul(sig, {{x, 1}}), 1, mul(tau, {{x, 1}}));
    nmod_mat_t TM; nmod_mat_init(TM, T.size(), cols, 3);
    for (size_t i = 0; i < T.size(); i++) for (long j = 0; j < cols; j++) nmod_mat_entry(TM, i, j) = T[i][j];
    long rkT = nmod_mat_rref(TM);
    std::vector<long> piv(rkT); for (long i = 0; i < rkT; i++) { long j = 0; while (!nmod_mat_entry(TM, i, j)) j++; piv[i] = j; }
    // representative: a syzygy whose residual modulo the reduced Taylor basis is nonzero (the residual is itself a
    // syzygy, since Taylor elements are syzygies)
    std::vector<long> z; long defect = dimSyz - rkT;
    for (long j = 0; j < dimSyz && z.empty(); j++) {
        std::vector<long> y(cols); for (long c = 0; c < cols; c++) y[c] = nmod_mat_entry(Kn, c, j);
        for (long i = 0; i < rkT; i++) { long a = y[piv[i]]; if (a) for (long c = 0; c < cols; c++) y[c] = (y[c] + 3 * 3 - a * nmod_mat_entry(TM, i, c)) % 3; }
        bool nz = false; for (long c = 0; c < cols; c++) nz |= y[c] != 0;
        if (nz) z = y;
    }
    nmod_mat_clear(Kn); nmod_mat_clear(TM);
    fprintf(out, "{\"control\": %s, \"seed2\": %u, \"base\": {\"N\": %d, \"dim_syz\": %ld, \"rank_taylor\": %ld, \"defect\": %ld}, \"steps\": [",
            control ? "true" : "false", seed2, n, dimSyz, rkT, defect); fflush(out);
    printf("base N=%d: defect %ld\n", n, defect); fflush(stdout);
    if (defect != 1 || z.empty()) { fprintf(out, "]}\n"); return 3; }
    Poly zt, zs; for (long r = 0; r < ne; r++) { if (z[r]) zt.push_back({byDeg[e][r], (int)z[r]}); if (z[ne + r]) zs.push_back({byDeg[e][r], (int)z[ne + r]}); }
    // diagnostics: does the representative kill the squared forms exactly?
    fprintf(out, "{\"z_tau_terms\": %zu, \"z_sigma_terms\": %zu, \"z_tau_A2_zero\": %s, \"z_sigma_C2_zero\": %s, \"z_sigma_CE_zero\": %s}%s",
            zt.size(), zs.size(), mul(zt, mul(A0, A0)).empty() ? "true" : "false", mul(zs, mul(C0, C0)).empty() ? "true" : "false",
            mul(zs, mul(C0, E0)).empty() ? "true" : "false", K ? ", " : "");
    bool alive = true;
    for (int k = 0; k < K && alive; k++) {
        int v = N0 + k;  // new cell; current board has cells 0..v-1
        Poly A = form(cf[0], v), B = form(cf[1], v), C = form(cf[2], v), E = form(cf[3], v);
        Poly AB = mul(A, B), AA = mul(A, A), CE = mul(C, E), CC = mul(C, C);
        auto sc = [](const Poly& p, int s) { Poly o; for (auto& [c, x] : p) if ((x * s) % 3) o.push_back({c, (x * s) % 3}); return o; };
        Poly dtau = add(sc(AB, 2 * cf[0][v]), sc(AA, cf[1][v]), 1), dsig = add(sc(CE, 2 * cf[2][v]), sc(CC, cf[3][v]), 1);
        Poly ob = add(mul(zt, dtau), mul(zs, dsig), 1);
        // solve tau w_tau + sigma w_sig = -ob in S_6 of the current board (cells 0..v-1)
        buildDeg(v);
        Poly tauv, sigv; tops(v, tauv, sigv);
        long n3 = byDeg[3].size(), n6 = byDeg[6].size();
        nmod_mat_t G, X, Bv; nmod_mat_init(G, n6, 2 * n3, 3); nmod_mat_init(X, 2 * n3, 1, 3); nmod_mat_init(Bv, n6, 1, 3);
        for (int s = 0; s < 2; s++) for (long r = 0; r < n3; r++) for (auto& [c, x] : (s ? sigv : tauv)) {
            int m = byDeg[3][r]; if (m & c) continue; long row = idxOf[m | c];
            nmod_mat_entry(G, row, s * n3 + r) = (nmod_mat_entry(G, row, s * n3 + r) + x) % 3; }
        for (auto& [c, x] : ob) nmod_mat_entry(Bv, idxOf[c], 0) = (3 - x) % 3;
        int ok = nmod_mat_can_solve(X, G, Bv);
        long obTerms = ob.size();
        fprintf(out, "%s{\"cell\": %d, \"coef_A\": %d, \"ob_terms\": %ld, \"ob_in_ideal\": %s", k ? ", " : "", v, cf[0][v], obTerms, ok ? "true" : "false");
        if (ok) {
            Poly wt, ws; for (long r = 0; r < n3; r++) { long a = nmod_mat_entry(X, r, 0), b = nmod_mat_entry(X, n3 + r, 0);
                if (a) wt.push_back({byDeg[3][r] | (1 << v), (int)a}); if (b) ws.push_back({byDeg[3][r] | (1 << v), (int)b}); }
            zt = add(zt, wt, 1); zs = add(zs, ws, 1);
            // check: z is a syzygy of the tops on cells 0..v
            Poly t2, s2; tops(v + 1, t2, s2);
            Poly chk = add(mul(zt, t2), mul(zs, s2), 1);
            fprintf(out, ", \"lift_is_syzygy\": %s}", chk.empty() ? "true" : "false");
            printf("cell %d: coefficient of A %d, obstruction in ideal, lift %s\n", v, cf[0][v], chk.empty() ? "verified" : "FAILED");
            if (!chk.empty()) alive = false;
        } else {
            fprintf(out, "}"); alive = false;
            printf("cell %d: coefficient of A %d, obstruction outside the ideal: the class dies\n", v, cf[0][v]);
        }
        fflush(out); fflush(stdout);
        nmod_mat_clear(G); nmod_mat_clear(X); nmod_mat_clear(Bv);
    }
    fprintf(out, "], \"survives_all\": %s}\n", alive ? "true" : "false");
    fclose(out); return 0;
}
