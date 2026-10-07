\\ Exact bounded branch-state recursion for actual marked root-polynomial kernels.
\\ Shared implementation for the finite-field and rational-function controls.
assert(c,s)={if(!c,error(s));};
inds(d)={my(V=List());for(S=0,2^NN-1,for(j=0,max(-1,(d-hammingweight(S))\2),if(2*j+hammingweight(S)<=d,listput(V,[S,j]))));Vec(V);};
source_jet(d,L)={my(I=inds(d));matrix(max(0,L),#I,i,j,polcoef(CH[I[j][1]+1]*T^I[j][2],i-1,T))};
source_eval(d)={my(I=inds(d));matrix(CC,#I,c,j,if(I[j][1]==COORD[c][1],ZZ[c]^I[j][2],0*OO))};
MEASURE_SYMBOLIC=0;
MAX_COEFF_DEGREE=0;
branch_state(d,L)={
 my(key=[d,L]);if(mapisdefined(CACHE,key),return(mapget(CACHE,key)));
 assert(d>=NN-2 && BB*d-L<CC,"state outside faithful evaluation range");
 CALLS++;MAXDEG=max(MAXDEG,d);
 my(U);
 if(L>BB*d,U=matrix(CC,0,i,j,0*OO),
  if(d<=NN && L<=BB,
   my(K=matker(source_jet(d,L)));U=source_eval(d)*K;
   assert(matrank(U)==matsize(K)[2],"base branch map lost a kernel vector"),
   my(ed=vector(PP,r,(d+(PP-1)*NN-2*(r-1))\PP),ll=vector(PP,r,(L-(r-1)+PP-1)\PP),children=vector(PP,r,branch_state(ed[r],ll[r])),sizes=vector(PP,r,matsize(children[r])[2]),total=vecsum(sizes),offset=0);
   my(C=matrix(HH*CC,total,i,j,0*OO),H=matrix(CC,total,i,j,0*OO));
   for(r=0,PP-1,
    for(c=1,CC,for(k=1,sizes[r+1],my(v=children[r+1][c,k]^PP);
     for(j=0,HH-1,C[j*CC+c,offset+k]=binomial(r,j)*ZZ[c]^(r-j)*v);
     H[c,offset+k]=RR[c]^(-HH)*binomial(r,HH)*ZZ[c]^(r-HH)*v
    ));offset+=sizes[r+1]
   );
   MAXCOLS=max(MAXCOLS,total);
   my(K=matker(C));U=H*K;
   assert(matrank(U)==matsize(K)[2],"reconstruction lost a compatible kernel vector")
  )
 );
 if(MEASURE_SYMBOLIC,for(i=1,matsize(U)[1],for(j=1,matsize(U)[2],if(U[i,j]!=0,MAX_COEFF_DEGREE=max(MAX_COEFF_DEGREE,max(poldegree(numerator(U[i,j]),XPAR),poldegree(denominator(U[i,j]),XPAR)))))));
 mapput(CACHE,key,U);U
};
