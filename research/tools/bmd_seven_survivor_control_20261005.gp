\\ Test the two alternative full survivor sources at the smallest p7 obstruction.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
profile(c,m,p,r)={
 my(ee=concat(vector(c+1,j,2*(j-1)),vector(c-m+1,j,r+2*(j-1))),q=vecmax(ee),rr=setminus(Set(vector(q+1,j,j-1)),Set(ee)));
 my(P=List(),C=matrix(#rr,q+1,i,j,Mod(binomial(j-1,rr[i]),p)),old=0);
 forstep(j=q,0,-1,
  my(trial=concat(Vec(P),[j+1]),nr=matrank(matrix(#rr,#trial,i,k,C[i,trial[k]])));
  if(nr>old,listput(P,j+1);old=nr);
  if(old==#rr,break);
 );
 assert(old==#rr,"constraint rank");
 my(E=select(j->!setsearch(Set(Vec(P)),j+1),vector(q+1,i,i-1)));
 assert(#E==#ee,"profile dimension");
 my(Z=matrix(#ee,q+1,i,j,Mod(binomial(ee[i],j-1),p)),Signed=matrix(#rr,q+1,i,j,(-1)^(j-1-rr[i])*C[i,j]));
 assert(matrank(Z)==#ee && Signed*Z~==matrix(#rr,#ee),"source/cut kernel");
 return([E,vector(#P,i,P[i]-1)]);
};

{
my(d=5,p=7,c=8*d-17,m=2*c+2,N=4*m,g=ffgen(p^6,'a),o=g^0);
for(mode=1,2,
 my(cut=if(mode==1,3,1),pow=if(mode==1,7,3),AA=profile(c,cut,p,pow),BB=profile(c,0,p,pow));
 print("mode=",mode," d=",d," p=",p," A_pivots=",AA[2]," B_pivots=",BB[2]," A_orders=",AA[1]," B_orders=",BB[1]);
 for(trial=1,2,
  my(u=random(g));while(u==0 || u^4==o,u=random(g));
  my(L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N),v=sqrt(L),w=sqrt(H));
  my(A=concat(vector(cut,j,o*T^(j-1)),vector(#AA[1],j,L*H^(cut-1)*T^AA[1][j])),B=vector(#BB[1],j,o*T^BB[1][j]),R=List());
  for(j=1,m,
   if(mode==1,
    listput(R,v*A[j]);listput(R,w*A[j]);listput(R,L*H*B[j]);listput(R,v*w^3*B[j]),
    listput(R,v*A[j]);listput(R,w^7*A[j]);listput(R,L*B[j]);listput(R,v*w^7*B[j])
   );
  );
  my(rank=matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))));
  print("mode=",mode," trial=",trial," u=",u," N=",N," rank=",rank," corank=",N-rank);
  if(rank==N,break);
 );
);
print("DONE: smallest falsifying control only; no extrapolation to general degrees.");
}
quit;
