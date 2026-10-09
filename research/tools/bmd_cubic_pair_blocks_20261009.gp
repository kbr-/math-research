\\ Check the new cubic-pair algebra encoding on every pair of the retained
\\ six-label witness; reuse its independently checked moving matrix.
\\ Stages: all cubic roots and9 cross sums;6-row Vandermonde; exact Schur
\\ identity; forced local prefix relation. Fixed6/9/15 sizes, no size sweep.
default(parisizemax,500000000);
default(parisize,64000000);
g=ffgen(Mod(1,3)*('g^4+'g^3+'g^2+'g+1),'g);
qrow(s,d,R)={my(Q=vector(R,j,0*s));Q[1]=s^0;for(l=1,R-1,Q[l+1]=s*Q[l]+if(l>=2,d*sum(h=0,l-2,Q[h+1]*Q[l-1-h]),0*s));Q};
{
my(one=g^0,e=g,v=g+one,D=v^2-one,A=D*e^2,B=D^2*e^4-e^2,t=0*one,u=one+A+B);
my(a=[0,e+D*e^2,-e+D*e^2,1,1+v*e+D*e^2,1-v*e+D*e^2]*one);
if(A==0||t==u,error("degenerate fibre"));
for(i=1,6,if(a[i]^3+A*a[i]^2+B*a[i]!=if(i<=3,t,u),error("fibre membership")));
my(M0=matrix(15,15,i,j,0*one),row=0,sums=List(),within=[1,2,6,13,14,15],cross=[3,4,5,7,8,9,10,11,12],crosssums=List());
for(i=1,6,for(j=i+1,6,row++;
 my(s=a[i]+a[j],delta=(a[i]-a[j])^2,Q=qrow(s,delta,15));
 for(k=1,15,M0[row,k]=Q[k]);
 if((i<=3&&j<=3)||(i>3&&j>3),
  if(delta!=-A*s-B,error("within-fibre relation"));listput(sums,s),
  my(H=s^3-A*s^2+B*s,J=H+A^2*s+A*B,eta=delta+A*s+B);
  if(A*delta!=H-t-u,error("delta elimination"));
  if((H-t-u)*(J-t-u)^2!=A^3*(t-u)^2,error("degree9 polynomial"));
  if(eta==0||delta*eta^2!=(t-u)^2,error("cross divisor identity"));
  if(Q[4]-A*Q[3]+B*Q[2]!=(t+u)*Q[1],error("forced prefix relation"));
  listput(crosssums,s)
 )
));
if(#Set(Vec(crosssums))!=9,error("sum coordinates not distinct"));
my(W0=matrix(6,6,i,j,M0[within[i],j]),vd=prod(i=1,6,prod(j=i+1,6,sums[j]-sums[i])));
if(matdet(W0)!=vd||vd==0,error("within Vandermonde"));
print("ALL6_FIBRE_MEMBERS; ALL9_CROSS_COORDINATES; WITHIN_VANDERMONDE = ",vd);
print("RAW_FIXED_CROSS_FIRST9_RANK = ",matrank(matrix(9,9,i,j,M0[cross[i],j])),"; FORCED_RELATIONS_CHECKED = 9");
my(lines=readstr("research/results/bmd-cubic-fibre-coupling-20261009/witness.txt"),M=[]);
for(i=1,#lines,my(bits=strsplit(lines[i],"="));if(#bits==2&&bits[1]=="WITNESS_MATRIX ",M=eval(bits[2])));
if(matsize(M)!=[15,15],error("saved witness missing"));
print("MOVING_RAW_CROSS_FIRST9_RANK = ",matrank(matrix(9,9,i,j,M[cross[i],j])));
my(W=matrix(6,6,i,j,M[within[i],j]),dw=matdet(W));
if(dw==0,error("retained mark has singular pivot; no Schur conclusion"));
my(C=matrix(9,6,i,j,M[cross[i],j]),E=matrix(6,9,i,j,M[within[i],j+6]),F=matrix(9,9,i,j,M[cross[i],j+6]),X=W^-1*E,S=F-C*X);
if(W*X!=E,error("pivot solve"));
my(perm=concat(within,cross),sgn=(-1)^sum(i=1,15,sum(j=i+1,15,if(perm[i]>perm[j],1,0))),ds=matdet(S),dm=matdet(M));
if(dm!=sgn*dw*ds||dm==0,error("Schur determinant identity"));
print("MOVING_PIVOT_DET = ",dw,"; SCHUR_DET = ",ds,"; ORIGINAL_NORMALIZED_DET = ",dm,"; ROW_SIGN = ",sgn);
print("WITHIN_PIVOT = ",W);print("CROSS_SCHUR = ",S);
my(path="research/results/bmd-cubic-pair-algebra-20261009/check.sing");
write(path,"ring r=(3,g),(x),dp; minpoly=g^4+g^3+g^2+g+1; matrix W[6][6]; matrix S[9][9];");
for(i=1,6,for(j=1,6,write(path,Str("W[",i,",",j,"]=",W[i,j],";"))));
for(i=1,9,for(j=1,9,write(path,Str("S[",i,",",j,"]=",S[i,j],";"))));
for(case=1,2,
 my(R=matrix(9,9,i,j,if(case==1,M0[cross[i],j],M[cross[i],j])),ix=matindexrank(R));
 if(#ix[1]!=8,error("rank8 control"));
 my(E8=matrix(8,8,i,j,R[ix[1][i],ix[2][j]]),de=matdet(E8),name=if(case==1,"Ezero","Emoving"));
 if(de==0,error("rank8 minor"));
 print("RANK8_MINOR_CASE = ",case,"; ROWS = ",ix[1],"; COLUMNS = ",ix[2],"; DET = ",de);
 write(path,Str("matrix ",name,"[8][8];"));
 for(i=1,8,for(j=1,8,write(path,Str(name,"[",i,",",j,"]=",E8[i,j],";"))));
 write(path,Str("if(det(",name,")!=",de," || det(",name,")==0){ ERROR(\"rank8 minor mismatch\"); }"));
);
write(path,Str("poly dw=det(W); poly ds=det(S); dw; ds; if(dw!=",dw," || ds!=",ds,"){ ERROR(\"factor mismatch\"); } else {print(\"INDEPENDENT_SCHUR_FACTORS_PASSED\");} quit;"));
print("CUBIC_PAIR_BLOCKS_COMPLETED");
}
quit;
