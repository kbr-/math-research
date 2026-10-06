\\ Independent full-polynomial reconstruction of f0 and its actual Frobenius-frame variation.
\\ Four character divisions replace a repeated960-square inverse; compare every resulting cut separately.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
finitecuts(P,M,N,u,ii,baseM)={
 my(o=u^0,nodes=[o,-o,ii,-ii],der=deriv(P,z),val=vector(4,j,nodes[j]^(-M)*subst(P,z,nodes[j])),dd=vector(4,j,nodes[j]^(-M)*(subst(der,z,nodes[j])-M/nodes[j]*subst(P,z,nodes[j]))),phase=ii^baseM);
 [dd[1]*(1-u)^(1-N),dd[2]*(-1-u)^(1-N),phase*(val[3]+val[4]),phase*(u^2+1)*(dd[3]+dd[4])]~;
};
cuts(P,M,N,u,ii)={
 my(v=finitecuts(P,M,N,u,ii,M),A=vector(7,j,polcoef(P,2*M-j+1,z)+polcoef(P,j-1,z)),B=vector(7,j,polcoef(P,2*M-j+1,z)-polcoef(P,j-1,z)));
 concat(v,[A[4]-A[2],A[6]-3*A[2],A[1],A[5],A[7]-3*A[3],B[4]-2*B[2],B[6]-B[2],B[3]-3*B[1],B[5]-3*B[1]]~);
};
{
my(d=10,D=119,N=960,M=486,MP=M+14,modulus=ffinit(7,4,'a),a=ffgen(modulus,'a),o=a^0,u=a,ii=ffprimroot(a)^((7^4-1)/4),ss=u^2+u^-2,quad=z^4-ss*z^2+o,C=u^N,Q=C*(1-u*z)*(1+z^2)^2*(u+C*z^7),marked=(z-u)^N,P0=marked*Q,Rev=z^(2*M)*subst(P0,z,1/z),neg=subst(P0,z,-z),negRev=subst(Rev,z,-z),pref=[[3,0],[2,0],[0,3],[1,3]],g=(T+ss+2)*(T+ss-2)^2);
my(powers=vector(2*D+11));powers[1]=o;for(j=2,#powers,powers[j]=powers[j-1]*quad);
my(small=2/(1+sqrt(Mod(1,7)+w+O(w^3))),first=vector(2*D\7+1,j,polcoef(small^(j-1),1,w)),P1=0*o,back=0*o,columns=0);
for(ch=1,4,
 my(al=pref[ch][1],be=pref[ch][2],pa=(-1)^(al+be),re=(-1)^be,RP=(z^2+1)^al*(z^2-1)^be,Proj=(P0+pa*neg+re*Rev+pa*re*negRev)/4,k=M-al-be,m=(k+1)\2,poly=z^(2*m-k)*Proj/RP,co=vector(m+1,j,0*o));
 assert(denominator(poly)==1,"full finite-character divisibility");
 forstep(e=m,0,-1,my(v=polcoef(poly,2*m+2*e,z));co[e+1]=v;if(v!=0,poly-=v*z^(2*m-2*e)*powers[e+1]));
 assert(poly==0,"complete invariant quotient reconstruction");
 my(P=Polrev(co,T),Rem=P%g,Quot=(P-Rem)/g);
 assert(poldegree(Quot,T)<=2*D && polcoef(Quot,2*D-1,T)==0 && polcoef(Quot,2*D-2,T)==0,"actual Frobenius core support");
 my(Var=T^7*Rem/2,Expected=T^7*Rem/2);
 for(e=0,2*D,
  my(qe=polcoef(Quot,e,T),res=e%7,power=e\7,A=(D-res)\7,B=(D-3-res)\7);
  if(qe!=0,assert(power<=A+B+1,"full actual frame exponent");Var+=g*qe*first[power+1]*T^(e+7);Expected-=g*qe*binomial(e,7)*T^(e+7)/4);
 );
 assert(Var==Expected,"direct frame derivative versus Hasse operator");
 for(e=0,poldegree(P,T),my(v=polcoef(P,e,T));if(v!=0,assert(M-al-be-2*e>=0,"kernel pole bound");back+=RP*v*z^(M-al-be-2*e)*powers[e+1]));
 if(Var!=0,for(e=0,poldegree(Var,T),my(v=polcoef(Var,e,T));if(v!=0,assert(MP-al-be-2*e>=0,"variation pole bound");P1+=RP*v*z^(MP-al-be-2*e)*powers[e+1])));
 columns+=2*D+2;
);
assert(columns==N && back==P0 && cuts(P0,M,N,u,ii)==vector(13,j,0*o)~,"full source kernel identity");
assert(finitecuts(P1,MP,N,u,ii,M)==vector(4,j,0*o)~,"variation retains all finite cuts");
my(top=sum(j=0,13,polcoef(P1,2*MP-j,z)*h^j)+O(h^14),bottom=sum(j=0,13,polcoef(P1,j,z)*h^j)+O(h^14),upper=top*(o-u*h+O(h^14))^(-N),lower=bottom/C*(o-h/u+O(h^14))^(-N),R0=sum(j=0,13,polcoef(lower,j,h)*z^j+polcoef(upper,j,h)*z^(40-j)),red=P1-marked*R0);
for(j=0,13,assert(polcoef(red,j,z)==0 && polcoef(red,2*MP-j,z)==0,"all outer-pole levels cancelled"));
my(reduced=red/z^14);assert(denominator(reduced)==1 && poldegree(reduced,z)<=2*M,"return to original ambient");
my(bv=cuts(reduced,M,N,u,ii),BM=Mat(vector(13,j,cuts(marked*z^(j-1),M,N,u,ii))),left=matker(BM~));assert(matsize(left)[2]==1,"one-dimensional bounded cokernel");
my(value=(left~*bv)[1]);assert(value!=0,"actual full first effective variation nonzero");
print("FIELD=",modulus," d=",d," D=",D," N=",N," u=",u," state=",D%49);
print("FULL_REDUCED_CUT_VECTOR=",bv);print("SMALL_COKERNEL_SCALAR=",value);
my(I=(u-ii)^N,J=(u+ii)^N,OUT="research/results/bmd-eight-septenary-variation-20261006/full-control-values.sing");
write(OUT,"ring Point=(7,a),(z),dp; minpoly=",liftall(modulus),";");
write(OUT,"number PointU=",u,"; number PointC=",C,"; number PointX=",I+J,"; number PointY=",ii*(I-J),";");
write(OUT,"matrix Actual[13][1];");for(j=1,13,write(OUT,"Actual[",j,",1]=",bv[j],";"));
print("PASS actual full-source reconstruction, frame derivative, all outer cancellations and nonzero induced scalar.");
}
quit;
