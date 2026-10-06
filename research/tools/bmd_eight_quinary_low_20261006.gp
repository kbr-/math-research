\\ Exact remaining cases for all-degree n8 quinary normality: d2,3,4,5.
\\ All d>=6 have a reviewed uniform proof; only these four degrees remain.
\\ Adapt the checked n7 source driver, cache one longest prefix per subset.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
assert(c,s)={if(!c,error(s));};
source_columns(d)={my(cols=List());for(mask=0,255,if(hammingweight(mask)<=d,for(q=0,(d-hammingweight(mask))\2,listput(cols,[mask,q]))));Vec(cols);};
prefixes(roots,N)={
 my(o=polcoef(roots[1],0,T),products=vector(256),coefs=vector(256));
 products[1]=o+O(T^N);coefs[1]=vector(N,j,if(j==1,o,0*o));
 for(mask=1,255,if(hammingweight(mask)<=5,
  my(bit=valuation(mask,2),previous=mask-2^bit);
  products[mask+1]=products[previous+1]*roots[bit+1];
  coefs[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T));
 ));coefs;
};
marked(coefs,cols,N,o)={matrix(N,N,i,j,if(i<=cols[j][2],0*o,coefs[cols[j][1]+1][i-cols[j][2]]));};
{
my(dims=[38,102,201,321],cols=vector(4,j,source_columns(j+1)),remaining=[2,3,4,5],certified=0,negative_done=0,modulus=ffinit(5,6,'a),a=ffgen(modulus,'a),o=a^0);
assert(default(nbthreads)==1,"one library thread");
for(j=1,4,assert(#cols[j]==dims[j] && dims[j]==sum(s=0,j+1,binomial(8,s)*(1+(j+1-s)\2)),"actual source count"));
print("TARGET n=8 p=5 degrees=[2,3,4,5] dimensions=",dims," new_cases=4 seed=20261006 threads=",default(nbthreads));
print("FIELD modulus=",modulus," field_size=",5^6);
for(trial=1,4,
 if(#remaining==0,break);
 my(slopes=vector(8,i,random(a)));
 while(#Set(slopes)!=8 || prod(i=1,8,slopes[i])==0,slopes=vector(8,i,random(a)));
 my(ell=vector(8,i,o+slopes[i]*T+O(T^321)),roots=apply(sqrt,ell));
 for(i=1,8,assert(polcoef(roots[i],0,T)==o && valuation(roots[i]^2-ell[i],T)>=321,"normalized square-root equations"));
 my(coefs=prefixes(roots,321),pending=List());print("POINT trial=",trial," slopes=",slopes);
 for(j=1,#remaining,
  my(d=remaining[j],N=dims[d-1],value=matdet(marked(coefs,cols[d-1],N,o)));
  if(value==0,listput(pending,d);print("RETRY d=",d," N=",N," determinant=0"),certified++;print("CERTIFIED d=",d," N=",N," determinant=",value));
 );
 if(!negative_done,
  my(badroots=roots);badroots[8]=badroots[7];
  assert(matdet(marked(prefixes(badroots,102),cols[2],102,o))==0,"repeated-root negative control");
  negative_done=1;print("NEGATIVE_CONTROL d=3 repeated slopes: determinant=0 PASS");
 );
 remaining=Vec(pending);
);
assert(#remaining==0 && certified==4 && negative_done,"complete remaining-degree coverage");
print("PASS all four missing degrees certified; no larger degree sampled.");
}
quit;
