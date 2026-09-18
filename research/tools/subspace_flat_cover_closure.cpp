// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact polynomial-calculus closure over F_2 of the bit PHP restricted to a random affine
// subspace W of the label-bit space, computed in residual coordinates y of W.
//
// Board: `rows` pigeons, n = 2^ell holes, label bits b_{i,t} = c_{i,t} + sum_j G[(i,t)][j] y_j,
// j < k, where G is a uniform v x kmax matrix of full column rank (v = rows*ell), so that
// W_k = c + span(first k columns) is a nested family of uniform subspaces.  Axioms: for each pair
// of rows the indicator of the collision flat, prod_t (1 + b_{i,t} + b_{i',t}), a multilinear
// polynomial of degree at most ell in y.  Boolean axioms are built into multilinear arithmetic.
// The linear equations of W are eliminated exactly: an invertible affine change of bit coordinates
// preserves bit degree, so the closure computed here is the degree-d PC closure of
// (bit PHP + equations of W) read on W.
//
// Closure: echelon basis with pivots at the highest monomial of a degree-major order; every basis
// row whose pivot has degree < d is multiplied by every variable until nothing new appears, or
// until the constant 1 is derived.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <string>
#include <unordered_set>
#include <vector>
typedef uint64_t u64;
struct Rng{u64 s;u64 next(){s+=0x9E3779B97F4A7C15ULL;u64 z=s;z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL;
    z=(z^(z>>27))*0x94D049BB133111EBULL;return z^(z>>31);}};
