// Values of the boundary maximal minors of the cube's order constraint matrix along a line.
//
// Setting (lem:cube-threshold-ideal, Part 2).  For the cube {0,1}^n over F_p, degree d, basis
// T^Q z^r (r in {0,1}^n, 2Q + |r| <= d; N elements, including 1), z_i = sum_{j>=1} (-1)^j C_{j-1}
// (y_i T)^j, the constraint matrix A is N x (N+1): entry (f, c) = [T^c] f for c = 0..N.  Its
// maximal minors M_c (delete column c) are homogeneous polynomials in y; M_N = +-Delta_{n,d}.
// This kernel restricts y to the affine line y = u + t v, evaluates every M_c(t) at t = 0..P-1,
// interpolates, and takes g(t) = gcd of the M_c(t) over F_p.
//
// Usage: bmd_cube_boundary_minors p n d P u_1..u_n v_1..v_n   (p prime, P <= p, P > every deg M_c)
// Output: "degMN D degg G" followed by "name:multiplicity" for the roots of g where the line meets
// y_i = 0 and y_i = y_j, and "rest:R" for the remaining degree of g; then "|" and the same for M_N.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstdint>
typedef long long ll;
static ll P;
static ll md(ll a) { a %= P; return a < 0 ? a + P : a; }
static ll pw(ll b, ll e) { ll r = 1; b = md(b); while (e) { if (e & 1) r = r * b % P; b = b * b % P; e >>= 1; } return r; }

static ll det(std::vector<std::vector<ll>> a) {
    int n = (int)a.size(); ll d = 1;
    for (int c = 0; c < n; ++c) {
        int piv = -1;
        for (int i = c; i < n; ++i) if (a[i][c]) { piv = i; break; }
        if (piv < 0) return 0;
        if (piv != c) { std::swap(a[piv], a[c]); d = md(-d); }
        d = d * a[c][c] % P;
        ll iv = pw(a[c][c], P - 2);
        for (int i = c + 1; i < n; ++i) if (a[i][c]) {
            ll f = a[i][c] * iv % P;
            for (int j = c; j < n; ++j) a[i][j] = md(a[i][j] - f * a[c][j]);
        }
    }
    return d;
}

