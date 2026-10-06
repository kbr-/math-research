\\ Controls for the count-based generic normality cutoff and explicit odd boundary cutoff.
\\ These are two new-range source certificates, one boundary certificate and one characteristic-safe face check.
\\ No finite sample substitutes for the uniform proofs.
default(parisizemax,1000000000);
default(nbthreads,1);
setrand(20261006);
x;t=varhigher("t");
assert(c,s)={if(!c,error(s));};
dim(n,d)=sum(s=0,min(n,d),binomial(n,s)*(1+(d-s)\2));
basis(n,d,aa,L)={
 my(o=aa[1]^0,ww=vector(n,i,sqrt(o+aa[i]*t+O(t^L))),out=List(),prodrows=vector(2^n,i,o+O(t^L)));
 for(i=1,n,assert(valuation(ww[i]^2-(o+aa[i]*t),t)>=L,"root equation"));
 for(mask=0,2^n-1,
  my(wt=hammingweight(mask));if(wt>d,next);
  if(mask,my(j=valuation(mask,2));prodrows[mask+1]=prodrows[mask-2^j+1]*ww[j+1]);
  for(q=0,(d-wt)\2,listput(out,t^q*prodrows[mask+1]));
 );
 assert(#out==dim(n,d),"original source count");
 return(matrix(#out,L,i,j,polcoef(out[i],j-1,t)));
};
{
my(cases=[[9,2,79],[9,3,211]]);
for(z=1,#cases,
 my(n=cases[z][1],d=cases[z][2],p=cases[z][3],N=dim(n,d),bound=2*dim(n-1,d)-2,old=2^(n-1)*d,modulus=ffinit(p,2,'a),a=ffgen(modulus,'a),slopes=vector(n,i,random(a)),attempt=0,detvalue=0);
 assert(p>bound && p<=old,"strictly new cutoff range");
 while(attempt<3 && detvalue==0,
  while(#Set(concat([0],slopes))!=n+1,slopes=vector(n,i,random(a)));
  detvalue=matdet(basis(n,d,slopes,N));attempt++;if(detvalue==0,slopes=vector(n,i,random(a)));
 );
 assert(detvalue!=0,"generic certificate in the predicted new range");
 print("NORMALITY n=",n," d=",d," p=",p," dimension=",N," new_bound=",bound," old_bound=",old," tries=",attempt);
 print("FIELD=",modulus," slopes=",slopes," determinant=",detvalue);
);
my(n=4,N=n+1,p=23,m=dim(n,2),lambda=3*binomial(N,4),cutoff=max(N*(N-1)+1,lambda),modulus=ffinit(p,4,'b),b=ffgen(modulus,'b),o=b^0,al=vector(n,i,random(b)),be=vector(n,i,random(b)),slopes=vector(n,i,al[i]+be[i]*x),M=basis(n,2,slopes,m+1),D=matdet(matrix(m,m,i,j,M[i,j])),Dp=matdet(matrix(m,m,i,j,if(j<m,M[i,j],M[i,m+1]))),aa=concat([0*o],slopes),V=prod(i=1,N,prod(j=i+1,N,aa[j]-aa[i])),full=N*binomial(N,2)+lambda);
assert(p>cutoff,"boundary cutoff");
assert(poldegree(D,x)==full && poldegree(V,x)==binomial(N,2),"full-degree line");
assert(poldegree(gcd(D,Dp),x)==N*binomial(N,2),"boundary primitive-minor certificate");
print("BOUNDARY n=",n," p=",p," cutoff=",cutoff," order=",m," threshold=",lambda," determinant_degree=",poldegree(D,x)," gcd_degree=",poldegree(gcd(D,Dp),x));
print("FIELD=",modulus," line_intercept=",al," line_direction=",be);
my(mm=3,r=3);
for(ci=1,2,
 my(pp=if(ci==1,23,3),one=Mod(1,pp),gamma=vector(r+2*mm+1,j,one*binomial(-3/2,j-1)),H=matrix(2*mm+1,2*mm+1));
 for(j=0,2*mm,
  my(k=r+j);
  for(i=0,mm-1,H[i+1,j+1]=gamma[i+1]*gamma[k-i+1];H[mm+i+1,j+1]=gamma[i+1]*gamma[k-i+1]*x^(k-i));
  H[2*mm+1,j+1]=sum(i=0,k,gamma[i+1]*gamma[k-i+1]*x^i);
 );
 my(detH=matdet(H),hr=sum(i=0,r,gamma[i+1]*gamma[r-i+1]*x^i));
 if(ci==1,
  my(qr=divrem(detH,x^(mm*(r+1))*(x-1)^(mm^2)*hr,x));
  assert(qr[2]==0 && poldegree(qr[1],x)==0 && qr[1]!=0,"unit face scalar");
  assert(poldegree(gcd(hr,deriv(hr,x)),x)==0 && subst(hr,x,0)!=0 && subst(hr,x,1)!=0,"noncollision simplicity after reduction");
  print("FACE p=23 m=3 r=3 unit=",qr[1]," residual=",hr),
  assert(detH==0,"negative control: small-prime zero cross row");print("FACE p=3 negative control determinant zero")
 );
);
print("PASS all new-range, boundary, reduced-face and negative controls.");
}
quit;
