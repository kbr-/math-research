\\ Uniform constant-global-tail matrices for the two ordinary/ordinary n8 profiles.
\\ e=4 mod32 (e>=36) and e=9 mod32 (e>=9); no original large jet matrices.
default(parisizemax,3000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
P=192;
OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
emit(s)={print(s);write(OUT,s);};
assert(c,s)={if(!c,error(s));};
b3(n,k)={if(k<0,0,lift(Mod(binomial(n,k),3)));};
paritysum(e)={if(e%2,0,if(e%4,1,2));};
powat(z,e,N)={Polrev(vector(N,k,Mod(b3(e,k-1)*(-1)^(k-1)*z^(e-k+1),3)),u);};
{
my(D=vector(P,k,lift(polcoef((Mod(1,3)+t+O(t^P))^-1*(Mod(1,3)-t+O(t^P))^-4,k-1,t))),uu=Mod(u,u^P),o=Mod(1,3));
for(cas=1,2,
 my(eclass=if(cas==1,4,9),delta=if(cas==1,17,35),gap=(63-delta)/2,n=if(cas==1,364,1093),alpha=n+1,kk=delta+1,L=n-delta,Mu=34,Ml=38,m0=26,nr=gap-3,dim=gap+3,Rmax=P+nr-1,Vmax=P-m0,Rall=Rmax+Vmax,K=matrix(Rall+1,Vmax+m0+1));
 emit(Str("CASE exponent_class=",eclass," precision=",P," gap=",gap," n_base=",n," L_base=",L," reduced_dimension=",dim));
 for(r=0,Rall,K[r+1,m0+1]=(b3(n,kk+r)*lift(Mod(2,3)^(kk+r)))%3);
 for(v=1,Vmax,for(r=0,Rall-v,K[r+1,v+m0+1]=(K[r+1,v+m0]+K[r+2,v+m0])%3));
 for(m=1,m0,for(r=0,Rmax,
  my(t=n-kk-r,vv=0);
  for(a=1,m,vv+=(-1)^t*b3(n,m-a)*b3(t+a-1,a-1));
  for(b=0,kk+r-m,vv+=b3(n,b)*b3(n-b-m,kk+r-b-m));
  K[r+1,m0+1-m]=vv%3;
 ));
 for(v=-m0,Vmax,
  my(Z=Mod(1,3)+t+O(t^L),H=Z^v*(Z+1)^n);
  for(r=0,Rmax,assert(lift(polcoef(H,L-1-r,t))%3==K[r+1,v+m0+1],"independent Taylor coefficient"));
 );
 emit(Str("PASS direct high Taylor identities for ",Vmax+m0+1," exponents and ",Rmax+1," indices"));
 my(F=matrix(dim,dim,j,k,0*uu*o),Evals=vector(Rmax+1,r,vector(3)));
 for(r=nr,Rmax,
  my(ee=L-1-r);
  Evals[r+1][1]=Mod(powat(1,ee-1,P)*((ee-Ml)+Ml*u),u^P);
  Evals[r+1][2]=Mod(powat(-1,ee-1,P)*(-(ee-Ml)+Ml*u),u^P);
  Evals[r+1][3]=Mod(Polrev(vector(P,k,Mod(b3(ee,k-1)*(-1)^(k-1)*paritysum(ee-Ml-k+1),3)),u),u^P);
 );
 for(j=0,dim-1,
  my(TA=matrix(Rmax+1,P));
  for(a=0,(P-1-j)\4,for(b=0,(P-1-j-4*a)\2,
   my(k=j+4*a+2*b,v=j-m0+2*a+2*b,coef=((-1)^a*b3(n,a)*D[b+1])%3);
   if(coef==0,next);
   for(r=0,min(Rmax,P+nr-1-k),TA[r+1,k+1]=(TA[r+1,k+1]+coef*K[r+1,v+m0+1])%3);
  ));
  my(TP=vector(Rmax+1,r,Mod(Polrev(vector(P,k,Mod(TA[r,k],3)),u),u^P)));
  F[1,j+1]=o*((j+alpha-Mu)+(Mu-j)*uu);
  F[2,j+1]=o*(-1)^j*(-(j+alpha-Mu)+(Mu-j)*uu);
  F[3,j+1]=Mod(Polrev(vector(P,k,Mod(b3(alpha,k-1)*(-1)^(k-1)*paritysum(alpha+j-Mu-k+1),3)),u),u^P);
  for(k=1,3,F[3+k,j+1]=sum(r=nr,Rmax,uu^(r-nr)*TP[r+1]*Evals[r+1][k]));
  for(r=0,nr-1,F[7+r,j+1]=TP[r+1]);
 );
 emit(Str("matrix=",F));
 emit(Str("entry_valuations=",matrix(dim,dim,i,j,min(P,valuation(lift(F[i,j]),u)))));
 my(DD=matdet(matrix(dim,dim,i,j,lift(F[i,j])+O(u^P))));
 emit(Str("determinant_series=",DD));
 if(DD==0,emit("UNRESOLVED"),emit(Str("leading_order=",valuation(DD,u)," leading_coefficient=",polcoef(DD,valuation(DD,u),u))));
);
}
quit;
