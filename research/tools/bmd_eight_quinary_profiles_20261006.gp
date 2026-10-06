\\ Full characteristic-five conic core profiles for all d>=6.
\\ Ordinary missing coefficients1,3,5; exceptional domain has two opposite-point rows.
\\ Test every local state (period25), not additional original-degree normality samples.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
core_basis(c)={
 my(q=2*c+1,rr=[1,3,5],C=matrix(3,q+1,i,j,Mod((-1)^(j-1-rr[i])*binomial(j-1,rr[i]),5)),piv=List(),rk=0);
 forstep(j=q,q-9,-1,
  my(ix=concat(Vec(piv),[j+1]),A=matrix(3,#ix,i,k,C[i,ix[k]]),nr=matrank(A));
  if(nr>rk,listput(piv,j+1);rk=nr);if(rk==3,break);
 );
 assert(rk==3,"ten-column pivot bound");
 my(PV=Vec(piv),Inv=matrix(3,3,i,j,C[i,PV[j]])^-1,E=select(e->!setsearch(Set(PV),e+1),vector(q+1,j,j-1)));
 [E,C,PV,Inv];
};
ordinary(D)={my(a=core_basis(D),E=a[1],lo=0);while(setsearch(Set(E),lo),lo++);[lo+2,select(e->e>=lo,E)];};
OUT=getenv("OUT");assert(OUT!="" && OUT!=0,"OUT required");
{
my(P=25,o=Mod(1,5),xp=(o+ep+O(ep^(P+2)))^63,Y=-xp-1,profiles=vector(25),exceptional=List());
for(d=6,30,
 my(D=16*d-41,A=ordinary(D),B=[]);
 if(d%5==1,
  my(c=D+1,co=core_basis(c),E=co[1],C=co[2],PV=co[3],Inv=co[4],top=E[#E],tail=select(e->e>top-P,E),R=matrix(2,#tail),zt=o+ep+O(ep^(P+2)),be=Mod(3,5)+4*ep/zt,zpowers=vector(c+1));
  zpowers[1]=o;for(k=2,c+1,zpowers[k]=zpowers[k-1]*zt);
  assert(top-1>P,"discarded positive-point and remainder terms");
  for(j=1,#tail,
   my(e=tail[j],aa=Inv*C[,e+1],f=Y^e,fp=e*Y^(e-1));
   for(k=1,3,f-=aa[k]*Y^(PV[k]-1);fp-=aa[k]*(PV[k]-1)*Y^(PV[k]-2));
   R[1,j]=o*2^e*ep^(top-e)*f;R[2,j]=o*2^e*ep^(top-e)*fp;
   my(fpoly=o*2^e*((X-1)^e-sum(k=1,3,aa[k]*(X-1)^(PV[k]-1))));
   for(k=1,3,assert(polcoef(fpoly,[1,3,5][k],X)==0,"actual core monomial constraint"));
   my(Ae=sum(k=0,c,polcoef(fpoly,2*k,X)*zpowers[k+1]),Ce=sum(k=0,c-3,polcoef(fpoly,7+2*k,X)*zpowers[k+1]),dAe=sum(k=1,c,if(k%5 && polcoef(fpoly,2*k,X)!=0,polcoef(fpoly,2*k,X)*k*ep*zpowers[k],Mod(0,5))));
   my(ref1=ep^(top-e)*(-2*xp^7)*Ce,ref2=ep^(top-e)*(-4*xp/ep)*(dAe-be*Ae-be*xp^7*Ce));
   assert(valuation(R[1,j]-ref1,ep)>=P && valuation(R[2,j]-ref2,ep)>=P,"direct original-domain row transformation");
  );
  my(v1=vecmin(vector(#tail,j,valuation(R[1,j],ep))),j1=0);assert(v1<P,"first row unresolved");
  for(j=1,#tail,if(valuation(R[1,j],ep)==v1,j1=j;break));
  for(j=1,#tail,R[1,j]/=ep^v1);
  my(pivot=R[1,j1]);for(j=1,#tail,R[1,j]/=pivot);
  my(mult=R[2,j1]);for(j=1,#tail,R[2,j]-=mult*R[1,j]);
  my(v2=vecmin(vector(#tail,j,valuation(R[2,j],ep))));assert(v1+v2<P,"primitive divisions within retained precision");
  for(j=1,#tail,R[2,j]/=ep^v2);
  my(LC=matrix(2,#tail,i,j,polcoef(R[i,j],0,ep)));assert(matrank(LC)==2,"full limiting constraint rank");
  my(lo=0,Es=Set(E),ts=Set(tail));
  while(setsearch(Es,lo),my(ix=setsearch(ts,lo));if(ix && LC[,ix]!=[0,0]~,break);lo++);
  my(high=select(e->e>=lo,E),H=matrix(2,#high,i,j,my(ix=setsearch(ts,high[j]));if(ix,LC[i,ix],0*o)),Ker=matker(H),outliers=vector(matsize(Ker)[2],j,sum(k=1,#high,Ker[k,j]*T^high[k])));
  B=[lo+2,outliers];assert(B[1]+1+#outliers==2*D+2,"exceptional full source dimension");
  print("EXCEPTION dmod25=",d%25," Dmod25=",D%25," ambient_pivot_offsets=",vector(3,j,PV[j]-1-2*D)," tail_offsets=",tail-vector(#tail,j,2*D)," row_orders=",[v1,v2]," constraints=",LC);
  listput(exceptional,[d%25,v1,v2]);
 );
 assert(A[1]+1+#A[2]==2*D+2,"ordinary full source dimension");
 my(ap=[A[1]-2*D,vector(#A[2],j,A[2][j]-2*D)],bp=if(#B,[B[1]-2*D,vector(#B[2],j,subst(B[2][j]/T^(2*D-25),T,z))],[]));
 profiles[d%25+1]=[d,D,ap,bp];
 print("PROFILE dmod25=",d%25," Dmod25=",D%25," A_main_offset=",ap[1]," A_outlier_offsets=",ap[2]);
 if(#B,print("B_main_offset=",bp[1]," B_outliers_div_T2Dminus25=",bp[2]));
);
write(OUT,"QUINARY_PROFILES=",profiles,";");
print("PASS all25 ordinary states and five exceptional states; complete profiles written.");
}
quit;
