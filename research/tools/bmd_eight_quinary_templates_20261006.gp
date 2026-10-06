\\ Exact local templates for the 25 characteristic-five bulk residues.
\\ High outlier coefficients need only h^0..h^3; marked binomial indices <=8.
default(parisizemax,3000000000);
default(nbthreads,1);
h;x;y;c;u;
assert(b,s)={if(!b,error(s));};
read("research/results/bmd-eight-quinary-source-20261006/profiles.gp");
profA(D)={my(a=QUINARY_PROFILES[((D+41)*11)%25+1][3]);[2*D+a[1],vector(#a[2],j,[[2*D+a[2][j],1]])];};
profB(D)={
 my(a=QUINARY_PROFILES[((D+41)*11)%25+1][4]);assert(#a==2,"exceptional domain state");
 [2*D+a[1],vector(#a[2],j,my(poly=a[2][j],v=List());for(k=0,poldegree(poly,z),my(co=polcoef(poly,k,z));if(co!=0,listput(v,[2*D-25+k,co])));Vec(v))];
};
maxdegree(S)={my(m=S[1]);for(j=1,#S[2],for(k=1,#S[2][j],m=max(m,S[2][j][k][1]+3)));m;};
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hsum(j,ord,shift,N,M,u,X,Y)={
 my(v=0*X,U=u^2+1);
 for(ia=0,ord,my(ib=ord-ia);for(k=0,ib,v+=binomial(j-M,ia)*binomial(N,ib)*(-1)^ib*U^(3-ib)*binomial(ib,k)*u^(ib-k)*vv(j-ia+k+shift,X,Y)));
 v;
};
evalpoint(P,a,C,X,Y)={subst(subst(subst(subst(P,'u,a),'c,C),'x,X),'y,Y);};
OUT=getenv("OUT");if(OUT==0||OUT=="",error("OUT required"));
{
my(o=Mod(1,5),u=o*'u,CP=o*'c,XP=o*'x,YP=o*'y,modulus=ffinit(5,6,'a),fa=ffgen(modulus,'a),fo=fa^0,ii=ffprimroot(fa)^((5^6-1)/4));
write(OUT,"// Generated exact polynomial matrices over F5[u,c,x,y]; primitive high rows.");
print("CONTROL_FIELD=",modulus," mark=",fa);
for(d=6,30,
 my(D=16*d-41,N=8*(D+1),exception=(d%5==1),AA=profA(D),BB=if(exception,profB(D),AA),powers=if(exception,[[5,0],[2,0],[0,3],[3,3]],[[3,0],[2,0],[0,3],[1,3]]),spaces=if(exception,[AA,BB,BB,AA],[AA,AA,AA,AA]),M=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(spaces[j]))),kap=2*M+1-N,nfin=4+2*exception,Mat=matrix(kap,kap),row=nfin,rs=u/(u^2+1),ss=u/(u^2-1),a0=rs^2,S=u^2+u^-2,maxlow=0,maxtail=0);
 for(j=0,kap-1,
  Mat[1,j+1]=(j-M+N)+(M-j)*u;
  Mat[2,j+1]=(-1)^j*((j-M+N)+(j-M)*u);
  Mat[3,j+1]=vv(j,XP,YP);
  Mat[4,j+1]=((j-M)*(u^2+1)+N)*vv(j-1,XP,YP)-N*u*vv(j,XP,YP);
  if(exception,
   Mat[5,j+1]=((j-M)*(u^2+1)+N)*vv(j,XP,YP)-N*u*vv(j+1,XP,YP);
   Mat[6,j+1]=hsum(j,3,0,N,M,u,XP,YP)-hsum(j,2,1,N,M,u,XP,YP);
  );
 );
 for(ch=1,4,
  my(al=powers[ch][1],be=powers[ch][2],re=(-1)^be,Space=spaces[ch],main=al+be+2*Space[1],hi=M-(M-al-be)%2,wid=(hi-main)/2,levels=vector(wid,j,hi-2*(j-1)),Out=matrix(wid,#Space[2]),Rel);
  for(j=1,#Space[2],
   my(emax=vecmax(vector(#Space[2][j],k,Space[2][j][k][1])));
   for(k=1,#Space[2][j],
    my(e=Space[2][j][k][1],coef=Space[2][j][k][2],lead=al+be+6+2*e,poly=coef*(-a0)^(e-emax)*(1+h)^(al+2)*(1-h)^(be+4)*(1-S*h+h^2+O(h^25))^e);
    for(i=1,wid,my(ix=(lead-levels[i])/2);if(ix>=0,assert(ix<25,"source tail period bound");maxtail=max(maxtail,ix);Out[i,j]+=polcoef(poly,ix,h)));
   );
  );
  if(#Space[2],assert(matrank(Out)==#Space[2],"outlier independence");Rel=matker(Out~)~,Rel=o*matid(wid));
  my(H=matrix(wid,kap,i,j,my(r=M-levels[i],k=r-kap+j);if(k>=0,o*binomial(N,k)*(-u)^k,0*o)),L=matrix(wid,kap,i,j,my(r=M-levels[i],k=r-j+1);if(k>=0,re*o*binomial(N,k)*(-1)^k*u^-k,0*o)));
  if(wid,maxlow=max(maxlow,M-levels[wid]));
  if(matsize(Rel)[1],
   my(A0=Rel*H,A1=Rel*L);
   for(i=1,matsize(A0)[1],
    my(den=o,gcdrow=0*o);
    for(j=1,kap,den=lcm(den,denominator(A0[i,j]));den=lcm(den,denominator(A1[i,j])));
    for(j=1,kap,A0[i,j]*=den;A1[i,j]*=den;assert(denominator(A0[i,j])==1 && denominator(A1[i,j])==1,"exact polynomial high row");gcdrow=gcd(gcdrow,gcd(A0[i,j],A1[i,j])));
    assert(gcdrow!=0,"nonzero high row");row++;
    for(j=1,kap,Mat[row,j]=(A0[i,j]+CP*A1[i,j])/gcdrow);
   );
  );
 );
 assert(row==kap && maxlow<25,"complete local template bound");
 my(Cv=fa^N,Iv=(fa-ii)^N,Jv=(fa+ii)^N,Xv=Iv+Jv,Yv=ii*(Iv-Jv),ME=matrix(kap,kap,i,j,evalpoint(Mat[i,j],fa,Cv,Xv,Yv)),jets=vector(4),nodes=[fo,-fo,ii,-ii],UF=fa^2+1,phase=(-1)^(M/2));
 for(node=1,4,
  my(zz=nodes[node]+v+O(v^4),F=zz^(-M)*(zz-fa)^N,Jt=matrix(4,kap));
  for(j=1,kap,for(k=0,3,Jt[k+1,j]=polcoef(F,k,v));F*=zz);
  jets[node]=Jt;
 );
 for(j=1,kap,
  assert(ME[1,j]==jets[1][2,j]/(1-fa)^(N-1) && ME[2,j]==jets[2][2,j]/(-1-fa)^(N-1),"direct real-node derivative cuts");
  assert(ME[3,j]==phase*(jets[3][1,j]+jets[4][1,j]) && ME[4,j]==phase*UF*(jets[3][2,j]+jets[4][2,j]),"direct value and derivative sum cuts");
  if(exception,assert(ME[5,j]==phase*UF*ii*(jets[3][2,j]-jets[4][2,j]) && ME[6,j]==phase*UF^3*(jets[3][4,j]+jets[4][4,j]-ii*(jets[3][3,j]-jets[4][3,j])),"direct exceptional Hasse cuts"));
 );
 my(rk=matrank(ME));
 print("PASS dmod25=",d%25," representative=",d," size=",kap," marked_rank=",rk," max_marked_index=",maxlow," max_outlier_index=",maxtail);
 write(OUT,"matrix B",d,"[",kap,"][",kap,"];");
 for(i=1,kap,for(j=1,kap,if(Mat[i,j]!=0,write(OUT,"B",d,"[",i,",",j,"]=",liftall(Mat[i,j]),";"))));
 write(OUT,"assess_template(B",d,",",d,",",N,");");
);
print("PASS all25 complete symbolic templates and direct finite-cut checks.");
}
quit;
