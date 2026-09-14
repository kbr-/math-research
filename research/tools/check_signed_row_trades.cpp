// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact spanning certificates for signed row trades on injection boards.
#include <algorithm>
#include <boost/multiprecision/cpp_int.hpp>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>

using Row = std::vector<int>;
using Matrix = std::vector<Row>;
using Sparse = std::vector<std::pair<int,int>>;
using Bits = std::vector<uint64_t>;
using boost::multiprecision::cpp_int;
void need(bool value,const char* message) {
    if(!value) throw std::runtime_error(message);
}
void json_row(std::ostream& out,const Row& row) {
    out<<'[';
    for(unsigned i=0;i<row.size();++i) { if(i)out<<','; out<<row[i]; }
    out<<']';
}
void json_matrix(std::ostream& out,const Matrix& rows) {
    out<<'[';
    for(unsigned i=0;i<rows.size();++i) { if(i)out<<','; json_row(out,rows[i]); }
    out<<']';
}
void json_sparse(std::ostream& out,const Sparse& row) {
    out<<'[';
    for(unsigned i=0;i<row.size();++i) {
        if(i)out<<',';
        out<<'['<<row[i].first<<','<<row[i].second<<']';
    }
    out<<']';
}
void json_bits(std::ostream& out,const Bits& row,int words) {
    out<<'[';
    for(int i=0;i<words;++i) {
        if(i)out<<',';
        std::ostringstream word;
        word<<std::hex<<std::setw(16)<<std::setfill('0')<<row[i];
        out<<'"'<<word.str()<<'"';
    }
    out<<']';
}
int code(const Row& tuple,int n) {
    int value=0;
    for(int x:tuple)value=value*n+x;
    return value;
}
int ipow(int base,int exponent) {
    int value=1;
    for(int i=0;i<exponent;++i)value*=base;
    return value;
}
Matrix injections(int r,int n) {
    Matrix result;
    Row row(r);
    std::function<void(int,unsigned)> visit=[&](int i,unsigned used) {
        if(i==r) { result.push_back(row); return; }
        for(int j=0;j<n;++j) if(!(used&(1u<<j))) {
            row[i]=j; visit(i+1,used|(1u<<j));
        }
    };
    visit(0,0);
    return result;
}
struct Geometry {
    int r,n,columns;
    Matrix faces,missing_faces;
    Row face_index,missing_index,missing_rows;
    std::vector<Sparse> marginal,trade;
    std::vector<Matrix> pairs;
    Geometry(int rows,int labels):r(rows),n(labels),faces(injections(r,n)),
        face_index(ipow(n,r),-1),missing_index(r*ipow(n,r-1),-1) {
        columns=faces.size();
        for(int i=0;i<columns;++i)face_index[code(faces[i],n)]=i;
        auto lower=injections(r-1,n);
        for(int i=0;i<r;++i)for(const auto& f:lower) {
            missing_index[i*ipow(n,r-1)+code(f,n)]=missing_faces.size();
            missing_faces.push_back(f); missing_rows.push_back(i);
        }
        marginal.resize(missing_faces.size());
        for(int j=0;j<columns;++j)for(int i=0;i<r;++i)
            marginal[boundary_row(faces[j],i)].push_back({j,1});
        Matrix current(r,Row(2));
        std::function<void(int,unsigned)> visit=[&](int i,unsigned used) {
            if(i==r) {
                Sparse row;
                for(int mask=0;mask<(1<<r);++mask) {
                    Row f(r);
                    for(int u=0;u<r;++u)f[u]=current[u][(mask>>u)&1];
                    row.push_back({face_index[code(f,n)],
                                   __builtin_popcount(unsigned(mask))%2?-1:1});
                }
                std::sort(row.begin(),row.end());
                balanced(row);
                trade.push_back(row); pairs.push_back(current); return;
            }
            for(int a=0;a<n;++a)if(!(used&(1u<<a)))
                for(int b=a+1;b<n;++b)if(!(used&(1u<<b))) {
                    current[i]={a,b};
                    visit(i+1,used|(1u<<a)|(1u<<b));
                }
        };
        visit(0,0);
    }
    int boundary_row(const Row& face,int missing) const {
        Row lower;
        for(int i=0;i<r;++i)if(i!=missing)lower.push_back(face[i]);
        return missing_index[missing*ipow(n,r-1)+code(lower,n)];
    }
    void balanced(const Sparse& vector) const {
        Row sums(missing_faces.size());
        for(auto [id,value]:vector)for(int i=0;i<r;++i)
            sums[boundary_row(faces[id],i)]+=value;
        need(std::all_of(sums.begin(),sums.end(),[](int x){return x==0;}),
             "exact integer row marginals vanish");
    }
    std::string key() const { return "r"+std::to_string(r)+"_n"+std::to_string(n); }
    void write(std::ostream& out) const {
        out<<"{\"record\":\"geometry\",\"key\":\""<<key()<<"\",\"rows\":"<<r
           <<",\"columns\":"<<n<<",\"faces\":";
        json_matrix(out,faces);
        out<<",\"marginal_missing_rows\":"; json_row(out,missing_rows);
        out<<",\"marginal_remaining_labels\":"; json_matrix(out,missing_faces);
        out<<",\"marginal_matrix\":[";
        for(unsigned i=0;i<marginal.size();++i) {
            if(i)out<<',';
            json_sparse(out,marginal[i]);
        }
        out<<"],\"trade_pairs\":[";
        for(unsigned i=0;i<pairs.size();++i) {
            if(i)out<<',';
            json_matrix(out,pairs[i]);
        }
        out<<"],\"trade_matrix\":[";
        for(unsigned i=0;i<trade.size();++i) {
            if(i)out<<',';
            json_sparse(out,trade[i]);
        }
        out<<"],\"all_trade_marginals_zero_over_integers\":true}\n";
    }
};
int first_bit(const Bits& bits) {
    for(unsigned i=0;i<bits.size();++i)if(bits[i])
        return 64*i+__builtin_ctzll(bits[i]);
    return -1;
}
bool bit(const Bits& row,int column) { return (row[column/64]>>(column%64))&1u; }
void toggle(Bits& row,int column) { row[column/64]^=uint64_t(1)<<(column%64); }
void add_bits(Bits& into,const Bits& other) {
    for(unsigned i=0;i<into.size();++i)into[i]^=other[i];
}
Bits binary_row(const Sparse& row,int columns) {
    Bits result((columns+63)/64);
    for(auto [i,c]:row)if(c%2)toggle(result,i);
    return result;
}
int rank_binary(std::ostream& out,const Geometry& g,const char* name,
                const std::vector<Sparse>& rows) {
    const int max_rank=std::min<int>(rows.size(),g.columns);
    Row where(g.columns,-1),pivots,accepted;
    std::vector<Bits> basis,coordinates;
    for(unsigned i=0;i<rows.size();++i) {
        Bits x=binary_row(rows[i],g.columns),c((max_rank+63)/64);
        for(int pivot=first_bit(x);pivot>=0;pivot=first_bit(x)) {
            int id=where[pivot];
            if(id<0) {
                id=basis.size(); where[pivot]=id;
                pivots.push_back(pivot); accepted.push_back(i);
                basis.push_back(x); toggle(c,id); break;
            }
            add_bits(x,basis[id]); toggle(c,id);
        }
        coordinates.push_back(c);
    }
    const int rank=basis.size();
    for(unsigned i=0;i<rows.size();++i) {
        Bits reconstructed((g.columns+63)/64);
        for(int j=0;j<rank;++j)if(bit(coordinates[i],j))
            add_bits(reconstructed,basis[j]);
        need(reconstructed==binary_row(rows[i],g.columns),"binary A=C*B factorization");
    }
    for(int j=0;j<rank;++j) {
        need(first_bit(basis[j])==pivots[j],"distinct leading pivot");
        need(bit(coordinates[accepted[j]],j),"accepted triangular diagonal");
        for(int k=j+1;k<rank;++k)
            need(!bit(coordinates[accepted[j]],k),"accepted triangular upper zero");
    }
    out<<"{\"record\":\"rank_factorization\",\"geometry\":\""<<g.key()
       <<"\",\"matrix\":\""<<name<<"\",\"prime\":2,\"rank\":"<<rank
       <<",\"encoding\":\"little-endian arrays of 64-bit hexadecimal words; bit i is column i\","
         "\"basis_rows\":[";
    for(int j=0;j<rank;++j) {
        if(j)out<<',';
        json_bits(out,basis[j],(g.columns+63)/64);
    }
    out<<"],\"coordinates\":[";
    for(unsigned i=0;i<coordinates.size();++i) {
        if(i)out<<',';
        json_bits(out,coordinates[i],(rank+63)/64);
    }
    out<<"],\"pivots\":";json_row(out,pivots);
    out<<",\"accepted_input_rows\":";json_row(out,accepted);
    out<<",\"factorization_and_independence_checked\":true}\n";
    return rank;
}
int powmod(int a,int exponent,int p) {
    int result=1;
    for(;exponent;exponent>>=1,a=a*a%p)
        if(exponent&1)result=result*a%p;
    return result;
}
Row field_row(const Sparse& row,int columns,int p) {
    Row result(columns);
    for(auto [i,c]:row)result[i]=(c%p+p)%p;
    return result;
}
int rank_field(std::ostream& out,const Geometry& g,const char* name,
               const std::vector<Sparse>& rows,int p) {
    if(p==2)return rank_binary(out,g,name,rows);
    const int max_rank=std::min<int>(rows.size(),g.columns);
    Row where(g.columns,-1),pivots,accepted;
    Matrix basis,coordinates;
    for(unsigned i=0;i<rows.size();++i) {
        Row x=field_row(rows[i],g.columns,p),c(max_rank);
        for(int pivot=0;pivot<g.columns;++pivot)if(x[pivot]) {
            int id=where[pivot],coefficient=x[pivot];
            if(id<0) {
                id=basis.size(); where[pivot]=id;
                int inverse=powmod(coefficient,p-2,p);
                for(int& v:x)v=v*inverse%p;
                basis.push_back(x);pivots.push_back(pivot);accepted.push_back(i);
                c[id]=coefficient;break;
            }
            for(int j=pivot;j<g.columns;++j)
                x[j]=(x[j]-coefficient*basis[id][j]%p+p)%p;
            c[id]=(c[id]+coefficient)%p;
        }
        coordinates.push_back(c);
    }
    int rank=basis.size();
    for(auto& c:coordinates)c.resize(rank);
    for(unsigned i=0;i<rows.size();++i) {
        Row reconstructed(g.columns);
        for(int j=0;j<rank;++j)if(coordinates[i][j])
            for(int col=0;col<g.columns;++col)
                reconstructed[col]=(reconstructed[col]+coordinates[i][j]*basis[j][col])%p;
        need(reconstructed==field_row(rows[i],g.columns,p),"prime-field A=C*B factorization");
    }
    for(int j=0;j<rank;++j) {
        need(basis[j][pivots[j]]==1,"normalized field pivot");
        for(int k=0;k<pivots[j];++k)need(!basis[j][k],"leading field pivot");
        need(coordinates[accepted[j]][j]!=0,"invertible accepted diagonal");
        for(int k=j+1;k<rank;++k)
            need(!coordinates[accepted[j]][k],"accepted upper coefficients zero");
    }
    out<<"{\"record\":\"rank_factorization\",\"geometry\":\""<<g.key()
       <<"\",\"matrix\":\""<<name<<"\",\"prime\":"<<p<<",\"rank\":"<<rank
       <<",\"encoding\":\"ordinary residue matrices\",\"basis_rows\":";
    json_matrix(out,basis);out<<",\"coordinates\":";json_matrix(out,coordinates);
    out<<",\"pivots\":";json_row(out,pivots);
    out<<",\"accepted_input_rows\":";json_row(out,accepted);
    out<<",\"factorization_and_independence_checked\":true}\n";
    return rank;
}
cpp_int ceil_sqrt(const cpp_int& x) {
    cpp_int high=1;
    while(high*high<x)high<<=1;
    cpp_int low=0;
    while(low+1<high) {
        cpp_int mid=(low+high)/2;
        if(mid*mid>=x)high=mid;else low=mid;
    }
    need(high*high>=x && (high-1)*(high-1)<x,"exact integer square-root ceiling");
    return high;
}
void parameters(std::ostream& out) {
    for(int ell:{16,32,48,64})for(int p:{2,3,5}) {
        cpp_int n=cpp_int(1)<<ell,m=n+1,D=cpp_int(ell)*ell*ell,t=D;
        cpp_int M=n*n,H=2*ell+2;
        cpp_int k=std::max(cpp_int(2*t),ceil_sqrt(m*H));
        cpp_int B=k*(D+1),h=3*(p-1)*ell;
        bool range=k<=m-t,packing=4*(k+t-1)<n,room=n>=2*B-1;
        need(range && packing && room==(ell>=48),"positive and negative target-room controls");
        need(D>=2*h+1 && t>=ell,"original source and enlarged target-window controls");
        out<<"{\"record\":\"relative_target_parameters\",\"ell\":"<<ell<<",\"prime\":"<<p
           <<",\"n\":\""<<n<<"\",\"M\":\""<<M<<"\",\"h\":\""<<h<<"\",\"D\":\""<<D
           <<"\",\"t\":\""<<t<<"\",\"H\":\""<<H<<"\",\"k\":\""<<k<<"\",\"B\":\""<<B
           <<"\",\"range_condition\":true,\"packing_condition\":true,\"old_degree_condition\":"
           <<(room?"true":"false")<<",\"passed\":true}\n";
    }
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"output already exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"sparse_rows\":\"[column,integer coefficient]\","
             "\"rank_certificate\":\"A=C*B, distinct leading pivots in B, invertible lower triangular C on accepted rows\","
             "\"large_integers\":\"exact decimal strings\"}\n";
        int cases=0;
        for(auto [r,n]:std::vector<std::pair<int,int>>{{1,3},{2,3},{2,4},{3,5},{3,6},{3,7},{4,8}}) {
            Geometry g(r,n);g.write(out);
            for(int p: r==4?Row{2}:Row{2,3,5}) {
                int marginal=rank_field(out,g,"marginals",g.marginal,p);
                int trades=rank_field(out,g,"trades",g.trade,p);
                int cycle=g.columns-marginal;
                bool spans=trades==cycle;
                need(spans==(n>=2*r),"trade spanning threshold control");
                if(n<2*r)need(cycle>0 && g.trade.empty(),"thin board has a nonzero cycle but no disjoint row pairs");
                out<<"{\"record\":\"case_summary\",\"rows\":"<<r<<",\"columns\":"<<n<<",\"prime\":"<<p
                   <<",\"top_faces\":"<<g.columns<<",\"marginal_rank\":"<<marginal<<",\"cycle_dimension\":"<<cycle
                   <<",\"trade_count\":"<<g.trade.size()<<",\"trade_rank\":"<<trades<<",\"spans\":"
                   <<(spans?"true":"false")<<",\"passed\":true}\n";
                ++cases;
            }
        }
        parameters(out);
        need(cases==19,"complete field-case count");
        out<<"{\"record\":\"summary\",\"geometries\":7,\"field_cases\":19,\"rank_factorizations\":38,"
             "\"parameter_cases\":12,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Signed row trades: 19 field cases, 38 exact rank factorizations, "
                    "and 12 parameter cases passed.\n";
        return 0;
    }catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
