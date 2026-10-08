\\ Select a bounded torsion input for the exact remaining paired degree classes.
default(parisizemax,2500000000);
default(nbthreads,1);
modulus=ffinit(7,2);a=ffgen(modulus,'a);o=a^0;
field=vector(49,i,o*((i-1)%7)+a*((i-1)\7));
chi(z)=if(z==0,0,if(z^24==o,1,-1));
val=matrix(48,49,i,j,o+field[i+1]*field[j]);
seen=0;best=10^9;chosen=[];selected=[];hist=Map();
{for(i=3,47,for(j=i+1,48,for(k=j+1,49,
my(ids=[2,i,j,k],sl=vector(4,t,field[ids[t]]),ns=List(),ex=1);
for(mask=0,15,if(hammingweight(mask)>=3,my(n=if(hammingweight(mask)%2,1,1+chi(prod(t=1,4,if(bittest(mask,t-1),sl[t],o)))));for(z=1,49,n+=1+chi(prod(t=1,4,if(bittest(mask,t-1),val[ids[t]-1,z],o))));if(n%4,error("rational elliptic two torsion"));listput(ns,n);my(e=n/2);ex=lcm(ex,e/gcd(e,4))));
my(bound=lcm(32,8*ex));seen++;print("SLOPES ",ids-vector(4,t,1)," quotient_orders ",Vec(ns)," A0_bound ",bound);
if(bound<best,best=bound;chosen=ids-vector(4,t,1);selected=Vec(ns));
)));}
if(seen!=16215 || #chosen!=4,error("complete curve selection"));
print("SELECTED slopes=",chosen," orders=",selected," torsion_bound=",best," modulus=",modulus);
write("research/results/bmd-nine-septenary-period-20261008/selected-extension-curve.gp","slCodes=",chosen,";torsionBound=",best,";baseModulus=",modulus,";");
print("COMPLETE 16215 quotient-count inputs; no original degree scan.");
