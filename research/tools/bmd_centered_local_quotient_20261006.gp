\\ Exhaustive basis controls for the centered first lift modulo its actual boundary source.
\\ Tests all polynomial basis columns, A=0 endpoint and every characteristic rank-drop branch.
\\ No marked nonvanishing is inferred from a quotient rank.
default(nbthreads,1);
T;s;
assert(c,msg)={if(!c,error(msg));};
{
my(primes=[0,3,5,7],cases=0,columns=0,drops=Set());
for(pi=1,#primes,
 my(p=primes[pi],o=1,a=2,beta=3);
 if(p,my(z=ffgen(ffinit(p,2,'z),'z));o=z^0;a=o;beta=z;print("FIELD p=",p," modulus=",ffinit(p,2,'z)));
 for(h=1,4,for(A=0,4,
  my(b=2*h-1,D=2*A+b,ell=o+a*T,G=(o+beta*T)^(h-1),g=(o-a*s)*(o+(beta-a)*s)^(2*h-2),root=-o/a,G0=subst(G,T,root),Gp=subst(deriv(G,T),T,root));
  assert(G0!=0 && poldegree(g,s)==b,"exact divisor hypothesis");
  my(R=matrix(4,2*(D+1)),predE=if(A==0,0,if(o*A==0 || o*(A-1)==0,1,2)),predO=if(o*D==0 || o*(D-2)==0,1,2));
  for(e=0,D,
   my(P=T^e,tilde=s^e*(o-a*s)^(D-e),P0=root^e,Pp=if(e==0,0,o*e*root^(e-1)),div=divrem(tilde,g,s),B=div[1],op=0);
   for(k=0,2*A,op+=o*(k\2)/16*polcoef(B,k,s)*s^(k+2));op*=g;
   my(r2=0,r1=0);
   if(A>0,r2=o*A*P0/(16*a^2);r1=((-4*A*o+2*Gp/(a*G0))*P0+(A-1)*Pp/a)/(16*a^2));
   my(num=sum(k=0,D+2,polcoef(op,k,s)*T^k*ell^(D+2-k))-r2-r1*ell,qr=divrem(num,ell^2,T));
   assert(qr[2]==0 && poldegree(qr[1],T)<=D,"even local quotient");
   R[1,e+1]=r2;R[2,e+1]=r1;
   op=0;for(k=0,D,op+=o*(2*k-D)/32*polcoef(tilde,k,s)*s^(k+2));
   r2=o*D*P0/(32*a^2);r1=-o*D*P0/(8*a^2)+(D-2)*Pp/(32*a^3);
   num=sum(k=0,D+2,polcoef(op,k,s)*T^k*ell^(D+2-k))-r2-r1*ell;qr=divrem(num,ell^2,T);
   assert(qr[2]==0 && poldegree(qr[1],T)<=D,"odd local quotient");
   R[3,D+2+e]=r2;R[4,D+2+e]=r1;columns+=2;
  );
  assert(matrank(R)==predE+predO,"exact function-quotient rank, not marked rank");
  drops=setunion(drops,Set([[p,predE,predO]]));cases++;
  print("PASS p=",p," h=",h," A=",A," D=",D," quotient_rank=",predE+predO);
 ));
);
print("PASS cases=",cases," basis_columns=",columns," rank_branches=",drops);
}
quit;
