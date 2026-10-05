\\ Check the actual r=2 KZ master encoding at p=3 and p=5, n=5.
\\ Five distinct nonzero branches over F_(p^2): ten pair columns; selected
\\ (pu+p-1,pv+p-1) coefficients have rank one, so the erasure is not vacuous.
\\ Exhaust all polynomial coefficients for reconstruction and star identities.
\\ The general theorem is proved separately; no dimension survey is run.
default(parisizemax, 100000000);
default(nbthreads, 1);
setrand(20261005);
if(default(nbthreads)!=1,error("thread setting failed"));
{
forprime(p=3,5,
my(X='x,Y='y,F=ffgen(ffinit(p,2,'v),'b),z=[1,F,F+1,2*F,2*F+1],m=(p-1)/2);
my(n=#z, pairs=List(),P=prod(i=1,n,X-z[i]),G,B, H, K,star_count=0,diag_count=0,rec_count=0);
if(#Set(z)!=n || vecprod(z)==0,error("invalid branches"));
G=vector(n,i,P/(X-z[i]));
B=vector(n,i,P^m/(X-z[i]));
for(i=1,n,for(j=i+1,n,listput(pairs,[i,j])));
pairs=Vec(pairs);
H=vector(#pairs,k,my(i=pairs[k][1],j=pairs[k][2]);(X-Y)*(B[i]*subst(B[j],X,Y)+B[j]*subst(B[i],X,Y)));
K=matrix(4,#pairs,u,k,my(a=(u-1)\2,b=(u-1)%2);polcoef(polcoef(H[k],p*a+p-1,X),p*b+p-1,Y));
if(matrank(K)!=1,error("nonvacuous KZ control failed"));
for(k=1,#pairs,
  my(i=pairs[k][1],j=pairs[k][2],expected=P/((X-z[i])*(X-z[j])));
  if(subst(H[k]/(X-Y),Y,X)/(2*P^(p-2))!=expected,error("diagonal mismatch"));
  diag_count++;
  my(rebuilt=0);
  for(r=0,p-1,for(s=0,p-1,
    my(dec=0);
    for(a=0,(n*m)\p,for(b=0,(n*m)\p,dec+=polcoef(polcoef(H[k],p*a+r,X),p*b+s,Y)*X^a*Y^b));
    rebuilt+=X^r*Y^s*subst(subst(dec,X,X^p),Y,Y^p);
  ));
  if(rebuilt!=H[k],error("residue reconstruction mismatch"));
  rec_count++;
);
for(i=1,n,
  my(st=vector(#pairs,k,if(pairs[k][1]==i || pairs[k][2]==i,1,0))~);
  my(h=H*st);
  if(K*st!=vector(4,j,0)~,error("star survives selected KZ coefficients"));
  my(rhs=-2*(deriv((X-Y)*P^m*subst(B[i],X,Y),X)+deriv((X-Y)*B[i]*subst(P^m,X,Y),Y)));
  if(h!=rhs,error("star derivative identity failed"));
  if(subst(h/(X-Y),Y,X)/(2*P^(p-2))!=deriv(G[i],X),error("star diagonal derivative failed"));
  if(sum(k=1,#pairs,st[k])!=n-1 || Mod(n-1,p)==0,error("original constant jet control failed"));
  star_count++;
);
my(u=vector(n,i,z[i]/subst(G[i],X,z[i])));
my(c=vector(#pairs,k,u[pairs[k][1]]+u[pairs[k][2]])~);
if(sum(i=1,n,u[i]*G[i])!=X,error("Lagrange linear polynomial failed"));
if(K*c!=vector(4,j,0)~,error("Lagrange erasure failed"));
if(subst((H*c)/(X-Y),Y,X)/(2*P^(p-2))!=1,error("erased diagonal must be one"));
if(p==3,
  my(a=vector(n,i,-1/z[i]),A=vecprod(a),R=prod(i=1,n,1+a[i]*X),nz=0);
  for(k=1,#pairs,
    my(i=pairs[k][1],j=pairs[k][2],hat=A/(a[i]*a[j])*H[k]);
    if(subst(hat/(X-Y),Y,X)/(2*P)!=R/((1+a[i]*X)*(1+a[j]*X)),error("original normalization failed"));
  );
  for(i=1,n,
    my(c0=sum(j=1,n,if(j==i,0,a[i]*a[j]/A)));
    if(c0!=a[i]/A*(sum(j=1,n,a[j])-a[i]),error("normalized constant jet mismatch"));
    if(c0!=0,nz++);
  );
  if(nz==0,error("all normalized original constant jets erased"));
  print("ternary normalized complement identities=10; nonzero erased constant jets=",nz);
);
my(mutated=H);
mutated[1]+=X^(2*p-1)*Y^(p-1)-X^(p-1)*Y^(2*p-1);
my(Kbad=matrix(4,#pairs,u,k,my(a=(u-1)\2,b=(u-1)%2);polcoef(polcoef(mutated[k],p*a+p-1,X),p*b+p-1,Y)));
my(star1=vector(#pairs,k,if(pairs[k][1]==1 || pairs[k][2]==1,1,0))~);
if(Kbad*star1==vector(4,j,0)~,error("mutated pair escaped the star-erasure check"));
print("p=",p,"; field polynomial=",ffinit(p,2,'v),"; branches: ",z);
print("n=5; pair columns=10; KZ coefficient rows=4; selected rank=",matrank(K));
print("full polynomial diagonal identities=",diag_count,"; all-p^2-residue reconstructions=",rec_count,"; star derivative/erasure identities=",star_count);
print("erased Lagrange diagonal=1; unnormalized star coefficient sums=4 mod p");
print("mutated pair fails the same selected star-erasure invariant");
print("PASS");
);
}
