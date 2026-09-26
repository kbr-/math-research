// Maximal minors of the boundary constraint matrix A_{4d} along a line of F_2 = 0 (route review of 26 September 2026).
//
// Statement tested.  The line-gcd property: along y(u) = (u, 1, u+1) (the line y3 = y1 + y2), the gcd over F_q[u] of the
// coordinates of the boundary solution W^(d) is u^{psi(d)}, psi(d) = floor(d^2/2) (lem:cube-line-gcd-criterion).
// W^(d) is the primitive kernel vector of A_{4d}, whose rows are the T-expansions at p_0 of the basis T^Q w^r
// (r in {0,1}^3, 2Q + |r| <= d) of V_d, w_i = (1 + a_i T)^{1/2}, a = 4y, columns c = 0..4d.  So W^(d) is the vector of
// signed maximal minors divided by their gcd g_{3,d}.  For each point u = u0, ..., u0+K-1 this program prints the
// 4d+1 maximal minors of A_{4d}(y(u)) mod q; bmd_cube_line_gcd.py (mode "minors") interpolates them in u and reports
// the multiplicities of their gcd at u = 0, -1, 1 and the rest, to compare with g_{3,d} restricted to the line.
//
// Usage: bmd_cube_line_minors q d1,d2,... u0 K
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 mulm(u64 a, u64 b) { return (unsigned __int128)a * b % P; }
static u64 pw(u64 b, u64 e) { u64 r = 1; b %= P; while (e) { if (e & 1) r = mulm(r, b); b = mulm(b, b); e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }
static u64 det(vector<vector<u64>> M) {
    size_t n = M.size(); u64 d = 1;
    for (size_t c = 0; c < n; c++) {
        size_t p = c; while (p < n && !M[p][c]) p++;
        if (p == n) return 0;
        if (p != c) { swap(M[p], M[c]); d = (P - d) % P; }
        d = mulm(d, M[c][c]); u64 iv = inv(M[c][c]);
        for (size_t r = c + 1; r < n; r++) if (M[r][c]) {
            u64 f = mulm(M[r][c], iv);
            for (size_t k = c; k < n; k++) M[r][k] = (M[r][k] + P - mulm(f, M[c][k])) % P;
        }
    }
    return d;
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: q d u0 K\n"); return 2; }
    P = atoll(argv[1]); long long u0 = atoll(argv[3]); int K = atoi(argv[4]);
    vector<int> ds; { const char *s = argv[2]; while (*s) { ds.push_back(atoi(s)); while (*s && *s != ',') s++; if (*s) s++; } }
    for (int d : ds) {
    int m = 4 * d, N = m + 1;
    // sqrt(1+x) coefficients binom(1/2, k) mod P
    vector<u64> sq(N, 0); sq[0] = 1;
    for (int k = 1; k < N; k++) { // binom(1/2,k) = binom(1/2,k-1) * (1/2 - (k-1)) / k
        u64 num = (inv(2) + P - (u64)(k - 1) % P) % P;
        sq[k] = mulm(mulm(sq[k - 1], num), inv(k));
    }
    vector<vector<int>> basis;  // (Q, r1, r2, r3)
    for (int Q = 0; 2 * Q <= d; Q++) for (int r = 0; r < 8; r++) {
        int w = (r & 1) + ((r >> 1) & 1) + ((r >> 2) & 1);
        if (2 * Q + w <= d) basis.push_back({Q, r & 1, (r >> 1) & 1, (r >> 2) & 1});
    }
    if ((int)basis.size() != 4 * d) { fprintf(stderr, "basis size %zu != 4d\n", basis.size()); return 3; }
    printf("d=%d m=%d rows %zu u0=%lld K=%d\n", d, m, basis.size(), u0, K);
    for (int i = 0; i < K; i++) {
        long long u = u0 + i;
        u64 y[3] = {(u64)((u % (long long)P + P) % P), 1, (u64)(((u + 1) % (long long)P + P) % P)};
        vector<vector<u64>> w(3, vector<u64>(N));
        for (int j = 0; j < 3; j++) { u64 a = mulm(4, y[j]), ap = 1; for (int k = 0; k < N; k++) { w[j][k] = mulm(sq[k], ap); ap = mulm(ap, a); } }
        vector<vector<u64>> A;
        for (auto &b : basis) {
            vector<u64> row(N, 0); row[b[0]] = 1;  // T^Q
            for (int j = 0; j < 3; j++) if (b[j + 1]) {
                vector<u64> nr(N, 0);
                for (int x = 0; x < N; x++) if (row[x]) for (int z = 0; x + z < N; z++) nr[x + z] = (nr[x + z] + mulm(row[x], w[j][z])) % P;
                row = nr;
            }
            A.push_back(row);
        }
        printf("MIN %lld", u);
        for (int c = 0; c < N; c++) {
            vector<vector<u64>> M; for (auto &row : A) { vector<u64> r2; for (int k = 0; k < N; k++) if (k != c) r2.push_back(row[k]); M.push_back(r2); }
            u64 dv = det(M); if (c & 1) dv = (P - dv) % P;
            printf(" %llu", (unsigned long long)dv);
        }
        printf("\n");
    }
    }
    return 0;
}
