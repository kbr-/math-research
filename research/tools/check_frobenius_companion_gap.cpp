// Exact finite controls for the companion-compression degree/width example.
// No floating-point arithmetic. Run via compute.sh; output is complete JSON.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Poly = std::vector<uint8_t>;
static void require(bool ok, const std::string& why) {
  if (!ok) throw std::runtime_error(why);
}
static unsigned weight(unsigned x) { return __builtin_popcount(x); }

struct Field {
  unsigned size, modulus;
  uint8_t mul[32][32]{}, inv[32]{};
  Field(unsigned degree, unsigned polynomial)
      : size(1u << degree), modulus(polynomial) {
    require(size <= 32, "field cap exceeded");
    for (unsigned a=0; a<size; ++a) for (unsigned b=0; b<size; ++b) {
      unsigned x=a, y=b, z=0;
      while (y) {
        if (y&1) z^=x;
        y>>=1; x<<=1;
        if (x&size) x^=modulus;
      }
      mul[a][b]=static_cast<uint8_t>(z);
    }
    for (unsigned a=1; a<size; ++a) {
      for (unsigned b=1; b<size; ++b) if (mul[a][b]==1) inv[a]=b;
      require(inv[a]!=0, "modulus did not yield a field");
    }
  }
};
static Poly product(const Poly& a, const Poly& b, const Field& f) {
  Poly c(a.size());
  for (unsigned i=0; i<a.size(); ++i) if (a[i])
    for (unsigned j=0; j<b.size(); ++j) if (b[j])
      c[i|j]^=f.mul[a[i]][b[j]];
  return c;
}
static Poly monomial_multiple(const Poly& a, unsigned mask) {
  Poly c(a.size());
  for (unsigned i=0; i<a.size(); ++i) if (a[i]) c[i|mask]^=a[i];
  return c;
}
static unsigned degree(const Poly& a) {
  unsigned d=0;
  for (unsigned i=0; i<a.size(); ++i) if (a[i]) d=std::max(d,weight(i));
  return d;
}
struct Space {
  const Field& f;
  std::vector<unsigned> order;
  std::vector<Poly> basis;
  unsigned rank=0;
  Space(unsigned n, const Field& field): f(field), order(n), basis(n) {
    for (unsigned i=0; i<n; ++i) order[i]=i;
    std::sort(order.begin(),order.end(),[](unsigned a,unsigned b){
      return weight(a)!=weight(b) ? weight(a)>weight(b) : a>b;
    });
  }
  int insert(Poly v) {
    for (unsigned pivot:order) if (v[pivot]) {
      const auto c=v[pivot];
      if (basis[pivot].empty()) {
        const auto scale=f.inv[c];
        for (auto& x:v) x=f.mul[scale][x];
        basis[pivot]=std::move(v); ++rank;
        return static_cast<int>(pivot);
      }
      for (unsigned j=0; j<v.size(); ++j)
        if (basis[pivot][j]) v[j]^=f.mul[c][basis[pivot][j]];
    }
    return -1;
  }
  bool contains(Poly v) const {
    for (unsigned pivot:order) if (v[pivot]) {
      if (basis[pivot].empty()) return false;
      auto c=v[pivot];
      for (unsigned j=0; j<v.size(); ++j)
        if (basis[pivot][j]) v[j]^=f.mul[c][basis[pivot][j]];
    }
    return true;
  }
};
static Space ns_space(const std::vector<Poly>& generators,
                      unsigned raw_degree, unsigned ceiling,
                      unsigned columns, const Field& f) {
  Space s(columns,f);
  if (ceiling>=raw_degree)
    for (const auto& g:generators)
      for (unsigned mask=0; mask<columns; ++mask)
        if (weight(mask)<=ceiling-raw_degree)
          s.insert(monomial_multiple(g,mask));
  return s;
}
static Space pc_space(const std::vector<Poly>& generators,
                      unsigned raw_degree, unsigned ceiling,
                      unsigned variables, const Field& f) {
  const unsigned columns=1u<<variables;
  Space s(columns,f);
  std::vector<unsigned> queue;
  auto add=[&](Poly v) {
    int pivot=s.insert(std::move(v));
    if (pivot>=0 && weight(static_cast<unsigned>(pivot))<ceiling)
      queue.push_back(static_cast<unsigned>(pivot));
  };
  if (raw_degree<=ceiling) for (auto g:generators) add(std::move(g));
  // Degree-descending echelon pivots span the complete filtered subspace.
  // Stored rows do not change, so each eligible row is multiplied only once.
  for (unsigned head=0; head<queue.size(); ++head) {
    Poly v=s.basis[queue[head]];
    for (unsigned j=0; j<variables; ++j)
      add(monomial_multiple(v,1u<<j));
    require(queue.size()<=columns, "closure queue exceeded dimension");
  }
  return s;
}
static unsigned matrix_rank(std::vector<Poly> a, const Field& f) {
  if (a.empty()) return 0;
  unsigned row=0;
  for (unsigned col=0; col<a[0].size() && row<a.size(); ++col) {
    unsigned pivot=row;
    while (pivot<a.size() && a[pivot][col]==0) ++pivot;
    if (pivot==a.size()) continue;
    std::swap(a[pivot],a[row]);
    auto inv=f.inv[a[row][col]];
    for (auto& x:a[row]) x=f.mul[inv][x];
    for (unsigned i=0; i<a.size(); ++i) if (i!=row && a[i][col]) {
      auto scale=a[i][col];
      for (unsigned j=col; j<a[i].size(); ++j)
        a[i][j]^=f.mul[scale][a[row][j]];
    }
    ++row;
  }
  return row;
}
static std::string run_case(unsigned k,unsigned h,unsigned modulus,bool ranks) {
  const unsigned variables=k+h*(k+1), columns=1u<<variables;
  require(variables<=11 && (!ranks || variables<=9),
          "enumeration refused: fixed column cap exceeded");
  Field f(k+1,modulus);
  std::vector<Poly> inputs(k+1,Poly(columns));
  inputs[0][1]=1; inputs[1][0]=1; inputs[1][1]=1;
  for (unsigned j=2; j<=k; ++j) inputs[j][1u<<(j-1)]=1;
  Poly P(columns); P[0]=1;
  for (unsigned u=0; u<h; ++u) {
    Poly factor(columns); factor[0]=1;
    for (unsigned j=0; j<=k; ++j) {
      auto term=monomial_multiple(inputs[j],1u<<(k+u*(k+1)+j));
      for (unsigned i=0; i<columns; ++i) factor[i]^=term[i];
    }
    P=product(P,factor,f);
  }
  Poly L(columns); L[0]=1;
  for (unsigned j=0; j<k; ++j) L[1u<<j]=1u<<(j+1);
  Poly H=product(L,P,f);
  require(degree(P)==2*h && degree(H)==2*h+1,
          "multilinear leading-degree control failed");
  std::vector<Poly> originals;
  for (auto& g:inputs) originals.push_back(product(g,P,f));
  Poly identity=originals[0];
  for (unsigned i=0; i<columns; ++i) identity[i]^=originals[1][i];
  require(identity==P, "original constant-cofactor identity failed");

  std::vector<uint8_t> values(1u<<k);
  for (unsigned x=0; x<values.size(); ++x) {
    unsigned value=1;
    for (unsigned j=0; j<k; ++j) if (x&(1u<<j)) value^=1u<<(j+1);
    require(value!=0, "encoded linear form unexpectedly vanished");
    values[x]=f.inv[value];
  }
  auto coeff=values;
  for (unsigned j=0; j<k; ++j)
    for (unsigned x=0; x<coeff.size(); ++x)
      if (x&(1u<<j)) coeff[x]^=coeff[x^(1u<<j)];
  Poly inverse(columns);
  for (unsigned x=0; x<coeff.size(); ++x) inverse[x]=coeff[x];
  require(degree(inverse)==k, "inverse degree was not sharp");
  require(product(inverse,H,f)==P, "compressed upper certificate failed");

  unsigned min_cut=1u<<k, cuts=0;
  for (unsigned left=0; left<(1u<<k); ++left) if (weight(left)==k/2) {
    std::vector<unsigned> A,B;
    for (unsigned j=0; j<k; ++j) ((left&(1u<<j))?A:B).push_back(j);
    std::vector<Poly> matrix(1u<<A.size(),Poly(1u<<B.size()));
    for (unsigned a=0; a<matrix.size(); ++a)
      for (unsigned b=0; b<matrix[a].size(); ++b) {
        unsigned x=0;
        for (unsigned j=0; j<A.size(); ++j) if (a&(1u<<j)) x|=1u<<A[j];
        for (unsigned j=0; j<B.size(); ++j) if (b&(1u<<j)) x|=1u<<B[j];
        matrix[a][b]=values[x];
      }
    min_cut=std::min(min_cut,matrix_rank(std::move(matrix),f)); ++cuts;
  }
  require(min_cut==(1u<<(k/2)), "Cauchy cut-rank control failed");
  std::ostringstream out;
  out << "{\"k\":"<<k<<",\"h\":"<<h<<",\"field_degree\":"<<k+1
      <<",\"field_modulus\":"<<modulus<<",\"variables\":"<<variables
      <<",\"Boolean_columns\":"<<columns<<",\"rank_spaces_checked\":"
      <<(ranks?"true":"false")<<",\"product_degree\":"<<degree(P)
      <<",\"compressed_generator_degree\":"<<degree(H)
      <<",\"inverse_degree\":"<<degree(inverse)
      <<",\"inverse_top_coefficient\":"<<unsigned(coeff.back())
      <<",\"balanced_cuts_checked\":"<<cuts
      <<",\"minimum_cut_rank\":"<<min_cut
      <<",\"upper_certificate_identity\":true";
  if (ranks) {
    auto orig_ns=ns_space(originals,2*h+1,2*h+1,columns,f);
    auto orig_pc=pc_space(originals,2*h+1,2*h+1,variables,f);
    require(orig_ns.contains(P) && orig_pc.contains(P), "original proof missing");
    require(!ns_space(originals,2*h+1,2*h,columns,f).contains(P),
            "original NS proof below active-axiom ceiling");
    require(!pc_space(originals,2*h+1,2*h,variables,f).contains(P),
            "original PC proof below active-axiom ceiling");
    out<<",\"original_NS_minimum\":"<<2*h+1
       <<",\"original_PC_minimum\":"<<2*h+1<<",\"compressed_NS\":[";
    for (unsigned d=2*h+1; d<=2*h+k+1; ++d) {
      auto space=ns_space({H},2*h+1,d,columns,f);
      bool member=space.contains(P);
      require(member==(d==2*h+k+1), "compressed NS threshold failed");
      if (d!=2*h+1) out<<",";
      out<<"{\"degree\":"<<d<<",\"rank\":"<<space.rank
         <<",\"contains_target\":"<<(member?"true":"false")<<"}";
    }
    out<<"],\"compressed_PC\":[";
    for (unsigned d=2*h+1; d<=2*h+2; ++d) {
      auto space=pc_space({H},2*h+1,d,variables,f);
      bool member=space.contains(P);
      require(member==(d==2*h+2), "compressed PC threshold failed");
      if (d!=2*h+1) out<<",";
      out<<"{\"degree\":"<<d<<",\"rank\":"<<space.rank
         <<",\"contains_target\":"<<(member?"true":"false")<<"}";
    }
    out<<"]";
  }
  out<<"}";
  return out.str();
}
int main(int argc,char** argv) {
  try {
    require(argc==3 && std::string(argv[1])=="--out", "usage: checker --out FILE");
    std::cerr<<"Plan: exact rank spaces at 32, 128 and 512 Boolean columns; "
             <<"one 2048-column identity-only control. No larger enumeration allowed.\n";
    std::string result="{\"scope\":\"Exact finite controls; not a proof of the arbitrary-parameter theorem\","
      "\"cases\":["+run_case(2,1,0b1011,true)+","
      +run_case(3,1,0b10011,true)+","
      +run_case(4,1,0b100101,true)+","
      +run_case(3,2,0b10011,false)+"]}\n";
    std::ofstream out(argv[2]); require(bool(out), "cannot open output");
    out<<result; require(bool(out), "cannot write output"); out.close();
    std::cout<<result;
  } catch (const std::exception& e) {
    std::cerr<<e.what()<<"\n"; return 1;
  }
}
