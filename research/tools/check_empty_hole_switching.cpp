// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact round trips for the empty-aware bipartite switching injection.
// Run under compute.sh; finite checks do not prove the asymptotic estimate.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using Edge=std::pair<int,int>;using Term=std::vector<Edge>;using Formula=std::vector<Term>;
static void need(bool b,const char*s){if(!b)throw std::runtime_error(s);}
// An action (p,h) occupies an edge; (-1,h) declares that hole empty.
struct State{int n;Term edges;std::set<int> empty;
  int row(int p)const{for(auto e:edges)if(e.first==p)return e.second;return -1;}
  int hole(int h)const{for(auto e:edges)if(e.second==h)return e.first;return -1;}
  bool decided(int v)const{return v<=n?row(v)>=0:hole(v-n-1)>=0||empty.count(v-n-1);}
  void act(Edge e){need(e.second>=0&&e.second<n,"hole index");need(hole(e.second)<0&&!empty.count(e.second),"hole already resolved");if(e.first<0)empty.insert(e.second);else{need(e.first<=n&&row(e.first)<0,"pigeon already assigned");edges.push_back(e);}}
};
static std::vector<int> vertices(const Term&t,int n){std::vector<int>v;for(auto e:t){if(e.first>=0)v.push_back(e.first);v.push_back(n+1+e.second);}return v;}
static std::pair<int,Term> first(const Formula&F,const State&s){for(size_t i=0;i<F.size();++i){Term free;bool bad=false;for(auto e:F[i]){if(s.row(e.first)==e.second)continue;if(s.row(e.first)>=0||s.hole(e.second)>=0||s.empty.count(e.second)){bad=true;break;}free.push_back(e);}if(!bad)return {int(i),free};}return {-1,{}};}
struct Round{int term;Term sigma,path;std::vector<int> beta,mask;};
struct Code{Term augmented;std::vector<std::vector<int>> beta,mask;std::vector<int> answers;};
static std::string key(const Code&c){std::ostringstream o;for(auto e:c.augmented)o<<e.first<<','<<e.second<<';';o<<'|';for(auto b:c.beta){for(int x:b)o<<x;o<<';';}o<<'|';for(auto b:c.mask){for(int x:b)o<<x;o<<';';}o<<'|';for(int x:c.answers)o<<x<<',';return o.str();}
static std::string key(Term t){std::sort(t.begin(),t.end());std::ostringstream o;for(auto e:t)o<<e.first<<','<<e.second<<';';return o.str();}
static std::pair<Code,int> encode(const Formula&F,const State&mu,const Term&path){
  int n=mu.n;State cur=mu;size_t at=0;std::vector<Round> rounds;
  while(at<path.size()){
    auto f=first(F,cur);need(f.first>=0&&!f.second.empty(),"path at nonconstant term");auto kv=vertices(f.second,n);std::set<int>K(kv.begin(),kv.end());Round z;z.term=f.first;
    while(at<path.size()){
      auto vs=vertices(Term{path[at]},n);bool touches=false;for(int v:vs)touches|=K.count(v)>0;if(!touches)break;z.path.push_back(path[at++]);
    }
    need(!z.path.empty(),"empty round");auto pv=vertices(z.path,n);std::set<int> touched(pv.begin(),pv.end());
    for(auto e:f.second)if(touched.count(e.first)||touched.count(n+1+e.second))z.sigma.push_back(e);
    need(!z.sigma.empty(),"no charged term edge");for(auto e:F[z.term])z.beta.push_back(std::find(z.sigma.begin(),z.sigma.end(),e)!=z.sigma.end());
    for(int v:vertices(z.sigma,n))z.mask.push_back(touched.count(v));
    for(auto e:z.path)cur.act(e);
    rounds.push_back(z);
  }
  Code c;State augmented=mu;int j=0;for(auto&z:rounds)for(auto e:z.sigma){augmented.act(e);++j;}
  c.augmented=augmented.edges;std::sort(c.augmented.begin(),c.augmented.end());
  std::set<int> kp,kh;for(int p=0;p<=n;++p)if(augmented.row(p)<0)kp.insert(p);for(int h=0;h<n;++h)if(augmented.hole(h)<0)kh.insert(h);
  for(auto&z:rounds){for(auto e:z.sigma){kp.insert(e.first);kh.insert(e.second);}std::vector<int>ps(kp.begin(),kp.end()),hs(kh.begin(),kh.end());auto vs=vertices(z.sigma,n);std::set<int>covered;c.beta.push_back(z.beta);c.mask.push_back(z.mask);
    for(auto e:z.path){int v=-1;for(size_t i=0;i<vs.size();++i)if(z.mask[i]&&!covered.count(vs[i])){v=vs[i];break;}need(v>=0,"missing touched query");
      auto ev=vertices(Term{e},n);need(std::find(ev.begin(),ev.end(),v)!=ev.end(),"query order mismatch");
      if(e.first<0){need(v==n+1+e.second,"empty answer at non-hole");c.answers.push_back(n+1);}else if(v<=n){auto it=std::find(hs.begin(),hs.end(),e.second);need(it!=hs.end(),"unknown hole partner");c.answers.push_back(int(it-hs.begin()));}else{auto it=std::find(ps.begin(),ps.end(),e.first);need(it!=ps.end(),"unknown pigeon partner");c.answers.push_back(int(it-ps.begin()));}
      covered.insert(ev.begin(),ev.end());
    }
  }return {c,j};
}
static Term decode(const Formula&F,const Code&c,int n,int s){
  State cur{n,c.augmented,{}};std::set<int>kp,kh;for(int p=0;p<=n;++p)if(cur.row(p)<0)kp.insert(p);for(int h=0;h<n;++h)if(cur.hole(h)<0)kh.insert(h);Term path;size_t d=0;
  need(c.beta.size()==c.mask.size(),"code shape");
  for(size_t ri=0;ri<c.beta.size();++ri){auto f=first(F,cur);need(f.first>=0,"decoder missing term");const Term&t=F[f.first];need(t.size()==c.beta[ri].size(),"beta shape");Term sigma;
    for(size_t i=0;i<t.size();++i)if(c.beta[ri][i]){sigma.push_back(t[i]);kp.insert(t[i].first);kh.insert(t[i].second);}
    need(!sigma.empty(),"decoder empty charge");auto vs=vertices(sigma,n);need(vs.size()==c.mask[ri].size(),"mask shape");std::vector<int>ps(kp.begin(),kp.end()),hs(kh.begin(),kh.end());std::set<int>covered;Term part;
    while(int(path.size()+part.size())<s){int v=-1;for(size_t i=0;i<vs.size();++i)if(c.mask[ri][i]&&!covered.count(vs[i])){v=vs[i];break;}if(v<0)break;need(d<c.answers.size(),"missing answer");int a=c.answers[d++];Edge e;
      if(a==n+1){need(v>n,"empty answer on pigeon");e={-1,v-n-1};}else if(v<=n){need(a>=0&&a<int(hs.size()),"hole answer index");e={v,hs[a]};}else{need(a>=0&&a<int(ps.size()),"pigeon answer index");e={ps[a],v-n-1};}
      part.push_back(e);auto ev=vertices(Term{e},n);covered.insert(ev.begin(),ev.end());
    }
    for(auto e:sigma){auto it=std::find(cur.edges.begin(),cur.edges.end(),e);need(it!=cur.edges.end(),"charged edge not present");cur.edges.erase(it);}for(auto e:part){cur.act(e);path.push_back(e);}
  }
  need(int(path.size())==s&&d==c.answers.size(),"path length mismatch");
  for(auto e:path)if(e.first<0){need(cur.empty.erase(e.second)==1,"empty recovery");}else{auto it=std::find(cur.edges.begin(),cur.edges.end(),e);need(it!=cur.edges.end(),"edge recovery");cur.edges.erase(it);}
  need(cur.empty.empty(),"unremoved empty marks");std::sort(cur.edges.begin(),cur.edges.end());return cur.edges;
}
static uint64_t nodes=0;
static void paths(const Formula&F,const State&mu,int cap,const std::function<void(const Term&)>&emit){
  std::function<void(State,Term)> rec;std::function<void(State,Term,std::vector<int>,size_t)> complete;
  auto visit=[&](){need(++nodes<=5000000,"five-million-node cap exceeded");};
  rec=[&](State state,Term path){visit();if(int(path.size())==cap){emit(path);return;}auto f=first(F,state);if(f.first<0||f.second.empty())return;complete(state,path,vertices(f.second,state.n),0);};
  complete=[&](State state,Term path,std::vector<int>K,size_t pos){visit();if(int(path.size())==cap){emit(path);return;}while(pos<K.size()&&state.decided(K[pos]))++pos;if(pos==K.size()){rec(state,path);return;}int v=K[pos],n=state.n;std::vector<Edge>answers;
    if(v<=n){for(int h=0;h<n;++h)if(state.hole(h)<0&&!state.empty.count(h))answers.push_back({v,h});}
    else{int h=v-n-1;answers.push_back({-1,h});for(int p=0;p<=n;++p)if(state.row(p)<0)answers.push_back({p,h});}
    for(auto e:answers){State next=state;next.act(e);Term pp=path;pp.push_back(e);complete(next,pp,K,pos+1);}
  };rec(mu,{});
}
static void all_mu(int n,int k,const std::function<void(const State&)>&emit){std::function<void(State,int,int)>rec;rec=[&](State st,int p,int left){if(!left){emit(st);return;}if(n+1-p<left)return;for(int row=p;row<=n;++row)for(int h=0;h<n;++h)if(st.hole(h)<0){State z=st;z.act({row,h});rec(z,row+1,left-1);}};rec(State{n,{},{}},0,k);}
static void write_term(std::ostream&o,const Term&t){o<<'[';for(size_t i=0;i<t.size();++i){if(i)o<<',';o<<'['<<t[i].first<<','<<t[i].second<<']';}o<<']';}
static void write_code(std::ostream&o,const Code&c){o<<"{\"augmented\":";write_term(o,c.augmented);for(auto z:{std::pair<const char*,std::vector<std::vector<int>>>{"beta",c.beta},{"masks",c.mask}}){o<<",\""<<z.first<<"\":[";for(size_t i=0;i<z.second.size();++i){if(i)o<<',';o<<'[';for(size_t j=0;j<z.second[i].size();++j){if(j)o<<',';o<<z.second[i][j];}o<<']';}o<<']';}o<<",\"answers\":[";for(size_t i=0;i<c.answers.size();++i){if(i)o<<',';o<<c.answers[i];}o<<"]}";}
int main(int argc,char**argv){try{
  need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");need(!std::filesystem::exists(argv[2]),"refusing overwrite");std::ofstream out(argv[2]);need(bool(out),"output open");std::mt19937 rng(20260921);uint64_t total_paths=0,total_empty=0,total_multi=0;bool corrupted_rejected=false;
  std::cout<<"Fixed suite: n=4,N=2,s=2 (120 restrictions/case), n=5,N=3,s=3 (300/case); 12 cases/board. At most 5,000,000 search nodes.\n";
  for(int n:{4,5}){int N=n-2,s=N;for(int c=0;c<12;++c){Formula F;
    if(c==0){for(int p=0;p<=n;++p)F.push_back({{p,n-1}});for(int i=0;i<n-1;++i)F.push_back({{i,i}});}
    else if(c==1){for(int i=0;i<n;++i)F.push_back({{i,i}});}
    else{for(int z=0;z<6;++z){int size=1+int(rng()%2);Term t;std::set<int>ps,hs;while(int(t.size())<size){int p=int(rng()%(n+1)),h=int(rng()%n);if(ps.count(p)||hs.count(h))continue;ps.insert(p);hs.insert(h);t.push_back({p,h});}std::sort(t.begin(),t.end());F.push_back(t);}}
    uint64_t count=0,bad=0,prefixes=0,empty_paths=0,multi=0;std::map<std::string,std::string> seen;std::map<int,uint64_t> histogram;Code example;Term example_mu,example_path;bool have=false;
    all_mu(n,n-N,[&](const State&mu){++count;bool isbad=false;paths(F,mu,s,[&](const Term&path){isbad=true;++prefixes;auto enc=encode(F,mu,path);need(enc.second>=(s+1)/2&&enc.second<=std::min(2*s,N),"charge range");++histogram[enc.second];need(key(decode(F,enc.first,n,s))==key(mu.edges),"round trip failed");std::string ck=key(enc.first),mk=key(mu.edges);auto it=seen.emplace(ck,mk);need(it.second||it.first->second==mk,"cross-restriction code collision");bool empty=std::any_of(path.begin(),path.end(),[](Edge e){return e.first<0;});empty_paths+=empty;multi+=enc.first.beta.size()>1;
      if(empty&&!have){example=enc.first;example_mu=mu.edges;example_path=path;have=true;}
      if(empty&&!corrupted_rejected){Code corrupt=enc.first;auto q=std::find(corrupt.answers.begin(),corrupt.answers.end(),n+1);*q=0;try{corrupted_rejected=key(decode(F,corrupt,n,s))!=mk;}catch(const std::exception&){corrupted_rejected=true;}}
    });bad+=isbad;});
    need(count==uint64_t(n==4?120:300),"restriction count");out<<"{\"case\":"<<c<<",\"n\":"<<n<<",\"N\":"<<N<<",\"s\":"<<s<<",\"seed\":20260921,\"terms\":[";for(size_t i=0;i<F.size();++i){if(i)out<<',';write_term(out,F[i]);}out<<"],\"restrictions\":"<<count<<",\"bad_restrictions\":"<<bad<<",\"all_bad_prefixes_checked\":"<<prefixes<<",\"prefixes_with_empty\":"<<empty_paths<<",\"multiple_round_prefixes\":"<<multi<<",\"round_trip_failures\":0,\"code_collisions_across_restrictions\":0,\"sigma_size_histogram\":{";bool comma=false;for(auto kv:histogram){if(comma)out<<',';comma=true;out<<'"'<<kv.first<<"\":"<<kv.second;}out<<'}';if(have){out<<",\"empty_example\":{\"mu\":";write_term(out,example_mu);out<<",\"path\":";write_term(out,example_path);out<<",\"code\":";write_code(out,example);out<<'}';}out<<"}\n";out.flush();total_paths+=prefixes;total_empty+=empty_paths;total_multi+=multi;
  }}
  need(total_empty>0&&total_multi>0&&corrupted_rejected,"nonvacuous empty/multi-round/corruption controls");out<<"{\"summary\":true,\"checked_prefixes\":"<<total_paths<<",\"with_empty\":"<<total_empty<<",\"multiple_rounds\":"<<total_multi<<",\"nodes\":"<<nodes<<",\"corrupted_empty_answer_rejected\":true}\n";std::cout<<"prefixes="<<total_paths<<" empty="<<total_empty<<" multiple-round="<<total_multi<<" nodes="<<nodes<<"; all checks passed\n";need(bool(out),"output failure");return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
