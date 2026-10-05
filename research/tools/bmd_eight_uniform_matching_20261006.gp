\\ Bounded coefficient matrix for the q=3^(32t+6) conic matching family.
\\ Strip seven exact global low-tail powers Z=u^L, then take Z=0.
\\ After four unit eliminations and known row powers, the residual matrix is22 square.
\\ This run computes that candidate leading Z coefficient, not yet the complete proof.
default(parisizemax,3000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
P=48;if(getenv("PREC")!=0 && getenv("PREC")!="",P=eval(getenv("PREC")));
OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
if(P<32 || P>256,error("precision outside validated digit bound"));
emit(s)={print(s);write(OUT,s);};
assert(c,s)={if(!c,error(s));};
b3(n,k)={if(k<0,0,lift(Mod(binomial(n,k),3)));};
paritysum(e)={if(e%2,0,if(e%4,1,2));}; \\ i^e+(-i)^e mod3
powat(z,e,N)={Polrev(vector(N,k,Mod(b3(e,k-1)*(-1)^(k-1)*z^(e-k+1),3)),u);};
{
my(n=364,L=339,alpha=365,Mu=194,Ml=170,kk=26,Rmax=P+8,Vmax=P-18,Rall=Rmax+Vmax);
my(K=matrix(Rall+1,Vmax+19),Low=matrix(Vmax+19,11));
emit(Str("precision=",P," n_mod729=",n," L_mod729=",L," rows22 cols22; initial global-tail coefficient only"));
for(r=0,Rall,K[r+1,19]=(b3(n,kk+r)*lift(Mod(2,3)^(kk+r)))%3);
for(v=1,Vmax,for(r=0,Rall-v,K[r+1,v+19]=(K[r+1,v+18]+K[r+2,v+18])%3));
for(m=1,18,for(r=0,Rmax,
 my(t=n-kk-r,vv=0);
 for(a=1,m,vv+=(-1)^t*b3(n,m-a)*b3(t+a-1,a-1));
 for(b=0,kk+r-m,vv+=b3(n,b)*b3(n-b-m,kk+r-b-m));
 K[r+1,19-m]=vv%3;
));
for(k=0,10,
 my(vv=b3(n,k+18));
 forstep(r=-(kk-18),-1,1,
  my(t=n-kk-r,poly=0);
  for(b=0,kk+r-18,poly+=b3(n,b)*b3(n-b-18,kk+r-b-18));
  vv-=poly*b3(t,k)*(-1)^(t-k);
 );
 for(a=1,18,vv+=b3(n,18-a)*(-1)^k*b3(a+k-1,k)*b3(a+L-1,a+k));
 Low[1,k+1]=vv%3;
);
for(v=-18,Vmax-1,for(k=0,10,Low[v+20,k+1]=(if(k,Low[v+19,k],0)-K[1,v+19]*b3(L,k)*(-1)^(L-k))%3));
\\ Independent base-q Taylor checks for every exponent needed by this precision.
for(v=-18,Vmax,
 my(Z=Mod(1,3)+t+O(t^L),H=Z^v*(Z+1)^n,F=subst(Pol(H,t),t,z-1));
 for(r=0,Rmax,assert(lift(polcoef(H,L-1-r,t))%3==K[r+1,v+19],"high coefficient recurrence"));
 for(k=0,10,assert(lift(polcoef(F,k,z))%3==Low[v+19,k+1],"low Taylor coefficient recurrence"));
);
emit(Str("PASS independent Taylor checks: ",Vmax+19," exponents, high indices0..",Rmax,", low indices0..10"));
my(A=vector(5,k,b3(0,0)*lift(polcoef(Mod(1,3)*(1+t)^2*(1-t)^4,k-1,t))),B=vector(5,k,lift(polcoef(Mod(1,3)*(1+t)*(1-t)^7,k-1,t))));
my(CH=matrix(18,11),CL=matrix(18,11),rr=0);
forstep(j=1,9,2,rr++;CH[rr,j+1]=1;CL[rr,j+1]=1);
forstep(j=1,7,2,rr++;CH[rr,j+1]=1;CL[rr,j+1]=-1);
rr++;CH[rr,1]=1;CL[rr,1]=1;
for(j=1,4,rr++;CH[rr,2+2*j+1]=1;CH[rr,3]=-A[j+1];CL[rr,2+2*j+1]=1;CL[rr,3]=-A[j+1]);
for(j=1,4,rr++;CH[rr,2*j+1]=1;CH[rr,1]=-B[j+1];CL[rr,2*j+1]=-1;CL[rr,1]=B[j+1]);
CH=Mod(CH,3);CL=Mod(CL,3);
my(Kleft=matker(CH~)~,Pure=lift(Kleft*CL));
assert(rr==18 && matrank(CH)==11 && matsize(Kleft)==[7,18] && Kleft*CH==matrix(7,11),"seven exact low combinations");
emit(Str("pure_low_rows=",Pure));
my(D=vector(P,k,lift(polcoef((Mod(1,3)+t+O(t^P))^-1*(Mod(1,3)-t+O(t^P))^-4,k-1,t))),uu=Mod(u,u^P),o=Mod(1,3),F=matrix(22,22,j,k,0*uu*o));
my(Evals=vector(Rmax+1,r,vector(3)));
for(r=9,Rmax,
 my(e=L-1-r);
 Evals[r+1][1]=Mod(powat(1,e-1,P)*((e-Ml)+Ml*u),u^P);
 Evals[r+1][2]=Mod(powat(-1,e-1,P)*(-(e-Ml)+Ml*u),u^P);
 Evals[r+1][3]=Mod(Polrev(vector(P,k,Mod(b3(e,k-1)*(-1)^(k-1)*paritysum(e-Ml-k+1),3)),u),u^P);
);
for(j=0,21,
 my(TA=matrix(Rmax+1,P),LO=matrix(11,P));
 for(a=0,(P-1-j)\4,for(b=0,(P-1-j-4*a)\2,
  my(k=j+4*a+2*b,v=j-18+2*a+2*b,coef=((-1)^a*b3(n,a)*D[b+1])%3);
  if(coef==0,next);
  for(r=0,min(Rmax,P+8-k),TA[r+1,k+1]=(TA[r+1,k+1]+coef*K[r+1,v+19])%3);
  for(h=0,10,LO[h+1,k+1]=(LO[h+1,k+1]+coef*Low[v+19,h+1])%3);
 ));
 my(TP=vector(Rmax+1,r,Mod(Polrev(vector(P,k,Mod(TA[r,k],3)),u),u^P)),LP=vector(11,r,Mod(Polrev(vector(P,k,Mod(LO[r,k],3)),u),u^P)));
 F[1,j+1]=o*(j+(Mu-j)*uu);
 F[2,j+1]=o*(-1)^j*(-j+(Mu-j)*uu);
 F[3,j+1]=Mod(Polrev(vector(P,k,Mod(b3(alpha,k-1)*(-1)^(k-1)*paritysum(alpha+j-Mu-k+1),3)),u),u^P);
 for(k=1,3,F[3+k,j+1]=sum(r=9,Rmax,uu^(r-9)*TP[r+1]*Evals[r+1][k]));
 for(r=0,8,F[7+r,j+1]=TP[r+1]);
 for(k=1,7,F[15+k,j+1]=sum(r=0,10,o*Pure[k,r+1]*uu^(10-r)*LP[r+1]));
);
emit(Str("matrix=",F));
emit(Str("entry_valuations=",matrix(22,22,i,j,min(P,valuation(lift(F[i,j]),u)))));
my(Det=matdet(matrix(22,22,i,j,lift(F[i,j])+O(u^P))));
emit(Str("determinant_series=",Det));
if(Det==0,emit("UNRESOLVED at this entry precision"),emit(Str("leading_order=",valuation(Det,u)," leading_coefficient=",polcoef(Det,valuation(Det,u),u))));
}
quit;
