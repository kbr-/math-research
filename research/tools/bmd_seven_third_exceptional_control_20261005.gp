\\ Independent exceptional-source and normalized marked-matrix checks, GF(3^6).
\\ d6 is the smallest type1 source; d10 is the smallest type0 newly normal family.
\\ Stages: actual block basis; direct Hasse rank; ambient cuts; every small entry.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
check(d)={
my(p=3,c=8*d-17,N=8*c+8,typ=c%3,M=4*c+if(typ==0,14,12),DD=2*M-N+1,g=ffgen(p^6,'a),o=g^0);
my(u=random(g));while(u==0 || u^4==o,u=random(g));
my(groups=List());
for(kind=0,3,
 my(al=[2,1,0,1][kind+1],be=[0,0,7,7][kind+1],oa=al,ob=be,low,outs=[]);
 if(typ==0,
  low=2*c+1;if(kind==0 || kind==3,low=2*c;outs=[2*c+3]),
  low=2*c;if(kind==0 || kind==3,low=2*c-1;outs=[2*c+2,2*c+1],oa=al+2;outs=[2*c+1])
 );
 listput(groups,[al,be,oa,ob,low,outs]);
);
my(bases=List());
for(kind=1,4,
 my(b=groups[kind]);
 for(e=0,b[5],listput(bases,[b[1],b[2],e]));
 for(k=1,#b[6],listput(bases,[b[3],b[4],b[6][k]]));
);
assert(#bases==N,"source dimension count");
my(maxe=vecmax(vector(N,j,bases[j][3])),L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N));
my(v=sqrt(L),w=sqrt(H),rows=vector(N,j,v^bases[j][1]*w^bases[j][2]*T^bases[j][3]));
my(rank=matrank(matrix(N,N,i,j,polcoef(rows[i],j-1,T))));
print("d=",d," p=",p," c=",c," u=",u," N=",N," direct_rank=",rank);
my(s=u^2+u^-2,quad=z^4-s*z^2+o,powers=vector(maxe+1));
powers[1]=o;for(e=1,maxe,powers[e+1]=powers[e]*quad);
my(polys=vector(N,j,z^(M-bases[j][1]-bases[j][2]-2*bases[j][3])
 *(z^2+o)^bases[j][1]*(z^2-o)^bases[j][2]*powers[bases[j][3]+1]));
my(S=matrix(2*M+1,N,i,j,polcoef(polys[j],i-1,z)),Phi=matrix(DD,2*M+1,i,j,0*o),ii=sqrt(-o),rr=0);
for(sg=0,1,
 my(a=(1-2*sg)*o);
 forstep(hh=1,5,2,
  rr++;for(j=0,2*M,my(ell=j-M);Phi[rr,j+1]=(binomial(ell,hh)-binomial(-ell,hh))*a^(ell-hh));
 );
);
rr++;for(j=0,2*M,Phi[rr,j+1]=ii^(j-M)+(-ii)^(j-M));
my(C=u^N,X=(u-ii)^N+(u+ii)^N,Y=ii*((u-ii)^N-(u+ii)^N),small=matrix(DD,DD,i,j,0*o));
for(kind=1,4,
 my(b=groups[kind],hi=M-((M-b[1]-b[2])%2),lo=b[1]+b[2]+2*b[5],nw=(hi-lo)/2,sign=if(kind<=2,1,-1));
 my(F=matrix(nw,2*M+1,i,j,0*o),Fsmall=matrix(nw,DD,i,j,0*o),piv=List());
 for(h=1,nw,
  my(r=M-hi+2*(h-1));F[h,2*M-r+1]=o;F[h,r+1]=sign*o;
  for(j=0,DD-1,
   my(k=r-(DD-1)+j);if(k>=0,Fsmall[h,j+1]=Mod(binomial(N%27,k),p)*(-u)^k);
   k=r-j;if(k>=0,Fsmall[h,j+1]+=sign*C*Mod(binomial(N%27,k),p)*(-u)^(-k));
  );
 );
 for(ei=1,#b[6],
  my(e=b[6][ei],peak=b[3]+b[4]+2*e,k=(hi-peak)/2+1);
  listput(piv,k);
  my(W=(1+t)^b[3]*(1-t)^b[4]*(1-s*t+t^2)^(e%9),R=F[k,],Rsmall=Fsmall[k,]);
  for(h=k,nw,my(cf=polcoef(W,h-k,t));F[h,]-=cf*R;Fsmall[h,]-=cf*Rsmall);
 );
 for(h=1,nw,if(!setsearch(Set(Vec(piv)),h),rr++;Phi[rr,]=F[h,];small[rr,]=Fsmall[h,]));
);
assert(rr==DD && matrank(Phi)==DD,"independent ambient cuts");
assert(matrank(S)==N && Phi*S==matrix(DD,N),"full source equals condition kernel");
my(marked=(z-u)^N,K=matrix(2*M+1,DD,i,j,polcoef(marked*z^(j-1),i-1,z)),DK=Phi*K);
rr=0;
for(sg=0,1,
 my(a=(1-2*sg)*o);
 forstep(hh=1,5,2,
  rr++;
  for(j=0,DD-1,
   my(val=0*o);
   for(k=0,hh,val+=Mod(binomial(N%27,k),p)*(a-u)^(hh-k)
    *(a^k*Mod(binomial((j-M)%27,hh-k),p)-(-u)^k*Mod(binomial((M-j-N)%27,hh-k),p)));
   small[rr,j+1]=a^(j+hh)*val;
   assert(small[rr,j+1]==(a-u)^(hh-N)*DK[rr,j+1],"normalized odd-part Hasse row");
  );
 );
);
for(j=0,DD-1,small[7,j+1]=[X,Y,-X,-Y][j%4+1];assert(small[7,j+1]==(-1)^(M/2)*DK[7,j+1],"i-row sign"));
for(r=8,DD,for(j=1,DD,assert(small[r,j]==DK[r,j],"normalized high-window row")));
my(smallrank=matrank(small));assert(N-rank==DD-smallrank,"equal direct and marked coranks");
if(d==6,assert(smallrank<DD,"type1 obstruction control"));
if(d==10,
 my(scalar=(-u^16+u^14-u^12-u^10+u^8-u^6-u^4+u^2-1)/u^6,
 predicted=scalar*(C+u^8)*((-u^2)*C*X+u*C*Y+X+u*Y)*(u*C+1)^2*(u*C-1)^2*C^4);
 assert(smallrank==DD && rank==N,"new normality control");
 assert(matdet(small)==predicted,"symbolic determinant independent evaluation");
);
print("ambient_source_rank=",N," condition_rank=",DD," marked_rank=",smallrank);
print("PASS: complete source, all normalized entries, direct and marked coranks");
};
check(6);check(10);
quit;
