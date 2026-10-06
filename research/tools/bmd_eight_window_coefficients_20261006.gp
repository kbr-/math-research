\\ Shared exact coefficient engine for all nine minimal first-survivor profiles.
\\ Pilot classes6 (proved normalization control),11,26. No original large jets.
default(parisizemax,3000000000);
default(nbthreads,1);
if(default(nbthreads)!=1,error("threads"));
P=192;OUT=getenv("OUT");if(OUT==0 || OUT=="",error("OUT required"));
CASES=[6,11,26];if(getenv("CASES")!=0 && getenv("CASES")!="",CASES=eval(getenv("CASES")));
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
 [H,Pure,S[5],S[6],Rmax,#HR-rank];
};
{
my(CUTS=vector(9,j,cuts(j-1)),den=(Mod(1,3)+t+O(t^P))^-1*(Mod(1,3)-t+O(t^P))^-4,D=vector(P,k,lift(polcoef(den,k-1,t))),uu=Mod(u,u^P),o=Mod(1,3));
for(res=0,8,emit(Str("CUT profile=",res," K=",CUTS[res+1][3]," codimension=",CUTS[res+1][4]," R=",CUTS[res+1][5]," pure_low=",CUTS[res+1][6]," high=",CUTS[res+1][1]," low=",CUTS[res+1][2])));
for(cas=1,#CASES,
 my(ec=CASES[cas],R=lift(Mod(3,128)^ec));
 assert(R>64,"supported class");
 my(delta=R-64,gap=(63-delta)/2,dr=((320-delta)*23)%27,cu=(8*dr-17)%9,cl=(cu+1)%9,U=CUTS[cu+1],V=CUTS[cl+1],ku=U[4],kl=V[4],Ru=U[5],Rl=V[5],m0=26+U[3]-V[3],bb=kl-gap,nfree=max(bb,0),extra=max(-bb,0),nq=gap+ku,dim=nq+nfree);
 my(n=if(ec%2,1093,364),alpha=n+1,kk=delta+1,L=n-delta,Mu=4*(cu%3)+U[3],Ml=4*(cl%3)+V[3],Rmax=P-1,Vmax=P-m0,Rall=Rmax+Vmax,K=matrix(Rall+1,Vmax+m0+1),Low=matrix(Vmax+m0+1,Rl+1));
 emit(Str("CASE exponent_class=",ec," precision=",P," reduced_dimension=",dim," gap=",gap," profiles=",cu,",",cl," m0=",m0," global_power=",U[6]+V[6]," pole_bound=",max(max(0,Ru-kk),Rl+1)));
 for(r=0,Rall,K[r+1,m0+1]=(b3(n,kk+r)*lift(Mod(2,3)^(kk+r)))%3);
 for(v=1,Vmax,for(r=0,Rall-v,K[r+1,v+m0+1]=(K[r+1,v+m0]+K[r+2,v+m0])%3));
 for(m=1,m0,for(r=0,Rmax,
  my(t=n-kk-r,val=0);
  for(a=1,m,val+=(-1)^t*b3(n,m-a)*b3(t+a-1,a-1));
  for(b=0,kk+r-m,val+=b3(n,b)*b3(n-b-m,kk+r-b-m));
  K[r+1,m0+1-m]=val%3;
 ));
 for(k=0,Rl,
  my(val=b3(n,k+m0));
  for(r=-(kk-m0),-1,
   my(t=n-kk-r,poly=0);
   for(b=0,kk+r-m0,poly+=b3(n,b)*b3(n-b-m0,kk+r-b-m0));
   val-=poly*b3(t,k)*(-1)^(t-k);
  );
  for(a=1,m0,val+=b3(n,m0-a)*(-1)^k*b3(a+k-1,k)*b3(a+L-1,a+k));
  Low[1,k+1]=val%3;
 );
 for(v=-m0,Vmax-1,for(k=0,Rl,Low[v+m0+2,k+1]=(if(k,Low[v+m0+1,k],0)-K[1,v+m0+1]*b3(L,k)*(-1)^(L-k))%3));
 for(v=-m0,Vmax,
  my(Z=Mod(1,3)+t+O(t^L),H=Z^v*(Z+1)^n,Taylor=subst(Pol(H,t),t,z-1));
  for(r=0,Rmax,assert(lift(polcoef(H,L-1-r,t))%3==K[r+1,v+m0+1],"high coefficient recurrence"));
  for(k=0,Rl,assert(lift(polcoef(Taylor,k,z))%3==Low[v+m0+1,k+1],"low coefficient recurrence"));
 );
 emit(Str("PASS full coefficient controls for ",Vmax+m0+1," exponent values"));
 my(F=matrix(dim,dim,i,j,0*o*uu),Eval=vector(P,r,vector(3)));
 for(r=0,P-1,
  my(e=L-1-r);
  Eval[r+1][1]=Mod(powat(1,e-1,P)*((e-Ml)+Ml*u),u^P);
  Eval[r+1][2]=Mod(powat(-1,e-1,P)*(-(e-Ml)+Ml*u),u^P);
  Eval[r+1][3]=Mod(Polrev(vector(P,k,Mod(b3(e,k-1)*(-1)^(k-1)*ps(e-Ml-k+1),3)),u),u^P);
 );
 for(j=0,nq-1,
  my(TA=matrix(P,P),LO=matrix(Rl+1,P));
  for(a=0,(P-1-j)\4,for(b=0,(P-1-j-4*a)\2,
   my(k=j+4*a+2*b,v=j-m0+2*a+2*b,co=((-1)^a*b3(n,a)*D[b+1])%3);
   if(co==0,next);
   for(r=0,P-1-k,TA[r+1,k+1]=(TA[r+1,k+1]+co*K[r+1,v+m0+1])%3);
   \\ High pole coefficient rows can need tau_r without its u^r weight.
   for(r=P-k,min(P-1,Rl+extra),TA[r+1,k+1]=(TA[r+1,k+1]+co*K[r+1,v+m0+1])%3);
   for(r=0,Rl,LO[r+1,k+1]=(LO[r+1,k+1]+co*Low[v+m0+1,r+1])%3);
  ));
  my(TP=vector(P,r,Mod(Polrev(vector(P,k,Mod(TA[r,k],3)),u),u^P)),LP=vector(Rl+1,r,Mod(Polrev(vector(P,k,Mod(LO[r,k],3)),u),u^P)));
  my(uf=[o*((j+alpha-Mu)+(Mu-j)*uu),o*(-1)^j*(-(j+alpha-Mu)+(Mu-j)*uu),Mod(Polrev(vector(P,k,Mod(b3(alpha,k-1)*(-1)^(k-1)*ps(alpha+j-Mu-k+1),3)),u),u^P)]);
  my(hh=vector(Ru+1,r,my(k=r-1-(nq-1)+j);if(k>=0,o*b3(alpha,k)*(-uu)^k,0*o*uu)));
  my(ll=vector(Ru+1,r,if(j<=r-1,o*b3(alpha,r-1-j)*(-1)^(alpha-r+1+j)*uu^(Ru-r+1+j),0*o*uu)));
  my(lf=vector(3,k,sum(r=0,P-1,uu^r*TP[r+1]*Eval[r+1][k])));
  my(lh=vector(Rl+1,r,my(t=r-1-bb);if(t>=0,uu^t*sum(a=0,t,o*(-1)^(t-a)*b3(L-1-a,t-a)*TP[a+1]),0*o*uu)));
  my(llow=vector(Rl+1,r,uu^(Rl-r+1)*LP[r]));
  my(ex=vector(extra,k,uu^(k-1)*sum(a=0,k-1,o*(-1)^(k-1-a)*b3(L-1-a,k-1-a)*TP[a+1])));
  my(col=concat([uf,mv(U[1],hh),mv(U[2],ll),lf,mv(V[1],lh),mv(V[2],llow),ex]));
  assert(#col==dim,"column dimension");F[,j+1]=col~;
 );
 for(h=0,nfree-1,
  my(lf=[Mod(powat(1,L-1,P)*((L+h-Ml)+(Ml-h)*u),u^P),Mod((-1)^h*powat(-1,L-1,P)*(-(L+h-Ml)+(Ml-h)*u),u^P),Mod(Polrev(vector(P,k,Mod(b3(L,k-1)*(-1)^(k-1)*ps(L+h-Ml-k+1),3)),u),u^P)]);
  my(lh=vector(Rl+1,r,my(t=1-bb+r-1+h);if(t>=0,o*b3(L,t)*(-uu)^t,0*o*uu)));
  my(ll=vector(Rl+1,r,if(r-1>=h,o*b3(L,r-1-h)*(-1)^(L-r+1+h)*uu^(Rl+1+h-r+1),0*o*uu)));
  my(col=concat([vector(ku,k,0*o*uu),lf,mv(V[1],lh),mv(V[2],ll),vector(extra,k,0*o*uu)]));
  assert(#col==dim,"free column dimension");F[,nq+h+1]=col~;
 );
 emit(Str("matrix=",F));
 emit(Str("entry_valuations=",matrix(dim,dim,i,j,min(P,valuation(lift(F[i,j]),u)))));
 my(DD=matdet(matrix(dim,dim,i,j,lift(F[i,j])+O(u^P))));
 emit(Str("determinant_series=",DD));
 if(DD==0,emit("UNRESOLVED"),emit(Str("leading_order=",valuation(DD,u)," leading_coefficient=",polcoef(DD,valuation(DD,u),u))));
 if(ec==6,assert(DD!=0 && valuation(DD,u)==480,"previous class6 normalization control"));
);
}
quit;
