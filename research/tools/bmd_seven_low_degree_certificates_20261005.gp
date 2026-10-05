\\ Complete remaining-prime certificates for n7,d2,3,4, using the actual root-polynomial source.
\\ The proved large-characteristic cutoff is p>64d. Reuse the existing p3,d2 coface certificate.
\\ Cache all relevant character prefixes once per admissible point; stop each case at its first nonzero determinant.
default(parisizemax,3000000000);
default(threadsize,64000000);
default(threadsizemax,512000000);
default(nbthreads,1);
setrand(20261005);
if(default(nbthreads)!=1,quit(1));
assert(c,s)={if(!c,error(s));};
source_columns(d)={
 my(cols=List());
 for(mask=0,127,if(hammingweight(mask)<=d,
  for(columnShift=0,(d-hammingweight(mask))\2,listput(cols,[mask,columnShift]));
 ));
 return(Vec(cols));
};
prefixes(roots,N)={
 my(o=polcoef(roots[1],0,T),products=vector(128),coefs=vector(128));
 products[1]=o+O(T^N);coefs[1]=vector(N,j,if(j==1,o,0*o));
 for(mask=1,127,if(hammingweight(mask)<=4,
  my(bit=valuation(mask,2),previous=mask-2^bit);
  products[mask+1]=products[previous+1]*roots[bit+1];
  coefs[mask+1]=vector(N,j,polcoef(products[mask+1],j-1,T));
 ));
 return(coefs);
};
marked(coefs,cols,N,o)={
 return(matrix(N,N,i,j,if(i<=cols[j][2],0*o,coefs[cols[j][1]+1][i-cols[j][2]])));
};
{
my(dims=[30,72,129],cols=vector(3,j,source_columns(j+1)),counts=vector(3,j,0),expected=0,certified=0,negative_done=0);
for(j=1,3,assert(#cols[j]==dims[j],"actual source dimensions"));
forprime(p=3,256,for(d=2,4,if(p<=64*d && !(p==3 && d==2),expected++;counts[d-1]++)));
assert(expected==124 && counts==[29,42,53],"complete bounded characteristic inventory");
print("TARGET n=7 degrees=[2,3,4] dimensions=",dims," cutoffs=[128,192,256] new_cases=",expected," per_degree=",counts," reused=(p3,d2) seed=20261005 threads=",default(nbthreads));
forprime(p=3,256,
 my(remaining=select(d->p<=64*d && !(p==3 && d==2),[2,3,4]),e=1);
 if(#remaining==0,next);
 while(p^e<4096,e++);
 my(modulus=ffinit(p,e,'a),g=ffgen(modulus,'a),o=g^0);
 print("FIELD p=",p," extension_degree=",e," modulus=",modulus);
 for(trial=1,4,
  if(#remaining==0,break);
  my(slopes=vector(7,i,random(g)));
  while(#Set(slopes)!=7 || prod(i=1,7,slopes[i])==0,slopes=vector(7,i,random(g)));
  my(ell=vector(7,i,o+slopes[i]*T+O(T^129)),roots=apply(sqrt,ell));
  for(i=1,7,assert(polcoef(roots[i],0,T)==o && valuation(roots[i]^2-ell[i],T)>=129,"actual normalized square-root prefixes"));
  my(coefs=prefixes(roots,129),pending=List());
  print("POINT p=",p," trial=",trial," slopes=",slopes);
  for(j=1,#remaining,
   my(d=remaining[j],N=dims[d-1],J=marked(coefs,cols[d-1],N,o),value=matdet(J));
   if(value==0,
    listput(pending,d);print("RETRY p=",p," d=",d," N=",N," determinant=0");
   ,
    certified++;print("CERTIFIED p=",p," d=",d," N=",N," determinant=",value);
   );
  );
  if(!negative_done,
   my(badroots=roots);badroots[7]=badroots[6];
   my(badcoefs=prefixes(badroots,72),bad=marked(badcoefs,cols[2],72,o));
   assert(matdet(bad)==0,"repeated-root negative control must be singular");
   negative_done=1;print("NEGATIVE CONTROL p=",p," d=3 repeated last two slopes: determinant=0 PASS");
  );
  remaining=Vec(pending);
 );
 assert(#remaining==0,"not every remaining characteristic was certified");
);
assert(certified==expected && negative_done,"complete certificate coverage");
print("PASS: all ",certified," new cases certified; combine the reused p3,d2 certificate and p>64d theorem.");
}
quit;
