\\ Independent exact comparison: 26-condition matching and full704-jet conic source.
\\ Single control q729,d8. The all-q matching lemma is proved separately.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
if(default(nbthreads)!=1,error("threads"));
assert(c,msg)={if(!c,error(msg));};
finitecuts(P,M,i)={my(D=deriv(P,z));[subst(D,z,1)-M*subst(P,z,1),-subst(D,z,-1)-M*subst(P,z,-1),i^(-M)*subst(P,z,i)+(-i)^(-M)*subst(P,z,-i)];};
hl(P,M,r,sig)={polcoef(P,2*M-r,z)+sig*polcoef(P,r,z);};
uppercuts(P,M,i)={concat(finitecuts(P,M,i),[hl(P,M,0,1),hl(P,M,1,1)])~;};
lowercuts(P,M,i,A,B)={my(C=List(finitecuts(P,M,i)));forstep(r=1,9,2,listput(C,hl(P,M,r,1)));forstep(r=1,7,2,listput(C,hl(P,M,r,-1)));listput(C,hl(P,M,0,1));for(j=1,4,listput(C,hl(P,M,2+2*j,1)-A[j+1]*hl(P,M,2,1)));for(j=1,4,listput(C,hl(P,M,2*j,-1)-B[j+1]*hl(P,M,0,-1)));assert(#C==21,"lower cuts");Vec(C)~;};
{
my(q=729,d=8,alpha=365,N=704,L=339,Mu=194,Ml=170,aexp=81);
my(modulus=ffinit(3,8,'a),a=ffgen(modulus,'a),o=a^0,ii=ffprimroot(a)^((3^8-1)/4),u=random(a));
while(u==0 || u^4==1,u=random(a));
assert(ii^2==-o,"fourth root");
my(S=u^2+u^-2,A=vector(5,j,polcoef((1+t)^2*(1-t)^4*(1-S*t+t^2)^aexp,j-1,t)),B=vector(5,j,polcoef((1+t)*(1-t)^7*(1-S*t+t^2)^aexp,j-1,t)));
print("FIELD=",modulus," u=",u," i=",ii," dimensions upperQ24 lowerFree2 constraints5+21");
my(Matrix=matrix(26,26,j,k,0*o),Z=u+t+O(t^L));
for(j=0,23,
 my(Pup=(z-u)^alpha*z^j,H=Z^(q-18+j)/((Z+u)^alpha*(Z^2-u^-2)^alpha*(Z^2+1)*(Z^2-1)^4));
 my(Plo=subst(Pol(H,t),t,z-u),col=concat(uppercuts(Pup,Mu,ii),lowercuts(Plo,Ml,ii,A,B)));
 assert(poldegree(Plo,z)<=L-1,"Taylor degree");assert(valuation(subst(Plo,z,Z)-H,t)>=L,"Taylor polynomial retains its variable and all jets");
 Matrix[,j+1]=col;
);
for(j=0,1,Matrix[,25+j]=concat(vector(5,k,0*o)~,lowercuts((z-u)^L*z^j,Ml,ii,A,B)));
my(md=matdet(Matrix));print("MATCHING determinant=",md);if(md==0,print("MATCHING rank=",matrank(Matrix)));
my(Zs=u+t+O(t^N),tau=(Zs^2-u^2)*(Zs^2-u^-2)/Zs^2,v=u*(Zs+1/Zs)/(u^2+1),w=u*(Zs-1/Zs)/(u^2-1));
assert(polcoef(tau,0,t)==0 && polcoef(tau,1,t)!=0 && polcoef(v,0,t)==o && polcoef(w,0,t)==o,"unramified normalized mark");
my(U=List(),V=List());
for(j=0,95,for(k=1,4,listput(U,[v,w^3,v^2,v*w^3][k]*tau^j)));
for(j=0,79,listput(V,v*tau^j);listput(V,w^3*tau^j));
for(j=0,78,listput(V,v^2*tau^j);listput(V,v*w^3*tau^j));
listput(V,v^2*w^4*tau^aexp);listput(V,v*w^7*tau^aexp);
assert(#U==384 && #V==320,"source counts");
my(rows=concat(Vec(U),apply(f->tau^alpha*v*w^4*f,Vec(V))),Jets=matrix(N,N,j,k,polcoef(rows[k],j-1,t)),jd=matdet(Jets));
print("DIRECT full704 determinant=",jd);if(jd==0,print("DIRECT rank=",matrank(Jets)));assert((md==0)==(jd==0),"matching/direct discrepancy");
print("PASS: 26-condition matching and full704-jet source zero/nonzero decisions agree at the same admissible mark.");
}
quit;
