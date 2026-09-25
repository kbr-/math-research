// Splitting type of the 3-cube's solution module restricted to a line through a point.
//
// Statement computed.  Let E be the module of solutions W = (W_0..W_m) of the (d+1)-system at m on
// {0,1}^3 (sum_c W_c [T^c] f = 0 for the basis f = T^Q z^r, 2Q+|r| <= d, of V_{3,d}; W_c homogeneous of
// degree l + m - c).  For a line L = {u0 P + u1 Q} in P^2, the solutions of the same system with W_c
// binary forms in (u0,u1) (y = u0 P + u1 Q) form a free graded module E_L = sum_i F[u0,u1](-b_i) of rank
// rho = m + 1 - 4d (when the restricted constraint matrix has rank 4d).  For l = 0..LMAX this program
// prints dim (E_L)_l and dim of {W_m : W in (E_L)_l}, and from the first it recovers the b_i.
// Restriction bound: if every global solution vanishes to order >= k at P (along L), then
// l_0(d+1,m) >= k + min_i b_i, because W|_L = u1^k X with X a section of E_L of degree l - k whose
// W_m is nonzero for a line not contained in {W_m = 0}.
//
// Usage: bmd_cube_line_splitting p P1 P2 P3 Q1 Q2 Q3 CASE [CASE ...], CASE = d:m:LMAX[:LMIN]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <algorithm>
#include <omp.h>
using namespace std;
typedef uint64_t u64;
static u64 PR;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= PR; while (e) { if (e & 1) r = r * a % PR; a = a * a % PR; e >>= 1; } return r; }
typedef vector<u64> Poly;  // polynomial in x = u1/u0, coefficient of x^i at index i
static Poly pmul(const Poly &a, const Poly &b) {
    Poly c(a.size() + b.size() - 1, 0);
    for (size_t i = 0; i < a.size(); i++) if (a[i]) for (size_t j = 0; j < b.size(); j++) c[i + j] = (c[i + j] + a[i] * b[j]) % PR;
    return c;
}

// rank of a dense matrix mod PR (rows x cols), destroys M
static int rank_mod(vector<vector<u64>> &M, int cols) {
    int r = 0, n = M.size();
    for (int c = 0; c < cols && r < n; c++) {
        int piv = -1;
        for (int i = r; i < n; i++) if (M[i][c]) { piv = i; break; }
        if (piv < 0) continue;
        swap(M[piv], M[r]);
        u64 iv = pw(M[r][c], PR - 2);
        for (int j = c; j < cols; j++) M[r][j] = M[r][j] * iv % PR;
        #pragma omp parallel for schedule(static)
        for (int i = r + 1; i < n; i++) if (M[i][c]) {
            u64 f = PR - M[i][c];
            for (int j = c; j < cols; j++) if (M[r][j]) M[i][j] = (M[i][j] + f * M[r][j]) % PR;
        }
        r++;
    }
    return r;
}

