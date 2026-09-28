\\ One symbolic test of an all-N Calogero-Sutherland eigenpolynomial hypothesis.
\\ Use the already solved five-root model over F3, not another dimension.
\\ Stages: original Schur coordinates; invariant operator images; exact
\\ coefficient conditions for coupling and eigenvalue; independent chain-rule
\\ checks on all elementary generators and all quadratic generator pairs.
X='X; Y='Y; e1='e1; e2='e2; e3='e3; e4='e4; e5='e5;
ee=[e1,e2,e3,e4,e5];
ef(j)=if(j==0,Mod(1,3),if(j<=5,ee[j]*Mod(1,3),0));
mc(f,ex)={for(i=1,5,f=polcoef(f,ex[i],ee[i]));return(f);};
wm(w)={
my(out=List());
for(k5=0,w\5,for(k4=0,(w-5*k5)\4,
for(k3=0,(w-5*k5-4*k4)\3,for(k2=0,(w-5*k5-4*k4-3*k3)\2,
  listput(out,[w-5*k5-4*k4-3*k3-2*k2,k2,k3,k4,k5])))));
return(Vec(out));
};
{
my(one=Mod(1,3),nn=5,rr=10,pairs=List());
for(i=0,nn-1,for(j=i+1,nn-1,listput(pairs,[i,j])));pairs=Vec(pairs);
my(ss=(X+Y)*one,dd=(X-Y)^2*one,q=vector(rr));q[1]=one;
for(l=1,rr-1,q[l+1]=ss*q[l]+dd*sum(j=0,l-2,q[j+1]*q[l-1-j]));
my(pp=X^nn+sum(j=1,nn,(-1)^j*ef(j)*X^(nn-j)));
my(rems=vector(rr+1,j,lift(Mod(X^(j-1)*one,pp))),C=matrix(rr,rr));
for(l=0,rr-1,
  my(anti=(Y-X)*q[l+1],red=0);
  for(i=0,l+1,for(j=0,l+1-i,
    my(co=polcoef(polcoef(anti,i,X),j,Y));
    if(co!=0,red+=co*rems[i+1]*subst(rems[j+1],X,Y))));
  for(k=1,rr,C[k,l+1]=polcoef(polcoef(red,pairs[k][1],X),pairs[k][2],Y)));
my(phi=matdet(C));
if(phi==0,error("known five-root normality control failed"));
my(mon15=wm(15),mon13=wm(13));
my(rebuilt=sum(j=1,#mon15,mc(phi,mon15[j])*prod(i=1,5,ee[i]^mon15[j][i])));
if(rebuilt!=phi,error("normalized weight is not 15"));
print("FIELD = F3(e1,e2,e3,e4,e5); ROOT_COUNT = 5; PAIR_RANK = 10");
print("SCHUR_COORDINATES = ",C);
print("PHI = ",phi);
my(ps=vector(11));ps[1]=nn*one;
for(k=1,10,ps[k+1]=sum(j=1,min(k-1,nn),(-1)^(j-1)*ef(j)*ps[k-j+1])
  +if(k<=nn,(-1)^(k-1)*k*ef(k),0));
my(A=matrix(nn,nn),B=matrix(nn,nn));
for(r=1,nn,for(s=1,nn,
  A[r,s]=sum(i=0,r-1,sum(j=0,s-1,(-1)^(i+j)*ef(r-1-i)*ef(s-1-j)*ps[i+j+1]));
  B[r,s]=sum(i=0,r-1,sum(j=0,s-1,(-1)^(i+j)*ef(r-1-i)*ef(s-1-j)*ps[i+j+3]))));
my(first=vector(nn,i,deriv(phi,ee[i])));
my(second=matrix(nn,nn,i,j,deriv(first[i],ee[j])));
my(Eul=sum(r=1,nn,r*ef(r)*first[r]));
my(U=sum(r=1,nn,sum(s=1,nn,A[r,s]*second[r,s])));
my(W=-sum(r=2,nn,binomial(nn-r+2,2)*ef(r-2)*first[r]));
my(Gamma=sum(r=1,nn,r*(2*nn-r-1)/2*ef(r)*first[r]));
my(H0=sum(r=1,nn,sum(s=1,nn,B[r,s]*second[r,s]))+Eul);
my(H1=2*Gamma-(nn-1)*Eul);
if(Eul!=0,error("Euler degree-15 control failed modulo3"));
my(eq=matrix(#mon15,2,i,j,if(j==1,mc(H1,mon15[i]),-mc(phi,mon15[i]))));
my(rhs=vector(#mon15,i,-mc(H0,mon15[i]))~);
my(harm=matrix(#mon13,2,i,j,if(j==1,mc(U,mon13[i]),2*mc(W,mon13[i]))));
print("RATIONAL_LAPLACIAN_PART = ",U);
print("PAIR_DERIVATIVE_PART = ",W);
print("TRIGONOMETRIC_FREE_PART = ",H0);
print("TRIGONOMETRIC_COUPLING_PART = ",H1);
print("HARMONIC_COEFFICIENT_RANK = ",matrank(harm));
my(witness_a=[8,0,0,0,1],witness_b=[10,0,1,0,0]);
if(mc(U,witness_a)!=0||mc(W,witness_a)!=one||
   mc(U,witness_b)!=2*one||mc(W,witness_b)!=2*one,
   error("two-coefficient coupling contradiction failed"));
print("HARMONIC_WITNESS_e1^8_e5 = [",mc(U,witness_a),",",mc(W,witness_a),"]");
print("HARMONIC_WITNESS_e1^10_e3 = [",mc(U,witness_b),",",mc(W,witness_b),"]");
my(centered=subst(phi,e1,0));
my(center_factor=e2*(e2*e3+e5)*(e2^4+e3*e5-e4^2)*one);
if(centered!=center_factor,error("centered control factorization failed"));
print("CENTERED_PHI = e2*(e2*e3+e5)*(e2^4+e3*e5-e4^2)");
print("EIGEN_PARAMETER_RANK = ",matrank(eq));
print("EIGEN_AUGMENTED_RANK = ",matrank(matconcat([eq,rhs])));
my(lead=0);
for(i=1,#mon15,if(mc(phi,mon15[i])!=0,lead=i;break));
for(coupling=0,2,
  my(ev=mc(H0+coupling*H1,mon15[lead])/mc(phi,mon15[lead]));
  print("COUPLING ",coupling," EIGENVALUE_CANDIDATE = ",ev,
        " RESIDUAL_ZERO = ",H0+coupling*H1-ev*phi==0));
\\ Check the invariant formulas without evaluating phi in root variables.
my(roots=['a,'b,'c,'d,'f],poly=prod(i=1,nn,X+roots[i])*one);
my(er=vector(nn,r,polcoef(poly,nn-r,X)),checks=0);
for(r=1,nn,for(s=1,nn,
  my(ad=sum(i=1,nn,deriv(er[r],roots[i])*deriv(er[s],roots[i])));
  my(bd=sum(i=1,nn,roots[i]^2*deriv(er[r],roots[i])*deriv(er[s],roots[i])));
  if(substvec(A[r,s],ee,er)!=ad,error("Laplacian chain rule failed ",r,",",s));
  if(substvec(B[r,s],ee,er)!=bd,error("Euler-weighted chain rule failed ",r,",",s));
  checks+=2));
for(r=1,nn,
  my(wd=0,gd=0);
  for(i=1,nn,for(j=i+1,nn,
    wd+=(deriv(er[r],roots[i])-deriv(er[r],roots[j]))/(roots[i]-roots[j]);
    gd+=(roots[i]^2*deriv(er[r],roots[i])-roots[j]^2*deriv(er[r],roots[j]))/(roots[i]-roots[j])));
  if(wd!=if(r>=2,-binomial(nn-r+2,2)*if(r==2,one,er[r-2]),0),
    error("pair derivative chain rule failed ",r));
  if(gd!=r*(2*nn-r-1)/2*er[r],error("weighted pair chain rule failed ",r));
  checks+=2);
if(substvec(A[1,1]+one,ee,er)==sum(i=1,nn,deriv(er[1],roots[i])^2),
   error("altered coefficient negative control missed"));
print("ALL_INVARIANT_OPERATOR_IDENTITIES_CHECKED = ",checks);
print("ALTERED_COEFFICIENT_DETECTED = 1");
print("TERNARY_BOUNDARY_CMS_COMPLETED");
}
quit;
