#define main classification_old_main
#include "../odd_prime_matching_residual_20260921_functional_classification/check.cpp"
#undef main
int main(int argc,char**argv){
 if(argc!=2)return 1;
 Check c(3);const auto old_rank=c.basis.size();
 for(int j=0;j<=c.v;j++){V q(c.dim);q[j]=1;c.add(q);}
 c.allowed.clear();
 auto generate=[&](V positions){int count=c.p;for(size_t j=0;j<positions.size();j++)count*=c.p;if(count>1000)std::exit(7);for(int code=0;code<count;code++){int z=code,offset=z%c.p;z/=c.p;V a(c.v);for(int j:positions){a[j]=z%c.p;z/=c.p;}c.allowed.insert(c.key(offset,a));}};
 for(int i=0;i<c.m;i++)generate(V{4*i,4*i+1,4*i+2,4*i+3});
 for(int j=0;j<c.n;j++)generate(V{j,4+j,8+j,12+j,16+j});
 std::cout<<"Testing 5605 affine forms over F3 against I_2 plus all affine polynomials; 231 coordinates.\n";
 c.run();
 std::ofstream out(argv[1]);out<<"{\"field\":3,\"old_NS_rank\":"<<old_rank<<",\"NS_plus_affine_rank\":"<<c.basis.size()<<",\"row_or_column_affine_classes\":"<<c.allowed.size()<<",\"tested\":"<<c.tested<<",\"affinizible\":"<<c.positive<<",\"passed\":true,\"scope\":\"Bounded two-row and column slices, 500 full-board samples, row/cross controls; not exhaustive over all affine forms.\"}\n";
 std::cout<<"Passed "<<c.tested<<" tests; "<<c.positive<<" affinizible; augmented span rank "<<c.basis.size()<<".\n";
}
