// Exact F3[u] determinant and polynomial inverse certificate using FLINT.
// Input: cases; then e,n,P, followed by n*n sparse coefficient lists (count; exponent,value).
// Case5 is the independent PARI calibration (det order40, coefficient2, inverse pole18).
#include <flint/nmod_poly_mat.h>
#include <flint/nmod_poly.h>
#include <fstream>
#include <iostream>
#include <chrono>
#include <stdexcept>
#include <algorithm>
#include <cmath>
using namespace std;
long ord(const nmod_poly_t a){for(long j=0;j<a->length;j++)if(a->coeffs[j])return j;return 1000000000;}
void check(bool b,const char*s){if(!b)throw runtime_error(s);}
int main(int argc,char**argv){
 check(argc==3,"input and output prefix required");ifstream in(argv[1]);check(bool(in),"input missing");
 int cases;in>>cases;
 for(int cs=0;cs<cases;cs++){
  int e,n,P;in>>e>>n>>P;check(n>0&&n<=48&&P==192,"bounded input");
  auto start=chrono::steady_clock::now();auto elapsed=[&](){return chrono::duration<double>(chrono::steady_clock::now()-start).count();};
  nmod_poly_mat_t A,N,C,E;nmod_poly_mat_init(A,n,n,3);nmod_poly_mat_init(N,n,n,3);nmod_poly_mat_init(C,n,n,3);nmod_poly_mat_init(E,n,n,3);
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   int count;in>>count;check(count>=0&&count<=P,"coefficient count");
   for(int k=0;k<count;k++){int a,b;in>>a>>b;check(a>=0&&a<P&&b>0&&b<3,"coefficient bounds");nmod_poly_set_coeff_ui(nmod_poly_mat_entry(A,i,j),a,b);}
  }
  check(bool(in),"truncated input");
  nmod_poly_t D,den,unit,inv,temp;nmod_poly_init(D,3);nmod_poly_init(den,3);nmod_poly_init(unit,3);nmod_poly_init(inv,3);nmod_poly_init(temp,3);
  cout<<"CASE "<<e<<" dimension="<<n<<" determinant start"<<endl;
  nmod_poly_mat_det(D,A);check(!nmod_poly_is_zero(D),"polynomial determinant zero");
  long v=ord(D);auto coef=nmod_poly_get_coeff_ui(D,v);
  cout<<"ORDER="<<v<<" COEFFICIENT="<<coef<<" determinant_seconds="<<elapsed()<<endl;
  check(nmod_poly_mat_inv(N,den,A),"inverse construction failed");
  long vd=ord(den),mn=1000000000;
  for(int i=0;i<n;i++)for(int j=0;j<n;j++)mn=min(mn,ord(nmod_poly_mat_entry(N,i,j)));
  long h=max(0L,vd-mn);check(h<P,"inverse poles reach precision");
  nmod_poly_shift_right(unit,den,vd);nmod_poly_inv_series(inv,unit,h+1);
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   if(vd>=h)nmod_poly_shift_right(temp,nmod_poly_mat_entry(N,i,j),vd-h);
   else nmod_poly_shift_left(temp,nmod_poly_mat_entry(N,i,j),h-vd);
   nmod_poly_mullow(nmod_poly_mat_entry(C,i,j),temp,inv,h+1);
  }
  nmod_poly_mat_mul(E,A,C);
  for(int i=0;i<n;i++)for(int j=0;j<n;j++)for(long k=0;k<=h;k++)
   check(nmod_poly_get_coeff_ui(nmod_poly_mat_entry(E,i,j),k)==(i==j&&k==h?1:0),"exact polynomial product failed");
  if(e==5)check(v==40&&coef==2&&h==18,"independent PARI control mismatch");
  string path=string(argv[2])+"-class"+to_string(e)+".txt";FILE*out=fopen(path.c_str(),"w");check(out,"certificate output");
  fprintf(out,"CASE=%d dimension=%d precision=%d order=%ld coefficient=%lu inverse_pole=%ld error_bound=%ld\n",e,n,P,v,coef,h,v+P-h);
  fprintf(out,"C in row-major order; FLINT polynomial format: length, modulus, coefficients.\n");
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){nmod_poly_fprint(out,nmod_poly_mat_entry(C,i,j));fputc('\n',out);}
  fprintf(out,"PASS exact A*C congruent to u^h I modulo u^(h+1).\n");fclose(out);
  cout<<"PASS class="<<e<<" order="<<v<<" coefficient="<<coef<<" pole="<<h<<" error="<<v+P-h<<" total_seconds="<<elapsed()<<endl;
  if(cs==0){double estimate=2*elapsed()*pow(48.0/n,4);cout<<"largest_estimate_seconds="<<estimate<<endl;check(estimate<120,"resize or optimize before largest matrix");}
  nmod_poly_clear(D);nmod_poly_clear(den);nmod_poly_clear(unit);nmod_poly_clear(inv);nmod_poly_clear(temp);
  nmod_poly_mat_clear(A);nmod_poly_mat_clear(N);nmod_poly_mat_clear(C);nmod_poly_mat_clear(E);
 }
}
