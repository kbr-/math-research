// Row and column problems of the two-plane lift on {0,1}^3.
//
// Statement tested.  In coordinates (t, u, s) = (x1, x1 - x2, x3) write P = sum_{b,c} u^b s^c R_bc(t), and let
// k = p^2 + 4p, D = 2k - p, psi = floor(p^2/2) (boundary parameters).  Multiplicity >= k at the nonzero vertices of the
// plane u = 0 is the condition, for each row b, that Q_b = sum_c s^c R_bc(t) has multiplicity >= k - b at the points
// (t, s) = (1,0), (0,1), (1,1); at the nonzero vertices of the plane s = 0 it is the condition, for each column c,
// that P_c = sum_b u^b R_bc(t) has multiplicity >= k - c at (t, u) = (1,1), (0,-1), (1,0).  The jet hypothesis at the
// origin kills the coefficients t^a w^e (w = s in rows, u in columns) of the row or column with index i and
// e < psi - i, a + e < k - i; degrees are deg R_bc <= D - b - c.  For each row b < psi ("side" problem) and each
// column c < psi ("diag" problem) the kernel reports the indices e < psi - i at which some solution has a nonzero
// coefficient (the unforced entries), and the rank against the number of conditions.
//
// Mode "plain D K m0": the square problem with multiplicity K at (1,0), (0,1), (1,1) and m0 at the origin in degree
// <= D; prints the dimension of the solution space (for comparison with the (-1)-curve count on the blown-up plane).
//
// Usage: bmd_cube_plane_rows prime rows p [p ...]   |   bmd_cube_plane_rows prime plain D K m0 [D K m0 ...]
// Ranks and nullspaces by FLINT nmod_mat modulo the prime.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <array>
#include <flint/flint.h>
#include <flint/nmod_mat.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static vector<vector<u64>> C;
static u64 binom(int n, int k) { return (k < 0 || k > n) ? 0 : C[n][k]; }
static u64 pw(u64 b, int e) { u64 r = 1; while (e-- > 0) r = r * b % P; return r; }

struct Sys { vector<array<int, 2>> mons; vector<vector<pair<int, u64>>> rows; };

// unknowns t^a w^e with a + e <= Dg, minus the killed jet coefficients (e < jj, a + e < Kjet)
static Sys build(int Dg, int K, const vector<array<long, 2>> &pts, int jj, int Kjet, int m0) {
    Sys S;
    for (int a = 0; a <= Dg; a++) for (int e = 0; a + e <= Dg; e++) {
        if (e < jj && a + e < Kjet) continue;
        if (a + e < m0) continue;
        S.mons.push_back({a, e});
    }
    int U = S.mons.size();
    for (auto &pt : pts) {
        u64 t0 = (pt[0] % (long)P + P) % P, w0 = (pt[1] % (long)P + P) % P;
        for (int al = 0; al < K; al++) for (int ga = 0; al + ga < K; ga++) {
            vector<pair<int, u64>> row;
            for (int u = 0; u < U; u++) {
                int a = S.mons[u][0], e = S.mons[u][1];
                if (a < al || e < ga) continue;
                u64 c = binom(a, al) * binom(e, ga) % P * pw(t0, a - al) % P * pw(w0, e - ga) % P;
                if (c) row.push_back({u, c});
            }
            S.rows.push_back(row);
        }
    }
    return S;
}

static long nullspace(const Sys &S, nmod_mat_t X) {
    int U = S.mons.size();
    nmod_mat_t A; nmod_mat_init(A, S.rows.size(), U, P);
    for (size_t r = 0; r < S.rows.size(); r++) for (auto &e : S.rows[r]) nmod_mat_entry(A, r, e.first) = e.second;
    nmod_mat_init(X, U, U, P);
    long nul = nmod_mat_nullspace(X, A);
    nmod_mat_clear(A);
    return nul;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: prime rows p... | prime plain D K m0 ...\n"); return 2; }
    P = atoll(argv[1]);
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    string mode = argv[2];
    int maxD = 0;
    if (mode == "rows") for (int i = 3; i < argc; i++) { int p = atoi(argv[i]); maxD = max(maxD, 2 * (p * p + 4 * p) - p); }
    else for (int i = 3; i < argc; i += 3) maxD = max(maxD, atoi(argv[i]));
    C.assign(maxD + 2, vector<u64>(maxD + 2, 0));
    for (int n = 0; n <= maxD + 1; n++) { C[n][0] = 1; for (int r = 1; r <= n; r++) C[n][r] = (C[n - 1][r - 1] + (r <= n - 1 ? C[n - 1][r] : 0)) % P; }
    if (mode == "plain") {
        for (int i = 3; i + 2 < argc; i += 3) {
            int Dg = atoi(argv[i]), K = atoi(argv[i + 1]), m0 = atoi(argv[i + 2]);
            Sys S = build(Dg, K, {{1, 0}, {0, 1}, {1, 1}}, 0, 0, m0);
            nmod_mat_t X; long nul = nullspace(S, X); nmod_mat_clear(X);
            printf("plain D=%d K=%d m0=%d: dimension %ld\n", Dg, K, m0, nul); fflush(stdout);
        }
        return 0;
    }
    for (int i = 3; i < argc; i++) {
        int p = atoi(argv[i]), k = p * p + 4 * p, D = 2 * k - p, psi = p * p / 2;
        printf("p=%d k=%d D=%d psi=%d\n", p, k, D, psi); fflush(stdout);
        for (int type = 0; type < 2; type++) {
            vector<array<long, 2>> pts = type == 0 ? vector<array<long, 2>>{{1, 0}, {0, 1}, {1, 1}}
                                                   : vector<array<long, 2>>{{1, 1}, {0, -1}, {1, 0}};
            for (int idx = 0; idx < psi; idx++) {
                int K = k - idx, Dg = D - idx, jj = psi - idx;
                Sys S = build(Dg, K, pts, jj, K, 0);
                nmod_mat_t X; long nul = nullspace(S, X);
                vector<int> unforced;
                for (int e = 0; e < jj; e++) {
                    bool nz = false;
                    for (size_t u = 0; u < S.mons.size() && !nz; u++) if (S.mons[u][1] == e)
                        for (long c = 0; c < nul && !nz; c++) if (nmod_mat_entry(X, u, c)) nz = true;
                    if (nz) unforced.push_back(e);
                }
                nmod_mat_clear(X);
                printf("%s %d: unknowns %zu conditions %zu nullity %ld; unforced entries below %d:", type == 0 ? "row(side)" : "col(diag)",
                       idx, S.mons.size(), S.rows.size(), nul, jj);
                for (int e : unforced) printf(" %d", e);
                printf("\n"); fflush(stdout);
            }
        }
    }
    return 0;
}
