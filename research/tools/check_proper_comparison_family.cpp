// Copyright (c) 2026 Kamil Braun. MIT License; see ../../LICENSE.
// Factored certificates reference the verified h=2 local OR-union template.
#include "binary_php.hpp"
#include <map>
#include <numeric>
#include <queue>
using namespace binary_php;

void ints(std::ostream& out,const std::vector<int>& v) {
    out<<'[';for(size_t j=0;j<v.size();j++){if(j)out<<',';out<<v[j];}out<<']';
}
void quoted(std::ostream& out,const std::string& value) {
    out<<'"';for(char c:value){if(c=='"'||c=='\\')out<<'\\';out<<c;}out<<'"';
}
struct Block {std::vector<int> inputs;int start=-1;bool packed=false;};
struct Module {int i,j,a,b,u;std::vector<int> map;};
void essentiality(const std::string& name,int m,int old,int variables,const std::vector<Word>& signals,
                  const std::vector<Block>& blocks,const std::vector<int>& A,const std::vector<int>& B,
                  const std::vector<std::vector<int>>& U,std::ostream& out) {
    int total_checks=0;
    for(int omitted=0;omitted<int(blocks.size());omitted++) {
        Word desired=0;
        for(int i=0;i<m;i++)if(!(omitted>=m && omitted<2*m && i==0))
            desired|=Word(1)<<blocks[A[i]].inputs[0];
        for(int j=0;j<m;j++)if(!(omitted<m && j==0))
            desired|=Word(1)<<blocks[B[j]].inputs[0];
        Word old_point=0;
        for(int i=0;i<old;i++)if(__builtin_parityll(signals[i]&desired))old_point|=Word(1)<<i;
        std::vector<int> values(old),old_ones,coefficient_ones,products(blocks.size());
        for(int i=0;i<old;i++) {
            values[i]=__builtin_parityll(signals[i]&old_point);
            need(values[i]==int((desired>>i)&1),"inverse old-point coordinates");
            if((old_point>>i)&1)old_ones.push_back(i);
        }
        std::vector<bool> coefficients(variables);
        for(int b=0;b<int(blocks.size());b++)if(b!=omitted) {
            for(int k=0;k<int(blocks[b].inputs.size());k++)if(values[blocks[b].inputs[k]]) {
                int coordinate=blocks[b].start+k;coefficients[coordinate]=true;coefficient_ones.push_back(coordinate);break;
            }
        }
        int checked=0,violated=0;
        for(int b=0;b<int(blocks.size());b++) {
            int product=1,arity=int(blocks[b].inputs.size());
            for(int row=0;row<2;row++) {
                int factor=1;
                for(int k=0;k<arity;k++)factor^=coefficients[blocks[b].start+row*arity+k] && values[blocks[b].inputs[k]];
                product&=factor;
            }
            products[b]=product;
            for(int signal:blocks[b].inputs) {
                int value=values[signal]*product;
                if(b==omitted)violated+=value;
                else{need(value==0,"retained companion fails deletion countermodel");++checked;}
            }
        }
        int target=0,sa=0,sb=0;
        for(int i=0;i<m;i++){sa^=products[A[i]];sb^=products[B[i]];}
        for(int i=0;i<m;i++)for(int j=0;j<m;j++)target^=products[U[i][j]];
        target^=sa*sb;
        need(target==1 && violated>0,"block deletion did not separate target");total_checks+=checked;
        out<<"{\"type\":\"block_deletion_countermodel\",\"case\":\""<<name<<"\",\"omitted_block\":"<<omitted
           <<",\"old_x_ones\":";ints(out,old_ones);out<<",\"coefficient_ones\":";ints(out,coefficient_ones);
        out<<",\"block_product_values\":";ints(out,products);
        out<<",\"retained_companions_checked\":"<<checked<<",\"violated_omitted_companions\":"<<violated
           <<",\"target_value\":1}\n";
    }
    out<<"{\"type\":\"essentiality_result\",\"case\":\""<<name<<"\",\"countermodels\":"<<blocks.size()
       <<",\"retained_companion_checks\":"<<total_checks<<"}\n";
    std::cout<<name<<": "<<blocks.size()<<" block-deletion countermodels and "<<total_checks
             <<" retained companion checks.\n";
}
int balance(const std::vector<std::vector<int>>& graph,const std::vector<bool>& removed,int children) {
    std::vector<bool> seen=removed;int largest=0;
    for(int first=0;first<int(graph.size());first++)if(!seen[first]) {
        std::queue<int> queue;queue.push(first);seen[first]=true;int weight=0;
        while(!queue.empty()) {
            int x=queue.front();queue.pop();weight+=x<children;
            for(int y:graph[x])if(!seen[y]){seen[y]=true;queue.push(y);}
        }
        largest=std::max(largest,weight);
    }
    return largest;
}
void run_case(const std::string& name,int m,int r,bool shared,std::ostream& out,bool models_only=false) {
    constexpr int h=2;const int old=2*m*r;need(old%2==0 && old<=60,"old-coordinate word guard");
    const Word all=(Word(1)<<old)-1;
    std::vector<Word> signals;for(int i=0;i<old;i++)signals.push_back(all^(Word(1)<<i));
    for(int i=0;i<old;i++) {
        Word square=0;for(int j=0;j<old;j++)if((signals[i]>>j)&1)square^=signals[j];
        need(square==(Word(1)<<i),"dense old-coordinate map not self-inverse");
    }
    out<<"{\"type\":\"case\",\"name\":\""<<name<<"\",\"m\":"<<m<<",\"h\":2,\"r\":"<<r
       <<",\"old_variables\":"<<old<<",\"shared_span_control\":"<<(shared?"true":"false")
       <<",\"signal_words\":[";
    for(int i=0;i<old;i++){if(i)out<<',';out<<signals[i];}out<<"]}\n";
    std::map<std::vector<int>,int> canonical;std::vector<Block> blocks;
    auto intern=[&](std::vector<int> inputs) {
        std::sort(inputs.begin(),inputs.end());inputs.erase(std::unique(inputs.begin(),inputs.end()),inputs.end());
        auto it=canonical.find(inputs);if(it!=canonical.end())return it->second;
        int id=int(blocks.size());canonical.emplace(inputs,id);blocks.push_back({inputs,-1,int(inputs.size())<=2*h});return id;
    };
    std::vector<int> A(m),B(m);std::vector<std::vector<int>> U(m,std::vector<int>(m));
    for(int i=0;i<m;i++) {
        std::vector<int> inputs(r);std::iota(inputs.begin(),inputs.end(),shared?0:i*r);A[i]=intern(inputs);
    }
    for(int j=0;j<m;j++) {
        std::vector<int> inputs(r);std::iota(inputs.begin(),inputs.end(),shared?0:(m+j)*r);B[j]=intern(inputs);
    }
    for(int i=0;i<m;i++)for(int j=0;j<m;j++) {
        auto inputs=blocks[A[i]].inputs;inputs.insert(inputs.end(),blocks[B[j]].inputs.begin(),blocks[B[j]].inputs.end());
        U[i][j]=intern(inputs);
    }
    int next=old,retained=0,packed=0,literal_directions=0;
    for(int id=0;id<int(blocks.size());id++) {
        Block& b=blocks[id];Space span(old);
        for(int signal:b.inputs)span.add(Bits{signals[signal]});
        need(span.rank==int(b.inputs.size()),"input rank after dense coordinate change");
        int literals=0;
        for(int j=0;j<old;j++)literals+=zero(span.reduce(Bits{Word(1)<<j}));
        literal_directions+=literals;
        if(b.packed)++packed;else{b.start=next;next+=h*int(b.inputs.size());++retained;}
        out<<"{\"type\":\"canonical_block\",\"case\":\""<<name<<"\",\"id\":"<<id<<",\"signals\":";
        ints(out,b.inputs);out<<",\"rank\":"<<span.rank<<",\"packed\":"<<(b.packed?"true":"false")
           <<",\"coefficient_start\":"<<b.start<<",\"literal_directions\":"<<literals;
        if(b.packed) {
            out<<",\"packing_bins\":[";
            for(int j=0;j<int(b.inputs.size());j+=2){if(j)out<<',';out<<'['<<b.inputs[j];if(j+1<int(b.inputs.size()))out<<','<<b.inputs[j+1];out<<']';}
            out<<']';
        }
        out<<"}\n";
    }
    need(literal_directions==0,"unexpected literal direction in a dense input span");
    if(models_only) {
        need(!shared && r==5 && retained==int(blocks.size()),"essentiality case must be the retained independent family");
        essentiality(name,m,old,next,signals,blocks,A,B,U,out);return;
    }
    std::vector<Module> modules;int domain_only=0,packed_zero=0;
    for(int i=0;i<m;i++)for(int j=0;j<m;j++) {
        int a=A[i],b=B[j],u=U[i][j];
        if(blocks[a].packed && blocks[b].packed && blocks[u].packed) {
            ++packed_zero;
            out<<"{\"type\":\"removed_module\",\"case\":\""<<name<<"\",\"i\":"<<i<<",\"j\":"<<j
               <<",\"reason\":\"all packed products agree identically\"}\n";continue;
        }
        if(a==b && b==u) {
            ++domain_only;
            out<<"{\"type\":\"removed_module\",\"case\":\""<<name<<"\",\"i\":"<<i<<",\"j\":"<<j
               <<",\"reason\":\"canonical P-P^2 uses domains only\",\"block\":"<<a<<"}\n";continue;
        }
        need(r==5 && !blocks[a].packed && !blocks[b].packed && !blocks[u].packed,"unsupported partially packed template");
        Module module{i,j,a,b,u,{}};
        module.map=blocks[a].inputs;module.map.insert(module.map.end(),blocks[b].inputs.begin(),blocks[b].inputs.end());
        for(int p=0;p<h*r;p++)module.map.push_back(blocks[a].start+p);
        for(int p=0;p<h*r;p++)module.map.push_back(blocks[b].start+p);
        for(int p=0;p<2*h*r;p++)module.map.push_back(blocks[u].start+p);
        need(module.map.size()==50,"local template variable count");
        auto unique=module.map;std::sort(unique.begin(),unique.end());
        need(std::adjacent_find(unique.begin(),unique.end())==unique.end(),"local template renaming is not injective");
        int id=int(modules.size());modules.push_back(module);
        out<<"{\"type\":\"module\",\"case\":\""<<name<<"\",\"id\":"<<id<<",\"i\":"<<i<<",\"j\":"<<j
           <<",\"blocks\":["<<a<<','<<b<<','<<u<<"],\"variable_map\":";ints(out,module.map);
        out<<",\"template_case\":\"proper_union_h2\"}\n";
    }
    std::map<std::pair<int,int>,std::vector<std::pair<int,std::string>>> cofactors;
    for(int id=0;id<int(modules.size());id++) {
        const auto& module=modules[id];
        for(int i=0;i<2*r;i++)cofactors[{module.u,i}].push_back({id,"E0_"+std::to_string(i)});
        for(int i=0;i<r;i++) {
            cofactors[{module.a,i}].push_back({id,"E1_"+std::to_string(i)});
            cofactors[{module.b,i}].push_back({id,"E2_"+std::to_string(i)});
        }
    }
    int summands=0;
    for(const auto& [key,terms]:cofactors) {
        out<<"{\"type\":\"collected_cofactor\",\"case\":\""<<name<<"\",\"block\":"<<key.first
           <<",\"input\":"<<key.second<<",\"summands\":[";
        for(size_t j=0;j<terms.size();j++) {
            if(j)out<<',';
            out<<"{\"module\":"<<terms[j].first<<",\"polynomial\":\"proper_union_h2/"<<terms[j].second<<"/cofactor\"}";++summands;
        }
        out<<"]}\n";
    }
    int projections=0;
    for(int id=0;id<int(modules.size());id++) {
        const Module& wanted=modules[id];
        for(int a=0;a<r;a++)for(int b=0;b<r;b++) {
            std::vector<int> surviving,killed;
            for(const auto& term:cofactors.at({wanted.a,a})) {
                const Module& source=modules[term.first];
                if(source.u==wanted.u){need(source.b==wanted.b,"isolation parent not unique");surviving.push_back(term.first);}
                else killed.push_back(term.first);
            }
            need(surviving==std::vector<int>{id} && int(killed.size())==m-1,"collected coefficient isolation failed");
            out<<"{\"type\":\"cofactor_projection\",\"case\":\""<<name<<"\",\"module\":"<<id
               <<",\"child_input\":"<<a<<",\"foreign_input\":"<<b<<",\"surviving_modules\":";
            ints(out,surviving);out<<",\"killed_modules\":";ints(out,killed);
            out<<",\"old_signal_monomial\":[["<<blocks[wanted.a].inputs[a]<<",1],["
               <<blocks[wanted.b].inputs[b]<<",2]]}\n";++projections;
        }
    }
    int separator=0;bool exhaustive=false;
    if(!modules.empty()) {
        need(int(blocks.size())==2*m+m*m && int(modules.size())==m*m,"main incidence size");
        std::vector<std::vector<int>> graph(blocks.size());
        for(const Module& module:modules)for(int child:{module.a,module.b}) {
            graph[child].push_back(module.u);graph[module.u].push_back(child);
        }
        out<<"{\"type\":\"comparison_graph\",\"case\":\""<<name<<"\",\"child_vertices\":"<<2*m<<",\"adjacency\":[";
        for(size_t i=0;i<graph.size();i++){if(i)out<<',';ints(out,graph[i]);}out<<"]}\n";
        separator=(2*m+2)/3;std::vector<bool> removed(graph.size());
        std::vector<int> witness;for(int i=0;i<separator;i++){removed[A[i]]=true;witness.push_back(A[i]);}
        need(3*balance(graph,removed,2*m)<=4*m,"balanced-separator upper witness");
        std::vector<int> histogram(graph.size()+1);int best=int(graph.size());
        if(m<=3) {
            exhaustive=true;Word stop=Word(1)<<graph.size();
            for(Word mask=0;mask<stop;mask++) {
                for(size_t i=0;i<graph.size();i++)removed[i]=(mask>>i)&1;
                if(3*balance(graph,removed,2*m)<=4*m) {
                    int size=__builtin_popcountll(mask);++histogram[size];best=std::min(best,size);
                }
            }
            need(best==separator,"exhaustive separator disagrees with analytic minimum");
        }
        out<<"{\"type\":\"separator_certificate\",\"case\":\""<<name<<"\",\"minimum\":"<<separator
           <<",\"removed_child_witness\":";ints(out,witness);
        out<<",\"exhaustive\":"<<(exhaustive?"true":"false");
        if(exhaustive){out<<",\"balanced_separator_size_histogram\":";ints(out,histogram);}
        out<<",\"lower_bound\":\"Fewer than m removed child/union vertices leave the remaining child graph connected; balance then needs at least ceil(2m/3) removed children.\"}\n";
    }
    if(shared)need(retained==1 && modules.empty() && domain_only==m*m && domain_only%2==1,"shared-span control");
    else if(r<=h)need(retained==0 && modules.empty() && packed_zero==m*m,"packing control");
    else need(int(cofactors.size())==2*m*r+2*m*m*r && summands==4*m*m*r && projections==m*m*r*r,"complete family ledger");
    out<<"{\"type\":\"family_result\",\"name\":\""<<name<<"\",\"canonical_blocks\":"<<blocks.size()
       <<",\"retained_blocks\":"<<retained<<",\"packed_blocks\":"<<packed<<",\"comparison_modules\":"<<modules.size()
       <<",\"domain_only_modules\":"<<domain_only<<",\"collected_cofactors\":"<<cofactors.size()
       <<",\"cofactor_summands\":"<<summands<<",\"nonzero_projection_checks\":"<<projections
       <<",\"minimum_balanced_separator\":"<<separator<<",\"total_variables_after_packing\":"<<next
       <<",\"certificate_degree_upper\":"<<(modules.empty()?(domain_only?8:0):12)<<"}\n";
    std::cout<<name<<": "<<retained<<" retained blocks, "<<modules.size()<<" modules, "<<projections
             <<" isolated collected coefficients, separator "<<separator<<".\n";
}
int main(int argc,char** argv) {
    try {
        bool models_only=argc==6 && std::string(argv[5])=="--essentiality";
        need((argc==5 || models_only) && std::string(argv[1])=="--template" && std::string(argv[3])=="--out",
             "usage: check_proper_comparison_family --template LOCAL.jsonl --out NEW.jsonl [--essentiality]");
        std::ifstream source(argv[2]);need(source.good(),"local template unavailable");
        std::ifstream existing(argv[4]);need(!existing.good(),"output exists");
        std::ofstream out(argv[4]);need(bool(out),"cannot open output");
        out<<"{\"schema\":1,\"field\":2,\"template\":";quoted(out,argv[2]);
        out<<",\"template_case\":\"proper_union_h2\",\"essentiality_mode\":"<<(models_only?"true":"false")
           <<",\"scope\":\"Source-compatible fixed-value certificates and block-deletion controls; not a PHP refutation\"}\n";
        for(int m:{2,3,6})run_case("independent_m"+std::to_string(m),m,5,false,out,models_only);
        if(!models_only){run_case("equal_span_control",3,5,true,out);run_case("packing_control",3,2,false,out);}
        out.close();need(bool(out),"output write failed");return 0;
    } catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
