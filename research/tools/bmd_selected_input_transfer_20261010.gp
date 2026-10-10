\\ Exact maximum output weight for each fixed supported input and omitted column.
\\ Tests whether primitive sparse input minors can occur in the attained top layer.
\\ Only constant matrices over the prime field; no claim of original-source noncancellation.
T='T;
greedycols(A)={my(piv=[]); for(k=1,matsize(A)[2],my(q=concat(piv,k));if(matrank(matrix(matsize(A)[1],#q,i,j,A[i,q[j]]))>#piv,piv=q));piv};
{
for(ci=1,3,
 my(n=if(ci==1,9,if(ci==2,7,4)),p=if(ci==1,5,if(ci==2,3,101)),m=n*(n+1)/2+2,
 b=Vec(sqrt(Mod(1,p)+T+O(T^(m+1)))),support=select(j->b[j+1]!=0,[0..m]));
 for(variant=0,1,
  my(J=vector(n,i,support[i])); J[n]=support[n+variant];
  print("CASE n=",n," p=",p," J=",J," sumJ=",sum(i=1,n,J[i]));
  for(c=0,m,
   my(K0=select(k->k!=c,vector(m+1,i,m+1-i)), A=matrix(n,m,i,j,if(K0[j]>=J[i],b[K0[j]-J[i]+1],Mod(0,p))),
   piv=greedycols(A),K=vecsort(vector(#piv,i,K0[piv[i]])),R=matrix(n,#K,i,j,if(K[j]>=J[i],b[K[j]-J[i]+1],Mod(0,p))));
   if(#piv!=n,error("Unexpected fixed-input rank loss"));
   print("omit=",c," max_degree=",sum(i=1,n,K[i]-J[i])," K=",K," scalar=",lift(matdet(R)));
  );
 );
);
print("SELECTED_INPUT_TRANSFER_COMPLETED");
}
quit;
