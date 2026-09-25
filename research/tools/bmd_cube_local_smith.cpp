// Elementary divisors of the cube's boundary constraint matrix along the collision divisor y_1 = 0.
//
// Setting (lem:cube-threshold-ideal, Part 2; prop:cube-boundary-torsion-coprime).  A is the
// N x (N+1) matrix of the coefficients of T^0..T^N in T^Q z^r (r in {0,1}^n, 2Q + |r| <= d), with
// z_i = sum_{j>=1} (-1)^j C_{j-1} (y_i T)^j.  Put y_1 = s and fix y_2..y_n in F_p (generic).  Over the
// discrete valuation ring F_p[[s]], the s-adic valuation of the gcd g of the maximal minors is the
// sum of the elementary divisors of A, and v_s(Delta_{n,d}) is the sum of those of A' = A minus its
// last column.  The kernel computes both lists by a local Smith reduction (pivot of least valuation,
// row and column elimination) in F_p[s]/(s^PREC).
//
// Usage: bmd_cube_local_smith p n DMIN DMAX PREC y_2..y_n [C1]   (one line pair per d)
// With C1, y_1 = C1 + s instead of s: C1 = y_2 studies the divisor y_1 = y_2.
// Output: "A: e_1 ... e_N (sum S)" and "A': ... (sum S')"; an "insufficient precision" line if a
// pivot is not found below PREC.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
typedef long long ll;
static ll P; static int PREC;
static ll md(ll a) { a %= P; return a < 0 ? a + P : a; }
static ll pw(ll b, ll e) { ll r = 1; b = md(b); while (e) { if (e & 1) r = r * b % P; b = b * b % P; e >>= 1; } return r; }
typedef std::vector<ll> ser;  // truncated power series in s, length PREC
static int val(const ser& a) { for (int i = 0; i < PREC; ++i) if (a[i]) return i; return PREC; }
static ser mul(const ser& a, const ser& b) {
    ser c(PREC, 0);
    for (int i = 0; i < PREC; ++i) if (a[i]) for (int j = 0; i + j < PREC; ++j) if (b[j]) c[i + j] = (c[i + j] + a[i] * b[j]) % P;
    return c;
}
static ser inv_unit(const ser& a) {  // a[0] != 0
    ser b(PREC, 0); b[0] = pw(a[0], P - 2);
    for (int k = 1; k < PREC; ++k) {
        ll acc = 0;
        for (int i = 1; i <= k; ++i) acc = (acc + a[i] * b[k - i]) % P;
        b[k] = md(-acc * b[0]);
    }
    return b;
}
static ser shift_down(const ser& a, int v) { ser b(PREC, 0); for (int i = v; i < PREC; ++i) b[i - v] = a[i]; return b; }

static std::vector<int> smith(std::vector<std::vector<ser>> A, bool& ok) {
    int R = (int)A.size(), C = (int)A[0].size();
    std::vector<int> ev; ok = true;
    std::vector<bool> rowdone(R, false), coldone(C, false);
    for (int step = 0; step < std::min(R, C); ++step) {
        int br = -1, bc = -1, bv = PREC;
        for (int i = 0; i < R; ++i) if (!rowdone[i]) for (int j = 0; j < C; ++j) if (!coldone[j]) {
            int v = val(A[i][j]); if (v < bv) { bv = v; br = i; bc = j; }
        }
        if (br < 0) { ok = false; break; }
        ev.push_back(bv);
        // unit part u with A[br][bc] = s^bv u; eliminate other rows: row_i -= (A[i][bc] / A[br][bc]) row_br
        ser u = inv_unit(shift_down(A[br][bc], bv));
        for (int i = 0; i < R; ++i) if (!rowdone[i] && i != br && val(A[i][bc]) < PREC) {
            ser f = mul(shift_down(A[i][bc], bv), u);  // valuation of A[i][bc] >= bv
            for (int j = 0; j < C; ++j) if (!coldone[j]) {
                ser t = mul(f, A[br][j]);
                for (int k = 0; k < PREC; ++k) A[i][j][k] = md(A[i][j][k] - t[k]);
            }
        }
        // column elimination does not change the remaining submatrix's entries outside row br
        rowdone[br] = true; coldone[bc] = true;
    }
    return ev;
}

