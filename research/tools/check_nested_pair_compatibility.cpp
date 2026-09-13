// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
#include "binary_php.hpp"
#include <bitset>
#include <map>
using namespace binary_php;
using Affines=std::vector<unsigned>;
unsigned wt(unsigned x){return __builtin_popcount(x);}
int value(unsigned affine,unsigned point){return __builtin_parity(affine&((point<<1)|1u));}
void nums(std::ostream& out,const std::vector<int>& a) {
    out<<'[';for(size_t j=0;j<a.size();++j){if(j)out<<',';out<<a[j];}out<<']';
}
void affines(std::ostream& out,const Affines& a) {
    out<<'[';for(size_t j=0;j<a.size();++j){if(j)out<<',';out<<a[j];}out<<']';
}
Space affine_space(int variables,const Affines& inputs) {
    Space span(variables+1);
    for(unsigned g:inputs) {
        need(g>1 && g<(1u<<(variables+1)),"nonconstant affine input range");
        Bits row=blank(variables+1);row[0]=g;span.add(row);
    }
    Bits one=blank(variables+1);flip(one,0);
    need(!zero(span.reduce(one)),"input span contains one");
    return span;
}
void pair_check(const std::string& name,int variables,const Affines& a,const Affines& b,
                bool column_model,int expected_intrinsic,std::ostream& out) {
    Space va=affine_space(variables,a),vb=affine_space(variables,b),vsum=va;
    for(const Bits& row:vb.rows)if(!row.empty())vsum.add(row);
    const bool equal=va.rank==vb.rank && vsum.rank==va.rank;
    const int ma=int(a.size()),mb=int(b.size()),offset=ma*mb,unknowns=2*offset;
    Space equations(unknowns);
    out<<"{\"type\":\"pair_fixture\",\"name\":\""<<name<<"\",\"variables\":"<<variables
       <<",\"a\":";affines(out,a);out<<",\"b\":";affines(out,b);
    out<<",\"column_model\":"<<(column_model?"true":"false")<<",\"rank_a\":"<<va.rank
       <<",\"rank_b\":"<<vb.rank<<",\"rank_union\":"<<vsum.rank
       <<",\"equal_spans\":"<<(equal?"true":"false")<<"}\n";
    for(unsigned point=0;point<(1u<<variables);++point) {
        if(column_model && wt(point)>1)continue;
        for(int j=0;j<ma;++j)for(int k=0;k<mb;++k) {
            Bits row=blank(unknowns);
            for(int i=0;i<mb;++i)if(value(b[i],point)&&value(b[k],point))flip(row,j*mb+i);
            for(int i=0;i<ma;++i)if(value(a[i],point)&&value(a[j],point))flip(row,offset+k*ma+i);
            std::vector<int> trace;int p=equations.add(row,&trace);
            out<<"{\"type\":\"pair_equation\",\"name\":\""<<name<<"\",\"point\":"<<point
               <<",\"j\":"<<j<<",\"k\":"<<k<<",\"trace\":";nums(out,trace);
            out<<",\"pivot\":"<<p;
            if(p>=0){out<<",\"basis\":";sparse_json(out,equations.rows[p]);}
            out<<"}\n";
        }
    }
    const int array_width=(ma+mb)*(variables+1);
    Space polynomial_arrays(array_width);int kernel_dimension=0;
    for(int p=0;p<unknowns;++p)if(!bit(equations.pivots,p)) {
        Bits seed=blank(unknowns);flip(seed,p);
        Bits kernel=equations.complete_dual(seed);
        Affines aa(ma),bb(mb);
        for(int j=0;j<ma;++j)for(int i=0;i<mb;++i)if(bit(kernel,j*mb+i))aa[j]^=b[i];
        for(int k=0;k<mb;++k)for(int i=0;i<ma;++i)if(bit(kernel,offset+k*ma+i))bb[k]^=a[i];
        for(unsigned x=0;x<(1u<<variables);++x)if(!column_model || wt(x)<=1)
            for(int j=0;j<ma;++j)for(int k=0;k<mb;++k)
                need((value(aa[j],x)&&value(b[k],x))==(value(bb[k],x)&&value(a[j],x)),
                     "pair kernel does not satisfy original equations");
        Bits encoded=blank(array_width);
        for(int j=0;j<ma+mb;++j) {
            unsigned g=j<ma?aa[j]:bb[j-ma];
            for(int q=0;q<=variables;++q)if((g>>q)&1)flip(encoded,j*(variables+1)+q);
        }
        polynomial_arrays.add(encoded);++kernel_dimension;
        out<<"{\"type\":\"pair_kernel_vector\",\"name\":\""<<name<<"\",\"coefficients\":";
        sparse_json(out,kernel);out<<",\"A\":";affines(out,aa);out<<",\"B\":";affines(out,bb);out<<"}\n";
    }
    int representation_kernel=ma*(mb-vb.rank)+mb*(ma-va.rank);
    need(kernel_dimension==unknowns-equations.rank,"coefficient kernel dimension");
    need(polynomial_arrays.rank==expected_intrinsic,"intrinsic pair-kernel prediction failed");
    need(kernel_dimension==representation_kernel+polynomial_arrays.rank,"representation kernel count");
    if(!column_model)need(expected_intrinsic==int(equal),"pure Boolean classification failed");
    out<<"{\"type\":\"pair_fixture_result\",\"name\":\""<<name<<"\",\"coefficient_kernel\":"
       <<kernel_dimension<<",\"zero_representation_kernel\":"<<representation_kernel
       <<",\"polynomial_array_kernel\":"<<polynomial_arrays.rank
       <<",\"faithful_model_prediction\":"<<int(equal)<<"}\n";
    std::cout<<name<<": coefficient kernel "<<kernel_dimension<<", polynomial-array kernel "
             <<polynomial_arrays.rank<<".\n";
}
unsigned product_word(int dimension,unsigned a,unsigned b) {
    unsigned result=(a&1u)&(b&1u);int index=1;
    for(int i=0;i<dimension;++i,++index) {
        unsigned ai=(a>>(i+1))&1u,bi=(b>>(i+1))&1u;
        if((ai*(b&1u))^((a&1u)*bi)^(ai*bi))result^=1u<<index;
    }
    for(int i=0;i<dimension;++i)for(int j=i+1;j<dimension;++j,++index)
        if((((a>>(i+1))&1u)*((b>>(j+1))&1u)) ^
           (((a>>(j+1))&1u)*((b>>(i+1))&1u)))result^=1u<<index;
    return result;
}
void translated_family(int dimension,std::ostream& out) {
    const int points=1<<dimension,width=1+dimension+dimension*(dimension-1)/2;
    std::vector<Affines> groups;
    for(int c=0;c<points;++c) {
        Affines group;
        for(int j=0;j<dimension;++j)group.push_back((1u<<(j+1))|((c>>j)&1u));
        groups.push_back(group);
    }
    groups.push_back(Affines(groups[0].begin(),groups[0].end()-1));
    Affines changed;unsigned prefix=0;
    for(unsigned g:groups[0]){prefix^=g;changed.push_back(prefix);}
    groups.push_back(changed);
    need((groups[0][0]^groups[1][0])==1,"aggregate input unit witness");
    out<<"{\"type\":\"translated_family\",\"dimension\":"<<dimension<<",\"groups\":[";
    for(size_t j=0;j<groups.size();++j){if(j)out<<',';affines(out,groups[j]);}
    out<<"],\"root_unit_witness\":{\"groups\":[0,1],\"input_indices\":[0,0]}}\n";
    std::vector<Space> linear,square;linear.reserve(groups.size());square.reserve(groups.size());
    for(int a=0;a<int(groups.size());++a) {
        linear.push_back(affine_space(dimension,groups[a]));Space w(width);
        for(int i=0;i<int(groups[a].size());++i)for(int j=i;j<int(groups[a].size());++j) {
            Bits row=blank(width);row[0]=product_word(dimension,groups[a][i],groups[a][j]);
            std::vector<int> trace;int p=w.add(row,&trace);
            out<<"{\"type\":\"translated_product\",\"dimension\":"<<dimension<<",\"group\":"<<a
               <<",\"inputs\":["<<i<<','<<j<<"],\"word\":"<<row[0]<<",\"trace\":";
            nums(out,trace);out<<",\"pivot\":"<<p;
            if(p>=0)out<<",\"basis_word\":"<<w.rows[p][0];
            out<<"}\n";
        }
        square.push_back(std::move(w));
    }
    std::map<int,int> histogram;int pairs=0,equal_pairs=0,nested_pairs=0;
    for(int a=0;a<int(groups.size());++a)for(int b=a+1;b<int(groups.size());++b) {
        Space ls=linear[a],ws=square[a];
        for(const Bits& row:linear[b].rows)if(!row.empty())ls.add(row);
        bool equal=linear[a].rank==linear[b].rank && ls.rank==linear[a].rank;
        bool nested=linear[a].rank!=linear[b].rank &&
                    ls.rank==std::max(linear[a].rank,linear[b].rank);
        out<<"{\"type\":\"translated_pair\",\"dimension\":"<<dimension<<",\"groups\":["<<a<<','<<b
           <<"],\"linear_union_rank\":"<<ls.rank<<",\"equal\":"<<(equal?"true":"false")
           <<",\"strictly_nested\":"<<(nested?"true":"false")<<",\"right_steps\":[";
        bool first=true;
        for(int p=0;p<width;++p)if(!square[b].rows[p].empty()) {
            std::vector<int> trace;int q=ws.add(square[b].rows[p],&trace);
            if(!first)out<<',';
            first=false;
            out<<"{\"source\":"<<p<<",\"trace\":";nums(out,trace);
            out<<",\"pivot\":"<<q;
            if(q>=0)out<<",\"basis_word\":"<<ws.rows[q][0];
            out<<'}';
        }
        int intersection=square[a].rank+square[b].rank-ws.rank;
        need(intersection>0,"translated square spaces unexpectedly separated");
        out<<"],\"square_union_rank\":"<<ws.rank<<",\"square_intersection\":"<<intersection<<"}\n";
        ++pairs;equal_pairs+=equal;nested_pairs+=nested;++histogram[intersection];
    }
    for(unsigned x=0;x<unsigned(points);++x) {
        std::vector<int> zeros;int translated_zeros=0;
        for(int a=0;a<int(groups.size());++a) {
            bool all_zero=true;for(unsigned g:groups[a])all_zero&=value(g,x)==0;
            if(all_zero){zeros.push_back(a);translated_zeros+=a<points;}
        }
        need(translated_zeros==1 && zeros[0]==int(x),"translated zero-space cover");
        out<<"{\"type\":\"translated_cover\",\"dimension\":"<<dimension<<",\"value\":"<<x
           <<",\"zero_groups\":";nums(out,zeros);out<<"}\n";
    }
    need(equal_pairs==1 && nested_pairs==3,"translated family span structure");
    out<<"{\"type\":\"translated_summary\",\"dimension\":"<<dimension<<",\"groups\":"<<groups.size()
       <<",\"pairs\":"<<pairs<<",\"equal_pairs\":"<<equal_pairs<<",\"strictly_nested_pairs\":"
       <<nested_pairs<<",\"intersection_histogram\":{";
    bool first=true;
    for(auto [rank,count]:histogram){if(!first)out<<',';first=false;out<<'"'<<rank<<"\":"<<count;}
    out<<"}}\n";
    std::cout<<"Translated dimension "<<dimension<<": "<<groups.size()<<" groups, "<<pairs
             <<" overlapping square pairs, one equal-span pair and three strict nestings.\n";
}

