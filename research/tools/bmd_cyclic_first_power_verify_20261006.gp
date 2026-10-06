\\ Independent pair-square recurrence checks the failed cyclic configuration.
\\ At a moved admissible mark, one explicit23-column minor checks orders0..21,23.
default(parisizemax, 200000000);
bmd_assert(x,s)=if(!x,error(s));
bmd_pair_matrix(a,len)={
  my(N=#a,M=binomial(N,2)+2,one=a[1]^0,J=matrix(binomial(N,2)+2,len,i,j,0*a[1]),row=2,c,g);
  J[1,1]=one;J[2,2]=one;
  for(i=1,N-1,for(j=i+1,N,
    g=vector(len);g[1]=one;
    for(k=1,len-1,
      c=if(k==1,a[i]+a[j],if(k==2,a[i]*a[j],0));
      g[k+1]=(c-sum(h=1,k-1,g[h+1]*g[k-h+1]))/2;
    );
    bmd_assert(Polrev(g,'T)^2%(T^len)==(1+(a[i]+a[j])*T+a[i]*a[j]*T^2)%(T^len),"pair-square recurrence");
    row++;for(k=1,len,J[row,k]=g[k]);
  ));
  return(J);
};
bmd_verify()={
  my(pol=Mod(1,23)*(x^3+x^2+21*x+22),z,omega,a,J,ker,piv,minor,bb=2,am,K,cols,cert);
  bmd_assert(polisirreducible(pol),"field polynomial");z=ffgen(pol,'z);omega=6*z^2+9*z+5;
  bmd_assert(omega^7==1 && omega!=1,"primitive seventh root");
  a=vector(7,i,omega^(i-1)-1);
  J=bmd_pair_matrix(a,23);
  ker=[0,0,0,14,5,12,12,1,21,13,1,22,10,2,22,11,10,21,6,1,0,0,0]~;
  bmd_assert(J*ker==vector(23)~,"retained nullvector");
  piv=matindexrank(J);bmd_assert(#piv[1]==22,"independent rank");
  minor=matrix(22,22,i,j,J[piv[1][i],piv[2][j]]);
  bmd_assert(matdet(minor)!=0,"rank22 witness");
  print("constant_mark_rank=22 rows=",piv[1]," columns=",piv[2]," minor=",matdet(minor));
  for(i=1,7,bmd_assert(1+bb*a[i]!=0,"moving branch collision"));
  am=vector(7,i,a[i]/(1+bb*a[i]));
  K=bmd_pair_matrix(am,24);
  cols=concat(vector(22,i,i),[24]);cert=matrix(23,23,i,j,K[i,cols[j]]);
  bmd_assert(matdet(cert)!=0,"moving orders0..21,23");
  bmd_assert(matdet(matrix(23,23,i,j,K[i,j]))==0,"moving first23 defect");
  print("moving_mark=",bb," normalized_slopes=",am);
  print("moving_minor_columns_zero_based=0..21,23 determinant=",matdet(cert));
  print("moving_first23_determinant=0");
  print("PASS: independent recurrence and two exact rank certificates");
};
bmd_verify();
quit;
