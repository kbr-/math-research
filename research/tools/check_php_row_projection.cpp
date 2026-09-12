// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact row projection, base-image budgets, coordinate inverses, and controls.
#define AFFINE_BASIS_PACKING_NO_MAIN
#include "check_affine_basis_packing.cpp"

struct RowCounts {int cases=0,certificates=0,models=0,activity=0,weak=0;};
int row_ns(std::ostream& out,RowCounts& count,const std::string& name,
           const std::vector<Poly>& ax,const std::vector<Poly>& cof,
           const Poly& target,int bound) {
    int degree=ns(out,name,ax,cof,target,bound);count.certificates++;return degree;
}
struct Board {
    int p,n,m,N;
    std::vector<Poly> boolean,rows,columns,row_base,full_base;
    std::vector<std::pair<int,int>> collision_cells;
};
Board board(int p,int n) {
    need(n>=2 && n<=3,"finite board range");
    int m=n+1,N=m*n;
    Board b{p,n,m,N,domains(p,std::vector<int>(N,2)),{},{},{},{},{}};
    for(int i=0;i<m;i++) {
        Poly row(p,-1);for(int j=0;j<n;j++)row=row+variable(p,i*n+j);
        b.rows.push_back(row);
    }
    for(int j=0;j<n;j++)for(int i=0;i<m;i++)for(int k=i+1;k<m;k++) {
        int x=i*n+j,y=k*n+j;
        b.collision_cells.push_back({x,y});b.columns.push_back(variable(p,x)*variable(p,y));
    }
    b.row_base=b.boolean;b.row_base.insert(b.row_base.end(),b.rows.begin(),b.rows.end());
    b.full_base=b.row_base;b.full_base.insert(b.full_base.end(),b.columns.begin(),b.columns.end());
    return b;
}
struct Projection {std::vector<int> pivots,free;std::vector<Poly> images;};
Projection projection(const Board& b,const std::vector<int>& pivots) {
    need(int(pivots.size())==b.m,"pivot count");
    Projection q{pivots,{},{}};
    for(int v=0;v<b.N;v++)q.images.push_back(variable(b.p,v));
    for(int i=0;i<b.m;i++) {
        need(pivots[i]>=0 && pivots[i]<b.n,"pivot column");
        Poly image(b.p,1);
        for(int j=0;j<b.n;j++)if(j!=pivots[i]) {
            image=image-variable(b.p,i*b.n+j);q.free.push_back(i*b.n+j);
        }
        q.images[i*b.n+pivots[i]]=image;
    }
    return q;
}
Poly project(const Poly& f,const Board& b,const Projection& q) {
    Block range{Poly(b.p),{},{},{},0,b.N};
    return affine_image(f,range,q.images);
}
std::vector<Poly> bool_image_cof(const Board& b,const Projection& q,int v) {
    std::vector<Poly> cof(b.row_base.size(),Poly(b.p));
    cof[v]=Poly(b.p,1);
    int row=v/b.n,column=v%b.n;
    if(column==q.pivots[row])
        cof[b.N+row]=Poly(b.p,-1)*(q.images[v]+variable(b.p,v)-Poly(b.p,1));
    return cof;
}
Matrix affine_coordinates(const std::vector<Poly>& values,const std::vector<int>& free,int p) {
    Matrix C(values.size(),std::vector<int>(free.size()+1));
    for(size_t i=0;i<values.size();i++)for(const auto& term:values[i].terms) {
        int total=0,var=-1;
        for(int v=0;v<NV;v++)if(term.first[v]){total+=term.first[v];var=v;}
        int column=0;
        if(total) {
            need(total==1,"coordinate map is nonlinear");
            auto found=std::find(free.begin(),free.end(),var);
            need(found!=free.end(),"coordinate map contains a pivot");
            column=1+int(found-free.begin());
        }
        C[i][column]=(C[i][column]+term.second)%p;
    }
    return C;
}
Matrix multiply_matrices(const Matrix& A,const Matrix& B,int p) {
    need(!A.empty() && !B.empty() && A[0].size()==B.size(),"matrix dimensions");
    Matrix C(A.size(),std::vector<int>(B[0].size()));
    for(size_t i=0;i<A.size();i++)for(size_t k=0;k<B.size();k++)
        for(size_t j=0;j<B[0].size();j++)C[i][j]=(C[i][j]+A[i][k]*B[k][j])%p;
    return C;
}
void integers_json(std::ostream& out,const std::vector<int>& values) {
    out<<'[';for(size_t i=0;i<values.size();i++){if(i)out<<',';out<<values[i];}out<<']';
}
long long collision_terms_formula(const Board& b,const std::vector<int>& histogram) {
    long long pairs=1LL*b.m*(b.m-1)/2,total=0;
    for(int k:histogram)
        total+=pairs+1LL*(b.n-1)*k*(b.m-k)+1LL*(b.n*b.n-1)*k*(k-1)/2;
    return total;
}
void run_projection(std::ostream& out,RowCounts& count,const Board& b,
                    const std::string& preset,const Projection& q,const Projection& baseline,
                    const std::vector<Poly>& input,const std::vector<Poly>& ys,
                    const Block& original,const std::vector<Poly>& source_ax,
                    const std::vector<Poly>& source_cof,const Poly& source_target) {
    const int p=b.p,N=b.N,next=original.end,companion_start=next+b.m;
    Poly one(p,1),v=q.images[0];
    std::string name="row_projection_n"+std::to_string(b.n)+"_F"+std::to_string(p)+"_"+preset;
    auto phi=[&](const Poly& f){return project(f,b,q);};
    out<<"{\"record\":\"projection_case\",\"name\":\""<<name<<"\",\"p\":"<<p<<",\"n\":"<<b.n
       <<",\"rows\":"<<b.m<<",\"pivots\":";integers_json(out,q.pivots);
    out<<",\"free_old_variable_ids\":";integers_json(out,q.free);
    out<<",\"old_variable_images\":";poly_vector(out,q.images);out<<"}\n";

    std::vector<Poly> projected_base;
    long long collision_terms=0;
    for(size_t i=0;i<b.full_base.size();i++) {
        std::vector<Poly> cof(b.full_base.size(),Poly(p));
        if(int(i)<N) {
            auto small=bool_image_cof(b,q,int(i));
            std::copy(small.begin(),small.end(),cof.begin());
        } else if(int(i)>=N+b.m) {
            auto [a,c]=b.collision_cells[i-N-b.m];cof[i]=one;
            if(a%b.n==q.pivots[a/b.n])cof[N+a/b.n]=cof[N+a/b.n]-variable(p,c);
            if(c%b.n==q.pivots[c/b.n])cof[N+c/b.n]=cof[N+c/b.n]-q.images[a];
        }
        Poly image=phi(b.full_base[i]);
        row_ns(out,count,name+"_base_image_"+std::to_string(i),b.full_base,cof,image,b.full_base[i].deg());
        bool is_row=int(i)>=N && int(i)<N+b.m;
        need(is_row?image.terms.empty():image.deg()==2,"projected base degree");
        if(!image.terms.empty())projected_base.push_back(image);
        if(int(i)>=N+b.m)collision_terms+=image.terms.size();
    }
    std::vector<int> histogram(b.n);
    for(int j:q.pivots)histogram[j]++;
    long long predicted=collision_terms_formula(b,histogram);
    long long pairs=1LL*b.m*(b.m-1)/2;
    long long minimum=b.n*pairs+1LL*(b.n-1)*(b.n*b.n+b.n-2)+(b.n*b.n-1);
    need(collision_terms==predicted && predicted>=minimum,"collision sparsity formula");
    if(preset=="cyclic")need(predicted==minimum,"balanced pivot minimum");

    std::vector<Poly> forward_values={one},backward_values={one},all_coordinates={one};
    for(int old:baseline.free)forward_values.push_back(q.images[old]);
    for(int old:q.free)backward_values.push_back(baseline.images[old]);
    for(const auto& image:q.images)all_coordinates.push_back(image);
    Matrix C=affine_coordinates(forward_values,q.free,p);
    Matrix D=affine_coordinates(backward_values,baseline.free,p);
    need(multiply_matrices(C,D,p)==identity(b.n*b.n)
         && multiply_matrices(D,C,p)==identity(b.n*b.n),"affine coordinate inverses");
    need(polynomial_rank(all_coordinates,p)==b.n*b.n,"row quotient affine dimension");
    auto profile=b.full_base;
    profile.insert(profile.end(),input.begin(),input.end());
    profile.push_back(original.product);profile.push_back(source_target);
    for(const auto& f:profile) {
        Poly first=project(f,b,baseline),current=phi(f);
        need(first.deg()==current.deg(),"pivot-dependent ordinary degree");
        need(phi(first)==current && project(current,b,baseline)==first,"projection compositions");
    }

    std::vector<Poly> projected_input;
    for(const auto& f:input){projected_input.push_back(phi(f));need(projected_input.back()==v,"row-congruent input");}
    need(polynomial_rank(projected_input,p)==1 && v.deg()==1,"projected input rank/degree");
    int projected_next=N;Block projected=block(projected_input,1,projected_next);
    need(projected_next==next && projected.product==phi(original.product),"projected ENS product");
    for(int i=0;i<3;i++)need(projected.axioms[i]==phi(original.axioms[i])
                           && original.axioms[i].deg()==5 && projected.axioms[i].deg()==3,
                           "companion activity degrees");
    auto vbool=bool_image_cof(b,q,0);
    row_ns(out,count,name+"_current_input_Booleanity",b.row_base,vbool,v*v-v,2);
    int epsilon=q.pivots[0]==0?1:0;Poly T(p);
    for(int i=0;i<3;i++) {
        Poly d=ys[i]+Poly(p,epsilon);
        std::vector<Poly> cof(b.row_base.size(),Poly(p));cof[N]=d;
        row_ns(out,count,name+"_input_kernel_"+std::to_string(i),b.row_base,cof,input[i]-v,2);
        T=T+variable(p,N+i)*d;
    }
    std::vector<Poly> product_cof(b.row_base.size(),Poly(p));product_cof[N]=Poly(p,-1)*T;
    row_ns(out,count,name+"_product_kernel",b.row_base,product_cof,
           original.product-projected.product,3);

    auto projected_ax=source_ax;
    for(int i=0;i<3;i++)projected_ax[companion_start+i]=projected.axioms[i];
    std::vector<std::vector<Poly>> images(source_ax.size(),
                                         std::vector<Poly>(projected_ax.size(),Poly(p)));
    for(int old=0;old<N;old++) {
        auto cof=bool_image_cof(b,q,old);
        for(int k=0;k<N;k++)images[old][k]=cof[k];
        for(int row=0;row<b.m;row++)images[old][next+row]=cof[N+row];
    }
    for(int old=N;old<next;old++)images[old][old]=one;
    for(int i=0;i<3;i++)images[companion_start+i][companion_start+i]=one;
    std::vector<Poly> projected_cof(projected_ax.size(),Poly(p));
    for(size_t i=0;i<source_cof.size();i++)if(!source_cof[i].terms.empty()) {
        Poly multiplier=phi(source_cof[i]);
        for(size_t k=0;k<projected_ax.size();k++)
            projected_cof[k]=projected_cof[k]+multiplier*images[i][k];
    }
    Poly projected_target=phi(source_target);
    int projected_degree=row_ns(out,count,name+"_projected_consequence",
                                 projected_ax,projected_cof,projected_target,6);
    need(projected_degree<=std::max(4,p),"projected consequence ceiling");

    // The new companion has a degree-five proof over the original row system.
    std::vector<Poly> old_target_cof(source_ax.size(),Poly(p));old_target_cof[companion_start]=one;
    old_target_cof[next]=Poly(p,-1)*(ys[0]+Poly(p,epsilon))*projected.product+input[0]*T;
    int old_target_degree=row_ns(out,count,name+"_old_proof_of_new_companion",
                                 source_ax,old_target_cof,projected.axioms[0],5);
    need(old_target_degree==5,"old companion proof degree");

    std::array<int,NV> beta{};beta[N]=1;
    auto pack=[&](const Poly& f){return specialize(f,N,beta);};
    need(pack(projected.product)==one-v,"rank-one packing image");
    std::vector<std::vector<Poly>> packed_images(projected_ax.size(),
                                                 std::vector<Poly>(b.row_base.size(),Poly(p)));
    for(int k=0;k<N;k++)packed_images[k][k]=one;
    for(int row=0;row<b.m;row++)packed_images[next+row][N+row]=one;
    for(int i=0;i<3;i++)for(size_t k=0;k<vbool.size();k++)
        packed_images[companion_start+i][k]=Poly(p,-1)*vbool[k];
    std::vector<Poly> packed_cof(b.row_base.size(),Poly(p));
    for(size_t i=0;i<projected_cof.size();i++)if(!projected_cof[i].terms.empty()) {
        Poly multiplier=pack(projected_cof[i]);
        for(size_t k=0;k<packed_cof.size();k++)
            packed_cof[k]=packed_cof[k]+multiplier*packed_images[i][k];
    }
    Poly packed_target=pack(projected_target);
    need(!packed_target.terms.empty() && packed_target.deg()==2,"nonvacuous packed consequence");
    int packed_degree=row_ns(out,count,name+"_packed_consequence",
                              b.row_base,packed_cof,packed_target,2);

    out<<"{\"record\":\"projection_result\",\"case\":\""<<name
       <<"\",\"source_input_rank\":3,\"projected_input_rank\":1,"
         "\"source_input_degree\":2,\"projected_input_degree\":1,"
         "\"source_consequence_degree\":6,\"projected_consequence_degree\":"<<projected_degree
       <<",\"packed_consequence_degree\":"<<packed_degree<<",\"coordinate_map\":";
    matrix_json(out,C,p);out<<",\"inverse_coordinate_map\":";matrix_json(out,D,p);
    out<<",\"pivot_histogram\":";integers_json(out,histogram);
    out<<",\"collision_image_terms\":"<<collision_terms<<",\"minimum_collision_image_terms\":"<<minimum
       <<",\"source_product_terms\":"<<original.product.terms.size()
       <<",\"projected_product_terms\":"<<projected.product.terms.size()
       <<",\"projected_base_as_list\":";poly_vector(out,projected_base);
    out<<",\"projected_input\":";poly_vector(out,projected_input);out<<"}\n";

    // Enumerate every Boolean model of the row subsystem, not only matchings.
    std::vector<int> patterns;
    for(int bits=0;bits<(1<<b.n);bits++)if(__builtin_popcount(unsigned(bits))%p==1)patterns.push_back(bits);
    int model_count=1;for(int row=0;row<b.m;row++)model_count*=int(patterns.size());
    for(int code=0;code<model_count;code++) {
        int residual=code;std::array<int,NV> point{};
        for(int row=0;row<b.m;row++) {
            int bits=patterns[residual%patterns.size()];residual/=int(patterns.size());
            for(int j=0;j<b.n;j++)point[row*b.n+j]=(bits>>j)&1;
        }
        point[N]=1;
        for(int old=0;old<N;old++)need(evaluate(q.images[old],point)==point[old],"projection on row plane");
        models(source_ax,point);models(projected_ax,point);models(b.row_base,point);
        need(evaluate(source_target,point)==0 && evaluate(projected_target,point)==0
             && evaluate(packed_target,point)==0,"row-model consequences");
        out<<"{\"record\":\"row_subsystem_common_model\",\"case\":\""<<name<<"\",\"point\":";
        point_json(out,point,next);out<<",\"original_product\":"<<evaluate(original.product,point)
           <<",\"projected_product\":"<<evaluate(projected.product,point)<<"}\n";count.models++;
    }
    std::array<int,NV> active{};
    for(int row=0;row<b.m;row++)active[row*b.n]=1;
    std::vector<int> available;
    for(size_t i=0;i<source_ax.size();i++)if(source_ax[i].deg()<=4) {
        need(evaluate(source_ax[i],active)==0,"old degree-four axiom subsystem");
        available.push_back(int(i));
    }
    need(evaluate(projected.axioms[0],active)==1,"truncated-space countermodel");
    out<<"{\"record\":\"activity_change_control\",\"case\":\""<<name
       <<"\",\"scope\":\"consistent row subsystem, columns omitted\","
         "\"old_available_degree\":4,\"old_minimum_proof_degree\":5,"
         "\"new_axiom_degree\":3,\"old_available_axiom_indices\":";
    integers_json(out,available);out<<",\"point\":";point_json(out,active,next);
    out<<",\"new_companion\":";jsonpoly(out,projected.axioms[0]);out<<",\"target_value\":1}\n";
    count.activity++;count.cases++;
}
void run_board(std::ostream& out,RowCounts& count,int p,int n) {
    Board b=board(p,n);need(b.N+3<=NV,"variable capacity");
    Poly one(p,1),x=variable(p,0);
    std::vector<Poly> ys={variable(p,n),variable(p,n+1),variable(p,2*n)},input;
    for(const auto& y:ys)input.push_back(x+b.rows[0]*y);
    need(polynomial_rank(input,p)==3,"original nonlinear input rank");
    auto with_x=input;with_x.push_back(x);
    need(polynomial_rank(with_x,p)==4,"unprojected span already contains x");
    std::string name="row_source_n"+std::to_string(n)+"_F"+std::to_string(p);
    for(int i=0;i<3;i++) {
        std::vector<Poly> cof(b.row_base.size(),Poly(p));cof[0]=one;
        cof[b.N]=ys[i]*(input[i]+x-one);
        row_ns(out,count,name+"_input_Booleanity_"+std::to_string(i),
               b.row_base,cof,input[i]*input[i]-input[i],4);
    }
    int next=b.N;Block original=block(input,1,next);
    std::vector<int> sizes(next,p);for(int old=0;old<b.N;old++)sizes[old]=2;
    auto source_ax=domains(p,sizes);
    source_ax.insert(source_ax.end(),b.rows.begin(),b.rows.end());
    int companion_start=int(source_ax.size());
    source_ax.insert(source_ax.end(),original.axioms.begin(),original.axioms.end());
    int fixed_y=(b.m-1)*n;
    std::vector<Poly> source_cof(source_ax.size(),Poly(p));
    source_cof[fixed_y]=one;source_cof[b.N]=one;
    for(int i=0;i<3;i++)source_cof[companion_start+i]=Poly(p,-1)*original.coef[i];
    Poly target=original.product*original.product-original.product+b.boolean[fixed_y]+source_ax[b.N];
    int degree=row_ns(out,count,name+"_consequence",source_ax,source_cof,target,6);
    need(degree==6,"source consequence degree");
    out<<"{\"record\":\"row_source\",\"name\":\""<<name<<"\",\"p\":"<<p<<",\"n\":"<<n
       <<",\"coordinate_rule\":\"row*n+column\",\"coefficient_range\":["<<b.N<<','<<next
       <<"],\"input_tuple\":";poly_vector(out,input);
    out<<",\"scope\":\"Boolean row subsystem plus one ENS block; no column axioms in common models\"}\n";
    Projection last=projection(b,std::vector<int>(b.m,n-1));
    Projection first=projection(b,std::vector<int>(b.m,0));
    std::vector<int> cyclic(b.m);for(int row=0;row<b.m;row++)cyclic[row]=row%n;
    run_projection(out,count,b,"last",last,last,input,ys,original,source_ax,source_cof,target);
    run_projection(out,count,b,"first",first,last,input,ys,original,source_ax,source_cof,target);
    run_projection(out,count,b,"cyclic",projection(b,cyclic),last,input,ys,original,source_ax,source_cof,target);
}
void weak_row_control(std::ostream& out,RowCounts& count,int p) {
    int width=p+1;Poly one(p,1),row(p,-1),u(p,1);
    auto ax=domains(p,std::vector<int>(width,2));
    for(int j=0;j<width;j++)row=row+variable(p,j);
    for(int j=1;j<width;j++)u=u-variable(p,j);
    ax.push_back(row);std::vector<Poly> cof(ax.size(),Poly(p));cof[0]=one;
    cof[width]=Poly(p,-1)*(u+variable(p,0)-one);
    row_ns(out,count,"weak_row_pivot_Booleanity_F"+std::to_string(p),ax,cof,u*u-u,2);
    std::array<int,NV> point{};for(int j=0;j<width;j++)point[j]=1;
    models(ax,point);
    need(evaluate(u,point)==1 && evaluate(variable(p,1)*variable(p,2),point)==1,"weak-row control");
    out<<"{\"record\":\"weak_row_control\",\"p\":"<<p<<",\"single_row_width\":"<<width
       <<",\"point\":";point_json(out,point,width);
    out<<",\"row_equation_value\":0,\"projected_pivot\":1,\"same_row_product\":1,"
         "\"scope\":\"one row only; not a full-board column model\"}\n";count.weak++;
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_php_row_projection --out PATH");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"refuse to overwrite output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");
        out<<"{\"record\":\"metadata\",\"schema\":1,\"arithmetic\":\"exact Fp ordinary polynomials\","
             "\"monomial_encoding\":\"[coefficient,[[variable,exponent],...]]\","
             "\"zero_polynomial\":[],\"n_values\":[2,3],\"p_values\":[2,3,5],"
             "\"pivot_presets\":[\"last\",\"first\",\"cyclic\"],\"randomness\":\"none\","
             "\"scope\":\"full PHP base-image identities; consistent row-only models and activity controls\"}\n";
        RowCounts count;
        for(int p:{2,3,5}){for(int n:{2,3})run_board(out,count,p,n);weak_row_control(out,count,p);}
        need(count.cases==18 && count.certificates==612 && count.models==1326
             && count.activity==18 && count.weak==3,"summary counts");
        out<<"{\"record\":\"summary\",\"status\":\"passed\",\"projection_cases\":"<<count.cases
           <<",\"NS_certificates\":"<<count.certificates<<",\"row_subsystem_common_models\":"<<count.models
           <<",\"activity_controls\":"<<count.activity<<",\"weak_row_controls\":"<<count.weak<<"}\n";
        out.close();need(bool(out),"output write failed");
        std::cout<<"PASS: 18 projections, 612 NS certificates, 1326 row-subsystem models, "
                   "18 activity controls, 3 weak-row controls.\n";
        return 0;
    } catch(const std::exception& error) {std::cerr<<"FAIL: "<<error.what()<<'\n';return 1;}
}
