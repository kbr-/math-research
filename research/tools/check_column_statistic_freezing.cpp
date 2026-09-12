// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Affine column-occupancy freezing with complete original-base image certificates.
#define STABLE_IDEAL_NORMALIZERS_NO_MAIN
#include "check_stable_ideal_normalizers.cpp"

struct FreezeCounts {
    int cases=0,base_images=0,base_certificates=0,columns=0,blocks=0,
        companion_images=0,field_images=0,zero_input_blocks=0,scope_controls=0;
};
struct CellImage {Poly value;char kind;int index;};
struct ResidualBase {
    int holes,rows,variables;std::vector<Poly> axioms,empty;
    std::vector<std::vector<std::vector<int>>> collision;
};
ResidualBase residual_base(int p,int holes) {
    int rows=holes+1,variables=rows*holes;
    need(variables<=NV,"residual variable capacity");std::vector<Poly> ax,empty;
    for(int i=0;i<rows;i++) {
        Poly row(p,-1);for(int j=0;j<holes;j++)row=row+variable(p,i*holes+j);
        ax.push_back(row);
    }
    for(int v=0;v<variables;v++)ax.push_back(variable(p,v)*variable(p,v)-variable(p,v));
    std::vector<std::vector<std::vector<int>>> index(
        holes,std::vector<std::vector<int>>(rows,std::vector<int>(rows,-1)));
    for(int j=0;j<holes;j++) {
        Poly q(p,1);for(int i=0;i<rows;i++)q=q-variable(p,i*holes+j);
        empty.push_back(q);
        for(int i=0;i<rows;i++)for(int k=i+1;k<rows;k++) {
            index[j][i][k]=index[j][k][i]=int(ax.size());
            ax.push_back(variable(p,i*holes+j)*variable(p,k*holes+j));
        }
    }
    return {holes,rows,variables,ax,empty,index};
}
void base_image(std::ostream& out,FreezeCounts& count,const std::string& name,
                const std::string& kind,const std::vector<int>& indices,
                int source_degree,const ResidualBase& base,const Poly& target,
                const std::vector<Poly>& cof) {
    need(target.deg()<=source_degree,"base-image degree increase");
    std::string certificate=name+"_base_"+std::to_string(count.base_images);
    if(target.terms.empty()) {
        for(const auto& q:cof)need(q.terms.empty(),"unexpected nonempty zero-image certificate");
    } else {
        ns(out,certificate,base.axioms,cof,target,source_degree);
        count.base_certificates++;
    }
    out<<"{\"record\":\"base_image\",\"case\":\""<<name<<"\",\"kind\":\""<<kind
       <<"\",\"source_indices\":[";
    for(size_t i=0;i<indices.size();i++){if(i)out<<',';out<<indices[i];}
    out<<"],\"source_degree\":"<<source_degree<<",\"image\":";jsonpoly(out,target);
    out<<",\"certificate\":";
    if(target.terms.empty())out<<"null";
    else out<<'\"'<<certificate<<'\"';
    out<<",\"verified\":true}\n";count.base_images++;
}
void statistic_ens(std::ostream& out,FreezeCounts& count,const std::string& name,
                   int p,int empty_column,int occupied_column) {
    Poly one(p,1),empty=variable(p,0),occupied=variable(p,1);
    int next=2;
    Block a=block({empty,occupied-one},2,next);
    Block b=block({occupied+one,empty+one},1,next);
    Block c=block({variable(p,b.first)+occupied,variable(p,a.first)+empty},2,next);
    Block d=block({variable(p,c.first)-variable(p,b.first),occupied-empty},1,next);
    std::vector<Block> blocks={a,b,c,d};std::vector<int> levels={1,1,2,3};
    need(next<=NV,"formal ENS variable capacity");
    std::array<int,NV> constants{},variable_level{};constants[0]=0;constants[1]=1;
    out<<"{\"record\":\"statistic_family\",\"case\":\""<<name
       <<"\",\"polynomial_space\":\"formal statistics Z0,Z1 followed by fresh coefficient variables\","
         "\"Z0_source_column\":"<<empty_column<<",\"Z1_source_column\":"<<occupied_column
       <<",\"statistic_images\":[0,1],\"formal_variables\":"<<next<<"}\n";
    for(size_t index=0;index<blocks.size();index++) {
        const auto& U=blocks[index];std::vector<int> values;int chosen=-1;
        for(size_t i=0;i<U.inputs.size();i++) {
            need(U.inputs[i].old(U.first),"input uses its own or later coefficient");
            for(const auto& term:U.inputs[i].terms)for(int v=2;v<U.first;v++)
                if(term.first[v])need(variable_level[v]<levels[index],"input uses a same-level coefficient");
            int value=evaluate(U.inputs[i],constants);values.push_back(value);
            if(chosen<0 && value)chosen=int(i);
        }
        for(int v=U.first;v<U.end;v++){constants[v]=0;variable_level[v]=levels[index];}
        if(chosen>=0)constants[U.first+chosen]=modpow(values[chosen],p-2,p);
        else count.zero_input_blocks++;
        Poly product_image=specialize(U.product,0,constants);
        need(product_image==Poly(p,chosen<0?1:0),"wrong constant product image");
        for(const auto& f:U.axioms) {
            need(specialize(f,0,constants).terms.empty(),"nonzero ENS companion image");
            count.companion_images++;
        }
        std::vector<Poly> fields;
        for(int v=U.first;v<U.end;v++) {
            Poly f=powp(variable(p,v),p)-variable(p,v);fields.push_back(f);
            need(specialize(f,0,constants).terms.empty(),"nonzero coefficient field image");
            count.field_images++;
        }
        out<<"{\"record\":\"statistic_block\",\"case\":\""<<name<<"\",\"index\":"<<index
           <<",\"level\":"<<levels[index]<<",\"accuracy\":"<<(U.end-U.first)/int(U.inputs.size())
           <<",\"coefficient_range\":["<<U.first<<','<<U.end<<"],\"inputs\":";
        poly_vector(out,U.inputs);out<<",\"source_product\":";jsonpoly(out,U.product);
        out<<",\"source_companions\":";poly_vector(out,U.axioms);
        out<<",\"source_field_axioms\":";poly_vector(out,fields);
        out<<",\"input_images\":[";
        for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}
        out<<"],\"coefficient_images\":[";
        for(int v=U.first;v<U.end;v++){if(v>U.first)out<<',';out<<constants[v];}
        out<<"],\"product_image\":";jsonpoly(out,product_image);
        out<<",\"all_companion_and_field_images_zero\":true}\n";count.blocks++;
    }
}
void freeze_case(std::ostream& out,FreezeCounts& count,int p,int copies,int matched) {
    const int N=3;
    need(copies>0 && (copies+1)%p==0 && matched>=0 && matched<copies,"copy parameters");
    int n=copies*(N+1)+matched,source_rows=n+1;
    need(n%copies==matched && n/copies-1==N,"residual-size formula");
    auto base=residual_base(p,N);Poly one(p,1),zero(p);
    std::string name="F"+std::to_string(p)+"_K"+std::to_string(copies)+"_n"+std::to_string(n);
    std::vector<std::vector<CellImage>> cells(
        source_rows,std::vector<CellImage>(n,CellImage{zero,'0',-1}));
    for(int i=0;i<matched;i++)cells[i][i]={one,'1',-1};
    for(int c=0;c<copies;c++)for(int i=0;i<base.rows;i++)for(int j=0;j<N;j++) {
        int row=matched+c*base.rows+i,column=matched+copies+c*N+j,v=i*N+j;
        cells[row][column]={variable(p,v),'x',v};
    }
    int dummy=source_rows-1;
    for(int c=0;c<copies;c++)for(int j=0;j<N;j++)
        cells[dummy][matched+copies+c*N+j]={base.empty[j],'q',j};
    out<<"{\"record\":\"case_start\",\"name\":\""<<name<<"\",\"p\":"<<p
       <<",\"copies\":"<<copies<<",\"source_holes\":"<<n<<",\"source_pigeons\":"<<source_rows
       <<",\"matched_prefix\":"<<matched<<",\"empty_columns\":"<<copies
       <<",\"residual_holes\":"<<N<<",\"residual_pigeons\":"<<base.rows
       <<",\"residual_variable_order\":\"row-major y_(i,j) at i*N+j\","
         "\"source_rows\":\"matched prefix, copies of residual rows, dummy\","
         "\"source_columns\":\"matched prefix, empty columns, copies of residual holes\","
         "\"residual_axioms\":";
    poly_vector(out,base.axioms);out<<",\"cell_images\":[";
    for(int i=0;i<source_rows;i++) {
        if(i)out<<',';
        out<<'[';
        for(int j=0;j<n;j++) {
            if(j)out<<',';
            need(cells[i][j].value.old(base.variables) && cells[i][j].value.deg()<=1,
                 "nonaffine or foreign-variable cell image");
            jsonpoly(out,cells[i][j].value);
        }
        out<<']';
    }
    out<<"]}\n";
    for(int i=0;i<source_rows;i++) {
        Poly target(p,-1);for(int j=0;j<n;j++)target=target+cells[i][j].value;
        std::vector<Poly> cof(base.axioms.size(),zero);
        if(i==dummy)for(int a=0;a<base.rows;a++)cof[a]=Poly(p,-copies);
        else if(i>=matched)cof[(i-matched)%base.rows]=one;
        base_image(out,count,name,"row",{i},1,base,target,cof);
    }
    for(int i=0;i<source_rows;i++)for(int j=0;j<n;j++) {
        const auto& a=cells[i][j];Poly target=a.value*a.value-a.value;
        std::vector<Poly> cof(base.axioms.size(),zero);
        if(a.kind=='x')cof[base.rows+a.index]=one;
        else if(a.kind=='q') {
            for(int r=0;r<base.rows;r++)cof[base.rows+r*N+a.index]=one;
            for(int r=0;r<base.rows;r++)for(int s=r+1;s<base.rows;s++)
                cof[base.collision[a.index][r][s]]=Poly(p,2);
        }
        base_image(out,count,name,"Boolean",{i,j},2,base,target,cof);
    }
    for(int j=0;j<n;j++)for(int i=0;i<source_rows;i++)for(int k=i+1;k<source_rows;k++) {
        const auto& a=cells[i][j];const auto& b=cells[k][j];
        Poly target=a.value*b.value;std::vector<Poly> cof(base.axioms.size(),zero);
        if(a.kind!='0' && b.kind!='0') {
            if(a.kind=='x' && b.kind=='x') {
                need(a.index%N==b.index%N && a.index/N!=b.index/N,"wrong residual collision");
                cof[base.collision[a.index%N][a.index/N][b.index/N]]=one;
            } else {
                need((a.kind=='x' && b.kind=='q') || (a.kind=='q' && b.kind=='x'),
                     "unexpected fixed or double-dummy collision");
                int v=a.kind=='x'?a.index:b.index,col=a.kind=='q'?a.index:b.index;
                need(v%N==col,"dummy column mismatch");
                cof[base.rows+v]=Poly(p,-1);
                for(int r=0;r<base.rows;r++)if(r!=v/N)
                    cof[base.collision[col][r][v/N]]=Poly(p,-1);
            }
        }
        base_image(out,count,name,"column_collision",{i,k,j},2,base,target,cof);
    }
    for(int j=0;j<n;j++) {
        Poly sigma(p);for(int i=0;i<source_rows;i++)sigma=sigma+cells[i][j].value;
        int expected=(j>=matched && j<matched+copies)?0:1;
        need(sigma==Poly(p,expected),"column statistic was not literally frozen");
        out<<"{\"record\":\"column_statistic\",\"case\":\""<<name<<"\",\"column\":"<<j
           <<",\"literal_value\":"<<expected<<"}\n";count.columns++;
    }
    statistic_ens(out,count,name,p,matched,matched+copies);
    Poly individual=cells[matched][matched+copies].value;
    need(individual==variable(p,0) && individual.deg()==1,"individual-cell scope control");
    std::array<int,NV> row_point{};
    for(int i=0;i<base.rows;i++)row_point[i*N]=1;
    std::vector<Poly> rows(base.axioms.begin(),base.axioms.begin()+base.rows);
    models(rows,row_point);
    Poly wrong(p,-1); // K=p would make the dummy row image p*sum(q)-1=-1.
    need(evaluate(wrong,row_point)!=0,"wrong-copy-count row control");
    out<<"{\"record\":\"scope_controls\",\"case\":\""<<name
       <<"\",\"individual_cell_image\":";jsonpoly(out,individual);
    out<<",\"wrong_copy_count\":"<<p<<",\"wrong_dummy_row_value\":"<<evaluate(wrong,row_point)
       <<",\"point_satisfies_all_degree_one_residual_axioms\":true,\"row_point\":";
    point_json(out,row_point,base.variables);out<<"}\n";count.scope_controls++;
    count.cases++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_column_statistic_freezing --out PATH");
        std::string path=argv[2];need(!std::ifstream(path).good(),"refusing to overwrite output");
        std::ofstream out(path);need(out.good(),"cannot open output");FreezeCounts count;
        out<<"{\"record\":\"schema\",\"version\":1,\"arithmetic\":\"exact prime fields\","
              "\"scope\":\"full weak-PHP base images and a separate formal-statistic ENS family\","
              "\"no_full_PHP_models_claimed\":true}\n";
        freeze_case(out,count,2,1,0);
        freeze_case(out,count,3,2,1);
        freeze_case(out,count,5,4,1);
        freeze_case(out,count,2,3,1);
        out<<"{\"record\":\"summary\",\"cases\":"<<count.cases
           <<",\"base_images\":"<<count.base_images<<",\"nonzero_base_NS_certificates\":"<<count.base_certificates
           <<",\"frozen_column_checks\":"<<count.columns<<",\"statistic_blocks\":"<<count.blocks
           <<",\"zero_companion_images\":"<<count.companion_images
           <<",\"zero_coefficient_field_images\":"<<count.field_images
           <<",\"zero_input_blocks\":"<<count.zero_input_blocks
           <<",\"scope_control_pairs\":"<<count.scope_controls<<"}\n";
        out.flush();need(out.good(),"output failure");
        std::cout<<"Passed "<<count.cases<<" projections, "<<count.base_images<<" full base images ("
                 <<count.base_certificates<<" nonzero NS certificates), "<<count.blocks
                 <<" multilevel statistic blocks; output "<<path<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<"\n";return 1;}
}