using Poly=std::bitset<512>;
int mu(int j,unsigned monomial) {
    int answer=0;
    for(unsigned x=1;x<8;++x)if(__builtin_ctz(x)==j && (x&monomial)==monomial)answer^=1;
    return answer;
}
int joint_moment(unsigned monomial,int theta_a,int theta_b,bool diagonal_pair) {
    unsigned old=monomial&7u,fresh=monomial>>3,a=fresh&7u,b=(fresh>>3)&7u;
    if(fresh==0)return old==0;
    if(b==0 && wt(a)==1)return theta_a*mu(__builtin_ctz(a),old);
    if(a==0 && wt(b)==1)return theta_b*mu(__builtin_ctz(b),old);
    if(diagonal_pair && wt(a)==1 && wt(b)==1 && a==b)return mu(__builtin_ctz(a),old);
    return 0;
}
Poly companion(int block,int i) {
    Poly p;p.flip(1u<<i);
    for(int j=0;j<3;++j)p.flip((1u<<i)|(1u<<j)|(1u<<(3+3*block+j)));
    return p;
}
Poly multiply_variable(const Poly& p,int variable) {
    if(variable<0)return p;
    Poly q;
    for(unsigned m=0;m<512;++m)if(p[m])q.flip(m|(1u<<variable));
    return q;
}
int functional_value(const Poly& p,int a,int b,bool pair) {
    int sum=0;
    for(unsigned m=0;m<512;++m)if(p[m]) {
        need(wt(m)<=4,"control exceeds original degree-four ceiling");
        sum^=joint_moment(m,a,b,pair);
    }
    return sum;
}
void component_control(const std::string& name,int theta_a,int theta_b,bool pair,
                       bool expected_valid,std::ostream& out) {
    int root_checks=0,own_checks=0,moments=0,extension_checks=0,violations=0;
    for(int block=0;block<2;++block) {
        int theta=block?theta_b:theta_a;
        for(int i=0;i<3;++i)for(int q=-1;q<3;++q) {
            unsigned old=(1u<<i)|(q<0?0u:(1u<<q));int rhs=0;
            for(int j=0;j<3;++j)rhs^=theta*mu(j,old|(1u<<j));
            need(rhs==0,"individual root equation failed");++root_checks;
            out<<"{\"type\":\"singleton_root_check\",\"case\":\""<<name<<"\",\"block\":"<<block
               <<",\"input\":"<<i<<",\"multiplier\":"<<q<<",\"value\":"<<rhs<<"}\n";
        }
        for(int i=0;i<3;++i)for(int j=0;j<3;++j) {
            int v=theta*(mu(j,1u<<i)^mu(j,(1u<<i)|(1u<<j)));
            need(v==0,"individual support equation failed");++own_checks;
            out<<"{\"type\":\"singleton_own_check\",\"case\":\""<<name<<"\",\"block\":"<<block
               <<",\"input\":"<<i<<",\"selected\":"<<j<<",\"value\":"<<v<<"}\n";
        }
    }
    for(unsigned m=0;m<512;++m)if(wt(m)<=4) {
        out<<"{\"type\":\"joint_moment\",\"case\":\""<<name<<"\",\"mask\":"<<m
           <<",\"value\":"<<joint_moment(m,theta_a,theta_b,pair)<<"}\n";++moments;
    }
    for(int block=0;block<2;++block)for(int i=0;i<3;++i)for(int q=-1;q<9;++q) {
        int v=functional_value(multiply_variable(companion(block,i),q),theta_a,theta_b,pair);
        ++extension_checks;violations+=v!=0;
        out<<"{\"type\":\"extension_check\",\"case\":\""<<name<<"\",\"block\":"<<block
           <<",\"input\":"<<i<<",\"multiplier\":"<<q<<",\"value\":"<<v<<"}\n";
    }
    need((violations==0)==expected_valid,"matched/mismatched control expectation");
    need((theta_a^theta_b)==int(!expected_valid),"equal-span dual obstruction");
    out<<"{\"type\":\"component_control_result\",\"case\":\""<<name<<"\",\"theta_a\":"<<theta_a
       <<",\"theta_b\":"<<theta_b<<",\"diagonal_pair\":"<<(pair?"true":"false")
       <<",\"root_checks\":"<<root_checks<<",\"own_checks\":"<<own_checks<<",\"moments\":"<<moments
       <<",\"extension_checks\":"<<extension_checks<<",\"violations\":"<<violations
       <<",\"dual_obstruction_value\":"<<(theta_a^theta_b)<<"}\n";
    std::cout<<name<<": "<<moments<<" joint moments, "<<extension_checks
             <<" original-budget extension checks, "<<violations<<" violations.\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out",
             "usage: check_nested_pair_compatibility --out NEW.jsonl");
        std::ifstream existing(argv[2]);need(!existing.good(),"output exists");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
             "\"affine_words\":\"bit zero is constant; bit j+1 is variable j\","
             "\"pair_unknowns\":\"C[j,i_b], then D[k,i_a], in row-major order\","
             "\"joint_masks\":\"old x0,x1,x2, then rA0,rA1,rA2,rB0,rB1,rB2\","
             "\"original_companion_degree\":3,\"joint_degree_ceiling\":4}\n";
        pair_check("separated",4,{2,4},{8,16},false,0,out);
        pair_check("strictly_nested",3,{2,4},{2,4,8},false,0,out);
        pair_check("proper_overlap",3,{2,4},{4,8},false,0,out);
        pair_check("identical",3,{2,4,8},{2,4,8},false,1,out);
        pair_check("changed_basis",3,{2,4,8},{6,12,8},false,1,out);
        pair_check("affine_offset",2,{2,4},{3,4},false,0,out);
        pair_check("redundant_equal",2,{2,4},{2,4,6},false,1,out);
        pair_check("column_relation_control",2,{2},{2,4},true,1,out);
        translated_family(6,out);
        component_control("mismatched",0,1,false,false,out);
        component_control("matched_zero",0,0,false,true,out);
        component_control("matched_one",1,1,true,true,out);
        out.close();need(bool(out),"output write failed");return 0;
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
