// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
// Exact NS spaces only: generated-axiom multiples, with no PC closure.
#include "binary_php.hpp"
#include <memory>
#include <random>
using namespace binary_php;
void xorin(Bits& a,const Bits& b) {
    need(a.size()==b.size(),"xor width");
    for(size_t j=0;j<a.size();++j)a[j]^=b[j];
}
void ints(std::ostream& out,const std::vector<int>& v) {
    out<<'[';for(size_t j=0;j<v.size();++j){if(j)out<<',';out<<v[j];}out<<']';
}
struct QuadraticBoard {
    int n,m,v,width;
    bool columns;
    std::vector<std::pair<int,int>> monomials;
    std::vector<std::vector<int>> product;
    QuadraticBoard(int holes,bool keep_columns):n(holes),m(n+1),v(n*m),
        columns(keep_columns),product(v,std::vector<int>(v,-1)) {
        need(n>=3 && n<=13,"planned board-size range");
        monomials.push_back({-1,-1});
        for(int a=0;a<v;++a)monomials.push_back({a,-1});
        for(int a=0;a<v;++a)for(int b=a;b<v;++b) {
            if(a==b)product[a][b]=a+1;
            else if(a/n!=b/n && (!columns || a%n!=b%n)) {
                product[a][b]=int(monomials.size());monomials.push_back({a,b});
            }
            product[b][a]=product[a][b];
        }
        width=int(monomials.size());
    }
    Bits unit()const{Bits a=blank(width);flip(a,0);return a;}
    Bits row(int i)const {
        Bits a=unit();for(int j=0;j<n;++j)flip(a,1+i*n+j);return a;
    }
    Bits multiply(const Bits& f,int variable)const {
        need(highest(f)<=v,"expected affine multiplicand");
        if(variable<0)return f;
        Bits a=blank(width);
        if(bit(f,0))flip(a,variable+1);
        for(int c=0;c<v;++c)if(bit(f,c+1)) {
            int p=product[variable][c];if(p>=0)flip(a,p);
        }
        return a;
    }
    int evaluate(const Bits& f,const std::vector<bool>& point)const {
        int ans=0;
        for(int j:support(f)) {
            const auto [a,b]=monomials[j];
            ans^=(a<0 || point[a]) && (b<0 || point[b]);
        }
        return ans;
    }
    void describe(std::ostream& out,const std::string& name)const {
        out<<"{\"type\":\"board\",\"name\":\""<<name<<"\",\"N\":"<<n
           <<",\"variables\":"<<v<<",\"columns_enforced\":"<<(columns?"true":"false")
           <<",\"monomials\":[";
        for(int j=0;j<width;++j) {
            if(j)out<<',';
            out<<'['<<monomials[j].first<<','<<monomials[j].second<<']';
        }
        out<<"]}\n";
    }
};
Space base_space(const QuadraticBoard& b,const std::string& name,std::ostream& out) {
    b.describe(out,name);Space base(b.width);
    for(int i=0;i<b.m;++i)for(int q=-1;q<b.v;++q) {
        std::vector<int> trace;int p=base.add(b.multiply(b.row(i),q),&trace);
        out<<"{\"type\":\"base_step\",\"board\":\""<<name<<"\",\"row\":"<<i
           <<",\"multiplier\":"<<q<<",\"trace\":";ints(out,trace);
        out<<",\"pivot\":"<<p;
        if(p>=0){out<<",\"basis_row\":";sparse_json(out,base.rows[p]);}
        out<<"}\n";
    }
    need(!zero(base.reduce(b.unit())),"base unexpectedly refuted through degree two");
    Bits omega=base.separating_dual(b.unit());
    need(bit(omega,0),"base design normalization");
    out<<"{\"type\":\"base_summary\",\"board\":\""<<name<<"\",\"rank\":"<<base.rank
       <<",\"quotient_dimension\":"<<b.width-base.rank<<",\"normalized_design\":";
    sparse_json(out,omega);out<<"}\n";
    return base;
}
using Family=std::vector<std::vector<Bits>>;
Family make_family(const QuadraticBoard& b,int groups,int arity,
                   bool planted,std::uint64_t seed,std::ostream& out) {
    Space linear(b.v);
    for(int i=0;i<b.m;++i) {
        Bits row=blank(b.v);for(int j=0;j<b.n;++j)flip(row,i*b.n+j);
        need(linear.add(row)>=0,"row coefficient dependence");
    }
    auto admit=[&](const Bits& f) {
        Bits row=blank(b.v);
        for(int j=0;j<b.v;++j)if(bit(f,j+1))flip(row,j);
        return linear.add(std::move(row))>=0;
    };
    Family result(groups);
    if(planted)for(int a=0;a<groups;++a) {
        need(2*a+1<b.m,"collision pair range");
        for(int row:{2*a,2*a+1}) {
            Bits f=b.unit();flip(f,row*b.n+1);
            need(admit(f),"collision inputs lost joint rank");
            result[a].push_back(std::move(f));
        }
    }
    std::mt19937_64 rng(seed);unsigned attempts=0,rejected=0;
    for(int a=0;a<groups;++a)while(int(result[a].size())<arity) {
        need(++attempts<10000,"input sampling retry guard");
        Bits f=blank(b.width);int c=0;
        for(int j=0;j<b.v;++j)if(rng()&1) {
            flip(f,j+1);if(j%b.n==0)c^=1;
        }
        if(planted?c:int(rng()&1))flip(f,0);
        if(!admit(f)){++rejected;continue;}
        result[a].push_back(std::move(f));
    }
    if(planted)for(auto& group:result) {
        Bits running=blank(b.width);
        for(Bits& f:group){xorin(running,f);f=running;}
    }
    need(linear.rank==b.m+groups*arity,"joint input-rank mismatch");
    out<<"{\"type\":\"family\",\"name\":\""<<(planted?"collision_spans":"random")
       <<"\",\"seed\":"<<seed<<",\"groups\":"<<groups<<",\"arity\":"<<arity
       <<",\"joint_rank_with_rows\":"<<linear.rank<<",\"random_attempts\":"<<attempts
       <<",\"rejected\":"<<rejected<<",\"prefix_basis_change\":"<<(planted?"true":"false")
       <<",\"inputs\":[";
    for(int a=0;a<groups;++a) {
        if(a)out<<',';
        out<<'[';
        for(int j=0;j<arity;++j){if(j)out<<',';sparse_json(out,result[a][j]);}
        out<<']';
    }
    out<<"]}\n";return result;
}
Space block_space(const QuadraticBoard& b,const Space& base,const std::vector<Bits>& inputs,
                  const std::string& family,int group,std::ostream& out) {
    Space extra(b.width);
    for(int i=0;i<int(inputs.size());++i)for(int q=-1;q<b.v;++q) {
        std::vector<int> base_trace,extra_trace;
        Bits value=base.reduce(b.multiply(inputs[i],q),&base_trace);
        int p=extra.add(std::move(value),&extra_trace);
        out<<"{\"type\":\"input_step\",\"family\":\""<<family<<"\",\"group\":"<<group
           <<",\"input\":"<<i<<",\"multiplier\":"<<q<<",\"base_trace\":";
        ints(out,base_trace);out<<",\"block_trace\":";ints(out,extra_trace);
        out<<",\"pivot\":"<<p;
        if(p>=0){out<<",\"basis_row\":";sparse_json(out,extra.rows[p]);}
        out<<"}\n";
    }
    out<<"{\"type\":\"block_summary\",\"family\":\""<<family<<"\",\"group\":"<<group
       <<",\"additional_rank\":"<<extra.rank<<",\"contains_unit_class\":"
       <<(zero(extra.reduce(base.reduce(b.unit())))?"true":"false")<<"}\n";
    return extra;
}

