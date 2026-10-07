// Exact single-weight solve for the six-root cyclic-source certificate.
// Uses FLINT modular RREF and an exact Dixon solve; no custom elimination.
// Input: rows cols rhs-cols, then two row-major Macaulay2 rational lists.
// Output: a Macaulay2 list matrix X with A X = B, or exit 2 if this profile supplies no rational certificate.
// The caller independently reconstructs and verifies the polynomial identity.
#include <flint/flint.h>
#include <flint/fmpq_mat.h>
#include <flint/nmod_mat.h>
#include <flint/ulong_extras.h>
#include <vector>
#include <fstream>
#include <iostream>
#include <string>
#include <stdexcept>
#include <chrono>
#include <cctype>

static bool sep(int c) {
    return c == EOF || std::isspace(static_cast<unsigned char>(c)) ||
           c=='{' || c=='}' || c==',' || c=='(' || c==')';
}
static void readq(std::istream& in, fmpq* q) {
    int c;
    do { c=in.get(); } while (c!=EOF && sep(c));
    if(c==EOF) throw std::runtime_error("missing rational entry");
    std::string token(1,static_cast<char>(c));
    while(in.peek()!=EOF && !sep(in.peek())) token+=static_cast<char>(in.get());
    if(token.find_first_not_of("+-0123456789/")!=std::string::npos ||
       fmpq_set_str(q,token.c_str(),10)!=0)
        throw std::runtime_error("invalid rational entry");
    if(fmpz_is_zero(fmpq_denref(q))) throw std::runtime_error("zero denominator");
    fmpq_canonicalise(q);
}
// The modular profile is only a choice of coordinates. Exact full products
// certify success; a modular inconsistency is never a rational nonmembership proof.
static int profile_solve(fmpq_mat_t x,const fmpq_mat_t a,const fmpq_mat_t b,bool report) {
    const mp_limb_t prime=1000003;
    const slong r=fmpq_mat_nrows(a),c=fmpq_mat_ncols(a);
    nmod_mat_t aug,trans;
    nmod_mat_init(aug,r,c+1,prime);
    auto residue=[&](const fmpq* q) {
        mp_limb_t den=fmpz_fdiv_ui(fmpq_denref(q),prime);
        if(!den) throw std::runtime_error("profile prime divides denominator");
        return static_cast<mp_limb_t>(
            (static_cast<unsigned long long>(fmpz_fdiv_ui(fmpq_numref(q),prime))*n_invmod(den,prime))%prime);
    };
    for(slong i=0;i<r;++i) {
        for(slong j=0;j<c;++j) nmod_mat_entry(aug,i,j)=residue(fmpq_mat_entry(a,i,j));
        nmod_mat_entry(aug,i,c)=residue(fmpq_mat_entry(b,i,0));
    }
    slong rank=nmod_mat_rref(aug);
    std::vector<slong> columns;
    for(slong i=0;i<rank;++i) {
        slong j=0;while(j<c+1 && !nmod_mat_entry(aug,i,j)) ++j;
        if(j==c) { nmod_mat_clear(aug); return 0; }
        if(j>c) throw std::runtime_error("invalid modular pivot row");
        columns.push_back(j);
    }
    nmod_mat_clear(aug);
    fmpq_mat_zero(x);
    if(!rank) return fmpq_mat_is_zero(b)?1:-1;
    nmod_mat_init(trans,rank,r,prime);
    for(slong i=0;i<rank;++i) for(slong j=0;j<r;++j)
        nmod_mat_entry(trans,i,j)=residue(fmpq_mat_entry(a,j,columns[i]));
    if(nmod_mat_rref(trans)!=rank) throw std::runtime_error("row profile rank mismatch");
    std::vector<slong> rows;
    for(slong i=0;i<rank;++i) {
        slong j=0;while(j<r && !nmod_mat_entry(trans,i,j)) ++j;
        if(j==r) throw std::runtime_error("missing row pivot");
        rows.push_back(j);
    }
    nmod_mat_clear(trans);
    if(report) std::cout<<"PROFILE prime="<<prime<<" square="<<rank<<std::endl;
    fmpq_mat_t square,rhs,solution,product;
    fmpq_mat_init(square,rank,rank); fmpq_mat_init(rhs,rank,1);
    fmpq_mat_init(solution,rank,1); fmpq_mat_init(product,r,1);
    for(slong i=0;i<rank;++i) {
        for(slong j=0;j<rank;++j)
            fmpq_set(fmpq_mat_entry(square,i,j),fmpq_mat_entry(a,rows[i],columns[j]));
        fmpq_set(fmpq_mat_entry(rhs,i,0),fmpq_mat_entry(b,rows[i],0));
    }
    if(!fmpq_mat_solve_dixon(solution,square,rhs))
        throw std::runtime_error("modular nonsingular subsystem failed exact solve");
    for(slong i=0;i<rank;++i) fmpq_set(fmpq_mat_entry(x,columns[i],0),fmpq_mat_entry(solution,i,0));
    fmpq_mat_mul(product,a,x);
    int ok=fmpq_mat_equal(product,b)?1:-1;
    fmpq_mat_clear(square); fmpq_mat_clear(rhs); fmpq_mat_clear(solution); fmpq_mat_clear(product);
    return ok;
}
static void controls() {
    fmpq_mat_t a,b,x,product;
    fmpq_mat_init(a,2,1); fmpq_mat_init(b,2,1);
    fmpq_mat_init(x,1,1); fmpq_mat_init(product,2,1);
    fmpq_one(fmpq_mat_entry(a,0,0));
    fmpq_one(fmpq_mat_entry(b,1,0));
    if(profile_solve(x,a,b,false)!=0)
        throw std::runtime_error("inconsistent control accepted");
    fmpq_zero(fmpq_mat_entry(b,1,0));
    fmpq_set_si(fmpq_mat_entry(b,0,0),-3,7);
    if(profile_solve(x,a,b,false)!=1)
        throw std::runtime_error("consistent control rejected");
    fmpq_mat_mul(product,a,x);
    if(!fmpq_mat_equal(product,b)) throw std::runtime_error("control product mismatch");
    fmpq_mat_clear(a); fmpq_mat_clear(b); fmpq_mat_clear(x); fmpq_mat_clear(product);
}
int main(int argc,char**argv) {
    try {
        if(argc!=3) throw std::runtime_error("usage: solver INPUT OUTPUT");
        flint_set_num_threads(1);
        controls();
        std::ifstream in(argv[1]);
        long r,c,k;
        if(!(in>>r>>c>>k) || r<1 || c<1 || k!=1 || r>10000 || c>10000 ||
           static_cast<long long>(r)*c>5000000)
            throw std::runtime_error("invalid or oversized dimensions");
        fmpq_mat_t a,b,x,product;
        fmpq_mat_init(a,r,c); fmpq_mat_init(b,r,k);
        fmpq_mat_init(x,c,k); fmpq_mat_init(product,r,k);
        for(long i=0;i<r;++i) for(long j=0;j<c;++j) readq(in,fmpq_mat_entry(a,i,j));
        for(long i=0;i<r;++i) for(long j=0;j<k;++j) readq(in,fmpq_mat_entry(b,i,j));
        int ch; while((ch=in.get())!=EOF) if(!sep(ch))
            throw std::runtime_error("unexpected trailing input");
        auto start=std::chrono::steady_clock::now();
        std::cout<<"SOLVE rows="<<r<<" cols="<<c<<std::endl;
        int ok=profile_solve(x,a,b,true);
        if(ok==1) {
            fmpq_mat_mul(product,a,x);
            if(!fmpq_mat_equal(product,b)) throw std::runtime_error("exact product mismatch");
            std::ofstream out(argv[2]);
            if(!out) throw std::runtime_error("cannot write solution");
            out<<"{";
            for(long i=0;i<c;++i) {
                if(i) out<<",";
                char* value=fmpq_get_str(nullptr,10,fmpq_mat_entry(x,i,0));
                out<<"{"<<value<<"}"; flint_free(value);
            }
            out<<"}\n";
            if(!out) throw std::runtime_error("solution write failed");
        }
        double sec=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout<<(ok==1?"SOLVED":ok==0?"MODULAR_INCONSISTENT_ONLY":"PROFILE_NOT_SUFFICIENT")<<" seconds="<<sec<<std::endl;
        fmpq_mat_clear(a); fmpq_mat_clear(b); fmpq_mat_clear(x); fmpq_mat_clear(product);
        flint_cleanup();
        return ok==1?0:2;
    } catch(const std::exception& e) {
        std::cerr<<"ERROR "<<e.what()<<std::endl; return 1;
    }
}
