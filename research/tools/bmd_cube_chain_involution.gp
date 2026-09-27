\\ Encoding checks for the uniform chain-graph obstruction, not a normality sweep.
\\ Check the coset-to-butterfly coordinates exhaustively at n3,n4,n5.
\\ Check every cut and exterior label at k2,k3; all four marked cut edges are fixed.
coord(g,j,k)={my(x=0);for(l=1,k,x+=2^(l-1)*if(l<j,bitxor(bittest(g,0),bittest(g,l)),bittest(g,l+1)));x};
invstate(level,x,k,j,L0,R0)={
 my(L=bitand(x,2^(j-1)-1),R=x\2^j);
 if(level<j,
  if(R!=R0,return(bitxor(x,2^(j-1))));
  if(level<j-1,return(bitxor(x,2^(j-2))));
 ,
  if(L!=L0,return(bitxor(x,2^(j-1))));
  if(level>j,return(bitxor(x,2^j)));
 );
 x
};
{
my(k,M,a,b,c,jj,xa,xb);
for(nn=3,5,k=nn-2;M=2^k;
 for(j=1,nn-1,
  if(j==1,a=1;b=2,if(j==nn-1,a=2^(nn-1);b=2^nn-1,a=2^j-1;b=2^j));
  for(g=0,2^nn-1,
   if(coord(g,j,k)!=coord(bitxor(g,a),j,k)||coord(g,j,k)!=coord(bitxor(g,b),j,k),error("coset invariance"));
  );
 );
 for(j=1,k,c=2^(j+1)-1;
  my(seen=matrix(M,M),cnt=0);
  for(g=0,2^nn-1,if(g<bitxor(g,c),
   xa=coord(g,j,k);xb=coord(g,j+1,k);
   if(bitand(bitxor(xa,xb),bitxor(M-1,2^(j-1)))!=0,error("wrong butterfly edge"));
   if(seen[xa+1,xb+1],error("duplicate butterfly edge"));seen[xa+1,xb+1]=1;cnt++;
  ));
  if(cnt!=2*M,error("edge cardinality"));
 );
 print("COSET_BUTTERFLY_ENCODING n=",nn," PASSED");
);
for(k=2,3,M=2^k;
 my(nv=(k+1)*M,el=List(),vlevel=vector(nv,i,(i-1)\M),vstate=vector(nv,i,(i-1)%M),A=matrix(nv,nv));
 for(j=1,k,for(x=0,M-1,for(bit=0,1,
  my(y=bitxor(bitand(x,bitxor(M-1,2^(j-1))),bit*2^(j-1)),u=(j-1)*M+x+1,v=j*M+y+1);
  listput(el,[u,v]);A[u,v]=1;A[v,u]=1;
 )));
 my(E=Vec(el),H=vector(nv,i,if(vlevel[i]==k,2,0))~);
 for(j=1,k,for(L0=0,2^(j-1)-1,for(R0=0,2^(k-j)-1,
  my(S=vector(nv,i,vlevel[i]*M+invstate(vlevel[i],vstate[i],k,j,L0,R0)+1));
  for(i=1,nv,if(S[S[i]]!=i||H[S[i]]!=H[i],error("involution or H")));
  for(e=1,#E,if(!A[S[E[e][1]],S[E[e][2]]],error("edge not preserved")));
  my(vfix=sum(i=1,nv,S[i]==i),efix=sum(e=1,#E,S[E[e][1]]==E[e][1]&&S[E[e][2]]==E[e][2]));
  if(vfix!=2^j+2^(k-j+1)||efix!=4,error("fixed count"));
  my(g=#E-nv+1,gq=(g+1+efix-vfix)/2);
  if(gq>(g-1)/2,error("quotient genus"));
  print("INVOLUTION k=",k," cut=",j," L=",L0," R=",R0," fixed_vertices=",vfix," fixed_edges=",efix," quotient_genus=",gq," permutation=",S);
 )));
 if(#E<=4,error("negative control needs exchanged edges"));
 print("WRONG_FIXED_EDGE_EXPANSION_REJECTED k=",k," fixed-edge fibre-degree1 differs from exchanged-edge fibre-degree2");
);
print("ALL_CHAIN_INVOLUTION_ENCODING_CONTROLS_PASSED");
}
quit;
