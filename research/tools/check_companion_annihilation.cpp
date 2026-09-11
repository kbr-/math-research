// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact affine-coefficient feasibility for all requested companion products.
#include "binary_php.hpp"
#include <filesystem>
using namespace binary_php;

struct Quotient {
    const Space& base;int width;
    std::vector<int> free_index,free_coordinates;
    explicit Quotient(const Space& b):base(b),free_index(b.width,-1){
        for(int j=0;j<b.width;j++){
            if(b.rows[j].empty()){
                free_index[j]=int(free_coordinates.size());free_coordinates.push_back(j);
            }
        }
        width=int(free_coordinates.size());
    }
    Bits project(Bits polynomial) const{
        Bits reduced=base.reduce(std::move(polynomial)),result=blank(width);
        for(int mon:support(reduced)){
            int j=free_index[mon];need(j>=0,"quotient reduction left a pivot");flip(result,j);
        }
        return result;
    }
    Bits lift_dual(const Bits& functional) const{
        Bits seed=blank(base.width);
        for(int j:support(functional)){
            need(j<width,"quotient dual range");flip(seed,free_coordinates[j]);
        }
        return base.complete_dual(std::move(seed));
    }
};
void put_block(Bits& destination,const Bits& source,int offset){
    int word=offset/64,shift=offset%64;
    for(size_t j=0;j<source.size();j++){
        need(word+int(j)<int(destination.size()),"block packing range");
        destination[word+j]^=source[j]<<shift;
        if(shift && word+j+1<destination.size()){
            destination[word+j+1]^=source[j]>>(64-shift);
        }
    }
}
Bits get_block(const Bits& source,int offset,int width){
    Bits result=blank(width);
    for(int j=0;j<width;j++){
        if(bit(source,offset+j))flip(result,j);
    }
    return result;
}
void hexword(std::ostream& out,Word value){
    auto flags=out.flags();out<<'"'<<std::hex<<value<<'"';out.flags(flags);
}
struct Result {bool feasible;int rank,targets;};

