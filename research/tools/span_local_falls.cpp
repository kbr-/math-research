// Span-local falls (entry-2026-09-27-span-local-test).
//
// Statement tested: the semantic form of conj:span-local-generation on the Boolean cube model of
// fall_degree.cpp (research/results/odd_prime_fall_degree_kernel_20260926): for randomized-prefix members
// P_1..P_M (h forms each, t random prefix rows; the first `share` forms of every block have the same linear
// part, each block with its own constants), in degrees d with H(d) = sum_{i<=d} C(N,i) below |cap P|/2, the
// top ideal gr I(cap_b P_b)_d equals sum over unions S of at most s members of gr I(cap_{b in S} P_b)_d for
// small s.  Printed per degree d: H(d)/|cap P| and excess_s(d) = dim gr I(cap P)_d - dim sum_{|S|<=s} gr I(P_S)_d
// for s = 1..smax.  Exact ranks mod 3 (FLINT), as in fall_degree.cpp.
// Usage: span_local_falls "N h t M share smax dmax seed [chain]; ..." (one JSON line per case).  With chain = 1
// (entry-2026-09-27-chain-falls) share is ignored and member b's form 0 has the linear part of member b-1's form 1,
// a chain of shared pieces along the members.
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <string>
#include <sstream>
using namespace std;
typedef vector<int> VI;
int N;
vector<unsigned> mons; vector<int> degStart;
static int popc(unsigned x){ return __builtin_popcount(x); }
static long binom(int n, int k){ long r=1; for(int i=1;i<=k;i++) r = r*(n-k+i)/i; return r; }
static nmod_mat_t* evalMat(const vector<unsigned>& pts, int d) {
    int cols = degStart[d+1];
    nmod_mat_t* A = new nmod_mat_t[1]; nmod_mat_init(*A, pts.size(), cols, 3);
    for (size_t r = 0; r < pts.size(); r++)
        for (int c = 0; c < cols; c++) nmod_mat_entry(*A, r, c) = ((mons[c] & pts[r]) == mons[c]) ? 1 : 0;
    return A;
}
static long rankOn(const vector<unsigned>& pts, int d) {
    if (d < 0 || pts.empty()) return 0;
    nmod_mat_t* A = evalMat(pts, d); long r = nmod_mat_rank(*A); nmod_mat_clear(*A); delete[] A; return r;
}
static void topParts(const vector<unsigned>& pts, int d, vector<VI>& acc) {   // degree-d parts of ker(E_{<=d} on pts)
    int cols = degStart[d+1];
    if (pts.empty()) { for (int c = degStart[d]; c < cols; c++) { VI v(cols - degStart[d]); v[c - degStart[d]] = 1; acc.push_back(v); } return; }
    nmod_mat_t* A = evalMat(pts, d);
    nmod_mat_t X; nmod_mat_init(X, cols, cols, 3);
    long k = nmod_mat_nullspace(X, *A);
    for (long j = 0; j < k; j++) {
        VI v(cols - degStart[d]); bool nz = false;
        for (int c = degStart[d]; c < cols; c++) { v[c - degStart[d]] = nmod_mat_entry(X, c, j); if (v[c - degStart[d]]) nz = true; }
        if (nz) acc.push_back(v);
    }
    nmod_mat_clear(X); nmod_mat_clear(*A); delete[] A;
}
static long rankRows(const vector<VI>& rows, int width) {
    if (rows.empty()) return 0;
    nmod_mat_t B; nmod_mat_init(B, rows.size(), width, 3);
    for (size_t r = 0; r < rows.size(); r++) for (int c = 0; c < width; c++) nmod_mat_entry(B, r, c) = rows[r][c];
    long rk = nmod_mat_rank(B); nmod_mat_clear(B); return rk;
}
static int runCase(int N_, int h, int t, int M, int share, int smax, int dmax, unsigned seed, int chain) {
    N = N_; mons.clear(); degStart.clear();
    if (N > 14 || M > 16 || smax > 4 || share > h) { fprintf(stderr, "refusing oversized case\n"); return 2; }
    for (int d = 0; d <= N; d++) { degStart.push_back(mons.size()); for (unsigned m = 0; m < (1u<<N); m++) if (popc(m)==d) mons.push_back(m); }
    degStart.push_back(mons.size());
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    vector<VI> sharedLin(share, VI(N)); for (auto& row: sharedLin) for (auto& a: row) a = u3(rng);
    vector<vector<char>> in(M, vector<char>(1u<<N, 0));
    if (chain && h < 2) { fprintf(stderr, "chain needs h >= 2\n"); return 2; }
    VI prevLin(N);
    for (int b = 0; b < M; b++) {
        vector<VI> A(h, VI(N+1)); for (auto& row: A) for (auto& a: row) a = u3(rng);
        if (!chain) for (int i = 0; i < share; i++) for (int j = 0; j < N; j++) A[i][j] = sharedLin[i][j];   // shared linear part, own constant
        if (chain && b > 0) for (int j = 0; j < N; j++) A[0][j] = prevLin[j];   // form 0 shares the linear part of b-1's form 1
        for (int j = 0; j < N; j++) prevLin[j] = A[1][j];
        vector<VI> C(t, VI(h)); for (auto& row: C) for (auto& a: row) a = u3(rng);
        for (unsigned x = 0; x < (1u<<N); x++) {
            VI g(h); bool any = false;
            for (int i = 0; i < h; i++) { int L = A[i][N]; for (int j=0;j<N;j++) if (x>>j&1) L += A[i][j]; g[i] = (L%3==0); any |= g[i]; }
            bool ok = !any;
            for (int j = 0; j < t && !ok; j++) { int s=0; for (int i=0;i<h;i++) s += C[j][i]*g[i]; if (s%3) ok = true; }
            in[b][x] = ok;
        }
    }
    auto ptsOf = [&](unsigned mask) { vector<unsigned> p; for (unsigned x=0;x<(1u<<N);x++){ bool ok=true; for(int b=0;b<M&&ok;b++) if (mask>>b&1) ok = in[b][x]; if(ok) p.push_back(x);} return p; };
    unsigned full = (1u<<M) - 1;
    vector<unsigned> PI = ptsOf(full);
    vector<vector<unsigned>> subsets(smax+1);
    for (unsigned mask = 1; mask < (1u<<M); mask++) { int c = popc(mask); if (c <= smax) subsets[c].push_back(mask); }
    vector<vector<vector<unsigned>>> subPts(smax+1);
    for (int s = 1; s <= smax; s++) for (unsigned mask: subsets[s]) subPts[s].push_back(ptsOf(mask));
    char head[200]; snprintf(head, sizeof head, "{\"N\": %d, \"h\": %d, \"t\": %d, \"M\": %d, \"share\": %d, \"chain\": %d, \"seed\": %u, \"capP\": %zu, \"degrees\": [", N,h,t,M,share,chain,seed,PI.size());
    string line(head);
    long prev = rankOn(PI, 0);
    for (int d = 1; d <= dmax; d++) {
        long rd = rankOn(PI, d); long grIdeal = binom(N,d) - (rd - prev); prev = rd;
        long H = 0; for (int i = 0; i <= d; i++) H += binom(N,i);
        char buf[160]; snprintf(buf, sizeof buf, "%s{\"d\": %d, \"H_over_cap\": %.3f, \"gr_ideal\": %ld, \"excess\": [", d==1?"":", ", d, PI.empty()?0.0:H/double(PI.size()), grIdeal);
        line += buf;
        vector<VI> acc;
        for (int s = 1; s <= smax; s++) {
            for (auto& p: subPts[s]) topParts(p, d, acc);
            long sumDim = rankRows(acc, degStart[d+1]-degStart[d]);
            line += (s==1?"":", ") + to_string(grIdeal - sumDim);
        }
        line += "]}";
    }
    line += "]}\n";
    fputs(line.c_str(), stdout); fflush(stdout);
    return 0;
}
int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "usage: span_local_falls \"N h t M share smax dmax seed; ...\"\n"); return 2; }
    std::stringstream all(argv[1]); std::string item;
    while (std::getline(all, item, ';')) {
        std::stringstream ss(item); int N_, h, t, M, share, smax, dmax; unsigned seed; int chain = 0;
        if (!(ss >> N_ >> h >> t >> M >> share >> smax >> dmax >> seed)) continue;
        ss >> chain;
        if (runCase(N_, h, t, M, share, smax, dmax, seed, chain)) return 2;
    }
    return 0;
}
