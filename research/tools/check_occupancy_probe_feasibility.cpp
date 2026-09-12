// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact NS/PC certificates and explicit second-moment designs for occupancy probes.
#define ENS_INPUT_REDUCTION_NO_MAIN
#include "check_ens_input_reduction.cpp"

int occupancy_mod(int value,int p){value%=p;return value<0?value+p:value;}
struct OccupancyCounts {int certificates=0,traces=0,normalizers=0,designs=0,constraints=0,controls=0;};
void occupancy_ns(std::ostream& out,OccupancyCounts& count,const std::string& name,
                  const std::vector<Poly>& axioms,const std::vector<Poly>& cof,
                  const Poly& target,int ceiling) {
    ns(out,name,axioms,cof,target,ceiling);count.certificates++;
}

using MomentMatrix=std::vector<std::vector<int>>;
MomentMatrix occupancy_moments(int n,int p) {
    int m=n+1,v=m*n;need(n>=3 && v<=128 && p<=7,"moment size/field guard");
    MomentMatrix moments(v+1,std::vector<int>(v+1));moments[0][0]=1;
    for(int i=0;i<m;i++)moments[0][1+i*n]=moments[1+i*n][0]=1;
    auto S=[&](int a,int b){return a<b?1:(a==b?(m-1-a)%2:0);};
    auto cross=[&](int j,int l,int a,int b) {
        if(j>l){std::swap(j,l);std::swap(a,b);}
        if(l>2)return 0;
        if(p==2) {
            if(j==0 && l==1)return S(a,b);
            if((j==0 && l==2) || (j==1 && l==2))return S(b,a);
        } else if(a!=b) {
            int half=modpow(2,p-2,p);
            if(j==0 && (l==1 || l==2))return half;
            if(j==1 && l==2)return p-half;
        }
        return 0;
    };
    for(int i=0;i<m;i++)for(int j=0;j<n;j++)for(int k=0;k<m;k++)for(int l=0;l<n;l++)
        moments[1+i*n+j][1+k*n+l]=j==l?(i==k && j==0?1:0):cross(j,l,i,k);
    return moments;
}
void moment_case(std::ostream& out,OccupancyCounts& count,int n,int p,bool valid) {
    auto L=occupancy_moments(n,p);int m=n+1,v=m*n,checks=0,failures=0;
    need(valid==(n%p==0),"moment validity parameter");
    const std::string name="moments_n"+std::to_string(n)+"_F"+std::to_string(p);
    for(int a=0;a<=v;a++)for(int b=0;b<=v;b++)need(L[a][b]==L[b][a],"nonsymmetric moments");
    auto check=[&](const std::string& kind,int generator,int multiplier,int value) {
        value=occupancy_mod(value,p);checks++;
        if(value) {
            failures++;
            out<<"{\"record\":\"moment_violation\",\"case\":\""<<name<<"\",\"kind\":\""<<kind
               <<"\",\"generator\":"<<generator<<",\"multiplier\":"<<multiplier<<",\"value\":"<<value<<"}\n";
        }
    };
    for(int i=0;i<m;i++)for(int a=0;a<=v;a++) {
        int value=-L[a][0];for(int j=0;j<n;j++)value+=L[a][1+i*n+j];
        check("row",i,a,value);
    }
    for(int j=1;j<n;j++)for(int a=0;a<=v;a++) {
        int value=0;for(int i=0;i<m;i++)value+=L[a][1+i*n+j];
        check("probe",j,a,value);
    }
    for(int a=1;a<=v;a++)check("Boolean",a,0,L[a][a]-L[a][0]);
    for(int j=0;j<n;j++)for(int i=0;i<m;i++)for(int k=i+1;k<m;k++)
        check("collision",(i*m+k)*n+j,0,L[1+i*n+j][1+k*n+j]);
    need(L[0][0]==1 && (valid?failures==0:failures>0),"moment design/control failed");
    out<<"{\"record\":\"moment_functional\",\"case\":\""<<name<<"\",\"n\":"<<n<<",\"p\":"<<p
       <<",\"coordinates\":\"constant at 0; x_i_j at 1+i*n+j\",\"matrix\":[";
    for(int a=0;a<=v;a++) {
        if(a)out<<',';
        out<<'[';
        for(int b=0;b<=v;b++){if(b)out<<',';out<<L[a][b];}out<<']';
    }
    out<<"],\"tested_NS2_generators\":"<<checks<<",\"violations\":"<<failures
       <<",\"normalized_design\":"<<(valid?"true":"false")<<"}\n";
    if(valid){count.designs++;count.constraints+=checks;}else count.controls++;
}

