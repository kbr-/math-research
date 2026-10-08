\\ Test the original first bulk degree n9,p3,d7 on the already counted F27 curve.
\\ A nonzero determinant plus the archived torsion annihilator proves a full progression.
\\ Exactly one degree/point; zero means this specialization is inconclusive.
\\ Stages: cached roots/subsets; complete 1024-square source; determinant; corruption control.
\\ Prior original 769-square certificates took 5s for four degrees over F_(3^8).
\\ Cubic sizing gives under 15s here; no growing degree series is launched.
default(parisizemax,2000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(n=9,d=7,p=3,N=1024,modulus=Mod(1,3)*(a^3+2*a+2),aa=ffgen(modulus,'a),one=aa^0,labels=vector(n,i,aa^(i-1)));
assert(default(nbthreads)==1,"one native thread");
assert(#Set(labels)==n && prod(i=1,n,labels[i])!=0,"distinct nonzero labels");
my(start=getwalltime(),ell=vector(n,i,one+labels[i]*T+O(T^N)),roots=apply(sqrt,ell));
for(i=1,n,assert(polcoef(roots[i],0,T)==one && valuation(roots[i]^2-ell[i],T)>=N,"unique normalized root"));
my(products=vector(2^n),coefs=vector(2^n),columns=List());
products[1]=one+O(T^N);coefs[1]=vector(N,j,if(j==1,one,0*one));
for(S=0,2^n-1,
 if(hammingweight(S)<=d,
  if(S>0,my(bit=valuation(S,2));products[S+1]=products[S-2^bit+1]*roots[bit+1];coefs[S+1]=vector(N,j,polcoef(products[S+1],j-1,T)));
  for(j=0,(d-hammingweight(S))\2,listput(columns,[S,j]))
 )
);
my(cols=Vec(columns));assert(#cols==N && N==2^(n-1)*(d-3),"complete nonspecial source count");
my(M=matrix(N,N,i,j,if(i<=cols[j][2],0*one,coefs[cols[j][1]+1][i-cols[j][2]])));
print("FIRST_BULK n=",n," p=",p," d=",d," N=",N," modulus=",modulus," labels=",labels);
print("SOURCE_READY wall_ms=",getwalltime()-start," estimated_determinant_seconds_under=15");
my(ds=getwalltime(),value=matdet(M));
print("ORIGINAL_DETERMINANT=",value," determinant_wall_ms=",getwalltime()-ds);
if(value!=0,
 M[,2]=M[,1];assert(matdet(M)==0,"duplicated-column corruption control");
 print("CORRUPTION_CONTROL duplicate source column gives zero determinant");
 print("FIRST_BULK_CERTIFIED d=7; archived annihilator may propagate after proof review")
,
 print("FIRST_BULK_INCONCLUSIVE: zero only at this finite-field mark, not a generic exception")
);
print("FIRST_BULK_TEST_COMPLETED wall_ms=",getwalltime()-start);
}
quit;
