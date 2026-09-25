// Local zero scheme of the 3-cube's threshold ideal at a point (lem:cube-threshold-zero-scheme).
//
// Statement computed.  On {0,1}^3 (characteristic p != 2), E_m is the sheaf of solutions W of the
// constraint system sum_c W_c [T^c](T^Q z^r) = 0 for the basis T^Q z^r (2Q+|r| <= d) of V_{3,d},
// z_i = r_0(y_i T) = sum_{j>=1} (-1)^j C_{j-1} y_i^j T^j.  For rho = m+1-4d >= 2 the image of
// W -> W_m is J_Z, the ideal sheaf of a zero-dimensional scheme Z.  This program computes the
// stalk J_{Z,P} = {W_m : W local solution at P} modulo m_P^K at a point P, in local coordinates
// (s,t) with y_i = b_i + es_i s + et_i t (a chart: one y fixed to a nonzero constant).
//
// Method.  Local solutions are approximated by solutions modulo m_P^N (N > K); by Artin-Rees the
// image of W_m modulo m_P^K is exact once N - K is large enough, which the caller checks by
// comparing two values of N.  The linear system over F_p has unknowns W_{c,e} (c = 0..m, monomial
// e of degree < N) and one equation per basis element and monomial of degree < N.  Columns are
// ordered: every W_c with c < m and W_m in degrees >= K first, then W_m in degrees K-1, ..., 0.
// One forward elimination then gives, for every K' <= K, dim of the image of W_m modulo m^K'
// (= |S_K'| - rank M + rank of M without S_K'), and the echelon rows restricted to S_K, whose
// common kernel is the image modulo m^K (they are written to OUT for the alpha computation).
//
// Lifts.  Optional arguments "i:0" (divisor y_i = 0) and "i:j" (divisor y_i = y_j), 1-based, add the
// collision lifts along those divisors (lem:cube-collision-lifts; the diagonal ones through the Mobius
// transport of thm:cube-dimension-three-boundary-threshold).  The lifts lie in the saturation of the
// lattice, so the annihilator (the stalk of E_m) is unchanged, while the lattice becomes saturated in
// codimension one near P and the truncation margin N - K needed for exactness drops.
//
// Mode "all": the dimensions printed are those of the jets of all coordinates W_c (not only W_m).
//
// Usage: bmd_cube_point_scheme p d m N K b1 b2 b3 es1 es2 es3 et1 et2 et3 OUT [i:0 | i:j ... | all]
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <omp.h>
using namespace std;
typedef uint64_t u64;
static u64 P;
static u64 pw(u64 a, u64 e) { u64 r = 1; a %= P; while (e) { if (e & 1) r = r * a % P; a = a * a % P; e >>= 1; } return r; }

int N;                        // truncation: monomials s^a t^b with a+b < N
vector<int> midx;             // index of (a,b) -> position, graded by total degree
int nm;
int id(int a, int b) { return midx[a * N + b]; }
vector<pair<int,int>> mono;

typedef vector<u64> Bi;       // bivariate polynomial truncated at total degree < N
Bi bmul(const Bi &x, const Bi &y) {
    Bi z(nm, 0);
    for (int i = 0; i < nm; i++) if (x[i]) {
        int a = mono[i].first, b = mono[i].second;
        for (int j = 0; j < nm; j++) if (y[j]) {
            int a2 = a + mono[j].first, b2 = b + mono[j].second;
            if (a2 + b2 >= N) continue;
            int k = id(a2, b2);
            z[k] = (z[k] + x[i] * y[j]) % P;
        }
    }
    return z;
}

