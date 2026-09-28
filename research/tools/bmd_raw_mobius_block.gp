\\ Audit the complete raw block used by the additive-subgroup proof.
\\ Q=27 is the first block that transports a nontrivial q=9 obstruction.
\\ No new dimension or parameter series: check all 25 block columns,
\\ reciprocal duality, and the symbolic relation for every A,B,tau.
X='X; Y='Y; u='u; aa='aa; bb='bb;
{
my(one=Mod(1,3),s=(X+Y)*one,delta=(X-Y)^2*one,Q=27,m=12,h=14);
my(q=vector(25));q[1]=one;
for(l=1,24,q[l+1]=s*q[l]+delta*sum(j=0,l-2,q[j+1]*q[l-1-j]));
my(coeff=vector(25));
for(l=0,24,
  my(raw=sum(i=0,l+2,binomial(h,i)*binomial(h,l+2-i)*X^i*Y^(l+2-i))*one);
  if(raw!=delta*q[l+1],error("truncated power encoding failed ",l));
  if(poldegree(q[l+1],X)>m||poldegree(q[l+1],Y)>m,error("bidegree failed"));
  my(recip=0);
  for(i=0,l,recip+=polcoef(polcoef(q[l+1],i,X),l-i,Y)*X^(m-i)*Y^(m-l+i));
  if(recip!=q[25-l],error("reciprocity failed ",l)));
my(F=(X^9*(1-u*X)^3*(1-u*Y)^12+Y^9*(1-u*Y)^3*(1-u*X)^12
      -aa*(X^3*(1-u*X)^9*(1-u*Y)^12+Y^3*(1-u*Y)^9*(1-u*X)^12)
      +bb*(X*(1-u*X)^11*(1-u*Y)^12+Y*(1-u*Y)^11*(1-u*X)^12))*one);
my(rebuilt=0);
for(l=0,24,
  my(found=0);
  for(i=0,l,
    my(c=polcoef(polcoef(q[l+1],i,X),l-i,Y));
    if(c!=0,
      coeff[l+1]=polcoef(polcoef(F,i,X),l-i,Y)/c;found=1;break));
  if(!found,error("zero original column ",l));
  rebuilt+=coeff[l+1]*q[l+1]);
if(rebuilt!=F,error("Mobius transformed relation leaves raw block"));
my(PX=(X^9-aa*X^3*(1-u*X)^6+bb*X*(1-u*X)^8)*one);
my(PY=subst(PX,X,Y));
if(F!=(1-u*X)^3*(1-u*Y)^12*PX+(1-u*Y)^3*(1-u*X)^12*PY,
  error("transported branch polynomial identity failed"));
if(coeff[25]!=(u^15-aa*u^21+bb*u^23)*one,error("last coefficient failed"));
print("FIELD = F3[aa,bb,u]; ADDITIVE_POLYNOMIAL = Z^9-aa*Z^3+bb*Z");
print("RAW_BLOCK = q0..q24; BIDEGREE_BOUND = (12,12)");
print("TRUNCATED_POWER_IDENTITIES_CHECKED = 25");
print("RECIPROCAL_IDENTITIES_CHECKED = 25");
print("TRANSPORTED_RELATION_COEFFICIENTS = ",coeff);
print("BRANCH_POLYNOMIAL_IDENTITY_CHECKED = 1");
print("TOP_COEFFICIENT = ",coeff[25]);
print("RAW_MOBIUS_BLOCK_COMPLETED");
}
quit;
