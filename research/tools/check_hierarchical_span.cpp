// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaustive small row-puncturing control and a fully specified subcube restriction.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
void need(bool v,const char*s){if(!v)throw std::runtime_error(s);}
struct Node{int depth,index;uint32_t leaves;};
std::vector<Node> nodes(int height){
 need(height>=1&&height<=5,"bounded tree height required");std::vector<Node> out;
 for(int d=0;d<height;++d)for(int j=0;j<(1<<d);++j){int size=1<<(height-d);uint32_t mask=0;for(int k=j*size;k<(j+1)*size;++k)mask|=uint32_t(1)<<k;out.push_back({d,j,mask});}
 return out;
}
int rank(std::vector<uint64_t> rows){
 uint64_t basis[64]{};int r=0;for(uint64_t x:rows)while(x){int p=63-__builtin_clzll(x);if(basis[p])x^=basis[p];else{basis[p]=x;++r;break;}}return r;
}
int canonical(const char*path){
 auto reverse=[](int x){int y=0;for(int j=0;j<5;++j)y=(y<<1)|((x>>j)&1);return y;};
 std::vector<int> survivors{0,8,16,24,32},assignment(33,-1);std::ofstream out(path);need(bool(out),"cannot open output");
 std::cout<<"Canonical height-five control: bit-reversal pinning outside the four-hole subcube; five surviving rows including the extra pigeon.\n";
 out<<"{\"height\":5,\"free_low_bits\":2,\"surviving_rows\":[0,8,16,24,32],\"remaining_holes\":[0,1,2,3],\"pinned_row_hole_pairs\":[";bool first=true;int pins=0;
 for(int i=0;i<32;++i)if(std::find(survivors.begin(),survivors.end(),i)==survivors.end()){
  assignment[i]=reverse(i);need(assignment[i]>=4,"pinned into reserved subcube");if(!first)out<<',';first=false;out<<'['<<i<<','<<assignment[i]<<']';++pins;
 }
 need(pins==28,"wrong pin count");out<<"],\"generator_columns\":[\"depth\",\"node_index\",\"coefficient_mask\",\"affine_constant\"],\"projected_generators\":[";
 std::vector<uint64_t> rows;int nonlocal=0,units=0;first=true;
 for(const auto&v:nodes(5)){int bit=4-v.depth,constant=0,full=0;uint64_t coeff=0;
  for(int i=0;i<32;++i)if(v.leaves&(uint32_t(1)<<i)){
   full^=(reverse(i)>>bit)&1;
   if(assignment[i]>=0)constant^=(assignment[i]>>bit)&1;
   else if(bit<2){auto it=std::find(survivors.begin(),survivors.end(),i);int pos=int(it-survivors.begin());coeff^=uint64_t(1)<<(2*pos+bit);}
  }
  need(full==0,"bit reversal does not satisfy the original parity");int support=0;for(int j=0;j<5;++j)support+=((coeff>>(2*j))&3)!=0;
  nonlocal+=support>1;units+=(coeff==0&&constant==1);rows.push_back(coeff);if(!first)out<<',';first=false;out<<'['<<v.depth<<','<<v.index<<','<<coeff<<','<<constant<<']';
 }
 int r=rank(rows);need(r==8&&nonlocal==0&&units==0,"canonical control failed");
 out<<"],\"coefficient_rank\":"<<r<<",\"local_dimensions\":[2,2,2,2,0],\"nonlocal_generators\":0,\"constant_one_generators\":0,\"passed\":true}\n";need(bool(out),"output write failed");
 std::cout<<"Rank "<<r<<", no nonlocal or constant-one generator; all original node parities vanish under bit reversal; passed\n";return 0;
}
int main(int argc,char**argv)try{
 need((argc==3||argc==4)&&std::string(argv[1])=="--out","usage: --out FILE [--canonical-only]");std::ifstream old(argv[2]);need(!old.good(),"refusing overwrite");
 if(argc==4){need(std::string(argv[3])=="--canonical-only","unknown option");return canonical(argv[2]);}
 std::cout<<"Fixed negative tree height 4: all 65536 row subsets, 15 node supports each. Positive height 5 with five surviving rows and four subcube holes. No larger enumeration.\n";
 std::ofstream out(argv[2]);need(bool(out),"cannot open output");auto tree=nodes(4);
 out<<"{\"row_puncturing\":{\"height\":4,\"columns_per_record\":[\"row_mask\",\"surviving_rows\",\"local_dimension\",\"quotient_dimension\",\"quotient_min_row_distance_or_zero\"],\"records\":[";
 int tested=0,min_slack=100;bool comma=false;
 for(uint32_t mask=0;mask<(uint32_t(1)<<16);++mask){int k=__builtin_popcount(mask),local=0,global=0,distance=100;
  for(const auto&v:tree){int support=__builtin_popcount(mask&v.leaves);if(support==1)++local;else if(support>=2){++global;distance=std::min(distance,support);}}
  if(!global)distance=0;
  if(k>=2){need(global>=k-1,"too few coupling coordinates");need(distance==2,"minimum quotient support is not two");++tested;min_slack=std::min(min_slack,global-(k-1));}
  if(comma)out<<',';
  comma=true;out<<'['<<mask<<','<<k<<','<<local<<','<<global<<','<<distance<<']';
 }
 out<<"],\"tested_nontrivial_subsets\":"<<tested<<",\"minimum_dimension_slack\":"<<min_slack<<"},\"subcube_restriction\":{\"height\":5,\"free_low_bits\":2,\"surviving_rows\":[0,4,8,12,16],\"remaining_holes\":[0,1,2,3],\"pinned_row_hole_pairs\":[";
 std::vector<int> survivors{0,4,8,12,16},assignment(33,-1);int hole=4;bool first=true;
 for(int i=0;i<33;++i)if(std::find(survivors.begin(),survivors.end(),i)==survivors.end()){
  assignment[i]=hole;need(hole<32,"pinning too many rows");if(!first)out<<',';first=false;out<<'['<<i<<','<<hole<<']';++hole;
 }
 need(hole==32,"pinning does not exhaust outside holes");
 out<<"],\"generator_columns\":[\"depth\",\"node_index\",\"coefficient_mask\",\"affine_constant\"],\"projected_generators\":[";
 auto large=nodes(5);std::vector<uint64_t> rows;int nonlocal=0,units=0;first=true;
 for(const auto&v:large){int bit=4-v.depth,constant=0;uint64_t coeff=0;
  for(int i=0;i<32;++i)if(v.leaves&(uint32_t(1)<<i)){
   if(assignment[i]>=0)constant^=(assignment[i]>>bit)&1;
   else if(bit<2){auto it=std::find(survivors.begin(),survivors.end(),i);need(it!=survivors.end(),"unknown surviving row");int pos=int(it-survivors.begin());coeff^=uint64_t(1)<<(2*pos+bit);}
  }
  int support=0;for(int j=0;j<5;++j)support+=((coeff>>(2*j))&3)!=0;
  nonlocal+=support>1;units+=(coeff==0&&constant==1);rows.push_back(coeff);
  if(!first)out<<',';
  first=false;out<<'['<<v.depth<<','<<v.index<<','<<coeff<<','<<constant<<']';
 }
 int r=rank(rows);need(r==10&&nonlocal==0,"subcube projection is not the full local coefficient space");
 out<<"],\"coefficient_rank\":"<<r<<",\"nonlocal_generators\":"<<nonlocal<<",\"constant_one_generators\":"<<units<<",\"passed\":true}}\n";need(bool(out),"output write failed");
 std::cout<<"Checked "<<tested<<" row subsets of size >=2: coupling dimension >=k-1 and quotient distance 2. Positive restriction: rank "<<r<<", nonlocal generators "<<nonlocal<<", constant-one generators "<<units<<"; passed\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