int main(int argc, char **argv) {
    if (argc < 16) { fprintf(stderr, "usage: p d m N K b1 b2 b3 es1 es2 es3 et1 et2 et3 OUT [i:0 | i:j ...]\n"); return 2; }
    P = atoll(argv[1]); int d = atoi(argv[2]), m = atoi(argv[3]); N = atoi(argv[4]); int K = atoi(argv[5]);
    long long b[3], es[3], et[3];
    for (int i = 0; i < 3; i++) { b[i] = atoll(argv[6 + i]); es[i] = atoll(argv[9 + i]); et[i] = atoll(argv[12 + i]); }
    const char *out = argv[15];
    if (P % 2 == 0 || K >= N || m + 1 - 4 * d < 1) { fprintf(stderr, "need odd p, K < N, rho >= 1\n"); return 2; }
    // Catalan numbers, binomial series and Psi_k divide by j+1 <= m+2 through Fermat inverses.
    if (P <= (u64)m + 2) { fprintf(stderr, "need p > m + 2 (inverses of 1..m+2)\n"); return 2; }
    midx.assign(N * N, -1);
    for (int deg = 0; deg < N; deg++) for (int a = deg; a >= 0; a--) { midx[a * N + (deg - a)] = mono.size(); mono.push_back({a, deg - a}); }
    nm = mono.size();
    // kappa_j = (-1)^j C_{j-1} mod P
    vector<u64> kap(m + 2, 0), cat(m + 2, 0);
    cat[0] = 1;
    for (int j = 1; j <= m + 1; j++) cat[j] = cat[j - 1] * 2 % P * ((2 * j - 1) % P) % P * pw(j + 1, P - 2) % P;
    for (int j = 1; j <= m + 1; j++) kap[j] = (j % 2) ? (P - cat[j - 1]) % P : cat[j - 1];
    // y_i as bivariate polynomials and z_i coefficients Zc[i][j] = kappa_j y_i^j
    vector<vector<Bi>> Zc(3, vector<Bi>(m + 1, Bi(nm, 0)));
    for (int i = 0; i < 3; i++) {
        Bi y(nm, 0);
        y[id(0, 0)] = ((b[i] % (long long)P) + P) % P;
        if (N > 1) { y[id(1, 0)] = ((es[i] % (long long)P) + P) % P; y[id(0, 1)] = ((et[i] % (long long)P) + P) % P; }
        Bi yp(nm, 0); yp[id(0, 0)] = 1;
        for (int j = 1; j <= m; j++) {
            yp = bmul(yp, y);
            for (int k = 0; k < nm; k++) Zc[i][j][k] = kap[j] * yp[k] % P;
        }
    }
    // ---- T-series with bivariate coefficients (length m+1) ----
    typedef vector<Bi> Ser;
    auto zero = [&]() { return Ser(m + 1, Bi(nm, 0)); };
    auto smul = [&](const Ser &x, const Ser &y) {
        Ser z = zero();
        #pragma omp parallel for schedule(dynamic)
        for (int c = 0; c <= m; c++)
            for (int j = 0; j <= c; j++) {
                bool nx = false, ny = false;
                for (int k = 0; k < nm && !nx; k++) nx = x[j][k];
                if (!nx) continue;
                for (int k = 0; k < nm && !ny; k++) ny = y[c - j][k];
                if (!ny) continue;
                Bi pr = bmul(x[j], y[c - j]);
                for (int k = 0; k < nm; k++) z[c][k] = (z[c][k] + pr[k]) % P;
            }
        return z;
    };
    vector<Bi> Y(3, Bi(nm, 0));
    for (int i = 0; i < 3; i++) {
        Y[i][id(0, 0)] = ((b[i] % (long long)P) + P) % P;
        if (N > 1) { Y[i][id(1, 0)] = ((es[i] % (long long)P) + P) % P; Y[i][id(0, 1)] = ((et[i] % (long long)P) + P) % P; }
    }
    // (1 + 4 y_i T)^e for rational exponent e = num/2: coefficient binom(e, j) (4 y_i)^j
    auto binser = [&](int i, long long num) {
        Ser S = zero();
        u64 half = pw(2, P - 2), e = ((num % (long long)P + (long long)P) % P) * half % P, cb = 1;
        Bi yp(nm, 0); yp[id(0, 0)] = 1;
        Bi y4(nm); for (int k = 0; k < nm; k++) y4[k] = 4 * Y[i][k] % P;
        for (int j = 0; j <= m; j++) {
            for (int k = 0; k < nm; k++) S[j][k] = cb * yp[k] % P;
            cb = cb * ((e + P - j) % P) % P * pw(j + 1, P - 2) % P;
            yp = bmul(yp, y4);
        }
        return S;
    };
    auto one = [&]() { Ser S = zero(); S[0][id(0, 0)] = 1; return S; };
    auto Tpow = [&](int Q) { Ser S = zero(); if (Q <= m) S[Q][id(0, 0)] = 1; return S; };
    auto zser = [&](int i) { Ser S = zero(); for (int j = 1; j <= m; j++) S[j] = Zc[i][j]; return S; };
    auto half_one_minus = [&](const Ser &w) {  // (1 - w)/2
        Ser S = zero(); u64 half = pw(2, P - 2);
        for (int j = 0; j <= m; j++) for (int k = 0; k < nm; k++) S[j][k] = (P - w[j][k]) % P * half % P;
        S[0][id(0, 0)] = (S[0][id(0, 0)] + half) % P;
        return S;
    };
    // Psi_k(U) = A_k(U) + (1 + B_k(U)) r_0(U): the element of order exactly k in
    // span{U^b (2b <= k), U^b r_0 (2b+1 <= k)}, r_0-coefficient at U^0 equal to 1; coefficients psi_j, j <= m
    auto psi = [&](int k) {
        vector<vector<u64>> gens;  // series in U up to degree m
        vector<u64> r0(m + 1, 0); for (int j = 1; j <= m; j++) r0[j] = kap[j];
        for (int bb = 1; 2 * bb <= k; bb++) { vector<u64> g(m + 1, 0); if (bb <= m) g[bb] = 1; gens.push_back(g); }
        for (int bb = 1; 2 * bb + 1 <= k; bb++) { vector<u64> g(m + 1, 0); for (int j = 0; j + bb <= m; j++) g[j + bb] = r0[j]; gens.push_back(g); }
        // solve r0 + sum x_g g = O(U^k): equations at U^0..U^{k-1}
        int ng = gens.size();
        vector<vector<u64>> E(k, vector<u64>(ng + 1, 0));
        for (int j = 0; j < k; j++) { for (int g = 0; g < ng; g++) E[j][g] = gens[g][j]; E[j][ng] = (P - r0[j]) % P; }
        vector<int> where(ng, -1); int r = 0;
        for (int c = 0; c < ng && r < k; c++) {
            int pv = -1; for (int i = r; i < k; i++) if (E[i][c]) { pv = i; break; }
            if (pv < 0) continue;
            swap(E[pv], E[r]); u64 iv = pw(E[r][c], P - 2);
            for (int j = 0; j <= ng; j++) E[r][j] = E[r][j] * iv % P;
            for (int i = 0; i < k; i++) if (i != r && E[i][c]) { u64 f = E[i][c]; for (int j = 0; j <= ng; j++) E[i][j] = (E[i][j] + (P - f) * E[r][j]) % P; }
            where[c] = r; r++;
        }
        for (int i = r; i < k; i++) if (E[i][ng]) { fprintf(stderr, "Psi_%d: inconsistent\n", k); exit(3); }
        vector<u64> ps = r0;
        for (int g = 0; g < ng; g++) if (where[g] >= 0) for (int j = 0; j <= m; j++) ps[j] = (ps[j] + E[where[g]][ng] * gens[g][j]) % P;
        for (int j = 0; j < k; j++) if (ps[j]) { fprintf(stderr, "Psi_%d: order < k\n", k); exit(3); }
        if (k <= m && !ps[k]) { fprintf(stderr, "Psi_%d: order > k\n", k); exit(3); }
        return ps;
    };
    // generators: rows A[f] (T-series)
    vector<Ser> A;
    for (int Q = 0; 2 * Q <= d; Q++) for (int r = 0; r < 8; r++) {
        if (2 * Q + __builtin_popcount(r) > d) continue;
        Ser S = Tpow(Q);
        for (int i = 0; i < 3; i++) if (r >> i & 1) S = smul(S, zser(i));
        A.push_back(S);
    }
    if ((int)A.size() != 4 * d) { fprintf(stderr, "basis size %zu != 4d\n", A.size()); return 3; }
    // collision lifts along the divisors through the point (lem:cube-collision-lifts, Mobius transport)
    for (int a = 16; a < argc; a++) {
        if (string(argv[a]) == "all") continue;
        int i = argv[a][0] - '1', j = (argv[a][2] == '0') ? -1 : argv[a][2] - '1';
        int o[2], no = 0; for (int x = 0; x < 3; x++) if (x != i && x != j) o[no++] = x;
        if (j < 0) {
            // y_i = 0: L = P' * sum_{l>=k} psi_l y_i^{l-k} T^l, P' = T^Q z_o0^r0 z_o1^r1, weight e <= d-1
            for (int Q = 0; 2 * Q <= d - 1; Q++) for (int r = 0; r < 4; r++) {
                int e = 2 * Q + __builtin_popcount(r); if (e > d - 1) continue;
                int k = d - e; vector<u64> ps = psi(k);
                Ser S = Tpow(Q);
                for (int x = 0; x < 2; x++) if (r >> x & 1) S = smul(S, zser(o[x]));
                Ser L = zero(); Bi yp(nm, 0); yp[id(0, 0)] = 1;
                for (int l = k; l <= m; l++) { for (int t = 0; t < nm; t++) L[l][t] = ps[l] * yp[t] % P; yp = bmul(yp, Y[i]); }
                A.push_back(smul(S, L));
            }
        } else {
            // y_i = y_j, Mobius frame T~ = T/(1+4 y_j T): slot i has y~_i = y_i - y_j, slot j has y~_j = -y_j,
            // slot o (third) has y~ = y_o - y_j; w~_i = w_i/w_j, w~_j = 1/w_j, w~_o = w_o/w_j.
            // Lift L~ = P~' * sum_l psi_l y~_i^{l-k} T~^l with P~' = T~^Q z~_j^{rj} z~_o^{ro}, mapped back by * w_j^d.
            int o3 = o[0];
            Ser wj = binser(j, 1), wjinv = binser(j, -1), wo = binser(o3, 1);
            Ser Tt = smul(Tpow(1), smul(wjinv, wjinv));
            Ser zj = half_one_minus(wjinv), zo = half_one_minus(smul(wo, wjinv));
            Ser wjd = one(); for (int x = 0; x < d; x++) wjd = smul(wjd, wj);
            Bi yti(nm); for (int t = 0; t < nm; t++) yti[t] = (Y[i][t] + P - Y[j][t]) % P;
            vector<Ser> Ttp(m + 1); Ttp[0] = one(); for (int l = 1; l <= m; l++) Ttp[l] = smul(Ttp[l - 1], Tt);
            for (int Q = 0; 2 * Q <= d - 1; Q++) for (int r = 0; r < 4; r++) {
                int e = 2 * Q + __builtin_popcount(r); if (e > d - 1) continue;
                int k = d - e; vector<u64> ps = psi(k);
                Ser S = smul(wjd, Ttp[Q]);
                if (r & 1) S = smul(S, zj);
                if (r & 2) S = smul(S, zo);
                Ser L = zero(); Bi yp(nm, 0); yp[id(0, 0)] = 1;
                for (int l = k; l <= m; l++) {
                    for (int c = 0; c <= m; c++) { Bi pr = bmul(Ttp[l][c], yp); for (int t = 0; t < nm; t++) L[c][t] = (L[c][t] + ps[l] * pr[t]) % P; }
                    yp = bmul(yp, yti);
                }
                A.push_back(smul(S, L));
            }
        }
    }
    int nf = A.size();
    fprintf(stderr, "generators: %d (4d = %d)\n", nf, 4 * d);
    // column order
    // Default: S = the jets of W_m below degree K.  Mode "all" (an argument "all" after OUT): S = the
    // jets of every coordinate W_c below degree K, so the printed dimensions are those of the image of
    // the truncated local solutions in (F[s,t]/m^K')^(m+1).
    bool allmode = false;
    for (int ai = 16; ai < argc; ai++) if (string(argv[ai]) == "all") allmode = true;
    vector<int> colc, cole;  // (c, monomial index)
    int cmin = allmode ? 0 : m;
    for (int c = 0; c < cmin; c++) for (int e = 0; e < nm; e++) { colc.push_back(c); cole.push_back(e); }
    for (int c = cmin; c <= m; c++) for (int e = 0; e < nm; e++) if (mono[e].first + mono[e].second >= K) { colc.push_back(c); cole.push_back(e); }
    int nrest = colc.size();
    vector<int> sdeg;  // degree of each S column, in order K-1 down to 0
    for (int deg = K - 1; deg >= 0; deg--) for (int c = cmin; c <= m; c++) for (int e = 0; e < nm; e++) if (mono[e].first + mono[e].second == deg) { colc.push_back(c); cole.push_back(e); sdeg.push_back(deg); }
    int ncol = colc.size(), nrow = nf * nm;
    vector<int> colpos((m + 1) * nm);
    for (int j = 0; j < ncol; j++) colpos[colc[j] * nm + cole[j]] = j;
    vector<uint32_t> M((size_t)nrow * ncol, 0);
    #pragma omp parallel for schedule(dynamic)
    for (int f = 0; f < nf; f++)
        for (int e = 0; e < nm; e++) {
            size_t row = (size_t)(f * nm + e) * ncol;
            int a = mono[e].first, bb = mono[e].second;
            for (int e2 = 0; e2 < nm; e2++) {      // unknown monomial e2, matrix monomial e - e2
                int a2 = mono[e2].first, b2 = mono[e2].second;
                if (a2 > a || b2 > bb) continue;
                int k = id(a - a2, bb - b2);
                for (int c = 0; c <= m; c++) {
                    u64 v = A[f][c][k];
                    if (v) M[row + colpos[c * nm + e2]] = v;
                }
            }
        }
    // forward elimination in column order
    int rk = 0; vector<int> pivcol;
    int rank_rest = -1;
    vector<int> rank_after(ncol + 1, 0);
    for (int col = 0; col < ncol; col++) {
        if (col == nrest) rank_rest = rk;
        int piv = -1;
        for (int i = rk; i < nrow; i++) if (M[(size_t)i * ncol + col]) { piv = i; break; }
        if (piv >= 0) {
            if (piv != rk) for (int j = col; j < ncol; j++) swap(M[(size_t)piv * ncol + j], M[(size_t)rk * ncol + j]);
            u64 inv = pw(M[(size_t)rk * ncol + col], P - 2);
            for (int j = col; j < ncol; j++) M[(size_t)rk * ncol + j] = M[(size_t)rk * ncol + j] * inv % P;
            const uint32_t *pr = &M[(size_t)rk * ncol];
            #pragma omp parallel for schedule(static)
            for (int i = rk + 1; i < nrow; i++) {
                uint32_t *ri = &M[(size_t)i * ncol];
                u64 fct = ri[col];
                if (!fct) continue;
                u64 nf2 = P - fct;
                for (int j = col; j < ncol; j++) if (pr[j]) ri[j] = (ri[j] + nf2 * pr[j]) % P;
            }
            pivcol.push_back(col);
            rk++;
        }
        rank_after[col + 1] = rk;
        if (col % 500 == 0) { fprintf(stderr, "col %d/%d rank %d\n", col, ncol, rk); fflush(stderr); }
    }
    if (rank_rest < 0) rank_rest = rk;
    printf("p=%llu d=%d m=%d N=%d K=%d point=(%lld,%lld,%lld) es=(%lld,%lld,%lld) et=(%lld,%lld,%lld): rows %d cols %d rank %d\n",
           (unsigned long long)P, d, m, N, K, b[0], b[1], b[2], es[0], es[1], es[2], et[0], et[1], et[2], nrow, ncol, rk);
    // for K' = 0..K: S_K' = W_m monomials of degree < K'; M without S_K' = prefix ending before degree K'-1 block
    for (int Kp = 0; Kp <= K; Kp++) {
        int sz = Kp * (Kp + 1) / 2 * (m + 1 - cmin);
        int prefix = nrest;
        for (size_t j = 0; j < sdeg.size(); j++) if (sdeg[j] >= Kp) prefix++;
        int rest_rank = rank_after[prefix];
        int img = sz - rk + rest_rank;
        printf("K'=%d: dim image of %s mod m^K' = %d, colength = %d\n", Kp, allmode ? "W" : "W_m", img, sz - img);
    }
    fflush(stdout);
    // echelon rows rank_rest..rk-1 restricted to S columns: their common kernel is the image mod m^K
    FILE *fo = fopen(out, "w");
    fprintf(fo, "# K=%d; S columns (a,b) for s^a t^b:", K);
    for (int j = nrest; j < ncol; j++) fprintf(fo, " %d,%d", mono[cole[j]].first, mono[cole[j]].second);
    fprintf(fo, "\n");
    for (int i = rank_rest; i < rk; i++) {
        for (int j = nrest; j < ncol; j++) fprintf(fo, "%u ", M[(size_t)i * ncol + j]);
        fprintf(fo, "\n");
    }
    fclose(fo);
    return 0;
}
