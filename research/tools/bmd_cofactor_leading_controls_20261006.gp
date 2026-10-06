\\ Complete cofactor-leading identity on actual degree-two sources, not normality sampling.
\\ Also checks that the first Catalan-support adjustment still collapses at n7,p3.
default(nbthreads,1);
x;T;
assert(c,s)={if(!c,error(s));};
bin(k)=if(k<0,0,binomial(1/2,k));
{
my(cases=0,checked=0,nonzero=0,primes=[0,3,5]);
for(pi=1,#primes,
 my(p=primes[pi],o=1,g=2);if(p,g=ffgen(ffinit(p,2,'g),'g);o=g^0);
 for(n=2,4,
  my(r=2+n*(n-1)/2,s=n,m=r+s,slopes=vector(n-1,i,g^i),roots=vector(n-1,i,sqrt(o+slopes[i]*T+O(T^(m+1)))),erows=List([o+O(T^(m+1)),o*T+O(T^(m+1))]),frows=List([o+O(T^(m+1))]));
  assert(#Set(concat([0],slopes))==n,"distinct old slopes");
  for(i=1,n-1,listput(erows,roots[i]);listput(frows,roots[i]));
  for(i=1,n-1,for(j=i+1,n-1,listput(erows,roots[i]*roots[j])));
  assert(#erows==r && #frows==s,"full actual row inventory");
  my(E=matrix(r,m+1,i,j,polcoef(erows[i],j-1,T)),F=matrix(s,m+1,i,j,polcoef(frows[i],j-1,T)),C=matrix(m+1,m+1,i,j,if(j>=i,o*bin(j-i)*x^(j-i),0)),M=matconcat([E;F*C]),deltaF=matdet(matrix(s,s,i,j,F[i,j])));
  for(j=0,m,
   my(I=select(k->k!=j,vector(m+1,k,k-1)),L=I[1..r],K=I[r+1..m],degree=s*(r+1));
   if(j>r,degree=r*s+m-j);
   my(tau=matdet(matrix(s,s,u,v,o*bin(K[v]-(u-1)))),pred=matdet(matrix(r,r,u,v,E[u,L[v]+1]))*deltaF*tau,actual=matdet(matrix(m,m,u,v,M[u,I[v]+1])));
   assert(poldegree(actual,x)<=degree,"nominal degree upper bound");
   assert(polcoef(actual,degree,x)==pred,"full cofactor leading coefficient");
   checked++;if(pred!=0,nonzero++);
  );
  print("PASS p=",p," n=",n," r=",r," s=",s," cofactors=",m+1);cases++;
 );
);
my(o=Mod(1,3),r=23,s=7,m=30,J=select(k->o*bin(k)!=0,vector(m+1,k,k-1)));
J=J[1..s];assert(J==[0,1,2,3,4,5,9],"first seven allowed exponents");
assert(sum(i=1,s,J[i])-s*(s-1)/2==3,"first support degree loss");
for(k=19,26,assert(o*bin(k)==0,"missing transfer block"));
for(j=0,m,
 my(I=select(k->k!=j,vector(m+1,k,k-1)),K=I[r+1..m],tau=matrix(s,s,u,v,o*bin(K[v]-J[u])));
 assert(vecsum(vector(s,v,tau[5,v]!=0))==0,"entire transfer row at exponent4 is zero");
 assert(matdet(tau)==0,"all support-adjusted candidate cofactor coefficients collapse");
);
assert(o*bin(6)==0,"ternary nominal common factor");
print("PASS cases=",cases," all_cofactors=",checked," nonzero_predictions=",nonzero);
print("PASS n7,p3: J=[0,1,2,3,4,5,9], loss3, all31 adjusted transfer minors zero.");
}
quit;