Result solve(const Board& board,const Quotient& quotient,const std::vector<Word>& inputs,
             int targets,const std::string& label,std::ostream& out){
    const int r=int(inputs.size()),parameters=r*(board.variables+1),width=targets*quotient.width;
    need(targets>=1 && targets<=r,"target prefix range");
    Space system(width);std::vector<Bits> representations(width),columns;
    columns.reserve(parameters);Bits target=blank(width);
    for(int i=0;i<targets;i++){
        put_block(target,quotient.project(board.affine(inputs[i])),i*quotient.width);
    }
    std::vector<std::vector<Bits>> pairs(targets,std::vector<Bits>(r));
    for(int i=0;i<targets;i++)for(int j=0;j<r;j++){
        pairs[i][j]=board.affine_product(inputs[i],board.affine(inputs[j]));
    }
    for(int j=0;j<r;j++)for(int coefficient=0;coefficient<=board.variables;coefficient++){
        Bits column=blank(width);
        for(int i=0;i<targets;i++){
            Bits polynomial=coefficient==0?pairs[i][j]:board.variable_product(pairs[i][j],coefficient-1);
            put_block(column,quotient.project(std::move(polynomial)),i*quotient.width);
        }
        columns.push_back(column);std::vector<int> trace;int pivot=system.add(std::move(column),&trace);
        if(pivot>=0){
            Bits representation=blank(parameters);flip(representation,j*(board.variables+1)+coefficient);
            for(int old:trace){
                need(!representations[old].empty(),"missing parameter representation");
                for(size_t word=0;word<representation.size();word++){
                    representation[word]^=representations[old][word];
                }
            }
            representations[pivot]=std::move(representation);
        }
    }
    std::vector<int> trace;Bits remainder=system.reduce(target,&trace);
    bool feasible=zero(remainder);
    out<<"{\"record\":\"companion_system\",\"label\":\""<<label<<"\",\"input_count\":"<<r
       <<",\"target_prefix\":"<<targets<<",\"parameters\":"<<parameters
       <<",\"equation_coordinates\":"<<width<<",\"rank\":"<<system.rank
       <<",\"feasible\":"<<(feasible?"true":"false")<<",\"old_affine_inputs\":[";
    for(int j=0;j<r;j++){
        if(j)out<<',';
        hexword(out,inputs[j]);
    }
    out<<']';
    if(feasible){
        Bits solution=blank(parameters),check=blank(width);
        for(int pivot:trace){
            for(size_t word=0;word<solution.size();word++)solution[word]^=representations[pivot][word];
        }
        std::vector<Word> coefficients(r);
        for(int index:support(solution)){
            for(size_t word=0;word<check.size();word++)check[word]^=columns[index][word];
            coefficients[index/(board.variables+1)]^=Word(1)<<(index%(board.variables+1));
        }
        need(check==target,"parameter solution failed original matrix");
        Bits h=board.unit(0);
        for(int j=0;j<r;j++){
            Bits term=board.affine_product(coefficients[j],board.affine(inputs[j]));
            for(size_t word=0;word<h.size();word++)h[word]^=term[word];
        }
        for(int i=0;i<targets;i++){
            need(zero(quotient.project(board.affine_product(inputs[i],h))),"direct companion solution check");
        }
        out<<",\"coefficient_affine_words\":[";
        for(int j=0;j<r;j++){
            if(j)out<<',';
            hexword(out,coefficients[j]);
        }
        out<<"],\"H_terms\":";sparse_json(out,h);
    }else{
        Bits dual=system.separating_dual(target);
        for(const Bits& column:columns)need(dot(column,dual)==0,"column dual check");
        std::vector<Bits> lifted;int normalization=0;std::uint64_t checked=0;
        for(int i=0;i<targets;i++){
            Bits functional=quotient.lift_dual(get_block(dual,i*quotient.width,quotient.width));
            normalization^=dot(functional,board.affine(inputs[i]));lifted.push_back(std::move(functional));
        }
        need(normalization==1,"lifted obstruction normalization");
        for(int j=0;j<r;j++)for(int coefficient=0;coefficient<=board.variables;coefficient++){
            int value=0;
            for(int i=0;i<targets;i++){
                Bits polynomial=coefficient==0?pairs[i][j]:board.variable_product(pairs[i][j],coefficient-1);
                value^=dot(lifted[i],polynomial);
            }
            need(value==0,"direct unreduced obstruction check");checked++;
        }
        int corrupt_parameter=0;
        while(corrupt_parameter<parameters && zero(columns[corrupt_parameter]))corrupt_parameter++;
        need(corrupt_parameter<parameters,"vacuous dual corruption control");
        int corrupt_coordinate=highest(columns[corrupt_parameter]);
        Bits corrupted=dual;flip(corrupted,corrupt_coordinate);
        need(dot(columns[corrupt_parameter],corrupted)==1,"corrupted dual not rejected");
        int corrupt_j=corrupt_parameter/(board.variables+1);
        int corrupt_v=corrupt_parameter%(board.variables+1),corrupt_value=0;
        for(int i=0;i<targets;i++){
            Bits functional=quotient.lift_dual(get_block(corrupted,i*quotient.width,quotient.width));
            Bits polynomial=corrupt_v==0?pairs[i][corrupt_j]
                :board.variable_product(pairs[i][corrupt_j],corrupt_v-1);
            corrupt_value^=dot(functional,polynomial);
        }
        need(corrupt_value==1,"lifted corruption control failed");
        out<<",\"dual_functionals\":[";
        for(int i=0;i<targets;i++){
            if(i)out<<',';
            sparse_json(out,lifted[i]);
        }
        out<<"],\"checked_parameter_equations\":"<<checked
           <<",\"corruption_coordinate\":"<<corrupt_coordinate
           <<",\"corruption_failed_parameter\":"<<corrupt_parameter;
    }
    out<<"}\n"<<std::flush;
    std::cout<<label<<", first "<<targets<<" companions: "
             <<(feasible?"FEASIBLE":"EXCLUDED")<<", rank "<<system.rank<<'/'<<parameters<<".\n"<<std::flush;
    return {feasible,system.rank,targets};
}

