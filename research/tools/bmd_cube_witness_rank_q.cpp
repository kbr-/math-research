// Exact dimension over Q of the face-divided witness space at (d, rho) and excess l on {0,1}^3.
//
// Statement tested.  V_l is the space of P' of degree <= 2k - d - 3d (k = l + 4d + rho), origin order >= l and
// multiplicity >= k - d w(v) at the seven nonzero vertices v (w = weight), so that prod (x_i - 1)^d P' is a witness of
// excess l (face divisibility).  Its dimension over Q is its number of columns minus the rank of the integer matrix of
// Hasse-derivative conditions, computed exactly by FLINT's multimodular fmpz_mat_rref_mul.  Equality with the
// dimension over F_q lets the modular cone certificate of bmd_cube_solution_cones lift to characteristic 0.
//
// With J=j as the first argument after rho, it also reports the rank with the rows added that put the jet of P' in
// J^j + m^k (J = (x1 - x2, x3)); P' and P = prod (x_i - 1)^d P' satisfy this together, since the product is a unit at
// the origin.  Equal ranks mean every rational witness of excess l has multiplicity >= j at (1:1:0).
//
// With T as the first argument after rho (before J=j), the space is restricted to its S_3-trivial part: orbit sums of
// monomials, conditions at the vertex representatives (1,0,0), (1,1,0), (1,1,1).
//
// Usage: bmd_cube_witness_rank_q d rho [T] [J=j] l [l ...]
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <array>
#include <flint/flint.h>
#include <flint/fmpz.h>
#include <flint/fmpz_mat.h>
using namespace std;

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: d rho l [l ...]\n"); return 2; }
    int d = atoi(argv[1]), rho = atoi(argv[2]);
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    int m = 4 * d + rho - 1, e = d;
    int jj = 0, first = 3; bool triv = false;
    if (argc > first && argv[first][0] == 'T') { triv = true; first++; }
    if (argc > first && argv[first][0] == 'J') { jj = atoi(argv[first] + 2); first++; }
    for (int ai = first; ai < argc; ai++) {
        int l = atoi(argv[ai]), k = l + m + 1, D = 2 * k - d, Dp = D - 3 * e;
        // basis: monomials, or S_3 orbit sums (trivial part)
        vector<vector<array<int, 3>>> basis;
        for (int t = l; t <= Dp; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) {
            int c = t - a - b;
            if (!triv) { basis.push_back({{a, b, c}}); continue; }
            if (b > a || c > b) continue;
            vector<array<int, 3>> orb;
            int perm[6][3] = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};
            int al[3] = {a, b, c};
            for (int s = 0; s < 6; s++) {
                array<int, 3> g; for (int i = 0; i < 3; i++) g[perm[s][i]] = al[i];
                bool seen = false; for (auto &o : orb) if (o == g) seen = true;
                if (!seen) orb.push_back(g);
            }
            basis.push_back(orb);
        }
        vector<array<int, 3>> mons;  // first monomial of each basis element (for the jet rows below, dense mode only)
        for (auto &bb : basis) mons.push_back(bb[0]);
        int U = basis.size();
        vector<array<int, 3>> verts;
        if (!triv) { for (int v = 1; v < 8; v++) verts.push_back({v & 1, (v >> 1) & 1, (v >> 2) & 1}); }
        else verts = {{1, 0, 0}, {1, 1, 0}, {1, 1, 1}};
        long nrows = 0;
        for (auto &vv : verts) { int w = vv[0] + vv[1] + vv[2]; long K = k - e * w; if (K > 0) nrows += K * (K + 1) * (K + 2) / 6; }
        fmpz_mat_t A; fmpz_mat_init(A, nrows, U);
        fmpz_t c, bin; fmpz_init(c); fmpz_init(bin);
        long r = 0;
        for (auto &vv : verts) {
            int w = vv[0] + vv[1] + vv[2];
            int K = k - e * w;
            for (int s = 0; s < K; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--) {
                int al[3] = {a0, a1, s - a0 - a1};
                for (int u = 0; u < U; u++) {
                    for (auto &mo : basis[u]) {
                        bool ok = true; fmpz_one(c);
                        for (int i = 0; i < 3 && ok; i++) {
                            int bi = mo[i];
                            if (bi < al[i] || (!vv[i] && bi != al[i])) { ok = false; break; }
                            fmpz_bin_uiui(bin, bi, al[i]); fmpz_mul(c, c, bin);
                        }
                        if (ok) fmpz_add(fmpz_mat_entry(A, r, u), fmpz_mat_entry(A, r, u), c);
                    }
                }
                r++;
            }
        }
        fmpz_mat_t B; fmpz_mat_init(B, nrows, U); fmpz_t den; fmpz_init(den);
        long rk = fmpz_mat_rref_mul(B, den, A);
        printf("(d,rho)=(%d,%d) l=%d%s: unknowns %d, rows %ld, rank over Q %ld, dimension over Q %ld\n", d, rho, l, triv ? " (trivial part)" : "", U, nrows, rk, (long)U - rk);
        fflush(stdout);
        if (jj > 0 && !triv) {
            // jet rows: coefficient of t^a u^b s^c (b + c < jj, a + b + c < k) in P'(t, t - u, s)
            vector<array<int, 3>> keys;
            for (int tot = 0; tot < k; tot++) for (int bc = 0; bc < jj && bc <= tot; bc++) for (int b = 0; b <= bc; b++) keys.push_back({tot - bc, b, bc - b});
            fmpz_mat_t A2; fmpz_mat_init(A2, nrows + keys.size(), U);
            for (long i = 0; i < nrows; i++) for (int u = 0; u < U; u++) fmpz_set(fmpz_mat_entry(A2, i, u), fmpz_mat_entry(A, i, u));
            for (size_t q = 0; q < keys.size(); q++) {
                int a = keys[q][0], b = keys[q][1], cc = keys[q][2];
                for (int u = 0; u < U; u++) {
                    int b1 = mons[u][0], b2 = mons[u][1], b3 = mons[u][2];
                    if (b3 != cc || b2 < b || b1 + b2 - b != a) continue;
                    fmpz_bin_uiui(bin, b2, b); if (b & 1) fmpz_neg(bin, bin);
                    fmpz_set(fmpz_mat_entry(A2, nrows + q, u), bin);
                }
            }
            fmpz_mat_t B2; fmpz_mat_init(B2, nrows + keys.size(), U); fmpz_t den2; fmpz_init(den2);
            long rk2 = fmpz_mat_rref_mul(B2, den2, A2);
            printf("  with the jet in J^%d + m^k: rank over Q %ld (%s)\n", jj, rk2, rk2 == rk ? "unchanged: every rational witness satisfies it" : "RISES");
            fflush(stdout);
            fmpz_mat_clear(A2); fmpz_mat_clear(B2); fmpz_clear(den2);
        }
        fmpz_mat_clear(A); fmpz_mat_clear(B); fmpz_clear(den);
        fmpz_clear(c); fmpz_clear(bin);
    }
    return 0;
}
