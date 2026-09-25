// Tangent cones at (1:1:0) of product solutions on {0,1}^3, through the vertex-line substitution.
//
// Statement tested.  For the boundary witnesses P_p (l = p^2 - 1, k = p^2 + 4p, degree <= 2k - p, multiplicity >= k at
// the seven nonzero vertices, origin order exactly l), the solution of a witness P is W_c = [w~]_{l+m-c},
// w~ = v(r0(y)) / prod_i L'(r0(y_i)), L(x) = x^2 - x, r0 = L^{-1} (threshold-ideal lemma, part 1).  If P lies in J^j,
// J = (x1 - x2, x3), with normal form sum_{a+b=j} u^a s^b R_ab(t) (u = x1 - x2, s = x3, t = x1), the tangent cone at
// (1:1:0) of the homogeneous component of degree n of w~ is the lambda^{n-j} coefficient of
//     G(lambda; U, S) = sum_{a+b=j} R_ab(r0(lambda)) r0'(lambda)^a (-1)^b U^a S^b / Delta(lambda),
// Delta(lambda) = L'(r0(lambda))^2 L'(0), in the chart y2 = 1, U = y1 - 1 (= t there), S = y3 (= s).  Products multiply
// normal forms.  The kernel computes P_p modulo a prime for the listed p, their normal forms at j = floor(p^2/2),
// and for each requested product pair (p1 p2 | p3 p4) with p1 + p2 = p3 + p4 = d and m = 4d + 1 the 2 x (m+1) matrix
// of tangent cones of the two product solutions, and its rank over F(sigma, tau) (by evaluation at random points).
// Rank 2 is the tangent-cone independence of lem:cube-order-squeeze.
//
// Usage: bmd_cube_product_cones prime SEED p1 p2 p3 p4     (e.g. 1000003 1 2 2 3 1)
// Nullspaces by FLINT nmod_mat.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <map>
#include <array>
#include <random>
#include <flint/flint.h>
#include <flint/nmod_mat.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 mulm(u64 a, u64 b) { return (unsigned __int128)a * b % P; }
static u64 addm(u64 a, u64 b) { return (a + b) % P; }
static u64 subm(u64 a, u64 b) { return (a + P - b) % P; }
static u64 pw(u64 b, u64 e) { u64 r = 1; b %= P; while (e) { if (e & 1) r = mulm(r, b); b = mulm(b, b); e >>= 1; } return r; }
static u64 inv(u64 a) { return pw(a, P - 2); }
static vector<vector<u64>> C;
static u64 binom(int n, int k) { return (k < 0 || k > n) ? 0 : C[n][k]; }

typedef vector<u64> Ser;  // power series in lambda mod lambda^N
static int N;
static Ser smul(const Ser &a, const Ser &b) {
    Ser r(N, 0);
    for (int i = 0; i < N; i++) if (a[i]) for (int j = 0; i + j < N; j++) r[i + j] = addm(r[i + j], mulm(a[i], b[j]));
    return r;
}
static Ser sinv(const Ser &a) {  // a[0] != 0
    Ser r(N, 0); u64 i0 = inv(a[0]); r[0] = i0;
    for (int n = 1; n < N; n++) { u64 s = 0; for (int i = 1; i <= n; i++) s = addm(s, mulm(a[i], r[n - i])); r[n] = mulm(P - s % P, i0); }
    return r;
}

// normal form: for each (a, b) with a + b = j, the coefficient polynomial R_ab(t)
struct Witness { int p, l, j; vector<vector<u64>> R; bool lowerZero; long nullity; };

