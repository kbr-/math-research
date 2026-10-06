\\ Full polynomial-source control of the remaining d2mod9 repair, at d11.
\\ Four character divisions replace a larger jet-matrix inversion.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
cut(P,M,N,u,ii)={
 my(nodes=[u^0,-u^0,ii,-ii],V=vector(4,j,nodes[j]^(-M)*subst(P,z,nodes[j])),Der=deriv(P,z),DD=vector(4,j,nodes[j]^(-M)*subst(Der,z,nodes[j])-M*nodes[j]^(-M-1)*subst(P,z,nodes[j])),H=vector(7,j,polcoef(P,2*M-j+1,z)),L=vector(7,j,polcoef(P,j-1,z)),C=u^N,phase=(-1)^(M/2));
 [DD[1]/(1-u)^(N-1),DD[2]/(-1-u)^(N-1),phase*(V[3]+V[4]),phase*(u^2+1)*(DD[3]+DD[4]),H[1]+L[1],H[5],u^4/C*L[5],u^6*(H[7]-2*H[3]+L[7]-2*L[3]),u^2*(H[3]-2*H[1]-L[3]+2*L[1]),H[4]-H[2],H[6]-2*H[2],u^3/C*(L[4]-L[2]),u^5/C*(L[6]-2*L[2])]~;
};
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hi(r,j,u)={my(k=r-12+j);if(k<0,0*u,u^k);};
ln(r,j,u)={if(j>r,0*u,u^j);};
{
my(d=11,D=135,N=1088,M=550,q=2*D+1,rows=[1,3,5],Cuts=matrix(3,q+1,i,j,Mod((-1)^(j-1-rows[i])*binomial(j-1,rows[i]),3)),PV=[2*D+2,2*D,2*D-1],Inv=matrix(3,3,i,j,Cuts[i,PV[j]])^-1,E=concat(vector(2*D-2,j,j-1),[2*D]),delta=vector(#E),xp=(Mod(1,3)+w+O(w^(q+3)))^365,yp=vector(q+1));
yp[1]=Mod(1,3);for(j=2,q+1,yp[j]=yp[j-1]*(xp-1));
for(j=1,#E,
 my(e=E[j],a=Inv*Cuts[,e+1],f=Mod(2,3)^e*(yp[e+1]-sum(k=1,3,a[k]*yp[PV[k]])));
 assert(polcoef(f,e,w)==1,"normalized frame");delta[j]=polcoef(f,e+1,w);
 assert(delta[j]==Mod(if(e==2*D-3,2,-e),3),"second-family actual frame variation");
);
my(modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,u=a,ii=ffprimroot(a)^((3^10-1)/4),rs=u/(u^2+1),ss=u/(u^2-1),aa=rs^2,b=-ss^2/aa,C=u^N,Su=u^2+u^-2,Fz=o*z^4-Su*z^2+o,powers=vector(2*D+5),g=(1-T)*(1+b*T)^2,pref=[[3,0],[2,0],[0,3],[1,3]]);
powers[1]=o;for(j=2,#powers,powers[j]=powers[j-1]*Fz);
my(Qz=(z-u)*(z^2+1)^2*(z^6-z^4+1+u*C*z*(z^6-z^2+1)),P0=(z-u)^N*Qz,Rev=z^(2*M)*subst(P0,z,1/z),neg=subst(P0,z,-z),negRev=subst(Rev,z,-z),P1=0*o,reconstructed=0*o);
for(ch=1,4,
 my(al=pref[ch][1],be=pref[ch][2],pa=(-1)^(al+be),re=(-1)^be,RP=rs^al*ss^be*(z^2+1)^al*(z^2-1)^be,Proj=(P0+pa*neg+re*Rev+pa*re*negRev)/4,k=M-al-be,m=(k+1)\2,Rpoly=z^(2*m-k)*Proj/RP,co=vector(m+1,j,0*o));
 assert(denominator(Rpoly)==1,"finite character divisibilities");
 forstep(e=m,0,-1,
  my(val=polcoef(Rpoly,2*m+2*e,z)/(-aa)^e);co[e+1]=val;
  if(val!=0,Rpoly-=val*(-aa)^e*z^(2*m-2*e)*powers[e+1]);
 );
 assert(Rpoly==0,"complete invariant polynomial reconstruction");
 my(P=Polrev(co,T),Rem=P%g,Quot=(P-Rem)/g);
 assert(poldegree(P,T)<=2*D+3 && poldegree(Rem,T)<3 && denominator(Quot)==1 && poldegree(Quot,T)<=2*D,"source degree bounds");
 assert(polcoef(Quot,2*D-1,T)==0 && polcoef(Quot,2*D-2,T)==0,"actual missing quotient directions");
 my(Var=2*T*Rem+g*sum(j=1,#E,polcoef(Quot,E[j],T)*delta[j]*T^(E[j]+1)),Expected=2*T*Rem+g*(-T^2*deriv(Quot,T)+2*polcoef(Quot,2*D-3,T)*T^(2*D-2)),part=0*o,back=0*o);
 assert(Var==Expected,"closed first-variation operator");
 for(e=0,poldegree(P,T),my(val=polcoef(P,e,T));if(val!=0,assert(M-al-be-2*e>=0,"kernel pole bound");back+=val*(-aa)^e*z^(M-al-be-2*e)*powers[e+1]));
 reconstructed+=RP*back;
 if(Var!=0,for(e=0,poldegree(Var,T),my(val=polcoef(Var,e,T));if(val!=0,assert(M-al-be-2*e>=0,"variation pole bound");part+=val*(-aa)^e*z^(M-al-be-2*e)*powers[e+1])));
 P1+=RP*part;
 for(outlier=0,1,
  my(ap=al+2*outlier,bp=be+4*outlier,lead=ap+bp+4*D,testpoly=rs^ap*ss^bp*(-aa)^(2*D)*z^(M-lead)*(z^2+1)^ap*(z^2-1)^bp*powers[2*D+1]);
  assert(cut(testpoly,M,N,u,ii)==vector(13,j,0*o)~,"top ordinary/outlier source cuts");
 );
);
assert(reconstructed==P0,"full kernel identity in actual source");
my(amplitude=aa*(1-u^2*C^2)/2,bv=cut(P1,M,N,u,ii),want=vector(13,j,0*o)~);want[11]=amplitude;want[13]=amplitude*u^5/C;
assert(bv==want,"actual full-source repair cut vector");
my(I=(u-ii)^N,J=(u+ii)^N,X=I+J,Y=ii*(I-J),cols=vector(13,j,cut(z^(j-1)*(z-u)^N,M,N,u,ii)),Marked=matrix(13,13,i,j,cols[j][i]),Template=matrix(13,13));
for(j=0,12,
 Template[,j+1]=[j+1+(1-j)*u,(-1)^j*(j+1+(j-1)*u),vv(j,X,Y),((j-1)*(u^2+1)+2)*vv(j-1,X,Y)-2*u*vv(j,X,Y),hi(0,j,u)+if(j==0,C,0*o),hi(4,j,u),ln(4,j,u),u^6*(hi(6,j,u)-2*hi(2,j,u))+C*(ln(6,j,u)-2*u^4*ln(2,j,u)),u^2*(hi(2,j,u)-2*hi(0,j,u))-C*(ln(2,j,u)-2*u^2*ln(0,j,u)),hi(3,j,u)-hi(1,j,u),hi(5,j,u)-2*hi(1,j,u),ln(3,j,u)-u^2*ln(1,j,u),ln(5,j,u)-2*u^4*ln(1,j,u)]~;
);
assert(Marked==Template,"every symbolic boundary matrix entry");
my(Repair=Marked);Repair[,8]=bv*C/amplitude;
assert(matdet(Repair)!=0,"nonzero first repair");
print("FIELD=",modulus," d=",d," D=",D," N=",N," u=",u);
print("FIRST_VARIATION_CUTS=",bv," amplitude=",amplitude);
print("REPAIR_DETERMINANT=",matdet(Repair));
print("PASS all actual frame coefficients, four character reconstructions, source cuts and full first-variation comparison.");
}
quit;
