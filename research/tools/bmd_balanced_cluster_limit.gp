\\ Test whether simultaneous 3+3 smoothing repairs the failed sequential
\\ degree-two characteristic-three limit. This is one mechanism test, not
\\ a dimension series or a proof of all-dimensional normality.
\\ Six roots: 0, eps, eps*g, 1, 1+eps*g^2, 1+eps*(1+g), over F_27.
\\ Stages: exact bounded series; coefficientwise row saturation using PARI
\\ kernels/rank; first-17-jet test; positive and sequential negative controls.
\\ Precision24, 17 rows, 99 Laurent-coordinate columns; <= 256 MB PARI stack.
\\ Full output is retained by compute.sh and save-run-output.py.
default(parisizemax,256000000);
default(parisize,64000000);
x='x;
bet(j)={my(v=if(j%3==1,-1,1));j=j\3;while(j>0,if(j%3==2,return(0));j=j\3);v};
{
my(ff=ffinit(3,3,'a),g=ffgen(ff,'a),one=g^0);
my(prec=24,cut=24,nr=17,nc=4*24+3,base=[0,0,0,1,1,1],slopes=[0,1,g,0,g^2,1+g]);
my(coefs=vector(prec+1,m,matrix(nr,nc,i,j,0*one)));
my(pairs=List(),rowno=2);
for(i=1,6,for(j=i+1,6,listput(pairs,[i,j])));
pairs=Vec(pairs);
if(#pairs!=15,error("pair count"));
for(i=1,3,for(j=i+1,3,if(slopes[i]==slopes[j],error("first cluster collision"))));
for(i=4,6,for(j=i+1,6,if(slopes[i]==slopes[j],error("second cluster collision"))));
coefs[1][1,2*cut+1]=one;
coefs[1][2,2*cut+1]=-one;
coefs[1][2,2*cut+3]=one;
for(k=1,#pairs,
  my(ii=pairs[k][1],jj=pairs[k][2]);
  for(m=0,prec,
    my(poly=0*one);
    for(u=0,m,
      my(v=m-u,fac=bet(u)*bet(v)*slopes[ii]^u*slopes[jj]^v);
      if(fac!=0,poly+=fac*x^(2*cut+base[ii]+base[jj]-2*(base[ii]*u+base[jj]*v)))
    );
    poly*= (x^2-1)^m;
    for(d=0,nc-1,coefs[m+1][k+2,d+1]=polcoef(poly,d,x));
  );
);
print("TEST = simultaneous balanced 3+3 coefficientwise limit; characteristic3");
print("FIELD_MODULUS = ",ff);
print("BASE_CENTERS = ",base,"; SLOPES = ",slopes);
print("ROWS = 1,T, then pairs ",pairs);
print("T=x^2-1; common multiplier x^",2*cut);
print("PRECISION = ",cut,"; ROWS = ",nr,"; COEFFICIENT_COLUMNS = ",nc);
my(step=0,rk=0);
while(1,
  my(M0=coefs[1],ix=matindexrank(M0)[1]);rk=#ix;
  print("SATURATION_STEP ",step," precision ",prec," residue_rank ",rk);
  if(rk==nr,break);
  if(prec<1,error("precision exhausted; no conclusion"));
  my(ker=matker(M0~),P=matrix(nr,nr,i,j,if(i<=rk,if(j==ix[i],one,0*one),ker[j,i-rk])));
  if(matrank(P)!=nr,error("row transform not invertible"));
  print("PIVOT_ROWS = ",ix,"; KERNEL_ROWS = ",ker~);
  my(trans=vector(prec+1,m,P*coefs[m]));
  coefs=vector(prec,m,matrix(nr,nc,i,j,if(i<=rk,trans[m][i,j],trans[m+1][i,j])));
  prec--;step++;
);
my(B0=coefs[1],J=matrix(nr,nr,i,j,sum(d=0,nc-1,B0[i,d+1]*binomial(d,j-1))));
print("SATURATED_LIMIT_BASIS (Laurent exponents after removing common x^",2*cut,"):");
for(i=1,nr,my(terms=List());for(d=0,nc-1,if(B0[i,d+1]!=0,listput(terms,[d-2*cut,B0[i,d+1]])));print(i," ",Vec(terms)));
print("FIRST_17_JET_MATRIX = ",J);
print("SIMULTANEOUS_JET_RANK = ",matrank(J));
print("SIMULTANEOUS_JET_DETERMINANT = ",matdet(J));
print("SIMULTANEOUS_JET_LEFT_KERNEL = ",matker(J~));
my(exps=[0,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21]);
my(neg=matrix(17,17,i,j,one*binomial(exps[i],j-1)));
my(pos=matrix(17,17,i,j,one*binomial(i-1,j-1)));
print("SEQUENTIAL_NEGATIVE_CONTROL_EXPONENTS = ",exps);
print("SEQUENTIAL_NEGATIVE_CONTROL_RANK = ",matrank(neg));
print("POSITIVE_CONSECUTIVE_CONTROL_RANK = ",matrank(pos));
if(matrank(neg)==17||matrank(pos)!=17,error("control failed"));
print("BALANCED_CLUSTER_LIMIT_TEST_COMPLETED");
}
quit;
