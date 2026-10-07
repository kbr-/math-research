\\ Exhaustive source and marked-entry controls for prime-power Frobenius splitting.
\\ Stages: q split versus iterated p split; reconstruction; branch constraint
\\ kernel equality; Lucas tensor entries. Small encoding controls, not new ranges.
default(parisizemax,2000000000);
default(nbthreads,1);
setrand(20261007);
assert(c,s)={if(!c,error(s));};
inds(n,d)={my(V=List());for(S=0,2^n-1,for(j=0,max(-1,(d-hammingweight(S))\2),if(2*j+hammingweight(S)<=d,listput(V,[S,j]))));Vec(V);};
extract(poly,q,iv,r)={if(poly==0,return(0));sum(j=0,max(-1,(poldegree(poly,T)-r)\q),if(q*j+r<=poldegree(poly,T),polcoef(poly,q*j+r,T)^iv*T^j,0))};
{
my(cases=[[3,3,2,7],[3,3,3,8],[3,5,2,4],[6,3,1,1]],checks=0,tensorchecks=0);
for(cas=1,#cases,
 my(n=cases[cas][1],p=cases[cas][2],depth=cases[cas][3],q=p^depth,d=cases[cas][4],ext=4,modulus=ffinit(p,ext,'a),a=ffgen(modulus,'a),o=a^0,aa=vector(n,i,random(a)));
 while(#Set(aa)!=n||prod(i=1,n,aa[i])==0,aa=vector(n,i,random(a)));
 print("CASE n=",n," p=",p," q=",q," d=",d," modulus=",modulus," slopes=",aa);
 my(I=inds(n,d),N=#I,ed=vector(q,r,(d+(q-1)*n-2*(r-1))\q),J=vector(q,r,inds(n,ed[r])),sizes=apply(length,J),total=vecsum(sizes),L=vector(q,r,max(0,(N-r+1+q-1)\q)),ivq=p^(ext-(depth%ext)),ivp=p^(ext-1));
 my(nn=max(N,vecmax(L)),ww=vector(n,i,sqrt(o+aa[i]*T+O(T^nn))),ch=vector(2^n,S,prod(i=1,n,if(bittest(S-1,i-1),ww[i],o))),R=prod(i=1,n,o+aa[i]*T)^((q-1)/2));
 for(i=1,n,assert(valuation(ww[i]^2-(o+aa[i]*T),T)>=nn,"root-square identity"));
 my(D=matrix(N,total,i,j,0*o),block=matrix(total,N,i,j,0*o),offset=0,jetoff=0,pos=Map(),cols=List());
 for(r=0,q-1,
  for(k=1,sizes[r+1],mapput(pos,[r,J[r+1][k][1],J[r+1][k][2]],offset+k);listput(cols,[r,J[r+1][k][1],J[r+1][k][2]]));
  for(i=1,sizes[r+1],for(j=1,L[r+1],block[offset+i,jetoff+j]=polcoef(ch[J[r+1][i][1]+1]*T^J[r+1][i][2],j-1,T)));
  offset+=sizes[r+1];jetoff+=L[r+1]
 );
 assert(jetoff==N,"jet partition");
 for(i=1,N,
  my(S=I[i][1],P=T^I[i][2]*o,Rc=prod(k=1,n,if(bittest(S,k-1),o,o+aa[k]*T)),poly=P*Rc^((q-1)/2),iter=[P],power=1);
  for(level=1,depth,
   my(next=vector(power*p,j,0*o));
   for(r=0,power-1,for(t=0,p-1,next[r+power*t+1]=extract(iter[r+1]*Rc^((p-1)/2),p,ivp,t)));
   iter=next;power*=p
  );
  for(r=0,q-1,
   my(out=extract(poly,q,ivq,r));assert(out==iter[r+1],"iterated split differs from direct q split");checks++;
   if(out!=0,for(k=0,poldegree(out,T),my(cf=polcoef(out,k,T));if(cf!=0,D[i,mapget(pos,[r,S,k])]=cf)))
  )
 );
 my(digit=D*block,rec=matrix(N,N,i,j,0*o),off=0);
 for(r=0,q-1,for(k=0,L[r+1]-1,for(i=1,N,rec[i,q*k+r+1]=digit[i,off+k+1]^q));off+=L[r+1]);
 my(expected=matrix(N,N,i,j,polcoef(R*ch[I[i][1]+1]*T^I[i][2],j-1,T)),source=matrix(N,N,i,j,polcoef(ch[I[i][1]+1]*T^I[i][2],j-1,T)));
 assert(rec==expected,"marked reconstruction");checks+=N^2;
 my(rows=List());for(S=0,2^n-1,for(i=1,n,if(!bittest(S,i-1),for(j=0,(q-3)/2,listput(rows,[S,i,j])))));
 my(C=matrix(#rows,total,u,v,my(S=rows[u][1],i=rows[u][2],j=rows[u][3],r=cols[v][1],k=cols[v][3],z=-o/aa[i]);if(cols[v][2]!=S||r<j,0*o,o*binomial(r,j)*(z^ivq)^(r-j)*z^k)));
 assert(C*D~==matrix(#rows,N,i,j,0*o),"branch conditions reject the image");
 my(rankD=matrank(D),rankC=matrank(C),K=matker(block~),rankCK=matrank(C*K),rankSource=matrank(source));
 assert(rankD==N && rankC==total-N,"exact branch-image kernel");
 assert(matsize(K)[2]-rankCK==N-rankSource,"compatibility/direct kernel mismatch");
 if(d>=n-2,assert(total-N==(q-1)*n*2^(n-2),"bulk codimension"));
 if(n==6,assert(rankSource==6,"negative degree-one control"));
 for(i=1,n,my(z=-o/aa[i]);for(j=0,q-1,for(r=0,q-1,my(jj=j,rr=r,fac=o,pp=1);
  for(level=1,depth,fac*=o*binomial(rr%p,jj%p)*z^(pp*((rr%p)-(jj%p)));rr=rr\p;jj=jj\p;pp*=p);
  assert(fac==o*binomial(r,j)*z^(r-j),"Lucas tensor entry");tensorchecks++
 )));
 print("PASS source_dim=",N," leaf_degrees=",ed," target_dim=",total," branch_rank=",rankC," source_rank=",rankSource," kernel_dim=",N-rankSource);
);
print("ITERATED_FROBENIUS_CONTROLS_COMPLETED source_checks=",checks," tensor_entries=",tensorchecks)
}
quit;
