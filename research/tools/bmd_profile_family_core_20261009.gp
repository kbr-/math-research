\\ Common first-root source encoder for the thirteen elliptic profiles.
\\ r=2j+delta, A=F_(L+j-1+delta)+G_3*T^L*F_j, p|L.
\\ The first frame has lower binomial indices <=15 and unit top block for p>47.
FAMILY_FRAMES=Map();
family_check(c,s)=if(!c,error(s));
family_coef(e,v)=if(e<v,0,(-1)^(e-v)*binomial(e,e-v));
family_frame(jp,H,Lrep=0,fieldPrime=0)={
  my(key=Str([jp,H,Lrep,fieldPrime]));
  if(mapisdefined(FAMILY_FRAMES,key),return(mapget(FAMILY_FRAMES,key)));
  my(o=if(fieldPrime,Mod(1,fieldPrime),1),top=2*jp+12,A=matrix(3,3,i,k,o*(-1)^(2*Lrep+top+k-(2*i-1))*binomial(2*Lrep+top+k,2*i-1)),inv=A^-1,F=matrix(H,16));
  for(h=0,H-1,my(e=2*Lrep+top-h,al=-inv*vector(3,i,o*(-1)^(e-(2*i-1))*binomial(e,2*i-1))~);F[h+1,]=vector(16,k,o*family_coef(e,2*Lrep+2*jp+k-1)+sum(v=1,3,al[v]*family_coef(2*Lrep+top+v,2*Lrep+2*jp+k-1))));
  mapput(FAMILY_FRAMES,key,F);F;
};

