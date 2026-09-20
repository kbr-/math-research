// Bounded exact controls for collective-polar-rank embeddings and a rank-jump pitfall.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using U=uint64_t;
using Matrix=std::vector<U>;
void need(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }
int bit(U x,int i) { return int((x>>i)&1U); }
int parity(U x) { return __builtin_parityll(x); }
int degree(U x) { return x?63-__builtin_clzll(x):-1; }
U remainder(U a,U b) { while(a && degree(a)>=degree(b))a^=b<<(degree(a)-degree(b));return a; }
U gcd(U a,U b) { while(b){U c=remainder(a,b);a=b;b=c;}return a; }
struct Field {
    int d;U poly;
    U mul(U a,U b)const {
        U c=0;
        for(int i=0;i<d;++i){if(b&1)c^=a;b>>=1;a<<=1;if(a&(U(1)<<d))a^=poly;}
        return c;
    }
    U pow(U a,U e)const { U z=1;while(e){if(e&1)z=mul(z,a);a=mul(a,a);e>>=1;}return z; }
    int trace(U a)const {
        U z=0,x=a;for(int i=0;i<d;++i){z^=x;x=mul(x,x);}need(z<=1,"field trace not binary");return int(z);
    }
    bool irreducible()const {
        std::vector<int> primes;int n=d;
        for(int q=2;q*q<=n;++q)if(n%q==0){primes.push_back(q);while(n%q==0)n/=q;}
        if(n>1)primes.push_back(n);
        U x=2,z=x;
        for(int i=1;i<=d;++i){z=mul(z,z);for(int q:primes)if(i==d/q && gcd(z^x,poly)!=1)return false;}
        return z==x;
    }
};
int rank(Matrix rows) {
    U piv[64]={};int r=0;
    for(U x:rows){while(x){int j=degree(x);if(piv[j])x^=piv[j];else{piv[j]=x;++r;break;}}}
    return r;
}
U polar_apply(const Matrix& a,U x) { U y=0;for(int i=0;i<int(a.size());++i)if(parity(a[i]&x))y|=U(1)<<i;return y; }
int bilinear(const Matrix& a,U x,U y) { return parity(polar_apply(a,x)&y); }
U rng=0xa83d72519;
U random_bits(){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
U solve_sample(Matrix rows,std::vector<int> rhs,int v) {
    int r=0;std::vector<int> piv;
    for(int col=0;col<v;++col){
        int p=r;while(p<int(rows.size()) && !bit(rows[p],col))++p;
        if(p==int(rows.size()))continue;
        std::swap(rows[r],rows[p]);std::swap(rhs[r],rhs[p]);
        for(int j=0;j<int(rows.size());++j)if(j!=r && bit(rows[j],col)){rows[j]^=rows[r];rhs[j]^=rhs[r];}
        piv.push_back(col);++r;
    }
    need(r==int(rows.size()),"gradient constraints lost independence");
    U x=random_bits();if(v<64)x&=(U(1)<<v)-1;
    for(int j:piv)x&=~(U(1)<<j);
    for(int j=0;j<r;++j)if(rhs[j]^parity(rows[j]&x))x|=U(1)<<piv[j];
    return x;
}
void vector_json(std::ostream& o,const std::vector<U>& x){o<<'[';for(size_t i=0;i<x.size();++i){if(i)o<<',';o<<x[i];}o<<']';}
void int_json(std::ostream& o,const std::vector<int>& x){o<<'[';for(size_t i=0;i<x.size();++i){if(i)o<<',';o<<x[i];}o<<']';}
bool target_ok(const std::vector<Matrix>& forms,const Matrix& vectors,int a) {
    for(int i=0;i<a;++i)for(int j=0;j<2*a;++j)for(int k=j+1;k<2*a;++k)
        if(bilinear(forms[i],vectors[j],vectors[k])!=int(j==2*i && k==2*i+1))return false;
    return true;
}
int field_rank(std::vector<std::vector<U>> a,const Field& f) {
    int r=0;
    for(int c=0;c<int(a.size());++c){
        int p=r;while(p<int(a.size()) && !a[p][c])++p;if(p==int(a.size()))continue;
        std::swap(a[r],a[p]);U inv=f.pow(a[r][c],(U(1)<<f.d)-2);
        for(U& x:a[r])x=f.mul(x,inv);
        for(int j=0;j<int(a.size());++j)if(j!=r && a[j][c]){U z=a[j][c];for(int k=0;k<int(a.size());++k)a[j][k]^=f.mul(z,a[r][k]);}
        ++r;
    }
    return r;
}
int main(int argc,char** argv)try {
    need(argc==3 && std::string(argv[1])=="--out","usage: check_quadratic_rank_structure --out FILE");
    const std::vector<Field> fields={{2,7},{8,0x11b},{20,0x100009},{32,0x10000008dULL}};
    std::cout<<"Fixed workload: four embeddings, at most 15 rank combinations per case, at most 256 samples per vector, matrices at most 64 by 64.\n";
    std::ofstream out(argv[2]);need(bool(out),"cannot open output");
    out<<"{\"scope\":\"exact binary collective-rank embeddings and base-field rank-jump control; no Bogolyubov computation or full-source test\",\"seed\":"<<rng<<",\"embeddings\":[";
    int total_attempts=0;
    for(int index=0;index<4;++index){
        int a=index+1;const Field f=fields[index];int v=2*f.d;
        need(f.irreducible(),"configured field polynomial is reducible");
        std::vector<Matrix> forms(a,Matrix(v));
        for(int i=0;i<a;++i)for(int j=0;j<f.d;++j)for(int k=0;k<f.d;++k)
            if(f.trace(f.mul(U(1)<<i,f.mul(U(1)<<j,U(1)<<k)))){
                forms[i][j]|=U(1)<<(f.d+k);forms[i][f.d+k]|=U(1)<<j;
            }
        std::vector<int> ranks;int minrank=v;
        for(int c=1;c<(1<<a);++c){Matrix z(v);for(int i=0;i<a;++i)if(c&(1<<i))for(int j=0;j<v;++j)z[j]^=forms[i][j];int r=rank(z);ranks.push_back(r);minrank=std::min(minrank,r);}
        need(minrank>=4*a*a,"test fails collective-rank hypothesis");
        Matrix vectors,gradients;std::vector<int> attempts,gradient_ranks;
        for(int step=0;step<2*a;++step){
            std::vector<int> rhs;
            for(int j=0;j<step;++j)for(int i=0;i<a;++i)rhs.push_back(j==2*i && step==2*i+1);
            bool found=false;
            for(int trial=1;trial<=256;++trial){
                ++total_attempts;U x=solve_sample(gradients,rhs,v);
                for(size_t j=0;j<gradients.size();++j)need(parity(gradients[j]&x)==rhs[j],"incorrect affine solution");
                Matrix candidate=gradients;for(const auto& b:forms)candidate.push_back(polar_apply(b,x));
                if(rank(candidate)==a*(step+1)){
                    vectors.push_back(x);gradients=std::move(candidate);attempts.push_back(trial);gradient_ranks.push_back(rank(gradients));found=true;break;
                }
            }
            need(found,"bounded sampler did not find the guaranteed positive-density choice");
        }
        need(rank(vectors)==2*a,"selected directions not independent");need(target_ok(forms,vectors,a),"diagonal leading-pair restriction failed");
        Matrix bad=vectors;bad[0]=0;need(!target_ok(forms,bad,a),"wrong-direction control was not detected");
        Matrix basis=vectors;
        for(int j=0;j<v && int(basis.size())<v;++j){Matrix b=basis;b.push_back(U(1)<<j);if(rank(b)>int(basis.size()))basis=std::move(b);}
        need(rank(basis)==v,"basis completion failed");
        if(index)out<<',';
        out<<"{\"a\":"<<a<<",\"variables\":"<<v<<",\"field_degree\":"<<f.d<<",\"field_polynomial\":"<<f.poly<<",\"combination_ranks\":";int_json(out,ranks);
        out<<",\"sample_attempts\":";int_json(out,attempts);out<<",\"gradient_ranks\":";int_json(out,gradient_ranks);
        out<<",\"selected_vectors\":";vector_json(out,vectors);out<<",\"full_coordinate_basis\":";vector_json(out,basis);
        out<<",\"polar_rows\":[";
        for(int i=0;i<a;++i){if(i)out<<',';vector_json(out,forms[i]);}
        out<<"],\"transformed_polar_rows\":[";
        for(int i=0;i<a;++i){
            if(i)out<<',';
            Matrix rows(v);
            for(int j=0;j<v;++j)for(int k=0;k<v;++k)if(bilinear(forms[i],basis[j],basis[k]))rows[j]|=U(1)<<k;
            vector_json(out,rows);
        }
        out<<"],\"transformed_linear_parts\":[";
        U mask=(U(1)<<f.d)-1;
        for(int i=0;i<a;++i){if(i)out<<',';U linear=0;for(int j=0;j<v;++j)if(f.trace(f.mul(U(1)<<i,f.mul(basis[j]&mask,basis[j]>>f.d))))linear|=U(1)<<j;out<<linear;}
        out<<"],\"leading_pairs_verified\":true,\"wrong_direction_detected\":true}";
    }
    Matrix b1(6),b2(6);auto edge=[](Matrix& b,int i,int j){b[i]|=U(1)<<j;b[j]|=U(1)<<i;};
    edge(b1,0,1);edge(b1,4,5);edge(b2,2,3);edge(b2,4,5);
    Matrix sum(6);for(int j=0;j<6;++j)sum[j]=b1[j]^b2[j];
    need(rank(b1)==4 && rank(b2)==4 && rank(sum)==4,"wrong base-field maximum-rank control");
    need(polar_apply(b1,U(1)<<2)==0 && polar_apply(b1,U(1)<<3)==0 && bilinear(b2,U(1)<<2,U(1)<<3)==1,"radical counterexample failed");
    Field extension{3,0xb};need(extension.irreducible(),"F8 polynomial failed");
    std::vector<std::vector<U>> lifted(6,std::vector<U>(6));
    for(int j=0;j<6;++j)for(int k=0;k<6;++k)lifted[j][k]=U(bit(b1[j],k))^(bit(b2[j],k)?2U:0U);
    int extended_rank=field_rank(lifted,extension);need(extended_rank==6,"extension did not reach generic maximum rank");
    out<<"],\"rank_jump_control\":{\"first_polar_rows\":";vector_json(out,b1);out<<",\"second_polar_rows\":";vector_json(out,b2);
    out<<",\"base_nonzero_ranks\":[4,4,4],\"extension_field_degree\":3,\"extension_polynomial\":11,\"combination_coefficients\":[1,2],\"extension_rank\":"<<extended_rank<<",\"first_radical_not_common_isotropic\":true},\"total_sample_attempts\":"<<total_attempts<<",\"all_checks_passed\":true}\n";
    need(bool(out),"output write failed");
    std::cout<<"Four exact embeddings passed; "<<total_attempts<<" candidate samples. Wrong-direction controls detected. Base-field rank 4 versus extension rank 6 verified.\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
