// Squarefreeness certificate for the non-collision part of Delta_{n,d} along a line (bmd-r104).
//
// Statement certified (prop:cube-extra-factors-double, thm:cube-boundary-collision-exponents).
// Over Q, Delta_{n,d} = c' prod_D l_D^{E_n(d)} Delta^nc, the product over the C(n+1,2) collision
// forms y_i and y_i - y_j.  Restrict to the affine line y = u + t v over F_p.  If
//   (a) deg_t Delta|_L equals the homogeneous degree sum_{c<N} c - sum Q (so c' and Delta(v) are
//       nonzero mod p),
//   (b) the collision roots are distinct and each has multiplicity exactly E_n(d), and
//   (c) the quotient R(t) = Delta|_L / prod_D (t - t_D)^{E_n(d)} is squarefree (gcd(R, R') = 1),
// then Delta^nc is squarefree over Q, so g^nc_{n,d} = 1 by the proposition and
// l_0(d+1, N) = deg Delta - C(n+1,2) E_n(d) in characteristic 0.
//
// Delta_{n,d} is the N x N determinant of the coefficients of T^0..T^{N-1} in T^Q z^r
// (2Q + |r| <= d), z_i = sum_{j>=1} (-1)^j C_{j-1} (y_i T)^j.  Entries are polynomials in t; the
// determinant is FLINT's nmod_poly_mat_det, and the gcd and factorization use nmod_poly.
//
// Usage: bmd_cube_delta_squarefree p n dmin dmax u_1..u_n v_1..v_n [MODE]
// MODE boundary (default): as above.
// MODE limit: the collision limit space U_d = span{T^Q z^r : Q + |r| <= d} (thm:cube-boundary-
//   collision-exponents) in place of V_d; reports the multiplicity of each collision root, whether
//   the quotient R by the full collision multiplicities is squarefree, and its factor degrees.
// MODE orders: boundary mode, and in addition, at every root t* in F_p of R, the orders at p_0 of
//   V_d at y = u + t* v (pivot columns of the reduced echelon form of the coefficients of
//   T^0..T^{N+2}); a simple Weierstrass point has orders 0..N-2, N.
// Output: one line per d (and per root in orders mode), flushed as it completes.
#include <flint/nmod_mat.h>
#include <cstring>
#include <flint/flint.h>
#include <flint/nmod_poly.h>
#include <flint/nmod_poly_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <utility>

typedef unsigned long ul;

