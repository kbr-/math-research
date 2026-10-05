\\ Independent full-source, ambient-kernel and finite-row control of the third survivor.
\\ Smallest c=5 mod9: d5,p3,N192. This checks the encoding, not extrapolated degrees.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
{
my(d=5,p=3,c=8*d-17,q=2*c+1,N=4*(q+1),M=N/2+6,g=ffgen(p^6,'a),o=g^0);
my(u=random(g));while(u==0 || u^4==o,u=random(g));
my(L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N),v=sqrt(L),w=sqrt(H),rows=List());
for(e=0,q,
 listput(rows,v*T^e);listput(rows,L*T^e);
 listput(rows,w^7*T^e);listput(rows,v*w^7*T^e);
);
my(rank=matrank(matrix(N,N,i,j,polcoef(rows[i],j-1,T))));
print("d=",d," p=",p," c=",c," u=",u," N=",N," direct_rank=",rank);
my(s=u^2+u^-2,quad=z^4-s*z^2+o,powers=vector(q+1),bases=List());
powers[1]=o;for(e=1,q,powers[e+1]=powers[e]*quad);
for(e=0,q,
 listput(bases,[1,0,e]);listput(bases,[2,0,e]);
 listput(bases,[0,7,e]);listput(bases,[1,7,e]);
);
my(polys=vector(N,j,z^(M-bases[j][1]-bases[j][2]-2*bases[j][3])
                  *(z^2+o)^bases[j][1]*(z^2-o)^bases[j][2]*powers[bases[j][3]+1]));
my(S=matrix(2*M+1,N,i,j,polcoef(polys[j],i-1,z)),Phi=matrix(13,2*M+1,i,j,0*o),ii=sqrt(-o),rr=0);
for(sg=0,1,
 my(a=(1-2*sg)*o);
 forstep(hh=1,5,2,
  rr++;
  for(j=0,2*M,
   my(ell=j-M);
   Phi[rr,j+1]=(binomial(ell,hh)-binomial(-ell,hh))*a^(ell-hh);
  );
 );
);
rr++;for(j=0,2*M,Phi[rr,j+1]=ii^(j-M)+(-ii)^(j-M));
for(r=0,5,rr++;Phi[rr,2*M-r+1]=o;Phi[rr,r+1]=o);
assert(rr==13 && matrank(Phi)==13,"independent thirteen ambient cuts");
assert(matrank(S)==N && Phi*S==matrix(13,N),"full source equals condition kernel");
my(marked=(z-u)^N,K=matrix(2*M+1,13,i,j,polcoef(marked*z^(j-1),i-1,z)),DK=Phi*K,small=matrix(13,13,i,j,0*o));
rr=0;
for(sg=0,1,
 my(a=(1-2*sg)*o);
 forstep(hh=1,5,2,
  rr++;
  for(j=0,12,
   my(val=0*o);
   for(k=0,hh,
    val+=Mod(binomial(3,k),p)*(a-u)^(hh-k)
       *(a^k*Mod(binomial((j-3)%9,hh-k),p)-(-u)^k*Mod(binomial((-j)%9,hh-k),p));
   );
   small[rr,j+1]=a^(j+hh)*val;
   assert(small[rr,j+1]==(a-u)^(hh-N)*DK[rr,j+1],"normalized odd-part Hasse row");
  );
 );
);
my(C=u^N,X=(u-ii)^N+(u+ii)^N,Y=ii*((u-ii)^N-(u+ii)^N));
for(j=0,12,small[7,j+1]=[X,Y,-X,-Y][j%4+1];assert(small[7,j+1]==-DK[7,j+1],"i-row sign"));
for(r=0,5,
 for(j=0,12,
  my(vh=0*o,vl=0*o,kh=r-12+j,kl=r-j);
  if(kh>=0,vh=Mod(binomial(3,kh),p)*(-u)^kh);
  if(kl>=0,vl=C*Mod(binomial(3,kl),p)*(-u)^(-kl));
  small[8+r,j+1]=vh+vl;
  assert(small[8+r,j+1]==DK[8+r,j+1],"high reciprocal-plus row");
 );
);
my(smallrank=matrank(small));
assert(smallrank==13 && rank==N,"normality control");
my(predicted=(u^6-1)/u^9*(C+u^3)*(C-u^3)*(-u^3*C*X+C*Y+u^3*X+u^6*Y)*(u^6*C+1)^3);
assert(matdet(small)==predicted,"fixed symbolic determinant evaluated independently");
print("ambient_source_rank=",N," condition_rank=13 marked_rank=",smallrank);
print("PASS: full source, every normalized matrix entry, and determinant identity");
}
quit;
