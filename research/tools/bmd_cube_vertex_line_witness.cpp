// Boundary witnesses on {0,1}^3 that vanish to a given order along the line through the origin and a vertex.
//
// Statement tested.  A witness for (k, l) is P in F[x1,x2,x3] of degree <= D with Hasse multiplicity >= k at the
// seven nonzero points of {0,1}^3 and order exactly l at the origin.  Let J = (x1 - x2, x3), the ideal of the line
// through 0 and the vertex (1,1,0).  The question: for the boundary parameters (savings p+1 at m = 4p, l = p^2 - 1,
// k = l + m + 1, D = 2k - p), is there a witness in J^j?  By the vertex-line lemma such a witness has a solution
// vector vanishing to order >= j at the double point (1:1:0), so j <= mult F_p = floor(p^2/2) for p <= 7 is forced;
// j = floor(p^2/2) + 1 is a control that must fail.
//
// Method.  Unknowns: coefficients c_beta, l <= |beta| <= D.  Rows: the Hasse derivatives of order < k at the seven
// vertices, and the coefficients of x1^a u^b x3^c with b + c < j in P(x1, x1 - u, x3).  A witness in J^j exists iff
// the rank rises when the degree-l coefficients are also forced to vanish (then some solution has a nonzero
// degree-l part).  Ranks by FLINT nmod_mat_rank modulo a prime.
//
// Usage: bmd_cube_vertex_line_witness prime p j [j ...]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <array>
#include <flint/flint.h>
#include <flint/nmod_mat.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static vector<vector<u64>> C;
static u64 binom(int n, int k) { return (k < 0 || k > n) ? 0 : C[n][k]; }

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: prime p j [j ...]\n"); return 2; }
    P = atoll(argv[1]); int p = atoi(argv[2]);
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    int l = p * p - 1, m = 4 * p, k = l + m + 1, D = 2 * k - p;
    C.assign(D + 2, vector<u64>(D + 2, 0));
    for (int n = 0; n <= D + 1; n++) { C[n][0] = 1; for (int r = 1; r <= n; r++) C[n][r] = (C[n - 1][r - 1] + (r <= n - 1 ? C[n - 1][r] : 0)) % P; }
    vector<array<int, 3>> mons; map<array<int, 3>, int> idx;
    for (int t = l; t <= D; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) {
        array<int, 3> e = {a, b, t - a - b}; idx[e] = mons.size(); mons.push_back(e);
    }
    int U = mons.size();
    printf("p=%d: k=%d l=%d D=%d unknowns=%d prime=%llu\n", p, k, l, D, U, (unsigned long long)P); fflush(stdout);
    // vertex rows
    vector<vector<pair<int, u64>>> base;
    for (int v = 1; v < 8; v++) {
        int vv[3] = {v & 1, (v >> 1) & 1, (v >> 2) & 1};
        for (int s = 0; s < k; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--) {
            int al[3] = {a0, a1, s - a0 - a1};
            vector<pair<int, u64>> row;
            for (int u = 0; u < U; u++) {
                u64 c = 1; bool ok = true;
                for (int i = 0; i < 3 && ok; i++) {
                    int bi = mons[u][i];
                    if (bi < al[i]) { ok = false; break; }
                    if (!vv[i] && bi != al[i]) { ok = false; break; }
                    c = c * binom(bi, al[i]) % P;
                }
                if (ok && c) row.push_back({u, c});
            }
            base.push_back(row);
        }
    }
    printf("vertex rows %zu\n", base.size()); fflush(stdout);
    for (int ai = 3; ai < argc; ai++) {
        int j = atoi(argv[ai]);
        vector<vector<pair<int, u64>>> rows = base;
        // P(x1, x1 - u, x3): monomial x1^b1 x2^b2 x3^b3 -> sum_b C(b2,b)(-1)^b x1^(b1+b2-b) u^b x3^b3
        map<array<int, 3>, vector<pair<int, u64>>> jr;
        for (int u = 0; u < U; u++) {
            int b1 = mons[u][0], b2 = mons[u][1], b3 = mons[u][2];
            for (int b = 0; b <= b2 && b + b3 < j; b++) {
                u64 c = binom(b2, b); if (b & 1) c = (P - c) % P;
                if (c) jr[{b1 + b2 - b, b, b3}].push_back({u, c});
            }
        }
        for (auto &kv : jr) rows.push_back(kv.second);
        auto rank_of = [&](bool kill_low) {
            int extra = 0;
            if (kill_low) for (int u = 0; u < U; u++) if (mons[u][0] + mons[u][1] + mons[u][2] == l) extra++;
            nmod_mat_t A; nmod_mat_init(A, rows.size() + extra, U, P);
            for (size_t r = 0; r < rows.size(); r++) for (auto &e : rows[r]) nmod_mat_entry(A, r, e.first) = e.second;
            size_t r = rows.size();
            if (kill_low) for (int u = 0; u < U; u++) if (mons[u][0] + mons[u][1] + mons[u][2] == l) nmod_mat_entry(A, r++, u) = 1;
            long rk = nmod_mat_rank(A); nmod_mat_clear(A); return rk;
        };
        long r0 = rank_of(false), r1 = rank_of(true);
        printf("j=%d: J-rows %zu, rank %ld, rank with degree-l part killed %ld: witness in J^j with origin order exactly l: %s\n",
               j, jr.size(), r0, r1, r1 > r0 ? "yes" : "no");
        fflush(stdout);
    }
    return 0;
}