int main(int argc, char** argv) {
    if (argc < 5) { std::fprintf(stderr, "usage: p n dmin dmax u.. v..\n"); return 2; }
    ul p = std::strtoul(argv[1], 0, 10);
    int n = std::atoi(argv[2]), dmin = std::atoi(argv[3]), dmax = std::atoi(argv[4]);
    if (argc != 5 + 2 * n && argc != 6 + 2 * n) { std::fprintf(stderr, "bad arguments\n"); return 2; }
    const char* mode = argc == 6 + 2 * n ? argv[5 + 2 * n] : "boundary";
    bool limit = !std::strcmp(mode, "limit"), orders = !std::strcmp(mode, "orders");
    if (!limit && !orders && std::strcmp(mode, "boundary")) { std::fprintf(stderr, "bad mode\n"); return 2; }
    nmod_t mod; nmod_init(&mod, p);
    std::vector<ul> u(n), v(n);
    for (int i = 0; i < n; ++i) { u[i] = std::strtoul(argv[5 + i], 0, 10) % p; v[i] = std::strtoul(argv[5 + n + i], 0, 10) % p; }
    // collision roots t_D: y_i = 0 and y_i = y_j on the line
    std::vector<ul> roots; std::vector<std::pair<int, int>> names;
    for (int i = 0; i < n; ++i) {
        roots.push_back(nmod_mul(nmod_neg(u[i], mod), n_invmod(v[i], p), mod)); names.push_back({i, -1});
    }
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
        ul num = nmod_sub(u[j], u[i], mod), den = nmod_sub(v[i], v[j], mod);
        if (!den) { std::fprintf(stderr, "v_i = v_j\n"); return 2; }
        roots.push_back(nmod_mul(num, n_invmod(den, p), mod)); names.push_back({i, j});
    }
    for (size_t a = 0; a < roots.size(); ++a) for (size_t b = a + 1; b < roots.size(); ++b)
        if (roots[a] == roots[b]) { std::fprintf(stderr, "collision roots not distinct\n"); return 2; }
    for (int d = dmin; d <= dmax; ++d) {
        std::vector<std::pair<int, unsigned>> basis;
        for (int Q = 0; Q <= d; ++Q)
            for (unsigned r = 0; r < (1u << n); ++r)
                if ((limit ? Q : 2 * Q) + __builtin_popcount(r) <= d) basis.push_back({Q, r});
        int N = (int)basis.size();
        long sumQ = 0; for (auto& b : basis) sumQ += b.first;
        long expdeg = (long)N * (N - 1) / 2 - sumQ;
        // E_n(d) = sum over (Q, r') in V_{n-1,d-1} of d - 2Q - |r'|
        long E = 0;
        for (int Q = 0; 2 * Q <= d - 1; ++Q)
            for (unsigned r = 0; r < (1u << (n - 1)); ++r) {
                int e = 2 * Q + __builtin_popcount(r);
                if (e <= d - 1) E += d - e;
            }
        // Catalan numbers mod p
        std::vector<ul> cat(N + 1); cat[0] = 1;
        for (int j = 1; j <= N; ++j) cat[j] = nmod_mul(nmod_mul(cat[j - 1], (2 * (2 * j - 1)) % p, mod), n_invmod(j + 1, p), mod);
        // series z_i: coefficient of T^j is (-1)^j C_{j-1} (u_i + t v_i)^j, a polynomial in t
        std::vector<std::vector<nmod_poly_struct>> z(n, std::vector<nmod_poly_struct>(N));
        for (int i = 0; i < n; ++i) {
            nmod_poly_t y; nmod_poly_init(y, p); nmod_poly_set_coeff_ui(y, 0, u[i]); nmod_poly_set_coeff_ui(y, 1, v[i]);
            nmod_poly_t yp; nmod_poly_init(yp, p); nmod_poly_one(yp);
            nmod_poly_init(&z[i][0], p);
            for (int j = 1; j < N; ++j) {
                nmod_poly_mul(yp, yp, y);
                nmod_poly_init(&z[i][j], p);
                ul c = cat[j - 1]; if (j % 2) c = nmod_neg(c, mod);
                nmod_poly_scalar_mul_nmod(&z[i][j], yp, c);
            }
            nmod_poly_clear(y); nmod_poly_clear(yp);
        }
        nmod_poly_mat_t A; nmod_poly_mat_init(A, N, N, p);
        nmod_poly_t tmp; nmod_poly_init(tmp, p);
        for (int b = 0; b < N; ++b) {
            std::vector<nmod_poly_struct> s(N);
            for (int a = 0; a < N; ++a) nmod_poly_init(&s[a], p);
            nmod_poly_one(&s[basis[b].first]);
            for (int i = 0; i < n; ++i) if (basis[b].second >> i & 1) {
                std::vector<nmod_poly_struct> o(N);
                for (int a = 0; a < N; ++a) nmod_poly_init(&o[a], p);
                for (int a = 0; a < N; ++a) if (!nmod_poly_is_zero(&s[a]))
                    for (int c = 1; a + c < N; ++c) { nmod_poly_mul(tmp, &s[a], &z[i][c]); nmod_poly_add(&o[a + c], &o[a + c], tmp); }
                for (int a = 0; a < N; ++a) { nmod_poly_swap(&s[a], &o[a]); nmod_poly_clear(&o[a]); }
            }
            for (int a = 0; a < N; ++a) { nmod_poly_set(nmod_poly_mat_entry(A, b, a), &s[a]); nmod_poly_clear(&s[a]); }
        }
        nmod_poly_t D; nmod_poly_init(D, p);
        nmod_poly_mat_det(D, A);
        long degD = nmod_poly_degree(D);
        std::printf("n=%d d=%d N=%d E=%ld: deg Delta|L=%ld (homogeneous degree %ld)", n, d, N, E, degD, expdeg);
        bool ok = (degD == expdeg);
        nmod_poly_t R, lin, q, r; nmod_poly_init(R, p); nmod_poly_init(lin, p); nmod_poly_init(q, p); nmod_poly_init(r, p);
        nmod_poly_set(R, D);
        for (size_t a = 0; a < roots.size(); ++a) {
            nmod_poly_zero(lin); nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(roots[a], mod));
            int k = 0;
            while (!nmod_poly_is_zero(R)) {
                nmod_poly_divrem(q, r, R, lin);
                if (!nmod_poly_is_zero(r)) break;
                nmod_poly_swap(R, q); ++k;
            }
            if (names[a].second < 0) std::printf(" y%d:%d", names[a].first + 1, k);
            else std::printf(" y%d-y%d:%d", names[a].first + 1, names[a].second + 1, k);
            if (!limit && k != E) ok = false;
        }
        nmod_poly_t Rd, G; nmod_poly_init(Rd, p); nmod_poly_init(G, p);
        nmod_poly_derivative(Rd, R); nmod_poly_gcd(G, R, Rd);
        long degR = nmod_poly_degree(R), degG = nmod_poly_degree(G);
        if (degG != 0) ok = false;
        nmod_poly_factor_t fac; nmod_poly_factor_init(fac);
        nmod_poly_factor(fac, R);
        std::printf(" | rest degree %ld, deg gcd(R,R')=%ld, factor degrees:", degR, degG);
        for (long k = 0; k < fac->num; ++k) std::printf(" %ld^%ld", nmod_poly_degree(fac->p + k), (long)fac->exp[k]);
        std::printf(" | %s %s\n", limit ? "limit squarefree" : "certificate", ok ? "PASSED" : "FAILED");
        std::fflush(stdout);
        if (orders) for (long k = 0; k < fac->num; ++k) if (nmod_poly_degree(fac->p + k) == 1) {
            ul ts = nmod_neg(nmod_mul(nmod_poly_get_coeff_ui(fac->p + k, 0), n_invmod(nmod_poly_get_coeff_ui(fac->p + k, 1), p), mod), mod);
            int M = N + 3;
            std::vector<std::vector<ul>> zz(n, std::vector<ul>(M, 0));
            for (int i = 0; i < n; ++i) {
                ul y = nmod_add(u[i], nmod_mul(ts, v[i], mod), mod), yp = 1;
                std::vector<ul> ct(M + 1); ct[0] = 1;
                for (int j = 1; j <= M; ++j) ct[j] = nmod_mul(nmod_mul(ct[j - 1], (2 * (2 * j - 1)) % p, mod), n_invmod(j + 1, p), mod);
                for (int j = 1; j < M; ++j) { yp = nmod_mul(yp, y, mod); ul c = nmod_mul(ct[j - 1], yp, mod); zz[i][j] = (j % 2) ? nmod_neg(c, mod) : c; }
            }
            nmod_mat_t B; nmod_mat_init(B, N, M, p);
            for (int b = 0; b < N; ++b) {
                std::vector<ul> s(M, 0); s[basis[b].first] = 1;
                for (int i = 0; i < n; ++i) if (basis[b].second >> i & 1) {
                    std::vector<ul> o(M, 0);
                    for (int a = 0; a < M; ++a) if (s[a]) for (int c = 1; a + c < M; ++c) o[a + c] = nmod_add(o[a + c], nmod_mul(s[a], zz[i][c], mod), mod);
                    s = o;
                }
                for (int a = 0; a < M; ++a) nmod_mat_entry(B, b, a) = s[a];
            }
            long rk = nmod_mat_rref(B);
            std::printf("  root t*=%lu: rank %ld of %d, orders beyond 0..N-2:", ts, rk, N);
            for (long i = 0; i < rk; ++i) { int c = 0; while (c < M && nmod_mat_entry(B, i, c) == 0) ++c; if (c >= N - 1) std::printf(" %d", c); }
            std::printf(" (N=%d)\n", N); std::fflush(stdout);
            nmod_mat_clear(B);
        }
        nmod_poly_factor_clear(fac);
        nmod_poly_clear(Rd); nmod_poly_clear(G); nmod_poly_clear(R); nmod_poly_clear(lin); nmod_poly_clear(q); nmod_poly_clear(r);
        nmod_poly_clear(D); nmod_poly_clear(tmp); nmod_poly_mat_clear(A);
        for (int i = 0; i < n; ++i) for (int j = 0; j < N; ++j) nmod_poly_clear(&z[i][j]);
    }
    return 0;
}