static u64 binom[70][70];
struct Index{
    int k,d;std::vector<u64> offset;std::vector<u64> masks;
    Index(int k_,int d_):k(k_),d(d_){
        offset.assign(d+2,0);
        for(int r=0;r<=d;r++)offset[r+1]=offset[r]+binom[k][r];
        masks.resize(offset[d+1]);
        for(u64 i=0;i<masks.size();i++)masks[i]=0;
        // enumerate masks by degree through Gosper's hack
        for(int r=0;r<=d&&r<=k;r++){
            if(r==0){masks[offset[0]]=0;continue;}
            u64 m=(1ULL<<r)-1,limit=1ULL<<k;
            while(m<limit){masks[rank(m)]=m;u64 c=m&-m,rr=m+c;m=(((rr^m)>>2)/c)|rr;}
        }
    }
    u64 rank(u64 m)const{
        int r=0;u64 acc=0;u64 x=m;
        while(x){int p=__builtin_ctzll(x);x&=x-1;r++;acc+=binom[p][r];}
        return offset[r]+acc;
    }
    u64 size()const{return masks.size();}
};
int main(int argc,char**argv){
    int ell=3,rows=-1,d=3,kmin=1,kmax=-1,seed=1,all=0,identity=0,count=0;
    for(int i=1;i<argc;i++){
        std::string a=argv[i];
        auto val=[&](){if(i+1>=argc){fprintf(stderr,"missing value\n");exit(2);}return atoi(argv[++i]);};
        if(a=="--ell")ell=val();else if(a=="--rows")rows=val();else if(a=="--d")d=val();
        else if(a=="--kmin")kmin=val();else if(a=="--kmax")kmax=val();else if(a=="--seed")seed=val();
        else if(a=="--all")all=1;else if(a=="--identity")identity=1;else if(a=="--count")count=1;
        else{fprintf(stderr,"unknown option %s\n",a.c_str());return 2;}
    }
    for(int i=0;i<70;i++){binom[i][0]=1;for(int j=1;j<70;j++)binom[i][j]=(j>i)?0:binom[i-1][j-1]+(j<=i-1?binom[i-1][j]:0);}
    int n=1<<ell;if(rows<0)rows=n+1;int v=rows*ell;
    int cols=std::min(v,60);if(kmax<0||kmax>cols)kmax=cols;
    // random v x cols matrix of full column rank, rows stored as masks over the columns
    std::vector<u64> G(v);std::vector<int> c(v);Rng rng{(u64)seed*1000003ULL+(u64)ell*7919ULL+(u64)rows};
    if(identity){if(v>60){fprintf(stderr,"identity needs v<=60\n");return 2;}
        for(int r=0;r<v;r++){G[r]=1ULL<<r;c[r]=0;}}
    else for(;;){
        for(int r=0;r<v;r++)G[r]=rng.next()&((cols==64)?~0ULL:((1ULL<<cols)-1));
        std::vector<u64> e(G);int rk=0;
        for(int col=0;col<cols;col++){int p=-1;for(int r=rk;r<v;r++)if((e[r]>>col)&1){p=r;break;}
            if(p<0)continue;std::swap(e[p],e[rk]);for(int r=0;r<v;r++)if(r!=rk&&((e[r]>>col)&1))e[r]^=e[rk];rk++;}
        if(rk==cols)break;
    }
    if(!identity)for(int r=0;r<v;r++)c[r]=rng.next()&1;
    if(count){
        // brute-force number of points of W_k whose labels are pairwise distinct (k <= 26)
        for(int k=kmin;k<=kmax&&k<=26;k++){
            u64 sol=0;std::vector<int> lab(rows);std::vector<char> seen(n);
            for(u64 y=0;y<(1ULL<<k);y++){
                std::fill(seen.begin(),seen.end(),0);bool ok=true;
                for(int i=0;i<rows&&ok;i++){int z=0;
                    for(int t=0;t<ell;t++)z|=((c[i*ell+t]^(__builtin_popcountll(G[i*ell+t]&y)&1))<<t);
                    if(seen[z])ok=false;seen[z]=1;}
                if(ok)sol++;
            }
            printf("{\"ell\":%d,\"rows\":%d,\"k\":%d,\"seed\":%d,\"injective_points\":%llu}\n",ell,rows,k,seed,(unsigned long long)sol);
        }
        return 0;
    }
    for(int k=kmin;k<=kmax;k++){
        auto t0=std::chrono::steady_clock::now();
        if(d>k){printf("{\"ell\":%d,\"rows\":%d,\"d\":%d,\"k\":%d,\"seed\":%d,\"skipped\":\"d>k\"}\n",ell,rows,d,k,seed);continue;}
        Index ix(k,d);u64 M=ix.size(),Mlow=ix.offset[d];u64 kmask=(k==64)?~0ULL:((1ULL<<k)-1);
        std::vector<std::vector<int>> mul(k,std::vector<int>(Mlow));
        for(int j=0;j<k;j++)for(u64 i=0;i<Mlow;i++)mul[j][i]=(int)ix.rank(ix.masks[i]|(1ULL<<j));
        std::vector<std::vector<u64>> basis(M);std::vector<char> has(M,0);
        std::deque<u64> work;bool found=false;u64 dim=0;u64 W=(M+63)/64;
        std::vector<u64> buf(W);
        auto insert=[&](std::vector<u64>&vec){
            long w=(long)W-1;
            for(;;){
                while(w>=0&&vec[w]==0)w--;
                if(w<0)return;
                u64 p=(u64)w*64+63-__builtin_clzll(vec[w]);
                if(has[p]){const auto&b=basis[p];for(long q=0;q<=w;q++)vec[q]^=b[q];}
                else{basis[p].assign(vec.begin(),vec.begin()+w+1);has[p]=1;dim++;
                    if(p<Mlow)work.push_back(p);if(p==0)found=true;return;}
            }
        };
        int trivial=0,unit=0;
        for(int i=0;i<rows&&!found;i++)for(int i2=i+1;i2<rows&&!found;i2++){
            std::unordered_set<u64> P;P.insert(0);
            for(int t=0;t<ell;t++){
                u64 form=(G[i*ell+t]^G[i2*ell+t])&kmask;int cst=c[i*ell+t]^c[i2*ell+t]^1;
                std::unordered_set<u64> Q;
                if(cst)Q=P;
                for(u64 m:P)for(int j=0;j<k;j++)if((form>>j)&1){u64 m2=m|(1ULL<<j);
                    auto it=Q.find(m2);if(it==Q.end())Q.insert(m2);else Q.erase(it);}
                P.swap(Q);
            }
            if(P.empty()){trivial++;continue;}
            if(P.size()==1&&*P.begin()==0)unit++;
            std::fill(buf.begin(),buf.end(),0);bool ok=true;
            for(u64 m:P){if(__builtin_popcountll(m)>d){ok=false;break;}u64 r=ix.rank(m);buf[r>>6]^=1ULL<<(r&63);}
            if(ok)insert(buf);
        }
        u64 axiom_dim=dim;
        while(!work.empty()&&!found){
            u64 p=work.front();work.pop_front();
            for(int j=0;j<k&&!found;j++){
                std::fill(buf.begin(),buf.end(),0);const auto&b=basis[p];
                for(size_t q=0;q<b.size();q++){u64 x=b[q];while(x){int s=__builtin_ctzll(x);x&=x-1;
                    int r=mul[j][q*64+s];buf[r>>6]^=1ULL<<(r&63);}}
                insert(buf);
            }
        }
        double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
        printf("{\"ell\":%d,\"rows\":%d,\"d\":%d,\"k\":%d,\"seed\":%d,\"identity\":%d,\"monomials\":%llu,"
               "\"axiom_span\":%llu,\"empty_flats\":%d,\"full_flats\":%d,\"closure_dim\":%llu,\"refuted\":%s,\"seconds\":%.2f}\n",
               ell,rows,d,k,seed,identity,(unsigned long long)M,(unsigned long long)axiom_dim,trivial,unit,
               (unsigned long long)dim,found?"true":"false",sec);
        fflush(stdout);
        if(!found&&!all)break;
    }
    return 0;
}
