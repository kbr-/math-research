\\ Complete n9 p3 interval below the d>=7 nonspecial/bulk regime.
\\ Reuses cached-root/subset implementation measured at0.82s for321 rows.
\\ Largest769-row cubic estimate about12s; not a cutoff for the exception set.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261007);
assert(c,s)={if(!c,error(s));};
source_columns(d)={my(cols=List());for(mask=0,511,if(hammingweight(mask)<=d,for(q=0,(d-hammingweight(mask))\2,listput(cols,[mask,q]))));Vec(cols);};
prefixes(roots,N)={
 my(o=polcoef(roots[1],0,T),products=vector(512),coefs=vector(512));
 products[1]=o+O(T^N);coefs[1]=vector(N,j,if(j==1,o,0*o));
 for(mask=1,511,if(hammingweight(mask)<=6,
  my(bit=valuation(mask,2),previous=mask-2^bit);
  products[mask+1]=products[previous+1]*roots[bit+1];
  coefs[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T));
 ));coefs;
};
marked(coefs,cols,N,o)={matrix(N,N,i,j,if(i<=cols[j][2],0*o,coefs[cols[j][1]+1][i-cols[j][2]]));};
{
my(dims=vector(4,j,sum(k=0,j+2,binomial(9,k)*(1+(j+2-k)\2))),cols=vector(4,j,source_columns(j+2)),remaining=[3,4,5,6],certified=0,negative_done=0,modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),o=a^0);
assert(default(nbthreads)==1,"one library thread");
for(j=1,4,assert(#cols[j]==dims[j] && dims[j]==sum(s=0,j+2,binomial(9,s)*(1+(j+2-s)\2)),"actual source count"));
print("TARGET n=9 p=3 degrees=[3,4,5,6] dimensions=",dims," new_cases=4 seed=20261007 threads=",default(nbthreads));
print("FIELD modulus=",modulus," field_size=",3^8);
for(trial=1,4,
 if(#remaining==0,break);
 my(slopes=vector(9,i,random(a)));
 while(#Set(slopes)!=9 || prod(i=1,9,slopes[i])==0,slopes=vector(9,i,random(a)));
 my(ell=vector(9,i,o+slopes[i]*T+O(T^dims[4])),roots=apply(sqrt,ell));
 for(i=1,9,assert(polcoef(roots[i],0,T)==o && valuation(roots[i]^2-ell[i],T)>=dims[4],"normalized square-root equations"));
 my(coefs=prefixes(roots,dims[4]),pending=List());print("POINT trial=",trial," slopes=",slopes);
 for(j=1,#remaining,
  my(d=remaining[j],N=dims[d-2]);print("DETERMINANT_STARTED d=",d," N=",N);my(value=matdet(marked(coefs,cols[d-2],N,o)));
  if(value==0,listput(pending,d);print("RETRY d=",d," N=",N," determinant=0"),certified++;print("CERTIFIED d=",d," N=",N," determinant=",value));
 );
 if(!negative_done,
  my(badroots=roots);badroots[9]=badroots[8];
  assert(matdet(marked(prefixes(badroots,dims[1]),cols[1],dims[1],o))==0,"repeated-root negative control");
  negative_done=1;print("NEGATIVE_CONTROL d=3 repeated slopes: determinant=0 PASS");
 );
 remaining=Vec(pending);
);
assert(#remaining==0 && certified==4 && negative_done,"complete remaining-degree coverage");
print("NINE_INITIAL_INTERVAL_COMPLETED: d3..6 certified; d2 previously proved. All d>=7 outside certified coefficient residues remain unresolved.");
}
quit;
