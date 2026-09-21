#define main previous_check_main
#include "../odd_prime_matching_residual_20260921_functional_classification/check.cpp"
#undef main
int main(int argc,char**argv){
 if(argc!=2)return 1;
 Check c(3);for(int i=0;i<=c.v;i++){V q(c.dim);q[i]=1;c.add(q);}auto before=c.basis.size();
 int terms=0;for(int i=0;i<c.m;i++)for(int k=0;k<c.m;k++)if(i!=k){V q(c.dim);q[c.pair(4*i,4*k+1)]=1;c.add(q);terms++;}
 if(int(c.basis.size()-before)!=terms)return 2;
 int states=0,negative=0;
 for(int a=-1;a<c.m;a++)for(int b=-1;b<c.m;b++){
  if(a>=0&&a==b)continue;
  states++;int dot=0;std::vector<int> inputs;
  for(int i=0;i<c.m;i++)for(int k=0;k<c.m;k++)if(i!=k){int x=(a==i),y=(b==k),L=c.mod(1+x+y),g=c.mod(1-L*L),beta=x*y;dot=c.mod(dot+beta*g);inputs.push_back(g);if(c.mod(beta*beta*beta-beta))return 3;}
  int P=c.mod(1-dot);bool wrong=false;for(int g:inputs){if(c.mod(g*P))return 4;wrong|=g!=0;}negative+=wrong;
 }
 std::ofstream out(argv[1]);out<<"{\"field\":3,\"holes\":4,\"rows\":5,\"I2_plus_affine_rank\":"<<before<<",\"selector_count\":"<<terms<<",\"nonlinear_quotient_rank\":"<<c.basis.size()-before<<",\"two_column_states_checked\":"<<states<<",\"zero_map_failure_states\":"<<negative<<",\"passed\":true,\"scope\":\"Exact small-board quotient rank and finite column-state map control; general rank and degree ledger are proved in the notebook.\"}\n";
 std::cout<<"Rank "<<c.basis.size()-before<<" for "<<terms<<" selectors; "<<states<<" states passed; wrong zero map fails on "<<negative<<" states.\n";
}
