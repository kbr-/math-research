\\ Exact fourth-merge profiles from three/four coefficient cuts, then
\\ Hasse normality controls on the actual full conic limit, not a surrogate.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
profile(c,m,p)={
 my(q=2*c+7-2*m,rr=if(m==3,[1,3,5],[1,3,5,2*c+2]),P=List(),C=matrix(#rr,q+1,i,j,Mod(binomial(j-1,rr[i]),p)),old=0);
 forstep(j=q,0,-1,
  my(trial=concat(Vec(P),[j+1]),nr=matrank(matrix(#rr,#trial,i,k,C[i,trial[k]])));
  if(nr>old,listput(P,j+1);old=nr);
  if(old==#rr,break);
 );
 assert(old==#rr,"constraint independence");
 my(E=select(j->!setsearch(Set(Vec(P)),j+1),vector(q+1,i,i-1)));
 assert(#E==2*c-m+2,"profile dimension");
 \\ Independent x-monomial basis, shifted to x=1, against exact constraints.
 my(ee=concat(vector(c+1,j,2*(j-1)),vector(c-m+1,j,7+2*(j-1))),Z=matrix(#ee,q+1,i,j,Mod(binomial(ee[i],j-1),p)));
 my(Signed=matrix(#rr,q+1,i,j,(-1)^(j-1-rr[i])*C[i,j]));
 assert(matrank(Z)==#ee && Signed*Z~==matrix(#rr,#ee),"source/cut kernel mismatch");
 return([E,vector(#P,i,P[i]-1)]);
};
{
my(cases=[[5,3],[5,5],[5,7],[5,11],[7,3]]);
for(k=1,#cases,
 my(d=cases[k][1],p=cases[k][2],c=8*d-17,m=2*c+2,N=4*m,AA=profile(c,3,p),BB=profile(c,2,p));
 my(g=ffgen(p^6,'a),o=g^0,passed=0);
 print("d=",d," p=",p," c=",c," A_missing=",AA[2]," B_missing=",BB[2]," A_max=",AA[1][#AA[1]]," B_max=",BB[1][#BB[1]]);
 for(trial=1,2,
  my(u=random(g));while(u==0 || u^4==o,u=random(g));
  my(L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N),v=sqrt(L),w=sqrt(H));
  my(A=concat([o,T*o,T^2*o],vector(#AA[1],j,L*H^2*T^AA[1][j])),B=concat([o,T*o],vector(#BB[1],j,H^2*T^BB[1][j])),R=List());
  assert(#A==m && #B==m,"full polynomial profile dimensions");
  for(j=1,m,listput(R,v*A[j]);listput(R,w^3*A[j]);listput(R,L*B[j]);listput(R,v*w^3*B[j]));
  my(rank=matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))));
  print("  trial=",trial," u=",u," N=",N," rank=",rank," corank=",N-rank);
  if(rank==N,passed=1;break);
 );
 print("  certified_at_a_mark=",passed);
);
print("DONE: exact profiles; nonzero marks certify only the listed cases, failures do not prove generic failure.");
}
quit;
