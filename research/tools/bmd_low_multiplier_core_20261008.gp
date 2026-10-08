\\ Shared exact coefficient-matrix Schur reduction and encoding helpers.
lm_assert(c,s)={if(!c,error(s));};
lm_sub(M,rr,cc)={matrix(#rr,#cc,i,j,M[rr[i],cc[j]]);};
lm_encode(M,codes)={my(sz=matsize(M));vector(sz[1],i,vector(sz[2],j,mapget(codes,Str(M[i,j]))));};
lm_smith(series)={
 my(A=series,H=matsize(A[1])[2],E0=matid(H),E1=matrix(H,H),depth=0,pivots=List(),derivative=1);
 while(#A,
  my(sz=matsize(A[1]),nr=sz[1],nc=sz[2],indices=matindexrank(A[1]),rr=indices[1],cc=indices[2],rank=#rr,prec=#A);
  if(rank,
   my(rs=setminus([1..nr],Set(rr)),cs=setminus([1..nc],Set(cc)),U=vector(prec,i,lm_sub(A[i],rr,cc)),B=vector(prec,i,lm_sub(A[i],rr,cs)),C=vector(prec,i,lm_sub(A[i],rs,cc)),D=vector(prec,i,lm_sub(A[i],rs,cs)),inv=U[1]^-1,X=vector(prec),newE0,newE1);
   for(k=0,prec-1,X[k+1]=inv*(B[k+1]-sum(j=1,k,U[j+1]*X[k-j+1])));
   newE0=lm_sub(E0,[1..H],cs)-lm_sub(E0,[1..H],cc)*X[1];
   if(prec>=2&&derivative,newE1=lm_sub(E1,[1..H],cs)-lm_sub(E1,[1..H],cc)*X[1]-lm_sub(E0,[1..H],cc)*X[2],newE1=matrix(H,#cs);derivative=0);
   E0=newE0;E1=newE1;listput(pivots,[depth,rank]);
   print("LOW_SMITH_STAGE order=",depth," pivots=",rank," rows_left=",nr-rank," precision_left=",prec);
   if(rank==nr,return([1,Vec(pivots),E0,E1,derivative]));
   A=vector(prec,k,D[k]-sum(j=0,k-1,C[j+1]*X[k-j]));
   lm_assert(A[1]==matrix(#rs,#cs),"exact zero Schur constant");
  );
  if(#A==1,break());A=vector(#A-1,i,A[i+1]);depth++;
 );
 [0,Vec(pivots),E0,E1,derivative];
};

lm_decode(A,field)={matrix(#A,#A[1],i,j,field[A[i][j]+1]);};
lm_frob(A,e)={matrix(matsize(A)[1],matsize(A)[2],i,j,A[i,j]^e);};
lm_cup(v,polys,off,I)={matrix(140,140,i,j,my(common=bitand(I[i][1],I[j][1]),S=511-bitxor(I[i][1],I[j][1]),shift=I[i][2]+I[j][2]);sum(l=0,poldegree(polys[common+1],T),polcoef(polys[common+1],l,T)*v[off[S+1]+shift+l+1]));};