static Witness witness(int p) {
    Witness W; W.p = p; W.l = p * p - 1; W.j = p * p / 2;
    int k = p * p + 4 * p, D = 2 * k - p, l = W.l;
    vector<array<int, 3>> mons;
    for (int t = l; t <= D; t++) for (int a = t; a >= 0; a--) for (int b = t - a; b >= 0; b--) mons.push_back({a, b, t - a - b});
    int U = mons.size();
    vector<vector<pair<int, u64>>> rows;
    for (int v = 1; v < 8; v++) {
        int vv[3] = {v & 1, (v >> 1) & 1, (v >> 2) & 1};
        for (int s = 0; s < k; s++) for (int a0 = s; a0 >= 0; a0--) for (int a1 = s - a0; a1 >= 0; a1--) {
            int al[3] = {a0, a1, s - a0 - a1};
            vector<pair<int, u64>> row;
            for (int u = 0; u < U; u++) {
                u64 c = 1; bool ok = true;
                for (int i = 0; i < 3 && ok; i++) {
                    int bi = mons[u][i];
                    if (bi < al[i] || (!vv[i] && bi != al[i])) { ok = false; break; }
                    c = mulm(c, binom(bi, al[i]));
                }
                if (ok && c) row.push_back({u, c});
            }
            rows.push_back(row);
        }
    }
    nmod_mat_t A, X; nmod_mat_init(A, rows.size(), U, P);
    for (size_t r = 0; r < rows.size(); r++) for (auto &e : rows[r]) nmod_mat_entry(A, r, e.first) = e.second;
    nmod_mat_init(X, U, U, P);
    W.nullity = nmod_mat_nullspace(X, A);
    nmod_mat_clear(A);
    // pick the first basis vector with a nonzero degree-l part
    int col = -1;
    for (long c = 0; c < W.nullity && col < 0; c++)
        for (int u = 0; u < U; u++) if (mons[u][0] + mons[u][1] + mons[u][2] == l && nmod_mat_entry(X, u, c)) { col = c; break; }
    if (col < 0) { fprintf(stderr, "p=%d: no witness\n", p); exit(1); }
    // normal form along L: P(t, t - u, s) = sum C(b2, b) (-u)^b t^(b1 + b2 - b) s^b3
    int j = W.j;
    W.R.assign(j + 1, vector<u64>(D + 1, 0));
    W.lowerZero = true;
    for (int u = 0; u < U; u++) {
        u64 cf = nmod_mat_entry(X, u, col); if (!cf) continue;
        int b1 = mons[u][0], b2 = mons[u][1], b3 = mons[u][2];
        for (int b = 0; b <= b2; b++) {
            if (b + b3 > j) continue;
            u64 c = mulm(cf, binom(b2, b)); if (b & 1) c = (P - c) % P;
            if (b + b3 < j) { if (c) W.lowerZero = false; continue; }
            W.R[b][b1 + b2 - b] = addm(W.R[b][b1 + b2 - b], c);  // R[a] with a = b (u-power), s-power j - a
        }
    }
    // lower coefficients must cancel after summing; recheck by accumulation
    {
        map<array<int, 3>, u64> low;
        for (int u = 0; u < U; u++) {
            u64 cf = nmod_mat_entry(X, u, col); if (!cf) continue;
            int b1 = mons[u][0], b2 = mons[u][1], b3 = mons[u][2];
            for (int b = 0; b <= b2; b++) if (b + b3 < j) {
                u64 c = mulm(cf, binom(b2, b)); if (b & 1) c = (P - c) % P;
                auto key = array<int, 3>{b1 + b2 - b, b, b3}; low[key] = addm(low[key], c);
            }
        }
        W.lowerZero = true; for (auto &kv : low) if (kv.second) W.lowerZero = false;
    }
    nmod_mat_clear(X);
    return W;
}

// G_p(lambda) numerator: vector over a (U^a S^(j-a)) of series R_a(r0) r0'^a (-1)^(j-a)
static vector<Ser> numerator(const Witness &W, const Ser &r0, const Ser &r0p) {
    vector<Ser> out(W.j + 1, Ser(N, 0));
    for (int a = 0; a <= W.j; a++) {
        Ser acc(N, 0);  // Horner in r0
        for (int e = (int)W.R[a].size() - 1; e >= 0; e--) { acc = smul(acc, r0); acc[0] = addm(acc[0], W.R[a][e]); }
        for (int i = 0; i < a; i++) acc = smul(acc, r0p);
        if ((W.j - a) & 1) for (auto &x : acc) x = (P - x) % P;
        out[a] = acc;
    }
    return out;
}
static vector<Ser> fmul(const vector<Ser> &f, const vector<Ser> &g) {  // forms in U (index = U-degree)
    vector<Ser> r(f.size() + g.size() - 1, Ser(N, 0));
    for (size_t a = 0; a < f.size(); a++) for (size_t b = 0; b < g.size(); b++) {
        Ser pr = smul(f[a], g[b]); for (int i = 0; i < N; i++) r[a + b][i] = addm(r[a + b][i], pr[i]);
    }
    return r;
}