int main(int argc, char** argv) {
    if (argc < 6) { std::fprintf(stderr, "usage: p n DMIN DMAX PREC y_2..y_n\n"); return 2; }
    P = std::atoll(argv[1]); int n = std::atoi(argv[2]), dmin = std::atoi(argv[3]), dmax = std::atoi(argv[4]); PREC = std::atoi(argv[5]);
    if (argc != 6 + n - 1 && argc != 6 + n) { std::fprintf(stderr, "bad arguments\n"); return 2; }
    ll c1 = argc == 6 + n ? md(std::atoll(argv[5 + n])) : 0;
    std::vector<ll> y(n, 0);
    for (int i = 1; i < n; ++i) y[i] = md(std::atoll(argv[6 + i - 1]));
    for (int d = dmin; d <= dmax; ++d) {
    std::vector<std::pair<int, unsigned>> basis;
    for (int Q = 0; 2 * Q <= d; ++Q)
        for (unsigned r = 0; r < (1u << n); ++r)
            if (2 * Q + __builtin_popcount(r) <= d) basis.push_back({Q, r});
    int N = (int)basis.size(), M = N + 1;
    std::vector<ll> cat(M + 1); cat[0] = 1;
    for (int j = 1; j <= M; ++j) cat[j] = cat[j - 1] * md(2 * (2 * j - 1)) % P * pw(j + 1, P - 2) % P;
    // z_i as series in T whose coefficients are series in s
    std::vector<std::vector<ser>> z(n, std::vector<ser>(M, ser(PREC, 0)));
    for (int j = 1; j < M; ++j) {
        ll cj = md((j % 2 ? -1 : 1) * cat[j - 1]);
        // y_1 = c1 + s: (c1 + s)^j = sum_k binom(j,k) c1^(j-k) s^k
        ll bin = 1;
        for (int k = 0; k <= j && k < PREC; ++k) {
            z[0][j][k] = cj * bin % P * pw(c1, j - k) % P;
            bin = bin * md(j - k) % P * pw(k + 1, P - 2) % P;
        }
        for (int i = 1; i < n; ++i) z[i][j][0] = cj * pw(y[i], j) % P;
    }
    std::vector<std::vector<ser>> A(N, std::vector<ser>(M, ser(PREC, 0)));
    for (int b = 0; b < N; ++b) {
        std::vector<ser> sr(M, ser(PREC, 0)); sr[basis[b].first][0] = 1;
        for (int i = 0; i < n; ++i) if (basis[b].second >> i & 1) {
            std::vector<ser> o(M, ser(PREC, 0));
            for (int a = 0; a < M; ++a) if (val(sr[a]) < PREC) for (int c = 1; a + c < M; ++c) {
                ser t = mul(sr[a], z[i][c]);
                for (int k = 0; k < PREC; ++k) o[a + c][k] = (o[a + c][k] + t[k]) % P;
            }
            sr = o;
        }
        A[b] = sr;
    }
    bool ok1, ok2;
    std::vector<int> e = smith(A, ok1);
    std::vector<std::vector<ser>> A2(N, std::vector<ser>(N));
    for (int b = 0; b < N; ++b) for (int c = 0; c < N; ++c) A2[b][c] = A[b][c];
    std::vector<int> e2 = smith(A2, ok2);
    std::sort(e.begin(), e.end()); std::sort(e2.begin(), e2.end());
    int s1 = 0, s2 = 0;
    std::printf("d=%d A:", d); for (int x : e) { std::printf(" %d", x); s1 += x; } std::printf(" (sum %d)%s\n", s1, ok1 ? "" : " insufficient precision");
    std::printf("d=%d A':", d); for (int x : e2) { std::printf(" %d", x); s2 += x; } std::printf(" (sum %d)%s\n", s2, ok2 ? "" : " insufficient precision");
    std::fflush(stdout);
    }
    return 0;
}
