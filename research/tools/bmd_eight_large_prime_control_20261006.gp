\\ Nine actual conic source profiles; marked maps of size at most17.
\\ Independent full conic jets only for the first ordinary/exceptional degrees6,7.
default(parisizemax,3000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
profA(D,pp)={
 my(q=2*D+1,rr=[1,3,5],C=matrix(3,6,i,j,Mod(binomial(q-j+1,rr[i]),pp)),PV=List(),rk=0);
 for(j=1,6,my(ix=concat(Vec(PV),[j]),A=matrix(3,#ix,i,k,C[i,ix[k]]),nr=matrank(A));if(nr>rk,listput(PV,j);rk=nr);if(rk==3,break));
 assert(rk==3,"actual six-column profile");my(off=Vec(PV)-vector(3,j,1),wide=vecmax(off),out=List());
 for(j=0,wide-1,if(!setsearch(Set(off),j),listput(out,[[q-j,1]])));
 [q-wide+2,Vec(out)];
};
maxdegree(S)={my(m=S[1]);for(j=1,#S[2],for(k=1,#S[2][j],m=max(m,S[2][j][k][1]+3)));m;};
{
for(cc=1,2,
 my(pp=[101,13][cc],d=[6,7][cc],ex=[2,4][cc],modulus=ffinit(pp,ex,'a),a=ffgen(modulus,'a),o=a^0,ii=ffprimroot(a)^((pp^ex-1)/4));
 print("FIELD p=",pp," modulus=",modulus);
 my(D=16*d-41,N=8*(D+1),exception=0,A=profA(D,pp),B=A,powers=if(exception,[[5,0],[2,0],[0,3],[3,3]],[[3,0],[2,0],[0,3],[1,3]]),spaces=if(exception,[A,B,B,A],[A,A,A,A]),M=vecmax(vector(4,j,powers[j][1]+powers[j][2]+2*maxdegree(spaces[j]))),kap=2*M+1-N,success=0);
 assert(kap>0 && kap<=17 && Mod(D-5,pp)!=0,"ordinary bounded marked size");
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
  if(d<=7 && trial==1,
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
print("DONE: independent ordinary dense and nonconsecutive source controls passed.");
}
quit;
