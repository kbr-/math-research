\\ Exact rational residue profiles for p large enough to preserve the displayed pivots.
\\ D residues comprise five nonconsecutive states, two marked-origin zeros, and exceptional D=5.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(states=[0,1,1/2,-1/2,3/2,-3/4,-5/4,5],rr=[1,3,5]);
for(si=1,#states,
 my(r=states[si],q=2*r+1,C=matrix(3,6,i,j,binomial(q-j+1,rr[i])),piv=List(),rk=0);
 for(j=1,6,my(ix=concat(Vec(piv),[j]),B=matrix(3,#ix,i,k,C[i,ix[k]]),nr=matrank(B));if(nr>rk,listput(piv,j);rk=nr);if(rk==3,break));
 assert(rk==3,"six-column rational rank");
 my(PV=Vec(piv),B=matrix(3,3,i,j,C[i,PV[j]]),co=B^-1*C,off=PV-vector(3,j,1),wid=vecmax(off),out=List());
 for(j=1,6,for(k=1,3,if(j<PV[k],assert(co[k,j]==0,"skipped-column greedy pivot certificate"))));
 for(j=0,wid-1,if(!setsearch(Set(off),j),listput(out,1-j)));
 print("r=",r," A_main_offset=",3-wid," A_outliers=",Vec(out)," pivot_offsets=",off," selected_det=",matdet(B)," coordinates=",co);
);
my(D=5,c=D+1,q=2*c+1,P=9,xp=sqrt(1+ep+O(ep^P)),Y=-xp-1,C=matrix(3,q+1,i,j,(-1)^(j-1-rr[i])*binomial(j-1,rr[i])),PV=[q+1,q,q-1],Inv=matrix(3,3,i,j,C[i,PV[j]])^-1,E=vector(2*D+1,j,j-1),top=2*D,tail=select(e->e>top-P,E),R=matrix(2,#tail));
for(j=1,#tail,
 my(e=tail[j],aa=Inv*C[,e+1],f=Y^e,fp=e*Y^(e-1));
 for(k=1,3,f-=aa[k]*Y^(PV[k]-1);fp-=aa[k]*(PV[k]-1)*Y^(PV[k]-2));
 R[1,j]=2^e*ep^(top-e)*f;R[2,j]=2^e*ep^(top-e)*fp;
);
my(v1=vecmin(vector(#tail,j,valuation(R[1,j],ep))),j1=0);
for(j=1,#tail,if(valuation(R[1,j],ep)==v1,j1=j;break));
for(j=1,#tail,R[1,j]/=ep^v1);
my(pivot=R[1,j1],lead1=polcoef(pivot,0,ep));for(j=1,#tail,R[1,j]/=pivot);
my(mult=R[2,j1]);for(j=1,#tail,R[2,j]-=mult*R[1,j]);
my(v2=vecmin(vector(#tail,j,valuation(R[2,j],ep))));assert(v1+v2<P,"complete primitive precision");
for(j=1,#tail,R[2,j]/=ep^v2);
my(LC=matrix(2,#tail,i,j,polcoef(R[i,j],0,ep)));assert(matrank(LC)==2,"independent exceptional domain constraints");
print("EXCEPTION D=5 ambient_det=",1/matdet(Inv)," tail_offsets=",tail-vector(#tail,j,2*D)," row_orders=",[v1,v2]," first_leading=",lead1," constraints=",LC);
print("PASS rational profile pivots and complete exceptional opposite-point constraints.");
}
quit;
