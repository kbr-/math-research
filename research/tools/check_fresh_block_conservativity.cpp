// Exact F2 test of same-degree conservativity when fresh complete accuracy-one ENS blocks are added.
// Two interfaces are compared at ordinary NS degree D:
//   full:     every polynomial in the existing variables (raw retained coefficients included);
//   products: old monomials times genuine retained whole products, by weighted degree.
// Boolean/field equations of every variable are applied by multilinear reduction, legal at no
// degree cost.  A companion g_i*P keeps its original degree deg(g_i)+1+max_j deg(g_j).
// For each new full-interface consequence the program checks that it vanishes on every model of
// the base source and finds the least degree at which it enters the base NS space.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
typedef uint64_t Mask;
typedef std::set<Mask> Poly;
typedef std::vector<uint64_t> Row;
static void toggle(Poly& p, Mask m){ auto it=p.find(m); if(it==p.end()) p.insert(m); else p.erase(it); }
static Poly mul(const Poly& a,const Poly& b){ Poly c; for(Mask x:a) for(Mask y:b) toggle(c,x|y); return c; }
static Poly add(const Poly& a,const Poly& b){ Poly c=a; for(Mask y:b) toggle(c,y); return c; }
static int deg(const Poly& p){ int d=0; for(Mask m:p) d=std::max(d,__builtin_popcountll(m)); return d; }
static Poly var(int v){ return Poly{Mask(1)<<v}; }
static Poly one(){ return Poly{0}; }
static bool eval(const Poly& p,Mask point){ bool v=false; for(Mask m:p) if((m&point)==m) v=!v; return v; }
struct Generator{ Poly poly; int original_degree; bool fresh; };
struct Product{ Poly poly; int weight; };
struct Source{
  int nvars=0; Mask fresh=0, old=0; std::vector<Generator> gens; std::vector<Product> products; std::vector<std::string> notes;
  Poly old_var(){ old|=Mask(1)<<nvars; return var(nvars++); }
  Poly block(const std::vector<Poly>& g,bool is_fresh,const std::string& name){
    Poly P=one(); int dmax=0; for(auto& gi:g) dmax=std::max(dmax,deg(gi));
    for(auto& gi:g){ if(is_fresh) fresh|=Mask(1)<<nvars; P=add(P,mul(var(nvars++),gi)); }
    for(auto& gi:g) gens.push_back({mul(gi,P),deg(gi)+1+dmax,is_fresh});
    if(!is_fresh) products.push_back({P,1+dmax});
    notes.push_back(name+(is_fresh?" (fresh)":" (base)")+" inputs="+std::to_string(g.size())+" input-degree="+std::to_string(dmax));
    return P; }
};
struct Space{                       // echelon basis of an ordinary NS space through degree D
  std::vector<Mask> cols; std::map<Mask,long> index; long first_existing=0, W=0, multiples=0; std::map<long,Row> pivots;
  static long lead(const Row& r){ for(size_t w=0;w<r.size();++w) if(r[w]) return long(w)*64+__builtin_ctzll(r[w]); return -1; }
  Row vec(const Poly& p) const { Row r(W,0); for(Mask t:p){ long j=index.at(t); r[j>>6]^=uint64_t(1)<<(j&63);} return r; }
  Row reduce(Row r) const { for(;;){ long l=lead(r); if(l<0) return r; auto it=pivots.find(l); if(it==pivots.end()) return r; for(long w=0;w<W;++w) r[w]^=it->second[w]; } }
  void insert(Row r){ r=reduce(std::move(r)); long l=lead(r); if(l>=0) pivots.emplace(l,std::move(r)); }
  Space(const Source& s,int D,bool with_fresh){
    Mask allowed=with_fresh? ~Mask(0) : ~s.fresh; std::vector<Mask> layer{0}; cols.push_back(0);
    for(int d=1;d<=D;++d){ std::vector<Mask> next; for(Mask m:layer){ int hi=m?64-__builtin_clzll(m):0; for(int v=hi;v<s.nvars;++v) if(allowed>>v&1) next.push_back(m|Mask(1)<<v);} cols.insert(cols.end(),next.begin(),next.end()); layer.swap(next); }
    std::stable_sort(cols.begin(),cols.end(),[&](Mask a,Mask b){ return bool(a&s.fresh)>bool(b&s.fresh); });   // fresh columns first
    for(long i=0;i<(long)cols.size();++i) index[cols[i]]=i;
    while(first_existing<(long)cols.size() && (cols[first_existing]&s.fresh)) ++first_existing;
    W=(cols.size()+63)/64;
    for(auto& g:s.gens){ if(g.fresh&&!with_fresh) continue; int room=D-g.original_degree; if(room<0) continue;
      for(Mask m:cols){ if(__builtin_popcountll(m)>room) continue; ++multiples; insert(vec(mul(Poly{m},g.poly))); } } }
  long existing_rank() const { long n=0; for(auto& kv:pivots) if(kv.first>=first_existing) ++n; return n; }
  Poly poly(const Row& r) const { Poly p; for(long j=0;j<(long)cols.size();++j) if(r[j>>6]>>(j&63)&1) p.insert(cols[j]); return p; }
  // rank of the given polynomials modulo this space: insert jointly with the ideal pivots, then restore
  long quotient_rank(const std::vector<Poly>& polys){ std::vector<long> added; for(auto& p:polys){ Row r=reduce(vec(p)); long l=lead(r); if(l>=0){ pivots.emplace(l,std::move(r)); added.push_back(l);} }
    for(long l:added) pivots.erase(l); return added.size(); }
};
typedef std::vector<std::pair<std::string,Poly>> Queries;
// Explicit NS witness of `target` in the extended source through degree D: cofactor of every generator.
static void witness_case(std::ostream& o,const std::string& name,const Source& s,int D,const Poly& target){
  Space sp(s,0,true); sp=Space(s,D,true); // column index only; rebuild rows with combination tracking
  std::vector<std::pair<int,Mask>> rows; for(size_t g=0;g<s.gens.size();++g){ int room=D-s.gens[g].original_degree; if(room<0) continue; for(Mask m:sp.cols) if(__builtin_popcountll(m)<=room) rows.push_back({int(g),m}); }
  size_t CW=(rows.size()+63)/64; std::map<long,std::pair<Row,Row>> piv;
  auto reduce=[&](Row& r,Row& c){ for(;;){ long l=Space::lead(r); if(l<0) return; auto it=piv.find(l); if(it==piv.end()) return; for(long w=0;w<sp.W;++w) r[w]^=it->second.first[w]; for(size_t w=0;w<CW;++w) c[w]^=it->second.second[w]; } };
  for(size_t i=0;i<rows.size();++i){ Row r=sp.vec(mul(Poly{rows[i].second},s.gens[rows[i].first].poly)), c(CW,0); c[i>>6]|=uint64_t(1)<<(i&63); reduce(r,c); long l=Space::lead(r); if(l>=0) piv.emplace(l,std::make_pair(std::move(r),std::move(c))); }
  Row r=sp.vec(target), c(CW,0); reduce(r,c); bool member=Space::lead(r)<0;
  std::vector<Poly> cof(s.gens.size()); if(member) for(size_t i=0;i<rows.size();++i) if(c[i>>6]>>(i&63)&1) toggle(cof[rows[i].first],rows[i].second);
  Poly check; if(member) for(size_t g=0;g<s.gens.size();++g) check=add(check,mul(cof[g],s.gens[g].poly));
  bool verified=member&&check==target;
  o<<"{\"witness_case\":\""<<name<<"\",\"degree\":"<<D<<",\"member\":"<<(member?"true":"false")<<",\"identity_verified\":"<<(verified?"true":"false")<<",\"cofactors\":[";
  for(size_t g=0;g<s.gens.size();++g){ o<<(g?",":"")<<"{\"generator\":"<<g<<",\"fresh\":"<<(s.gens[g].fresh?"true":"false")<<",\"original_degree\":"<<s.gens[g].original_degree<<",\"cofactor\":[";
    bool f=true; for(Mask m:cof[g]){ o<<(f?"":",")<<"["; f=false; bool h=true; for(int v=0;v<64;++v) if(m>>v&1){ o<<(h?"":",")<<v; h=false;} o<<"]"; } o<<"]}"; }
  o<<"]}\n"; o.flush(); std::cout<<name<<" D="<<D<<" member="<<member<<" identity_verified="<<verified<<std::endl; }
