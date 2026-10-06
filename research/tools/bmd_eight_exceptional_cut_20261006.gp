\\ Three complete residue states of the exceptional conic cut, if precision9 suffices.
\\ The two constraints on the known saturated ambient basis reduce in high columns
\\ to evaluation and derivative at X=-sqrt(1+epsilon), up to invertible row factors.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(P=9,x=(Mod(1,3)+ep+O(ep^P))^14,Y=-x-1,rr=[1,3,5]);
for(cs=1,3,
 my(d=[7,10,13][cs],D=16*d-41,c=D+1,q=2*c+1,C=matrix(3,q+1,i,j,Mod((-1)^(j-1-rr[i])*binomial(j-1,rr[i]),3)),piv=List(),rank=0);
 forstep(j=q,q-8,-1,
  my(ix=concat(Vec(piv),[j+1]),B=matrix(3,#ix,i,k,C[i,ix[k]]),rk=matrank(B));
  if(rk>rank,listput(piv,j+1);rank=rk);
  if(rank==3,break);
 );
 assert(rank==3,"known ambient cuts need more than nine offsets");
 my(PV=Vec(piv),B=matrix(3,3,i,j,C[i,PV[j]]),E=select(e->!setsearch(Set(PV),e+1),vector(q+1,j,j-1)),top=E[#E],tail=select(e->e>top-P,E),R=matrix(2,#tail));
 my(zt=Mod(1,3)+ep+O(ep^(P+1)),xp=zt^14,be=Mod(1,3)+ep/zt,zpowers=vector(c+1));zpowers[1]=Mod(1,3);for(k=2,c+1,zpowers[k]=zpowers[k-1]*zt);
 for(j=1,#tail,
  my(e=tail[j],a=B^-1*C[,e+1],f=Y^e,fp=e*Y^(e-1));
  for(k=1,3,f-=a[k]*Y^(PV[k]-1);fp-=a[k]*(PV[k]-1)*Y^(PV[k]-2));
  R[1,j]=Mod(2,3)^e*ep^(top-e)*f;
  R[2,j]=Mod(2,3)^e*ep^(top-e)*fp;
  my(fpoly=Mod(2,3)^e*((X-1)^e-sum(k=1,3,a[k]*(X-1)^(PV[k]-1))));
  for(k=1,3,assert(polcoef(fpoly,rr[k],X)==0,"actual core coefficient cut"));
  my(Ae=sum(k=0,c,polcoef(fpoly,2*k,X)*zpowers[k+1]),Ce=sum(k=0,c-3,polcoef(fpoly,7+2*k,X)*zpowers[k+1]),dAe=sum(k=1,c,if(k%3 && polcoef(fpoly,2*k,X)!=0,polcoef(fpoly,2*k,X)*k*ep*zpowers[k],Mod(0,3))));
  my(ref1=ep^(top-e)*(-2*xp^7)*Ce,ref2=ep^(top-e)*(-4*xp/ep)*(dAe-be*Ae-be*xp^7*Ce));
  assert(valuation(R[1,j]-ref1,ep)>=P && valuation(R[2,j]-ref2,ep)>=P,"direct original-constraint row transformation");
 );
 my(v1=vecmin(vector(#tail,j,valuation(R[1,j],ep))),j1=0);
 assert(v1<P,"first row unresolved");
 for(j=1,#tail,if(valuation(R[1,j],ep)==v1,j1=j;break));
 for(j=1,#tail,R[1,j]/=ep^v1);
 my(pivot=R[1,j1]);for(j=1,#tail,R[1,j]/=pivot);
 my(mult=R[2,j1]);for(j=1,#tail,R[2,j]-=mult*R[1,j]);
 my(v2=vecmin(vector(#tail,j,valuation(R[2,j],ep))));
 assert(v2<P-v1,"second row needs more coefficient precision");
 for(j=1,#tail,R[2,j]/=ep^v2);
 my(LC=matrix(2,#tail,i,j,polcoef(R[i,j],0,ep)));
 assert(matrank(LC)==2,"primitive constraint rows independent");
 print("dmod9=",d%9," Dmod9=",D%9," core_top=",top," ambient_pivots=",PV-vector(3,j,1)," tail_offsets=",vector(#tail,j,tail[j]-2*D)," row_orders=",[v1,v2]," limit_constraints=",LC);
 print("PASS bounded exceptional cuts and direct original-constraint identities for residue ",d%9);
);
}
quit;
