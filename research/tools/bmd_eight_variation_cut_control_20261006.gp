\\ Full Laurent-source check of the uniform first-variation cut vector, d6.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
cut(P,M,N,u,ii)={
 my(nodes=[u^0,-u^0,ii,-ii],V=vector(4,j,nodes[j]^(-M)*subst(P,z,nodes[j])),Der=deriv(P,z),D=vector(4,j,nodes[j]^(-M)*subst(Der,z,nodes[j])-M*nodes[j]^(-M-1)*subst(P,z,nodes[j])),H=vector(7,j,polcoef(P,2*M-j+1,z)),L=vector(7,j,polcoef(P,j-1,z)),C=u^N);
 [D[1]/(1-u)^(N-1),D[2]/(-1-u)^(N-1),V[3]+V[4],(u^2+1)*(D[3]+D[4]),H[1]+L[1],u^6*(H[7]+L[7]),H[2]+2*H[4]+H[6],u^5/C*(L[2]+2*L[4]+L[6]),u^4*(H[3]+H[5]-L[3]-L[5])]~;
};
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hi(rr,jj,u)={my(k=rr-8+jj);if(k<0,0*u,binomial(7,k)*(-u)^k);};
ln(rr,jj,u)={my(k=rr-jj);if(k<0,0*u,binomial(7,k)*(-1)^k*u^jj);};
{
my(d=6,D=55,N=448,M=228,E=concat(vector(2*D-3,j,j-1),[2*D-2,2*D-1]),nbase=3+#E,modulus=ffinit(3,10,'a),a=ffgen(modulus,'a),o=a^0,u=a,ii=ffprimroot(a)^((3^10-1)/4),rs=u/(u^2+1),ss=u/(u^2-1),aa=rs^2,Su=u^2+u^-2,Fz=o*z^4-Su*z^2+o,powers=vector(2*D),pref=[[3,0],[2,0],[0,3],[1,3]],functions=List(),delta=List());
powers[1]=o;for(j=2,#powers,powers[j]=powers[j-1]*Fz);
for(ch=1,4,
 for(j=1,nbase,
  my(core=(j>3),e=if(core,E[j-3],j-1),al=pref[ch][1]+2*core,be=pref[ch][2]+4*core,lead=al+be+2*e,poly=rs^al*ss^be*(-aa)^e*z^(M-lead)*(z^2+1)^al*(z^2-1)^be*powers[e+1]);
  assert(lead<=M,"full polynomial source within ambient");listput(functions,poly);listput(delta,if(core,if(e==2*D-1,0,-e),2));
 );
);
assert(#functions==N,"full source count");
my(Space=matrix(2*M+1,N,i,j,polcoef(functions[j],i-1,z)),P0=aa*z*(z-u)^(N+2)*(z^2+1)^2,target=vector(2*M+1,i,polcoef(P0,i-1,z))~,ix=matindexrank(Space));
assert(#ix[1]==N,"independent full source");
my(coords=matrix(N,N,i,j,Space[ix[1][i],j])^-1*vector(N,i,target[ix[1][i]])~);
assert(Space*coords==target,"explicit kernel source reconstruction");
my(P1=0*o);
for(j=1,N,if(delta[j]%3 && coords[j]!=0,assert(polcoef(functions[j],0,z)==0 && polcoef(functions[j],1,z)==0,"no hidden negative pole");P1+=coords[j]*delta[j]*(-aa)*Fz*(functions[j]/z^2)));
assert(denominator(P1)==1 && poldegree(P1,z)<=2*M,"first variation stays in ambient");
my(C=u^N,I=(u-ii)^N,J=(u+ii)^N,X=I+J,Y=ii*(I-J),amplitude=aa^2*(1+C*u^2)/2,bv=cut(P1,M,N,u,ii),want=[0,0,0,0,0,0,amplitude,amplitude*u^5/C,0]~);
assert(bv==want,"full polynomial first-variation cut vector");
my(markedcols=vector(9,j,cut(z^(j-1)*(z-u)^N,M,N,u,ii)),marked=matrix(9,9,i,j,markedcols[j][i]),formula=matrix(9,9));
for(j=0,8,
 formula[,j+1]=[(j+1)-j*u,(-1)^j*((j+1)+j*u),vv(j,X,Y),(j*(u^2+1)+1)*vv(j-1,X,Y)-u*vv(j,X,Y),hi(0,j,u)+if(j==0,C,0*o),u^6*hi(6,j,u)+C*ln(6,j,u),hi(1,j,u)+2*hi(3,j,u)+hi(5,j,u),u^4*ln(1,j,u)+2*u^2*ln(3,j,u)+ln(5,j,u),u^4*(hi(2,j,u)+hi(4,j,u))-C*(u^2*ln(2,j,u)+ln(4,j,u))]~;
);
assert(marked==formula,"symbolic nine-condition matrix against direct polynomial cuts");
my(repair=marked);repair[,8]=bv*C/amplitude;
assert(matdet(repair)!=0,"bounded repair nonzero at control");
print("FIELD=",modulus," d=",d," u=",u);
print("FIRST_VARIATION_CUTS=",bv," predicted_amplitude=",amplitude);
print("REPAIR_DETERMINANT=",matdet(repair));
print("PASS full kernel reconstruction, first variation, every cut entry and symbolic marked matrix.");
}
quit;
