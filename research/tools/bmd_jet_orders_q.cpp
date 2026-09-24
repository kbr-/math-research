// Exact per-order minimum degrees on the full grid F_p^n (p prime), via origin jets.
//
// Statement computed.  delta_p(n,k,l) is the least total degree of a formal polynomial P over F_p
// with Hasse multiplicity >= k at every nonzero point of F_p^n and exactly l at the origin.
//
// Reduction (as in bmd_jet_orders.cpp, with y_i = x_i^p - x_i).  Polynomials expand uniquely as
// sum c x^eps y^e with 0 <= eps_i < p, of degree max(|eps| + p|e|).  Terms with |e| >= k lie in
// (y)^k, inside every m_a^k; the span of the terms with |e| < k maps isomorphically onto the product
// of the jet spaces (CRT, dimension p^n C(n+k-1,n)).  Admissible P correspond to origin jets v via
// P(v) = T(sum_beta v_beta prod_i g_{beta_i}(x_i)), g_b = x^b (1 - x^((p-1) p^K)), p^K >= k, which is
// x^b mod x^k and vanishes to order p^K at every nonzero a.  One leftmost-pivot elimination with
// columns in descending |beta| and rows in descending degree gives delta_p(n,k,l) for every l.
//
// Usage: bmd_jet_orders_q p n k [--out PATH]
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>

static int P;
static int md(long a) { a %= P; return a < 0 ? a + P : a; }
static int inv(int a) { for (int b = 1; b < P; ++b) if (a * b % P == 1) return b; return 0; }

// f = sum_j (sum_{eps<p} T[eps][j] x^eps) y^j, y = x^p - x; returns T[eps][j] for j < jmax.
static void ybasis(std::vector<int> f, std::vector<std::vector<int>>& T, int jmax) {
    T.assign(P, std::vector<int>(jmax, 0));
    for (int j = 0; ; ++j) {
        while (!f.empty() && f.back() == 0) f.pop_back();
        if (f.empty()) break;
        // divide f by the monic y = x^p - x: f = quot * y + rem, deg rem < p
        std::vector<int> quot(f.size() > (size_t)P ? f.size() - P : 0, 0);
        for (int d = (int)f.size() - 1; d >= P; --d) {
            int c = f[d];
            if (!c) continue;
            quot[d - P] = c;
            f[d] = 0;
            f[d - P + 1] = md(f[d - P + 1] + c);  // subtract c x^(d-p) (x^p - x): adds c x^(d-p+1)
        }
        if (j < jmax) for (int e = 0; e < P && e < (int)f.size(); ++e) T[e][j] = f[e];
        f = quot;
    }
}

int main(int argc, char** argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: bmd_jet_orders_q p n k [--out PATH]\n"); return 2; }
    P = std::atoi(argv[1]); int n = std::atoi(argv[2]), k = std::atoi(argv[3]);
    std::string out;
    for (int i = 4; i < argc; ++i) if (!std::strcmp(argv[i], "--out") && i + 1 < argc) out = argv[++i];
    auto t0 = std::chrono::steady_clock::now();
    long pK = 1; while (pK < k) pK *= P;
    std::vector<std::vector<std::vector<int>>> T(k);  // T[b][eps][j]
    for (int b = 0; b < k; ++b) {
        long top = b + (P - 1) * pK;
        std::vector<int> f(top + 1, 0);
        f[b] = 1; f[top] = md(-1);
        ybasis(f, T[b], k);
    }
    std::vector<std::vector<int>> cols, es;
    { std::vector<int> cur(n, 0);
      struct R { static void go(int i, int left, int n, std::vector<int>& cur, std::vector<std::vector<int>>& o) {
          if (i == n) { o.push_back(cur); return; }
          for (int e = 0; e <= left; ++e) { cur[i] = e; go(i + 1, left - e, n, cur, o); } cur[i] = 0; } };
      R::go(0, k - 1, n, cur, cols); es = cols; }
    std::stable_sort(cols.begin(), cols.end(), [](const std::vector<int>& a, const std::vector<int>& b) {
        int sa = 0, sb = 0; for (int x : a) sa += x; for (int x : b) sb += x; return sa > sb; });
    long C = cols.size();
    std::vector<int> lev(C); std::vector<long> N(k, 0);
    for (long c = 0; c < C; ++c) { int s = 0; for (int x : cols[c]) s += x; lev[c] = s; N[s]++; }
    long npow = 1; for (int i = 0; i < n; ++i) npow *= P;
    int maxdeg = n * (P - 1) + P * (k - 1);
    std::vector<long> pivrow(C, -1);
    std::vector<std::vector<uint8_t>> basis;
    std::vector<long> pivcount(k, 0);
    std::vector<int> delta(k, -1);
    int remaining = k; long rowsUsed = 0;
    for (int D = maxdeg; D >= 0 && remaining > 0; --D) {
        for (long epsId = 0; epsId < npow; ++epsId) {
            std::vector<int> eps(n); long t = epsId; int pe = 0;
            for (int i = 0; i < n; ++i) { eps[i] = t % P; t /= P; pe += eps[i]; }
            if ((D - pe) % P != 0 || D - pe < 0) continue;
            int se = (D - pe) / P;
            for (const auto& e : es) {
                int s = 0; for (int x : e) s += x;
                if (s != se) continue;
                std::vector<uint8_t> row(C);
                for (long c = 0; c < C; ++c) {
                    long v = 1;
                    for (int i = 0; i < n && v; ++i) v = v * T[cols[c][i]][eps[i]][e[i]] % P;
                    row[c] = v;
                }
                ++rowsUsed;
                long lead = -1;
                for (long c = 0; c < C; ++c) {
                    if (!row[c]) continue;
                    if (pivrow[c] < 0) { lead = c; break; }
                    const auto& br = basis[pivrow[c]];
                    int f = row[c];  // basis rows are normalized to leading 1
                    for (long d = c; d < C; ++d) if (br[d]) row[d] = md(row[d] - f * br[d]);
                }
                if (lead < 0) continue;
                int iv = inv(row[lead]);
                for (long d = lead; d < C; ++d) row[d] = row[d] * iv % P;
                pivrow[lead] = basis.size();
                basis.push_back(row);
                pivcount[lev[lead]]++;
            }
        }
        for (int l = 0; l < k; ++l)
            if (delta[l] < 0 && !(pivcount[l] < N[l])) { delta[l] = D; --remaining; }
    }
    double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::string js = "{\"p\": " + std::to_string(P) + ", \"n\": " + std::to_string(n) + ", \"k\": " + std::to_string(k) +
        ", \"columns\": " + std::to_string(C) + ", \"rows_used\": " + std::to_string(rowsUsed) +
        ", \"seconds\": " + std::to_string(secs) + ", \"delta\": [";
    for (int l = 0; l < k; ++l) js += (l ? ", " : "") + std::to_string(delta[l]);
    js += "]}\n";
    if (!out.empty()) { FILE* f = std::fopen(out.c_str(), "w"); std::fputs(js.c_str(), f); std::fclose(f); }
    std::fputs(js.c_str(), stdout);
    return 0;
}