void symbolic_case(std::ostream&,OccupancyCounts&,int);
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","usage: check_occupancy_probe_feasibility --out NEW-PATH.jsonl");
        std::filesystem::path path(argv[2]);need(!std::filesystem::exists(path),"output already exists");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot open output");OccupancyCounts count;
        for(int p:{2,3,5})symbolic_case(out,count,p);
        moment_case(out,count,3,3,true);moment_case(out,count,4,2,true);moment_case(out,count,5,5,true);
        moment_case(out,count,4,3,false);moment_case(out,count,3,2,false);moment_case(out,count,4,5,false);
        out<<"{\"record\":\"summary\",\"NS_certificates\":"<<count.certificates<<",\"PC_traces\":"<<count.traces
           <<",\"one_row_normalizers\":"<<count.normalizers<<",\"NS2_designs\":"<<count.designs
           <<",\"annihilated_generators\":"<<count.constraints<<",\"controls\":"<<count.controls
           <<",\"verified\":true}\n";
        out.close();need(bool(out),"failed writing output");
        std::cout<<"Verified "<<count.certificates<<" NS certificates, "<<count.traces<<" PC traces, "
                 <<count.designs<<" normalized designs ("<<count.constraints<<" generators), and "
                 <<count.controls<<" controls.\n";
    } catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
