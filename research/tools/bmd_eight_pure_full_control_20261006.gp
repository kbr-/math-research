\\ Independent full-polynomial and original-domain control, q=7^4,D=(q-9)/8=299.
\\ This tests the general source/variation formula, not an original integer cube degree.
\\ No2400-square inverse: four polynomial divisions and a13-condition cokernel only.
default(parisizemax,3000000000);
default(nbthreads,1);
v;z;T;h;w;u;
read("research/results/bmd-eight-exceptional-deformation-20261006/high-cuts.gp");
assert(c,s)={if(!c,error(s));};
finitecuts(P,M,N,uu,ii,baseM)={
 my(o=uu^0,nodes=[o,-o,ii,-ii],J=vector(4,j,my(zz=nodes[j]+v+O(v^4));zz^(-M)*subst(P,z,zz)),phase=ii^baseM,U=uu^2+1);
 [polcoef(J[1],1,v)*(1-uu)^(1-N),polcoef(J[2],1,v)*(-1-uu)^(1-N),phase*(polcoef(J[3],0,v)+polcoef(J[4],0,v)),phase*U*(polcoef(J[3],1,v)+polcoef(J[4],1,v)),phase*U*ii*(polcoef(J[3],1,v)-polcoef(J[4],1,v)),phase*U^3*(polcoef(J[3],3,v)+polcoef(J[4],3,v)-ii*(polcoef(J[3],2,v)-polcoef(J[4],2,v)))]~;
};
cuts(P,M,N,uu,ii,W)={my(tail=concat(vector(9,j,polcoef(P,2*M-j+1,z)),vector(9,j,polcoef(P,j-1,z)))~);concat(finitecuts(P,M,N,uu,ii,M),W*tail);};
{
my(q=7^4,D=(q-9)/8,N=q-1,M=4*D+10,MP=M+14,modulus=ffinit(7,6,'a),a=ffgen(modulus,'a),o=a^0,uu=a,zz=uu^q,ii=ffprimroot(a)^((7^6-1)/4),ss=uu^2+uu^-2,lam=-ss-2,quad=z^4-ss*z^2+o,C=uu^N,marked=(z-uu)^N,P0=zz*z^2*(z^q-zz)*(1+zz*z^7),Rev=z^(2*M)*subst(P0,z,1/z),neg=subst(P0,z,-z),negRev=subst(Rev,z,-z),pref=[[5,0],[2,0],[0,3],[3,3]],g=(T+ss+2)*(T+ss-2)^2,W=matrix(7,18,i,j,subst(HIGH_CUTS[i,j],u,uu)));
assert(D==299 && N==2400,"small pure-power source control");
my(powers=vector(2*D+14));powers[1]=o;for(j=2,#powers,powers[j]=powers[j-1]*quad);
my(small=2/(1+sqrt(Mod(1,7)+w+O(w^3))),first=vector(2*D\7+2,j,polcoef(small^(j-1),1,w)),P1=0*o,back=0*o,K=(2*D-3)/7,domainchecked=0);
for(ch=1,4,
 my(al=pref[ch][1],be=pref[ch][2],pa=(-1)^(al+be),re=(-1)^be,RP=(z^2+1)^al*(z^2-1)^be,Proj=(P0+pa*neg+re*Rev+pa*re*negRev)/4,k=M-al-be,m=(k+1)\2,poly=z^(2*m-k)*Proj/RP,co=vector(m+1,j,0*o));
 assert(denominator(poly)==1,"full finite-character divisibility");
 forstep(e=m,0,-1,my(cc=polcoef(poly,2*m+2*e,z));co[e+1]=cc;if(cc!=0,poly-=cc*z^(2*m-2*e)*powers[e+1]));
 assert(poly==0,"complete invariant quotient reconstruction");
 my(P=Polrev(co,T),Rem=P%g,Quot=(P-Rem)/g,dc=0*o);
 if(ch==1 || ch==4,
  assert(poldegree(Quot,T)<=2*D-1 && polcoef(Quot,2*D-4,T)==0,"actual ordinary core support"),
  my(s0=sum(j=0,3,lam^j*polcoef(Quot,7*K+j,T)),s1=sum(j=0,3,j*lam^j*polcoef(Quot,7*K+j,T)));
  assert(s0==0 && s1==0,"both limiting domain equations");
  s0=sum(j=0,6,lam^j*polcoef(Quot,7*(K-1)+j,T));s1=sum(j=0,6,j*lam^j*polcoef(Quot,7*(K-1)+j,T));
  dc=((s0-s1)+s1*T/lam)*T^(7*K)/4;
  \\ Direct original coordinate constraints on the lifted Frobenius frame.
  my(yy=sqrt(o+w*lam^7+O(w^4)),rowA=0*w+O(w^2),rowB=0*w+O(w^2),beta=2*o);
  for(e=7*(K-1),2*D,
   my(res=e%7,pow=e\7,qq=polcoef(Quot,e,T)+w*polcoef(dc,e,T));
   if(qq!=0,
    my(EE=2^(pow-1)*w^(K-pow)*((yy-1)^pow+(-yy-1)^pow),OO=2^(pow-1)*w^(K-pow)*((yy-1)^pow-(-yy-1)^pow)/yy);
    rowA+=qq*(res-beta*lam)*lam^(res-1)*EE;rowB+=qq*lam^res*OO;
   );
  );
  assert(valuation(rowA,w)>=2 && valuation(rowB,w)>=2,"direct original-domain lift through first effective order");domainchecked++;
 );
 my(Var=T^7*Rem/2+g*dc,Expected=Var);
 for(e=0,2*D,my(qe=polcoef(Quot,e,T),res=e%7,pow=e\7,cc=if(ch==1||ch==4,D,D+1));
  if(qe!=0,assert(pow<=(cc-res)\7+(cc-3-res)\7+1,"full actual residue-chain frame exponent");Var+=g*qe*first[pow+1]*T^(e+7);Expected-=g*qe*binomial(e,7)*T^(e+7)/4));
 assert(Var==Expected,"direct frame derivative versus Hasse operator");
 for(e=0,poldegree(P,T),my(cc=polcoef(P,e,T));if(cc!=0,back+=RP*cc*z^(M-al-be-2*e)*powers[e+1]));
 if(Var!=0,for(e=0,poldegree(Var,T),my(cc=polcoef(Var,e,T));if(cc!=0,assert(MP-al-be-2*e>=0,"variation pole bound");P1+=RP*cc*z^(MP-al-be-2*e)*powers[e+1])));
);
assert(domainchecked==2 && back==P0 && cuts(P0,M,N,uu,ii,W)==vector(13,j,0*o)~,"full source kernel identity");
assert(finitecuts(P1,MP,N,uu,ii,M)==vector(6,j,0*o)~,"variation retains all six finite cuts");
my(top=sum(j=0,13,polcoef(P1,2*MP-j,z)*h^j)+O(h^14),bottom=sum(j=0,13,polcoef(P1,j,z)*h^j)+O(h^14),upper=top*(o-uu*h+O(h^14))^(-N),lower=bottom/C*(o-h/uu+O(h^14))^(-N),R0=sum(j=0,13,polcoef(lower,j,h)*z^j+polcoef(upper,j,h)*z^(40-j)),red=P1-marked*R0);
for(j=0,13,assert(polcoef(red,j,z)==0 && polcoef(red,2*MP-j,z)==0,"all outer-pole levels cancelled"));
my(reduced=red/z^14);assert(denominator(reduced)==1 && poldegree(reduced,z)<=2*M,"return to original ambient");
my(bv=cuts(reduced,M,N,uu,ii,W),BM=Mat(vector(13,j,cuts(marked*z^(j-1),M,N,uu,ii,W))),left=matker(BM~));assert(matsize(left)[2]==1,"one-dimensional bounded cokernel");
my(value=(left~*bv)[1]);print("FIELD=",modulus," q=",q," D=",D," N=",N," u=",uu);
print("FULL_REDUCED_CUT_VECTOR=",bv);print("SMALL_COKERNEL_SCALAR=",value);
my(OUT="research/results/bmd-eight-exceptional-deformation-20261006/full-control-values.sing");
write(OUT,"ring Point=(7,a),(t),dp;minpoly=",liftall(modulus),";");write(OUT,"number PointU=",uu,";number PointZ=",zz,";");write(OUT,"matrix Actual[13][1];");for(j=1,13,write(OUT,"Actual[",j,",1]=",bv[j],";"));
print("PASS full polynomial, both original-domain lift rows, frame derivative and all pole/finite cuts.");
}
quit;