static long rank_mod(vector<vector<u64>> M) {
    long r = 0; size_t rows = M.size(), cols = rows ? M[0].size() : 0;
    for (size_t c = 0; c < cols && r < (long)rows; c++) {
        size_t piv = r; while (piv < rows && !M[piv][c]) piv++;
        if (piv == rows) continue;
        swap(M[piv], M[r]); u64 iv = inv(M[r][c]);
        for (size_t i = 0; i < rows; i++) if (i != (size_t)r && M[i][c]) {
            u64 f = mulm(M[i][c], iv); for (size_t k = 0; k < cols; k++) M[i][k] = subm(M[i][k], mulm(f, M[r][k]));
        }
        r++;
    }
    return r;
}

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: prime seed p1 p2 p3 p4\n"); return 2; }
    P = atoll(argv[1]); unsigned seed = atoi(argv[2]);
    int q[4]; for (int i = 0; i < 4; i++) q[i] = atoi(argv[3 + i]);
    { const char *th = getenv("OMP_NUM_THREADS"); flint_set_num_threads(th ? atoi(th) : 1); }
    int d = q[0] + q[1]; if (q[2] + q[3] != d) { fprintf(stderr, "pairs must have equal sums\n"); return 2; }
    int m = 4 * d + 1;
    int maxD = 0; for (int i = 0; i < 4; i++) maxD = max(maxD, 2 * (q[i] * q[i] + 4 * q[i]) - q[i]);
    C.assign(maxD + 2, vector<u64>(maxD + 2, 0));
    for (int n = 0; n <= maxD + 1; n++) { C[n][0] = 1; for (int r = 1; r <= n; r++) C[n][r] = addm(C[n - 1][r - 1], r <= n - 1 ? C[n - 1][r] : 0); }
    map<int, Witness> Wit;
    for (int i = 0; i < 4; i++) if (!Wit.count(q[i])) {
        Wit[q[i]] = witness(q[i]);
        Witness &W = Wit[q[i]];
        printf("P_%d: l=%d j=%d nullity %ld; normal-form coefficients below j vanish: %s\n", W.p, W.l, W.j, W.nullity, W.lowerZero ? "yes" : "NO");
        fflush(stdout);
    }
    int lA = Wit[q[0]].l + Wit[q[1]].l, lB = Wit[q[2]].l + Wit[q[3]].l;
    int jA = Wit[q[0]].j + Wit[q[1]].j, jB = Wit[q[2]].j + Wit[q[3]].j;
    N = max(lA, lB) + m + 2;
    Ser lam(N, 0); if (N > 1) lam[1] = 1;
    Ser r0(N, 0);  // r0 = -lambda + r0^2
    for (int it = 0; it < N + 1; it++) { Ser sq = smul(r0, r0); for (int i = 0; i < N; i++) r0[i] = subm(sq[i], lam[i]); }
    Ser Lp(N, 0); for (int i = 0; i < N; i++) Lp[i] = mulm(2, r0[i]); Lp[0] = subm(Lp[0], 1);  // L'(r0) = 2 r0 - 1
    Ser r0p = sinv(Lp);
    Ser Delta = smul(Lp, Lp); for (auto &x : Delta) x = (P - x) % P;  // times L'(0) = -1
    Ser Dinv = sinv(Delta);
    auto H = [&](int a, int b) {
        vector<Ser> f = fmul(numerator(Wit[a], r0, r0p), numerator(Wit[b], r0, r0p));
        for (auto &s : f) s = smul(s, Dinv);
        return f;
    };
    vector<Ser> HA = H(q[0], q[1]), HB = H(q[2], q[3]);
    printf("d=%d m=%d: product A = P_%d P_%d (l=%d, j=%d), product B = P_%d P_%d (l=%d, j=%d)\n", d, m, q[0], q[1], lA, jA, q[2], q[3], lB, jB);
    // tangent cone of coordinate c: lambda^(l + m - c - j) coefficient, a form of degree j in (U, S)
    auto cone = [&](const vector<Ser> &Hf, int l, int j, int c) {
        vector<u64> f(j + 1, 0); int o = l + m - c - j;
        if (o >= 0 && o < N) for (int a = 0; a <= j; a++) f[a] = Hf[a][o];
        return f;
    };
    for (int c = m; c >= m - 2; c--) {
        vector<u64> fa = cone(HA, lA, jA, c), fb = cone(HB, lB, jB, c);
        printf("c=%d cone A (coefficients of U^a S^(j-a), a = 0..j):", c); for (auto x : fa) printf(" %llu", (unsigned long long)x);
        printf(" | cone B:"); for (auto x : fb) printf(" %llu", (unsigned long long)x); printf("\n");
    }
    // rank over F(sigma, tau): evaluate at random points
    mt19937_64 rng(seed);
    long best = 0; int zeroA = 0, zeroB = 0;
    for (int trial = 0; trial < 5; trial++) {
        u64 tau = rng() % P, sig = rng() % P;
        vector<vector<u64>> M(2, vector<u64>(m + 1, 0));
        for (int c = 0; c <= m; c++) {
            vector<u64> fa = cone(HA, lA, jA, c), fb = cone(HB, lB, jB, c);
            u64 va = 0, vb = 0;
            for (int a = 0; a <= jA; a++) va = addm(va, mulm(fa[a], mulm(pw(tau, a), pw(sig, jA - a))));
            for (int a = 0; a <= jB; a++) vb = addm(vb, mulm(fb[a], mulm(pw(tau, a), pw(sig, jB - a))));
            M[0][c] = va; M[1][c] = vb;
        }
        long rk = rank_mod(M); best = max(best, rk);
        printf("trial %d (tau=%llu, sigma=%llu): rank %ld\n", trial, (unsigned long long)tau, (unsigned long long)sig, rk);
    }
    for (int c = 0; c <= m; c++) {
        bool za = true, zb = true;
        for (auto x : cone(HA, lA, jA, c)) if (x) za = false;
        for (auto x : cone(HB, lB, jB, c)) if (x) zb = false;
        zeroA += za; zeroB += zb;
    }
    printf("coordinates with zero cone: A %d, B %d (of %d)\n", zeroA, zeroB, m + 1);
    printf("tangent cones independent over F(sigma,tau): %s\n", best == 2 ? "yes" : "not certified");
    return 0;
}