Space intersection(const Space& left,const Space& right,const std::string& family,
                   int group,std::ostream& out) {
    Space joint=left,result(left.width);
    std::vector<Bits> tags(left.width);
    for(int p=0;p<left.width;++p)if(!left.rows[p].empty())tags[p]=left.rows[p];
    for(int p=0;p<right.width;++p)if(!right.rows[p].empty()) {
        std::vector<int> trace,common_trace;
        Bits value=joint.reduce(right.rows[p],&trace),tag=blank(left.width);
        for(int q:trace)xorin(tag,tags[q]);
        int q=highest(value),common=-1;
        if(q>=0) {
            joint.insert_reduced(std::move(value),q);tags[q]=tag;
        } else {
            need(zero(left.reduce(tag)) && zero(right.reduce(tag)),"intersection membership");
            common=result.add(tag,&common_trace);
            need(common>=0,"dependent intersection witness");
        }
        out<<"{\"type\":\"intersection_step\",\"family\":\""<<family<<"\",\"group\":"<<group
           <<",\"right_pivot\":"<<p<<",\"joint_trace\":";ints(out,trace);
        out<<",\"joint_pivot\":"<<q<<",\"left_component\":";sparse_json(out,tag);
        if(q>=0){out<<",\"joint_row\":";sparse_json(out,joint.rows[q]);}
        else {
            out<<",\"common_trace\":";ints(out,common_trace);
            out<<",\"common_pivot\":"<<common<<",\"common_row\":";
            sparse_json(out,result.rows[common]);
        }
        out<<"}\n";
    }
    need(result.rank==left.rank+right.rank-joint.rank,"intersection dimension identity");
    out<<"{\"type\":\"intersection_summary\",\"family\":\""<<family<<"\",\"through_group\":"
       <<group<<",\"left_rank\":"<<left.rank<<",\"right_rank\":"<<right.rank
       <<",\"joint_rank\":"<<joint.rank<<",\"intersection_rank\":"<<result.rank<<"}\n";
    return result;
}
void check_joint_rank(const QuadraticBoard& b,const Family& f) {
    Space linear(b.v);int expected=b.m;
    for(int i=0;i<b.m;++i) {
        Bits a=blank(b.v);for(int j=0;j<b.n;++j)flip(a,i*b.n+j);
        need(linear.add(a)>=0,"row rank in joint recheck");
    }
    for(const auto& group:f)for(const Bits& g:group) {
        Bits a=blank(b.v);
        for(int j=0;j<b.v;++j)if(bit(g,j+1))flip(a,j);
        need(linear.add(a)>=0,"emitted inputs lost joint independence");
        ++expected;
    }
    need(linear.rank==expected,"emitted joint-rank count");
}
void test_family(const QuadraticBoard& b,const Space& base,const Family& inputs,
                 const std::string& name,bool expect_unit,std::ostream& out) {
    check_joint_rank(b,inputs);
    Bits unit_class=base.reduce(b.unit());
    Space common=block_space(b,base,inputs[0],name,0,out);
    int processed=1;
    if(expect_unit)need(zero(common.reduce(unit_class)),"positive first-block control");
    for(int a=1;a<int(inputs.size()) && common.rank>0;++a) {
        Space next=block_space(b,base,inputs[a],name,a,out);
        if(expect_unit)need(zero(next.reduce(unit_class)),"positive block control");
        common=intersection(common,next,name,a,out);++processed;
    }
    bool has_unit=zero(common.reduce(unit_class));
    if(expect_unit)need(has_unit,"positive common-unit control");
    out<<"{\"type\":\"family_result\",\"family\":\""<<name<<"\",\"processed_blocks\":"
       <<processed<<",\"total_blocks\":"<<inputs.size()<<",\"common_dimension\":"<<common.rank
       <<",\"contains_unit_class\":"<<(has_unit?"true":"false");
    if(common.rank) {
        Bits target=unit_class;
        if(!has_unit)for(const Bits& row:common.rows)if(!row.empty()){target=row;break;}
        need(!zero(base.reduce(target)),"common target already an old consequence");
        Bits dual=base.separating_dual(target);
        out<<",\"target\":";sparse_json(out,target);
        out<<",\"base_separating_functional\":";sparse_json(out,dual);
        out<<",\"functional_on_unit\":"<<bit(dual,0)<<",\"functional_on_target\":"<<dot(dual,target);
    }
    out<<"}\n";
    std::cout<<name<<": common dimension "<<common.rank<<", unit="<<has_unit
             <<", processed "<<processed<<'/'<<inputs.size()<<" blocks.\n";
}
void satisfiable_control(const QuadraticBoard& full,const Family& family,std::ostream& out) {
    QuadraticBoard b(full.n,false);
    std::vector<bool> point(b.v,false);std::vector<int> ones;
    for(int i=0;i<b.m;++i){point[i*b.n]=true;ones.push_back(i*b.n);}
    unsigned base_checks=0,input_checks=0;
    for(int i=0;i<b.m;++i)for(int q=-1;q<b.v;++q) {
        need(b.evaluate(b.multiply(b.row(i),q),point)==0,"row-only base evaluation");
        ++base_checks;
    }
    for(const auto& group:family)for(const Bits& old:group) {
        Bits g=blank(b.width);
        for(int j=0;j<=b.v;++j)if(bit(old,j))flip(g,j);
        for(int q=-1;q<b.v;++q) {
            need(b.evaluate(b.multiply(g,q),point)==0,"row-only input evaluation");
            ++input_checks;
        }
    }
    need(b.evaluate(b.unit(),point)==1,"evaluation normalization");
    out<<"{\"type\":\"satisfiable_no_columns_control\",\"N\":"<<b.n
       <<",\"one_cells\":";ints(out,ones);
    out<<",\"base_multiple_checks\":"<<base_checks<<",\"input_multiple_checks\":"
       <<input_checks<<",\"all_evaluations_zero\":true,\"unit_evaluation\":1,"
         "\"omitted_column_collision_value\":1}\n";
    std::cout<<"Without column exclusions: explicit model verifies "<<base_checks
             <<" base and "<<input_checks<<" input multiples; unit stays nonzero.\n";
}
Bits quadratic_product(const QuadraticBoard& b,const Bits& f,const Bits& g) {
    need(highest(f)<=b.v && highest(g)<=b.v,"affine product inputs");
    Bits product=blank(b.width);
    if(bit(f,0) && bit(g,0))flip(product,0);
    for(int a=0;a<b.v;++a) {
        bool value=(bit(f,a+1)&&bit(g,0)) ^ (bit(f,0)&&bit(g,a+1)) ^
                   (bit(f,a+1)&&bit(g,a+1));
        if(value)flip(product,a+1);
    }
    for(int j=b.v+1;j<b.width;++j) {
        const auto [a,c]=b.monomials[j];
        bool value=(bit(f,a+1)&&bit(g,c+1)) ^ (bit(f,c+1)&&bit(g,a+1));
        if(value)flip(product,j);
    }
    return product;
}
void square_pairs(const QuadraticBoard& b,const Space& base,const Family& family,
                  const std::string& name,bool unit_control,std::ostream& out) {
    check_joint_rank(b,family);
    std::vector<Space> squares;squares.reserve(family.size());
    Bits unit=base.reduce(b.unit());
    for(int a=0;a<int(family.size());++a) {
        Space w(b.width);
        for(int i=0;i<int(family[a].size());++i)
            for(int j=i;j<int(family[a].size());++j) {
                std::vector<int> base_trace,space_trace;
                Bits product=quadratic_product(b,family[a][i],family[a][j]);
                if(i==j)need(product==family[a][i],"affine square reduction");
                Bits value=base.reduce(std::move(product),&base_trace);
                int p=w.add(std::move(value),&space_trace);
                out<<"{\"type\":\"square_product_step\",\"family\":\""<<name
                   <<"\",\"group\":"<<a<<",\"inputs\":["<<i<<','<<j
                   <<"],\"base_trace\":";ints(out,base_trace);
                out<<",\"space_trace\":";ints(out,space_trace);
                out<<",\"pivot\":"<<p<<"}\n";
            }
        bool contains_unit=zero(w.reduce(unit));
        if(unit_control)need(contains_unit,"square-space positive unit control");
        out<<"{\"type\":\"square_space_summary\",\"family\":\""<<name
           <<"\",\"group\":"<<a<<",\"rank\":"<<w.rank<<",\"contains_unit\":"
           <<(contains_unit?"true":"false")<<"}\n";
        squares.push_back(std::move(w));
    }
    int count=0,max_intersection=0,separated=0;
    for(int a=0;a<int(squares.size());++a)for(int c=a+1;c<int(squares.size());++c) {
        Space joint=squares[a];
        for(int p=0;p<b.width;++p)if(!squares[c].rows[p].empty()) {
            std::vector<int> trace;int q=joint.add(squares[c].rows[p],&trace);
            out<<"{\"type\":\"square_pair_step\",\"family\":\""<<name
               <<"\",\"groups\":["<<a<<','<<c<<"],\"right_pivot\":"<<p
               <<",\"joint_trace\":";ints(out,trace);out<<",\"pivot\":"<<q<<"}\n";
        }
        int common=squares[a].rank+squares[c].rank-joint.rank;
        need(common>=0,"negative square intersection dimension");
        if(unit_control)need(common>=1,"unit disappeared from pair intersection");
        max_intersection=std::max(max_intersection,common);++count;
        separated+=common==0;
        out<<"{\"type\":\"square_pair_summary\",\"family\":\""<<name
           <<"\",\"groups\":["<<a<<','<<c<<"],\"left_rank\":"<<squares[a].rank
           <<",\"right_rank\":"<<squares[c].rank<<",\"joint_rank\":"<<joint.rank
           <<",\"intersection_rank\":"<<common<<"}\n";
    }
    const int h=(b.n-1)/6,D=3*h+1;
    need(h>=1 && b.n>=2*D-1,"first-boundary application parameters");
    out<<"{\"type\":\"square_family_result\",\"family\":\""<<name<<"\",\"N\":"<<b.n
       <<",\"h\":"<<h<<",\"D\":"<<D<<",\"pairs\":"<<count
       <<",\"separated_pairs\":"<<separated<<",\"max_intersection\":"<<max_intersection
       <<",\"all_pairs_separated\":"<<(separated==count?"true":"false")<<"}\n";
    std::cout<<"N="<<b.n<<' '<<name<<": "<<separated<<'/'<<count
             <<" square pairs separated; max intersection "<<max_intersection
             <<"; h="<<h<<" D="<<D<<".\n";
}
int main(int argc,char** argv) {
    try {
        need(argc>=3 && std::string(argv[1])=="--out",
             "usage: check_quadratic_relative_kernel --out NEW.jsonl [--square-pairs] [--holes N]");
        bool square_mode=false;int holes=11;
        for(int a=3;a<argc;++a) {
            std::string option=argv[a];
            if(option=="--square-pairs")square_mode=true;
            else if(option=="--holes" && a+1<argc)holes=std::stoi(argv[++a]);
            else throw std::runtime_error("unknown or incomplete option");
        }
        need(square_mode?(holes>=7 && holes<=13 && holes%2==1):(holes==11),
             "unsupported mode/board combination");
        std::ifstream existing(argv[2]);need(!existing.good(),"output exists");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        if(square_mode)out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"degree\":2,"
             "\"space\":\"Within-block product subspaces in the old NS quotient\","
             "\"basis_encoding\":\"Product labels plus complete reduction traces\","
             "\"indices\":\"zero based; multiplier -1 means constant one\"}\n";
        else out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"degree\":2,"
             "\"space\":\"NS generator multiples, no PC closure\","
             "\"indices\":\"zero based; multiplier -1 means constant one\","
             "\"row_representation\":\"sorted nonzero monomial indices\"}\n";
        QuadraticBoard b(holes,true);Space base=base_space(b,"functional",out);
        int r=square_mode?holes/2+1:6;
        Family random=make_family(b,r,r,false,2026091387ULL,out);
        if(square_mode)square_pairs(b,base,random,"random",false,out);
        else test_family(b,base,random,"random",false,out);
        Family positive=make_family(b,r,r,true,2026091388ULL,out);
        if(square_mode)square_pairs(b,base,positive,"collision_spans",true,out);
        else {
            test_family(b,base,positive,"collision_spans",true,out);
            satisfiable_control(b,positive,out);
        }
        out.close();need(bool(out),"output write failed");return 0;
    } catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