int main(int argc, char** argv) {
    if (argc < 5) { std::fprintf(stderr, "usage: p n d P u.. v..\n"); return 2; }
    P = std::atoll(argv[1]); int n = std::atoi(argv[2]), d = std::atoi(argv[3]); ll npts = std::atoll(argv[4]);
    if (argc != 5 + 2 * n || npts > P) { std::fprintf(stderr, "bad arguments\n"); return 2; }
    std::vector<ll> u(n), v(n);
    for (int i = 0; i < n; ++i) { u[i] = md(std::atoll(argv[5 + i])); v[i] = md(std::atoll(argv[5 + n + i])); }
    // basis (Q, r)
    std::vector<std::pair<int, unsigned>> basis;
    for (int Q = 0; 2 * Q <= d; ++Q)
        for (unsigned r = 0; r < (1u << n); ++r)
            if (2 * Q + __builtin_popcount(r) <= d) basis.push_back({Q, r});
    int N = (int)basis.size(), M = N + 1;  // coefficients T^0..T^N
    // Catalan numbers mod P
    std::vector<ll> cat(M + 1); cat[0] = 1;
    for (int j = 1; j <= M; ++j) cat[j] = cat[j - 1] * md(2 * (2 * j - 1)) % P * pw(j + 1, P - 2) % P;
    std::vector<std::vector<ll>> vals(M, std::vector<ll>(npts));
    for (ll t = 0; t < npts; ++t) {
        std::vector<std::vector<ll>> z(n, std::vector<ll>(M, 0));
        for (int i = 0; i < n; ++i) {
            ll y = md(u[i] + t * v[i]), yp = 1;
            for (int j = 1; j < M; ++j) { yp = yp * y % P; z[i][j] = md((j % 2 ? -1 : 1) * cat[j - 1] % P * yp); }
        }
        std::vector<std::vector<ll>> A(N, std::vector<ll>(M, 0));
        for (int b = 0; b < N; ++b) {
            std::vector<ll> s(M, 0); s[basis[b].first] = 1;
            for (int i = 0; i < n; ++i) if (basis[b].second >> i & 1) {
                std::vector<ll> o(M, 0);
                for (int a = 0; a < M; ++a) if (s[a]) for (int c = 1; a + c < M; ++c) o[a + c] = (o[a + c] + s[a] * z[i][c]) % P;
                s = o;
            }
            A[b] = s;
        }
        for (int c = 0; c < M; ++c) {
            std::vector<std::vector<ll>> B(N, std::vector<ll>(N));
            for (int b = 0; b < N; ++b) for (int j = 0, k = 0; j < M; ++j) if (j != c) B[b][k++] = A[b][j];
            vals[c][t] = det(B);
        }
    }
    // Newton interpolation at t = 0..npts-1, then expansion to monomial coefficients
    auto interp = [&](const std::vector<ll>& ys) {
        int m = (int)ys.size();
        std::vector<ll> cf(ys);
        for (int j = 1; j < m; ++j)
            for (int i = m - 1; i >= j; --i) cf[i] = md(cf[i] - cf[i - 1]) * pw(i - (i - j), P - 2) % P;
        std::vector<ll> poly(1, 0);
        for (int i = m - 1; i >= 0; --i) {
            std::vector<ll> q(poly.size() + 1, 0);  // poly * (t - i)
            for (size_t a = 0; a < poly.size(); ++a) { q[a + 1] = (q[a + 1] + poly[a]) % P; q[a] = md(q[a] - poly[a] * i); }
            q[0] = (q[0] + cf[i]) % P;
            poly = q;
        }
        while (poly.size() > 1 && poly.back() == 0) poly.pop_back();
        return poly;
    };
    auto pmod = [&](std::vector<ll> a, const std::vector<ll>& b) {
        ll iv = pw(b.back(), P - 2);
        while (a.size() >= b.size()) {
            ll f = a.back() * iv % P; size_t s0 = a.size() - b.size();
            for (size_t i = 0; i < b.size(); ++i) a[s0 + i] = md(a[s0 + i] - f * b[i]);
            while (a.size() > 1 && a.back() == 0) a.pop_back();
            if (a.size() == 1 && a[0] == 0) break;
            if (a.size() < b.size()) break;
        }
        return a;
    };
    auto iszero = [](const std::vector<ll>& a) { return a.size() == 1 && a[0] == 0; };
    std::vector<std::vector<ll>> polys(M);
    for (int c = 0; c < M; ++c) polys[c] = interp(vals[c]);
    for (int c = 0; c < M; ++c) if ((ll)polys[c].size() >= npts) { std::fprintf(stderr, "too few points\n"); return 3; }
    std::vector<ll> g = polys[0];
    for (int c = 1; c < M; ++c) {
        std::vector<ll> a = g, b = polys[c];
        if (iszero(b)) continue;
        if (iszero(a)) { g = b; continue; }
        while (!iszero(b)) { std::vector<ll> r = pmod(a, b); a = b; b = r; }
        g = a;
    }
    auto mult = [&](std::vector<ll> f, ll root) {
        int k = 0;
        while (f.size() > 1) {
            std::vector<ll> q(f.size() - 1); ll acc = 0;
            for (int i = (int)f.size() - 1; i >= 0; --i) { acc = (acc * root + f[i]) % P; if (i > 0) q[i - 1] = acc; }
            if (acc) break;
            f = q; ++k;
        }
        return k;
    };
    int degMN = (int)polys[N].size() - 1, degg = (int)g.size() - 1, used = 0;
    std::printf("degMN %d degg %d", degMN, degg);
    for (int i = 0; i < n; ++i) {
        ll r = md(-u[i]) * pw(v[i], P - 2) % P; int k = mult(g, r); used += k;
        std::printf(" y%d:%d", i + 1, k);
    }
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
        ll r = md(u[j] - u[i]) * pw(md(v[i] - v[j]), P - 2) % P; int k = mult(g, r); used += k;
        std::printf(" y%d-y%d:%d", i + 1, j + 1, k);
    }
    std::printf(" rest:%d |", degg - used);
    // the same multiplicities in M_N = +-Delta_{n,d}
    std::vector<ll> D = polys[N]; int usedD = 0;
    for (int i = 0; i < n; ++i) { ll r = md(-u[i]) * pw(v[i], P - 2) % P; int k = mult(D, r); usedD += k; std::printf(" D:y%d:%d", i + 1, k); }
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
        ll r = md(u[j] - u[i]) * pw(md(v[i] - v[j]), P - 2) % P; int k = mult(D, r); usedD += k;
        std::printf(" D:y%d-y%d:%d", i + 1, j + 1, k);
    }
    std::printf(" D:rest:%d\n", degMN - usedD);
    return 0;
}