void analyze_annihilators(const Board& board,const Quotient& quotient,
                         const std::vector<Word>& inputs,int targets,
                         const std::string& label,std::ostream& out){
    std::vector<int> domain;
    for(int mon=0;mon<board.low;mon++){
        if(quotient.base.rows[mon].empty())domain.push_back(mon);
    }
    const int d=int(domain.size()),width=targets*quotient.width;
    Space image(width),kernel(d);std::vector<Bits> columns,representations(width),kernel_vectors;
    std::vector<int> independent_columns,pivot_coordinates;
    for(int j=0;j<d;j++){
        Bits column=blank(width);
        for(int i=0;i<targets;i++){
            put_block(column,quotient.project(board.affine_product(inputs[i],board.unit(domain[j]))),
                      i*quotient.width);
        }
        columns.push_back(column);std::vector<int> trace;int pivot=image.add(std::move(column),&trace);
        Bits representation=blank(d);flip(representation,j);
        for(int old:trace){
            need(!representations[old].empty(),"annihilator representation reference");
            for(size_t word=0;word<representation.size();word++){
                representation[word]^=representations[old][word];
            }
        }
        if(pivot>=0){
            representations[pivot]=std::move(representation);
            independent_columns.push_back(j);pivot_coordinates.push_back(pivot);
        }else{
            Bits check=blank(width),h=blank(board.width);
            for(int index:support(representation)){
                flip(h,domain[index]);
                for(size_t word=0;word<check.size();word++)check[word]^=columns[index][word];
            }
            need(zero(check),"annihilator kernel column check");
            for(int i=0;i<targets;i++){
                need(zero(quotient.project(board.affine_product(inputs[i],h))),"annihilator product check");
            }
            need(kernel.add(representation)>=0,"dependent kernel witness");
            kernel_vectors.push_back(std::move(representation));
        }
    }
    need(image.rank+kernel.rank==d,"annihilator rank-nullity check");
    Space minor_space(image.rank);std::vector<Bits> minor_rows;
    for(int coordinate:pivot_coordinates){
        Bits row=blank(image.rank);
        for(int j=0;j<image.rank;j++){
            if(bit(columns[independent_columns[j]],coordinate))flip(row,j);
        }
        need(minor_space.add(row)>=0,"singular claimed rank minor");minor_rows.push_back(std::move(row));
    }
    out<<"{\"record\":\"quadratic_annihilator_map\",\"label\":\""<<label
       <<"\",\"target_prefix\":"<<targets<<",\"domain_dimension\":"<<d
       <<",\"image_rank\":"<<image.rank<<",\"kernel_dimension\":"<<kernel.rank
       <<",\"domain_monomials\":[";
    for(int j=0;j<d;j++){
        if(j)out<<',';
        out<<domain[j];
    }
    out<<"],\"kernel_coordinate_vectors\":[";
    for(size_t j=0;j<kernel_vectors.size();j++){
        if(j)out<<',';
        sparse_json(out,kernel_vectors[j]);
    }
    out<<"],\"minor_input_columns\":[";
    for(size_t j=0;j<independent_columns.size();j++){
        if(j)out<<',';
        out<<independent_columns[j];
    }
    out<<"],\"minor_output_coordinates\":[";
    for(size_t j=0;j<pivot_coordinates.size();j++){
        if(j)out<<',';
        out<<pivot_coordinates[j];
    }
    out<<"],\"minor_rows\":[";
    for(size_t j=0;j<minor_rows.size();j++){
        if(j)out<<',';
        sparse_json(out,minor_rows[j]);
    }
    out<<"]}\n"<<std::flush;
    std::cout<<label<<", quadratic annihilators of first "<<targets<<" inputs: kernel "
             <<kernel.rank<<" in dimension "<<d<<".\n"<<std::flush;
}
int main(int argc,char** argv){
    try{
        std::string path,base_path,input_path;int first_targets=3,only_alpha=-1;
        for(int j=1;j<argc;j++){
            std::string arg=argv[j];
            if(arg=="--out" && j+1<argc)path=argv[++j];
            else if(arg=="--base" && j+1<argc)base_path=argv[++j];
            else if(arg=="--inputs" && j+1<argc)input_path=argv[++j];
            else if(arg=="--first-targets" && j+1<argc)first_targets=std::stoi(argv[++j]);
            else if(arg=="--alpha" && j+1<argc)only_alpha=std::stoi(argv[++j]);
            else throw std::runtime_error("Usage: check_companion_annihilation --base PROOF --inputs SPREAD --out NEW_PATH [--first-targets K] [--alpha A]");
        }
        need(!path.empty() && !base_path.empty() && !input_path.empty()
             && !std::filesystem::exists(path),"input paths and new --out required");
        need(first_targets>=1 && first_targets<=24 && only_alpha>=-1 && only_alpha<7,"query parameter range");
        std::ofstream out(path);need(bool(out),"cannot open output");
        Board board(7);out<<"{\"schema\":1,\"suite\":\"companion_annihilation\",\"p\":2,\"n\":7,\"degree\":3}\n";
        Space base=load_pc3(board,base_path,out);Quotient quotient(base);
        need(base.rows[0].empty(),"unexpected base refutation");
        std::cout<<"Replayed C3 proof and verified coverage/closure; quotient dimension "
                 <<quotient.width<<".\n"<<std::flush;
        auto sources=read_spread(input_path);
        std::vector<Word> control{old_input(sources[0][0]),old_input(sources[0][1])};
        need(solve(board,quotient,control,2,"two-input-control",out).feasible,"two-input positive control");
        analyze_annihilators(board,quotient,control,1,"first-input-control",out);
        analyze_annihilators(board,quotient,control,2,"two-input-control",out);
        int excluded=0,feasible=0;
        for(int alpha=0;alpha<7;alpha++){
            if(only_alpha>=0 && alpha!=only_alpha)continue;
            std::vector<Word> inputs;for(Word word:sources[alpha])inputs.push_back(old_input(word));
            analyze_annihilators(board,quotient,inputs,3,"spread-"+std::to_string(alpha),out);
            int targets=first_targets;
            while(true){
                Result result=solve(board,quotient,inputs,targets,"spread-"+std::to_string(alpha),out);
                if(!result.feasible){excluded++;break;}
                if(targets==24){feasible++;break;}
                targets=std::min(24,targets+3);
            }
        }
        out<<"{\"record\":\"summary\",\"excluded_spaces\":"<<excluded
           <<",\"feasible_spaces\":"<<feasible<<",\"all_certificate_checks_passed\":true}\n";
        out.close();need(bool(out),"output write failure");return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
