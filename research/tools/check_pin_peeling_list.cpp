// Exact bounded pin-peeling/list-rank controls with pins outside Q.
// Tests false code-matched pins and early slot revelation; no heavy rounds or probability estimates.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using V=std::vector<int>;
struct Pattern { int row,mask,value; };
using Term=std::vector<Pattern>;
struct Node { int term,begin,end; };
struct Move { int row,hole,pos,last; };
struct Path { std::vector<Node> nodes; std::vector<Move> moves; };
struct Candidate { V rows,labels; Path path; uint64_t poly; int degree; V events; std::string word; int peels,forward; };
const V code={-1,-1,-1,5,6,1,2,3,7}, holes={0,4};
int s_global=1;
std::vector<Term> terms;
V pin_row,pin_label;
void require(bool b,const char* msg) { if(!b) throw std::runtime_error(msg); }
bool matches(int x,const Pattern& p) { return (x&p.mask)==p.value; }
bool next_node(V a,Path path,Path& result);
bool query_node(V a,Path path,const V& uncovered,int at,Path& result) {
    const int t=path.nodes.back().term;
    const int pos=uncovered[at], row=terms[t][pos].row;
    for(int h:holes) {
        if(std::find(a.begin(),a.end(),h)!=a.end()) continue;
        V b=a; b[row]=h; Path p=path;
        bool last=at+1==int(uncovered.size()) || int(p.moves.size())+1==s_global;
        p.moves.push_back({row,h,pos,int(last)}); p.nodes.back().end=int(p.moves.size());
        if(int(p.moves.size())==s_global) { result=p; return true; }
        if(at+1<int(uncovered.size())) {
            if(query_node(b,p,uncovered,at+1,result)) return true;
        } else if(next_node(b,p,result)) return true;
    }
    return false;
}
bool term_dead(int t,const V& a,unsigned hidden=0) {
    if(pin_row[t]>=0) {
        int j=pin_row[t];
        if(j<s_global && (hidden&(1U<<j))) return true;
        if(a[j]!=pin_label[t]) return true; // every pin is outside Q
    }
    for(const auto& p:terms[t]) if(a[p.row]>=0 && !matches(a[p.row],p)) return true;
    return false;
}
int pick(const V& a,unsigned hidden=0) {
    for(int priority=0;priority<2;++priority) for(int t=0;t<int(terms.size());++t)
        if((pin_row[t]<0)==bool(priority) && !term_dead(t,a,hidden)) return t;
    return -1;
}
bool next_node(V a,Path path,Path& result) {
    for(int t=0;t<int(terms.size());++t) if(!term_dead(t,a)) {
        bool complete=true;
        for(const auto& p:terms[t]) if(a[p.row]<0) complete=false;
        if(complete) return false;
    }
    int t=pick(a);if(t<0)return false;
    V un;
    for(int k=0;k<int(terms[t].size());++k) if(a[terms[t][k].row]<0) un.push_back(k);
    require(!un.empty(),"selected a satisfied original term");
    int begin=int(path.moves.size());path.nodes.push_back({t,begin,begin});
    return query_node(a,path,un,0,result);
}
uint64_t times_literal(uint64_t f,int variable,bool positive,int vars) {
    uint64_t g=0;
    for(int m=0;m<(1<<vars);++m) if((f>>m)&1U) g^=uint64_t(1)<<(m|(1<<variable));
    return positive ? g : g^f;
}
uint64_t witness(const Path& path,const V& js,const V& y,int& degree,V& events,
                 std::string& word,int& peels,int& forward) {
    V a=code;for(int k=0;k<s_global;++k)a[k]=y[k];
    unsigned hidden=(1U<<s_global)-1;int done=0,vars=3*s_global;uint64_t f=1;
    auto record=[&](int t,int action) {
        events.push_back(pin_row[t]<0?1:0);events.push_back(t);
        word+=action<0?"A;":"P"+std::to_string(action)+";";
        for(const auto& p:terms[t]) {
            if(p.row<s_global && (hidden&(1U<<p.row))) {
                for(int b=0;b<3;++b) if(p.mask&(1<<b))
                    f=times_literal(f,3*p.row+b,p.value&(1<<b),vars);
            } else if(a[p.row]>=0 && !matches(a[p.row],p)) f=0;
        }
    };
    for(const auto& node:path.nodes) {
        require(node.begin==done,"noncontiguous original trace");
        for(int attempts=0;;++attempts) {
            require(attempts<=s_global,"peeling did not terminate");
            int t=pick(a,hidden);require(t>=0,"simulation lost the real current term");
            if(t==node.term) {record(t,-1);break;}
            int j=pin_row[t];require(j>=0,"misleading term lacks a matched pin");
            auto it=std::find(js.begin(),js.end(),j);
            require(it!=js.end(),"misleading pin not on a moved row");
            int k=int(it-js.begin());require(k>=done && (hidden&(1U<<k)),"peel is not a fresh future move");
            record(t,k);++peels;if(k>done)++forward;
            a[j]=-1;hidden&=~(1U<<k);a[k]=code[j];
        }
        for(int k=node.begin;k<node.end;++k) {
            const auto& m=path.moves[k];a[m.row]=m.hole;a[k]=code[m.row];hidden&=~(1U<<k);++done;
        }
    }
    degree=0;
    for(int m=0;m<(1<<vars);++m) if((f>>m)&1U)degree=std::max(degree,__builtin_popcount(unsigned(m)));
    require(int(events.size())/2<=2*s_global,"too many advance/peel events in no-round test");
    return f;
}
int eval(uint64_t p,const V& y) {
    int x=0,v=0; for(int k=0;k<int(y.size());++k) x|=y[k]<<(3*k);
    for(int m=0;m<(1<<(3*int(y.size())));++m) if(((p>>m)&1U) && (m&x)==m) v^=1;
    return v;
}
V trace_key(const Path& p) { V x; for(const auto& n:p.nodes) x.push_back(n.term); return x; }
std::string raw_key(const Path& p) {
    std::string x;
    for(const auto& m:p.moves) x+=std::to_string(m.pos)+","+std::to_string(m.last)+","+std::to_string(m.hole)+";";
    return x;
}
void emit_v(std::ostream& o,const V& v) {
    o<<'['; for(size_t k=0;k<v.size();++k) { if(k) o<<','; o<<v[k]; } o<<']';
}
uint64_t state=178923;
unsigned rnd(unsigned bound) { state^=state<<13;state^=state>>7;state^=state<<17;return unsigned(state%bound); }
int main(int argc,char** argv) try {
    require(argc==3 && std::string(argv[1])=="--out","usage: check_pin_peeling_list --out FILE");
    std::ofstream out(argv[2]);require(bool(out),"cannot open output");
    // At most 2 * 6*5 candidates per reader; 131 tiny readers, 6 signature bits.
    out<<"{\"scope\":\"pin-peeling fibers with outside pins; exact F2 witnesses; no heavy rounds\",\"seed\":178923,\"n\":8,\"N\":2,\"readers\":[";
    int total=0, accepted=0, fibers=0,multi=0,maxfiber=0; bool first=true; int raw_max=0,total_peels=0,total_forward=0;
    for(int test=0;test<131;++test) {
        s_global=1+(test%2);terms.clear();pin_row.clear();pin_label.clear();
        if(test==0) {
            s_global=1;terms={{{3,4,4}},{{4,4,4}}};pin_row={4,3};pin_label={6,5};
        } else if(test==1) {
            s_global=2;terms={{{3,4,4}},{{4,4,4}},{{1,4,0},{7,2,2}},{{1,4,4},{8,2,2}}};
            pin_row={4,3,-1,-1};pin_label={6,5,0,0};
        } else if(test==2) {
            s_global=2;terms={{{3,4,4}},{{3,4,4}},{{7,2,2}}};
            pin_row={7,-1,-1};pin_label={3,0,0};
        } else {
            int count=2+int(rnd(7));
            for(int t=0;t<count;++t) {
                V rows(9);std::iota(rows.begin(),rows.end(),0);
                for(int a=8;a>0;--a)std::swap(rows[a],rows[rnd(unsigned(a+1))]);
                int r=1+int(rnd(3));Term term;
                for(int k=0;k<r;++k) {
                    int mask=1<<rnd(3);if(test>96 && rnd(2))mask|=1<<rnd(3);
                    term.push_back({rows[k],mask,int(rnd(8))&mask});
                }
                terms.push_back(term);
                pin_row.push_back(rnd(2)?rows[r]:-1);pin_label.push_back(code[3+rnd(6)]);
            }
        }
        std::map<std::string,std::vector<Candidate>> groups;
        std::map<std::string,int> raw_counts;
        for(int j=3;j<9;++j) for(int l=3;l<(s_global==1?4:9);++l) {
            if(s_global==2 && j==l) continue;
            ++total; V js={j};if(s_global==2) js.push_back(l);
            V a=code,y;for(int k=0;k<s_global;++k) {y.push_back(code[js[k]]);a[js[k]]=-1;a[k]=y.back();}
            Path path;if(!next_node(a,{},path)) continue;
            bool ok=true;
            for(int k=0;k<s_global;++k) if(path.moves[k].row!=js[k]) ok=false;
            if(!ok) continue;
            V free=y,excluded;std::sort(free.begin(),free.end());
            for(const auto& node:path.nodes) {
                if(pin_row[node.term]>=0)excluded.push_back(pin_label[node.term]);
                for(int k=node.begin;k<node.end;++k) {
                    const auto& m=path.moves[k];const auto& pat=terms[node.term][m.pos];
                    auto it=std::find_if(free.begin(),free.end(),[&](int h){return matches(h,pat)&&std::find(excluded.begin(),excluded.end(),h)==excluded.end();});
                    if(it==free.end() || *it!=y[k]) {ok=false;break;}
                    free.erase(it);
                }
            }
            if(!ok)continue;
            int deg=0,peels=0,forward=0;V events;std::string word;
            uint64_t p=witness(path,js,y,deg,events,word,peels,forward);
            require(eval(p,y)==1,"zero diagonal augmented trace witness");
            std::string raw=raw_key(path);++raw_counts[raw];
            groups[raw+"/"+word].push_back({js,y,path,p,deg,events,word,peels,forward});
            ++accepted;total_peels+=peels;total_forward+=forward;
        }
        for(const auto& z:raw_counts)raw_max=std::max(raw_max,z.second);
        if(!first) out<<',';
        first=false;
        out<<"{\"test\":"<<test<<",\"s\":"<<s_global<<",\"terms\":[";
        for(size_t t=0;t<terms.size();++t) {
            if(t) out<<',';
            out<<'[';
            for(size_t k=0;k<terms[t].size();++k) {if(k) out<<',';auto p=terms[t][k];out<<'['<<p.row<<','<<p.mask<<','<<p.value<<']';}
            out<<']';
        }
        out<<"],\"pins\":[";
        for(size_t t=0;t<terms.size();++t){if(t)out<<',';out<<'['<<pin_row[t]<<','<<pin_label[t]<<']';}
        out<<"],\"fibers\":[";bool fg=true;
        for(auto& item:groups) {
            auto& cs=item.second;
            std::sort(cs.begin(),cs.end(),[](const auto& a,const auto& b){return a.events<b.events;});
            int z=int(cs.size());++fibers;if(z>1)++multi;maxfiber=std::max(maxfiber,z);

            std::vector<uint64_t> matrix;
            for(int i=0;i<z;++i) {
                uint64_t row=0;
                for(int j=0;j<z;++j) {int v=eval(cs[i].poly,cs[j].labels);if(i<j)require(!v,"upper triangular entry nonzero");if(i==j)require(v,"diagonal missing");row|=uint64_t(v)<<j;}
                matrix.push_back(row);
            }
            auto reduced=matrix;int rank=0;
            for(int col=0;col<z;++col) {
                int pivot=rank;while(pivot<z && !((reduced[pivot]>>col)&1U))++pivot;
                if(pivot==z)continue;
                std::swap(reduced[rank],reduced[pivot]);
                for(int i=0;i<z;++i)if(i!=rank && ((reduced[i]>>col)&1U))reduced[i]^=reduced[rank];
                ++rank;
            }
            require(rank==z,"fiber witnesses are dependent");
            if(!fg)out<<',';
            fg=false;
            out<<"{\"raw_advice\":\""<<item.first<<"\",\"rank\":"<<rank<<",\"preimages\":[";
            for(int i=0;i<z;++i) {
                if(i)out<<',';
                out<<"{\"moves\":";emit_v(out,cs[i].rows);out<<",\"slot_labels\":";emit_v(out,cs[i].labels);
                out<<",\"terms\":";emit_v(out,trace_key(cs[i].path));out<<",\"extended_trace\":";emit_v(out,cs[i].events);out<<",\"peels\":"<<cs[i].peels<<",\"forward_peels\":"<<cs[i].forward;out<<",\"degree\":"<<cs[i].degree<<",\"monomials\":[";
                bool fm=true;for(int m=0;m<(1<<(3*s_global));++m)if((cs[i].poly>>m)&1U){if(!fm)out<<',';fm=false;out<<m;}
                out<<"],\"evaluation_row_mask\":"<<matrix[i]<<'}';
            }
            out<<"]}";
        }
        out<<"]}";
    }
    require(raw_max>=2 && total_peels>0 && total_forward>0 && multi>0,"nonvacuous peeling/list controls missing");
    out<<"],\"summary\":{\"candidate_inputs\":"<<total<<",\"accepted_preimages\":"<<accepted<<",\"fibers\":"<<fibers<<",\"multiple_preimage_fibers\":"<<multi<<",\"largest_fiber\":"<<maxfiber<<",\"raw_maximum_fiber\":"<<raw_max<<",\"peeling_events\":"<<total_peels<<",\"forward_peeling_events\":"<<total_forward<<",\"all_triangular_checks_passed\":true}}\n";
    require(bool(out),"output write failed");
    std::cout<<"Candidates "<<total<<"; accepted "<<accepted<<"; fibers "<<fibers<<"; multiple fibers "<<multi<<"; maximum "<<maxfiber<<". Exact triangular checks passed; nontrivial peeling and forward revelation controls passed.\n";
} catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
