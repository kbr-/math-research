\\ Generic cross-block for a quadratic-image additive-flag recursion in char3.
\\ After affine normalization, the two triples are
\\ 0, +/-eps + (v^2-1)eps^2 and 1, 1+/-v eps + (v^2-1)eps^2.
\\ This is one symbolic all-v local block, not a larger-q normality run.
\\ Stages: root series with independent square checks; full even8/mixed9
\\ coefficientwise saturation; canonical limit rows and marked rank tests.
default(parisizemax,2000000000);
default(parisize,128000000);
z='z;y='y;v='v;
beta(j)={my(s=if(j%3==1,-1,1));j=j\3;while(j>0,if(j%3==2,return(0));j=j\3);s};
{
my(o=Mod(1,3),D=o*(v^2-1),P=20,nc=2*P+2,rr=[0,1,-1],roots=vector(2,h,vector(3,i,vector(P+1,m,0*o))),checks=0);
for(h=0,1,for(i=1,3,for(m=0,P,
 my(pol=0*o,C=if(h==0,o,o*v),r=rr[i]);
 if(m==0,pol=y^(P*h)*o,
  if(r!=0,for(k=(m+1)\2,m,my(fac=o*r^m*beta(k)*binomial(k,m-k)*C^(2*k-m)*D^(m-k));
   if(fac!=0,pol+=fac*(y-1)^k*y^(P*h-h*k)))));
 roots[h+1][i][m+1]=pol
)));
for(h=0,1,for(i=1,3,for(m=0,P,
 my(r=rr[i],C=if(h==0,o,o*v),rhs=if(m==0,y^(2*P*h)*o,if(m==1,r*C*(y-1)*y^(2*P*h-h),if(m==2,r^2*D*(y-1)*y^(2*P*h-h),0*o))));
 if(sum(j=0,m,roots[h+1][i][j+1]*roots[h+1][i][m-j+1])!=rhs,error("root square coefficient mismatch"));checks++
)));
print("FIELD F3(v); D=v^2-1; precision20; ROOT_SQUARE_CHECKS = ",checks);
my(limits=List(),valuations=List(),firsts=List(),seconds=List(),allcoefs=List());
for(block=1,2,
 my(nr=if(block==1,8,9),prec=P,coefs=vector(P+1,m,matrix(nr,nc,i,j,0*o)));
 if(block==1,
  coefs[1][1,P+1]=o;coefs[1][2,P+1]=-o;coefs[1][2,P+2]=o;
  my(row=2);
  for(h=0,1,for(i=1,3,for(j=i+1,3,row++;
   for(m=0,P,my(pol=sum(k=0,m,roots[h+1][i][k+1]*roots[h+1][j][m-k+1])*y^(P*(1-2*h)+h));
    for(k=0,nc-1,coefs[m+1][row,k+1]=polcoef(pol,k,y))
   )
  ))),
  for(i=1,3,for(j=1,3,for(m=0,P,
   my(pol=sum(k=0,m,roots[1][i][k+1]*roots[2][j][m-k+1]));
   for(k=0,nc-1,coefs[m+1][3*(i-1)+j,k+1]=polcoef(pol,k,y))
  )))
 );
 print("BLOCK ",block," ROWS ",nr);
 my(step=0,total=0);
 while(1,
  my(M0=coefs[1],ix=matindexrank(M0)[1],rk=#ix);
  print("STEP ",step," PRECISION ",prec," RANK ",rk);
  if(rk==nr,break);
  if(prec<1,error("precision exhausted; no complete lattice claim"));
  my(K=matker(M0~),T=matrix(nr,nr,i,j,if(i<=rk,if(j==ix[i],o,0*o),K[j,i-rk])));
  if(matrank(T)!=nr||M0~*K!=matrix(nc,nr-rk,i,j,0*o),error("basis/kernel reconstruction"));
  print("PIVOT_ROWS = ",ix,"; KERNEL_ROWS = ",K~);
  my(next=vector(prec+1,m,T*coefs[m]));
  coefs=vector(prec,m,matrix(nr,nc,i,j,if(i<=rk,next[m][i,j],next[m+1][i,j])));
  total+=nr-rk;prec--;step++
 );
 my(B=coefs[1],cols=matindexrank(B)[2],pivot=matrix(nr,nr,i,j,B[i,cols[j]]),C=matsolve(pivot,B));
 if(pivot*C!=B,error("canonical row reconstruction"));
 print("VALUATION = ",total);
 print("CANONICAL_LIMIT = ",vector(nr,i,sum(j=0,nc-1,C[i,j+1]*y^(j-P))));
 print("SUPPORTS = ",vector(nr,i,my(s=List());for(j=0,nc-1,if(C[i,j+1]!=0,listput(s,j-P)));Vec(s)));
 listput(allcoefs,vector(9,m,matsolve(pivot,coefs[m])));listput(limits,C);listput(firsts,matsolve(pivot,coefs[2]));listput(seconds,matsolve(pivot,coefs[3]));listput(valuations,total)
);
my(J=matrix(17,17,i,j,0*o),Mv=matrix(17,17,i,j,0*o),Mz=matrix(17,17,i,j,0*o));
for(i=1,17,my(block=if(i<=8,1,2),r=if(i<=8,i,i-8),odd=if(i<=8,0,1));
 for(j=0,16,
  J[i,j+1]=sum(k=0,nc-1,limits[block][r,k+1]*binomial(2*k+odd,j));
  Mv[i,j+1]=sum(k=0,nc-1,if(2*k+odd>=j,limits[block][r,k+1]*binomial(2*k+odd,j)*v^(2*k+odd-j),0*o));
  Mz[i,j+1]=sum(k=0,nc-1,if(2*k+odd>=j,limits[block][r,k+1]*binomial(2*k+odd,j)*z^(2*k+odd-j),0*o))
 )
);
print("TOTAL_FUNCTION_VALUATION = ",vecsum(Vec(valuations)),"; BLOCK_VALUATIONS = ",Vec(valuations));
print("LIMIT_JET_DET_AT_X1 = ",matdet(J));
print("LIMIT_JET_DET_AT_XV = ",matdet(Mv));
print("GENERIC_MARK_DETERMINANT_STARTED");
my(dz=matdet(Mz));print("GENERIC_MARK_DETERMINANT = ",dz);
if(dz==0,my(Kz=matker(Mz~));if(Mz~*Kz!=matrix(17,matsize(Kz)[2],i,j,0*o),error("generic mark kernel reconstruction"));print("GENERIC_MARK_RANK = ",17-matsize(Kz)[2]);print("GENERIC_MARK_ROW_KERNEL = ",Kz));
my(M1=matrix(17,17,i,j,my(block=if(i<=8,1,2),r=if(i<=8,i,i-8),odd=if(i<=8,0,1));sum(k=0,nc-1,if(2*k+odd>=j-1,firsts[block][r,k+1]*binomial(2*k+odd,j-1)*z^(2*k+odd-j+1),0*o))));
my(KL=matker(Mz~),KR=matker(Mz));
print("FIRST_DELAYED_PAIRING_STARTED");
print("FIRST_DELAYED_PAIRING = ",KL~*M1*KR);
my(M2=matrix(17,17,i,j,my(block=if(i<=8,1,2),r=if(i<=8,i,i-8),odd=if(i<=8,0,1));sum(k=0,nc-1,if(2*k+odd>=j-1,seconds[block][r,k+1]*binomial(2*k+odd,j-1)*z^(2*k+odd-j+1),0*o))));
my(piv=matindexrank(Mz),ir=piv[1],ic=piv[2],U0=matrix(16,16,i,j,Mz[ir[i],ic[j]]),b1=M1*KR);
print("SECOND_DELAYED_PAIRING_STARTED");
my(sol=matsolve(U0,matrix(16,1,i,j,b1[ir[i],j])),X=matrix(17,1,i,j,0*o));
for(i=1,16,X[ic[i],1]=sol[i,1]);
if(Mz*X!=b1,error("first kernel lift mismatch"));
print("SECOND_DELAYED_PAIRING = ",KL~*(M2*KR-M1*X));
my(Js=vector(9,m,Mz));Js[2]=M1;Js[3]=M2;
for(m=4,9,Js[m]=matrix(17,17,i,j,
 my(block=if(i<=8,1,2),r=if(i<=8,i,i-8),odd=if(i<=8,0,1));
 sum(k=0,nc-1,if(2*k+odd>=j-1,allcoefs[block][m][r,k+1]*binomial(2*k+odd,j-1)*z^(2*k+odd-j+1),0*o))
));
my(lifts=List(),Uinv=U0^-1);listput(lifts,KR);
for(m=1,8,
 my(rhs=-sum(j=1,m,Js[j+1]*lifts[m-j+1]),obs=KL~*rhs);
 print("KERNEL_LIFT_ORDER = ",m,"; OBSTRUCTION = ",obs);
 if(obs!=matrix(1,1,i,j,0*o),break);
 my(sol=Uinv*matrix(16,1,i,j,rhs[ir[i],j]),lift=matrix(17,1,i,j,0*o));
 for(i=1,16,lift[ic[i],1]=sol[i,1]);
 if(Mz*lift!=rhs,error("higher kernel lift mismatch"));listput(lifts,lift)
);
print("QUADRATIC_TRIPLE_BLOCK_COMPLETED")
}
quit;
