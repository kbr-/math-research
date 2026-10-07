\\ Exact controls for a Frobenius/branch transition precision certificate.
\\ F3(u), n3, d7 recursion: compare truncated integral frames with rational arithmetic.
\\ This tests the local certificate, not finite-state closure or new normality.
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
 my(rows=matindexrank(U)[1],R=submat(U,rows,[1..k]),Z=U*R^(-1),h=max(0,-mval(Z)));
 XPAR^h*Z
};
transition(children)={
 my(sizes=apply(U->matsize(U)[2],children),total=vecsum(sizes),off=0,C=matrix(CC,total,i,j,0*OO),H=C);
 for(r=0,PP-1,for(c=1,CC,for(k=1,sizes[r+1],my(v=children[r+1][c,k]^PP);C[c,off+k]=ZZ[c]^r*v;H[c,off+k]=RR[c]^(-1)*r*ZZ[c]^(r-1)*v));off+=sizes[r+1]);
 [XPAR^AC*C,XPAR^AH*H]
};
cert_state(d,L)={
 my(key=[d,L]);if(mapisdefined(CERTCACHE,key),return(mapget(CERTCACHE,key)));
 my(U);
 if(L>BB*d,U=matrix(CC,0,i,j,0*OO),
 if(d<=NN && L<=BB,U=frame(source_eval(d)*matker(source_jet(d,L))),
  my(ch=vector(PP,r,cert_state((d+(PP-1)*NN-2*(r-1))\PP,(L-(r-1)+PP-1)\PP)),pair=transition(ch),C=pair[1],H=pair[2],pv=matindexrank(C),rows=pv[1],cols=pv[2],s=matsize(C)[2],rk=#cols,k=s-rk);
  assert(k==max(0,BB*d+1-GG-L),"known elliptic rank profile failed");
  my(v=if(rk,valuation(matdet(submat(C,rows,cols)),XPAR),0));assert(v>=0,"C not integral");
  my(K=selected_kernel(C,rows,cols),Y=XPAR^v*H*K,rr=[],w=0,h=0);
  if(k,rr=matindexrank(Y)[1];assert(#rr==k,"H image rank");my(R=submat(Y,rr,[1..k]));w=valuation(matdet(R),XPAR);assert(w>=0 && mval(Y)>=0,"image integral bound");my(Z=Y*R^(-1));h=max(0,-mval(Z));U=XPAR^h*Z,U=matrix(CC,0,i,j,0*OO));
  my(loss=v+2*w,N=max(1,(loss+PP-2)\(PP-1)));assert(N<1000,"precision too large for control budget");
  for(test=0,1,
   my(approx=apply(V->matrix(matsize(V)[1],matsize(V)[2],i,j,truncate(V[i,j]+O(XPAR^N))+if(test && i==1 && j==1,OO*XPAR^N,0*OO)),ch),pq=transition(approx),Ca=pq[1],Ha=pq[2]);
   if(rk,assert(valuation(matdet(submat(Ca,rows,cols)),XPAR)==v,"pivot certificate unstable"));
   if(k,my(Ka=selected_kernel(Ca,rows,cols),Ya=XPAR^v*Ha*Ka,Ra=submat(Ya,rr,[1..k]),Ua=XPAR^h*Ya*Ra^(-1));assert(valuation(matdet(Ra),XPAR)==w,"image pivot unstable");assert(mval(Ua-U)>=PP*N-loss,"precision bound violated"));
   CHECKS++
  );
  print("STATE ",key," C_size=",matsize(C)," output_dimension=",k," pivot_v=",v," image_w=",w," frame_scale=",h," precision=",N," retained_bound=",PP*N-loss);
  MAXPREC=max(MAXPREC,N)
 ));
 mapput(CERTCACHE,key,U);U
};
{
T='x;XPAR='u;NN=3;PP=3;OO=Mod(1,3);BB=4;CC=12;HH=1;GG=1;
AA=[OO,OO*XPAR,OO*(XPAR^2+XPAR+2)];
my(coords=List());for(S=0,7,for(i=1,NN,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
RR=vector(CC,c,my(S=COORD[c][1],i=COORD[c][2]);AA[i]*prod(h=1,NN,if(h==i||bittest(S,h-1),OO,OO+AA[h]*ZZ[c])));
AC=0;AH=0;for(c=1,CC,for(r=0,2,AC=max(AC,-valuation(ZZ[c]^r,XPAR));if(r,AH=max(AH,-valuation(RR[c]^(-1)*r*ZZ[c]^(r-1),XPAR)))));
my(prec=29,ell=vector(NN,i,OO+AA[i]*T+O(T^prec)),roots=apply(sqrt,ell));for(i=1,NN,assert(valuation(roots[i]^2-ell[i],T)>=prec,"root equations"));
CH=vector(8,S,prod(i=1,NN,if(bittest(S-1,i-1),roots[i],OO)));
CERTCACHE=Map();CHECKS=0;MAXPREC=0;
print("F3(u), labels=",AA," coefficient clearing powers=",[AC,AH]," source d7 has28 columns; branch ambient12");gettime();
my(U=cert_state(7,28),direct=source_eval(7)*matker(source_jet(7,28)));
assert(matsize(U)[2]==matsize(direct)[2] && matrank(matconcat([U,direct]))==matsize(U)[2],"direct original kernel mismatch");
my(N=5,bad=matdiagonal([OO,OO*XPAR^N]),approx=matrix(2,2,i,j,truncate(bad[i,j]+O(XPAR^N))));
assert(matrank(bad)==2 && matrank(approx)==1,"hidden pivot negative control");assert(valuation(matdet(bad),XPAR)>=N,"hidden pivot should fail rank certificate");
print("CHECKS=",CHECKS," MAX_PRECISION=",MAXPREC," CPU_MS=",gettime(),"; hidden pivot refused");
print("ADIC_BRANCH_CONTROLS_COMPLETED: local precision certificate only; no closed automaton claimed")
}
quit;
