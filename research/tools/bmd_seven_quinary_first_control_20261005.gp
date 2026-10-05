\\ Independent first-source/profile controls for four characteristic-five profile types.
\\ Smallest actual original degrees: 8,13,16,21; each encodes a distinct full polynomial block.
default(parisizemax,3000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
check(d)={
my(p=5,c=8*d-17,N=8*c+8,cr=c%25,typ=if(cr==1,1,if(cr==11,3,if(cr==12,4,2))),M=4*c+14,DD=21,g=ffgen(p^4,'a),o=g^0);
my(u=random(g));while(u==0 || u^4==o,u=random(g));
my(alow,blow,aouts=[],bouts=[]);
if(typ==1,alow=2*c-1;blow=2*c+1;aouts=[2*c-1,2*c-2]);
if(typ==3,alow=2*c+1;blow=2*c;bouts=[2*c+3]);
if(typ==4,alow=2*c;blow=2*c-1;aouts=[2*c+1];bouts=[2*c+2,2*c+1]);
if(typ==2,alow=2*c+1;blow=2*c;bouts=[2*c+1]);
\\ Check the actual shifted polynomial source and the asserted greedy pivots.
for(block=1,2,
 my(q=2*c+if(block==1,1,3),missing=if(block==1,[1,3,5],[1,3,5,q-1]),
     exponents=concat(vector(c+1,j,2*(j-1)),vector(c-if(block==1,3,2)+1,j,7+2*(j-1))),
     Q=matrix(#missing,q+1,i,j,Mod((-1)^(j-1-missing[i])*binomial(j-1,missing[i]),p)),
     U=matrix(q+1,#exponents,i,j,Mod(binomial(exponents[j],i-1),p)),piv=List(),selected=matrix(#missing,0));
 assert(Q*U==matrix(#missing,#exponents),"shifted-source coefficient constraints");
 assert(matrank(U)==#exponents && matrank(Q)==#missing,"full shifted-source kernel");
 forstep(j=q,0,-1,
  my(candidate=matconcat([selected,Q[,j+1]]));
  if(matrank(candidate)>#piv,listput(piv,q-j);selected=candidate);
  if(#piv==#missing,break);
 );
 my(expected=if(typ==1,if(block==1,[0,1,4],[0,1,2,3]),
                if(typ==3,if(block==1,[0,1,2],[1,2,3,4]),
                if(typ==4,if(block==1,[1,2,3],[0,3,4,5]),if(block==1,[0,1,2],[0,1,3,4])))));
 assert(Vec(piv)==expected,"exceptional greedy profile");
 print("d=",d," block=",block," pivot_offsets=",Vec(piv));
);
my(groups=List([
 [2,0,2,4,blow,bouts], [1,0,3,4,alow,aouts],
 [0,3,2,7,alow,aouts], [1,3,1,7,blow,bouts]
]));
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
 my(a=(1-2*sg)*o);rr++;
 for(j=0,2*M,my(ell=j-M);Phi[rr,j+1]=ell*a^(ell-1));
);
rr++;for(j=0,2*M,Phi[rr,j+1]=ii^(j-M)+(-ii)^(j-M));
my(C=u^N,X=(u-ii)^N+(u+ii)^N,Y=ii*((u-ii)^N-(u+ii)^N),small=matrix(DD,DD,i,j,0*o));
for(kind=1,4,
 my(b=groups[kind],hi=M-((M-b[1]-b[2])%2),lo=b[1]+b[2]+2*b[5],nw=(hi-lo)/2,sign=if(kind<=2,1,-1));
 my(F=matrix(nw,2*M+1,i,j,0*o),Fsmall=matrix(nw,DD,i,j,0*o),piv=List());
 for(h=1,nw,
  my(r=M-hi+2*(h-1));F[h,2*M-r+1]=o;F[h,r+1]=sign*o;
  for(j=0,DD-1,
   my(k=r-(DD-1)+j);if(k>=0,Fsmall[h,j+1]=Mod(binomial(N%25,k),p)*(-u)^k);
   k=r-j;if(k>=0,Fsmall[h,j+1]+=sign*C*Mod(binomial(N%25,k),p)*(-u)^(-k));
  );
 );
 for(ei=1,#b[6],
  my(e=b[6][ei],peak=b[3]+b[4]+2*e,k=(hi-peak)/2+1);
  listput(piv,k);
  my(W=(1+t)^b[3]*(1-t)^b[4]*(1-s*t+t^2)^(e%25),R=F[k,],Rsmall=Fsmall[k,]);
  for(h=k,nw,my(cf=polcoef(W,h-k,t));F[h,]-=cf*R;Fsmall[h,]-=cf*Rsmall);
 );
 for(h=1,nw,if(!setsearch(Set(Vec(piv)),h),rr++;Phi[rr,]=F[h,];small[rr,]=Fsmall[h,]));
);
assert(rr==DD && matrank(Phi)==DD,"independent ambient cuts");
assert(matrank(S)==N && Phi*S==matrix(DD,N),"full source equals condition kernel");
my(marked=(z-u)^N,K=matrix(2*M+1,DD,i,j,polcoef(marked*z^(j-1),i-1,z)),DK=Phi*K);
rr=0;
for(sg=0,1,
 my(a=(1-2*sg)*o);rr++;
 for(j=0,DD-1,
  small[rr,j+1]=a^(j+1)*((j-M)*(a-u)+N*a);
  assert(small[rr,j+1]==(a-u)^(1-N)*DK[rr,j+1],"normalized derivative row");
 );
);
for(j=0,DD-1,small[3,j+1]=[X,Y,-X,-Y][j%4+1];assert(small[3,j+1]==-DK[3,j+1],"i-row sign"));
for(r=4,DD,for(j=1,DD,assert(small[r,j]==DK[r,j],"normalized high-window row")));
my(smallrank=matrank(small));assert(N-rank==DD-smallrank,"equal direct and marked coranks");

print("ambient_source_rank=",N," condition_rank=",DD," marked_rank=",smallrank);
print("PASS: complete source, all normalized entries, direct and marked coranks");
};
check(8);check(13);check(16);check(21);
quit;
