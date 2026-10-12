// Check the categorical switching encoding, not a hard-system lower bound.
// A canonical term-query path of length s is encoded by a restriction with s
// fewer stars, term-position masks, and its actual q-ary path values.
// Refuted by: a failed round trip, a full-code collision, or a violated exact tail bound.
// Possible because: masks and path values must reconstruct term choices; incorrect choices collide.
// Expected: every full encoding decodes; omitted masks and omitted path values
// each have actual collisions; dropping the switching tail fails a survival bound.
// Full finite series: q=2,n=2 all DNFs; q=3,n=2 all DNFs;
// q=3,n=3 all DNFs with at most three terms, width at most two.
// No dense algebra kernel is needed: finite trees, bitsets and exact integer weights.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <vector>
using U=std::uint64_t;
using I=__int128_t;
U pw(U a,int b){U r=1;while(b--)r*=a;return r;}
struct Term{std::vector<int> vars,vals;U truth=0;};
struct Enc{int rp;std::vector<int> masks,values;};
struct Model{
 int q,n,b,ns,na;std::vector<Term> terms;std::vector<std::array<int,3>> states;
 std::vector<U> compatible,weights;std::vector<int> cache;U family=0,truth=0;
 U checks=0,roundtrips=0,failures=0,families=0,tailchecks=0,survivalchecks=0;
 bool noMask=false,noValues=false,noTail=false;
 std::string noMaskWitness,noValuesWitness;
 Model(int qq,int nn,int bb):q(qq),n(nn),b(bb),ns(pw(q+1,n)),na(pw(q,n)){
  for(int code=0;code<ns;code++){
   auto a=decode(code);states.push_back(a);U mask=0;int stars=0;
   for(int j=0;j<n;j++)stars+=a[j]==q;
   for(int x=0;x<na;x++){int y=x;bool ok=true;for(int j=0;j<n;j++){int z=y%q;y/=q;if(a[j]!=q&&a[j]!=z)ok=false;}if(ok)mask|=U(1)<<x;}
   compatible.push_back(mask);weights.push_back(pw(q,stars)*pw(127,n-stars));
  }
  // Original categorical terms are positive equalities; digit q means absent.
  for(int code=0;code<ns;code++){
   auto a=decode(code);Term t;for(int j=0;j<n;j++)if(a[j]!=q){t.vars.push_back(j);t.vals.push_back(a[j]);}
   if(int(t.vars.size())<=b){t.truth=compatible[code];terms.push_back(t);}
  }
 }
 std::array<int,3> decode(int code)const{std::array<int,3>a{};for(int j=0;j<n;j++){a[j]=code%(q+1);code/=q+1;}return a;}
 int code(const std::array<int,3>&a)const{int r=0;for(int j=n-1;j>=0;j--)r=r*(q+1)+a[j];return r;}
 void check(bool ok,const char*what){checks++;if(!ok){if(failures<6)std::cout<<"FAIL "<<what<<" family="<<family<<"\n";failures++;}}
 int first(int rho)const{
  for(int i=0;i<int(terms.size());i++)if((family>>i)&1){bool ok=true;auto&t=terms[i];
   for(int j=0;j<int(t.vars.size());j++){int x=states[rho][t.vars[j]];if(x!=q&&x!=t.vals[j]){ok=false;break;}}
   if(ok)return i;
  }return -1;
 }
 std::vector<int> freevars(int rho,int i)const{std::vector<int>v;for(int x:terms[i].vars)if(states[rho][x]==q)v.push_back(x);return v;}
 int assign(int rho,const std::vector<int>&v,int val)const{
  auto a=states[rho];for(int j=int(v.size())-1;j>=0;j--){a[v[j]]=val%q;val/=q;}return code(a);
 }
 int depth(int rho){
  if(cache[rho]>=0)return cache[rho];
  int i=first(rho);if(i<0){check((truth&compatible[rho])==0,"false leaf semantics");return cache[rho]=0;}
  auto v=freevars(rho,i);if(v.empty()){check((truth&compatible[rho])==compatible[rho],"true leaf semantics");return cache[rho]=0;}
  int d=0;for(int val=0;val<int(pw(q,v.size()));val++)d=std::max(d,depth(assign(rho,v,val)));
  return cache[rho]=int(v.size())+d;
 }
 std::vector<std::pair<int,int>> path(int rho,int s){
  if(s==0)return {};
  int i=first(rho);auto v=freevars(rho,i);std::vector<std::pair<int,int>> out;
  if(s<=int(v.size())){for(int j=0;j<s;j++)out.push_back({v[j],0});return out;}
  for(int val=0;val<int(pw(q,v.size()));val++){
   int next=assign(rho,v,val);if(depth(next)<s-int(v.size()))continue;
   for(int x:v)out.push_back({x,states[next][x]});
   auto tail=path(next,s-v.size());out.insert(out.end(),tail.begin(),tail.end());return out;
  }
  check(false,"long path exists");return out;
 }
 Enc encode(int rho,int s){
  auto pth=path(rho,s);check(int(pth.size())==s,"path length");Enc e{rho,{},{}};auto forced=states[rho];int current=rho,pos=0;
  while(pos<s){int i=first(current);auto&t=terms[i];auto fv=freevars(current,i);int use=std::min(int(fv.size()),s-pos),mask=0;auto actual=states[current];
   for(int j=0;j<use;j++){int x=fv[j],slot=std::find(t.vars.begin(),t.vars.end(),x)-t.vars.begin();
    check(pth[pos+j].first==x,"path variable order");mask|=1<<slot;forced[x]=t.vals[slot];actual[x]=pth[pos+j].second;e.values.push_back(actual[x]);}
   check(mask!=0,"nonempty mask");e.masks.push_back(mask);current=code(actual);pos+=use;
  }e.rp=code(forced);return e;
 }
 int recover(const Enc&e){auto a=states[e.rp];int pos=0;std::vector<int>changed;
  for(int mask:e.masks){int i=first(code(a));if(i<0)return -1;auto&t=terms[i];
   for(int j=0;j<int(t.vars.size());j++)if((mask>>j)&1){int x=t.vars[j];if(pos>=int(e.values.size())||std::find(changed.begin(),changed.end(),x)!=changed.end())return -1;
    if(a[x]!=t.vals[j])return -1;
    changed.push_back(x);a[x]=e.values[pos++];}
  }
  if(pos!=int(e.values.size()))return -1;
  for(int x:changed)a[x]=q;
  return code(a);
 }
 std::string key(const Enc&e,bool masks,bool vals){std::string k=std::to_string(e.rp)+":";
  if(masks){for(int x:e.masks)k+=std::to_string(x)+",";}
  k+="|";
  if(vals){for(int x:e.values)k+=std::to_string(x)+",";}
  return k;
 }
 void one(U f){family=f;truth=0;for(int i=0;i<int(terms.size());i++)if((f>>i)&1)truth|=terms[i].truth;cache.assign(ns,-1);families++;
  U nonzero=0;for(int rho=0;rho<ns;rho++){depth(rho);if(truth&compatible[rho])nonzero+=weights[rho];}
  U den=pw(128*q,n),muNum=__builtin_popcountll(truth),muDen=pw(q,n);
  if(I(nonzero)*muDen>I(muNum)*den)noTail=true;
  for(int s=1;s<=n;s++){
   U bad=0;std::map<std::string,int> full,omitM,omitV;
   for(int rho=0;rho<ns;rho++)if(depth(rho)>=s){bad+=weights[rho];auto e=encode(rho,s);check(recover(e)==rho,"full round trip");roundtrips++;
    auto k=key(e,true,true);auto ins=full.emplace(k,rho);check(ins.second||ins.first->second==rho,"full encoding injective");
    auto im=omitM.emplace(key(e,false,true),rho);if(!im.second&&im.first->second!=rho&&!noMask){noMask=true;noMaskWitness=std::to_string(f)+":"+std::to_string(s)+":"+std::to_string(im.first->second)+","+std::to_string(rho);}
    auto iv=omitV.emplace(key(e,true,false),rho);if(!iv.second&&iv.first->second!=rho&&!noValues){noValues=true;noValuesWitness=std::to_string(f)+":"+std::to_string(s)+":"+std::to_string(iv.first->second)+","+std::to_string(rho);}
   }
   check(I(bad)*pw(127,s)<=I(pw(2*b*q*q,s))*den,"weighted switching tail");tailchecks++;
   check(I(nonzero)*muDen*pw(127,s)<=I(pw(q,s-1))*muNum*den*pw(127,s)+I(pw(2*b*q*q,s))*den*muDen,"density survival bound");survivalchecks++;
  }
 }
 void run(bool all){
  int m=terms.size();U forms=all?pw(2,m):1+U(m)+U(m)*(m-1)/2+U(m)*(m-1)*(m-2)/6;
  std::cout<<"PLAN q="<<q<<" n="<<n<<" width="<<b<<" terms="<<m<<" forms="<<forms<<" restrictions="<<ns<<" full_assignments="<<na<<" cutoff_tests="<<forms*n<<"\n"<<std::flush;
  if(forms*ns>2000000){std::cerr<<"oversized fixture\n";std::exit(2);}
  if(all){for(U f=0;f<pw(2,m);f++)one(f);}else{one(0);for(int i=0;i<m;i++){one(U(1)<<i);for(int j=i+1;j<m;j++){one((U(1)<<i)|(U(1)<<j));for(int k=j+1;k<m;k++)one((U(1)<<i)|(U(1)<<j)|(U(1)<<k));}}}
  check(families==forms,"completion count");
  std::cout<<"RESULT q="<<q<<" n="<<n<<" forms="<<families<<" roundtrips="<<roundtrips<<" tail="<<tailchecks<<" survival="<<survivalchecks<<" assertions="<<checks<<" failures="<<failures<<"\n";
  if(noMask)std::cout<<"CONTROL omitted-mask collision "<<noMaskWitness<<"\n";
  if(noValues)std::cout<<"CONTROL omitted-values collision "<<noValuesWitness<<"\n";
  std::cout<<"CONTROL missing-tail-refuted="<<noTail<<"\n"<<std::flush;
 }
};
int main(){
 Model a(2,2,2),b(3,2,2),c(3,3,2);a.run(true);b.run(true);c.run(false);
 bool controls=(a.noMask||b.noMask||c.noMask)&&(a.noValues||b.noValues||c.noValues)&&a.noTail&&b.noTail&&c.noTail;
 std::cout<<"FINAL assertions="<<a.checks+b.checks+c.checks<<" failures="<<a.failures+b.failures+c.failures<<" all_controls="<<controls<<"\n";
 return a.failures+b.failures+c.failures||!controls?1:0;
}
