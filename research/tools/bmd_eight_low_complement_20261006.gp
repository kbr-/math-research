\\ Exact finite complement of all-prime n8 bulk, after the joint-coefficient reduction.
\\ All d>=6 have a reviewed uniform proof; only these four degrees remain.
\\ Adapt the checked n7 source driver, cache one longest prefix per subset.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
assert(c,s)={if(!c,error(s));};
source_columns(d)={my(cols=List());for(mask=0,255,if(hammingweight(mask)<=d,for(q=0,(d-hammingweight(mask))\2,listput(cols,[mask,q]))));Vec(cols);};
prefixes(roots,N,maxd)={
 my(o=polcoef(roots[1],0,T),products=vector(256),coefs=vector(256));
 products[1]=o+O(T^N);coefs[1]=vector(N,j,if(j==1,o,0*o));
 for(mask=1,255,if(hammingweight(mask)<=maxd,
  my(bit=valuation(mask,2),previous=mask-2^bit);
  products[mask+1]=products[previous+1]*roots[bit+1];
  coefs[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T));
 ));coefs;
};
marked(coefs,cols,N,o)={matrix(N,N,i,j,if(i<=cols[j][2],0*o,coefs[cols[j][1]+1][i-cols[j][2]]));};

read("research/results/bmd-eight-low-complement-20261006/inventory.gp");
{
my(dims=[38,102,201,321],cols=vector(4,j,source_columns(j+1)),certified=0,negative_done=0,counts=vector(4,j,0),points=0);
assert(EXPECTED_TOTAL==118 && vector(4,j,#LOW_PRIMES[j])==[10,20,37,51] && #ALL_PRIMES==70,"complete planned finite inventory");
assert(default(nbthreads)==1,"one library thread");
for(j=1,4,assert(#cols[j]==dims[j] && dims[j]==sum(s=0,j+1,binomial(8,s)*(1+(j+1-s)\2)),"actual original-source count"));
print("TARGET n8 degrees2..5 dimensions=",dims," case_counts=[10,20,37,51] total=118 primes=70 seed=20261006");
print("SIZING: same321-prefix driver previously took0.82s for four cases atp5^6;70 points estimate<=60s. No larger degree tested.");
for(pi=1,#ALL_PRIMES,
 my(pp=ALL_PRIMES[pi],remaining=select(d->setsearch(LOW_PRIMES[d-1],pp)>0,[2,3,4,5]),ext=1);
 while(pp^ext<4096,ext++);
 my(modulus=ffinit(pp,ext,'a),a=ffgen(modulus,'a),o=a^0);print("FIELD p=",pp," degree=",ext," modulus=",modulus);
 for(trial=1,4,
  if(#remaining==0,break);
  my(maxd=vecmax(remaining),maxN=dims[maxd-1],slopes=vector(8,i,random(a)));
  while(#Set(slopes)!=8 || prod(i=1,8,slopes[i])==0,slopes=vector(8,i,random(a)));
  my(ell=vector(8,i,o+slopes[i]*T+O(T^maxN)),roots=apply(sqrt,ell));
  for(i=1,8,assert(polcoef(roots[i],0,T)==o && valuation(roots[i]^2-ell[i],T)>=maxN,"normalized square-root equations"));
  my(coefs=prefixes(roots,maxN,maxd),pending=List());points++;print("POINT p=",pp," trial=",trial," slopes=",slopes);
  for(j=1,#remaining,
   my(d=remaining[j],N=dims[d-1],value=matdet(marked(coefs,cols[d-1],N,o)));
   if(value==0,listput(pending,d);print("RETRY p=",pp," d=",d," N=",N," determinant=0"),certified++;counts[d-1]++;print("CERTIFIED p=",pp," d=",d," N=",N," determinant=",value));
  );
  if(!negative_done,
   my(badroots=roots);badroots[8]=badroots[7];
   assert(matdet(marked(prefixes(badroots,102,3),cols[2],102,o))==0,"repeated-root negative control");
   negative_done=1;print("NEGATIVE_CONTROL p=",pp," d=3 repeated slopes: determinant=0 PASS");
  );
  remaining=Vec(pending);
 );
 assert(#remaining==0,"every planned degree certified at current prime");
);
assert(certified==EXPECTED_TOTAL && counts==[10,20,37,51] && negative_done,"complete finite complement");
print("PASS certified=",certified," counts=",counts," points=",points," no larger degree or already proved prime-degree pair sampled.");
}
quit;
