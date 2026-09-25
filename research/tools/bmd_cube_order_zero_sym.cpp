// Order-zero thresholds on {0,1}^n by symmetric dual solutions (compiled; any n).
//
// Statement computed.  By lem:cube-dual-polynomial-form at l = 0, the savings at (k, 0) on {0,1}^n are
// >= d+1 with m = k-1 iff there is Phi(u_1..u_n) with Phi(0) = 1, deg Phi <= m and
//     [Phi * z^a(u)]_{m-Q} = 0   for every a in {0,1}^n, Q >= 0 with 2Q + |a| <= d,
// where z^a = prod_{a_i=1} r_0(u_i), r_0(u) = sum_{j>=1} (-1)^j C_{j-1} u^j.  The system is invariant
// under permutations of the variables, so averaging a solution over S_n (n! invertible) gives a
// symmetric one: it suffices to solve for Phi = 1 + sum_lambda x_lambda m_lambda over monomial
// symmetric polynomials, and to impose the equations for a = (1^k, 0^(n-k)) at monomials u^g with g
// sorted within the first k and within the last n-k coordinates (the equation polynomial is invariant
// under S_k x S_(n-k)).  For each d <= DMAX the program prints the least m <= MMAX with a solution, the
// least m at which savings >= d+1 at order 0 (the scan mode checks the larger m as well).
//
// Usage: bmd_cube_order_zero_sym p n DMAX MMAX [MSTART [DMIN [scan]]]  ("scan": report solvability at
// every m in [MSTART, MMAX] instead of stopping at the least one)  (MSTART must not exceed the true
// threshold at DMIN; it is a lower bound from an earlier run)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <omp.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = r * a % P; a = a * a % P; e >>= 1; } return r; }

static void partitions(int n, int total, int maxpart, vector<int> &cur, vector<vector<int>> &out) {
    if (total == 0) { vector<int> v = cur; v.resize(n, 0); out.push_back(v); return; }
    if ((int)cur.size() == n) return;
    for (int x = min(total, maxpart); x >= 1; x--) { cur.push_back(x); partitions(n, total - x, x, cur, out); cur.pop_back(); }
}
// compositions g of D into n parts, sorted descending within [0,k) and within [k,n)
static void blocks(int n, int k, int D, vector<vector<int>> &out) {
    for (int D1 = 0; D1 <= D; D1++) {
        vector<vector<int>> A, B; vector<int> cur;
        if (k == 0) { if (D1) continue; A.push_back({}); }
        else { vector<vector<int>> t; partitions(k, D1, D1, cur, t); if (D1 == 0) t = {vector<int>(k, 0)}; A = t; }
        if (n - k == 0) { if (D - D1) continue; B.push_back({}); }
        else { vector<vector<int>> t; cur.clear(); partitions(n - k, D - D1, D - D1, cur, t); if (D - D1 == 0) t = {vector<int>(n - k, 0)}; B = t; }
        for (auto &a : A) for (auto &b : B) { vector<int> g = a; g.insert(g.end(), b.begin(), b.end()); out.push_back(g); }
    }
}