static void run_case(std::ostream& o,const std::string& name,const Source& s,int D,bool& all_ok,const Queries& queries=Queries()){
  Space ext(s,D,true), base(s,D,false);
  long inter=ext.existing_rank(), brank=base.pivots.size();
  // whole-product interface
  std::vector<Poly> iface; std::vector<std::pair<unsigned,unsigned>> label; std::vector<int> olds; for(int v=0;v<s.nvars;++v) if(s.old>>v&1) olds.push_back(v);
  for(unsigned U=0;U<(1u<<s.products.size());++U){ int w=0; Poly Z=one(); for(size_t a=0;a<s.products.size();++a) if(U>>a&1){ w+=s.products[a].weight; Z=mul(Z,s.products[a].poly);} if(w>D) continue;
    for(unsigned S=0;S<(1u<<olds.size());++S){ if(__builtin_popcount(S)+w>D) continue; Mask m=0; for(size_t i=0;i<olds.size();++i) if(S>>i&1) m|=Mask(1)<<olds[i]; iface.push_back(mul(Poly{m},Z)); label.push_back({S,U}); } }
  long qb=base.quotient_rank(iface), qe=ext.quotient_rank(iface);
  // explicit interface relations gained by the extension: combinations in I_D(extended) but not I_D(base)
  std::vector<std::vector<long>> lost; if(qb!=qe){ std::map<long,std::pair<Row,std::vector<uint64_t>>> piv; size_t CW=(iface.size()+63)/64; Space acc(base);
    for(size_t i=0;i<iface.size();++i){ Row r=ext.reduce(ext.vec(iface[i])); std::vector<uint64_t> c(CW,0); c[i>>6]|=uint64_t(1)<<(i&63);
      for(;;){ long l=Space::lead(r); if(l<0){ Poly sum; for(size_t k=0;k<iface.size();++k) if(c[k>>6]>>(k&63)&1) sum=add(sum,iface[k]);
            Row b=acc.reduce(acc.vec(sum)); if(Space::lead(b)>=0){ acc.insert(b); std::vector<long> rel; for(size_t k=0;k<iface.size();++k) if(c[k>>6]>>(k&63)&1) rel.push_back(k); lost.push_back(rel);} break; }
        r=ext.reduce(std::move(r)); l=Space::lead(r); if(l<0) continue; auto it=piv.find(l); if(it==piv.end()){ piv.emplace(l,std::make_pair(r,c)); break; }
        for(long w=0;w<ext.W;++w) r[w]^=it->second.first[w]; for(size_t w=0;w<CW;++w) c[w]^=it->second.second[w]; } } }
  // new full-interface consequences
  std::vector<Poly> news; { Space acc(base); for(auto& kv:ext.pivots) if(kv.first>=ext.first_existing){ Poly p=ext.poly(kv.second); Row r=acc.reduce(acc.vec(p)); if(Space::lead(r)>=0){ news.push_back(acc.poly(r)); acc.insert(r);} } }
  std::map<int,Space> cache; std::map<int,long> loss_histogram;
  o<<"{\"case\":\""<<name<<"\",\"degree\":"<<D<<",\"variables\":"<<s.nvars<<",\"blocks\":[";
  for(size_t i=0;i<s.notes.size();++i) o<<(i?",":"")<<"\""<<s.notes[i]<<"\"";
  o<<"],\"extended\":{\"columns\":"<<ext.cols.size()<<",\"generator_multiples\":"<<ext.multiples<<",\"rank\":"<<ext.pivots.size()<<",\"existing_variable_intersection_rank\":"<<inter<<"}"
   <<",\"base\":{\"columns\":"<<base.cols.size()<<",\"generator_multiples\":"<<base.multiples<<",\"rank\":"<<brank<<"}"
   <<",\"full_interface_conservative\":"<<(inter==brank?"true":"false")
   <<",\"product_interface\":{\"expressions\":"<<iface.size()<<",\"base_quotient_rank\":"<<qb<<",\"extended_quotient_rank\":"<<qe<<",\"preserved\":"<<(qb==qe?"true":"false")<<"}"
   <<",\"gained_interface_relations\":[";
  for(size_t i=0;i<lost.size();++i){ o<<(i?",":"")<<"["; for(size_t k=0;k<lost[i].size();++k){ auto lb=label[lost[i][k]]; o<<(k?",":"")<<"{\"old_mask\":"<<lb.first<<",\"product_mask\":"<<lb.second<<"}"; } o<<"]"; }
  o<<"],\"new_consequences\":[";
  for(size_t i=0;i<news.size();++i){ const Poly& t=news[i];
    bool vanishes=true; Mask basevars=0; for(int v=0;v<s.nvars;++v) if(!(s.fresh>>v&1)) basevars|=Mask(1)<<v; long models=0;
    for(Mask pt=0;pt<=basevars;++pt){ if(pt&~basevars) continue; bool model=true; for(auto& g:s.gens) if(!g.fresh&&eval(g.poly,pt)){ model=false; break; } if(model){ ++models; if(eval(t,pt)) vanishes=false; } }
    int enters=-1; for(int E=D+1;E<=s.nvars;++E){ auto it=cache.find(E); if(it==cache.end()) it=cache.emplace(E,Space(s,E,false)).first; const Space& b=it->second; if(Space::lead(b.reduce(b.vec(t)))<0){ enters=E; break; } }
    loss_histogram[enters-D]++;
    o<<(i?",":"")<<"{\"terms\":"<<t.size()<<",\"degree\":"<<deg(t)<<",\"base_models\":"<<models<<",\"vanishes_on_base_models\":"<<(vanishes?"true":"false")<<",\"least_base_NS_degree\":"<<enters<<",\"monomials\":[";
    bool f=true; for(Mask m:t){ o<<(f?"":",")<<"["; f=false; bool g=true; for(int v=0;v<64;++v) if(m>>v&1){ o<<(g?"":",")<<v; g=false;} o<<"]"; } o<<"]}"; }
  o<<"],\"loss_histogram\":{"; { bool f=true; for(auto& kv:loss_histogram){ o<<(f?"":",")<<"\""<<kv.first<<"\":"<<kv.second; f=false; } }
  o<<"},\"queries\":[";
  for(size_t i=0;i<queries.size();++i){ const Poly& q=queries[i].second; bool in_ext=Space::lead(ext.reduce(ext.vec(q)))<0, in_base=Space::lead(base.reduce(base.vec(q)))<0;
    o<<(i?",":"")<<"{\"name\":\""<<queries[i].first<<"\",\"in_extended\":"<<(in_ext?"true":"false")<<",\"in_base\":"<<(in_base?"true":"false")<<"}";
    std::cout<<"   query "<<queries[i].first<<": extended="<<in_ext<<" base="<<in_base<<std::endl; }
  o<<"]}\n"; o.flush();
  for(auto& kv:loss_histogram) std::cout<<"   loss "<<kv.first<<": "<<kv.second<<" consequences"<<std::endl;
  std::cout<<name<<" D="<<D<<" full: inter="<<inter<<" base="<<brank<<(inter==brank?" conservative":" NEW") <<" | products: "<<qb<<" -> "<<qe<<(qb==qe?" preserved":" LOST")<<std::endl;
  if(inter!=brank||qb!=qe) all_ok=false; }
