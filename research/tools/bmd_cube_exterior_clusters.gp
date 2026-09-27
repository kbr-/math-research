\\ Test the all-dimensional collision-cluster mechanism, not a new dimension.
\\ n=3 is the smallest control containing both two double clusters and a
\\ quadruple cluster. All 15 set partitions of its four labeled roots are checked.
\\ Stages: build the symbolic exterior connection; retain columns 0..6;
\\ compare all seven columns with the independent f wedge h generating series;
\\ specialize every cluster partition and compare exact ranks with the formula.
\\ The existing monic order-nine control makes these seven pair columns complete.
X='X; a='a; b='b; c='c; T='T;
dv(f)=-a^2*deriv(f,a)-b^2*deriv(f,b)-c^2*deriv(f,c);
special(f,roots)=subst(subst(subst(f,a,roots[2]),b,roots[3]),c,roots[4]);
{
my(nn=3,ss=6,pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]);
my(pp=X*(X-a)*(X-b)*(X-c),D=matrix(4,4),W=matrix(ss,ss));
for(u=0,nn,my(rem=lift(Mod(-(u+1/2)*X^(u+1),pp)));
  for(v=0,nn,D[v+1,u+1]=polcoef(rem,v,X)));
for(k=1,ss,my(u=pairs[k][1],v=pairs[k][2]);
  for(t=1,ss,my(i=pairs[t][1],j=pairs[t][2]);
    W[t,k]=D[i+1,u+1]*(j==v)-D[j+1,u+1]*(i==v)
      +(i==u)*D[j+1,v+1]-(j==u)*D[i+1,v+1]));
my(z=vector(ss,i,i==1)~,K=matrix(ss,7));
for(j=0,6,
  for(i=1,ss,K[i,j+1]=z[i]);
  z=(vector(ss,i,dv(z[i]))~+W*z)/(j+1));
my(ff=vector(7,j,lift(Mod(binomial(-1/2,j-1)*X^(j-1),pp))));
my(hh=vector(7,j,lift(Mod(binomial(-3/2,j-1)*X^j,pp))));
for(j=0,6,for(t=1,ss,
  my(u=pairs[t][1],v=pairs[t][2]);
  my(cc=sum(q=0,j,polcoef(ff[q+1],u,X)*polcoef(hh[j-q+1],v,X)
    -polcoef(ff[q+1],v,X)*polcoef(hh[j-q+1],u,X)));
  if(cc!=K[t,j+1],error("generating series mismatch"))));
print("PARAMETERS n=3 pair_rank=6 columns=0..6 characteristic=0");
print("SYMBOLIC_KRYLOV = ",K);
my(count=0,defects=0);
for(b1=0,1,for(b2=0,1+b1,for(b3=0,1+max(b1,b2),
  my(roots=[0,b1,b2,b3],groups=1+vecmax(roots),mult=vector(groups));
  for(j=1,4,mult[roots[j]+1]++);
  my(def=0);
  for(j=1,groups,if(mult[j]>=2,def+=(mult[j]-2)*(mult[j]-3)/2);
    for(k=j+1,groups,def+=(mult[j]-1)*(mult[k]-1)));
  my(M=matrix(ss,7,i,j,special(K[i,j],roots)),rk=matrank(M));
  if(rk!=ss-def,error("cluster rank mismatch ",roots));
  count++;if(def>0,defects++);
  print("PARTITION ",roots," MULTIPLICITIES ",mult," RANK ",rk," DEFECT ",def);
)));
if(count!=15||defects!=4,error("incomplete partition inventory"));
print("GENERATING_COEFFICIENT_IDENTITIES = 42");
print("SET_PARTITIONS_CHECKED = ",count);
print("FREE_HULL_IMPLIES_FULL_CYCLIC_FIBER_COUNTEREXAMPLES = ",defects);
print("EXTERIOR_CLUSTER_CONTROL_COMPLETED");
}
quit;
