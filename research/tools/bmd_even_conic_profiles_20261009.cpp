// Exact characteristic-three order profiles of F_c(X^2)+X F_(c-h)(X^2).
// Compare each bounded high-window encoding with the complete Pascal matrix.
#include <flint/nmod_mat.h>
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
void ck(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int binom3(int n,int k){if(k<0||k>n)return 0;static int C[3][3]={{1,0,0},{1,1,0},{1,2,1}};int v=1;while(n||k){int a=n%3,b=k%3;if(b>a)return 0;v=v*C[a][b]%3;n/=3;k/=3;}return v;}
std::vector<int> pivots(nmod_mat_t A){slong rank=nmod_mat_rref(A);std::vector<int>p;for(int i=0;i<rank;i++){int j=0;while(j<A->c&&nmod_mat_entry(A,i,j)==0)j++;ck(j<A->c,"nonzero RREF row");p.push_back(j);}ck(std::is_sorted(p.begin(),p.end()),"ordered pivots");return p;}
struct Profile{int d,c,s;std::vector<int>p,missing;};
Profile make(int h,int period,int d){int m=0;while((1<<m)<h)m++;ck((1<<m)==h,"dyadic width");int c=h-1+((h*(d-m+1)-1-(h-1))%period+period)%period,L=2*c-2*h+2;
 nmod_mat_t window;nmod_mat_init(window,h,2*h-1,3);for(int j=0;j<h;j++)for(int i=0;i<2*h-1;i++)nmod_mat_entry(window,j,i)=binom3(L+2*j,2*j-i);auto p=pivots(window);nmod_mat_clear(window);ck((int)p.size()==h,"full bounded window rank");
 std::vector<int>exponents;for(int j=0;j<=c;j++)exponents.push_back(2*j);for(int j=0;j<=c-h;j++)exponents.push_back(2*j+1);
 nmod_mat_t whole;nmod_mat_init(whole,exponents.size(),2*c+1,3);for(int j=0;j<(int)exponents.size();j++)for(int i=0;i<=2*c;i++)nmod_mat_entry(whole,j,i)=binom3(exponents[j],i);auto full=pivots(whole);nmod_mat_clear(whole);
 std::vector<int>expected;for(int i=0;i<L;i++)expected.push_back(i);for(int i:p)expected.push_back(L+i);ck(full==expected,"bounded profile equals the full actual monomial source");
 int s=p.back()-h+1;ck(s>=0&&s<h,"bounded pole increment");std::vector<int>missing;for(int i=0;i<=p.back();i++)if(!std::binary_search(p.begin(),p.end(),i))missing.push_back(p.back()-i);std::sort(missing.begin(),missing.end());ck((int)missing.size()==s,"complete missing Bernstein coefficients");
 return {d,c,s,p,missing};}
void vec(std::ostream&out,const std::vector<int>&v){out<<'[';for(size_t i=0;i<v.size();i++)out<<(i?",":"")<<v[i];out<<']';}
int main(int argc,char**argv){try{ck(argc==2,"output required");std::ofstream out(argv[1]);out<<"{\"prime\":3,\"profiles\":[";bool first=true;for(auto pair:std::vector<std::pair<int,int>>{{4,9},{8,27},{16,81}}){auto[h,period]=pair;std::array<int,16>hist{};std::vector<int>ordinary;for(int d=0;d<period;d++){auto r=make(h,period,d);hist[r.s]++;if(!r.s)ordinary.push_back(d);if(h==16){if(!first)out<<',';first=false;out<<"{\"degree_residue\":"<<d<<",\"c_representative\":"<<r.c<<",\"s\":"<<r.s<<",\"pivot_offsets\":";vec(out,r.p);out<<",\"missing_rho_powers\":";vec(out,r.missing);out<<'}';}}std::cout<<"WIDTH "<<h<<" PERIOD "<<period<<" profiles="<<period<<" full_source_controls=true\n";for(int s=0;s<h;s++)if(hist[s])std::cout<<"SHIFT "<<s<<" count="<<hist[s]<<"\n";std::cout<<"ORDINARY ";vec(std::cout,ordinary);std::cout<<'\n';}out<<"],\"all_117_full_source_controls\":true}\n";std::cout<<"COMPLETE all117 bounded profiles match full Pascal RREF; every missing coefficient retained.\n";}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
