// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
#include "binary_php.hpp"
#include <map>
using namespace binary_php;

struct Inputs {
    int n,r;
    Word constants=0;
    std::vector<Word> cells;
    Word at(int i,int j)const{return cells[i*n+j];}
};
void numbers(std::ostream& out,const std::vector<int>& v) {
    out<<'[';for(size_t j=0;j<v.size();++j){if(j)out<<',';out<<v[j];}out<<']';
}
bool has(const std::vector<int>& v,int x){return std::find(v.begin(),v.end(),x)!=v.end();}
int parity(Word a,Word b){return __builtin_parityll(a&b);}
void describe(const std::string& name,const Inputs& a,std::ostream& out) {
    out<<"{\"type\":\"inputs\",\"name\":\""<<name<<"\",\"N\":"<<a.n
       <<",\"rank_parameter\":"<<a.r<<",\"constant_word\":"<<a.constants<<",\"cell_words\":[";
    for(size_t j=0;j<a.cells.size();++j){if(j)out<<',';out<<a.cells[j];}out<<"]}\n";
}
int deletion(const std::string& name,const Inputs& a,const std::vector<int>& rows,
             const std::vector<int>& cols,Space* local,std::ostream& out) {
    int pivot_col=0;while(has(cols,pivot_col))++pivot_col;
    Space span(a.r);bool first=true;
    out<<"{\"type\":\"deletion\",\"name\":\""<<name<<"\",\"rows\":";numbers(out,rows);
    out<<",\"columns\":";numbers(out,cols);out<<",\"base_column\":"<<pivot_col<<",\"basis_steps\":[";
    for(int i=0;i<=a.n && span.rank<a.r;++i)if(!has(rows,i))
      for(int j=0;j<a.n && span.rank<a.r;++j)if(!has(cols,j) && j!=pivot_col) {
        Word raw=a.at(i,j)^a.at(i,pivot_col);std::vector<int> trace;
        int p=span.add(Bits{raw},&trace);
        if(p>=0) {
            if(!first)out<<',';
            first=false;
            out<<"{\"row\":"<<i<<",\"column\":"<<j<<",\"raw_word\":"<<raw<<",\"trace\":";
            numbers(out,trace);out<<",\"pivot\":"<<p<<",\"basis_word\":"<<span.rows[p][0]<<'}';
        }
      }
    out<<"],\"rank\":"<<span.rank<<",\"dual_basis\":[";first=true;int nullity=0;
    for(int p=0;p<a.r;++p)if(!bit(span.pivots,p)) {
        Bits seed=blank(a.r);flip(seed,p);Word w=span.complete_dual(seed)[0];
        for(int i=0;i<=a.n;++i)if(!has(rows,i))for(int j=0;j<a.n;++j)if(!has(cols,j))
            need(!parity(w,a.at(i,j)^a.at(i,pivot_col)),"dual fails an omitted generator");
        if(!first)out<<',';
        first=false;++nullity;
        out<<"{\"free_coordinate\":"<<p<<",\"word\":"<<w;
        if(local) {
            local->add(Bits{w});std::vector<int> row_coefficients,support_cells;
            int constant=parity(w,a.constants);
            for(int i=0;i<=a.n;++i) {
                int beta=has(rows,i)?0:parity(w,a.at(i,pivot_col));
                if(beta){row_coefficients.push_back(i);constant^=1;}
                for(int j=0;j<a.n;++j)if(parity(w,a.at(i,j))^beta) {
                    need(has(rows,i)||has(cols,j),"localized support escaped deleted stars");
                    support_cells.push_back(i*a.n+j);
                }
            }
            out<<",\"row_equation_coefficients\":";numbers(out,row_coefficients);
            out<<",\"localized_constant\":"<<constant<<",\"localized_cells\":";
            numbers(out,support_cells);
        }
        out<<'}';
    }
    need(nullity==a.r-span.rank,"dual dimension mismatch");out<<"]}\n";return span.rank;
}
void basic(const std::string& name,const Inputs& a,int expected_local,int expected_min,
           std::ostream& out) {
    describe(name,a,out);Space global(a.r),local(a.r);
    for(int i=0;i<=a.n;++i)for(int j=1;j<a.n;++j)global.add(Bits{a.at(i,j)^a.at(i,0)});
    need(global.rank==a.r,"fixture inputs not independent modulo rows");
    std::map<int,int> counts;int total=0;
    for(int i=0;i<=a.n;++i)for(int j=0;j<a.n;++j)for(int k=j+1;k<a.n;++k) {
        int rank=deletion(name,a,{i},{j,k},&local,out);++counts[rank];++total;
    }
    need(local.rank==expected_local && counts.begin()->first==expected_min,"basic prediction failed");
    out<<"{\"type\":\"basic_summary\",\"name\":\""<<name<<"\",\"global_rank\":"<<global.rank
       <<",\"deletions\":"<<total<<",\"rank_histogram\":{";
    bool first=true;for(auto [rank,count]:counts){if(!first)out<<',';first=false;out<<'"'<<rank<<"\":"<<count;}
    out<<"},\"localized_dimension\":"<<local.rank<<",\"localized_basis\":[";first=true;
    for(const Bits& row:local.rows)if(!row.empty()){if(!first)out<<',';first=false;out<<row[0];}
    out<<"]}\n";
    std::cout<<name<<": "<<total<<" deletions, minimum rank "<<counts.begin()->first
             <<", localized-direction dimension "<<local.rank<<".\n";
}
void strong(const std::string& name,const Inputs& a,std::ostream& out) {
    describe(name,a,out);int total=0;
    for(int i=0;i<=a.n;++i)for(int k=i+1;k<=a.n;++k)
      for(int j=0;j<a.n;++j)for(int l=j+1;l<a.n;++l)
       for(int s=l+1;s<a.n;++s)for(int t=s+1;t<a.n;++t) {
         need(deletion(name,a,{i,k},{j,l,s,t},nullptr,out)==a.r,"strong deletion rank failed");
         ++total;
       }
    out<<"{\"type\":\"strong_summary\",\"name\":\""<<name<<"\",\"deletions\":"<<total
       <<",\"all_ranks\":"<<a.r<<"}\n";
    std::cout<<name<<": all "<<total<<" two-row/four-column deletions retain rank "<<a.r<<".\n";
}
Inputs read_inputs(const std::string& path) {
    std::ifstream in(path);Inputs a;in>>a.n>>a.r>>a.constants;
    need(bool(in)&&a.n==11&&a.r==6,"expected archived eleven-hole rank-six inputs");
    need(a.constants<(Word(1)<<a.r),"constant range");a.cells.resize(a.n*(a.n+1));
    for(Word& cell:a.cells){in>>cell;need(bool(in)&&cell<(Word(1)<<a.r),"cell word range");}
    std::string extra;need(!(in>>extra),"unexpected trailing input");return a;
}
Inputs cells(int n,const std::vector<int>& selected) {
    Inputs a{n,int(selected.size()),0,std::vector<Word>(n*(n+1))};
    for(int j=0;j<a.r;++j)a.cells[selected[j]]|=Word(1)<<j;
    return a;
}
Word rectangle_row(int r,Word u,Word v) {
    Word row=0;int p=0;
    for(int i=0;i<r;++i)for(int j=i+1;j<r;++j,++p)
        if((((u>>i)&1)*((v>>j)&1))^(((u>>j)&1)*((v>>i)&1)))row|=Word(1)<<p;
    return row;
}
void rectangles(const std::string& name,const Inputs& a,int expected_nullity,std::ostream& out) {
    describe(name,a,out);int q=a.r*(a.r-1)/2;need(q<=63,"rectangle word guard");
    Space equations(std::max(q,1));int scanned=0;bool first=true;
    out<<"{\"type\":\"rectangle_certificate\",\"name\":\""<<name<<"\",\"unknowns\":"<<q
       <<",\"basis_steps\":[";
    for(int i=0;i<=a.n && equations.rank<q;++i)for(int k=i+1;k<=a.n && equations.rank<q;++k)
      for(int j=0;j<a.n && equations.rank<q;++j)for(int l=j+1;l<a.n && equations.rank<q;++l)
       for(int s=0;s<a.n && equations.rank<q;++s)if(s!=j && s!=l)
        for(int t=s+1;t<a.n && equations.rank<q;++t)if(t!=j && t!=l) {
            Word raw=rectangle_row(a.r,a.at(i,j)^a.at(i,l),a.at(k,s)^a.at(k,t));
            std::vector<int> trace;int p=equations.add(Bits{raw},&trace);++scanned;
            if(p>=0) {
                if(!first)out<<',';
                first=false;out<<"{\"rows\":["<<i<<','<<k<<"],\"columns\":["<<j<<','<<l<<','<<s<<','<<t
                   <<"],\"raw_word\":"<<raw<<",\"trace\":";numbers(out,trace);
                out<<",\"pivot\":"<<p<<",\"basis_word\":"<<equations.rows[p][0]<<'}';
            }
        }
    out<<"],\"equations_scanned\":"<<scanned<<",\"rank\":"<<equations.rank<<",\"kernel_basis\":[";
    first=true;int nullity=0;
    for(int p=0;p<q;++p)if(!bit(equations.pivots,p)) {
        Bits seed=blank(std::max(q,1));flip(seed,p);Word w=equations.complete_dual(seed)[0];
        for(int i=0;i<=a.n;++i)for(int k=i+1;k<=a.n;++k)
          for(int j=0;j<a.n;++j)for(int l=j+1;l<a.n;++l)
           for(int s=0;s<a.n;++s)if(s!=j && s!=l)
            for(int t=s+1;t<a.n;++t)if(t!=j && t!=l)
                need(!parity(w,rectangle_row(a.r,a.at(i,j)^a.at(i,l),a.at(k,s)^a.at(k,t))),
                     "Hessian kernel fails a rectangle equation");
        if(!first)out<<',';
        first=false;out<<w;++nullity;
    }
    need(nullity==q-equations.rank && nullity==expected_nullity,"rectangle nullity prediction");
    out<<"],\"kernel_dimension\":"<<nullity<<"}\n";
    std::cout<<name<<": rectangle rank "<<equations.rank<<'/'<<q<<", kernel "<<nullity<<".\n";
}
Inputs restrict_matching_edge(const Inputs& a,int row,int column) {
    Inputs b{a.n-1,a.r,a.constants^a.at(row,column),{}};
    for(int i=0;i<=a.n;++i)if(i!=row)for(int j=0;j<a.n;++j)if(j!=column)
        b.cells.push_back(a.at(i,j));
    need(b.cells.size()==size_t(b.n*(b.n+1)),"restricted board shape");return b;
}
int restricted_cell(int n,int cell,int row,int column) {
    int i=cell/n,j=cell%n;
    if(i==row && j==column)return -2; // one
    if(i==row || j==column)return -1; // zero
    return (i-(i>row))*(n-1)+j-(j>column);
}
void column_family(const Inputs& ambient,std::ostream& out) {
    Inputs core=ambient;core.r=5;core.constants&=31;
    for(Word& w:core.cells)w&=31;
    describe("column_family_core",core,out);
    const int row=core.n,pairs=(core.n+1)/2,translations=32;
    out<<"{\"type\":\"column_family\",\"N\":"<<core.n<<",\"h\":1,\"D\":4,\"groups\":"
       <<pairs*translations<<",\"input_count\":7,\"local_column\":0,\"matching_row\":"<<row
       <<",\"input_rule\":\"U_0+c_0,...,U_4+c_4,x_(2k,0),x_(2k+1,0)\"}\n";
    for(int k=0;k<pairs;++k) {
        int a=2*k*core.n,b=(2*k+1)*core.n;
        Inputs tuple=core;tuple.r=7;tuple.cells[a]|=32;tuple.cells[b]|=64;
        std::string name="original_pair_"+std::to_string(k);describe(name,tuple,out);
        need(deletion(name,tuple,{}, {},nullptr,out)==7,"original tuple affine independence");
        out<<"{\"type\":\"original_relation\",\"pair\":"<<k<<",\"cells\":["<<a<<','<<b
           <<"],\"old_generator\":\"column exclusion\",\"raw_boolean_witness_ones\":["<<a<<','<<b<<"]}\n";
    }
    for(int column:{0,1}) {
        Inputs reduced=restrict_matching_edge(core,row,column);
        std::string name=column==0?"covered_column_core":"wrong_column_core";
        describe(name,reduced,out);need(deletion(name,reduced,{}, {},nullptr,out)==5,"restricted core rank");
        rectangles(name,reduced,0,out);
        int killed=0,remaining_collisions=0,core_only=0;
        for(int k=0;k<pairs;++k) {
            int a=2*k*core.n,b=(2*k+1)*core.n;
            int ra=restricted_cell(core.n,a,row,column),rb=restricted_cell(core.n,b,row,column);
            bool unit=ra==-2 || rb==-2,collision=ra>=0 && rb>=0;
            if(collision)need(ra%reduced.n==rb%reduced.n && ra/reduced.n!=rb/reduced.n,
                              "residual collision geometry");
            Inputs original=core;original.r=7;original.cells[a]|=32;original.cells[b]|=64;
            Inputs tuple=restrict_matching_edge(original,row,column);
            std::string tuple_name=name+"_pair_"+std::to_string(k);describe(tuple_name,tuple,out);
            int expected_rank=5+int(ra>=0)+int(rb>=0);
            need(deletion(tuple_name,tuple,{}, {},nullptr,out)==expected_rank,"restricted tuple affine rank");
            for(int c=0;c<translations;++c) {
                out<<"{\"type\":\"restricted_block\",\"selected_column\":"<<column<<",\"pair\":"<<k
                   <<",\"translation\":"<<c<<",\"core_constant_word\":"<<(reduced.constants^Word(c))
                   <<",\"local_images\":["<<ra<<','<<rb<<"],\"unit_input\":"<<(unit?"true":"false")
                   <<",\"nontrivial_old_collision\":"<<(collision?"true":"false")<<"}\n";
                killed+=unit;remaining_collisions+=collision;core_only+=!unit && ra==-1 && rb==-1;
            }
        }
        need(column==0?(killed==32 && core_only==160 && remaining_collisions==0):
                       (killed==0 && core_only==0 && remaining_collisions==160),"family restriction prediction");
        out<<"{\"type\":\"column_restriction_summary\",\"selected_column\":"<<column
           <<",\"residual_holes\":"<<reduced.n<<",\"groups\":"<<pairs*translations
           <<",\"unit_blocks\":"<<killed<<",\"core_only_blocks\":"<<core_only
           <<",\"blocks_with_old_collision\":"<<remaining_collisions<<"}\n";
        std::cout<<name<<": "<<killed<<" unit blocks, "<<core_only<<" core-only blocks, "
                 <<remaining_collisions<<" retained collision relations.\n";
    }
}
int main(int argc,char** argv) {
    try {
        need((argc==5 || (argc==6 && (std::string(argv[5])=="--rectangles" ||
                                    std::string(argv[5])=="--column-family"))) &&
             std::string(argv[1])=="--ambient" && std::string(argv[3])=="--out",
             "usage: check_quadratic_source_relations --ambient INPUT.txt --out NEW.jsonl [--rectangles|--column-family]");
        Inputs ambient=read_inputs(argv[2]);std::ifstream existing(argv[4]);need(!existing.good(),"output exists");
        std::ofstream out(argv[4]);need(bool(out),"cannot open output");
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,"
             "\"encoding\":\"Word bit j is the coefficient of input j; cells are row-major, zero based\","
             "\"scope\":\"Exact deletion ranks and localized affine directions, not a new NS quotient elimination\"}\n";
        Inputs conclusion=ambient;conclusion.r=5;conclusion.constants&=31;
        for(Word& w:conclusion.cells)w&=31;
        Inputs extension=conclusion;extension.r=6;extension.cells[0]|=32;
        if(argc==6 && std::string(argv[5])=="--column-family") {
            column_family(ambient,out);
        } else if(argc==6) {
            rectangles("archived_ambient",ambient,0,out);
            rectangles("MP_conclusion",conclusion,0,out);
            rectangles("MP_with_cell_antecedent",extension,0,out);
            rectangles("single_cell",cells(4,{0}),0,out);
            rectangles("column_pair",cells(4,{0,4}),1,out);
            rectangles("row_pair",cells(4,{0,1}),1,out);
            rectangles("matching_pair",cells(4,{0,5}),0,out);
        } else {
            basic("archived_ambient",ambient,0,6,out);
            strong("MP_conclusion",conclusion,out);
            basic("MP_with_cell_antecedent",extension,1,5,out);
            basic("single_cell",cells(4,{0}),1,0,out);
            basic("column_pair",cells(4,{0,4}),2,0,out);
            basic("row_pair",cells(4,{0,1}),2,0,out);
            basic("matching_pair",cells(4,{0,5}),2,0,out);
        }
        out.close();need(bool(out),"output write failed");return 0;
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
