\\ Independent original-root and literal monic-alternant reference.
\\ Full controls compare every norm coefficient, including selected cofactors.
\\ Large inputs check full norm gcds and three reduced point matrices; original
\\ roots independently check the noncolliding homogeneous direction.
default(parisizemax,1000000000);
default(parisize,128000000);
default(nbthreads,1);
x='x;z='z;Y=varhigher("Y");X=varhigher("X");T=varhigher("T");
assert(c,s)={if(!c,error(s));};
read(getenv("BMD_REDUCED_DATA"));
orig(aa,L)={
 my(N=#aa,m=N*(N-1)/2+2,o=aa[2]^0,out=List([vector(L,j,if(j==1,o,0*o)),vector(L,j,if(j==2,o,0*o))]));
 for(i=1,N,for(j=i+1,N,my(G=sqrt(o+(aa[i]+aa[j])*T+aa[i]*aa[j]*T^2+O(T^L)));listput(out,vector(L,k,polcoef(G,k-1,T)))));
 matrix(m,L,i,j,out[i][j])
};
normpoly(P,p,e)={if(P==0,return(0));my(NP=1);for(j=0,e-1,NP*=sum(k=0,poldegree(P,x),polcoef(P,k,x)^(p^j)*x^k));NP};
reduced(aa)={
 my(N=#aa,R=N*(N-1)/2,o=aa[2]^0,PX=prod(i=1,N,X-aa[i]),PY=subst(PX,X,Y),G=sqrt(o+o*T+O(T^(R+3))),bs=vector(R+3,j,polcoef(G,j-1,T)),M=matrix(R,R+1,i,j,0*o));
 for(j=0,R,
  my(k=j+2,C=sum(h=0,k,bs[h+1]*bs[k-h+1]*X^h*Y^(k-h)),qr=divrem(C,Y-X),a,b,row=0,H);
  assert(qr[2]==0,"literal alternant division");H=qr[1]%PX;
  H=sum(i=0,N-1,X^i*(polcoef(H,i,X)%PY));
  for(a=0,N-1,for(b=a+1,N-1,row++;M[row,j+1]=polcoef(polcoef(H,a,X),b,Y)));
 );M
};
{
for(ci=1,#DATA,
 my(d=DATA[ci],n=d[1],p=d[2],e=d[3],N=n+1,R=N*(N-1)/2,m=R+2,threshold=3*binomial(N,4),field=Mod(1,p)*Polrev(d[4],z),g=ffgen(field,'g),o=g^0,
 al=concat([0*o],vector(n,i,sum(j=0,e-1,d[5][i][j+1]*g^j))),be=concat([0*o],vector(n,i,sum(j=0,e-1,d[6][i][j+1]*g^j))),
 D0=Mod(1,p)*Polrev(d[7],x),D1=Mod(1,p)*Polrev(d[8],x),power=(p^e-1)/(p-1));
 assert(polisirreducible(field),"irreducible modulus");
 if(#d>=10&&d[10],
  my(Vline=prod(i=1,N,prod(j=i+1,N,al[j]-al[i]+x*(be[j]-be[i]))));
  assert(poldegree(Vline,x)==R&&poldegree(gcd(Vline,deriv(Vline,x)),x)==0,"independent separated collision parameters");
  print("SQUAREFREE_LINE_VANDERMONDE n=",n," p=",p," degree=",R)
 );
 assert(poldegree(D0,x)==e*threshold&&pollead(D0)==1,"full reduced norm degree");
 my(gcdall=gcd(D0,D1));for(j=1,#d[9],gcdall=gcd(gcdall,Mod(1,p)*Polrev(d[9][j][2],x)));
 assert(poldegree(gcdall,x)==0,"independent complete norm gcd");
 my(betaP=reduced(be),betaV=prod(i=1,N,prod(j=i+1,N,be[j]-be[i])),betaRoot=orig(be,m),lead=matdet(matrix(R,R,i,j,betaP[i,j])));
 assert(betaV!=0&&lead!=0,"full noncolliding homogeneous direction");
 assert(matdet(betaRoot)==betaV^N*lead,"independent original direction frame");
 my(normlead=lead^power);
 for(point=0,1,
  my(aa=vector(N,i,al[i]+point*be[i]),P=reduced(aa),v0=matdet(matrix(R,R,i,j,P[i,j])),v1=matdet(matrix(R,R,i,j,if(j<R,P[i,j],P[i,R+1]))));
  assert(o*subst(D0,x,point)==v0^power/normlead,"independent reduced initial value");
  assert(o*subst(D1,x,point)==v1^power/normlead,"independent reduced adjacent value");
  for(k=1,#d[9],
   my(j0=d[9][k][1],val);val=matdet(matrix(R,R,i,j,if(j==j0+1,P[i,R+1],P[i,j])));
   assert(o*subst(Mod(1,p)*Polrev(d[9][k][2],x),x,point)==val^power/normlead,"independent additional cofactor value")
  )
 );
 if(FULL_CONTROL==1,
  my(aa=vector(N,i,al[i]+x*be[i]),M=orig(aa,m+1),V=prod(i=1,N,prod(j=i+1,N,aa[j]-aa[i])),VP=V^N,
  raw=matdet(matrix(m,m,i,j,M[i,j])),raw1=matdet(matrix(m,m,i,j,if(j<m,M[i,j],M[i,m+1]))));
  assert(raw%VP==0&&raw1%VP==0,"exact original frame division");
  my(ND=normpoly(raw/VP,p,e),NA=normpoly(raw1/VP,p,e),lc=pollead(ND));
  assert(o*D0==ND/lc&&o*D1==NA/lc,"full original reduced norm coefficients");
  for(k=1,#d[9],
   my(j0=d[9][k][1],other);other=matdet(matrix(m,m,i,j,if(j==j0+3,M[i,m+1],M[i,j])));
   assert(other%VP==0,"additional original frame division");
   assert(o*Mod(1,p)*Polrev(d[9][k][2],x)==normpoly(other/VP,p,e)/lc,"full additional norm coefficients")
  )
 );
 if(FULL_CONTROL==2,
  print("FULL_REDUCED_BUILD n=",n," p=",p);
  my(aa=vector(N,i,al[i]+x*be[i]),P=reduced(aa),pairs=List(),ur=List(),uc=List());
  for(a=0,N-1,for(b=a+1,N-1,listput(pairs,[a,b])));
  for(j=0,R-1,for(i=1,R,if(pairs[i][1]+pairs[i][2]-1==j&&P[i,j+1]!=0,
   assert(poldegree(P[i,j+1],x)==0,"constant graded pivot");listput(ur,i);listput(uc,j+1);break
  )));
  my(freer=select(i->!setsearch(Set(Vec(ur)),i),[1..R]),freec=select(i->!setsearch(Set(Vec(uc)),i),[1..R+1]),kk=#ur,zz=#freer);
  assert(freec[#freec]==R+1&&freec[#freec-1]==R,"marked coordinates retained");
  my(U=matrix(kk,kk,i,j,P[ur[i],uc[j]]),E=matrix(kk,zz+1,i,j,P[ur[i],freec[j]]),C=matrix(zz,kk,i,j,P[freer[i],uc[j]]),D=matrix(zz,zz+1,i,j,P[freer[i],freec[j]]),UI=U^-1);
  assert(U*UI==matid(kk),"independent unit inverse");
  my(S=D-C*UI*E);
  print("FULL_REDUCED_DETERMINANTS n=",n," p=",p," size=",zz);
  my(a0=matdet(matrix(zz,zz,i,j,S[i,j])),a1=matdet(matrix(zz,zz,i,j,if(j<zz,S[i,j],S[i,zz+1]))),ND=normpoly(a0,p,e),NA=normpoly(a1,p,e),lc=pollead(ND));
  assert(o*D0==ND/lc&&o*D1==NA/lc,"complete independent reduced polynomial norms");
  for(k=1,#d[9],
   my(pos=setsearch(Set(freec),d[9][k][1]+1),other);
   assert(pos>0&&pos<=zz,"free cofactor position");
   other=matdet(matrix(zz,zz,i,j,if(j==pos,S[i,zz+1],S[i,j])));
   assert(o*Mod(1,p)*Polrev(d[9][k][2],x)==normpoly(other,p,e)/lc,"complete reduced additional norm")
  )
 );
 print("PASS n=",n," p=",p," e=",e," full_polynomial=",FULL_CONTROL," selected_minors=",2+#d[9]);
);
print("REDUCED_BOUNDARY_INDEPENDENT_COMPLETED")
}
quit;
