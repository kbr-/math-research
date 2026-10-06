\\ Independent memberships: raw high/low cuts from the shared profile construction.
\\ Shared exact coefficient engine for all nine minimal first-survivor profiles.
\\ Pilot classes6 (proved normalization control),11,26. No original large jets.
default(parisizemax,3000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));


assert(c,s)={if(!c,error(s));};
emit(s)={print(s);write(OUT,s);};
b3(n,k)={if(k<0,0,lift(Mod(binomial(n,k),3)));};
mv(A,v)={if(#A==0,[],Vec(A*v~));};
ps(e)={if(e%2,0,if(e%4,1,2));};
powat(z,e,N)={Polrev(vector(N,k,Mod(b3(e,k-1)*(-1)^(k-1)*z^(e-k+1),3)),u);};
SHAPES=[[0,[0],0,[0],9,11],[-1,[-2,-1],1,[],7,7],[1,[],1,[],6,5],[1,[],0,[3],14,21],[0,[1],-1,[1,2],12,17],[-1,[-1,0],-2,[-1,0,1],10,13],[-2,[-3,-2,-1],-3,[-3,-2,-1,0],8,9],[1,[],1,[],6,5],[1,[],1,[],6,5]];
cuts(res)={
 my(c=54+res,S=SHAPES[res+1],M=4*c+S[5],Rmax=0,HR=List(),LR=List());
 my(main=[[2,0],[1,0],[0,3],[1,3]],out=[[2,4],[3,4],[2,7],[1,7]],signs=[1,1,-1,-1]);
 for(ch=1,4,
  my(isA=(ch==2 || ch==3),bound=2*c+if(isA,S[1],S[3]),es=if(isA,S[2],S[4]),par=(main[ch][1]+main[ch][2])%2,hi=M-(M-par)%2,lo=main[ch][1]+main[ch][2]+2*bound,w=(hi-lo)/2);
  if(w==0,assert(#es==0,"outlier without high window");next);
  my(levels=vector(w,i,hi-2*(i-1)),O=matrix(w,#es),Rel);
  Rmax=max(Rmax,M-levels[w]);
  if(#es,
   my(base=2*c+es[1]);assert(base%9==0 && es==vector(#es,j,es[1]+j-1),"consecutive Frobenius outliers");
   for(j=0,#es-1,
    my(poly=Mod(1,3)*(1+t)^out[ch][1]*(1-t)^out[ch][2]*(1+t^2)^j,lead=out[ch][1]+out[ch][2]+2*(base+j));
    for(i=1,w,my(k=(lead-levels[i])/2);if(k>=0,assert(k<9,"tail index must be below9");O[i,j+1]=polcoef(poly,k,t)));
   );
   assert(matrank(O)==#es,"outlier span");
   Rel=matker(O~)~;
  ,Rel=Mod(matid(w),3));
  for(i=1,matsize(Rel)[1],
   my(h=vector(33,j,Mod(0,3)),l=h);
   for(j=1,w,h[M-levels[j]+1]=Rel[i,j];l[M-levels[j]+1]=signs[ch]*Rel[i,j]);
   listput(HR,h);listput(LR,l);
  );
 );
 assert(#HR==S[6]-3,"all high cuts");
 my(CH=matrix(#HR,Rmax+1,i,j,HR[i][j]),CL=matrix(#LR,Rmax+1,i,j,LR[i][j]),rank=matrank(CH),left=matker(CH~)~,sel=matindexrank(CH)[1]);
 assert(#sel==rank,"independent high rows");
 my(H=matrix(rank,Rmax+1,i,j,CH[sel[i],j]),Pure=if(rank==#HR,[],left*CL));
 my(T=matrix(#HR,#HR,i,j,if(i<=rank,if(j==sel[i],Mod(1,3),Mod(0,3)),left[i-rank,j])));
 assert(matdet(T)!=0,"invertible exact high/low split");
 [CH,CL,S[5],S[6],Rmax,#HR-rank];
};

fullcut(P,M,C,ii)={
 my(R=C[5],H=vector(R+1,j,polcoef(P,2*M-j+1,z)),Lo=vector(R+1,j,polcoef(P,j-1,z)),D=deriv(P,z));
 concat([subst(D,z,1)-M*subst(P,z,1),-subst(D,z,-1)-M*subst(P,z,-1),ii^(-M)*subst(P,z,ii)+(-ii)^(-M)*subst(P,z,-ii)],Vec(C[1]*H~+C[2]*Lo~));
};
{
my(modulus=ffinit(3,4,'a),a=ffgen(modulus,'a),o=a^0,u=a,ii=ffprimroot(a)^((3^4-1)/4),S=u^2+u^-2,T=o*z^4-S*z^2+o);
assert(u^4!=1 && ii^2==-o,"admissible conic");
print("FIELD=",modulus," u=",u);
for(res=0,8,
 my(c=54+res,C=cuts(res),Sh=SHAPES[res+1],M=4*c+Sh[5],dim=8*c+8,count=0);
 for(ch=1,4,
  my(A=[2,1,0,1][ch],B=[0,0,3,3][ch],isA=(ch==2||ch==3),bound=2*c+if(isA,Sh[1],Sh[3]),es=if(isA,Sh[2],Sh[4]),base=o*(z^2+1)^A*(z^2-1)^B,power=o);
  for(j=0,bound,
   my(P=z^(M-A-B-2*j)*base*power);
   assert(fullcut(P,M,C,ii)==vector(Sh[6],k,0*o),"main source membership");count++;power*=T;
  );
  if(#es,
   A+=if(isA,2,0);B+=4;base=o*(z^2+1)^A*(z^2-1)^B;power=T^(2*c+es[1]);
   for(j=1,#es,
    my(P=z^(M-A-B-2*(2*c+es[j]))*base*power);
    assert(fullcut(P,M,C,ii)==vector(Sh[6],k,0*o),"outlier membership");count++;power*=T;
   );
  );
 );
 my(CM=matrix(Sh[6],2*M+1,i,j,fullcut(o*z^(j-1),M,C,ii)[i]));
 assert(count==dim && matrank(CM)==2*M+1-dim,"dimension and independent full cuts");
 print("PASS profile=",res," c=",c," sections=",count," ambient=",2*M+1," cut_rank=",matrank(CM)," pure_low=",C[6]);
);
print("PASS all nine exact profile membership and codimension controls");
}
quit;
