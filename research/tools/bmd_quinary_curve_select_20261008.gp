\\ Select a bounded torsion input for the exact remaining paired degree classes.
default(parisizemax,2500000000);
default(nbthreads,1);
modulus=ffinit(5,2);a=ffgen(modulus,'a);o=a^0;
field=vector(25,i,o*((i-1)%5)+a*((i-1)\5));
chi(z)=if(z==0,0,if(z^12==o,1,-1));
val=matrix(24,25,i,j,o+field[i+1]*field[j]);
seen=0;best=10^9;chosen=[];selected=[];hist=Map();
{for(i=3,23,for(j=i+1,24,for(k=j+1,25,
my(ids=[2,i,j,k],sl=vector(4,t,field[ids[t]]),ns=List(),ex=1);
for(mask=0,15,if(hammingweight(mask)>=3,my(n=if(hammingweight(mask)%2,1,1+chi(prod(t=1,4,if(bittest(mask,t-1),sl[t],o)))));for(z=1,25,n+=1+chi(prod(t=1,4,if(bittest(mask,t-1),val[ids[t]-1,z],o))));if(n%4,error("rational elliptic two torsion"));listput(ns,n);my(e=n/2);ex=lcm(ex,e/gcd(e,4))));
my(bound=lcm(32,8*ex));seen++;print("SLOPES ",ids-vector(4,t,1)," quotient_orders ",Vec(ns)," A0_bound ",bound);
if(bound<best && Vec(ns)!=[32,32,32,32,32],best=bound;chosen=ids-vector(4,t,1);selected=Vec(ns));
)));}
if(seen!=1771 || #chosen!=4,error("complete curve selection"));
print("SELECTED slopes=",chosen," orders=",selected," torsion_bound=",best," modulus=",modulus);
write("research/results/bmd-nine-quinary-period-20261008/selected-curve.gp","slCodes=",chosen,";torsionBound=",best,";baseModulus=",modulus,";");
print("COMPLETE 1771 quotient-count inputs; no original degree scan.");
