// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact ordinary-PHP degree-two spaces and target-weighted overlap identities.
// Run through compute.sh. Complete sparse bases are written to --out NEW_PATH.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Row=std::vector<std::uint8_t>;
using Sparse=std::vector<std::pair<int,int>>;
void need(bool ok,const std::string& message){if(!ok)throw std::runtime_error(message);}
int residue(int a,int p){a%=p;return a<0?a+p:a;}
int power(int a,int e,int p){int r=1;while(e--)r=r*a%p;return r;}
bool zero(const Row& row){return std::all_of(row.begin(),row.end(),[](auto c){return c==0;});}
void sparse_json(std::ostream& out,const Sparse& row){
    out<<'[';
    for(size_t i=0;i<row.size();i++){if(i)out<<',';out<<'['<<row[i].first<<','<<row[i].second<<']';}
    out<<']';
}
struct Basis {
    int p,columns,rank=0;
    size_t stored=0;
    std::array<std::array<int,8>,8> mul{};
    std::vector<Sparse> rows;
    Basis(int prime,int size):p(prime),columns(size),rows(size){
        need(p<=7 && columns<=20000,"matrix size/field guard");
        for(int a=0;a<p;a++)for(int b=0;b<p;b++)mul[a][b]=a*b%p;
    }
    Row reduce(Row row) const {
        need(int(row.size())==columns,"matrix width mismatch");
        for(int pivot=columns-1;pivot>=0;pivot--){
            int c=row[pivot];if(!c || rows[pivot].empty())continue;
            for(const auto& cell:rows[pivot]){
                int v=int(row[cell.first])-mul[c][cell.second];
                row[cell.first]=static_cast<std::uint8_t>(v<0?v+p:v);
            }
        }
        return row;
    }
    bool add(Row row){
        row=reduce(std::move(row));
        int pivot=columns-1;while(pivot>=0 && !row[pivot])pivot--;
        if(pivot<0)return false;
        int inv=power(row[pivot],p-2,p);Sparse result;
        for(int i=0;i<=pivot;i++)if(row[i])result.push_back({i,mul[inv][row[i]]});
        stored+=result.size();need(stored<=5000000,"sparse basis storage guard");
        rows[pivot]=std::move(result);rank++;return true;
    }
    void write(std::ostream& out,const std::string& name) const {
        for(int i=0;i<columns;i++)if(!rows[i].empty()){
            out<<"{\"record\":\"basis_row\",\"space\":\""<<name<<"\",\"pivot\":"<<i<<",\"cells\":";
            sparse_json(out,rows[i]);out<<"}\n";
        }
    }
};
struct Board {
    int n,m,variables,columns;
    std::vector<std::pair<int,int>> monomials;
    std::vector<std::vector<int>> product;
    explicit Board(int holes):n(holes),m(n+1),variables(m*n),
        product(variables,std::vector<int>(variables,-1)){
        need(variables<=256,"board variable guard");
        monomials.push_back({-1,-1});
        for(int i=0;i<variables;i++)monomials.push_back({i,-1});
        for(int i=0;i<variables;i++)for(int j=i;j<variables;j++){
            if(i==j)product[i][j]=i+1; // Boolean reduction x_i^2 -> x_i.
            else if(i%n!=j%n){
                product[i][j]=int(monomials.size());monomials.push_back({i,j});
            } // Different rows in one column vanish. Same-row products remain.
            product[j][i]=product[i][j];
        }
        columns=int(monomials.size());
    }
    Row row_axiom(int i,int p) const {
        Row r(variables+1);r[0]=p-1;
        for(int j=0;j<n;j++)r[1+i*n+j]=1;
        return r;
    }
    Row lift_affine(const Row& f) const {
        Row r(columns);std::copy(f.begin(),f.end(),r.begin());return r;
    }
    Row multiply_affine(const Row& f,int variable,int p) const {
        Row r(columns);r[variable+1]=f[0];
        for(int i=0;i<variables;i++){
            int id=product[variable][i];
            if(id>=0)r[id]=static_cast<std::uint8_t>((r[id]+f[i+1])%p);
        }
        return r;
    }
};
void check_php(std::ostream& out,int p){
    // q=1, c=2, n=p+5 is the boundary c=(n-q-p)/2 of the new theorem.
    Board board(p+5);Basis consequences(p,board.columns);
    for(int i=0;i<board.m;i++){
        Row row=board.row_axiom(i,p);consequences.add(board.lift_affine(row));
        for(int v=0;v<board.variables;v++)consequences.add(board.multiply_affine(row,v,p));
    }
    int affine_rank=0;
    for(int i=0;i<=board.variables;i++)if(!consequences.rows[i].empty())affine_rank++;
    // This certifies closure at degree two: the only affine consequences are
    // row equations, all of whose variable multiples have already been added.
    need(affine_rank==board.m,"unexpected affine PC consequence");
    Row constant(board.columns);constant[0]=1;
    need(!zero(consequences.reduce(constant)),"unexpected degree-two refutation");
    Basis image(p,board.columns);
    for(int i=0;i<=board.variables;i++){
        Row f(board.variables+1);f[i]=1;
        image.add(consequences.reduce(board.multiply_affine(f,0,p)));
    }
    int kernel_dimension=board.variables+1-image.rank;
    Basis annihilators(p,board.variables+1);
    auto add_candidate=[&](Row f){
        need(zero(consequences.reduce(board.multiply_affine(f,0,p))),"candidate not annihilated");
        annihilators.add(std::move(f));
    };
    for(int i=0;i<board.m;i++)add_candidate(board.row_axiom(i,p));
    for(int i=0;i<board.m;i++){
        Row f(board.variables+1);f[1+i*board.n]=1;if(i==0)f[0]=p-1;add_candidate(f);
    }
    need(annihilators.rank==2*board.m && kernel_dimension==annihilators.rank,"annihilator dimension mismatch");
    Row same_row(board.variables+1);same_row[2]=1; // f=x_(0,1), M=x_(0,0).
    need(board.product[0][1]>=0,"same-row exclusion inserted into normal form");
    need(!zero(consequences.reduce(board.multiply_affine(same_row,0,p))),"same-row collision incorrectly derivable");
    out<<"{\"record\":\"php_case\",\"p\":"<<p<<",\"n\":"<<board.n<<",\"m\":"<<board.m
       <<",\"q\":1,\"degree_ceiling\":2,\"variables\":"<<board.variables
       <<",\"normal_monomials\":"<<board.columns<<",\"normalized_C2_rank\":"<<consequences.rank
       <<",\"affine_consequence_rank\":"<<affine_rank<<",\"target_image_rank\":"<<image.rank
       <<",\"annihilator_dimension\":"<<kernel_dimension<<",\"predicted_dimension\":"<<2*board.m
       <<",\"same_row_collision_not_derived\":true,\"monomials\":[";
    for(size_t i=0;i<board.monomials.size();i++){
        if(i)out<<',';
        out<<'['<<board.monomials[i].first<<','<<board.monomials[i].second<<']';
    }
    out<<"]}\n";
    consequences.write(out,"normalized_C2");image.write(out,"target_image");
    annihilators.write(out,"affine_annihilator");
    out<<"{\"record\":\"php_case_passed\"}\n";
    std::cout<<"p="<<p<<", n="<<board.n<<": C2 rank "<<consequences.rank
             <<", affine annihilator dimension "<<kernel_dimension<<" (predicted "<<2*board.m<<").\n";
}
void check_subsets(std::ostream& out,int p){
    int n=p+2,count=0;Basis basis(p,n);
    for(int mask=0;mask<(1<<n);mask++)if(__builtin_popcount(static_cast<unsigned>(mask))==p){
        Row r(n);for(int i=0;i<n;i++)r[i]=(mask>>i)&1;basis.add(std::move(r));count++;
    }
    need(basis.rank==n-1,"p-subset kernel is larger than constants");
    for(const auto& row:basis.rows)if(!row.empty()){
        int sum=0;for(const auto& cell:row)sum+=cell.second;need(sum%p==0,"constant kernel lost");
    }
    out<<"{\"record\":\"subset_case\",\"p\":"<<p<<",\"coordinates\":"<<n
       <<",\"subset_count\":"<<count<<",\"rank\":"<<basis.rank<<",\"kernel_dimension\":1}\n";
    basis.write(out,"subset_incidence");
}
void coefficients_json(std::ostream& out,const std::vector<int>& poly,int xmax){
    out<<'[';bool comma=false;
    for(int x=0;x<=xmax;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
        int c=poly[4*x+2*y+z];if(!c)continue;
        if(comma)out<<',';
        comma=true;out<<'['<<c<<",["<<x<<','<<y<<','<<z<<"]]";
    }
    out<<']';
}
int check_overlap(std::ostream& out,int p){
    int count=0;
    for(int alpha=1;alpha<p;alpha++){
        int inv=power(alpha,p-2,p),xmax=p+1;
        std::vector<int> chi(p),lhs(4*(xmax+1)),rhs(lhs.size()),correction(lhs.size());
        int choose=1;
        for(int i=0;i<p;i++){
            chi[i]=residue((i==0?1:0)-choose*power(residue(-alpha,p),p-1-i,p),p);
            if(i<p-1)choose=choose*(p-1-i)/(i+1);
        }
        auto add=[&](std::vector<int>& poly,int x,int y,int z,int c){
            auto& v=poly.at(4*x+2*y+z);v=residue(v+c,p);
        };
        // f=t=x, later inputs (x+y,z), u=-y, and t*u=-xy is supplied.
        // Compare t*chi(x)*z*(1-alpha^-1*(x+y)) with its field and error terms.
        for(int i=0;i<p;i++){
            add(lhs,i+1,0,1,chi[i]);add(lhs,i+2,0,1,-inv*chi[i]);
            add(lhs,i+1,1,1,-inv*chi[i]);add(correction,i+1,1,1,-inv*chi[i]);
        }
        rhs=correction;add(rhs,p+1,0,1,inv);add(rhs,2,0,1,-inv);
        need(lhs==rhs,"weighted overlap coefficient identity");
        need(std::any_of(correction.begin(),correction.end(),[](int c){return c!=0;}),"vacuous missing-error control");
        int witness=0;
        for(int x=0;x<=xmax;x++)witness=residue(witness+correction[4*x+3]*power(alpha,x,p),p);
        need(witness==p-1,"missing-error witness at (alpha,1,1)");
        out<<"{\"record\":\"overlap_identity\",\"p\":"<<p<<",\"alpha\":"<<alpha
           <<",\"lhs\":";coefficients_json(out,lhs,xmax);
        out<<",\"rhs\":";coefficients_json(out,rhs,xmax);
        out<<",\"required_error\":";coefficients_json(out,correction,xmax);
        out<<",\"omitted_error_value_at_alpha_1_1\":"<<witness<<"}\n";count++;
    }
    return count;
}
std::vector<int> field_product(int a,int b,int p,int d,const std::vector<int>& modulus){
    std::vector<int> x(d),y(d),result(2*d-1);
    for(int i=0;i<d;i++){x[i]=a%p;y[i]=b%p;a/=p;b/=p;}
    for(int i=0;i<d;i++)for(int j=0;j<d;j++)result[i+j]=residue(result[i+j]+x[i]*y[j],p);
    for(int k=2*d-2;k>=d;k--){
        int c=result[k];
        for(int j=0;j<d;j++)result[k-d+j]=residue(result[k-d+j]-c*modulus[j],p);
        result[k]=0;
    }
    result.resize(d);return result;
}
int check_spread(std::ostream& out,int p){
    Board board(p+5);int d=p==2?3:2,copies=2,r=copies*d;
    std::vector<int> modulus=d==3?std::vector<int>{1,1,0,1}:std::vector<int>{p==5?2:1,0,1};
    // For degrees two and three, no root over F_p is equivalent to irreducibility.
    for(int a=0;a<p;a++){
        int value=0;for(int i=0;i<=d;i++)value=residue(value+modulus[i]*power(a,i,p),p);
        need(value!=0,"extension-field modulus has a root");
    }
    std::vector<int> embedding(2*r,-1);std::vector<bool> used(board.variables);
    embedding[0]=0;used[0]=true;
    for(int j=0;j<d;j++){embedding[r+j]=(j+1)*board.n;used[(j+1)*board.n]=true;}
    int cursor=0;
    for(int i=0;i<2*r;i++)if(embedding[i]<0){
        while(cursor<board.variables && (used[cursor] || cursor%board.n==board.n-1))cursor++;
        need(cursor<board.variables,"embedding space too small");
        embedding[i]=cursor;used[cursor]=true;
    }
    out<<"{\"record\":\"spread_case\",\"p\":"<<p<<",\"n\":"<<board.n<<",\"d\":"<<d
       <<",\"copies\":"<<copies<<",\"input_rank\":"<<r<<",\"modulus\":[";
    for(size_t i=0;i<modulus.size();i++){if(i)out<<',';out<<modulus[i];}
    out<<"],\"embedding\":[";
    for(size_t i=0;i<embedding.size();i++){if(i)out<<',';out<<embedding[i];}
    out<<"],\"matching\":[[0,0]]}\n";
    std::vector<std::vector<Row>> spaces(board.n);
    for(int alpha=0;alpha<board.n;alpha++){
        Basis span(p,2*r);
        for(int j=0;j<r;j++){
            Row row(2*r);row[j]=1;int unit=1;for(int k=0;k<j%d;k++)unit*=p;
            auto product=field_product(alpha,unit,p,d,modulus);
            for(int k=0;k<d;k++)row[r+(j/d)*d+k]=static_cast<std::uint8_t>(product[k]);
            span.add(row);spaces[alpha].push_back(row);
            Sparse sparse;for(int k=0;k<2*r;k++)if(row[k])sparse.push_back({k,row[k]});
            out<<"{\"record\":\"spread_input\",\"alpha\":"<<alpha<<",\"input\":"<<j<<",\"abstract_cells\":";
            sparse_json(out,sparse);out<<"}\n";
        }
        need(span.rank==r,"spread input rank");
        const Row& first=spaces[alpha][0];int constant=0;bool survives=false;
        for(int i=0;i<2*r;i++)if(first[i]){
            int v=embedding[i];
            if(v==0)constant=residue(constant+first[i],p);
            else if(v/board.n!=0 && v%board.n!=0)survives=true;
        }
        need(constant==1 && !survives,"designated input is not identically one after matching");
        out<<"{\"record\":\"spread_normalization\",\"alpha\":"<<alpha
           <<",\"input\":0,\"restricted_constant\":1,\"surviving_terms\":0}\n";
    }
    int pairs=0;
    for(int a=0;a<board.n;a++)for(int b=a+1;b<board.n;b++){
        Basis joint(p,2*r);
        for(const auto& row:spaces[a])joint.add(row);
        for(const auto& row:spaces[b])joint.add(row);
        need(joint.rank==2*r,"spread spaces intersect nontrivially");
        out<<"{\"record\":\"spread_pair\",\"alpha\":"<<a<<",\"beta\":"<<b
           <<",\"joint_rank\":"<<joint.rank<<"}\n";pairs++;
    }
    out<<"{\"record\":\"spread_case_passed\",\"pairs\":"<<pairs<<",\"all_blocks_normalized\":true}\n";
    return pairs;
}
int main(int argc,char** argv){
    try{
        if(argc==2 && std::string(argv[1])=="--help"){
            std::cout<<"Usage: check_target_annihilators --out NEW_PATH\n";return 0;
        }
        need(argc==3 && std::string(argv[1])=="--out","--out NEW_PATH required");
        need(!std::filesystem::exists(argv[2]),"output exists; choose a new path");
        std::ofstream out(argv[2]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"suite\":\"target_annihilators\",\"seed\":null,\"arithmetic\":\"exact finite fields\",\"scope\":\"ordinary PHP C2 spaces plus local overlap identities; no global elimination claim\"}\n";
        int identities=0,pairs=0;
        for(int p:{2,3,5,7}){
            check_php(out,p);check_subsets(out,p);identities+=check_overlap(out,p);pairs+=check_spread(out,p);
        }
        out<<"{\"record\":\"summary\",\"php_cases\":4,\"subset_cases\":4,\"overlap_identities\":"<<identities
           <<",\"omitted_error_controls\":"<<identities<<",\"spread_cases\":4,\"spread_pairs\":"<<pairs
           <<",\"all_passed\":true}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"4 exact ordinary-PHP spaces, 4 subset-rank checks, "<<identities
                 <<" overlap identities, and 4 normalized spread families passed.\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
