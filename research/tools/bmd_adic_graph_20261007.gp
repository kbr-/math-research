\\ Finite-precision branch graph pilot over F3(u), n3, with explicit certificate checks.
\\ All modes retain their full partial state and edge records; only total closure is a certificate.
\\ Exact rational arithmetic is retained here as a checked reference, not a scalable kernel.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
mval(M)={my(v=1000000);for(i=1,matsize(M)[1],for(j=1,matsize(M)[2],if(M[i,j]!=0,v=min(v,valuation(M[i,j],XPAR)))));v};
submat(M,rr,cc)=matrix(#rr,#cc,i,j,M[rr[i],cc[j]]);
selected_kernel(M,rr,cc)={
 my(s=matsize(M)[2],free=select(j->!setsearch(Set(cc),j),[1..s]),K=matrix(s,#free,i,j,if(i==free[j],OO,0*OO)));
 if(#cc && #free,my(Z=-matsolve(submat(M,rr,cc),submat(M,rr,free)));for(i=1,#cc,for(j=1,#free,K[cc[i],j]=Z[i,j])));
 K
};
frame(U)={
 my(k=matsize(U)[2]);if(!k,return(U));
 my(rows=matindexrank(U)[1]);
 if(USE_CANONICAL,rows=improve_pivot(XPAR^max(0,-mval(U))*U,rows,[1..k])[1]);
 my(R=submat(U,rows,[1..k]),Z=U*R^(-1),h=max(0,-mval(Z)));
 if(USE_CANONICAL,assert(h==0,"unsaturated frame after exchanges");my(canon=canonical_rows(Z));assert(#canon==k,"saturated frame reduction");Z=Z*submat(Z,canon,[1..k])^(-1));
 XPAR^h*Z
};
transition(children)={
 my(sizes=apply(U->matsize(U)[2],children),total=vecsum(sizes),off=0,C=matrix(CC,total,i,j,0*OO),H=C);
 for(r=0,PP-1,for(c=1,CC,for(k=1,sizes[r+1],my(v=children[r+1][c,k]^PP);C[c,off+k]=ZZ[c]^r*v;H[c,off+k]=RR[c]^(-1)*r*ZZ[c]^(r-1)*v));off+=sizes[r+1]);
 [matrix(CC,total,i,j,XPAR^if(USE_ROWS,ROWPOW[i],AC)*C[i,j]),XPAR^AH*H]
};

\\ Breadth-first graph pilot; every accepted edge checks the published local bound.
chop(M,N)=matrix(matsize(M)[1],matsize(M)[2],i,j,truncate(M[i,j]+O(XPAR^N)));
improve_pivot(M,rr,cc)={
 if(!USE_PIVOTS || !#rr,return([rr,cc]));
 my(v=valuation(matdet(submat(M,rr,cc)),XPAR),bound=v+1);
 for(step=1,bound,
  my(Ai=submat(M,rr,cc)^(-1),X=Ai*submat(M,rr,[1..matsize(M)[2]]),Y=submat(M,[1..matsize(M)[1]],cc)*Ai,best=0,which=0,ii=0,jj=0);
  for(i=1,matsize(X)[1],for(j=1,matsize(X)[2],if(X[i,j]!=0 && valuation(X[i,j],XPAR)<best,best=valuation(X[i,j],XPAR);which=1;ii=i;jj=j)));
  for(i=1,matsize(Y)[1],for(j=1,matsize(Y)[2],if(Y[i,j]!=0 && valuation(Y[i,j],XPAR)<best,best=valuation(Y[i,j],XPAR);which=2;ii=i;jj=j)));
  if(!which,return([rr,cc]));
  if(which==1,cc[ii]=jj,rr[jj]=ii);
  my(nv=valuation(matdet(submat(M,rr,cc)),XPAR));assert(nv==v+best && nv<v,"Cramer exchange failed");v=nv;EXCHANGES++
 );error("pivot exchange bound")
};
canonical_rows(Z)={
 my(M=chop(Z,1),k=matsize(Z)[2],rows=List());
 for(i=1,matsize(Z)[1],my(rr=concat(Vec(rows),[i]));if(matrank(submat(M,rr,[1..k]))>#rows,listput(rows,i));if(#rows==k,return(Vec(rows))));
 error("reduction not full column rank")
};
pick(M,r)={
 if(!r,return([[],[]]));
 my(mm=1,pv);
 while(mm<=PP*PREC,
  pv=matindexrank(chop(M,mm));
  if(#pv[1]>=r,my(cc=pv[2][1..r],rr=matindexrank(submat(chop(M,mm),[1..matsize(M)[1]],cc))[1]);if(matdet(submat(M,rr,cc))!=0,return(improve_pivot(M,rr,cc))));
  mm*=2
 );
 pv=matindexrank(M);if(#pv[1]<r,return([]));my(cc=pv[2][1..r],rr=matindexrank(submat(M,[1..matsize(M)[1]],cc))[1]);improve_pivot(M,rr,cc)
};
edge(state,digit)={
 my(flag=state[1],newflag=min(2,PP*flag+digit),frames=state[2],out=vector(3*CC),records=List());
 for(j=0,2,for(delta=0,CC-1,
  my(ch=vector(PP,r,my(jp=-floor((digit-j-2*(r-1))/PP),dp=BB*NN+BB*floor((digit-j-2*(r-1))/PP)-ceil((BB*(NN+digit-j)-delta-(r-1))/PP));if(dp<0,matrix(CC,0,i,k,0*OO),frames[jp*CC+dp+1])));
  my(parentd=NN+newflag-j,L=BB*parentd-delta,k=max(0,(BB*parentd+1-GG)-max(L,0)),pair=transition(ch),C=pair[1],H=pair[2],s=matsize(C)[2],r=s-k);
  if(r<0 || r>min(CC,s),return([0,"RANK_SIZE",j,delta,r,s,k]));
  my(pv=pick(C,r));if(#pv==0,return([0,"NO_PIVOT",j,delta,r,s,k]));
  my(rows=pv[1],cols=pv[2],alpha=if(r,max(0,-mval(submat(C,rows,cols)^(-1))),0));
  if(alpha>=(PP-1)*PREC+1,return([0,"C_PRECISION",j,delta,alpha,PREC]));
  my(K=selected_kernel(C,rows,cols),sigma=if(USE_RELATIVE,max(0,-mval(K)),alpha),Y=XPAR^sigma*H*K,rr=[],beta=0,h=0,U=matrix(CC,0,i,k,0*OO));
  if(k,
   my(ip=pick(Y,k));if(#ip==0,return([0,"NO_IMAGE_PIVOT",j,delta,k]));
   rr=ip[1];my(R=submat(Y,rr,[1..k]));beta=max(0,-mval(R^(-1)));
   if(alpha+beta>(PP-1)*PREC,return([0,"IMAGE_PRECISION",j,delta,alpha,beta,PREC]));
   my(Z=Y*R^(-1));h=max(0,-mval(Z));
   if(USE_CANONICAL,assert(h==0,"image frame not saturated");my(canon=canonical_rows(Z));assert(#canon==k,"image reduction rank");Z=Z*submat(Z,canon,[1..k])^(-1);rr=canon;beta=max(0,-mval(submat(Y,rr,[1..k])^(-1)));assert(alpha+beta<=(PP-1)*PREC,"canonical chart precision"));
   U=chop(XPAR^h*Z,PREC);
   if(matrank(U)!=k,return([0,"TRUNCATED_FRAME_RANK",j,delta,k]))
  );
  out[j*CC+delta+1]=U;listput(records,[j,delta,r,rows,cols,alpha,sigma,rr,beta,h]);
  if(getwalltime()-STARTMS>60000,return([0,"PILOT_TIME_BUDGET",j,delta]))
 ));
 [1,[newflag,out],Vec(records)]
};
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;GG=1;PREC=16;MAXSTATES=8;USE_RELATIVE=(getenv("BMD_ADIC_RELATIVE")!=0);USE_ROWS=(getenv("BMD_ADIC_ROWS")!=0);USE_PIVOTS=(getenv("BMD_ADIC_PIVOTS")!=0);USE_CANONICAL=USE_PIVOTS && (getenv("BMD_ADIC_NOCANONICAL")==0);EXCHANGES=0;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];
my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
ROWPOW=vector(CC,c,max(0,-2*valuation(ZZ[c],XPAR)));
RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
AC=0;AH=0;for(c=1,CC,for(r=0,2,AC=max(AC,-valuation(ZZ[c]^r,XPAR));if(r,AH=max(AH,-valuation(RR[c]^(-1)*r*ZZ[c]^(r-1),XPAR)))));
my(ell=vector(NN,i,OO+AA[i]*T+O(T^13)),roots=apply(sqrt,ell));for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=13,"root equations"));
CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
my(base=vector(3*CC));
for(j=0,2,for(delta=0,CC-1,my(d=NN-j,L=BB*d-delta,U=frame(source_eval(d)*matker(source_jet(d,L))),k=max(0,BB*d+1-GG-max(L,0)));assert(matsize(U)[2]==k,"base minimal rank");base[j*CC+delta+1]=chop(U,PREC);assert(matrank(base[j*CC+delta+1])==k,"base truncation lost rank")));
my(states=List([[0,base]]),witness=List([0]),seen=Map(),edges=List(),at=1,stop=0);mapput(seen,Str([0,base]),1);
print("PILOT relative=",USE_RELATIVE," row_clearing=",USE_ROWS," pivot_exchange=",USE_PIVOTS," canonical_saturation=",USE_CANONICAL," precision=",PREC," state_cap=",MAXSTATES," states contain36 frames in ambient12; 60s in-driver budget");
print("BASE_STATE = ",[0,base]);STARTMS=getwalltime();
while(at<=#states && !stop,
 for(a=0,2,
  my(before=getwalltime(),result=edge(states[at],a),elapsed=getwalltime()-before);
  if(!result[1],print("CERTIFICATE_REFUSED source=",at," representative_x=",witness[at]," digit=",a," reason=",result," wall_ms=",elapsed);stop=1;break);
  my(key=Str(result[2]),dest);
  if(mapisdefined(seen,key),dest=mapget(seen,key),
   if(#states>=MAXSTATES,print("STATE_CAP_REACHED; graph incomplete; accepted local edge source=",at," digit=",a," wall_ms=",elapsed);stop=1;break);
   listput(states,result[2]);listput(witness,PP*witness[at]+a);dest=#states;mapput(seen,key,dest);print("STATE ",dest," representative_x=",witness[dest]," DATA = ",result[2])
  );
  listput(edges,[at,a,dest,result[3]]);print("EDGE = ",[at,a,dest,result[3]]," WALL_MS=",elapsed);
  if(elapsed>10000,print("STOP_SCALING: one edge exceeds10s; optimize before further graph expansion");stop=1;break)
 );at++
);
print("GRAPH_RESULT states=",#states," edges=",#edges," closed=",!stop && at>#states," elapsed_ms=",getwalltime()-STARTMS," pivot_exchanges=",EXCHANGES);
print("ADIC_GRAPH_PILOT_COMPLETED; only closed=true with all certified edges would be an all-degree certificate")
}
quit;
