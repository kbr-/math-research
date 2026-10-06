\\ Merge v into w instead of z into v in the actual elliptic source.
\\ At p7,D=0 or5, the new inner source F_D+R*x*F_D limits to F_(2D+1).
\\ At D5, both constrained coordinates give the same limit (opposite-point unit Wronskian).
default(parisizemax,3000000000);
default(nbthreads,1);
v;h;x;y;c;u;
assert(b,s)={if(!b,error(s));};
vv(j,X,Y)={my(k=(j%4+4)%4);[X,Y,-X,-Y][k+1];};
hsum(j,ord,shift,N,M,u,X,Y)={my(v=0*X,U=u^2+1);for(ia=0,ord,my(ib=ord-ia);for(k=0,ib,v+=binomial(j-M,ia)*binomial(N,ib)*(-1)^ib*U^(3-ib)*binomial(ib,k)*u^(ib-k)*vv(j-ia+k+shift,X,Y)));v;};
evalpoint(P,a,C,X,Y)={subst(subst(subst(subst(P,'u,a),'c,C),'x,X),'y,Y);};
{
my(o=Mod(1,7),u=o*'u,CP=o*'c,XP=o*'x,YP=o*'y,modulus=ffinit(7,4,'a),fa=ffgen(modulus,'a),fo=fa^0,ii=ffprimroot(fa)^((7^4-1)/4),OUT="research/results/bmd-eight-small-prime-source-20261006/seven-alternative.sing");
write(OUT,"// Actual alternative full-source marked maps for p7,D0,D5.");print("FIELD=",modulus);
for(cs=1,2,
 my(d=[10,9][cs],D=16*d-41,N=8*(D+1),ex=(cs==2),L=2*D+1,powers=if(ex,[[5,0],[2,0],[0,7],[3,7]],[[3,0],[2,0],[0,7],[1,7]]),M=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*L)),kap=2*M+1-N,Mat=matrix(kap,kap),row=0);
 assert(Mod(2*D+1,7)!=0,"ordinary core consecutive");
 if(ex,my(q=Mod(2*D+3,7));assert(q!=0 && 1-2/q!=0 && 1-4/q!=0,"exceptional top-two opposite-point unit block"));
 for(node=1,2,
  my(a=o*(-1)^(node-1),z=a+v+O(v^6),zz=1/z);
  for(hh=1,3,row++;my(h0=2*hh-1);
   for(j=0,kap-1,
    my(e=(j-M)%7,n=N%7,F=(z/a)^e*(1+(z-a)/(a-u))^n,G=(zz/a)^e*(1+(zz-a)/(a-u))^n);
    Mat[row,j+1]=a^j*(a-u)^5*polcoef(F-G,h0,v);
   );
  );
 );
 for(j=0,kap-1,
  Mat[7,j+1]=vv(j,XP,YP);Mat[8,j+1]=((j-M)*(u^2+1)+N)*vv(j-1,XP,YP)-N*u*vv(j,XP,YP);
  if(ex,Mat[9,j+1]=((j-M)*(u^2+1)+N)*vv(j,XP,YP)-N*u*vv(j+1,XP,YP);Mat[10,j+1]=hsum(j,3,0,N,M,u,XP,YP)-hsum(j,2,1,N,M,u,XP,YP));
 );row=8+2*ex;
 for(ch=1,4,
  my(al=powers[ch][1],be=powers[ch][2],re=(-1)^be,hi=M-(M-al-be)%2,main=al+be+2*L,wid=(hi-main)/2);
  for(k=1,wid,row++;my(r=M-hi+2*(k-1));assert(r<7,"one-digit high cuts");
   for(j=0,kap-1,my(kh=r-kap+1+j,kl=r-j);Mat[row,j+1]=if(kh>=0,o*binomial(N,kh)*(-u)^kh,0*o)+re*CP*if(kl>=0,o*binomial(N,kl)*(-1)^kl*u^-kl,0*o));
  );
 );assert(row==kap,"complete alternative codimension");
 for(i=1,kap,
  my(den=o,gcdrow=0*o);for(j=1,kap,den=lcm(den,denominator(Mat[i,j])));for(j=1,kap,Mat[i,j]*=den;gcdrow=gcd(gcdrow,Mat[i,j]));assert(gcdrow!=0,"nonzero cut row");for(j=1,kap,Mat[i,j]/=gcdrow;assert(denominator(Mat[i,j])==1,"polynomial normalized cut"));
 );
 my(uf=fa,rs=uf/(uf^2+1),ss=uf/(uf^2-1),a0=rs^2,b0=-ss^2/a0,t=fo*T+O(T^N),r=sqrt(1-t),s=sqrt(1+b0*t),source=List());
 for(ch=1,4,my(pre=r^powers[ch][1]*s^powers[ch][2]);for(j=0,L,listput(source,pre*t^j)));
 assert(#source==N,"full alternative source dimension");
 my(fullrank=matrank(matrix(N,N,i,j,polcoef(source[i],j-1,T))),Iv=(uf-ii)^N,Jv=(uf+ii)^N,Cv=uf^N,Xv=Iv+Jv,Yv=ii*(Iv-Jv),ME=matrix(kap,kap,i,j,evalpoint(Mat[i,j],uf,Cv,Xv,Yv)),rk=matrank(ME));
 assert(N-fullrank==kap-rk,"independent full alternative source and bounded map agree");
 print("ALTERNATIVE d=",d," Dmod7=",D%7," N=",N," M=",M," size=",kap," bounded_rank=",rk," full_rank=",fullrank);
 write(OUT,"matrix Alt",cs,"[",kap,"][",kap,"];");for(i=1,kap,for(j=1,kap,if(Mat[i,j]!=0,write(OUT,"Alt",cs,"[",i,",",j,"]=",liftall(Mat[i,j]),";"))));
 write(OUT,"assess_alternative(Alt",cs,",",cs,",",N,",",[8,20][cs],");");
);
print("PASS both full alternative-source controls.");
}
quit;
