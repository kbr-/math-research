\\ Audit the proposed normalized coproduct identification on the already
\\ retained Q=27 raw block, not a new root count or a size series.
\\ Check all 25 polynomials, the diagonal normalization, and the distinct
\\ ordinary repeated-root power source's Frobenius restriction.
X='X;Y='Y;z='z;a='a;b='b;
{
my(one=Mod(1,3),Q=27,m=12,d=24,C=binomial(d,m)*one);
if(C==0,error("normalizing binomial is not a unit"));
my(s=(X+Y)*one,delta=(X-Y)^2*one,q=vector(d+1));q[1]=one;
for(l=1,d,q[l+1]=s*q[l]+delta*sum(i=0,l-2,q[i+1]*q[l-1-i]));
for(j=0,d,
  my(polar=0);
  for(i=0,j,
    if(m-i>=0 && m-i<=d-j,
      polar+=binomial(j,i)*binomial(d-j,m-i)*X^i*Y^(j-i)));
  polar*=(-1)^j/C;
  if(polar!=q[j+1],error("normalized coproduct mismatch ",j));
  if(subst(q[j+1],Y,X)!=(-X)^j*one,error("diagonal normalization mismatch ",j)));
my(ordinary=(z-a)^m*(z-b)^m*one);
if(deriv(ordinary,z)!=0,error("ordinary product is not a cube"));
if(deriv(q[2],X)==0,error("non-cube raw column negative control missed"));
print("FIELD = F3; Q = 27; m = 12; NORMALIZING_BINOMIAL = ",C);
print("POLARIZATION_IDENTITIES_CHECKED = 25");
print("DIAGONAL_IDENTITIES_CHECKED = 25");
print("ORDINARY_ROOT_PRODUCT_NONZERO_EXPONENTS = ",
  select(j->polcoef(ordinary,j,z)!=0,vector(d+1,j,j-1)));
print("RAW_q1_X_DERIVATIVE = ",deriv(q[2],X));
print("RAW_POLARIZATION_CONTROL_COMPLETED");
}
quit;
