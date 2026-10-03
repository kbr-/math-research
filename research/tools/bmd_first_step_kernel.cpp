// The dimension-four first step from the Taylor colon formula, exactly in the weighted symmetric ring
// (cycle bmd-20261009-kau).
//
// Statement tested: for n = 4 and d given, (T_d)_c = { g in B_c : g k in (F, m1) }, where B = F_p[e1..e4],
// deg e_j = j, F = Delta/u, m1 = M_{N-1}/u, k = K/u and u = (e4 V)^(d^2+(d-1)^2) (thm:cube-taylor-collision-factor,
// lem:cube-taylor-colon-formula, thm:cube-first-step-link-duality (a)). The first step l_0(d+1, 8d-3) is the least
// c with (T_d)_c != 0, and it is at most lambda = 10d^2-10d-5 (F itself).
//
// Method. (1) Evaluate the Taylor minors at random points a of F_p^4 (rows T^s w_S, 2s+|S| <= d; columns the Taylor
// coefficients at T = 0 of orders 0..N+1), divide by u(a), and interpolate F, m1, k in the monomial bases of B in
// degrees lambda, lambda+1, lambda+2 (square system on as many points as monomials; checked on 40 further points).
// (2) For each requested c, the map (g, A, G) -> g k - A F - G m1 from B_c + B_{c+2} + B_{c+1} to B_{c+lambda+2};
// its kernel projects injectively to g when c+2 < lambda+1 (F, m1 coprime: g = 0 forces A = m1 h with deg h < 0),
// and contains the one Koszul solution (0, m1, -F) when c+2 = lambda+1; dim (T_d)_c = dim ker minus that.
// Exact linear algebra mod p with FLINT (nmod_mat_rank). Each degree also reports the rank of the (A, G) columns
// alone, which checks coprimality of F and m1 mod p as used.
// Usage: bmd_first_step_kernel d p1[,p2...] seed1[,seed2...] c1 [c2 ...]   (one run per prime, same degrees)
#include <flint/flint.h>
#include <flint/nmod_mat.h>
#include <flint/nmod_vec.h>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <random>
#include <vector>
#include <array>
using namespace std;

typedef array<int, 4> Mono;
static vector<Mono> basis(int D) {
    vector<Mono> out;
    for (int i4 = 0; 4 * i4 <= D; ++i4)
        for (int i3 = 0; 4 * i4 + 3 * i3 <= D; ++i3)
            for (int i2 = 0; 4 * i4 + 3 * i3 + 2 * i2 <= D; ++i2)
                out.push_back({D - 4 * i4 - 3 * i3 - 2 * i2, i2, i3, i4});
    return out;
}

static nmod_t mod;
static mp_limb_t pw(mp_limb_t b, long e) { return n_powmod2(b, e, mod.n); }

