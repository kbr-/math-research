// Maximal minors of the extended Taylor matrix on a random plane (cycle bmd-20261009-de, 9 October 2026).
//
// Statement tested.  conj:cube-four-first-step-self-link requires deg T_d = lambda(lambda+1)/2 for the first-step curve
// T_d in P^3 of branch coordinates (n = 4): equal Betti numbers of T_d and its link by (F, delta F) give equal degrees,
// and the degrees add to deg (F, delta F) = lambda(lambda+1).  By lem:cube-polar-minor-identity and
// cor:cube-first-step-brill-noether, off collisions V(T_d) is where all N+1 maximal minors of the N x (N+1) matrix
// [b_0..b_N] vanish, and V(F, delta F) = V(Delta, M_{N-1}).  This program writes those minors restricted to the affine
// plane a(x, y) = U0 + x U1 + y U2 (U random mod p, seeded), as bivariate polynomials, together with the collision
// forms a_i and a_i - a_j on the plane, as a Macaulay2 script fragment; bmd_plane_degrees.m2 saturates and counts.
//
// Rows: T^q w_S, S subset of {1..4}, 2q + |S| <= d (N = 8d - 4 of them); w_i = (1 + a_i T)^{1/2}; column c is the
// coefficient of T^c.  Entry (q, S; c) is homogeneous of degree c - q in a.  Minor omitting column c has degree at most
// N(N+1)/2 - c - sum q; the program interpolates on a (D+1) x (D+1) grid with D the largest such degree, and checks
// that every coefficient above total degree D vanishes.  The common collision factor of the minors is divided out
// here (exact synthetic division by each collision form while it divides all of them), so that the Groebner work
// in Macaulay2 runs on low-degree generators.
//
// It also writes extraK = K / (common factor), K = det[b_0..b_{N-2}, b_{N+1}]: by the second polar minor
// identity, Q is a unit times K modulo the polar ideal (cycle bmd-20261009-dh).
// Usage: bmd_plane_minors p d seed OUT.m2
#include <flint/nmod_mat.h>
#include <flint/nmod_poly.h>
#include <cstdio>
#include <cstdlib>
#include <array>
#include <random>
#include <vector>
using namespace std;

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: p d seed OUT.m2\n"); return 2; }
    const mp_limb_t p = strtoull(argv[1], 0, 10);
    const int d = atoi(argv[2]);
    const unsigned seed = atoi(argv[3]);
    nmod_t mod; nmod_init(&mod, p);
    struct Row { int q, S; };
    vector<Row> rows;
    for (int S = 0; S < 16; ++S) {
        int k = __builtin_popcount(S);
        for (int q = 0; 2 * q + k <= d; ++q) rows.push_back({q, S});
    }
    const int N = rows.size(), C = N + 1;
    long sumq = 0; for (auto &r : rows) sumq += r.q;
    const int D = (int)((long)N * (N + 1) / 2 - sumq);   // degree bound of the minor omitting column 0
    printf("d=%d N=%d columns=%d sumq=%ld D=%d p=%lu seed=%u\n", d, N, C, sumq, D, (unsigned long)p, seed);
    if (D + 1 > (long)p) { fprintf(stderr, "grid larger than the field\n"); return 1; }
    mt19937_64 rng(seed);
    mp_limb_t U[3][4];
    for (auto &u : U) for (auto &v : u) v = rng() % p;
    // half-binomial coefficients binom(1/2, k) mod p
    vector<mp_limb_t> hb(C + 1);
    hb[0] = 1;
    const mp_limb_t half = nmod_inv(2, mod);
    for (int k = 1; k <= C; ++k)   // binom(1/2,k) = binom(1/2,k-1) * (1/2 - k + 1) / k
        hb[k] = nmod_mul(hb[k - 1], nmod_mul(nmod_sub(half, (mp_limb_t)(k - 1) % p, mod), nmod_inv(k, mod), mod), mod);
    const int G = D + 1;
    // vals[c][j*G + k]: minor omitting column c at (x, y) = (j, k)
    // vals[C] holds K = det[b_0..b_{N-2}, b_{N+1}], the Taylor-frame analogue of Q (lem:cube-polar-minor-identity)
    vector<vector<mp_limb_t>> vals(C + 1, vector<mp_limb_t>((size_t)G * G));
    nmod_mat_t M, sub; nmod_mat_init(M, N, C, p); nmod_mat_init(sub, N, N, p);
    const int CS = C + 1;   // series through T^(N+1)
    vector<mp_limb_t> a(4), ser(CS), tmp(CS), kcol(N);
    for (int j = 0; j < G; ++j)
        for (int k = 0; k < G; ++k) {
            for (int i = 0; i < 4; ++i)
                a[i] = nmod_add(U[0][i], nmod_add(nmod_mul(j, U[1][i], mod), nmod_mul(k, U[2][i], mod), mod), mod);
            for (int r = 0; r < N; ++r) {
                fill(ser.begin(), ser.end(), 0); ser[0] = 1;
                for (int i = 0; i < 4; ++i) if (rows[r].S >> i & 1) {
                    // multiply by sum_k hb[k] a_i^k T^k, truncated at T^(CS-1)
                    vector<mp_limb_t> f(CS); mp_limb_t pw = 1;
                    for (int t = 0; t < CS; ++t) { f[t] = nmod_mul(hb[t], pw, mod); pw = nmod_mul(pw, a[i], mod); }
                    fill(tmp.begin(), tmp.end(), 0);
                    for (int s = 0; s < CS; ++s) if (ser[s]) for (int t = 0; s + t < CS; ++t)
                        tmp[s + t] = nmod_add(tmp[s + t], nmod_mul(ser[s], f[t], mod), mod);
                    ser = tmp;
                }
                for (int c = 0; c < C; ++c) nmod_mat_entry(M, r, c) = c >= rows[r].q ? ser[c - rows[r].q] : 0;
                kcol[r] = N + 1 >= rows[r].q ? ser[N + 1 - rows[r].q] : 0;
            }
            for (int c = 0; c < C; ++c) {
                for (int r = 0; r < N; ++r)
                    for (int cc = 0, t = 0; cc < C; ++cc) if (cc != c) nmod_mat_entry(sub, r, t++) = nmod_mat_entry(M, r, cc);
                vals[c][(size_t)j * G + k] = nmod_mat_det(sub);
            }
            for (int r = 0; r < N; ++r) {
                for (int cc = 0; cc < N - 1; ++cc) nmod_mat_entry(sub, r, cc) = nmod_mat_entry(M, r, cc);
                nmod_mat_entry(sub, r, N - 1) = kcol[r];
            }
            vals[C][(size_t)j * G + k] = nmod_mat_det(sub);
        }
    // interpolate: first in y for each x = j, then in x for each y-coefficient; F[c][b][e] = coefficient of x^e y^b
    vector<mp_limb_t> xs(G); for (int t = 0; t < G; ++t) xs[t] = t;
    long bad = 0;
    vector<vector<vector<mp_limb_t>>> F(C + 1, vector<vector<mp_limb_t>>(G, vector<mp_limb_t>(G, 0)));
    {
        nmod_poly_t P; nmod_poly_init(P, p);
        vector<mp_limb_t> col(G);
        for (int c = 0; c <= C; ++c) {
            vector<vector<mp_limb_t>> cy(G, vector<mp_limb_t>(G, 0));   // cy[j][b]: coefficient of y^b at x = j
            for (int j = 0; j < G; ++j) {
                nmod_poly_interpolate_nmod_vec(P, xs.data(), &vals[c][(size_t)j * G], G);
                for (int b = 0; b < G; ++b) cy[j][b] = nmod_poly_get_coeff_ui(P, b);
            }
            for (int b = 0; b < G; ++b) {
                for (int j = 0; j < G; ++j) col[j] = cy[j][b];
                nmod_poly_interpolate_nmod_vec(P, xs.data(), col.data(), G);
                for (int e = 0; e < G; ++e) {
                    mp_limb_t v = nmod_poly_get_coeff_ui(P, e);
                    if (v && e + b > D) ++bad;
                    else F[c][b][e] = v;
                }
            }
        }
        nmod_poly_clear(P);
    }
    // collision forms on the plane: l = c0 + c1 x + c2 y for a_i and a_i - a_j
    vector<array<mp_limb_t, 3>> forms;
    for (int i = 0; i < 4; ++i) forms.push_back({U[0][i], U[1][i], U[2][i]});
    for (int i = 0; i < 4; ++i) for (int k = i + 1; k < 4; ++k)
        forms.push_back({nmod_sub(U[0][i], U[0][k], mod), nmod_sub(U[1][i], U[1][k], mod), nmod_sub(U[2][i], U[2][k], mod)});
    // Strip the common collision factor: divide every nonzero minor by a form while it divides all of them.  Exact
    // division by c2 y + r(x), r = c0 + c1 x, from the top y-degree: f_b = c2 q_{b-1} + r q_b; divisibility is f_0 = r q_0.
    auto divide = [&](const vector<vector<mp_limb_t>> &f, const array<mp_limb_t, 3> &l, vector<vector<mp_limb_t>> &q) {
        const mp_limb_t ic2 = nmod_inv(l[2], mod);
        q.assign(G, vector<mp_limb_t>(G, 0));
        vector<mp_limb_t> acc(G);
        for (int b = G - 1; b >= 1; --b) {
            for (int e = 0; e < G; ++e) acc[e] = f[b][e];
            if (b < G - 1)   // subtract r * q_b
                for (int e = 0; e < G; ++e) {
                    mp_limb_t t = nmod_mul(l[0], q[b][e], mod);
                    if (e > 0) t = nmod_add(t, nmod_mul(l[1], q[b][e - 1], mod), mod);
                    acc[e] = nmod_sub(acc[e], t, mod);
                }
            for (int e = 0; e < G; ++e) q[b - 1][e] = nmod_mul(acc[e], ic2, mod);
        }
        for (int e = 0; e < G; ++e) {   // remainder f_0 - r q_0 must vanish (and nothing may overflow degree G-1)
            mp_limb_t t = nmod_mul(l[0], q[0][e], mod);
            if (e > 0) t = nmod_add(t, nmod_mul(l[1], q[0][e - 1], mod), mod);
            if (t != f[0][e]) return false;
        }
        for (int b = 0; b < G; ++b) if (q[b][G - 1] && l[1]) return false;
        return true;
    };
    auto zero = [&](const vector<vector<mp_limb_t>> &f) {
        for (auto &row : f) for (auto v : row) if (v) return false;
        return true;
    };
    vector<int> live; for (int c = 0; c < C; ++c) if (!zero(F[c])) live.push_back(c);
    vector<int> stripped(forms.size(), 0);
    for (size_t t = 0; t < forms.size(); ++t) {
        if (!forms[t][2]) { fprintf(stderr, "collision form %zu has no y term; choose another seed\n", t); return 1; }
        for (;;) {
            vector<vector<vector<mp_limb_t>>> Q(live.size());
            bool all = true;
            for (size_t u = 0; u < live.size() && all; ++u) all = divide(F[live[u]], forms[t], Q[u]);
            if (!all) break;
            for (size_t u = 0; u < live.size(); ++u) F[live[u]] = move(Q[u]);
            ++stripped[t];
        }
    }
    // K: divide by the same collision factor, reporting any shortfall
    vector<int> kshort(forms.size(), 0);
    for (size_t t = 0; t < forms.size(); ++t)
        for (int e = 0; e < stripped[t]; ++e) {
            vector<vector<mp_limb_t>> q;
            if (!divide(F[C], forms[t], q)) { kshort[t] = stripped[t] - e; break; }
            F[C] = move(q);
        }
    printf("K shortfall per form (0 = divisible by the whole factor):");
    for (int v : kshort) printf(" %d", v);
    printf("\n");
    printf("common collision exponents:");
    for (int v : stripped) printf(" %d", v);
    printf("\n");
    FILE *out = fopen(argv[4], "w");
    fprintf(out, "-- generated by research/tools/bmd_plane_minors.cpp: p=%lu d=%d seed=%u N=%d D=%d\n",
            (unsigned long)p, d, seed, N, D);
    fprintf(out, "-- common collision factor divided out, exponents per form:");
    for (int v : stripped) fprintf(out, " %d", v);
    fprintf(out, "\nminorList = {\n");
    for (int c = 0; c < C; ++c) {
        bool first = true;
        for (int b = 0; b < G; ++b) for (int e = 0; e < G; ++e) if (F[c][b][e]) {
            fprintf(out, "%s%lu*x^%d*y^%d", first ? "" : "+", (unsigned long)F[c][b][e], e, b);
            first = false;
        }
        if (first) fprintf(out, "0");
        fprintf(out, "%s\n", c + 1 < C ? "," : "");
    }
    fprintf(out, "};\n");
    fprintf(out, "extraK = ");
    { bool first = true;
      for (int b = 0; b < G; ++b) for (int e = 0; e < G; ++e) if (F[C][b][e]) {
          fprintf(out, "%s%lu*x^%d*y^%d", first ? "" : "+", (unsigned long)F[C][b][e], e, b); first = false; }
      if (first) fprintf(out, "0");
      fprintf(out, ";\n"); }
    fprintf(out, "collisionForms = {");
    vector<pair<int,int>> pairs;
    for (int i = 0; i < 4; ++i) pairs.push_back({i, -1});
    for (int i = 0; i < 4; ++i) for (int k = i + 1; k < 4; ++k) pairs.push_back({i, k});
    for (size_t t = 0; t < pairs.size(); ++t) {
        auto [i, k] = pairs[t];
        mp_limb_t c0 = U[0][i], c1 = U[1][i], c2 = U[2][i];
        if (k >= 0) { c0 = nmod_sub(c0, U[0][k], mod); c1 = nmod_sub(c1, U[1][k], mod); c2 = nmod_sub(c2, U[2][k], mod); }
        fprintf(out, "%s%lu+%lu*x+%lu*y", t ? ", " : "", (unsigned long)c0, (unsigned long)c1, (unsigned long)c2);
    }
    fprintf(out, "};\n");
    fclose(out);
    printf("terms above the degree bound (must be 0): %ld\n", bad);
    return bad ? 1 : 0;
}