int main(int argc,char** argv){
  if((argc!=3&&argc!=5)||std::string(argv[1])!="--out"||(argc==5&&std::string(argv[3])!="--suite")){ std::cerr<<"usage: --out PATH [--suite cycle167|cycle168]\n"; return 2; }
  std::string suite=argc==5?argv[4]:"cycle167";
  { std::ifstream t(argv[2]); if(t.good()){ std::cerr<<"refusing to overwrite\n"; return 2; } }
  std::ofstream out(argv[2]); bool ok=true;
  auto olds=[&](Source& s,int n){ std::vector<Poly> x; for(int i=0;i<n;++i) x.push_back(s.old_var()); return x; };
  auto G0=[&](std::vector<Poly>& v){ return std::vector<Poly>{add(v[0],v[3]),add(v[1],v[4]),add(v[2],v[5])}; };
  if(suite=="cycle168"){
    // second-level base on n+n old variables, with `helpers` fresh rank-n helpers (x_i+y_i+offset bits)
    auto second_level=[&](int n,int helpers,int depth,std::vector<int> Ds,const std::string& name){
      Source s; auto v=olds(s,2*n); std::vector<Poly> xs(v.begin(),v.begin()+n), ys(v.begin()+n,v.end());
      Poly A=s.block(xs,false,"A"), B=s.block(ys,false,"B"); Poly E=s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)");
      if(depth>=3) s.block({add(E,one()),v[0]},false,"F(1+E,x1)");
      for(int h=0;h<helpers;++h){ std::vector<Poly> g; for(int i=0;i<n;++i){ Poly gi=add(xs[i],ys[i]); if(h>>i&1) gi=add(gi,one()); g.push_back(gi);} s.block(g,true,"G"+std::to_string(h)); }
      for(int D:Ds) run_case(out,name,s,D,ok); };
    second_level(2,1,2,{5,6,7,8,9},"n2-one-helper");
    second_level(2,2,2,{5,6,7,8,9},"n2-two-helpers");
    second_level(2,3,2,{5,6,7,8},"n2-three-helpers");
    second_level(2,1,3,{7,8,9,10,11},"n2-third-level-base-one-helper");
    second_level(2,2,3,{7,8,9,10},"n2-third-level-base-two-helpers");
    { // which parts of the degree-seven relation are new?  n=3, one helper
      Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"), B=s.block({v[3],v[4],v[5]},false,"B"); Poly E=s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)");
      auto g=G0(v); s.block(g,true,"G0"); Poly x123=mul(mul(v[0],v[1]),v[2]), y123=mul(mul(v[3],v[4]),v[5]), g123=mul(mul(g[0],g[1]),g[2]);
      Queries q{{"E*x1x2x3",mul(E,x123)},{"E*y1y2y3",mul(E,y123)},{"E*g1g2g3",mul(E,g123)},{"E*(x1x2x3+y1y2y3)",mul(E,add(x123,y123))},{"E*(g1g2g3+x1x2x3+y1y2y3)",mul(E,add(g123,add(x123,y123)))},
                {"E*x1x2",mul(E,mul(v[0],v[1]))},{"E*g1g2",mul(E,mul(g[0],g[1]))},{"E*x1y2",mul(E,mul(v[0],v[4]))},{"E*x1",mul(E,v[0])},{"A*B*g1",mul(mul(A,B),g[0])},{"E+A*B",add(E,mul(A,B))}};
      for(int D:{6,7}) run_case(out,"n3-one-helper-queries",s,D,ok,q); }
    std::cout<<(ok?"ALL PRESERVED":"SOME INTERFACE NOT PRESERVED")<<std::endl; return 0; }
  if(suite=="cycle168-rank4"){
    Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"), B=s.block({v[3],v[4],v[5]},false,"B"); s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)");
    auto g=G0(v); g.push_back(add(v[0],v[4])); s.block(g,true,"G0+(x1+y2)"); for(int D:{6,7}) run_case(out,"n3-rank4-helper",s,D,ok);
    std::cout<<(ok?"ALL PRESERVED":"SOME INTERFACE NOT PRESERVED")<<std::endl; return 0; }
  if(suite=="cycle168-witness"){
    Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"), B=s.block({v[3],v[4],v[5]},false,"B"); Poly E=s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)");
    auto g=G0(v); s.block(g,true,"G0"); Poly x123=mul(mul(v[0],v[1]),v[2]), y123=mul(mul(v[3],v[4]),v[5]), g123=mul(mul(g[0],g[1]),g[2]);
    witness_case(out,"n3-degree-seven-relation",s,7,mul(E,add(g123,add(x123,y123)))); return 0; }
  { Source s; auto v=olds(s,6); s.block({v[0],v[1],v[2]},false,"A"); s.block({v[3],v[4],v[5]},false,"B"); s.block(v,false,"C"); s.block(G0(v),true,"G0");
    for(int D:{4,5,6}) run_case(out,"retained-ABC-plus-G0",s,D,ok); }
  { Source s; auto v=olds(s,5); s.block({v[0],v[1],v[2],v[3]},false,"A"); s.block({v[0],v[1],v[2],v[3]},true,"A-copy"); for(int D:{4,5,6}) run_case(out,"shared-rank4-copy",s,D,ok); }
  { Source s; auto v=olds(s,5); s.block({v[0],v[1],v[2],v[3]},false,"A"); s.block({add(v[0],v[4]),add(v[1],v[4]),add(v[2],v[4]),v[3]},true,"mixed"); for(int D:{4,5,6}) run_case(out,"rank4-mixed-helper",s,D,ok); }
  { Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"); Poly B=s.block({v[3],v[4],v[5]},false,"B");
    s.block({add(A,one()),add(B,one()),add(v[0],v[3])},true,"level2(1+A,1+B,x1+y1)"); for(int D:{5,6,7}) run_case(out,"level-two-fresh",s,D,ok); }
  { Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"); Poly B=s.block({v[3],v[4],v[5]},false,"B");
    s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)"); s.block(G0(v),true,"G0"); for(int D:{5,6,7,8}) run_case(out,"level-two-base-plus-G0",s,D,ok); }
  { Source s; auto v=olds(s,6); Poly A=s.block({v[0],v[1],v[2]},false,"A"); Poly B=s.block({v[3],v[4],v[5]},false,"B");
    s.block({add(A,one()),add(B,one())},false,"E(1+A,1+B)"); s.block({v[0],v[1],v[2]},true,"A-copy"); for(int D:{6,7}) run_case(out,"level-two-base-plus-A-copy",s,D,ok); }
  { Source s; auto v=olds(s,6); s.block({v[0],v[1],v[2]},false,"A"); s.block({v[3],v[4],v[5]},false,"B"); s.block(v,false,"C"); s.block(G0(v),true,"G0");
    s.block({add(add(v[0],v[3]),one()),add(v[1],v[4]),add(v[2],v[5])},true,"G1"); run_case(out,"retained-ABC-plus-G0-G1",s,5,ok); }
  std::cout<<(ok?"ALL PRESERVED":"SOME INTERFACE NOT PRESERVED")<<std::endl; return 0; }
