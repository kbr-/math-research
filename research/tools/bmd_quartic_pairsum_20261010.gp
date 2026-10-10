\\ Full N9 coordinate audit, not another normality case.
\\ Compare every new q-column via the pair-sum power basis against the saved original Schur matrix.
default(parisize,128000000);
X='X;Y='Y;s='s;B='B;
read(getenv("BMD_QUARTIC_MATRIX"));
{
my(o=Mod(1,3),N=9,r=36,P=o*(X^9-X^4+B*X),rem=vector(r+1),pairs=List(),Tmat=matrix(r,r));rem[1]=o;
for(j=1,r,rem[j+1]=lift(Mod(X*rem[j],P)));
for(u=0,N-1,for(v=u+1,N-1,listput(pairs,[u,v])));
for(j=0,r-1,
 my(alt=o*(Y-X)*(X+Y)^j,red=0);
 for(u=0,j+1,my(c=polcoef(polcoef(alt,u,X),j+1-u,Y));if(c!=0,red+=c*rem[u+1]*subst(rem[j+2-u],X,Y)));
 for(k=1,r,Tmat[k,j+1]=polcoef(polcoef(red,pairs[k][1],X),pairs[k][2],Y));
);
my(H=o*(-s^9-s^4-B*s),A=H^2+s^3+B,F=A^2-s^2*H,W=(F-B^2)/s,
 delta=Mod(-A,s*0+F)*Mod(-W/B^2,F),Jmat=matrix(r,r));
if(delta^2!=Mod(H,F)||delta^4+Mod(s,F)*delta+Mod(s^3+B,F)!=0,error("Pair equations"));
for(j=0,r-1,
 my(v=Mod(0,F));
 for(h=0,j\2,
  my(c=(binomial(2*h,h)/(h+1))*binomial(j,2*h));
  if(c%3,v+=Mod(c*s^(j-2*h)*H^(h\2),F)*if(h%2,delta,1));
 );
 my(poly=lift(v));for(k=0,r-1,Jmat[k+1,j+1]=polcoef(poly,k,s));
);
if(Tmat*Jmat!=OLD,error("Original column comparison"));
my(dt=matdet(Tmat),dn=matdet(Jmat));
print("TRANSITION_DETERMINANT=",dt);
if(dt!=o*B&&dt!=-o*B,error("Pair sum index control"));
if(dt*dn!=o*(B^11-B^6),error("Source determinant control"));
print("PAIR_SUM_ALL_COLUMNS_PASS entries=1296 index=",dt," source_det=",dn);
print("PAIR_SUM_POLYNOMIAL=",F);
print("Q2_REMAINDER=",sum(k=0,r-1,Jmat[k+1,3]*s^k));
print("QUARTIC_PAIR_SUM_COMPLETED");
}
quit;
