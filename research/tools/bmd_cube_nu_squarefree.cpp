// Squarefreeness of the non-collision part of Hermite-Pade determinants Delta_nu along a line.
//
// Statement tested (conj:cube-degree-vector-squarefree, bmd-r108).  For a degree vector
// nu = (nu_r)_{r in {0,1}^n} (nu_r >= -1), V_nu = sum_r w^r F[T]_{<= nu_r} with
// w_i = (1 + a_i T)^{1/2}, and Delta_nu(a) is the N x N determinant of the coefficients of
// T^0..T^{N-1} in the rows T^j w^r (N = sum (nu_r + 1)).  The collision forms are a_i and a_i - a_j.
// Along the affine line a = u + t v over F_p the kernel computes Delta_nu|_L with FLINT
// (nmod_poly_mat_det), checks that its degree equals the homogeneous degree sum_{c<N} c - sum j,
// removes each collision root with its full multiplicity, and reports the multiplicities, the
// remaining degree, gcd(R, R') and the factor degrees of the remainder R.  If deg is full and
// gcd(R, R') = 1, the part of Delta_nu prime to the collision forms is squarefree over Q (as in
// the certificate of check:cube-boundary-squarefree), provided the collision multiplicities
// mod p equal those over Q.
//
// Usage: bmd_cube_nu_squarefree p n u_1..u_n v_1..v_n NU1/NU2/...   (or @FILE holding that list)
//   each NU is a comma-separated list of 2^n integers, indexed by r = sum r_i 2^i.
// Output: one line per degree vector, flushed.
#include <flint/flint.h>
#include <flint/nmod_poly.h>
#include <flint/nmod_poly_mat.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <utility>

