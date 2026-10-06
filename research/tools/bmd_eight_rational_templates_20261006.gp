\\ Exact integer matrices for eight rational residue states, with local denominators removed by unit pivots.
\\ Each high outlier has leading coefficient1 after its own nonzero field scale.
default(parisizemax,3000000000);
default(nbthreads,1);
h;x;y;c;u;
assert(b,s)={if(!b,error(s));};
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hsum(j,ord,shift,N,M,u,X,Y)={my(v=0*X,U=u^2+1);for(ia=0,ord,my(ib=ord-ia);for(k=0,ib,v+=binomial(j-M,ia)*binomial(N,ib)*(-1)^ib*U^(3-ib)*binomial(ib,k)*u^(ib-k)*vv(j-ia+k+shift,X,Y)));v;};
maxdegree(S)={my(m=S[1]);for(j=1,#S[2],m=max(m,S[2][j]+3));m;};
evalpoint(P,a,C,X,Y)={subst(subst(subst(subst(P,'u,a),'c,C),'x,X),'y,Y);};
OUT=getenv("OUT");assert(OUT!="" && OUT!=0,"OUT required");
{
my(states=[0,1,1/2,-1/2,3/2,-3/4,-5/4,5],profiles=[[0,[0]],[-1,[-1,-2]],[-1,[0,-1]],[0,[1]],[-2,[-1,-2,-3]],[1,[]],[1,[]],[1,[]]],u='u,CP='c,XP='x,YP='y,modulus=ffinit(101,2,'a),fa=ffgen(modulus,'a),fo=fa^0,ii=ffprimroot(fa)^((101^2-1)/4));
write(OUT,"// Exact integer matrices in u,c,x,y for rational D residue states.");
print("CONTROL_FIELD=",modulus," mark=a");
for(si=1,8,
 my(r=states[si],N=8*r+8,exception=(si==8),AA=profiles[si],BB=AA,powers=if(exception,[[5,0],[2,0],[0,3],[3,3]],[[3,0],[2,0],[0,3],[1,3]]),spaces=[AA,BB,BB,AA],K=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(spaces[j]))),M=4*r+K,kap=2*K-7,nfin=4+2*exception,Mat=matrix(kap,kap),row=nfin,S=u^2+u^-2,maxlow=0,maxtail=0);
 for(j=0,kap-1,
  Mat[1,j+1]=(j-M+N)+(M-j)*u;Mat[2,j+1]=(-1)^j*((j-M+N)+(j-M)*u);
  Mat[3,j+1]=vv(j,XP,YP);Mat[4,j+1]=((j-M)*(u^2+1)+N)*vv(j-1,XP,YP)-N*u*vv(j,XP,YP);
  if(exception,Mat[5,j+1]=((j-M)*(u^2+1)+N)*vv(j,XP,YP)-N*u*vv(j+1,XP,YP);Mat[6,j+1]=hsum(j,3,0,N,M,u,XP,YP)-hsum(j,2,1,N,M,u,XP,YP));
 );
 for(ch=1,4,
  my(al=powers[ch][1],be=powers[ch][2],re=(-1)^be,Space=spaces[ch],main=al+be+2*Space[1],hi=K-(K-al-be)%2,wid=(hi-main)/2,levels=vector(wid,j,hi-2*(j-1)),Out=matrix(wid,#Space[2]),Rel=matid(wid),pivs=List());
  for(j=1,#Space[2],
   my(e=2*r+Space[2][j],lead=al+be+6+2*Space[2][j],poly=(1+h)^(al+2)*(1-h)^(be+4)*(1-S*h+h^2+O(h^9))^e);
   for(i=1,wid,my(ix=(lead-levels[i])/2);if(ix>=0,assert(ix<9,"bounded source tail");maxtail=max(maxtail,ix);Out[i,j]=polcoef(poly,ix,h)));
  );
  for(j=1,#Space[2],
   my(ip=0);for(i=1,wid,if(Out[i,j]!=0,ip=i;break));assert(ip && Out[ip,j]==1,"unit leading outlier pivot");listput(pivs,ip);
   for(i=1,wid,if(i!=ip,my(mu=Out[i,j]);Out[i,]-=mu*Out[ip,];Rel[i,]-=mu*Rel[ip,]));
  );
  my(keep=select(i->!setsearch(Set(Vec(pivs)),i),vector(wid,j,j)),RR=matrix(#keep,wid,i,j,Rel[keep[i],j]),H=matrix(wid,kap,i,j,my(z=K-levels[i],k=z-kap+j);if(k>=0,binomial(N,k)*(-u)^k,0)),L=matrix(wid,kap,i,j,my(z=K-levels[i],k=z-j+1);if(k>=0,re*binomial(N,k)*(-1)^k*u^-k,0)));
  if(wid,maxlow=max(maxlow,K-levels[wid]));
  my(A0=RR*H,A1=RR*L);
  for(i=1,#keep,
   my(val=1000);for(j=1,kap,A0[i,j]*=u^64;A1[i,j]*=u^64;if(A0[i,j]!=0,val=min(val,valuation(A0[i,j],u)));if(A1[i,j]!=0,val=min(val,valuation(A1[i,j],u))));assert(val<1000,"nonzero high cut");row++;
   for(j=1,kap,Mat[row,j]=(A0[i,j]+CP*A1[i,j])/u^val;assert(denominator(Mat[row,j])==1,"integer polynomial matrix entry"));
  );
 );
 assert(row==kap && maxlow<=8 && maxtail<=3,"complete bounded local matrix");
 my(dd=0);for(d=6,106,if(Mod(16*d-41,101)==Mod(r,101),dd=d;break));assert(dd>=6,"actual control degree");
 my(Da=16*dd-41,Na=8*(Da+1),Ma=4*Da+K,Cv=fa^Na,Iv=(fa-ii)^Na,Jv=(fa+ii)^Na,Xv=Iv+Jv,Yv=ii*(Iv-Jv),ME=matrix(kap,kap,i,j,evalpoint(Mat[i,j],fa,Cv,Xv,Yv)),jets=vector(4),nodes=[fo,-fo,ii,-ii],UF=fa^2+1,phase=(-1)^(Ma/2));
 for(node=1,4,my(zz=nodes[node]+v+O(v^4),F=zz^(-Ma)*(zz-fa)^Na,Jt=matrix(4,kap));for(j=1,kap,for(k=0,3,Jt[k+1,j]=polcoef(F,k,v));F*=zz);jets[node]=Jt;);
 for(j=1,kap,
  assert(ME[1,j]==jets[1][2,j]/(1-fa)^(Na-1) && ME[2,j]==jets[2][2,j]/(-1-fa)^(Na-1),"actual real-node derivative cuts");
  assert(ME[3,j]==phase*(jets[3][1,j]+jets[4][1,j]) && ME[4,j]==phase*UF*(jets[3][2,j]+jets[4][2,j]),"actual complex-node cuts");
  if(exception,assert(ME[5,j]==phase*UF*ii*(jets[3][2,j]-jets[4][2,j]) && ME[6,j]==phase*UF^3*(jets[3][4,j]+jets[4][4,j]-ii*(jets[3][3,j]-jets[4][3,j])),"actual exceptional Hasse cuts"));
 );
 print("STATE=",si," r=",r," K=",K," size=",kap," n0=",N," marked_index=",maxlow," outlier_index=",maxtail," control_d=",dd," p101_rank=",matrank(ME));
 write(OUT,"matrix B",si,"[",kap,"][",kap,"];");for(i=1,kap,for(j=1,kap,if(Mat[i,j]!=0,write(OUT,"B",si,"[",i,",",j,"]=",Mat[i,j],";"))));write(OUT,"assess_template(B",si,",",si,",",N,");");
);
print("PASS all eight integer rational templates and direct finite-Hasse controls.");
}
quit;