static int run(int d, mp_limb_t p, unsigned seed, const vector<int> &cs) {
    nmod_init(&mod, p);
    int lambda = 10 * d * d - 10 * d - 5, beta = d * d + (d - 1) * (d - 1);
    // rows of V_d: (s, S)
    vector<pair<int, int>> rows;
    for (int S = 0; S < 16; ++S) { int sz = __builtin_popcount(S); for (int s = 0; 2 * s + sz <= d; ++s) rows.push_back({s, S}); }
    int N = rows.size(), C = N + 2;
    printf("d=%d N=%d lambda=%d beta=%d p=%lu seed=%u\n", d, N, lambda, beta, (unsigned long)p, seed);
    if (N != 8 * d - 4) { fprintf(stderr, "N != 8d-4\n"); return 1; }
    // binomial(1/2, j) mod p
    vector<mp_limb_t> half(C);
    half[0] = 1; mp_limb_t inv2 = n_invmod(2, p);
    for (int j = 1; j < C; ++j) {
        mp_limb_t num = nmod_sub(inv2, (j - 1) % p, mod);
        half[j] = nmod_mul(nmod_mul(half[j - 1], num, mod), n_invmod(j, p), mod);
    }
    mt19937_64 rng(seed);
    vector<int> degs = {lambda, lambda + 1, lambda + 2};
    vector<vector<Mono>> bases; for (int D : degs) bases.push_back(basis(D));
    int npts = bases[2].size() + 40;
    // values of F, m1, k at points, and the monomial evaluations
    vector<array<mp_limb_t, 4>> evals; vector<array<mp_limb_t, 3>> vals;
    while ((int)evals.size() < npts) {
        array<mp_limb_t, 4> a; for (auto &x : a) x = rng() % p;
        // u(a) = (e4 V)^beta
        mp_limb_t e4 = 1, V = 1;
        for (int i = 0; i < 4; ++i) e4 = nmod_mul(e4, a[i], mod);
        for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j) V = nmod_mul(V, nmod_sub(a[i], a[j], mod), mod);
        mp_limb_t u = pw(nmod_mul(e4, V, mod), beta);
        if (u == 0) continue;
        // Taylor matrix N x C
        nmod_mat_t X; nmod_mat_init(X, N, C, p);
        for (int r = 0; r < N; ++r) {
            vector<mp_limb_t> ser(C, 0); ser[0] = 1;
            for (int i = 0; i < 4; ++i) if (rows[r].second >> i & 1) {
                vector<mp_limb_t> sq(C), out(C, 0);
                for (int j = 0; j < C; ++j) sq[j] = nmod_mul(half[j], pw(a[i], j), mod);
                for (int x = 0; x < C; ++x) if (ser[x]) for (int y = 0; x + y < C; ++y) out[x + y] = nmod_add(out[x + y], nmod_mul(ser[x], sq[y], mod), mod);
                ser = out;
            }
            int s = rows[r].first;
            for (int c = 0; c < C; ++c) nmod_mat_entry(X, r, c) = c >= s ? ser[c - s] : 0;
        }
        auto minor = [&](vector<int> cols) {
            nmod_mat_t M; nmod_mat_init(M, N, N, p);
            for (int r = 0; r < N; ++r) for (int j = 0; j < N; ++j) nmod_mat_entry(M, r, j) = nmod_mat_entry(X, r, cols[j]);
            mp_limb_t v = nmod_mat_det(M); nmod_mat_clear(M); return v;
        };
        vector<int> c0(N); for (int j = 0; j < N; ++j) c0[j] = j;                     // Delta: columns 0..N-1
        vector<int> c1 = c0; c1[N - 1] = N;                                          // M_{N-1}: 0..N-2, N
        vector<int> c2 = c0; c2[N - 1] = N + 1;                                      // K: 0..N-2, N+1
        mp_limb_t ui = n_invmod(u, p);
        vals.push_back({nmod_mul(minor(c0), ui, mod), nmod_mul(minor(c1), ui, mod), nmod_mul(minor(c2), ui, mod)});
        nmod_mat_clear(X);
        // elementary symmetric functions
        array<mp_limb_t, 4> e = {0, 0, 0, 0};
        for (int S = 1; S < 16; ++S) { int sz = __builtin_popcount(S); mp_limb_t prod = 1; for (int i = 0; i < 4; ++i) if (S >> i & 1) prod = nmod_mul(prod, a[i], mod); e[sz - 1] = nmod_add(e[sz - 1], prod, mod); }
        evals.push_back(e);
    }
    // interpolate the three forms
    vector<map<Mono, mp_limb_t>> forms(3);
    for (int f = 0; f < 3; ++f) {
        auto &bs = bases[f]; int n = bs.size();
        nmod_mat_t Vm, rhs, sol; nmod_mat_init(Vm, n, n, p); nmod_mat_init(rhs, n, 1, p); nmod_mat_init(sol, n, 1, p);
        auto monoval = [&](const array<mp_limb_t, 4> &e, const Mono &m) {
            mp_limb_t v = 1; for (int j = 0; j < 4; ++j) v = nmod_mul(v, pw(e[j], m[j]), mod); return v; };
        for (int i = 0; i < n; ++i) { for (int j = 0; j < n; ++j) nmod_mat_entry(Vm, i, j) = monoval(evals[i], bs[j]); nmod_mat_entry(rhs, i, 0) = vals[i][f]; }
        if (!nmod_mat_solve(sol, Vm, rhs)) { fprintf(stderr, "singular interpolation system for form %d\n", f); return 1; }
        int bad = 0;
        for (int i = n; i < npts; ++i) {
            mp_limb_t v = 0; for (int j = 0; j < n; ++j) v = nmod_add(v, nmod_mul(nmod_mat_entry(sol, j, 0), monoval(evals[i], bs[j]), mod), mod);
            if (v != vals[i][f]) ++bad;
        }
        int nz = 0; for (int j = 0; j < n; ++j) if (nmod_mat_entry(sol, j, 0)) { forms[f][bs[j]] = nmod_mat_entry(sol, j, 0); ++nz; }
        printf("form %s: degree %d, %d monomials, %d nonzero, check points failing %d of %d\n", f == 0 ? "F" : f == 1 ? "m1" : "k", degs[f], n, nz, bad, npts - n);
        fflush(stdout);
        if (bad) return 1;
        nmod_mat_clear(Vm); nmod_mat_clear(rhs); nmod_mat_clear(sol);
    }
    // kernel dimensions
    for (int c : cs) {
        vector<Mono> bg = basis(c), bA = basis(c + 2), bG = basis(c + 1), tgt = basis(c + lambda + 2);
        map<Mono, int> idx; for (int i = 0; i < (int)tgt.size(); ++i) idx[tgt[i]] = i;
        int cols = bg.size() + bA.size() + bG.size();
        nmod_mat_t M; nmod_mat_init(M, tgt.size(), cols, p);
        int col = 0;
        auto add = [&](const vector<Mono> &bs, const map<Mono, mp_limb_t> &form, bool neg) {
            for (auto &m : bs) {
                for (auto &[fm, v] : form) {
                    Mono t = {m[0] + fm[0], m[1] + fm[1], m[2] + fm[2], m[3] + fm[3]};
                    mp_limb_t &e = nmod_mat_entry(M, idx.at(t), col);
                    e = neg ? nmod_sub(e, v, mod) : nmod_add(e, v, mod);
                }
                ++col;
            }
        };
        add(bg, forms[2], false); add(bA, forms[0], true); add(bG, forms[1], true);
        // coprimality of F and m1 mod p, as used: the (A, G) columns alone must have rank cols - |g| (less one
        // Koszul vector at c = lambda - 1), so that every kernel vector has g != 0
        nmod_mat_t AG; nmod_mat_window_init(AG, M, 0, bg.size(), tgt.size(), cols);
        nmod_mat_t AGc; nmod_mat_init_set(AGc, AG); nmod_mat_window_clear(AG);
        long agrank = nmod_mat_rank(AGc); nmod_mat_clear(AGc);
        printf("c=%d: (A, G) columns %d, rank %ld\n", c, cols - (int)bg.size(), agrank);
        long rank = nmod_mat_rank(M);
        long kernel = cols - rank, koszul = (c + 2 == lambda + 1) ? 1 : (c + 2 > lambda + 1 ? -1 : 0);
        if (koszul < 0) printf("c=%d: beyond the injectivity range of this count; kernel %ld\n", c, kernel);
        else printf("c=%d: map %zu x %d, rank %ld, kernel %ld, Koszul %ld, dim (T_d)_c = %ld\n", c, tgt.size(), cols, rank, kernel, koszul, kernel - koszul);
        fflush(stdout);
        nmod_mat_clear(M);
    }
    return 0;
}

static vector<unsigned long> list(const char *text) {
    vector<unsigned long> out; char *end;
    for (const char *q = text; *q; q = *end ? end + 1 : end) out.push_back(strtoul(q, &end, 10));
    return out;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s d p1[,p2...] seed1[,seed2...] c1 [c2 ...]\n", argv[0]); return 2; }
    int d = atoi(argv[1]);
    vector<unsigned long> ps = list(argv[2]), seeds = list(argv[3]);
    if (ps.size() != seeds.size()) { fprintf(stderr, "one seed per prime\n"); return 2; }
    vector<int> cs; for (int arg = 4; arg < argc; ++arg) cs.push_back(atoi(argv[arg]));
    for (size_t i = 0; i < ps.size(); ++i) if (int r = run(d, ps[i], seeds[i], cs)) return r;
    return 0;
}
