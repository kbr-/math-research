\\ Exact comparison at every D=7 mod37 in the n9 bulk.
p=37;h=128;s=128*7-448;
w(k)=max(0,k\2-max(1,k-h+1)+1);
{my(den=sum(k=2,2*h-2,w(k)*valuation(k,p)),num=sum(k=2,2*h-2,if((2*s+k)%p==0,w(k),0)));
if(den!=216||num!=218||2*h-2>=p^2,error("comparison control"));
print("CLASS D=7+37t t>=0; h=128; s=128D-448; denominator_valuation=",den," numerator_first_level=",num," valuation_lower_bound=",num-den);
print("PASS entire class has nonunit joint-leading factor; paired residual classes are D=3 mod37, so the new cover certifies this class by a different coefficient.");}
quit;
