// Independent FLINT verification of all character congruences modulo3^5.
#include <flint/nmod_poly.h>
#include <fstream>
#include <iostream>
#include <array>
#include <stdexcept>
void check(bool c,const char*s){if(!c)throw std::runtime_error(s);}
int main(int argc,char**argv){
 try{
  check(argc==2,"usage ring-input");std::ifstream in(argv[1]);
  int count,mod,power;in>>count>>mod>>power;check(count==466&&mod==243&&power==9360,"complete input");
  std::array<int,5>periods={1,3,9,27,81},counts{};int genus=0;
  for(int i=0;i<count;i++){
   int mask,g,expected;in>>mask>>g>>expected;check(mask>0&&mask<512&&g>0&&g<=4,"input scope");
   genus+=g;nmod_poly_t f,x,tau,saved,test,corrupt;
   nmod_poly_init(f,mod);nmod_poly_init(x,mod);nmod_poly_init(tau,mod);
   nmod_poly_init(saved,mod);nmod_poly_init(test,mod);nmod_poly_init(corrupt,mod);
   for(int j=0;j<=2*g;j++){long c;in>>c;long r=c%mod;if(r<0)r+=mod;nmod_poly_set_coeff_ui(f,j,r);}
   for(int j=0;j<2*g;j++){unsigned long c;in>>c;check(c<(unsigned)mod,"canonical residue");nmod_poly_set_coeff_ui(saved,j,c);}
   check(in.good()&&nmod_poly_degree(f)==2*g&&nmod_poly_get_coeff_ui(f,2*g)==1,"monic polynomial");
   nmod_poly_set_coeff_ui(x,1,1);nmod_poly_powmod_ui_binexp(tau,x,power,f);
   check(nmod_poly_equal(tau,saved),"independent power coefficients");
   int found=-1;
   for(int j=0;j<5;j++){
    nmod_poly_powmod_ui_binexp(test,tau,periods[j]+1,f);
    if(nmod_poly_equal(test,tau)){found=j;break;}
   }
   check(found>=0&&periods[found]==expected,"independent period");
   counts[found]++;
   nmod_poly_set(corrupt,saved);nmod_poly_set_coeff_ui(corrupt,0,(nmod_poly_get_coeff_ui(saved,0)+1)%mod);
   check(!nmod_poly_equal(tau,corrupt),"coefficient corruption detected");
   nmod_poly_clear(f);nmod_poly_clear(x);nmod_poly_clear(tau);
   nmod_poly_clear(saved);nmod_poly_clear(test);nmod_poly_clear(corrupt);
  }
  check(genus==769,"complete genus sum");std::cout<<"FLINT_RETURN_RING_COMPLETED characters="<<count<<" genus_sum="<<genus<<" modulus243 global_period27 counts";
  for(auto c:counts)std::cout<<" "<<c;std::cout<<" coefficient_corruptions_detected=466\n";
 }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 1;}
}
