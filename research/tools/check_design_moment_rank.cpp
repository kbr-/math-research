// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact functional-PHP moment fillings and ranks; no polynomial-calculus closure.
#include "binary_php.hpp"
#include <filesystem>
#include <functional>
#include <map>
using namespace binary_php;

void hexword(std::ostream& out,Word x) {
    const auto flags=out.flags(); out<<'"'<<std::hex<<x<<'"'; out.flags(flags);
}
void integers(std::ostream& out,const std::vector<int>& v) {
    out<<'['; for(size_t i=0;i<v.size();++i){if(i)out<<',';out<<v[i];} out<<']';
}
struct Moments {
    int n,m,degree,variables;
    std::string name;
    std::vector<Word> monomials;
    std::unordered_map<Word,int> ids;
    std::vector<int> values;
    Moments(int holes,int rows,int d,std::string label)
        :n(holes),m(rows),degree(d),variables(n*m),name(std::move(label)) {
        need(variables<64 && d>=2 && d<=4,"Fixed finite fixture guard");
        for(int size=0;size<=d;++size) {
            std::function<void(int,int,unsigned,unsigned,Word)> enumerate=
            [&](int start,int left,unsigned used_rows,unsigned used_cols,Word mask) {
                if(!left){monomials.push_back(mask);return;}
                for(int x=start;x<variables;++x)
                    if(!(used_rows&(1u<<(x/n))) && !(used_cols&(1u<<(x%n))))
                        enumerate(x+1,left-1,used_rows|(1u<<(x/n)),
                                  used_cols|(1u<<(x%n)),mask|(Word(1)<<x));
            };
            enumerate(0,size,0,0,0);
        }
        for(int i=0;i<int(monomials.size());++i)
            need(ids.emplace(monomials[i],i).second,"Duplicate matching");
        values.assign(monomials.size(),0); values[0]=1;
    }
    int value(Word monomial) const {
        auto found=ids.find(monomial);
        return found==ids.end()?0:values[found->second];
    }
    unsigned rows(Word monomial) const {
        unsigned answer=0;
        while(monomial) {
            int x=__builtin_ctzll(monomial);monomial&=monomial-1;
            answer|=1u<<(x/n);
        }
        return answer;
    }
    void quadratic(const std::vector<int>& destination,Word u,Word v) {
        Word mean=0;
        for(int i=0;i<m;++i)mean|=Word(1)<<(i*n+destination[i]);
        for(int k=1;k<int(monomials.size());++k) {
            Word mask=monomials[k];int d=__builtin_popcountll(mask);
            if(d>2)break;
            int answer=(mask&mean)==mask;
            if(d==2) {
                int a=__builtin_ctzll(mask),b=__builtin_ctzll(mask&(mask-1));
                answer^=((u>>a)&(v>>b)&1)^((v>>a)&(u>>b)&1);
            }
            values[k]=answer;
        }
        for(int a=0;a<variables;++a)for(int b=0;b<variables;++b) {
            int actual=value((Word(1)<<a)|(Word(1)<<b))
                       ^(value(Word(1)<<a)&value(Word(1)<<b));
            int expected=((u>>a)&(v>>b)&1)^((v>>a)&(u>>b)&1);
            need(actual==expected,"Quadratic covariance differs from prescribed wedge");
        }
    }
    void extend(std::ostream& out) {
        for(int k=3;k<=degree;++k) {
            std::map<unsigned,std::vector<Word>> groups;
            for(Word mask:monomials)
                if(__builtin_popcountll(mask)==k)groups[rows(mask)].push_back(mask);
            for(const auto& [row_set,top]:groups) {
                const int width=int(top.size())+1;
                std::map<Word,Bits> faces;
                for(int j=0;j<int(top.size());++j) {
                    Word remaining=top[j];
                    while(remaining) {
                        int x=__builtin_ctzll(remaining);remaining&=remaining-1;
                        Word face=top[j]^(Word(1)<<x);
                        auto [it,inserted]=faces.try_emplace(face);
                        if(inserted)it->second=blank(width);
                        flip(it->second,j+1);
                    }
                }
                Space equations(width);
                for(auto& [face,equation]:faces) {
                    if(value(face))flip(equation,0);
                    equations.add(equation);
                }
                need(equations.rows[0].empty(),"Boundary filling inconsistent");
                Bits seed=blank(width);flip(seed,0);
                Bits solution=equations.complete_dual(std::move(seed));
                for(const auto& [face,equation]:faces)
                    need(dot(equation,solution)==0,"Original face equation failed");
                for(int j=0;j<int(top.size());++j)values[ids.at(top[j])]=bit(solution,j+1);
                out<<"{\"record\":\"filling\",\"case\":\""<<name<<"\",\"degree\":"<<k
                   <<",\"row_mask\":";hexword(out,row_set);
                out<<",\"unknowns\":"<<top.size()<<",\"face_equations\":"<<faces.size()
                   <<",\"equation_rank\":"<<equations.rank
                   <<",\"free_choice\":\"all zero except normalized RHS coordinate\"}\n";
            }
        }
    }
    void validate_and_save(std::ostream& out) const {
        long checks=0;
        need(value(0)==1,"Normalization");
        for(Word mask:monomials) if(__builtin_popcountll(mask)<degree)
            for(int i=0;i<m;++i) {
                int answer=value(mask);
                for(int j=0;j<n;++j)answer^=value(mask|(Word(1)<<(i*n+j)));
                need(answer==0,"NS row multiple failed");++checks;
            }
        for(int j=0;j<int(monomials.size());++j) {
            out<<"{\"record\":\"moment\",\"case\":\""<<name<<"\",\"mask\":";
            hexword(out,monomials[j]);out<<",\"value\":"<<values[j]<<"}\n";
        }
        out<<"{\"record\":\"NS_validation\",\"case\":\""<<name<<"\",\"holes\":"<<n
           <<",\"rows\":"<<m<<",\"degree\":"<<degree
           <<",\"matching_moments\":"<<monomials.size()<<",\"row_multiples_checked\":"<<checks
           <<",\"all_passed\":true}\n";
        std::cout<<name<<": "<<monomials.size()<<" moments, "<<checks
                 <<" row multiples verified.\n";
    }
    int matrix_rank(std::ostream& out,int t,bool centered) const {
        int width=0;
        while(width<int(monomials.size()) && __builtin_popcountll(monomials[width])<=t)++width;
        Space space(width);
        for(int i=0;i<width;++i) {
            Bits row=blank(width);
            for(int j=0;j<width;++j) {
                int answer=value(monomials[i]|monomials[j]);
                if(centered)answer^=values[i]&values[j];
                if(answer)flip(row,j);
            }
            if(centered)need(!bit(row,i),"Centered moment diagonal is nonzero");
            std::vector<int> trace;
            int pivot=space.add(std::move(row),&trace);
            out<<"{\"record\":\"rank_step\",\"case\":\""<<name<<"\",\"t\":"<<t
               <<",\"centered\":"<<(centered?"true":"false")
               <<",\"row\":"<<i<<",\"pivot\":"<<pivot<<",\"xor_pivots\":";
            integers(out,trace);out<<",\"reduced_support\":";
            if(pivot<0)out<<"[]";else sparse_json(out,space.rows[pivot]);
            out<<"}\n";
        }
        if(centered)need(space.rank%2==0,"Alternating binary rank parity");
        return space.rank;
    }
    void ranks(std::ostream& out,bool unsatisfiable) const {
        int previous=0;
        for(int t=0;t<=degree/2;++t) {
            int gram=matrix_rank(out,t,false),cov=matrix_rank(out,t,true);
            need(gram==1+cov,"Centered rank decomposition");
            if(unsatisfiable) {
                need(gram>=2*t+1 && gram>previous,"Moment-rank growth bound");
                if(t==1)need(cov==2,"Prescribed rank-two covariance changed");
            } else need(gram==1 && cov==0,"Satisfiable point must remain flat");
            previous=gram;
            out<<"{\"record\":\"rank_summary\",\"case\":\""<<name<<"\",\"t\":"<<t
               <<",\"gram_rank\":"<<gram<<",\"covariance_rank\":"<<cov<<"}\n";
            std::cout<<name<<": t="<<t<<", Gram rank "<<gram<<", covariance rank "<<cov<<".\n";
        }
    }
};
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","Usage: checker --out PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"Refusing to replace prior evidence");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"Cannot create output");
        out<<"{\"record\":\"schema\",\"field\":2,\"variable_index\":\"i*n+j\","
              "\"normal_form\":\"partial matching monomials; excluded products zero; repeated cells idempotent\","
              "\"scope\":\"one degree-four rank-two extension, a two-collision quadratic control, "
              "and a satisfiable flat point; all ranks use exact XOR elimination\"}\n";
        Moments extended(7,8,4,"seven_hole_quartic");
        extended.quadratic({0,0,1,2,3,4,5,6},(Word(1)<<0)|(Word(1)<<1),
                           (Word(1)<<7)|(Word(1)<<9));
        extended.extend(out);extended.validate_and_save(out);extended.ranks(out,true);

        Moments alternative(5,6,2,"two_collisions_one_empty");
        Word u=0,v=0;
        for(int x:{0,2,11,12})u|=Word(1)<<x;
        for(int x:{5,8,16,18,23,24,28,29})v|=Word(1)<<x;
        alternative.quadratic({0,0,1,1,3,4},u,v);
        alternative.validate_and_save(out);alternative.ranks(out,true);
        out<<"{\"record\":\"one_collision_promise_control\",\"case\":\"two_collisions_one_empty\","
              "\"column_defects\":[1,1,1,0,0],\"first_subset\":[0,1],\"first_answer\":0,"
              "\"second_subset\":[2],\"second_answer\":1,\"selected_empty_column\":2,"
              "\"row_label_XOR\":0,\"scope\":\"the earlier promised search does not cover this mean\"}\n";

        Moments point(3,3,4,"satisfiable_injection");
        Word assignment=(Word(1)<<0)|(Word(1)<<4)|(Word(1)<<8);
        for(int i=0;i<int(point.monomials.size());++i)
            point.values[i]=(point.monomials[i]&assignment)==point.monomials[i];
        point.validate_and_save(out);point.ranks(out,false);
        out<<"{\"record\":\"summary\",\"all_passed\":true}\n";
        out.close();need(bool(out),"Output write failed");
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