// rank of [A | b] vs A; returns true if consistent
static bool solvable(vector<vector<u64>> &M, int nu) {
    int n = M.size(), r = 0;
    for (int c = 0; c <= nu && r < n; c++) {
        int piv = -1; for (int i = r; i < n; i++) if (M[i][c]) { piv = i; break; }
        if (piv < 0) continue;
        if (c == nu) return false;  // pivot in the RHS column: inconsistent
        swap(M[piv], M[r]);
        u64 iv = pw(M[r][c], P - 2);
        for (int j = c; j <= nu; j++) M[r][j] = M[r][j] * iv % P;
        #pragma omp parallel for schedule(static)
        for (int i = r + 1; i < n; i++) if (M[i][c]) {
            u64 f = P - M[i][c];
            for (int j = c; j <= nu; j++) if (M[r][j]) M[i][j] = (M[i][j] + f * M[r][j]) % P;
        }
        r++;
    }
    return true;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: p n DMAX MMAX [MSTART]\n"); return 2; }
    P = atoll(argv[1]); int n = atoi(argv[2]), DMAX = atoi(argv[3]), MMAX = atoi(argv[4]);
    int MSTART = argc > 5 ? atoi(argv[5]) : 1, DMIN = argc > 6 ? atoi(argv[6]) : 1;
    bool scan = argc > 7 && string(argv[7]) == "scan";
    if (P % 2 == 0 || P <= (u64)MMAX + 2) { fprintf(stderr, "need odd p > MMAX + 2\n"); return 2; }
    vector<u64> cat(MMAX + 2, 0), kap(MMAX + 2, 0); cat[0] = 1;
    for (int j = 1; j <= MMAX + 1; j++) cat[j] = cat[j - 1] * 2 % P * ((2 * j - 1) % P) % P * pw(j + 1, P - 2) % P;
    for (int j = 1; j <= MMAX + 1; j++) kap[j] = (j % 2) ? (P - cat[j - 1]) % P : cat[j - 1];
    // symmetric basis up to degree MMAX: exponent vectors (sorted desc) and their distinct permutations
    vector<vector<int>> lam; vector<int> ldeg; vector<vector<vector<int>>> perms;
    for (int j = 1; j <= MMAX; j++) {
        vector<vector<int>> t; vector<int> cur; partitions(n, j, j, cur, t);
        for (auto &v : t) {
            lam.push_back(v); ldeg.push_back(j);
            vector<int> s = v; sort(s.begin(), s.end());
            vector<vector<int>> ps; do ps.push_back(s); while (next_permutation(s.begin(), s.end()));
            perms.push_back(ps);
        }
    }
    printf("n=%d p=%llu: symmetric unknowns up to degree %d: %zu\n", n, (unsigned long long)P, MMAX, lam.size()); fflush(stdout);
    int m0 = MSTART;
    for (int d = DMIN; d <= DMAX; d++) {
        int found = -1;
        for (int m = m0; m <= MMAX; m++) {
            // unknowns: lambda with degree <= m (they are ordered by degree)
            int nu = 0; while (nu < (int)lam.size() && ldeg[nu] <= m) nu++;
            vector<vector<u64>> M;
            for (int Q = 0; 2 * Q <= d; Q++) for (int k = 0; k <= n && 2 * Q + k <= d; k++) {
                int D = m - Q; if (D < 0) continue;
                vector<vector<int>> gs; blocks(n, k, D, gs);
                vector<vector<u64>> rows(gs.size(), vector<u64>(nu + 1, 0));
                #pragma omp parallel for schedule(dynamic)
                for (size_t gi = 0; gi < gs.size(); gi++) {
                    const vector<int> &g = gs[gi];
                    vector<u64> &row = rows[gi];
                    // constant term Phi_0 = 1: coefficient of u^g in z^a
                    bool ok = true; u64 c0 = 1;
                    for (int i = 0; i < n; i++) { if (i < k) { if (g[i] < 1) { ok = false; break; } c0 = c0 * kap[g[i]] % P; } else if (g[i]) { ok = false; break; } }
                    if (ok) row[nu] = (P - c0) % P;  // move to the right-hand side
                    for (int L = 0; L < nu; L++) {
                        if (ldeg[L] > D - k) break;
                        u64 acc = 0;
                        for (auto &e : perms[L]) {
                            bool good = true; u64 c = 1;
                            for (int i = 0; i < n; i++) {
                                if (i < k) { int f = g[i] - e[i]; if (f < 1) { good = false; break; } c = c * kap[f] % P; }
                                else if (e[i] != g[i]) { good = false; break; }
                            }
                            if (good) acc = (acc + c) % P;
                        }
                        row[L] = acc;
                    }
                }
                for (auto &r : rows) { bool nz = false; for (auto x : r) if (x) { nz = true; break; } if (nz) M.push_back(r); }
            }
            bool sol = solvable(M, nu);
            if (scan) { printf("d=%d m=%d: %s\n", d, m, sol ? "solvable" : "not solvable"); fflush(stdout); if (sol && found < 0) found = m; continue; }
            if (sol) { found = m; break; }
        }
        printf("d=%d: least m with an order-zero solution (savings >= %d at l = 0) = %d\n", d, d + 1, found);
        fflush(stdout);
        if (found < 0) break;
        m0 = found;  // thresholds do not decrease in d (I^(d+2) is contained in I^(d+1))
    }
    return 0;
}
