\\ Independent direct Taylor check of the ordinary matching normalization.
\\ First e9-class member q19683,d156: fixed19/17 matrices only, not19648 jets.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
if(default(nbthreads)!=1,error("threads"));
assert(c,s)={if(!c,error(s));};
pc(P,L,k,u)={u^(L-1-k)*sum(t=k,L-1,polcoef(P,t,'x)*binomial(t,t-k)*(-1)^(t-k));};
finite(P,L,M,u,i,scale)={my(D=deriv(P,'x),nodes=[u^0,-u^0,i,-i],val=vector(4,j,scale*subst(P,'x,nodes[j]/u-1)),der=vector(4,j,scale/u*subst(D,'x,nodes[j]/u-1)));[der[1]-M*val[1],-der[2]-M*val[2],i^(-M)*val[3]+(-i)^(-M)*val[4]]~;};
{
my(q=19683,d=156,delta=35,gap=14,n=(q-1)/2,alpha=n+1,L=n-delta,nr=gap-3,dim=gap+5,reduced=gap+3,r=64*d-128,s=r-64,Mu=(r+4)/2,Ml=(s+4)/2);
my(modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,ii=ffprimroot(a)^((3^10-1)/4),u=random(a));
while(u==0 || u^4==1,u=random(a));
assert(ii^2==-o && L==s+gap,"parameters");
print("FIELD=",modulus," u=",u," q=",q," d=",d," Taylor_length=",L," matrices=",dim,"/",reduced);
my(Big=matrix(dim,dim,j,k,0*o),Small=matrix(reduced,reduced,j,k,0*o),Z=o+x+O(x^L));
my(F=Z^(-26)*(Z+1)^n*(1-u^4*Z^2)^n/((1+u^2*Z^2)*(1-u^2*Z^2)^4));
for(j=0,dim-1,
 my(P=Pol(F,x));
 my(U=[o*((j+alpha-Mu)+(Mu-j)*u),o*(-1)^j*(-(j+alpha-Mu)+(Mu-j)*u),ii^(j-Mu)*(ii-u)^alpha+(-ii)^(j-Mu)*(-ii-u)^alpha]~);
 my(tau=vector(nr,k,polcoef(P,L-k,x)),upperHigh=[if(j==gap+4,o,0*o),if(j==gap+3,o,if(j==gap+4,-alpha*u,0*o))]~);
 my(lowerFinite=finite(P,L,Ml,u,ii,u^(L-1)),lowerHigh=[pc(P,L,2*Ml,u),pc(P,L,2*Ml-1,u)]~,extra=vector(gap-5,k,pc(P,L,L-k,u))~);
 Big[,j+1]=concat(concat(U,upperHigh),concat(concat(lowerFinite,lowerHigh),extra));
 if(j<reduced,
  my(R=Pol(P%x^(L-nr),x));
  Small[,j+1]=concat(concat(U,finite(R,L-nr,Ml,u,ii,u^(L-1-nr))),tau~);
 );
 if(j%4==0,print("constructed column ",j+1,"/",dim));
 if(j<dim-1,F*=u*Z);
);
my(DB=matdet(Big),DS=matdet(Small),power=(gap-3)*(gap+2)/2);
assert(DB!=0 && DS!=0,"control point must witness nonzero constant coefficient");
my(ratio=DB/(u^power*DS));
assert(ratio==o || ratio==-o,"ordinary normalization mismatch");
print("full19 constant-tag determinant=",DB);
print("residual17 determinant=",DS," power=",power," ratio=",ratio);
print("PASS: direct full Taylor matching agrees with normalized residual; no large original jet matrix.");
}
quit;