family_first(r,H,eps,bvar,T,Lrep=0,fieldPrime=0)={
  family_check(r>=0&&r<=12&&H>=32,"profile and column window range");
  my(jp=r\2,parity=r%2,lo=jp-1+parity,coff=jp+7,amin=lo+1,width=coff-lo,q=jp+1,ncut=width-q,o=if(fieldPrime,Mod(1,fieldPrime),1));
  my(g=o*(1+T)*(1+bvar*T)^2,G=g*(1+eps*T)^4,Q=matrix(width,q,i,k,polcoef(G*T^(k-1),lo+i,T)),piv=vector(q,i,i),small=matrix(q,q,i,k,Q[piv[i],k]),D=matdet(small));
  if(D==0,piv=Vec(matindexrank(Q)[1]);family_check(#piv==q,"full domain rank");small=matrix(q,q,i,k,Q[piv[i],k]);D=matdet(small));
  my(adj=matadjoint(small));family_check(small*adj==D*matid(q)&&D!=0,"exact domain adjugate");
  my(free=setminus(Set(vector(width,i,i)),Set(piv)),where=vector(width));
  for(i=1,q,where[piv[i]]=i);
  my(cuts=matrix(ncut,width,i,k,if(k==free[i],D,0)-if(where[k],sum(v=1,q,Q[free[i],v]*adj[v,where[k]]),0)));
  family_check(cuts*Q==matrix(ncut,q),"every high constraint annihilates the complete domain");
  my(F=family_frame(jp,H,Lrep,fieldPrime),gc=vector(4,i,polcoef(g,i-1,T)),top=2*jp+12,R=matrix(2*ncut,H));
  for(h=0,H-1,
    my(E=vector(width,i,my(a=lo+i);eps^(a-amin)*sum(u=a,coff,F[h+1,2*(u-jp)+1]*binomial(Lrep+u,u-a))),B=vector(width,i,my(a=lo+i);sum(v=0,3,gc[v+1]*eps^(a-amin+3-v)*sum(u=a-v,coff-3,F[h+1,7+2*(u-jp)+1]*binomial(Lrep+u,u-a+v)))),fac=2^(top-h)*eps^h);
    for(i=1,ncut,R[i,h+1]=fac*sum(k=1,width,cuts[i,k]*E[k]);R[ncut+i,h+1]=fac*sum(k=1,width,cuts[i,k]*B[k]))
  );
  [r,jp,parity,lo,coff,top,R,Q,piv,cuts,max(5,2*width-1),g,q];
};

family_limit(packet,S,T)={
  my(C=S[1],nrow=matsize(C)[1],H=matsize(C)[2],tail=0,top=packet[6],g=packet[12],gdeg=poldegree(packet[12],T));
  family_check(vecmax(S[2])<H,"omitted columns remain positive after every row operation");
  for(k=1,H,if(C[,k]!=vector(nrow)~,tail=k));
  my(q=tail-nrow,lo=top+gdeg-tail);
  family_check(q>=0,"full limiting row rank");
  family_check(lo+1+q==2*(packet[4]+packet[13]+1),"full scalar dimension preserved");
  if(q==0,return([lo,lo,matrix(0,0),matrix(0,0)]));
  my(piv=Vec(S[4]),free=setminus(Set(vector(tail,i,i)),Set(piv)),inv=matrix(nrow,nrow,i,k,C[i,piv[k]])^-1,K=matrix(tail,q));
  family_check(#free==q,"complete free columns");
  for(k=1,q,my(z=-inv*C[,free[k]]);K[free[k],k]=1;for(i=1,nrow,K[piv[i],k]=z[i]));
  family_check(C[,1..tail]*K==matrix(nrow,q),"exact full high kernel");
  my(high=matrix(tail,q,i,k,my(a=lo+i);sum(v=0,gdeg,my(h=top+v-a);if(h>=0&&h<tail,polcoef(g,v,T)*K[h+1,k],0))),last=tail);
  while(last>0&&high[last,]==vector(q),last--);
  family_check(last>0&&matrank(high)==q,"independent full scalar high quotient");
  [lo,lo+last,high[1..last,],K];
};

\\ A primitive polynomial annihilator avoids carrying arbitrary high-basis denominators
\\ into the next degeneration. Its annihilation identity and full rank are checked.
family_annihilator(Q,variable,fieldPrime=0)={
  my(shape=matsize(Q),width=shape[1],q=shape[2],C=matker(Q~)~);
  family_check(matrank(Q)==q&&matsize(C)[1]==width-q,"complete high domain and annihilator");
  for(i=1,width-q,
    my(den=1);
    for(j=1,width,den=lcm(den,denominator(C[i,j])));
    C[i,]*=den;
    my(common=content(C[i,]));family_check(common!=0,"nonzero domain constraint");C[i,]/=common;
    if(!fieldPrime,
      my(scale=1);for(j=1,width,my(v=Vec(C[i,j]));for(k=1,#v,scale=lcm(scale,denominator(v[k]))));C[i,]*=scale
    );
    for(j=1,width,family_check(poldegree(denominator(C[i,j]),variable)==0,"polynomial high constraint"))
  );
  family_check(C*Q==matrix(width-q,q),"primitive constraints retain the exact high span");C;
};

family_second(r,lo,coff,Q,H,eps,bvar,T,Lrep=0,fieldPrime=0)={
  my(width=coff-lo,q=matsize(Q)[2],ncut=width-q,amin=lo+1,top=2*coff,o=if(fieldPrime,Mod(1,fieldPrime),1));
  family_check(q>0&&ncut>0,"use the complete-polynomial lemma when no high constraint remains");
  my(bound=max(1,2*width-1));
  if(fieldPrime,family_check(fieldPrime>bound,"higher prime-power binomial carry must be retained");family_check(Mod(2*Lrep+top+1,fieldPrime)!=0,"ordinary ambient pivot must be replaced in this characteristic"));
  my(C=family_annihilator(Q,bvar,fieldPrime),cuts=matrix(ncut,width,i,j,subst(C[i,j],bvar,eps)),R=matrix(2*ncut,H));
  for(h=0,H-1,
    my(e=2*Lrep+top-h,al=o*(-1)^e*e/(o*(2*Lrep+top+1)),F=vector(2*width,k,o*family_coef(e,2*Lrep+2*amin+k-1)+al*family_coef(2*Lrep+top+1,2*Lrep+2*amin+k-1)));
    my(E=vector(width,i,my(a=lo+i);eps^(a-amin)*sum(u=a,coff,F[2*(u-amin)+1]*binomial(Lrep+u,u-a))),B=vector(width,i,my(a=lo+i);eps^(a-amin+1)*sum(u=a,coff-1,F[3+2*(u-amin)+1]*binomial(Lrep+u,u-a))+eps^(a-amin)*sum(u=a-1,coff-1,F[3+2*(u-amin)+1]*binomial(Lrep+u,u-a+1))),fac=2^(top-h)*eps^h);
    for(i=1,ncut,R[i,h+1]=fac*sum(k=1,width,cuts[i,k]*E[k]);R[ncut+i,h+1]=fac*sum(k=1,width,cuts[i,k]*B[k]))
  );
  [r,r\2,r%2,lo,coff,top,R,Q,[],cuts,bound,o*(1+T),q];
};

\\ Final one-root source: low F_(L+lo) plus T^L times high vectors, p|L.
\\ Eliminate the complete low polynomial block in w, T=w^2-1; retain all 2q jets.
family_endpoint(limit,fieldPrime=0)={
  my(lo=limit[1],coff=limit[2],Q=limit[3],q=matsize(Q)[2],width=coff-lo,o=if(fieldPrime,Mod(1,fieldPrime),1));
  if(q==0,return([matrix(0,0),o,0]));
  my(bound=max(0,2*width-1));
  if(fieldPrime,family_check(fieldPrime>bound,"endpoint needs higher prime-power degree data"));
  my(M=matrix(2*q,2*q,i,j,
    my(z=2*lo+1+i,k=(j+1)\2,bit=(j-1)%2);
    sum(a=lo+1,coff,Q[a-lo,k]*sum(v=0,bit,my(lower=2*a-z+v);if(lower<0,0,o*binomial(bit,v)*binomial(a,lower)*2^lower)))
  ));
  [M,matdet(M),bound];
};
