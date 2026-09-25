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
// Usage: bmd_cube_witness_rank_q d rho [J=j] l [l ...]
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
    int jj = 0, first = 3;
    if (argc > 3 && argv[3][0] == 'J') { jj = atoi(argv[3] + 2); first = 4; }
    for (int ai = first; ai < argc; ai++) {
        int l = atoi(argv[ai]), k = l + m + 1, D = 2 * k - d, Dp = D - 3 * e;
        vector<array<int, 3>> mons;
        for (int t = l; t <= Dp; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) mons.push_back({a, b, t - a - b});
        int U = mons.size();
        long nrows = 0;
        for (int v = 1; v < 8; v++) { int w = (v & 1) + ((v >> 1) & 1) + ((v >> 2) & 1); long K = k - e * w; if (K > 0) nrows += K * (K + 1) * (K + 2) / 6; }
        fmpz_mat_t A; fmpz_mat_init(A, nrows, U);
        fmpz_t c, bin; fmpz_init(c); fmpz_init(bin);
        long r = 0;
        for (int v = 1; v < 8; v++) {
            int vv[3] = {v & 1, (v >> 1) & 1, (v >> 2) & 1}, w = vv[0] + vv[1] + vv[2];
            int K = k - e * w;
            for (int s = 0; s < K; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--) {
                int al[3] = {a0, a1, s - a0 - a1};
                for (int u = 0; u < U; u++) {
                    bool ok = true; fmpz_one(c);
                    for (int i = 0; i < 3 && ok; i++) {
                        int bi = mons[u][i];
                        if (bi < al[i] || (!vv[i] && bi != al[i])) { ok = false; break; }
                        fmpz_bin_uiui(bin, bi, al[i]); fmpz_mul(c, c, bin);
                    }
                    if (ok) fmpz_set(fmpz_mat_entry(A, r, u), c);
                }
                r++;
            }
        }
        fmpz_mat_t B; fmpz_mat_init(B, nrows, U); fmpz_t den; fmpz_init(den);
        long rk = fmpz_mat_rref_mul(B, den, A);
        printf("(d,rho)=(%d,%d) l=%d: unknowns %d, rows %ld, rank over Q %ld, dimension over Q %ld\n", d, rho, l, U, nrows, rk, (long)U - rk);
        fflush(stdout);
        if (jj > 0) {
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