void symbolic_case(std::ostream& out,OccupancyCounts& count,int p) {
    constexpr int n=3,m=4,variables=12;const Poly zero(p),one(p,1);
    const std::string name="symbolic_n3_F"+std::to_string(p);
    std::vector<Poly> rows,sigma;
    for(int i=0;i<m;i++) {
        Poly row(p,-1);for(int j=0;j<n;j++)row=row+variable(p,i*n+j);rows.push_back(row);
    }
    for(int j=0;j<n;j++) {
        Poly sum(p);for(int i=0;i<m;i++)sum=sum+variable(p,i*n+j);sigma.push_back(sum);
    }
    std::vector<NFRule> rules;
    for(int v=0;v<variables;v++)rules.push_back(domain_rule(p,v,2));
    int collision_index=-1;
    for(int j=0;j<n;j++)for(int i=0;i<m;i++)for(int k=i+1;k<m;k++) {
        if(j==0 && i==0 && k==1)collision_index=m+int(rules.size());
        Mon mon{};mon[i*n+j]=mon[k*n+j]=1;
        rules.push_back({variable(p,i*n+j)*variable(p,k*n+j),mon});
    }
    auto domain=rule_axioms(rules),base=rows;base.insert(base.end(),domain.begin(),domain.end());
    auto gamma=base;for(int j=1;j<n;j++)gamma.push_back(sigma[j]);
    Proof pc(p,gamma);std::vector<int> row_lines;
    std::vector<std::vector<Poly>> row_cof;
    for(int i=0;i<2;i++) {
        std::vector<Poly> cof(gamma.size(),zero);cof[i]=one;int line=pc.ax(i);
        for(int j=1;j<n;j++) {
            Poly cell=variable(p,i*n+j),D=cell*sigma[j]-cell;
            auto nf=normal_form(D,rules);need(nf.value==zero,"column occupancy identity");
            int probe=int(base.size())+j-1;cof[probe]=cof[probe]-cell;
            int cell_line=pc.mv(pc.ax(probe),i*n+j);
            for(size_t t=0;t<domain.size();t++)if(nf.cofactors[t].deg()>=0) {
                cof[m+t]=cof[m+t]+nf.cofactors[t];
                cell_line=pc.lc(cell_line,pc.mul(pc.ax(m+int(t)),nf.cofactors[t]),1,-1);
            }
            need(pc.val(cell_line)==cell,"PC occupied cell extraction");
            line=pc.lc(line,cell_line,1,-1);
        }
        Poly target=variable(p,i*n)-one;
        need(pc.val(line)==target,"PC unprobed-row consequence");
        occupancy_ns(out,count,name+"_row_"+std::to_string(i),gamma,cof,target,2);
        row_lines.push_back(line);row_cof.push_back(cof);
    }
    Poly X=variable(p,0),Y=variable(p,n);
    auto ref=row_cof[0];for(size_t t=0;t<ref.size();t++)ref[t]=Poly(p,-1)*Y*ref[t]-row_cof[1][t];
    ref[collision_index]=ref[collision_index]+one;
    occupancy_ns(out,count,name+"_NS3_refutation",gamma,ref,one,3);
    int final=pc.lc(pc.ax(collision_index),pc.mv(row_lines[0],n),1,-1);
    final=pc.lc(final,row_lines[1],1,-1);
    trace(out,pc,name+"_PC2_refutation",final,one,2);count.traces++;

    std::array<int,NV> affine_point{};for(int i=0;i<m;i++)affine_point[i*n]=1;
    models(rows,affine_point);for(int j=1;j<n;j++)need(evaluate(sigma[j],affine_point)==0,"affine control");
    need(evaluate(gamma[collision_index],affine_point)==1,"affine control accidentally a full model");
    out<<"{\"record\":\"degree_one_control\",\"case\":\""<<name<<"\",\"point\":";
    point_json(out,affine_point,variables);
    out<<",\"model_scope\":\"row equations and probed column sums only\",\"collision_value\":1}\n";
    count.controls++;

    if(n%p!=0) {
        int inverse=modpow(n%p,p-2,p);std::vector<Poly> beta,Hcof(base.size(),zero);
        Hcof[0]=Poly(p,-1);for(int i=0;i<m;i++)Hcof[i]=Hcof[i]-Poly(p,inverse)*X;
        Poly H=one;
        for(int j=0;j<n;j++) {
            Poly cell=variable(p,j),D=cell*sigma[j]-cell;
            auto nf=normal_form(D,rules);need(nf.value==zero,"normalizer local identity");
            int scalar=j==0?inverse:p-1;
            for(size_t t=0;t<domain.size();t++)Hcof[m+t]=Hcof[m+t]+Poly(p,scalar)*nf.cofactors[t];
            if(j>0){beta.push_back(cell+Poly(p,inverse)*X);H=H-beta.back()*sigma[j];}
        }
        occupancy_ns(out,count,name+"_one_row_base_zero",base,Hcof,H,2);
        auto short_ref=Hcof;short_ref.insert(short_ref.end(),beta.begin(),beta.end());
        occupancy_ns(out,count,name+"_NS2_refutation",gamma,short_ref,one,2);
        int next=variables;Block U=block({sigma[1],sigma[2]},1,next);
        need(affine_image(U.product,U,beta)==H,"source ENS product image");
        for(size_t i=0;i<beta.size();i++) {
            Poly image=affine_image(U.axioms[i],U,beta);
            need(image==sigma[i+1]*H && U.axioms[i].deg()==3,"companion image/original degree");
            auto cof=Hcof;for(auto& term:cof)term=term*sigma[i+1];
            occupancy_ns(out,count,name+"_companion_"+std::to_string(i),base,cof,image,3);
            Poly field=powp(beta[i],p)-beta[i];auto nf=normal_form(field,rules);
            need(nf.value==zero,"normalizer coefficient field");
            occupancy_ns(out,count,name+"_field_"+std::to_string(i),domain,nf.cofactors,field,p);
        }
        out<<"{\"record\":\"one_row_normalizer\",\"case\":\""<<name<<"\",\"n_inverse\":"<<inverse
           <<",\"source_inputs\":";poly_vector(out,U.inputs);out<<",\"source_product\":";jsonpoly(out,U.product);
        out<<",\"source_companions\":";poly_vector(out,U.axioms);out<<",\"coefficient_images\":";
        poly_vector(out,beta);out<<",\"product_image\":";jsonpoly(out,H);out<<",\"verified\":true}\n";
        count.normalizers++;
    }
}
