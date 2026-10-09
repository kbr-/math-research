\\ Exact control of the two-residue within-prefix formula, N9,R36.
\\ Reuse the independently source-checked matrix. Stages: complete H9
\\ transport; moment boundary; all27 interpolants; all729 Schur entries;
\\ independent determinant export. No larger size or new normality claim.
default(parisizemax,500000000);
default(parisize,64000000);
z='z;
g=ffgen(Mod(1,3)*('g^4+'g^3+'g^2+'g+1),'g);o=g^0;
qvec(s,d,L)={my(Q=vector(L,j,0*s));Q[1]=s^0;for(l=1,L-1,Q[l+1]=s*Q[l]+if(l>=2,d*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*s));Q};
{
my(theta=g+2,bb=g^3+g^2,tau=theta^2,N=9,R=36,mu=3,A=theta,B=theta^2-o,base=vector(N,i,((i-1)%3)*o+((i-1)\3)*bb),a=vector(N,i,base[i]+theta*base[i]^2),M=[]);
my(lines=readstr("research/results/bmd-effective-recursion-20261007/quadratic-moving-success.txt"));
for(i=1,#lines,my(bits=strsplit(lines[i],"="));if(#bits==2&&bits[1]=="MOVING_MATRIX ",M=eval(bits[2])));
if(matsize(M)!=[R,R],error("saved matrix"));
my(wi=List(),ci=List(),ss=List(),rowscale=vector(R,j,0*o),Q0=matrix(R,N-2,i,j,0*o),row=0);
for(i=1,N,for(j=i+1,N,row++;
 my(s=a[i]+a[j],delta=(a[i]-a[j])^2,den=(1+tau*a[i])*(1+tau*a[j]),q=qvec(s,delta,N-2));
 if(den==0||delta==0,error("invalid label/mark"));rowscale[row]=den^mu;
 for(k=1,N-2,Q0[row,k]=q[k]);
 if((i-1)\3==(j-1)\3,
  if(delta!=-A*s-B,error("within cubic relation"));listput(wi,row);listput(ss,s),
  listput(ci,row)
 )
));
my(Wi=Vec(wi),Ci=Vec(ci),roots=Vec(ss),Scl=matrix(R,R,i,j,rowscale[i]*M[i,j]),hp=qvec(o*z,-A*z-B,N-2),HC=matrix(N-2,N-2,i,j,polcoef(hp[j],i-1,z)));
if(matdet(HC)!=o,error("monic polynomial basis"));
my(Low=Q0*HC^-1,Vsmall=matrix(N,N-2,i,j,roots[i]^(j-1)));
if(matrix(N,N-2,i,j,Low[Wi[i],j])!=Vsmall,error("low polynomial lifts"));
my(crossLiftChecks=0,rr=0);
for(i=1,N,for(j=i+1,N,rr++;
 my(ssum=a[i]+a[j],eta=(a[i]-a[j])^2+A*ssum+B);
 if(Low[rr,3]-ssum^2!=eta,error("quadratic source lift"));
 if((i-1)\3!=(j-1)\3,if(eta==0,error("cross lift unit"));crossLiftChecks++)
));
print("NONZERO_CROSS_LIFT_CORRECTIONS = ",crossLiftChecks);

my(T=matrix(N-2,N-2,i,j,Q0[Wi[i],j])^-1*matrix(N-2,N-2,i,j,Scl[Wi[i],j]));
if(matdet(T)==0||Q0*T!=matrix(R,N-2,i,j,Scl[i,j]),error("complete block transport"));
my(H=prod(i=1,N,z-roots[i]),Hp=deriv(H),weights=vector(N,i,subst(Hp,z,roots[i])^-1),Mom=matrix(2,N,i,j,roots[j]^(i-1)*weights[j]));
if(Mom*Vsmall!=matrix(2,N-2,i,j,0*o),error("residue annihilator"));
my(Bound=matrix(N,2,i,j,Scl[Wi[i],N-2+j]),G2=Mom*Bound,dg=matdet(G2));
if(dg==0,error("retained mark has singular within boundary"));
my(Tail=matrix(N,R-N,i,j,Scl[Wi[i],N+j]),Gamma=G2^-1*Mom*Tail,Y=Tail-Bound*Gamma);
my(Lag=matrix(N,N,i,j,polcoef((H/(z-roots[j]))*weights[j],i-1,z)),PC=Lag*Y);
if(matrix(2,R-N,i,j,PC[N-2+i,j])!=matrix(2,R-N,i,j,0*o),error("high interpolation coefficients"));
my(Plo=matrix(N-2,R-N,i,j,PC[i,j]));
if(Vsmall*Plo!=Y,error("full within reconstruction"));
my(S=matrix(R-N,R-N,i,j,Scl[Ci[i],N+j])-matrix(R-N,N-2,i,j,Low[Ci[i],j])*Plo-matrix(R-N,2,i,j,Scl[Ci[i],N-2+j])*Gamma);
my(W=matrix(N,N,i,j,Scl[Wi[i],j]),Direct=matrix(R-N,R-N,i,j,Scl[Ci[i],N+j])-matrix(R-N,N,i,j,Scl[Ci[i],j])*W^-1*Tail);
if(S!=Direct,error("Schur reconstruction"));
my(Wmono=concat(Vsmall,Bound),vdet=prod(i=1,N,prod(j=i+1,N,roots[j]-roots[i])));
if(matdet(Wmono)!=-vdet*dg,error("boundary determinant sign"));
my(ds=matdet(S),dm=matdet(M));
if(ds==0||dm!=2*g^3+2*g^2+2*g+1,error("old original witness"));
print("N = ",N,"; ORIGINAL_PAIR_SIZE = ",R,"; REMAINING_SIZE = ",R-N);
print("COMPLETE_BLOCK_IDENTITIES = ",R*(N-2),"; WITHIN_IDENTITIES = ",N*(R-N),"; SCHUR_IDENTITIES = ",(R-N)^2);
print("BOUNDARY_MATRIX = ",G2,"; BOUNDARY_DETERMINANT = ",dg,"; SCHUR_DETERMINANT = ",ds,"; ORIGINAL_DETERMINANT = ",dm);
print("WITHIN_ROOTS = ",roots,"; RESIDUE_WEIGHTS = ",weights);
print("BOUNDARY_SOLUTIONS = ",Gamma);print("INTERPOLATION_COEFFICIENTS = ",Plo);print("CORRECTED_SCHUR = ",S);
my(path="research/results/bmd-within-interpolation-20261010/check.sing");
write(path,"ring r=(3,g),(x),dp; minpoly=g^4+g^3+g^2+g+1; matrix B[2][2]; matrix S[27][27]; matrix M[36][36];");
for(i=1,2,for(j=1,2,write(path,Str("B[",i,",",j,"]=",G2[i,j],";"))));
for(i=1,27,for(j=1,27,write(path,Str("S[",i,",",j,"]=",S[i,j],";"))));
for(i=1,36,for(j=1,36,write(path,Str("M[",i,",",j,"]=",M[i,j],";"))));
write(path,Str("poly db=det(B); poly ds=det(S); poly dm=det(M); db; ds; dm; if(db!=",dg," || ds!=",ds," || dm!=",dm,"){ERROR(\"determinant mismatch\");} else {print(\"INDEPENDENT_INTERPOLATION_DETERMINANTS_PASSED\");} quit;"));
my(Jcols=[1,2,3,5,6,7,8,9,11],Good=matrix(33,36,i,j,0*o),Bad=matrix(3,36,i,j,0*o),block=0,frames=List(),frameOK=1,allrows=List(Wi));
for(i=1,9,for(j=1,36,Good[i,j]=M[Wi[i],j]));
for(f1=0,2,for(f2=f1+1,2,block++;
 my(rows=vector(9,k,my(i=3*f1+(k-1)\3+1,j=3*f2+(k-1)%3+1);(i-1)*N-(i-1)*i/2+j-i),F=matrix(9,9,i,j,M[rows[i],Jcols[j]]),df=matdet(F));
 for(ri=1,9,listput(allrows,rows[ri]));listput(frames,F);print("LOCAL_FRAME = ",block,"; DET = ",df);
 if(df==0,frameOK=0,
  my(Zf=F^-1*matrix(9,36,i,j,M[rows[i],j]));
  if(F*Zf!=matrix(9,36,i,j,M[rows[i],j]),error("local frame reconstruction"));
  for(i=1,8,for(j=1,36,Good[9+8*(block-1)+i,j]=Zf[i,j]));
  for(j=1,36,Bad[block,j]=Zf[9,j])
 )
));
my(apath="research/results/bmd-within-interpolation-20261010/aggregate-check.sing");
write(apath,"ring r=(3,g),(x),dp; minpoly=g^4+g^3+g^2+g+1;");
for(bi=1,3,
 write(apath,Str("matrix F",bi,"[9][9];"));
 for(i=1,9,for(j=1,9,write(apath,Str("F",bi,"[",i,",",j,"]=",frames[bi][i,j],";"))));
 write(apath,Str("if(det(F",bi,")!=",matdet(frames[bi]),"){ERROR(\"local frame mismatch\");}"))
);
if(frameOK,
 my(Agg=matrix(33,33,i,j,Good[i,j]),da=matdet(Agg));
 print("AGGREGATE_FIRST33_RANK = ",matrank(Agg),"; DET = ",da);
 write(apath,"matrix Agg[33][33];");
 for(i=1,33,for(j=1,33,write(apath,Str("Agg[",i,",",j,"]=",Agg[i,j],";"))));
 write(apath,Str("if(det(Agg)!=",da,"){ERROR(\"aggregate determinant mismatch\");}"));
 if(da!=0,
  my(Small=matrix(3,3,i,j,Bad[i,33+j])-matrix(3,33,i,j,Bad[i,j])*Agg^-1*matrix(33,3,i,j,Good[i,33+j]),dsmall=matdet(Small));
  if(dsmall==0,error("smaller correction contradicts original"));
  my(perm=Vec(allrows),signrow=(-1)^sum(i=1,R,sum(j=i+1,R,if(perm[i]>perm[j],1,0))),frameprod=prod(bi=1,3,matdet(frames[bi])));
  if(da*dsmall*frameprod!=signrow*dm,error("full aggregate determinant reconstruction"));
  print("FULL_AGGREGATE_RECONSTRUCTION_PASSED; ROW_SIGN = ",signrow);

  print("SMALL_CORRECTION = ",Small,"; DET = ",dsmall);
  write(apath,"matrix Small[3][3];");
  for(i=1,3,for(j=1,3,write(apath,Str("Small[",i,",",j,"]=",Small[i,j],";"))));
  write(apath,Str("if(det(Small)!=",dsmall,"){ERROR(\"small correction mismatch\");}")),
  print("PRESCRIBED_AGGREGATE_PIVOT_FAILED; no alternative pivot search")
 ),
 print("PRESCRIBED_LOCAL_FRAME_FAILED; aggregate test not reached")
);
write(apath,"print(\"INDEPENDENT_AGGREGATE_CHECK_COMPLETED\"); quit;");
print("WITHIN_INTERPOLATION_COMPLETED")
}
quit;
