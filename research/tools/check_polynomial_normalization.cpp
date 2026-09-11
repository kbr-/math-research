// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Ordinary polynomial identities, literal matching witnesses, and exact F_2
// degree-two tests for affine normalizers of a saved spread. Run via compute.sh.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Word=std::uint64_t;
using Bits=std::vector<Word>;
using Mono=std::vector<int>;
using Poly=std::map<Mono,int>;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
int mod(int a,int p){a%=p;return a<0?a+p:a;}
Poly constant(int a){return a?Poly{{{},a}}:Poly{};}
Poly variable(int v){return {{{v},1}};}
void add(Poly& a,const Poly& b,int scale,int p){
    for(const auto& [monomial,c]:b){
        int value=mod(a[monomial]+scale*c,p);
        if(value)a[monomial]=value;else a.erase(monomial);
    }
}
Poly multiply(const Poly& a,const Poly& b,int p){
    Poly result;
    for(const auto& [u,c]:a)for(const auto& [v,d]:b){
        Mono product;std::merge(u.begin(),u.end(),v.begin(),v.end(),std::back_inserter(product));
        need(product.size()<=12,"polynomial degree guard");
        int value=mod(result[product]+c*d,p);
        if(value)result[product]=value;else result.erase(product);
    }
    need(result.size()<100000,"polynomial term guard");return result;
}
int degree(const Poly& p){int d=0;for(const auto& term:p)d=std::max(d,int(term.first.size()));return d;}
void poly_json(std::ostream& out,const Poly& poly){
    out<<'[';bool comma=false;
    for(const auto& [monomial,c]:poly){
        if(comma)out<<',';
        comma=true;out<<'['<<c<<",[";
        for(size_t i=0;i<monomial.size();i++){if(i)out<<',';out<<monomial[i];}
        out<<"]]";
    }
    out<<']';
}
void hexword(std::ostream& out,Word word){
    auto flags=out.flags();out<<'"'<<std::hex<<word<<'"';out.flags(flags);
}
void check_identities(std::ostream& out){
    int cases=0,companions=0,omission_controls=0;
    for(int p:{2,3,5,7})for(int n:{1,2,4,7}){
        Poly row=constant(-1),h=constant(1),rhs,collision_sum,boolean_sum;
        std::vector<Poly> inputs;
        for(int j=0;j<n;j++){
            Poly x=variable(j),y=variable(n+j),d=x;add(d,y,-1,p);inputs.push_back(d);
            add(row,x,1,p);add(h,multiply(x,d,p),-1,p);
            Poly boolean=multiply(x,x,p);add(boolean,x,-1,p);add(boolean_sum,boolean,1,p);
            add(collision_sum,multiply(x,y,p),1,p);
        }
        add(rhs,row,-1,p);add(rhs,boolean_sum,-1,p);add(rhs,collision_sum,1,p);
        need(h==rhs && degree(h)==2,"ordinary normalization identity");
        Poly missing_collision=rhs;add(missing_collision,collision_sum,-1,p);
        Poly missing_boolean=rhs;add(missing_boolean,boolean_sum,1,p);
        need(h!=missing_collision && h!=missing_boolean,"vacuous omission control");omission_controls+=2;
        // Additional column forms vanish on the near-matching witnesses too.
        for(int j=0;j<n;j++){
            Poly c=constant(-1);
            for(int i=0;i<=n;i++)if(i!=1)add(c,variable(i*n+j),1,p);
            inputs.push_back(c);
        }
        out<<"{\"record\":\"normalization_identity\",\"p\":"<<p<<",\"n\":"<<n
           <<",\"pair\":[0,1],\"H\":";poly_json(out,h);out<<",\"rhs\":";poly_json(out,rhs);
        out<<",\"all_companion_images\":[";
        for(size_t i=0;i<inputs.size();i++){
            if(i)out<<',';
            Poly image=multiply(inputs[i],h,p),expanded;
            add(expanded,multiply(inputs[i],row,p),-1,p);
            add(expanded,multiply(inputs[i],boolean_sum,p),-1,p);
            add(expanded,multiply(inputs[i],collision_sum,p),1,p);
            need(image==expanded && degree(image)<=3,"companion image certificate");
            poly_json(out,image);companions++;
        }
        Poly x=variable(0),field=constant(1),geometric;
        for(int e=0;e<p;e++){
            if(e<=p-2)add(geometric,field,1,p);
            field=multiply(field,x,p);
        }
        add(field,x,-1,p);Poly boolean=multiply(x,x,p);add(boolean,x,-1,p);
        need(field==multiply(boolean,geometric,p) && degree(field)==p,"field image certificate");
        out<<"],\"field_image\":";poly_json(out,field);
        out<<",\"boolean_cofactor\":";poly_json(out,geometric);
        out<<",\"certificate_degree\":3,\"omission_controls\":2}\n";cases++;
    }
    out<<"{\"record\":\"identity_summary\",\"cases\":"<<cases
       <<",\"companion_images\":"<<companions<<",\"omission_controls\":"<<omission_controls<<"}\n";
    std::cout<<cases<<" ordinary identities, "<<companions<<" companion images, "
             <<omission_controls<<" omission controls.\n";
}
void check_matchings(std::ostream& out){
    constexpr int n=4,m=5;int cases=0;std::vector<int> by_size(n),matching(m,-1);
    std::function<void(int,int,int)> visit=[&](int next_row,int used,int q){
        std::vector<int> rows,holes;
        for(int i=0;i<m;i++)if(matching[i]<0)rows.push_back(i);
        for(int j=0;j<n;j++)if(!(used&(1<<j)))holes.push_back(j);
        need(rows.size()==holes.size()+1 && rows.size()>=2,"residual dimensions");
        std::vector<int> assignment=matching;assignment[rows[0]]=holes[0];assignment[rows[1]]=holes[0];
        for(size_t k=2;k<rows.size();k++)assignment[rows[k]]=holes[k-1];
        Word bits=0;std::vector<int> occupancy(n);
        for(int i=0;i<m;i++){
            need(assignment[i]>=0 && assignment[i]<n,"row assignment");
            if(matching[i]>=0)need(assignment[i]==matching[i],"matching not extended");
            bits|=Word(1)<<(i*n+assignment[i]);occupancy[assignment[i]]++;
        }
        for(int j=0;j<n;j++){
            need(((bits>>(rows[0]*n+j))&1)==((bits>>(rows[1]*n+j))&1),"row difference not zero");
            int merged=occupancy[j]-int(assignment[rows[1]]==j)-1;
            need(merged==0,"extra column input not zero");
            need(occupancy[j]==(j==holes[0]?2:1),"near-matching collision pattern");
        }
        out<<"{\"record\":\"matching_witness\",\"n\":4,\"q\":"<<q<<",\"matching\":[";
        bool comma=false;for(int i=0;i<m;i++)if(matching[i]>=0){
            if(comma)out<<',';
            comma=true;out<<'['<<i<<','<<matching[i]<<']';
        }
        out<<"],\"unmatched_pair\":["<<rows[0]<<','<<rows[1]<<"],\"assignment_bits\":";
        hexword(out,bits);out<<",\"row_and_input_equations_zero\":true}\n";
        cases++;by_size[q]++;
        if(q==n-1)return;
        for(int i=next_row;i<m;i++)for(int j=0;j<n;j++)if(!(used&(1<<j))){
            matching[i]=j;visit(i+1,used|(1<<j),q+1);matching[i]=-1;
        }
    };
    visit(0,0,0);need(by_size==std::vector<int>({1,20,120,240}),"partial matching coverage");
    out<<"{\"record\":\"matching_summary\",\"n\":4,\"cases\":"<<cases
       <<",\"by_size\":[1,20,120,240],\"valid_over_every_prime\":true}\n";
    std::cout<<cases<<" matching obstructions, including every q<4 on the five-by-four board.\n";
}
Bits blank(int width){return Bits((width+63)/64);}
bool bit(const Bits& b,int i){return (b[i/64]>>(i%64))&1;}
void flip(Bits& b,int i){b[i/64]^=Word(1)<<(i%64);}
bool empty(const Bits& b){return std::all_of(b.begin(),b.end(),[](Word x){return x==0;});}
int dot(const Bits& a,const Bits& b){
    need(a.size()==b.size(),"dot width");int result=0;
    for(size_t i=0;i<a.size();i++)result^=__builtin_parityll(a[i]&b[i]);
    return result;
}
void bits_json(std::ostream& out,const Bits& b){
    out<<'[';for(size_t i=0;i<b.size();i++){if(i)out<<',';hexword(out,b[i]);}out<<']';
}
struct BinarySpace{
    int width,rank=0;std::vector<Bits> rows;
    explicit BinarySpace(int w):width(w),rows(w){need(w>0 && w<5000,"matrix width guard");}
    Bits reduce(Bits value) const{
        need(value.size()==size_t((width+63)/64),"row width");
        for(int i=width-1;i>=0;i--)if(bit(value,i) && !rows[i].empty()){
            for(int j=0;j<=i/64;j++)value[j]^=rows[i][j];
        }
        return value;
    }
    bool add(Bits value){
        value=reduce(std::move(value));
        for(int i=width-1;i>=0;i--)if(bit(value,i)){rows[i]=std::move(value);rank++;return true;}
        return false;
    }
    Bits normalized_dual() const{
        need(rows[0].empty(),"constant is in the span");Bits result=blank(width);flip(result,0);
        for(int i=1;i<width;i++)if(!rows[i].empty() && dot(rows[i],result))flip(result,i);
        for(const Bits& row:rows)if(!row.empty())need(dot(row,result)==0,"basis dual check");
        return result;
    }
};
struct Board{
    static constexpr int n=7,m=8,variables=56;
    int width;std::vector<std::pair<int,int>> monomials;
    std::vector<std::vector<int>> products;
    Board():products(variables,std::vector<int>(variables,-1)){
        monomials.push_back({-1,-1});
        for(int i=0;i<variables;i++)monomials.push_back({i,-1});
        for(int i=0;i<variables;i++)for(int j=i;j<variables;j++){
            if(i==j)products[i][j]=i+1;
            else if(i%n!=j%n){products[i][j]=int(monomials.size());monomials.push_back({i,j});}
            products[j][i]=products[i][j];
        }
        width=int(monomials.size());need(width==1401,"normal monomial count");
        need(products[0][1]>=0 && products[0][n]<0,"same-row/column distinction");
    }
    Bits lift(Word affine) const{
        need((affine>>57)==0,"affine width guard");Bits result=blank(width);result[0]=affine;return result;
    }
    Bits multiply_affine(Word affine,int v) const{
        Bits result=blank(width);if(affine&1)flip(result,v+1);
        for(int i=0;i<variables;i++)if((affine>>(i+1))&1){
            int id=products[v][i];if(id>=0)flip(result,id);
        }
        return result;
    }
    std::vector<Bits> multiples(Word affine) const{
        std::vector<Bits> result{lift(affine)};
        for(int i=0;i<variables;i++)result.push_back(multiply_affine(affine,i));
        return result;
    }
};
std::vector<std::vector<Word>> read_spaces(const std::string& path){
    std::ifstream input(path);need(bool(input),"cannot read saved input certificate");
    std::vector<std::vector<Word>> spaces(7);std::string line;int found=0;
    // The fixed, documented producer schema uses one compact JSON record per line.
    while(std::getline(input,line))if(line.find("\"record\":\"accepted_space\"")!=std::string::npos){
        need(line.size()<10000,"input line guard");
        auto a=line.find("\"alpha\":");auto start=line.find("\"inputs\":[");
        need(a!=std::string::npos && start!=std::string::npos,"saved space schema");
        int alpha=std::stoi(line.substr(a+8));need(alpha>=0 && alpha<7 && spaces[alpha].empty(),"space index");
        start+=10;auto end=line.find(']',start);need(end!=std::string::npos,"input array end");
        while(start<end){
            auto quote=line.find('"',start);if(quote==std::string::npos || quote>=end)break;
            auto close=line.find('"',quote+1);need(close<end,"hex word terminator");
            std::string token=line.substr(quote+1,close-quote-1);size_t used=0;
            Word value=std::stoull(token,&used,16);need(used==token.size() && (value>>48)==0,"input word");
            spaces[alpha].push_back(value);start=close+1;
        }
        need(spaces[alpha].size()==24,"input rank-width count");found++;
    }
    need(found==7 && input.eof(),"missing input spaces or read error");return spaces;
}
void check_spread(std::ostream& out,const std::string& path){
    Board board;BinarySpace base(board.width);std::vector<Bits> base_generators;
    for(int i=0;i<Board::m;i++){
        Word row=1;for(int j=0;j<Board::n;j++)row^=Word(1)<<(1+i*Board::n+j);
        for(Bits generator:board.multiples(row)){base.add(generator);base_generators.push_back(std::move(generator));}
    }
    int affine_rank=0;for(int i=0;i<=Board::variables;i++)if(!base.rows[i].empty())affine_rank++;
    need(base.rank==420 && affine_rank==8,"base C2 closure/rank check");
    need(!empty(base.reduce(board.lift(1))),"base degree-two refutation");
    out<<"{\"record\":\"degree_two_base\",\"p\":2,\"n\":7,\"variables\":56,\"width\":"<<board.width
       <<",\"rank\":"<<base.rank<<",\"affine_rank\":"<<affine_rank<<",\"monomials\":[";
    for(size_t i=0;i<board.monomials.size();i++){
        if(i)out<<',';
        out<<'['<<board.monomials[i].first<<','<<board.monomials[i].second<<']';
    }
    out<<"]}\n";
    for(int i=0;i<board.width;i++)if(!base.rows[i].empty()){
        out<<"{\"record\":\"base_basis_row\",\"pivot\":"<<i<<",\"words\":";
        bits_json(out,base.rows[i]);out<<"}\n";
    }
    auto spaces=read_spaces(path);int obstructed=0,positive_controls=0;
    for(int alpha=0;alpha<7;alpha++){
        BinarySpace span=base;std::vector<Bits> generators=base_generators;std::vector<Word> old_inputs;
        for(Word source:spaces[alpha]){
            Word affine=0;
            for(int i=0;i<48;i++)if((source>>i)&1)affine^=Word(1)<<(1+(i/6)*7+i%6);
            old_inputs.push_back(affine);
            for(Bits generator:board.multiples(affine)){span.add(generator);generators.push_back(std::move(generator));}
        }
        bool normalizable=empty(span.reduce(board.lift(1)));
        out<<"{\"record\":\"spread_normalizer_test\",\"alpha\":"<<alpha
           <<",\"rank\":"<<span.rank<<",\"affine_coefficients_suffice\":"<<(normalizable?"true":"false")
           <<",\"old_affine_inputs\":[";
        for(size_t i=0;i<old_inputs.size();i++){if(i)out<<',';hexword(out,old_inputs[i]);}out<<']';
        if(!normalizable){
            Bits dual=span.normalized_dual();need(bit(dual,0),"dual normalization");
            for(const Bits& generator:generators)need(dot(generator,dual)==0,"original generator dual check");
            int altered=-1,failed=-1;
            for(int j=1;j<board.width && altered<0;j++){
                Bits corrupt=dual;flip(corrupt,j);
                for(size_t k=0;k<generators.size();k++)if(dot(generators[k],corrupt)){
                    altered=j;failed=int(k);break;
                }
            }
            need(altered>0 && failed>=0,"nonconstant corruption control");
            out<<",\"dual_words\":";bits_json(out,dual);
            out<<",\"checked_generators\":"<<generators.size()<<",\"corruption_coordinate\":"<<altered
               <<",\"corruption_failed_generator\":"<<failed;obstructed++;
        }
        out<<"}\n";
        std::cout<<"Spread "<<alpha<<": rank "<<span.rank<<'/'<<board.width
                 <<", affine normalizer "<<(normalizable?"FOUND":"excluded by checked dual")<<".\n";
    }
    for(int a=0;a<Board::m;a++)for(int b=a+1;b<Board::m;b++){
        BinarySpace span=base;
        for(int j=0;j<Board::n;j++){
            Word difference=(Word(1)<<(1+a*Board::n+j))^(Word(1)<<(1+b*Board::n+j));
            for(Bits generator:board.multiples(difference))span.add(std::move(generator));
        }
        need(empty(span.reduce(board.lift(1))),"collision-pair positive control");positive_controls++;
    }
    out<<"{\"record\":\"spread_summary\",\"spaces\":7,\"affine_normalizer_obstructions\":"<<obstructed
       <<",\"collision_pair_positive_controls\":"<<positive_controls<<"}\n";
}
int main(int argc,char** argv){
    try{
        std::string path,input;
        for(int i=1;i<argc;i++){
            std::string arg=argv[i];
            if(arg=="--out" && i+1<argc)path=argv[++i];
            else if(arg=="--inputs" && i+1<argc)input=argv[++i];
            else throw std::runtime_error("Usage: check_polynomial_normalization --inputs SAVED_JSONL --out NEW_PATH");
        }
        need(!input.empty() && !path.empty() && !std::filesystem::exists(path),"input and new --out required");
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"polynomial_normalization\",\"arithmetic\":\"exact\"}\n";
        check_identities(out);check_matchings(out);check_spread(out,input);
        out<<"{\"record\":\"summary\",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
