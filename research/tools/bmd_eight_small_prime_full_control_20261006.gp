\\ Nine actual conic source profiles; marked maps of size at most17.
\\ Independent full conic jets only for the first ordinary/exceptional degrees6,7.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
read("research/results/bmd-eight-small-prime-source-20261006/profiles.gp");
profA(D,dd,pi)={my(a=SMALL_PRIME_PROFILES[pi][2][dd%SMALL_PRIME_PROFILES[pi][1]+1][3]);[2*D+a[1],vector(#a[2],j,[[2*D+a[2][j],1]])];};
profB(D,dd,pi)={my(pp=SMALL_PRIME_PROFILES[pi][1],a=SMALL_PRIME_PROFILES[pi][2][dd%pp+1][4]);assert(#a==2,"exceptional profile present");[2*D+a[1],vector(#a[2],j,my(poly=a[2][j],v=List());for(k=0,poldegree(poly,z),my(co=polcoef(poly,k,z));if(co!=0,listput(v,[2*D-pp+k,co])));Vec(v))];};
maxdegree(S)={my(m=S[1]);for(j=1,#S[2],for(k=1,#S[2][j],m=max(m,S[2][j][k][1]+3)));m;};
{
for(pi=1,3,
 my(pp=[7,11,13][pi],d=[9,7,11][pi],modulus=ffinit(pp,4,'a),a=ffgen(modulus,'a),o=a^0,ii=ffprimroot(a)^((pp^4-1)/4));print("FIELD p=",pp," modulus=",modulus);
 my(D=16*d-41,N=8*(D+1),exception=1,A=profA(D,d,pi),B=profB(D,d,pi),powers=if(exception,[[5,0],[2,0],[0,3],[3,3]],[[3,0],[2,0],[0,3],[1,3]]),spaces=if(exception,[A,B,B,A],[A,A,A,A]),M=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(spaces[j]))),kap=2*M+1-N,success=0);
 assert(kap>0 && kap<=21,"bounded marked size");
 for(ch=1,4,assert(spaces[ch][1]+1+#spaces[ch][2]==2*D+2,"source dimension"));
 print("CASE d=",d," p=",pp," D=",D," N=",N," M=",M," conditions=",kap," exception=",exception);
 for(trial=1,2,
  my(u=a+(trial-1)*o,rs=u/(u^2+1),ss=u/(u^2-1),aa=rs^2,bb=ss^2,S=u^2+u^-2,rows=List());
  assert(u!=0 && u^4!=1,"admissible mark");
  for(ch=1,4,
   my(al=powers[ch][1],be=powers[ch][2],pa=(-1)^(al+be),re=(-1)^be);
   for(which=1,2,
    my(ex=if(which==1,al,be),node=if(which==1,ii,o));
    for(h=0,ex\2-1,
     my(order=ex%2+2*h,zz=node+x+O(x^(order+1)),trans=[zz,-zz,1/zz,-1/zz],signs=[1,pa,re,pa*re],vals=vector(4,k,trans[k]^(-M)*(trans[k]-u)^N),rr=vector(kap));
     for(j=0,kap-1,rr[j+1]=polcoef(sum(k=1,4,signs[k]*vals[k])/4,order,x);for(k=1,4,vals[k]*=trans[k]));
     listput(rows,rr);
    );
   );
   my(Space=spaces[ch],main=al+be+2*Space[1],hi=M-(M-al-be)%2,wid=(hi-main)/2,levels=vector(wid,j,hi-2*(j-1)),Out=matrix(wid,#Space[2]),Rel);
   for(j=1,#Space[2],
    for(k=1,#Space[2][j],
     my(e=Space[2][j][k][1],coef=Space[2][j][k][2],lead=al+be+6+2*e,poly=coef*rs^(al+2)*ss^(be+4)*(-aa)^e*(1+h)^(al+2)*(1-h)^(be+4)*(1-S*h+h^2+O(h^16))^e);
     for(i=1,wid,my(idx=(lead-levels[i])/2);if(idx>=0,assert(idx<16,"high cut coefficient precision");Out[i,j]+=polcoef(poly,idx,h)));
    );
   );
   if(#Space[2],assert(matrank(Out)==#Space[2],"outlier high vectors independent");Rel=matker(Out~)~,Rel=matid(wid));
   my(H=matrix(wid,kap,i,j,my(r=M-levels[i],kh=r-(kap-1)+(j-1),kl=r-(j-1));if(kh>=0,o*binomial(N,kh)*(-u)^kh,0*o)+re*if(kl>=0,o*binomial(N,kl)*(-u)^(N-kl),0*o)));
   if(matsize(Rel)[1], my(C=Rel*H);for(i=1,matsize(C)[1],listput(rows,Vec(C[i,]))));
  );
  assert(#rows==kap,"all finite and high cut counts");
  my(C=matrix(kap,kap,i,j,rows[i][j]),rk=matrank(C));
  print("  trial=",trial," u=",u," rank=",rk," determinant=",matdet(C));
  if(trial==1,
   my(t=o*T+O(T^N),r=sqrt(1-t),s=sqrt(1-bb/aa*t),g=(1-t)*(1-bb/aa*t)^2,source=List());
   for(ch=1,4,
    my(pre=r^powers[ch][1]*s^powers[ch][2],Space=spaces[ch]);
    for(j=0,Space[1],listput(source,pre*t^j));
    for(j=1,#Space[2],listput(source,pre*g*sum(k=1,#Space[2][j],Space[2][j][k][2]*t^Space[2][j][k][1])));
   );
   assert(#source==N,"full reference source count");
   my(fullrank=matrank(matrix(N,N,i,j,polcoef(source[i],j-1,T))));
   assert(N-fullrank==kap-rk,"independent full-jet/matching nullity comparison");
   print("  PASS full conic jet encoding: size=",N," rank=",fullrank," common_corank=",N-fullrank);
  );
  if(rk==kap,success=1;break);
 );
 print("  certified_mark=",success);
);
print("DONE: all three actual exceptional-source full-jet comparisons passed.");
}
quit;
