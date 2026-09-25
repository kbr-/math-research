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
// Relaxation mode (third argument "relax", then j): keep only the multiplicity conditions at the vertices of the plane
// x1 = x2 that differ from 0, namely (1,1,0), (0,0,1), (1,1,1), and the jet condition at the origin (the terms of degree < k
// outside J^j vanish), drop the origin order and the other vertices, and report whether every such polynomial of
// degree <= D lies in J^j (nullity with and without the whole-polynomial J^j rows).  Equal nullities mean that the
// planar relaxation of the vertex-line conjecture holds at this p.
//
// Mask mode (third argument "relaxmask", then pairs MASK j): the same test with the multiplicity conditions kept at the
// vertices v = (v&1, (v>>1)&1, (v>>2)&1) whose bit v is set in MASK; "relax" is MASK 152 (the plane x1 = x2).
//
// Usage: bmd_cube_vertex_line_witness prime p j [j ...]   |   ... prime p relax j   |   ... prime p relaxmask MASK j [MASK j ...]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <array>
#include <string>
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
    bool relaxmask = argc > 3 && string(argv[3]) == "relaxmask";
    bool relax = relaxmask || (argc > 3 && string(argv[3]) == "relax");
    if (relax) {  // unknowns: all monomials of degree <= D
        mons.clear(); idx.clear();
        for (int t = 0; t <= D; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) {
            array<int, 3> e = {a, b, t - a - b}; idx[e] = mons.size(); mons.push_back(e);
        }
    }
    int U = mons.size();
    printf("p=%d: k=%d l=%d D=%d unknowns=%d prime=%llu\n", p, k, l, D, U, (unsigned long long)P); fflush(stdout);
    // vertex rows
    vector<vector<pair<int, u64>>> base;
    vector<int> vtx;  // vertex of each base row
    for (int v = 1; v < 8; v++) {
        int vv[3] = {v & 1, (v >> 1) & 1, (v >> 2) & 1};
        if (relax && !relaxmask && vv[0] != vv[1]) continue;  // plane x1 = x2 only
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
            base.push_back(row); vtx.push_back(v);
        }
    }
    printf("vertex rows %zu\n", base.size()); fflush(stdout);
    for (int ai = 4; relax && ai < argc; ai += relaxmask ? 2 : argc) {
        int mask = relaxmask ? atoi(argv[ai]) : 152, j = atoi(argv[relaxmask ? ai + 1 : ai]);
        vector<vector<pair<int, u64>>> sel;
        for (size_t r = 0; r < base.size(); r++) if (mask >> vtx[r] & 1) sel.push_back(base[r]);
        // J^j rows split by total degree: the jet rows (degree < k) are imposed, the rest are the test
        map<array<int, 3>, vector<pair<int, u64>>> jr;
        for (int u = 0; u < U; u++) {
            int b1 = mons[u][0], b2 = mons[u][1], b3 = mons[u][2];
            for (int b = 0; b <= b2 && b + b3 < j; b++) {
                u64 c = binom(b2, b); if (b & 1) c = (P - c) % P;
                if (c) jr[{b1 + b2 - b, b, b3}].push_back({u, c});
            }
        }
        vector<vector<pair<int, u64>>> jet = sel, all = sel;
        size_t njet = 0;
        for (auto &kv : jr) { all.push_back(kv.second); if (kv.first[0] + kv.first[1] + kv.first[2] < k) { jet.push_back(kv.second); njet++; } }
        auto rank_rows = [&](vector<vector<pair<int, u64>>> &rows) {
            nmod_mat_t A; nmod_mat_init(A, rows.size(), U, P);
            for (size_t r = 0; r < rows.size(); r++) for (auto &e : rows[r]) nmod_mat_entry(A, r, e.first) = e.second;
            long rk = nmod_mat_rank(A); nmod_mat_clear(A); return rk;
        };
        long r0 = rank_rows(jet), r1 = rank_rows(all);
        printf("relax mask=%d j=%d: unknowns %d, vertex rows %zu, jet rows %zu, all J rows %zu; nullity with jet only %ld, with whole J^j %ld: relaxation %s\n",
               mask, j, U, sel.size(), njet, jr.size(), (long)U - r0, (long)U - r1, r0 == r1 ? "holds" : "fails");
        fflush(stdout);
    }
    if (relax) return 0;
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
