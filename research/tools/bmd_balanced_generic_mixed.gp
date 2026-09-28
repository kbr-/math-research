\\ Generic-parameter audit of the SAME 3+3 smoothing mechanism.
\\ No new dimension: compute mixed function-lattice valuation over F3(b,c,d).
\\ If it is31, the known internal valuation18 and specialized original
\\ determinant2 eps49 prove generic six-label limiting normality.
\\ Mixed9 rows,25 coefficient columns, precision12; PARI exact rational kernels.
\\ Stages: construct the mixed epsilon series on y=x²; saturated residue ranks;
\\ retain all generic kernel transformations and the resulting limit basis.
default(parisizemax,512000000);
default(parisize,128000000);
y='y;b='b;c='c;d='d;
bet(j)={my(v=if(j%3==1,-1,1));j=j\3;while(j>0,if(j%3==2,return(0));j=j\3);v};
{
my(one=Mod(1,3),aa=[0,1,b],bb=[0,c,d],cut=12,prec=12,nr=9,nc=25);
my(coefs=vector(prec+1,m,matrix(nr,nc,i,j,0*one)));
for(i=1,3,for(j=1,3,
 for(m=0,prec,
  my(poly=0*one);
  for(u=0,m,my(v=m-u,fac=one*bet(u)*bet(v)*aa[i]^u*bb[j]^v);
   if(fac!=0,poly+=fac*y^(cut-v)));
  poly*=(y-1)^m;
  for(k=0,nc-1,coefs[m+1][3*(i-1)+j,k+1]=polcoef(poly,k,y));
 )));
print("GENERIC_MIXED_FIELD = F3(b,c,d)");
print("SLOPES = ",aa," and ",bb,"; y=x²; common factor y^",cut," after removing x");
print("ROWS9 COLUMNS25 PRECISION12");
my(step=0,total=0);
while(1,
 my(M0=coefs[1],ix=matindexrank(M0)[1],rk=#ix);
 print("GENERIC_SATURATION_STEP ",step," precision ",prec," residue_rank ",rk);
 if(rk==nr,break);
 if(prec<1,error("precision exhausted"));
 my(ker=matker(M0~),P=matrix(nr,nr,i,j,if(i<=rk,if(j==ix[i],one,0*one),ker[j,i-rk])));
 if(matrank(P)!=nr,error("noninvertible transform"));
 print("PIVOT_ROWS = ",ix,"; KERNEL_ROWS = ",ker~);
 my(trans=vector(prec+1,m,P*coefs[m]));
 coefs=vector(prec,m,matrix(nr,nc,i,j,if(i<=rk,trans[m][i,j],trans[m+1][i,j])));
 total+=nr-rk;prec--;step++;
);
print("GENERIC_MIXED_VALUATION = ",total);
print("GENERIC_LIMIT_BASIS = ",vector(nr,i,sum(k=0,nc-1,coefs[1][i,k+1]*y^k)));
print("GENERIC_MIXED_AUDIT_COMPLETED");
}
quit;
