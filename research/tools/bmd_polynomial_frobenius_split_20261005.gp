\\ Exact source-preserving Frobenius split: every character and every marked jet.
\\ n=6,p=3,d=1 is the known nonclassical negative control; d=8 checks contraction.
\\ n=4,p=5,d=6 checks the odd-prime version against a known normal family.
default(parisizemax,2000000000);setrand(20261005);
assert(c,s)={if(!c,error(s));};
inds(n,d)={my(V=List());for(S=0,2^n-1,for(j=0,(d-hammingweight(S))\2,if(2*j+hammingweight(S)<=d,listput(V,[S,j]))));Vec(V);};
{
my(cases=[[6,3,1],[6,3,8],[4,5,6]]);
for(cas=1,#cases,
 my(n=cases[cas][1],p=cases[cas][2],d=cases[cas][3],ext=6,g=ffgen(p^ext,'a),o=g^0,aa=vector(n,i,random(g)));
 while(#Set(aa)!=n || prod(i=1,n,aa[i])==0,aa=vector(n,i,random(g)));
 my(I=inds(n,d),N=#I,ed=vector(p,r,(d+(p-1)*n-2*(r-1))\p),J=vector(p,r,inds(n,ed[r])),sizes=apply(length,J),total=sum(r=1,p,sizes[r]),L=vector(p,r,(N-(r-1)+p-1)\p));
 my(nn=max(N,vecmax(sizes)),ww=vector(n,i,sqrt(o+aa[i]*T+O(T^nn))),ch=vector(2^n,S,prod(i=1,n,if(bittest(S-1,i-1),ww[i],o))),R=prod(i=1,n,o+aa[i]*T)^((p-1)/2));
 my(source=matrix(N,N,i,j,polcoef(ch[I[i][1]+1]*T^I[i][2],j-1,T)),D=matrix(N,total,i,j,0*o),block=matrix(total,N,i,j,0*o),rec=matrix(N,N,i,j,0*o),offset=0,jetoff=0,pos=Map());
 for(r=1,p,
   for(k=1,sizes[r],mapput(pos,[r,J[r][k][1],J[r][k][2]],offset+k));
   my(Jet=matrix(sizes[r],L[r],i,j,polcoef(ch[J[r][i][1]+1]*T^J[r][i][2],j-1,T)));
   for(i=1,sizes[r],for(j=1,L[r],block[offset+i,jetoff+j]=Jet[i,j]));
   offset+=sizes[r];jetoff+=L[r];
 );
 assert(jetoff==N,"digit jet count");
 for(i=1,N,
   my(S=I[i][1],jj=I[i][2],poly=T^jj*prod(k=1,n,if(bittest(S,k-1),o,o+aa[k]*T))^((p-1)/2));
   for(r=0,p-1,for(k=0,(poldegree(poly,T)-r)\p,
     if(p*k+r<=poldegree(poly,T),
       my(cf=polcoef(poly,p*k+r,T)^(p^(ext-1)));
       if(cf!=0,assert(hammingweight(S)+2*k<=ed[r+1],"degree overflow");D[i,mapget(pos,[r+1,S,k])]=cf);
     )
   ));
 );
 my(digit=D*block,off=0);
 for(r=0,p-1,for(k=0,L[r+1]-1,for(i=1,N,rec[i,p*k+r+1]=digit[i,off+k+1]^p));off+=L[r+1]);
 my(expected=matrix(N,N,i,j,polcoef(R*ch[I[i][1]+1]*T^I[i][2],j-1,T)));
 assert(rec==expected,"marked reconstruction failed");
 my(rankD=matrank(D),rankJ=matrank(source));assert(rankD==N,"split is not injective");
 print("n=",n," p=",p," d=",d," source_dim=",N," target_degrees=",ed," target_dim=",total," image_codim=",total-N," source_jet_rank=",rankJ," all marked entries PASS slopes=",aa);
 if(d==1,assert(rankJ==6,"known degree-one failure missing"),
   assert(total-N==(p-1)*n*2^(n-2),"bulk codimension");
   my(Q=matker(D),K=matker(block~),comp=Q~*K,rankC=matrank(comp));
   assert(#K==total-N && #Q==total-N,"kernel/quotient dimensions");
   assert(total-N-rankC==N-rankJ,"compatibility/direct kernel mismatch");
   print("compatibility_size=",total-N," compatibility_rank=",rankC," exact kernel equivalence PASS");
 );
);
}
quit;
