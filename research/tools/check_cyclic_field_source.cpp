// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Binary finite-field pair certificates, CRT maps, and complete cyclic sources.
#include "domain_polynomial.hpp"
#include "ns_witness.hpp"
#include <boost/multiprecision/cpp_int.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace domain_polynomial;
using boost::multiprecision::cpp_int;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Field {
    int d,q,modulus;
    explicit Field(int m):d(31-__builtin_clz(unsigned(m))),q(1<<d),modulus(m){
        need(d>=1 && d<=4,"small exact field guard");
        for(int a=1;a<q;++a)need(power(a,q-1)==1,"every nonzero residue is a unit");
    }
    int mul(int a,int b) const{
        int result=0;
        while(b){if(b&1)result^=a;b>>=1;a<<=1;if(a&q)a^=modulus;}
        return result;
    }
    int power(int a,int e) const{
        int result=1;while(e){if(e&1)result=mul(result,a);a=mul(a,a);e>>=1;}return result;
    }
};
using Vector=std::vector<Polynomial>;
Vector product(const Ring& r,const Field& f,const Vector& a,const Vector& b){
    Vector result(f.d);
    for(int i=0;i<f.d;++i)for(int j=0;j<f.d;++j){
        auto term=r.multiply(a[i],b[j]);int scalar=f.mul(1<<i,1<<j);
        for(int k=0;k<f.d;++k)if((scalar>>k)&1)r.accumulate(result[k],term);
    }
    return result;
}
Vector inverse_polynomial(const Ring& r,const Field& f,const Vector& a){
    Vector V(f.d);V[0]=r.constant(1);
    for(int u=1;u<f.d;++u){
        Vector L(f.d);
        for(int i=0;i<f.d;++i){
            int scalar=f.power(1<<i,1<<u);
            for(int j=0;j<f.d;++j)if((scalar>>j)&1)r.accumulate(L[j],a[i]);
        }
        V=product(r,f,V,L);
    }
    return V;
}
Vector pair_cofactors(const Ring& r,const Field& f,const Vector& a,int i,int j){
    auto V=inverse_polynomial(r,f,a);Vector h(f.d);
    for(int lambda=0;lambda<f.d;++lambda){
        Polynomial coordinate;
        for(int k=0;k<f.d;++k)if((f.mul(1<<k,1<<lambda)>>j)&1)r.accumulate(coordinate,V[k]);
        h[lambda]=r.multiply(a[i],coordinate);need(degree(h[lambda])<=f.d,"inverse coefficient degree");
    }
    return h;
}
std::vector<Polynomial> booleans(const Ring& r,int variables){
    Vector result;
    for(int i=0;i<variables;++i){auto x=r.variable(i);result.push_back(r.subtract(r.power(x,2),x));}
    return result;
}
void numbers(std::ostream& out,const std::vector<unsigned>& v){
    out<<'[';for(unsigned i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';
}
int rank(std::vector<unsigned> rows,int columns){
    int pivot=0;
    for(int j=0;j<columns && pivot<int(rows.size());++j){
        int i=pivot;while(i<int(rows.size()) && !((rows[i]>>j)&1))++i;
        if(i==int(rows.size()))continue;
        std::swap(rows[i],rows[pivot]);
        for(int k=0;k<int(rows.size());++k)if(k!=pivot && ((rows[k]>>j)&1))rows[k]^=rows[pivot];
        ++pivot;
    }
    return pivot;
}
struct Writer {
    Ring r{2,80};int certificates=0;
    void certificate(std::ostream& out,const std::string& system,const std::string& name,
                     const Vector& axioms,const Polynomial& target,const std::map<int,Polynomial>& cof,
                     int budget,const Polynomial* source=nullptr,int T=0,int k=0){
        out<<"{\"record\":\"NS_certificate\",\"system\":\""<<system<<"\",\"name\":\""<<name
           <<"\",\"target\":";write_json(out,target);out<<",\"budget\":"<<budget;
        if(source){
            need(budget<=T*degree(*source)+k,"complete original degree ledger");
            out<<",\"source_axiom\":";write_json(out,*source);
            out<<",\"original_degree\":"<<degree(*source)<<",\"weighted_transfer_ceiling\":"<<T*degree(*source)+k;
        }
        ns_witness::write_terms(out,r,axioms,target,cof,budget,name);out<<"}\n";++certificates;
    }
    void boolean_certificate(std::ostream& out,const std::string& system,const std::string& name,
                             int variables,const Polynomial& target,int budget,
                             const Polynomial* source=nullptr,int T=0,int k=0){
        auto red=domain_reduce(r,target,std::vector<int>(variables,2));
        verify_reduction(r,target,std::vector<int>(variables,2),red);
        need(red.remainder.empty(),"Boolean-zero target");std::map<int,Polynomial> cof;
        for(int i=0;i<variables;++i)if(!red.coefficients[i].empty())cof[i]=red.coefficients[i];
        certificate(out,system,name,booleans(r,variables),target,cof,budget,source,T,k);
    }
};
void local_fields(std::ostream& out,Writer& w){
    auto& r=w.r;
    for(int modulus:{3,7,11,19}){
        Field f(modulus);Vector a,b;
        for(int i=0;i<f.d;++i){a.push_back(r.variable(i));b.push_back(r.variable(f.d+i));}
        auto C=product(r,f,a,b),axioms=booleans(r,2*f.d);axioms.insert(axioms.end(),C.begin(),C.end());
        std::string system="field_product_d"+std::to_string(f.d);
        out<<"{\"record\":\"field_product_system\",\"system\":\""<<system<<"\",\"dimension\":"<<f.d
           <<",\"modulus_bits\":"<<modulus<<",\"generators\":";write_polynomials(out,axioms);
        out<<",\"inverse_coordinates\":";write_polynomials(out,inverse_polynomial(r,f,a));
        out<<",\"multiplication_table\":[";
        for(int x=0;x<f.q;++x){
            if(x)out<<',';
            out<<'[';for(int y=0;y<f.q;++y){if(y)out<<',';out<<f.mul(x,y);}out<<']';
        }
        out<<"],\"scope\":\"binary polynomials; component equations only construct kernel witnesses\"}\n";
        for(int i=0;i<f.d;++i)for(int j=0;j<f.d;++j){
            auto h=pair_cofactors(r,f,a,i,j);auto target=r.multiply(a[i],b[j]);
            auto error=target;std::map<int,Polynomial> cof;
            for(int lambda=0;lambda<f.d;++lambda){
                r.accumulate(error,r.multiply(h[lambda],C[lambda]),-1);cof[2*f.d+lambda]=h[lambda];
            }
            auto red=domain_reduce(r,error,std::vector<int>(2*f.d,2));
            verify_reduction(r,error,std::vector<int>(2*f.d,2),red);
            need(red.remainder.empty() && red.degree<=f.d+2,"field pair Boolean correction");
            for(int id=0;id<2*f.d;++id)cof[id]=red.coefficients[id];
            w.certificate(out,system,"pair_"+std::to_string(i)+"_"+std::to_string(j),axioms,target,cof,f.d+2);
        }
        for(int mask=1;mask<f.q;++mask){
            Polynomial q;for(int j=0;j<f.d;++j)if((mask>>j)&1)r.accumulate(q,C[j]);
            std::vector<unsigned> polar(2*f.d);
            for(const auto& [m,coefficient]:q){
                need(coefficient==1 && m.size()==2 && m[0]!=m[1],"bilinear support");
                polar[m[0]]^=1u<<m[1];polar[m[1]]^=1u<<m[0];
            }
            need(rank(polar,2*f.d)==2*f.d,"nondegenerate scalar product component");
            out<<"{\"record\":\"component_span_rank\",\"dimension\":"<<f.d<<",\"component_mask\":"<<mask
               <<",\"polar_rank\":"<<2*f.d<<",\"polar_rows\":";numbers(out,polar);out<<"}\n";
        }
        int zeroes=0;
        for(int x=0;x<f.q;++x)for(int y=0;y<f.q;++y)if(!f.mul(x,y)){
            need(x==0 || y==0,"finite-field product zero locus");
            out<<"{\"record\":\"field_product_zero\",\"dimension\":"<<f.d<<",\"A\":"<<x<<",\"B\":"<<y<<"}\n";++zeroes;
        }
        need(zeroes==2*f.q-1,"complete field-product zero count");
        if(f.d==2){
            std::map<int,int> point{{0,1},{1,1},{2,1},{3,1}};
            need(!r.evaluate(C[0],point) && r.evaluate(C[1],point)==1,"missing component control");
            out<<"{\"record\":\"missing_component_control\",\"dimension\":2,\"A\":3,\"B\":3,"
                 "\"C0\":0,\"C1\":1,\"x0_z0\":1,\"scope\":\"C0 alone does not imply the pair relation\"}\n";
        }
    }
    need(w.certificates==30,"all local field pair certificates");
}
unsigned polynomial_product(unsigned a,unsigned b){unsigned r=0;while(b){if(b&1)r^=a;a<<=1;b>>=1;}return r;}
unsigned apply_binary_matrix(const std::vector<unsigned>& matrix,unsigned v){
    unsigned result=0;
    for(unsigned i=0;i<matrix.size();++i)result|=unsigned(__builtin_parity(matrix[i]&v))<<i;
    return result;
}
std::vector<unsigned> invert(std::vector<unsigned> rows){
    int n=rows.size();need(n<=15,"small matrix guard");
    for(int i=0;i<n;++i)rows[i]|=1u<<(n+i);
    for(int j=0;j<n;++j){
        int i=j;while(i<n && !((rows[i]>>j)&1))++i;need(i<n,"CRT invertibility");
        std::swap(rows[i],rows[j]);
        for(int k=0;k<n;++k)if(k!=j && ((rows[k]>>j)&1))rows[k]^=rows[j];
    }
    for(auto& row:rows)row>>=n;
    return rows;
}
struct CRT {
    int t;std::vector<Field> fields;std::vector<int> offsets;
    std::vector<unsigned> left,right,left_inverse,right_inverse;Vector inputs,components,left_forms,right_forms;
    CRT(const Ring& r,int length,const std::vector<int>& moduli):t(length){
        unsigned factor_product=1;int dimension=0;
        for(int modulus:moduli){
            fields.emplace_back(modulus);offsets.push_back(dimension);dimension+=fields.back().d;
            factor_product=polynomial_product(factor_product,modulus);
        }
        need(dimension==t && factor_product==((1u<<t)|1),"complete squarefree cyclic factorization");
        left.resize(t);right.resize(t);
        for(unsigned nu=0;nu<fields.size();++nu){
            const auto& f=fields[nu];int z=f.d==1?1:2;
            for(int j=0;j<t;++j){
                int a=f.power(z,(t-j)%t),b=f.power(z,j);
                for(int k=0;k<f.d;++k){
                    if((a>>k)&1)left[offsets[nu]+k]|=1u<<j;
                    if((b>>k)&1)right[offsets[nu]+k]|=1u<<j;
                }
            }
        }
        left_inverse=invert(left);right_inverse=invert(right);
        for(int i=0;i<t;++i){
            need(apply_binary_matrix(left_inverse,apply_binary_matrix(left,1u<<i))==(1u<<i),"left CRT round trip");
            need(apply_binary_matrix(right_inverse,apply_binary_matrix(right,1u<<i))==(1u<<i),"right CRT round trip");
        }
        for(int i=0;i<t;++i){
            Polynomial g,a,b;
            for(int j=0;j<t;++j){
                r.accumulate(g,r.multiply(r.variable(j),r.variable(t+(j+i)%t)));
                if((left[i]>>j)&1)r.accumulate(a,r.variable(j));
                if((right[i]>>j)&1)r.accumulate(b,r.variable(t+j));
            }
            inputs.push_back(g);left_forms.push_back(a);right_forms.push_back(b);
        }
        for(unsigned nu=0;nu<fields.size();++nu){
            const auto& f=fields[nu];int offset=offsets[nu];
            Vector a(left_forms.begin()+offset,left_forms.begin()+offset+f.d);
            Vector b(right_forms.begin()+offset,right_forms.begin()+offset+f.d);
            auto C=product(r,f,a,b);
            for(int k=0;k<f.d;++k){
                Polynomial image;
                for(int i=0;i<t;++i)if((right[offset+k]>>i)&1)r.accumulate(image,inputs[i]);
                need(image==C[k],"literal cyclic product under CRT");components.push_back(image);
            }
        }
    }
    void write(std::ostream& out) const{
        out<<"{\"record\":\"cyclic_CRT\",\"t\":"<<t<<",\"moduli\":[";
        for(unsigned i=0;i<fields.size();++i){if(i)out<<',';out<<fields[i].modulus;}
        out<<"],\"component_offsets\":[";
        for(unsigned i=0;i<offsets.size();++i){if(i)out<<',';out<<offsets[i];}
        out<<"],\"left_rows\":";numbers(out,left);out<<",\"right_and_output_rows\":";numbers(out,right);
        out<<",\"left_inverse_rows\":";numbers(out,left_inverse);out<<",\"right_inverse_rows\":";numbers(out,right_inverse);
        out<<",\"actual_inputs\":";write_polynomials(out,inputs);out<<",\"component_products\":";write_polynomials(out,components);
        out<<",\"matrix_encoding\":\"row bitmasks; lower bit is lower input index\",\"passed\":true}\n";
    }
};
void source(std::ostream& out,Writer& w,const CRT& crt){
    auto& r=w.r;auto one=r.constant(1);need(crt.t==3,"complete source fixture length");
    const auto& f=crt.fields[1];int offset=crt.offsets[1];
    Vector a(crt.left_forms.begin()+offset,crt.left_forms.begin()+offset+f.d);
    auto h=pair_cofactors(r,f,a,0,0);auto extra=r.variable(6);
    auto weight=r.multiply(extra,r.multiply(a[0],crt.right_forms[offset]));
    need(degree(weight)==3,"homogeneous cubic multiplier");
    Vector beta(3);
    for(int lambda=0;lambda<f.d;++lambda)for(int i=0;i<3;++i)if((crt.right[offset+lambda]>>i)&1)
        r.accumulate(beta[i],r.multiply(extra,h[lambda]));
    auto kernel_generators=booleans(r,7);kernel_generators.insert(kernel_generators.end(),crt.inputs.begin(),crt.inputs.end());
    auto error=weight;std::map<int,Polynomial> kernel_cof;
    for(int i=0;i<3;++i){
        need(degree(beta[i])<=3,"actual parent coefficient bound");
        r.accumulate(error,r.multiply(beta[i],crt.inputs[i]),-1);kernel_cof[7+i]=beta[i];
    }
    auto red=domain_reduce(r,error,std::vector<int>(7,2));verify_reduction(r,error,std::vector<int>(7,2),red);
    need(red.remainder.empty() && !error.empty() && red.degree<=5,"nonliteral kernel Boolean correction");
    for(int i=0;i<7;++i)kernel_cof[i]=red.coefficients[i];
    out<<"{\"record\":\"cyclic_kernel_system\",\"generators\":";write_polynomials(out,kernel_generators);
    out<<",\"weight\":";write_json(out,weight);out<<",\"pair_coefficients\":";write_polynomials(out,beta);
    out<<",\"nonzero_Boolean_correction\":";write_json(out,error);out<<"}\n";
    w.certificate(out,"cyclic_kernel","costed_pair_kernel",kernel_generators,weight,kernel_cof,5);
    int fresh=7;std::vector<Block> bottoms;std::map<int,Polynomial> phi;
    for(int j=0;j<3;++j)for(int k=0;k<3;++k){
        auto b=make_block(r,{r.subtract(one,r.variable(j)),r.subtract(one,r.variable(3+k))},1,fresh);
        phi[b.variables[0][0]]=one;phi[b.variables[0][1]]=r.variable(j);
        need(r.substitute(b.product,phi)==r.multiply(r.variable(j),r.variable(3+k)),"literal reused bottom");
        bottoms.push_back(b);
    }
    Vector actual_inputs;
    for(int i=0;i<3;++i){Polynomial g;for(int j=0;j<3;++j)r.accumulate(g,bottoms[3*j+(j+i)%3].product);actual_inputs.push_back(g);}
    auto parent=make_block(r,actual_inputs,1,fresh);
    for(int i=0;i<3;++i){phi[parent.variables[0][i]]=beta[i];need(r.substitute(parent.inputs[i],phi)==crt.inputs[i],"actual complete cyclic sums");}
    need(fresh==28 && r.substitute(parent.product,phi)==r.add(r.subtract(one,weight),error),"parent product includes the Boolean correction");
    out<<"{\"record\":\"cyclic_source_system\",\"old_variables\":7,\"source_variables\":28,\"old_Boolean_axioms\":";
    write_polynomials(out,booleans(r,7));out<<",\"bottoms\":[";
    for(unsigned i=0;i<bottoms.size();++i){if(i)out<<',';write_block(out,bottoms[i]);}
    out<<"],\"parent\":";write_block(out,parent);out<<",\"simultaneous_map\":[";bool comma=false;
    for(const auto& [id,p]:phi){if(comma)out<<',';comma=true;out<<'['<<id<<',';write_json(out,p);out<<']';}
    out<<"],\"weight\":";write_json(out,weight);out<<",\"coefficient_degree\":3,\"weight_degree\":3,"
         "\"row_by_variable\":[0,0,0,1,1,1,0],\"scope\":\"local complete two-level source; not a PHP instance\"}\n";
    int before=w.certificates;
    auto bools=booleans(r,7);for(int i=0;i<7;++i)w.boolean_certificate(out,"cyclic_source","old_"+std::to_string(i),7,
        r.multiply(weight,bools[i]),5,&bools[i],3,3);
    auto blocks=bottoms;blocks.push_back(parent);
    for(unsigned b=0;b<blocks.size();++b){
        for(unsigned i=0;i<blocks[b].companions.size();++i){
            const auto& original=blocks[b].companions[i];
            w.boolean_certificate(out,"cyclic_source","companion_"+std::to_string(b)+"_"+std::to_string(i),7,
                r.multiply(weight,r.substitute(original,phi)),b==bottoms.size()?10:6,&original,3,3);
        }
        for(int id:blocks[b].variables[0]){
            auto original=r.subtract(r.power(r.variable(id),2),r.variable(id));
            auto image=r.subtract(r.power(phi.at(id),2),phi.at(id));
            w.boolean_certificate(out,"cyclic_source","field_"+std::to_string(id),7,r.multiply(weight,image),
                                   b==bottoms.size()?9:5,&original,3,3);
        }
    }
    need(w.certificates-before==49,"complete weighted cyclic-source image count");
    int models=0;
    for(unsigned bits=0;bits<128;++bits){
        std::map<int,int> point;for(int i=0;i<7;++i)point[i]=(bits>>i)&1;
        if(!r.evaluate(weight,point))continue;
        for(const auto& [id,p]:phi)point[id]=r.evaluate(p,point);
        for(const auto& b:blocks){
            for(const auto& p:b.companions)need(!r.evaluate(p,point),"conditional cyclic-source model");
            for(int id:b.variables[0])need(point[id]==0 || point[id]==1,"binary coefficient domain");
        }
        out<<"{\"record\":\"conditional_cyclic_source_model\",\"old_point\":"<<bits<<",\"assignment\":[";
        for(int i=0;i<fresh;++i){if(i)out<<',';out<<point.at(i);}out<<"]}\n";++models;
    }
    need(models==16,"complete nonzero-weight support");
    std::map<int,int> point;for(int i=0;i<7;++i)point[i]=(9>>i)&1;
    auto image=r.substitute(parent.companions[0],phi);
    need(!r.evaluate(weight,point) && r.evaluate(image,point)==1,"unweighted source-map control");
    out<<"{\"record\":\"cyclic_unweighted_control\",\"old_point\":9,\"weight_value\":0,\"companion_value\":1,"
         "\"companion_image\":";write_json(out,image);out<<"}\n";
}
cpp_int ceil_sqrt(const cpp_int& a){
    cpp_int lo=0,hi=1;while(hi*hi<a)hi<<=1;
    while(lo+1<hi){cpp_int mid=(lo+hi)/2;if(mid*mid>=a)hi=mid;else lo=mid;}
    need(hi*hi>=a && (hi-1)*(hi-1)<a,"integer ceiling square root");return hi;
}
void parameters(std::ostream& out){
    for(unsigned ell:{40u,64u,128u}){
        unsigned logell=0;while((1u<<logell)<ell)++logell;
        cpp_int n=cpp_int(1)<<ell,m=n+1,v=m*ell,M=n*n,D=cpp_int(ell)*ell*ell;
        unsigned s=1;while(2*((cpp_int(1)<<(s+1))-1)<=v)++s;
        cpp_int R=(cpp_int(1)<<s)-1,H=3*ell+logell+4,k=ceil_sqrt((v*v*H+R-1)/R);
        cpp_int high=k+s-2,affine=2*k+1,T=high>affine?high:affine,B=T*D+k;
        cpp_int num=m*(cpp_int(ell)*(ell-1)*(ell-2)/6)*k*(k-1)*(k-2),den=v*(v-1)*(v-2);
        cpp_int packing=16*(k-1),room=2*B+2*k-1;
        need(2*R<=v && 2*((cpp_int(1)<<(s+1))-1)>v,"largest permitted cyclic length");
        need(R*k*k>=v*v*H && 2*k<=v && 2*num<=den && packing<n,"cyclic image/domain/packing conditions");
        bool board=room<=n;need(board==(ell>=64),"positive and negative cyclic parameter controls");
        out<<"{\"record\":\"cyclic_parameters\",\"ell\":"<<ell<<",\"n\":\""<<n<<"\",\"v\":\""<<v
           <<"\",\"M\":\""<<M<<"\",\"D\":\""<<D<<"\",\"s\":"<<s<<",\"c\":"<<s+2<<",\"R\":\""<<R
           <<"\",\"H\":\""<<H<<"\",\"k\":\""<<k<<"\",\"T\":\""<<T<<"\",\"B\":\""<<B
           <<"\",\"epsilon_numerator\":\""<<num<<"\",\"epsilon_denominator\":\""<<den
           <<"\",\"packing_left\":\""<<packing<<"\",\"room_required\":\""<<room
           <<"\",\"image_domain_packing_conditions\":true,\"old_degree_bound\":"<<(board?"true":"false")<<",\"passed\":true}\n";
    }
}
int main(int argc,char** argv){
    try{
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];need(!std::filesystem::exists(path),"output exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");Writer w;
        out<<"{\"record\":\"schema\",\"version\":1,\"base_field\":2,"
             "\"polynomials\":\"[coefficient,[variable IDs with repetitions]]\",\"large_integers\":\"exact decimal strings\"}\n";
        local_fields(out,w);CRT small(w.r,3,{3,7});small.write(out);
        CRT(w.r,7,{3,11,13}).write(out);CRT(w.r,15,{3,7,19,25,31}).write(out);
        source(out,w,small);parameters(out);need(w.certificates==80,"total exact certificate count");
        out<<"{\"record\":\"summary\",\"NS_certificates\":80,\"weighted_source_images\":49,"
             "\"conditional_source_models\":16,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"80 exact NS certificates, three CRT decompositions, complete cyclic-source and parameter controls passed.\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
