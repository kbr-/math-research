\\ Exact monic Schur-frame test of a stronger branch family, not a normality grid.
\\ Controls: N4 known normalized polynomial B; N9 quadratic family excluded by a proved relation.
\\ Target: N9 roots of X^9-X^4+B*X. The36-square determinant has B-degree<=floor(378/8)=47.
default(parisize,128000000);
X='X;Y='Y;B='B;
{
my(o=Mod(1,3),ss=(X+Y)*o,dd=(X-Y)^2*o,q=vector(36));q[1]=o;
for(j=1,35,q[j+1]=ss*q[j]+dd*sum(k=0,j-2,q[k+1]*q[j-1-k]));
for(ci=1,3,
 my(N=if(ci==1,4,9),d=if(ci==3,4,2),r=N*(N-1)/2,P=o*(X^N-X^d+B*X),
 rem=vector(r+1),pairs=List(),M=matrix(r,r));rem[1]=o;
 for(j=1,r,rem[j+1]=lift(Mod(X*rem[j],P)));
 for(u=0,N-1,for(v=u+1,N-1,listput(pairs,[u,v])));
 for(j=0,r-1,
  my(alt=(Y-X)*q[j+1],red=0);
  for(u=0,j+1,my(c=polcoef(polcoef(alt,u,X),j+1-u,Y));if(c!=0,red+=c*rem[u+1]*subst(rem[j+2-u],X,Y)));
  for(k=1,r,M[k,j+1]=polcoef(polcoef(red,pairs[k][1],X),pairs[k][2],Y));
  if(red!=sum(k=1,r,M[k,j+1]*(X^pairs[k][1]*Y^pairs[k][2]-X^pairs[k][2]*Y^pairs[k][1])),error("Alternant encoding"));
 );
 print("FAMILY_MATRIX N=",N," exponent=",d," size=",r);
 my(D=matdet(M));
 if(ci==1&&D!=o*B,error("Known four-label control"));
 if(ci==2&&D!=0,error("Quadratic obstruction control"));
 if(ci==3&&poldegree(D,B)>47,error("Degree bound"));
 print("NORMALIZED_DETERMINANT=",D);
 if(D!=0,print("FACTORIZATION=",factor(D)),
  if(ci==3,my(K=matker(M));print("NULLITY=",matsize(K)[2]);print("FIRST_KERNEL=",K[,1]);if(M*K!=0,error("Kernel check")))
 );
 if(ci==3,print("TARGET_MATRIX=",M));
);
print("QUARTIC_BRANCH_FAMILY_COMPLETED");
}
quit;
