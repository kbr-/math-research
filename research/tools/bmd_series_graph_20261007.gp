\\ Residual-certified finite-precision graph pilot, using PARI series candidates.
\\ Residuals are checked as exact Laurent-polynomial products; no series rank is trusted.
default(parisizemax,2000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
mval(M)={my(v=1000000);for(i=1,matsize(M)[1],for(j=1,matsize(M)[2],if(M[i,j]!=0,v=min(v,valuation(M[i,j],XPAR)))));v};
submat(M,rr,cc)=matrix(#rr,#cc,i,j,M[rr[i],cc[j]]);
chop(M,N)=matrix(matsize(M)[1],matsize(M)[2],i,j,OO*truncate(M[i,j]+O(XPAR^N)));
canonical_rows(Z)={
 my(M=chop(Z,1),k=matsize(Z)[2],rows=List());
 for(i=1,matsize(Z)[1],my(rr=concat(Vec(rows),[i]));if(matrank(submat(M,rr,[1..k]))>#rows,listput(rows,i));if(#rows==k,return(Vec(rows))));
 error("reduction not full column rank")
};
inverse_residual(A,Q)={my(alpha=max(0,-mval(Q)),rho=mval(A*Q-matid(matsize(A)[1])));[alpha,rho]};
inv_candidate(A)={
 my(n=matsize(A)[1]);if(!n,return([matrix(0,0),0,1000000]));
 my(key=Str(A));if(mapisdefined(INVCACHE,key),INVHITS++;return(mapget(INVCACHE,key)));
 for(t=1,3,
  my(work=WP*2^t,Bs,ok=1,started=getwalltime());
  iferr(Bs=matsolve(matrix(n,n,i,j,A[i,j]+O(XPAR^work)),matid(n)),E,ok=0);
  INVMS+=getwalltime()-started;if(!ok,next);
  my(Qfull=matrix(n,n,i,j,truncate(Bs[i,j]+O(XPAR^work))),alpha=max(0,-mval(Qfull)),want=max(WP,alpha+1),Q=chop(Qfull,want));
  started=getwalltime();my(vr=inverse_residual(A,Q));RESMS+=getwalltime()-started;
  if(vr[2]>=want && vr[2]>vr[1],
   if(!NEGATIVE,my(bad=Q);bad[1,1]+=OO*XPAR^(-2*WP);my(vb=inverse_residual(A,bad));assert(vb[2]<=max(0,vb[1]),"corrupt inverse was accepted");NEGATIVE=1);
   my(ans=[Q,vr[1],vr[2]]);mapput(INVCACHE,key,ans);INVS++;return(ans)
  )
 );[]
};
improve(M,rr,cc)={
 if(!#rr,return([rr,cc,matrix(0,0),0,1000000]));
 my(cert=inv_candidate(submat(M,rr,cc)));if(!#cert,return([]));
 my(bound=#rr*cert[2]+1);
 for(step=1,bound,
  my(Q=cert[1],X=Q*submat(M,rr,[1..matsize(M)[2]]),Y=submat(M,[1..matsize(M)[1]],cc)*Q,best=0,which=0,ii=0,jj=0);
  assert(cert[3]>cert[2],"Cramer sign not certified");
  for(i=1,matsize(X)[1],for(j=1,matsize(X)[2],if(X[i,j]!=0 && valuation(X[i,j],XPAR)<best,best=valuation(X[i,j],XPAR);which=1;ii=i;jj=j)));
  for(i=1,matsize(Y)[1],for(j=1,matsize(Y)[2],if(Y[i,j]!=0 && valuation(Y[i,j],XPAR)<best,best=valuation(Y[i,j],XPAR);which=2;ii=i;jj=j)));
  if(!which,return([rr,cc,cert[1],cert[2],cert[3]]));
  if(which==1,assert(!setsearch(Set(cc),jj),"duplicate column exchange");cc[ii]=jj,assert(!setsearch(Set(rr),ii),"duplicate row exchange");rr[jj]=ii);
  EXCHANGES++;cert=inv_candidate(submat(M,rr,cc));if(!#cert,return([]))
 );error("Cramer exchange bound")
};
pick(M,r)={
 if(!r,return([[],[],matrix(0,0),0,1000000]));
 my(pv,ok=1,Ms=matrix(matsize(M)[1],matsize(M)[2],i,j,M[i,j]+O(XPAR^(2*WP))));
 iferr(pv=matindexrank(Ms),E,ok=0);
 if(ok && #pv[2]>=r,
  my(cc=pv[2][1..r],rr);
  iferr(rr=matindexrank(submat(Ms,[1..matsize(M)[1]],cc))[1],E,ok=0);
  if(ok && #rr==r,my(ans=improve(M,rr,cc));if(#ans,return(ans)))
 );[]
};
transition(ch)={
 my(sizes=apply(U->matsize(U)[2],ch),s=vecsum(sizes),off=0,C=matrix(CC,s,i,j,0*OO),H=C);
 for(r=0,2,for(c=1,CC,for(k=1,sizes[r+1],my(v=ch[r+1][c,k]^3);C[c,off+k]=OO*truncate(CCOEF[c,r+1]*v+O(XPAR^WP));H[c,off+k]=OO*truncate(HCOEF[c,r+1]*v+O(XPAR^WP))));off+=sizes[r+1]);[C,H]
};
local_step(ch,k)={
 my(key=Str([ch,k]));if(mapisdefined(LOCALCACHE,key),LOCALHITS++;return(mapget(LOCALCACHE,key)));
 my(pair=transition(ch),C=pair[1],H=pair[2],s=matsize(C)[2],r=s-k);
 if(r<0 || r>min(CC,s),return([0,"RANK_SIZE",r,s,k]));
 my(pv=pick(C,r));if(!#pv,return([0,"PIVOT_CANDIDATE",r,s,k]));
 my(rr=pv[1],cc=pv[2],Q=pv[3],alpha=pv[4],rhoA=pv[5]);
 if(WP<=alpha || rhoA<=0,return([0,"TRUE_PIVOT_PRECISION",alpha,rhoA]));
 my(free=select(j->!setsearch(Set(cc),j),[1..s]),K=matrix(s,k,i,j,if(i==free[j],OO,0*OO)));
 if(r && k,my(Z=chop(-Q*submat(C,rr,free),WP));for(i=1,r,for(j=1,k,K[cc[i],j]=Z[i,j])));
 my(sigma=if(k,max(0,-mval(K)),0),tau=if(k,mval(submat(C,rr,[1..s])*K),1000000),e=min(WP,tau+sigma)-alpha,U=matrix(CC,0,i,j,0*OO),rows=[],beta=0,rhoR=1000000,retained=1000000);
 if(k,
  my(Y=chop(XPAR^sigma*H*K,WP),ip=pick(Y,k));assert(mval(Y)>=0,"image not integral");
  if(!#ip,return([0,"IMAGE_CANDIDATE",k]));
  rows=ip[1];my(ic=inv_candidate(submat(Y,rows,[1..k])));if(!#ic,return([0,"IMAGE_INVERSE"]));
  beta=ic[2];rhoR=ic[3];retained=min(e-beta,rhoR);
  if(retained<PREC,return([0,"IMAGE_PRECISION",alpha,sigma,tau,beta,rhoR,retained,PREC]));
  my(W=Y*ic[1]);if(mval(W)<0,return([0,"UNSATURATED_IMAGE",mval(W)]));
  rows=canonical_rows(W);ic=inv_candidate(submat(Y,rows,[1..k]));if(!#ic,return([0,"CANONICAL_INVERSE"]));
  beta=ic[2];rhoR=ic[3];retained=min(e-beta,rhoR);if(retained<PREC,return([0,"CANONICAL_PRECISION",retained]));
  U=chop(Y*ic[1],PREC);assert(mval(U)>=0 && submat(U,rows,[1..k])==matid(k),"canonical output chart")
 );
 my(ans=[1,U,[r,rr,cc,alpha,rhoA,sigma,tau,rows,beta,rhoR,retained]]);mapput(LOCALCACHE,key,ans);LOCALS++;ans
};
edge(state,digit)={
 my(flag=state[1],nf=min(2,3*flag+digit),frames=state[2],out=vector(3*CC),rec=List());
 for(j=0,2,for(delta=0,CC-1,
  my(ch=vector(3,r,my(jp=-floor((digit-j-2*(r-1))/3),dp=BB*NN+BB*floor((digit-j-2*(r-1))/3)-ceil((BB*(NN+digit-j)-delta-(r-1))/3));if(dp<0,matrix(CC,0,i,k,0*OO),frames[jp*CC+dp+1])));
  my(d=NN+nf-j,L=BB*d-delta,k=max(0,BB*d+1-GG-max(L,0)),result=local_step(ch,k));
  if(!result[1],return([0,j,delta,result]));out[j*CC+delta+1]=result[2];listput(rec,concat([j,delta],result[3]));
  if(getwalltime()-STARTMS>120000,return([0,j,delta,"PILOT_TIME_BUDGET"]))
 ));[1,[nf,out],Vec(rec)]
};
{
XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;GG=1;PREC=16;WP=3*PREC;MAXSTATES=64;
my(AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)],coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));my(COORD=Vec(coords),ZZ=vector(CC,c,-OO/AA[COORD[c][2]]),RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c]))),AH=0);
for(c=1,CC,for(r=1,2,AH=max(AH,-valuation(RR[c]^(-1)*r*ZZ[c]^(r-1),XPAR))));
CCOEF=matrix(CC,3,c,r,truncate(XPAR^max(0,-2*valuation(ZZ[c],XPAR))*ZZ[c]^(r-1)+O(XPAR^WP)));
HCOEF=matrix(CC,3,c,r,if(r==1,0*OO,truncate(XPAR^AH*RR[c]^(-1)*(r-1)*ZZ[c]^(r-2)+O(XPAR^WP))));
my(lines=readstr("research/results/bmd-exception-adic-closure-20261007/canonical-pilot.txt"),base=0,reference=0);
for(i=1,#lines,my(z=strsplit(lines[i],"BASE_STATE = "));if(#z==2,base=eval(z[2]));z=strsplit(lines[i]," DATA = ");if(#z==2 && eval(strsplit(z[1]," representative_x=")[2])==1,reference=eval(z[2])));
assert(base!=0 && reference!=0,"missing independently checked reference states");
base[2]=apply(U->chop(U,PREC),base[2]);reference[2]=apply(U->chop(U,PREC),reference[2]);
for(i=1,#base[2],my(U=base[2][i],k=matsize(U)[2]);if(k,assert(submat(U,canonical_rows(U),[1..k])==matid(k),"base chart")));
INVCACHE=Map();LOCALCACHE=Map();INVS=0;INVHITS=0;LOCALS=0;LOCALHITS=0;INVMS=0;RESMS=0;EXCHANGES=0;NEGATIVE=0;STARTMS=getwalltime();
my(states=List([base]),xs=List([0]),seen=Map(),edges=List(),at=1,stop=0,reference_checks=0);mapput(seen,Str(base),1);
print("SERIES_GRAPH precision=",PREC," product_precision=",WP," cap=",MAXSTATES," time_budget_ms=120000; exact residual certificates");print("BASE_STATE = ",base);
while(at<=#states && !stop,
 for(a=0,2,
  my(start=getwalltime(),result=edge(states[at],a),elapsed=getwalltime()-start);
  if(!result[1],print("CERTIFICATE_REFUSED source=",at," representative_x=",xs[at]," digit=",a," reason=",result," wall_ms=",elapsed);stop=1;break);
  if(at==1 && a<=1,assert(result[2]==if(a==0,base,reference),"rational-reference state mismatch");reference_checks+=3*CC);
  my(key=Str(result[2]),dest);
  if(mapisdefined(seen,key),dest=mapget(seen,key),if(#states>=MAXSTATES,print("STATE_CAP_REACHED; graph incomplete");stop=1;break);listput(states,result[2]);listput(xs,3*xs[at]+a);dest=#states;mapput(seen,key,dest);print("STATE ",dest," representative_x=",xs[dest]," DATA = ",result[2]));
  listput(edges,[at,a,dest,result[3]]);print("EDGE = ",[at,a,dest,result[3]]," WALL_MS=",elapsed);
  if(elapsed>10000,print("STOP_SCALING: edge exceeds10s");stop=1;break)
 );at++
);
print("GRAPH_RESULT states=",#states," edges=",#edges," closed=",!stop && at>#states," elapsed_ms=",getwalltime()-STARTMS," inverses=",INVS," inverse_cache_hits=",INVHITS," local_transitions=",LOCALS," local_cache_hits=",LOCALHITS," candidate_inverse_ms=",INVMS," residual_check_ms=",RESMS," exchanges=",EXCHANGES," reference_frame_checks=",reference_checks," corruption_detected=",NEGATIVE);
print("SERIES_GRAPH_COMPLETED; closed=false is not a complete normality certificate")
}
quit;
