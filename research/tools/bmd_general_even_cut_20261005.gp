\\ Audit U=g*F_A+x^(2r+1)*F_B, x^2=1+epsilon*t, in odd characteristic.
\\ The theorem predicts F_min(B,m-1)+g*span(t^e), E the exact core orders.
\\ Seven structural controls, each at most eight source columns; all coefficients
\\ through each candidate leading order are checked, not merely a final rank.
default(parisizemax, 100000000);
default(nbthreads, 1);
if(default(nbthreads)!=1,error("thread setting failed"));
liftcoef(exps,v,h,p,e)=sum(l=1,#exps,v[l]*Mod(binomial(exps[l]/2,h),p))*Mod(2,p)^e;
{
my(t='t,z='z,cases=[
 [3,3,3,2,0,t^2],
 [3,3,3,2,0,(t-1)^2],
 [3,0,4,2,0,(t-1)^2],
 [5,1,1,3,0,(t+1)^3],
 [3,2,1,0,0,1],
 [5,1,3,1,2,t+1],
 [3,-1,0,2,0,t^2]
],checked=0,mutations=0);
for(k=1,#cases,
 my(v=cases[k],p=v[1],A=v[2],B=v[3],m=v[4],r=v[5],g=Mod(1,p)*v[6],C=B-m,b=min(B,m-1),D=A+B+2,exps=List(),E=List(),Pred=List(),old=0);
 if(poldegree(g,t)!=m,error("wrong cut degree"));
 for(j=0,A,listput(exps,2*j));
 for(j=0,C,listput(exps,2*r+1+2*j));
 exps=Vec(exps);
 if(#exps,
  my(dx=vecmax(exps),W=matrix(dx+1,#exps,h,j,Mod(binomial(exps[j],h-1),p)));
  for(h=0,dx,
    my(rk=matrank(matrix(h+1,#exps,i,j,W[i,j])));
    if(rk>old,listput(E,h);old=rk);
  );
  E=Vec(E);
  if(#E!=#exps,error("core dimension"));
  my(pivot=matrix(#E,#exps,i,j,W[E[i]+1,j]),V=pivot^-1);
  for(j=1,#E,
    my(e=E[j],vcol=vector(#exps,l,V[l,j])~);
    for(h=0,e,
      my(c=liftcoef(exps,vcol,h,p,e));
      if(c!=Mod(if(h==e,1,0),p),error("lift has a pole or wrong reduction"));
      checked++;
    );
    if(e>0 && A>=0,
      my(bad=vcol,detected=0);bad[1]+=1;
      for(h=0,e-1,if(liftcoef(exps,bad,h,p,e)!=0,detected=1));
      if(!detected,error("mutated positive-order lift escaped integrality check"));
      mutations++;
    );
  );
 , E=[]);
 for(j=0,B,
   my(qr=divrem(t^j,g));
   if(g*qr[1]+qr[2]!=t^j || poldegree(qr[2],t)>=m || poldegree(qr[1],t)>C,error("division source identity"));
 );
 for(j=0,b,listput(Pred,t^j));
 for(j=1,#E,listput(Pred,g*t^E[j]));
 Pred=Vec(Pred);
 if(#Pred!=D,error("full source dimension"));
 my(L=vecmax(vector(D,j,poldegree(Pred[j],t)))+1,M=matrix(L,D,i,j,polcoef(Pred[j],i-1,t)));
 if(matrank(M)!=D,error("limit reductions dependent"));
 my(jrank=matrank(matrix(D,D,i,j,polcoef(Pred[j],i-1,t))));
 if(k==1 && jrank!=7,error("cut-at-mark negative control"));
 if(k==2 && jrank!=8,error("finite-cut moved-mark control"));
 print("case=",k," p=",p," A=",A," B=",B," m=",m," r=",r," g=",g," core_orders=",E," dimension=",D," limit_degree=",L-1," first_D_jet_rank=",jrank);
);
my(M=6,start=6,U=(1+sqrt(1+4*z+O(z^M)))/2,H=matrix(M,M,s,j,my(i=start+j-1,n=s-1);if(n==0,1,binomial(i-n-1,n)+2*binomial(i-n-1,n-1))));
for(s=0,M-1,for(j=1,M,
 if(polcoef(U^(start+j-1),s,z)!=H[s+1,j],error("even coefficient identity"));
 if(denominator(H[s+1,j])!=1,error("nonintegral even coefficient"));
));
if(matdet(H)!=1,error("integer top block"));
forprime(p=3,5,
 my(Hp=matrix(M,M,s,j,Mod(H[s,j],p)*Mod(4,p)^(-(s-1))));
 if(matdet(Hp)!=Mod(4,p)^(-M*(M-1)/2),error("dyadic top block"));
);
my(p=3,mm=4,q=9,ep='e,Cv=matrix(mm,mm,h,j,Mod(binomial(j-1,h-1),p)),top=matrix(mm,mm),matched=0);
for(col=1,mm,
 my(i=q-mm+col,ev=Mod(2,p)^i*ep^(-i)*sum(j=0,i,if(j%2,0,binomial(i,j)*(-1)^(i-j)*(1+ep*t)^(j/2))));
 my(phi=vector(mm,h,sum(j=h-1,i\2,binomial(j,h-1)*polcoef(ev,j,t)))~,psi=Cv^-1*phi);
 for(ss=0,mm-1,
  my(value=2*ep^(i-ss)*psi[ss+1],hs=if(ss==0,1,binomial(i-ss-1,ss)+2*binomial(i-ss-1,ss-1)));
  if(valuation(value,ep)<0,error("confluent top system not integral"));
  top[ss+1,col]=polcoef(value+O(ep),0,ep);
  if(top[ss+1,col]!=(-1)^i*Mod(4,p)^(i-ss)*hs,error("confluent top scaling mismatch"));
  matched++;
 );
);
if(matdet(top)!=(-1)^sum(j=1,mm,q-mm+j)*Mod(4,p)^(mm*(q-mm+1)),error("confluent determinant"));
print("actual Hasse top block: p3,m4,q9,root1 multiplicity4; matched entries=",matched,"; scaled system integral; determinant a unit");
print("integer even-cut top block: m=6, indices6..11, determinant=1; every coefficient agrees with the generating series");
print("removable-value H_3(6)=",H[4,1],"; dyadic top block a unit at p3,p5");
print("all checked lift coefficients=",checked,"; mutated positive-order lifts rejected=",mutations);
print("PASS");
}
