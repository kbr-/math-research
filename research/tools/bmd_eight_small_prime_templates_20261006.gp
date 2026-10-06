\\ Minimal local digit inventory of actual p7,p11,p13 marked maps; all global powers retained.
default(parisizemax,3000000000);
default(nbthreads,1);
h;x;y;c;u;
assert(b,s)={if(!b,error(s));};
read("research/results/bmd-eight-small-prime-source-20261006/profiles.gp");
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hsum(j,ord,shift,N,M,u,X,Y)={my(v=0*X,U=u^2+1);for(ia=0,ord,my(ib=ord-ia);for(k=0,ib,v+=binomial(j-M,ia)*binomial(N,ib)*(-1)^ib*U^(3-ib)*binomial(ib,k)*u^(ib-k)*vv(j-ia+k+shift,X,Y)));v;};
maxdegree(S)={my(m=S[1]);for(j=1,#S[2],for(k=1,#S[2][j],m=max(m,S[2][j][k][1]+3)));m;};
evalpoint(P,a,C,X,Y)={subst(subst(subst(subst(P,'u,a),'c,C),'x,X),'y,Y);};
profA(D,dd,pi)={my(a=SMALL_PRIME_PROFILES[pi][2][dd%SMALL_PRIME_PROFILES[pi][1]+1][3]);[2*D+a[1],vector(#a[2],j,[[2*D+a[2][j],1]])];};
profB(D,dd,pi)={my(pp=SMALL_PRIME_PROFILES[pi][1],a=SMALL_PRIME_PROFILES[pi][2][dd%pp+1][4]);assert(#a==2,"exceptional profile present");[2*D+a[1],vector(#a[2],j,my(poly=a[2][j],v=List());for(k=0,poldegree(poly,z),my(co=polcoef(poly,k,z));if(co!=0,listput(v,[2*D-pp+k,co])));Vec(v))];};
{
my(total=0);
for(pi=1,3,
 my(pp=SMALL_PRIME_PROFILES[pi][1],o=Mod(1,pp),u=o*'u,CP=o*'c,XP=o*'x,YP=o*'y,modulus=ffinit(pp,4,'a),fa=ffgen(modulus,'a),fo=fa^0,ii=ffprimroot(fa)^((pp^4-1)/4),OUT=Str("research/results/bmd-eight-small-prime-source-20261006/matrices-p",pp,".sing"));
 write(OUT,"// Complete minimal local marked inventory at p",pp,".");print("CONTROL_FIELD p=",pp," modulus=",modulus);
 for(d0=6,pp+5,
  my(D0=16*d0-41,ex=((D0-5)%pp==0),A0=profA(D0,d0,pi),B0=if(ex,profB(D0,d0,pi),A0),powers=if(ex,[[5,0],[2,0],[0,3],[3,3]],[[3,0],[2,0],[0,3],[1,3]]),ss0=if(ex,[A0,B0,B0,A0],[A0,A0,A0,A0]),MM=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(ss0[j]))),maxindex=0);
  for(ch=1,4,my(al=powers[ch][1],be=powers[ch][2],main=al+be+2*ss0[ch][1],hi=MM-(MM-al-be)%2,wid=(hi-main)/2);if(wid,maxindex=max(maxindex,MM-(main+2))));
  my(period=pp);while(period<=max(maxindex,3),period*=pp);
  for(digit=0,period/pp-1,
   my(d=d0+pp*digit,D=16*d-41,N=8*(D+1),AA=profA(D,d,pi),BB=if(ex,profB(D,d,pi),AA),spaces=if(ex,[AA,BB,BB,AA],[AA,AA,AA,AA]),M=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(spaces[j]))),kap=2*M+1-N,nfin=4+2*ex,Mat=matrix(kap,kap),row=nfin,rs=u/(u^2+1),a0=rs^2,S=u^2+u^-2,maxlow=0,maxtail=0);
   for(j=0,kap-1,
    Mat[1,j+1]=(j-M+N)+(M-j)*u;Mat[2,j+1]=(-1)^j*((j-M+N)+(j-M)*u);Mat[3,j+1]=vv(j,XP,YP);Mat[4,j+1]=((j-M)*(u^2+1)+N)*vv(j-1,XP,YP)-N*u*vv(j,XP,YP);
    if(ex,Mat[5,j+1]=((j-M)*(u^2+1)+N)*vv(j,XP,YP)-N*u*vv(j+1,XP,YP);Mat[6,j+1]=hsum(j,3,0,N,M,u,XP,YP)-hsum(j,2,1,N,M,u,XP,YP));
   );
   for(ch=1,4,
    my(al=powers[ch][1],be=powers[ch][2],re=(-1)^be,Space=spaces[ch],main=al+be+2*Space[1],hi=M-(M-al-be)%2,wid=(hi-main)/2,levels=vector(wid,j,hi-2*(j-1)),Out=matrix(wid,#Space[2]),Rel);
    for(j=1,#Space[2],my(emax=vecmax(vector(#Space[2][j],k,Space[2][j][k][1])));
     for(k=1,#Space[2][j],my(e=Space[2][j][k][1],co=Space[2][j][k][2],lead=al+be+6+2*e,poly=co*(-a0)^(e-emax)*(1+h)^(al+2)*(1-h)^(be+4)*(1-S*h+h^2+O(h^16))^e);
      for(i=1,wid,my(ix=(lead-levels[i])/2);if(ix>=0,assert(ix<period && ix<16,"source tail digit bound");maxtail=max(maxtail,ix);Out[i,j]+=polcoef(poly,ix,h)));
     );
    );
    if(#Space[2],assert(matrank(Out)==#Space[2],"full outlier independence");Rel=matker(Out~)~,Rel=o*matid(wid));
    my(H=matrix(wid,kap,i,j,my(r=M-levels[i],k=r-kap+j);if(k>=0,o*binomial(N,k)*(-u)^k,0*o)),L=matrix(wid,kap,i,j,my(r=M-levels[i],k=r-j+1);if(k>=0,re*o*binomial(N,k)*(-1)^k*u^-k,0*o)));
    if(wid,maxlow=max(maxlow,M-levels[wid]));my(High0=Rel*H,High1=Rel*L);
    for(i=1,matsize(Rel)[1],my(den=o,gcdrow=0*o);for(j=1,kap,den=lcm(den,denominator(High0[i,j]));den=lcm(den,denominator(High1[i,j])));
     for(j=1,kap,High0[i,j]*=den;High1[i,j]*=den;assert(denominator(High0[i,j])==1 && denominator(High1[i,j])==1,"polynomial high row");gcdrow=gcd(gcdrow,gcd(High0[i,j],High1[i,j])));
     assert(gcdrow!=0,"nonzero high row");row++;for(j=1,kap,Mat[row,j]=(High0[i,j]+CP*High1[i,j])/gcdrow);
    );
   );
   assert(row==kap && maxlow<=maxindex && maxlow<period,"complete minimal digit criterion");
   my(Cv=fa^N,Iv=(fa-ii)^N,Jv=(fa+ii)^N,Xv=Iv+Jv,Yv=ii*(Iv-Jv),ME=matrix(kap,kap,i,j,evalpoint(Mat[i,j],fa,Cv,Xv,Yv)),jets=vector(4),nodes=[fo,-fo,ii,-ii],UF=fa^2+1,phase=(-1)^(M/2));
   for(node=1,4,my(zz=nodes[node]+v+O(v^4),F=zz^(-M)*(zz-fa)^N,Jt=matrix(4,kap));for(j=1,kap,for(k=0,3,Jt[k+1,j]=polcoef(F,k,v));F*=zz);jets[node]=Jt;);
   for(j=1,kap,
    assert(ME[1,j]==jets[1][2,j]/(1-fa)^(N-1) && ME[2,j]==jets[2][2,j]/(-1-fa)^(N-1),"direct real-node cuts");
    assert(ME[3,j]==phase*(jets[3][1,j]+jets[4][1,j]) && ME[4,j]==phase*UF*(jets[3][2,j]+jets[4][2,j]),"direct complex-node cuts");
    if(ex,assert(ME[5,j]==phase*UF*ii*(jets[3][2,j]-jets[4][2,j]) && ME[6,j]==phase*UF^3*(jets[3][4,j]+jets[4][4,j]-ii*(jets[3][3,j]-jets[4][3,j])),"direct exceptional Hasse cuts"));
   );
   total++;print("STATE p=",pp," d=",d," period=",period," class=",d%period," size=",kap," index=",maxlow," tail=",maxtail," rank=",matrank(ME));
   my(lx=2*sum(k=0,(period-1)\2,(-1)^k*o*binomial(N%period,2*k)*u^(2*k)),ly=-2*sum(k=0,(period-2)\2,(-1)^k*o*binomial(N%period,2*k+1)*u^(2*k+1)));
   write(OUT,"matrix B",d,"[",kap,"][",kap,"];");for(i=1,kap,for(j=1,kap,if(Mat[i,j]!=0,write(OUT,"B",d,"[",i,",",j,"]=",liftall(Mat[i,j]),";"))));
   write(OUT,"assess_template(B",d,",",pp,",",d,",",N,",",period,",",liftall(lx),",",liftall(ly),");");
  );
 );
);
assert(total==49,"minimal local-state inventory");print("PASS all49 complete symbolic states and direct finite-Hasse controls.");
}
quit;
