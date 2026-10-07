\\ Test the generic slope stratum of conj:cube-balanced-limit-generic-classical.
\\ Exactly N=7, p=3, degree two: labels 0,eps,b eps,1,1+c eps,1+d eps,1+e eps.
\\ No finite-field slope specialization. K=F3(b,c,d,e); y=x^2=1+T.
\\ Stages: even 11-row and mixed 12-row coefficient lattices, exact DVR saturation,
\\ complete row operations/limit bases, then their support and Hasse rank.
\\ Precision 12 contains every coefficient needed by the archived sample's 11 divisions.
\\ A precision failure is inconclusive, never a generic assertion.
default(parisizemax,2000000000);
default(parisize,128000000);
y='y;b='b;c='c;d='d;e='e;
bet(j)={my(v=if(j%3==1,-1,1));j=j\3;while(j>0,if(j%3==2,return(0));j=j\3);v};
{
my(one=Mod(1,3),aa=[0,1,b],bb=[0,c,d,e],cut=12,precision=12,nc=26,allbasis=List(),valuations=List());
print("FIELD F3(b,c,d,e); slopes ",aa," and ",bb,"; y=x^2; common y shift ",cut);
for(block=1,2,
 my(nr=if(block==1,11,12),prec=precision,coefs=vector(prec+1,m,matrix(nr,nc,i,j,0*one)),pairs=List());
 if(block==1,
  coefs[1][1,cut+1]=one;coefs[1][2,cut+1]=-one;coefs[1][2,cut+2]=one;
  for(i=1,3,for(j=i+1,3,listput(pairs,[aa[i],aa[j],0,0])));
  for(i=1,4,for(j=i+1,4,listput(pairs,[bb[i],bb[j],1,1]))),
  for(i=1,3,for(j=1,4,listput(pairs,[aa[i],bb[j],0,1])))
 );
 for(k=1,#pairs,
  my(q=pairs[k],r=k+if(block==1,2,0));
  for(m=0,prec,
   my(poly=0*one);
   for(u=0,m,my(v=m-u,fac=one*bet(u)*bet(v)*q[1]^u*q[2]^v);
    if(fac!=0,poly+=fac*y^(cut+if(block==1,q[3],0)-q[3]*u-q[4]*v)));
   poly*=(y-1)^m;
   if(poldegree(poly,y)>=nc,error("coefficient support exceeds retained window"));
   for(j=0,nc-1,coefs[m+1][r,j+1]=polcoef(poly,j,y))
  )
 );
 my(step=0,total=0);
 print("BLOCK ",block," ROWS ",nr," COLUMNS ",nc," PRECISION ",prec);
 while(1,
  my(M0=coefs[1],ix=matindexrank(M0)[1],rk=#ix);
  print("STEP ",step," REMAINING_PRECISION ",prec," RANK ",rk);
  if(rk==nr,break);
  if(prec<1,error("precision exhausted; no conclusion"));
  my(ker=matker(M0~),P=matrix(nr,nr,i,j,if(i<=rk,if(j==ix[i],one,0*one),ker[j,i-rk])));
  if(matrank(P)!=nr,error("noninvertible transform"));
  if(M0~*ker!=matrix(nc,nr-rk,i,j,0*one),error("kernel reconstruction failure"));
  print("PIVOT_ROWS ",ix," KERNEL_ROWS ",ker~);
  my(trans=vector(prec+1,m,P*coefs[m]));
  coefs=vector(prec,m,matrix(nr,nc,i,j,if(i<=rk,trans[m][i,j],trans[m+1][i,j])));
  total+=nr-rk;prec--;step++
 );
 my(B=coefs[1],expected=if(block==1,vector(11,i,i-7),concat([-7],vector(11,i,i-6))),supp=List());
 for(j=0,nc-1,if(sum(i=1,nr,if(B[i,j+1]!=0,1,0))>0,listput(supp,j-cut)));
 print("VALUATION ",total," SUPPORT ",Vec(supp)," EXPECTED ",expected);
 print("LIMIT_BASIS ",vector(nr,i,sum(j=0,nc-1,B[i,j+1]*y^j)));
 if(Vec(supp)!=expected,error("generic support differs from sampled monomial prediction"));
 listput(valuations,total);listput(allbasis,B)
);
my(exps=vecsort(concat(vector(11,i,2*(i-7)),concat([-13],vector(11,i,2*(i-6)+1)))));
my(H=matrix(23,23,i,j,Mod(binomial(exps[i]+13,j-1),3)));
print("FULL_LAURENT_EXPONENTS ",exps);
print("HASSE_RANK ",matrank(H)," OF 23; shift 13 preserves jets away from zero");
print("RESIDUE_COUNTS_MOD3 ",vector(3,r,sum(i=1,23,if(lift(Mod(exps[i],3))==r-1,1,0))));
print("FUNCTION_VALUATION ",vecsum(Vec(valuations))," BLOCK_VALUATIONS ",Vec(valuations));
if(matrank(H)!=22,error("unexpected Hasse rank"));
print("GENERIC_SEVEN_LIMIT_COMPLETED")
}
quit;
