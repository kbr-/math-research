// Cross-member falls of randomized-prefix members on the Boolean cube, by evaluation ranks.
// Statement tested (member-universality follow-up): at fixed total excluded density spread over
// M members (h = 2t+1 dense forms each, t random prefix rows), does the first degree d with
// dim gr I(cap P_b)_d > dim sum_b gr I(P_b)_d stay near N/2 or descend with M?
// In the cube's graded ring (squarefree monomials), (gr I(P))_d = degree-d parts of
// ker(E_{<=d} on P); its dimension is C(N,d) - (rank_d - rank_{d-1}). Exact arithmetic mod 3 (FLINT).
// Usage: fall_degree N h t M dmax seed [dump_instance_path]
#include <flint/nmod_mat.h>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <random>
#include <algorithm>
#include <string>
using namespace std;
typedef vector<int> VI;
int N, h, t, M, dmax; unsigned seed;
vector<unsigned> mons;           // squarefree monomials as bitmasks, sorted by degree
vector<int> degStart;            // degStart[d] = first index of degree d
static int popc(unsigned x){ return __builtin_popcount(x); }
nmod_mat_t* evalMat(const vector<unsigned>& pts, int d) {   // rows: points, cols: monomials deg <= d
    int cols = degStart[d+1];
    nmod_mat_t* A = new nmod_mat_t[1];
    nmod_mat_init(*A, pts.size(), cols, 3);
    for (size_t r = 0; r < pts.size(); r++)
        for (int c = 0; c < cols; c++)
            nmod_mat_entry(*A, r, c) = ((mons[c] & pts[r]) == mons[c]) ? 1 : 0;
    return A;
}
long rankOn(const vector<unsigned>& pts, int d) {
    if (d < 0) return 0;
    nmod_mat_t* A = evalMat(pts, d);
    long r = nmod_mat_rank(*A);
    nmod_mat_clear(*A); delete[] A; return r;
}
// append the degree-d parts of ker(E_{<=d} on pts) as rows of `acc` (vector of rows)
void topParts(const vector<unsigned>& pts, int d, vector<VI>& acc) {
    nmod_mat_t* A = evalMat(pts, d);
    int cols = degStart[d+1];
    nmod_mat_t X; nmod_mat_init(X, cols, cols, 3);
    long k = nmod_mat_nullspace(X, *A);
    for (long j = 0; j < k; j++) {
        VI v(degStart[d+1] - degStart[d]);
        bool nz = false;
        for (int c = degStart[d]; c < degStart[d+1]; c++) { v[c - degStart[d]] = nmod_mat_entry(X, c, j); if (v[c-degStart[d]]) nz = true; }
        if (nz) acc.push_back(v);
    }
    nmod_mat_clear(X); nmod_mat_clear(*A); delete[] A;
}
long rankRows(const vector<VI>& rows, int width) {
    if (rows.empty()) return 0;
    nmod_mat_t B; nmod_mat_init(B, rows.size(), width, 3);
    for (size_t r = 0; r < rows.size(); r++) for (int c = 0; c < width; c++) nmod_mat_entry(B, r, c) = rows[r][c];
    long rk = nmod_mat_rank(B); nmod_mat_clear(B); return rk;
}
long binom(int n, int k){ long r=1; for(int i=1;i<=k;i++) r = r*(n-k+i)/i; return r; }
int main(int argc, char** argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 2; }
    N = atoi(argv[1]); h = atoi(argv[2]); t = atoi(argv[3]); M = atoi(argv[4]); dmax = atoi(argv[5]); seed = atoi(argv[6]);
    FILE* dump = argc > 7 ? fopen(argv[7], "w") : nullptr;
    for (int d = 0; d <= N; d++) { degStart.push_back(mons.size()); for (unsigned m = 0; m < (1u<<N); m++) if (popc(m)==d) mons.push_back(m); }
    degStart.push_back(mons.size());
    mt19937 rng(seed); uniform_int_distribution<int> u3(0,2);
    vector<unsigned> cube(1u<<N); for (unsigned x=0;x<(1u<<N);x++) cube[x]=x;
    vector<vector<unsigned>> P(M); vector<char> inAll(1u<<N, 1);
    for (int b = 0; b < M; b++) {
        vector<VI> A(h, VI(N+1)); for (auto& row: A) for (auto& a: row) a = u3(rng);
        vector<VI> C(t, VI(h)); for (auto& row: C) for (auto& a: row) a = u3(rng);
        if (dump) { fprintf(dump, "block %d\n", b); for (auto& row: A){ for(int a: row) fprintf(dump,"%d ",a); fprintf(dump,"\n"); }
                    for (auto& row: C){ for(int a: row) fprintf(dump,"%d ",a); fprintf(dump,"\n"); } }
        for (unsigned x = 0; x < (1u<<N); x++) {
            VI g(h); bool any=false;
            for (int i = 0; i < h; i++) { int L = A[i][N]; for (int j=0;j<N;j++) if (x>>j&1) L += A[i][j]; g[i] = (L%3==0); any |= g[i]; }
            bool ok = !any;
            for (int j = 0; j < t && !ok; j++) { int s=0; for (int i=0;i<h;i++) s += C[j][i]*g[i]; if (s%3) ok = true; }
            if (ok) P[b].push_back(x); else inAll[x] = 0;
        }
    }
    if (dump) fclose(dump);
    vector<unsigned> PI; for (unsigned x=0;x<(1u<<N);x++) if (inAll[x]) PI.push_back(x);
    char head[256]; snprintf(head, sizeof head, "N=%d h=%d t=%d M=%d seed=%u |capP|=%zu density=%.4f", N,h,t,M,seed,PI.size(), PI.size()/double(1u<<N));
    std::string line(head);  // one atomic line per run, so parallel runs do not interleave
    long prevRank = rankOn(PI, 0); int firstFall = -1;
    line += " excessByDegree=";
    for (int d = 1; d <= dmax; d++) {
        long rd = rankOn(PI, d);
        long grP = rd - prevRank; prevRank = rd;
        long grIdeal = binom(N,d) - grP;
        vector<VI> acc; for (int b = 0; b < M; b++) topParts(P[b], d, acc);
        long sumDim = rankRows(acc, degStart[d+1]-degStart[d]);
        long excess = grIdeal - sumDim;
        line += (d==1 ? "" : ","); line += std::to_string(excess);
        if (excess > 0 && firstFall < 0) firstFall = d;
    }
    line += " firstFall=" + std::to_string(firstFall) + "\n";
    fputs(line.c_str(), stdout); fflush(stdout);
    return 0;
}
