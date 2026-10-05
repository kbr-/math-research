\\ Does merging a5 into a3 repair the actual d5,p7 rational-boundary defect?
\\ Source derived from the eight-character table:
\\ v*A + w*A + v^2*w^2*C + v*w^3*C,
\\ A=F2+v^2*w^4*span(tau^EA), C=span(tau^EC).
\\ EA is the order set of F_c+x^7 F_(c-3), EC of F_c+x^7 F_c.
default(parisizemax,1000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
profile(c,m,p)={
 my(ee=concat(vector(c+1,j,2*(j-1)),vector(c-m+1,j,7+2*(j-1))),q=vecmax(ee),rr=setminus(Set(vector(q+1,j,j-1)),Set(ee)));
 my(P=List(),C=matrix(#rr,q+1,i,j,Mod(binomial(j-1,rr[i]),p)),old=0);
 forstep(j=q,0,-1,
  my(trial=concat(Vec(P),[j+1]),nr=matrank(matrix(#rr,#trial,i,k,C[i,trial[k]])));
  if(nr>old,listput(P,j+1);old=nr);
  if(old==#rr,break);
 );
 assert(old==#rr,"constraint rank");
 my(E=select(j->!setsearch(Set(Vec(P)),j+1),vector(q+1,i,i-1)));
 assert(#E==#ee,"profile dimension");
 my(Z=matrix(#ee,q+1,i,j,Mod(binomial(ee[i],j-1),p)),Signed=matrix(#rr,q+1,i,j,(-1)^(j-1-rr[i])*C[i,j]));
 assert(matrank(Z)==#ee && Signed*Z~==matrix(#rr,#ee),"source/cut kernel");
 return([E,vector(#P,i,P[i]-1)]);
};
{
my(d=5,p=7,c=8*d-17,m=2*c+2,N=4*m,AA=profile(c,3,p),CC=profile(c,0,p),g=ffgen(p^6,'a),o=g^0);
print("d=",d," p=",p," c=",c," A_missing=",AA[2]," C_missing=",CC[2]," C_orders=",CC[1]);
for(trial=1,2,
 my(u=random(g));while(u==0 || u^4==o,u=random(g));
 my(L=o+u^2/(u^2+1)^2*T+O(T^N),H=o+u^2/(u^2-1)^2*T+O(T^N),v=sqrt(L),w=sqrt(H));
 my(A=concat([o,T*o,T^2*o],vector(#AA[1],j,L*H^2*T^AA[1][j])),C=vector(#CC[1],j,T^CC[1][j]),R=List());
 for(j=1,m,listput(R,v*A[j]);listput(R,w*A[j]);listput(R,L*H*C[j]);listput(R,v*w^3*C[j]));
 my(rank=matrank(matrix(N,N,i,j,polcoef(R[i],j-1,T))));
 print("trial=",trial," u=",u," N=",N," rank=",rank," corank=",N-rank);

 \\ Independent complete Laurent ambient and geometric constraints.
 my(M=N/2+10,sv=u^2+u^-2,quad=z^4-sv*z^2+o,maxe=vecmax(CC[1]),powers=vector(maxe+1));
 powers[1]=o;for(e=1,maxe,powers[e+1]=powers[e]*quad);
 my(bases=List());
 for(e=0,2*c+1,listput(bases,[1,0,e]);listput(bases,[0,1,e]));
 
 for(j=1,#CC[1],listput(bases,[2,2,CC[1][j]]);listput(bases,[1,3,CC[1][j]]));
 my(polys=vector(#bases,j,z^(M-bases[j][1]-bases[j][2]-2*bases[j][3])
                  *(z^2+o)^bases[j][1]*(z^2-o)^bases[j][2]*powers[bases[j][3]+1]));
 my(S=matrix(2*M+1,N,i,j,polcoef(polys[j],i-1,z)),Phi=matrix(21,2*M+1,i,j,0*o),ii=sqrt(-o),row=3);
 for(j=0,2*M,
  Phi[1,j+1]=o+(-o)^(j-M);Phi[2,j+1]=(j-M)*Phi[1,j+1];
  Phi[3,j+1]=ii^(j-M)+(-ii)^(j-M);
 );
 my(groups=[[2,2,92,106,49,51,1],[1,0,95,105,1,0,1],
            [0,1,95,105,1,0,-1],[1,3,92,106,49,51,-1]]);
 for(ki=1,4,
  my(gr=groups[ki],ar=gr[1],br=gr[2],lo=gr[3],hi=gr[4],nw=(hi-lo)\2,piv=List());
  my(F=matrix(nw,2*M+1,i,j,if(j-1==M+hi-2*(i-1),o,0*o)
                             +gr[7]*if(j-1==M-hi+2*(i-1),o,0*o)));
  forstep(e=gr[6],gr[5],-1,
   my(pk=(hi-ar-br-2*e)\2+1,amp=vector(2*M+1,j,F[pk,j]));
   listput(piv,pk);
   my(Pout=z^(M-ar-br-2*e)*(z^2+o)^ar*(z^2-o)^br*powers[e+1]);
   for(hh=pk,nw,
    my(co=polcoef(Pout,M+hi-2*(hh-1),z));
    for(j=1,2*M+1,F[hh,j]-=co*amp[j]);
   );
  );
  for(hh=1,nw,if(!setsearch(Set(Vec(piv)),hh),row++;for(j=1,2*M+1,Phi[row,j]=F[hh,j])));
 );
 assert(row==21 && matrank(Phi)==21,"twenty-one independent ambient conditions");
 assert(matrank(S)==N && Phi*S==matrix(21,N),"actual Laurent source equals condition kernel");
 my(marked=(z-u)^N,K=matrix(2*M+1,21,i,j,polcoef(marked*z^(j-1),i-1,z)));
 
 my(DK=Phi*K,U=(u-o)^N+(u+o)^N,V=(u-o)^N-(u+o)^N,X=(u-ii)^N+(u+ii)^N,Y=ii*((u-ii)^N-(u+ii)^N));
 for(j=0,20,
  my(Rj=if(j%2==0,U,V),Sj=if(j%2==0,V,U));
  assert(DK[1,j+1]==Rj,"finite value row");
  assert((1-u^2)*DK[2,j+1]==((j-1)*(1-u^2)+3)*Rj+3*u*Sj,"finite derivative row");
  assert(-DK[3,j+1]==[X,Y,-X,-Y][j%4+1],"finite i row");
 );
 my(smallrank=matrank(DK));
 assert(21-smallrank==N-rank,"direct Hasse vs twenty-one-condition coranks");
 print("ambient_source_rank=",N," phi_rank=21 marked_rank=",smallrank," independent geometric encoding PASS");
 if(rank==N,break);
);
print("DONE: alternative full-profile conic test; no all-degree inference.");
}
quit;