typedef unsigned long ul;

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: p n u.. v.. NU/NU/...\n"); return 2; }
    ul p = std::strtoul(argv[1], 0, 10);
    int n = std::atoi(argv[2]);
    if (argc != 4 + 2 * n) { std::fprintf(stderr, "bad arguments\n"); return 2; }
    nmod_t mod; nmod_init(&mod, p);
    std::vector<ul> u(n), v(n);
    for (int i = 0; i < n; ++i) { u[i] = std::strtoul(argv[3 + i], 0, 10) % p; v[i] = std::strtoul(argv[3 + n + i], 0, 10) % p; }
    std::vector<ul> roots; std::vector<std::pair<int, int>> names;
    for (int i = 0; i < n; ++i) { roots.push_back(nmod_mul(nmod_neg(u[i], mod), n_invmod(v[i], p), mod)); names.push_back({i, -1}); }
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
        ul den = nmod_sub(v[i], v[j], mod);
        if (!den) { std::fprintf(stderr, "v_i = v_j\n"); return 2; }
        roots.push_back(nmod_mul(nmod_sub(u[j], u[i], mod), n_invmod(den, p), mod)); names.push_back({i, j});
    }
    for (size_t a = 0; a < roots.size(); ++a) for (size_t b = a + 1; b < roots.size(); ++b)
        if (roots[a] == roots[b]) { std::fprintf(stderr, "collision roots not distinct\n"); return 2; }
    std::string all(argv[3 + 2 * n]);
    if (!all.empty() && all[0] == '@') {  // read the degree vectors from a file
        FILE* fh = std::fopen(all.c_str() + 1, "r");
        if (!fh) { std::fprintf(stderr, "cannot read %s\n", all.c_str() + 1); return 2; }
        all.clear(); int ch;
        while ((ch = std::fgetc(fh)) != EOF) if (ch != '\n' && ch != ' ') all.push_back((char)ch);
        std::fclose(fh);
    }
    size_t pos = 0;
    while (pos <= all.size()) {
        size_t nx = all.find('/', pos); if (nx == std::string::npos) nx = all.size();
        std::string spec = all.substr(pos, nx - pos); pos = nx + 1;
        std::vector<int> nu; size_t q = 0;
        while (q <= spec.size()) { size_t c = spec.find(',', q); if (c == std::string::npos) c = spec.size(); nu.push_back(std::atoi(spec.substr(q, c - q).c_str())); q = c + 1; }
        if ((int)nu.size() != (1 << n)) { std::fprintf(stderr, "bad degree vector %s\n", spec.c_str()); return 2; }
        std::vector<std::pair<int, unsigned>> basis;
        for (unsigned r = 0; r < (1u << n); ++r) for (int j = 0; j <= nu[r]; ++j) basis.push_back({j, r});
        int N = (int)basis.size();
        if (N == 0) continue;
        long sumj = 0; for (auto& b : basis) sumj += b.first;
        long expdeg = (long)N * (N - 1) / 2 - sumj;
        // binom(1/2, k) mod p
        std::vector<ul> bc(N); bc[0] = 1;
        ul half = n_invmod(2, p);
        for (int k = 1; k < N; ++k) {
            ul num = nmod_sub(half, (ul)(k - 1) % p, mod);
            bc[k] = nmod_mul(nmod_mul(bc[k - 1], num, mod), n_invmod((ul)k, p), mod);
        }
        // w_i series with polynomial-in-t coefficients: bc[k] (u_i + t v_i)^k
        std::vector<std::vector<nmod_poly_struct>> w(n, std::vector<nmod_poly_struct>(N));
        for (int i = 0; i < n; ++i) {
            nmod_poly_t y, yp; nmod_poly_init(y, p); nmod_poly_init(yp, p);
            nmod_poly_set_coeff_ui(y, 0, u[i]); nmod_poly_set_coeff_ui(y, 1, v[i]); nmod_poly_one(yp);
            for (int k = 0; k < N; ++k) {
                nmod_poly_init(&w[i][k], p);
                nmod_poly_scalar_mul_nmod(&w[i][k], yp, bc[k]);
                nmod_poly_mul(yp, yp, y);
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
                    for (int c = 0; a + c < N; ++c) { nmod_poly_mul(tmp, &s[a], &w[i][c]); nmod_poly_add(&o[a + c], &o[a + c], tmp); }
                for (int a = 0; a < N; ++a) { nmod_poly_swap(&s[a], &o[a]); nmod_poly_clear(&o[a]); }
            }
            for (int a = 0; a < N; ++a) { nmod_poly_set(nmod_poly_mat_entry(A, b, a), &s[a]); nmod_poly_clear(&s[a]); }
        }
        nmod_poly_t D, R, lin, qq, rr, Rd, G;
        nmod_poly_init(D, p); nmod_poly_init(R, p); nmod_poly_init(lin, p); nmod_poly_init(qq, p); nmod_poly_init(rr, p);
        nmod_poly_init(Rd, p); nmod_poly_init(G, p);
        nmod_poly_mat_det(D, A);
        long degD = nmod_poly_degree(D);
        std::printf("n=%d nu=%s N=%d: deg %ld (homogeneous %ld)", n, spec.c_str(), N, degD, expdeg);
        nmod_poly_set(R, D);
        for (size_t a = 0; a < roots.size(); ++a) {
            nmod_poly_zero(lin); nmod_poly_set_coeff_ui(lin, 1, 1); nmod_poly_set_coeff_ui(lin, 0, nmod_neg(roots[a], mod));
            int k = 0;
            while (!nmod_poly_is_zero(R)) { nmod_poly_divrem(qq, rr, R, lin); if (!nmod_poly_is_zero(rr)) break; nmod_poly_swap(R, qq); ++k; }
            if (names[a].second < 0) std::printf(" a%d:%d", names[a].first + 1, k);
            else std::printf(" a%d-a%d:%d", names[a].first + 1, names[a].second + 1, k);
        }
        long degR = nmod_poly_degree(R), degG = 0;
        if (degR > 0) { nmod_poly_derivative(Rd, R); nmod_poly_gcd(G, R, Rd); degG = nmod_poly_degree(G); }
        std::printf(" | rest %ld, deg gcd(R,R')=%ld, factors:", degR, degG);
        if (degR > 0) {
            nmod_poly_factor_t fac; nmod_poly_factor_init(fac); nmod_poly_factor(fac, R);
            for (long k = 0; k < fac->num; ++k) std::printf(" %ld^%ld", nmod_poly_degree(fac->p + k), (long)fac->exp[k]);
            nmod_poly_factor_clear(fac);
        }
        std::printf(" | %s\n", (degD == expdeg && degG == 0) ? "SQUAREFREE" : (degD != expdeg ? "DEGREE-DROP" : "REPEATED"));
        std::fflush(stdout);
        nmod_poly_clear(D); nmod_poly_clear(R); nmod_poly_clear(lin); nmod_poly_clear(qq); nmod_poly_clear(rr);
        nmod_poly_clear(Rd); nmod_poly_clear(G); nmod_poly_clear(tmp); nmod_poly_mat_clear(A);
        for (int i = 0; i < n; ++i) for (int k = 0; k < N; ++k) nmod_poly_clear(&w[i][k]);
    }
    return 0;
}