static int run_case(int d, int m, int LMAX, int LMIN, long long *Pp, long long *Qq);
int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "usage: p P1 P2 P3 Q1 Q2 Q3 CASE [CASE ...], CASE = d:m:LMAX\n"); return 2; }
    PR = atoll(argv[1]);
    long long Pp[3], Qq[3];
    for (int i = 0; i < 3; i++) { Pp[i] = atoll(argv[2 + i]); Qq[i] = atoll(argv[5 + i]); }
    for (int a = 8; a < argc; a++) {
        int d, m, L, L0 = 0;
        int got = sscanf(argv[a], "%d:%d:%d:%d", &d, &m, &L, &L0);
        if (got < 3) { fprintf(stderr, "bad case %s\n", argv[a]); return 2; }
        int rc = run_case(d, m, L, L0, Pp, Qq);
        if (rc) return rc;
    }
    return 0;
}
static int run_case(int d, int m, int LMAX, int LMIN, long long *Pp, long long *Qq) {
    if (PR % 2 == 0 || PR <= (u64)m + 2 || m + 1 - 4 * d < 1) { fprintf(stderr, "need odd p > m+2, rho >= 1\n"); return 2; }
    // kappa_j = (-1)^j C_{j-1}
    vector<u64> cat(m + 2, 0), kap(m + 2, 0); cat[0] = 1;
    for (int j = 1; j <= m + 1; j++) cat[j] = cat[j - 1] * 2 % PR * ((2 * j - 1) % PR) % PR * pw(j + 1, PR - 2) % PR;
    for (int j = 1; j <= m + 1; j++) kap[j] = (j % 2) ? (PR - cat[j - 1]) % PR : cat[j - 1];
    // y_i(x) = P_i + x Q_i (dehomogenized, u0 = 1); z_i coefficients [T^j] z_i = kap_j y_i^j
    vector<vector<Poly>> Z(3, vector<Poly>(m + 1));
    for (int i = 0; i < 3; i++) {
        Poly y = {(u64)((Pp[i] % (long long)PR + (long long)PR) % (long long)PR), (u64)((Qq[i] % (long long)PR + (long long)PR) % (long long)PR)};
        Poly yp = {1};
        Z[i][0] = {0};
        for (int j = 1; j <= m; j++) { yp = pmul(yp, y); Z[i][j] = yp; for (auto &c : Z[i][j]) c = c * kap[j] % PR; }
    }
    // basis rows: F[f][c] = [T^c] f as polynomial in x, homogeneous degree c - Q (as binary form)
    struct Row { int Q; vector<Poly> F; };
    vector<Row> rows;
    for (int Q = 0; 2 * Q <= d; Q++) for (int r = 0; r < 8; r++) {
        if (2 * Q + __builtin_popcount(r) > d) continue;
        vector<Poly> S(m + 1, Poly{0});
        if (Q <= m) S[Q] = Poly{1};
        for (int i = 0; i < 3; i++) if (r >> i & 1) {
            vector<Poly> N(m + 1, Poly{0});
            for (int a = 0; a <= m; a++) for (int b = 1; a + b <= m; b++) {
                Poly pr = pmul(S[a], Z[i][b]);
                if (N[a + b].size() < pr.size()) N[a + b].resize(pr.size(), 0);
                for (size_t k = 0; k < pr.size(); k++) N[a + b][k] = (N[a + b][k] + pr[k]) % PR;
            }
            S = N;
        }
        rows.push_back({Q, S});
    }
    if ((int)rows.size() != 4 * d) { fprintf(stderr, "basis size\n"); return 3; }
    int rho = m + 1 - 4 * d;
    printf("p=%llu d=%d m=%d rho=%d line P=(%lld,%lld,%lld) Q=(%lld,%lld,%lld)\n", (unsigned long long)PR, d, m, rho, Pp[0], Pp[1], Pp[2], Qq[0], Qq[1], Qq[2]);
    // degrees l from LMIN (negative allowed: W_c of negative degree is 0) to LMAX
    int NL = LMAX - LMIN + 1;
    vector<int> dims(NL), dimsm(NL);
    for (int l = LMIN; l <= LMAX; l++) {
        // unknowns: coefficients of W_c, degree D_c = l + m - c (x^0..x^D_c), c = 0..m; W_m block last
        vector<int> off(m + 2, 0);
        for (int c = 0; c <= m; c++) off[c + 1] = off[c] + max(0, l + m - c + 1);
        int nu = off[m + 1];
        vector<vector<u64>> M;
        for (auto &R : rows) {
            int deg = l + m - R.Q;  // binary-form degree of sum_c W_c F_c
            for (int e = 0; e <= deg; e++) {
                vector<u64> eq(nu, 0);
                bool any = false;
                for (int c = 0; c <= m; c++) {
                    const Poly &F = R.F[c];
                    int Dc = l + m - c;
                    for (size_t k = 0; k < F.size(); k++) if (F[k]) {
                        int a = e - (int)k;
                        if (a < 0 || a > Dc) continue;  // Dc < 0: no unknowns
                        eq[off[c] + a] = (eq[off[c] + a] + F[k]) % PR;
                        any = true;
                    }
                }
                if (any) M.push_back(eq);
            }
        }
        // dim of solutions = nu - rank; dim of W_m image = dim - dim{solutions with W_m = 0}
        vector<vector<u64>> M2 = M;
        int rk = rank_mod(M, nu);
        int nW = off[m + 1] - off[m];
        // solutions with W_m = 0: add equations W_m coefficients = 0
        for (int a = 0; a < nW; a++) { vector<u64> eq(nu, 0); eq[off[m] + a] = 1; M2.push_back(eq); }
        int rk2 = rank_mod(M2, nu);
        dims[l - LMIN] = nu - rk;
        dimsm[l - LMIN] = (nu - rk) - (nu - rk2);
        printf("l=%d: dim E_L = %d, dim W_m image = %d\n", l, dims[l - LMIN], dimsm[l - LMIN]);
        fflush(stdout);
    }
    // recover b_i from h(l) = sum_i max(0, l - b_i + 1): second differences
    printf("generator degrees b_i:");
    // valid when dims vanish below LMIN (checked: dims[0] must be 0 for a complete recovery)
    for (int i = 0; i < NL; i++) {
        int h = dims[i], h1 = i >= 1 ? dims[i - 1] : 0, h2 = i >= 2 ? dims[i - 2] : 0;
        int cnt = h - 2 * h1 + h2;
        for (int k = 0; k < cnt; k++) printf(" %d", i + LMIN);
    }
    printf("%s\n", dims[0] ? "  (incomplete: dim E_L nonzero at LMIN; lower LMIN)" : "");
    return 0;
}
