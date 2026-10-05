\\ Independent same-q audit of the global-tail normalization.
\\ Tag low coefficients by X/u^L in the full26 matching map; compare its X^7
\\ coefficient with the direct22 residual matrix, before any u truncation.
default(parisizemax,3000000000);
default(nbthreads,1);
setrand(20261006);
if(default(nbthreads)!=1,error("threads"));
assert(c,msg)={if(!c,error(msg));};
fc(P,M,i)={my(D=deriv(P,z));[subst(D,z,1)-M*subst(P,z,1),-subst(D,z,-1)-M*subst(P,z,-1),i^(-M)*subst(P,z,i)+(-i)^(-M)*subst(P,z,-i)]~;};
hc(H,L,A,B)={my(C=List());forstep(r=1,9,2,listput(C,H[r+1]+L[r+1]));forstep(r=1,7,2,listput(C,H[r+1]-L[r+1]));listput(C,H[1]+L[1]);for(j=1,4,listput(C,H[3+2*j]+L[3+2*j]-A[j+1]*(H[3]+L[3])));for(j=1,4,listput(C,H[1+2*j]-L[1+2*j]-B[j+1]*(H[1]-L[1])));Vec(C)~;};
lc(P,M,i,A,B,tag)={concat(fc(P,M,i),hc(vector(11,k,polcoef(P,2*M-k+1,z)),vector(11,k,tag*polcoef(P,k-1,z)),A,B));};
{
my(q=729,n=364,alpha=365,L=339,Mu=194,Ml=170,modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,ii=ffprimroot(a)^((3^10-1)/4),u=random(a));
while(u==0 || u^4==1,u=random(a));
assert(ii^2==-o,"i");
my(A=vector(5,k,polcoef(o*(1+t)^2*(1-t)^4,k-1,t)),B=vector(5,k,polcoef(o*(1+t)*(1-t)^7,k-1,t)),CH=matrix(18,11),CL=matrix(18,11));
for(k=1,11,my(e=vector(11,j,if(j==k,o,0*o)),zero=vector(11,j,0*o));CH[,k]=hc(e,zero,A,B);CL[,k]=hc(zero,e,A,B));
my(Kleft=matker(CH~)~,Pure=Kleft*CL);
assert(matsize(Kleft)==[7,18] && matrank(CH)==11,"exact low combinations");
my(Big=matrix(26,26,j,k,0*o),Small=matrix(22,22,j,k,0*o),Z=o+t+O(t^L),tag=X/u^L);
print("FIELD=",modulus," u=",u," q729; compare full26 tagged map and direct22 constant-tail matrix.");
for(j=0,23,
 my(Pup=(z-u)^alpha*z^j,upper=fc(Pup,Mu,ii));
 upper[1]/=(1-u)^(alpha-1);upper[2]/=(-1-u)^(alpha-1);
 my(up=concat(upper,[polcoef(Pup,2*Mu,z)+tag*polcoef(Pup,0,z),polcoef(Pup,2*Mu-1,z)+tag*polcoef(Pup,1,z)]~));
 my(F=u^j*Z^(j-18)*(Z+1)^n*(1-u^4*Z^2)^n/((1+u^2*Z^2)*(1-u^2*Z^2)^4));
 my(Plo=u^(L-1)*subst(Pol(F,t),t,z/u-1));
 assert(valuation(subst(Plo,z,u*Z)/u^(L-1)-F,t)>=L,"full normalized Taylor identity");
 Big[,j+1]=concat(up,lc(Plo,Ml,ii,A,B,tag));
 if(j<=21,
  my(T=vector(9,r,polcoef(F,L-r,t)),Remainder=Plo-sum(r=0,8,u^r*T[r+1]*(z-u)^(L-1-r)));
  Small[,j+1]=concat(concat(upper,fc(Remainder,Ml,ii)/u^9),concat(T~,u^11/u^L*Pure*vector(11,k,polcoef(Plo,k-1,z))~));
 );
);
for(j=0,1,Big[,25+j]=concat(vector(5,k,0*o)~,lc((z-u)^L*z^j,Ml,ii,A,B,tag)));
my(DB=matdet(Big),DS=matdet(Small),order=valuation(DB,X),co=polcoef(DB,7,X));
assert(DS!=0,"control point gives no residual coefficient");
assert(order==7 && co!=0,"global-tail order mismatch");
my(ratio=co*u^14/DS);
assert(ratio==o || ratio==-o,"row-power normalization mismatch");
print("tagged26 lowest X order=",order," coefficient=",co);
print("direct22 determinant=",DS," normalized_ratio=",ratio);
print("PASS: seven exact global powers and the u^-14 normalization agree without u truncation.");
}
quit;
