\\ Exhaustive small encoding controls for all cuts 1<=m<p, p=3,5,7, c=p.
\\ At q=1, tau=x^2-1 and y=x^p. Compare the entire original and normalized basis spans.
\\ Separately check the claimed first variation of the exact rationalized psi.
default(parisizemax,1000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,quit(1));
assert(c,s)={if(!c,error(s));};
{
my(count=0);
forprime(p=3,7,
 my(o=Mod(1,p),c=p,t=1,tau=x^2-o,y=x^p,psi=2*(y-o));
 for(m=1,p-1,
  my(g=(o+tau)^m,raw=concat(vector(c+1,j,g*tau^(j-1)),vector(c+1,j,y*tau^(j-1))),basis=List());
  for(j=0,m-1,listput(basis,y*tau^j));
  for(r=0,p-1,
   my(A=(c-r)\p,B=(c-m-r)\p,K=A+B+1);
   assert(A==B || A==B+1,"complete even/odd y powers");
   for(k=0,K,listput(basis,g*tau^r*psi^k));
  );
  assert(#basis==2*c+2,"dimension count");
  my(bound=max(2*(c+m),2*c+p),R=matrix(bound+1,#raw,i,j,polcoef(raw[j],i-1,x)),B=matrix(bound+1,#basis,i,j,polcoef(basis[j],i-1,x)));
  assert(matrank(R)==#raw && matrank(B)==#raw && matrank(matconcat([R,B]))==#raw,"exact full polynomial spans");
  count++;print("p=",p," cut=",m," c=",c," dimension=",#raw," full_span=PASS");
 );
 \\ Coefficients of q^0,q^1 in psi^k/Z^k, for every local k residue.
 for(k=0,p-1,
  my(h=sqrt(o+q+O(q^3)),b=(2/(o+h))^k);
  assert(polcoef(b,0,q)==o && polcoef(b,1,q)==-k*o/4,"first variation coefficient");
 );
);
print("PASS: ",count," complete source-span controls and every first-variation digit at p3,5,7");
}
quit;
