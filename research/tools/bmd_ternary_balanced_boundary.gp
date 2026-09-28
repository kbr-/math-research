\\ Test a named all-N coefficient-grouping hypothesis over F3:
\\ Phi_N is a scalar times the product of the four-root cubic over all
\\ four-subsets. Both sides have degree 3*binomial(N,4).
\\ It predicts zero on every four-root pair-balance hyperplane.
\\ The complete first test is the generic five-root hyperplane, scaled
\\ to [0,1,t,1+t,u]; this dimension is already solved. No larger N is run.
\\ Stages: exact q recurrence, pair evaluation, compiled determinant,
\\ exact collision-factor removal, and the known four-root zero control.
t='t; u='u;
{
my(one=Mod(1,3),aa=[0,1,t,1+t,u],rr=10,Q=matrix(rr,rr),V=one,row=0);
for(i=1,5,for(j=i+1,5,
  row++;
  my(s=(aa[i]+aa[j])*one,d=(aa[i]-aa[j])^2*one,q=vector(rr));
  q[1]=one;
  for(l=1,rr-1,q[l+1]=s*q[l]+d*sum(k=0,l-2,q[k+1]*q[l-1-k]));
  for(l=1,rr,Q[row,l]=q[l]);
  V*=aa[j]-aa[i]));
print("FIELD = F3(t,u); ROOTS = [0,1,t,1+t,u]; BALANCE = 0+(1+t)=1+t");
print("PAIR_PREFIX = ",Q);
print("Computing the generic balanced-hyperplane determinant.");
my(det=matdet(Q),phi=det/V^3);
if(type(phi)=="t_RFRAC",error("collision normalization did not divide exactly"));
if(det!=V^3*phi,error("normalized determinant identity failed"));
my(control=matrix(6,6),r=0);
for(i=1,4,for(j=i+1,4,r++;for(l=1,6,
  my(source=0);
  for(ii=1,5,for(jj=ii+1,5,source++;if(ii==i&&jj==j,control[r,l]=Q[source,l])));
)));
if(matdet(control)!=0,error("known balanced four-root control failed"));
print("VANDERMONDE = ",V);
print("NORMALIZED_BALANCED_PHI = ",phi);
print("NORMALIZED_IS_ZERO = ",phi==0);
print("FOUR_ROOT_NEGATIVE_CONTROL = 0");
print("TERNARY_BALANCED_BOUNDARY_COMPLETED");
}
quit;
