#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <utility>
#include <vector>
using Edge=std::pair<int,int>;
std::array<long long,5> count(const std::vector<Edge>& edges){std::array<long long,5> z{};for(unsigned mask=0;mask<(1u<<16);mask++){int d=__builtin_popcount(mask);if(d>4)continue;bool ok=true;for(auto [u,v]:edges)if((mask>>u&1u)&&(mask>>v&1u)){ok=false;break;}if(ok)z[d]++;}return z;}
int main(int argc,char**argv){if(argc!=2)return 1;std::vector<std::vector<Edge>> cases(4);for(int j=1;j<16;j++)cases[0].push_back({0,j});for(int i=0;i<8;i++)for(int j=i+1;j<8;j++)cases[1].push_back({i,j});cases[2]=cases[1];for(int i=8;i<16;i++)for(int j=i+1;j<16;j++)cases[2].push_back({i,j});std::vector<Edge> all;for(int i=0;i<16;i++)for(int j=i+1;j<16;j++)all.push_back({i,j});std::mt19937 rng(321);std::shuffle(all.begin(),all.end(),rng);cases[3].assign(all.begin(),all.begin()+60);const std::array<std::string,4> names={"star","clique8","two_cliques8","seed321_60_edges"};std::ofstream out(argv[1]);out<<"{\"vertices\":16,\"degree_cutoff\":4,\"subsets_per_case\":65536,\"cases\":[";
for(int c=0;c<4;c++){auto z=count(cases[c]);long long J=std::accumulate(z.begin(),z.end(),0LL),r=cases[c].size(),Q=16*15-2*r,bound=4*Q*Q;if(J*24>bound)return 2;if(c)out<<",";out<<"{\"name\":\""<<names[c]<<"\",\"distinct_heads\":"<<r<<",\"independent_counts\":[";for(int j=0;j<5;j++){if(j)out<<",";out<<z[j];}out<<"],\"image_count\":"<<J<<",\"bound_numerator\":"<<bound<<",\"bound_denominator\":24,\"passed\":true}";}
auto z=count({{0,1}});long long J=std::accumulate(z.begin(),z.end(),0LL);if(J<=2400)return 3;out<<"],\"duplicate_head_control\":{\"actual_distinct_heads\":1,\"incorrect_reported_heads\":60,\"actual_image_count\":"<<J<<",\"incorrect_bound\":2400,\"rejected\":true},\"scope\":\"Exact small head-graph counts; no finite claim of asymptotic PHP separation.\"}\n";std::cout<<"Four exact head graphs passed; repeated-head overcount rejected ("<<J<<">2400).\n";return 0;}
