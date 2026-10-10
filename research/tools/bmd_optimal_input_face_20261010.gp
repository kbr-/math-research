\\ For n9,p5, optimal cofactor transfer terms cannot use input >=25:
\\ their complementary identity columns have weights >=25, larger than every transfer
\\ weight k-26<=21, so all these independent high columns belong to every maximum basis.
\\ Enumerate the remaining C(11,8)=165 inputs containing zero, with every output available.
T='T;
greedycols(A)={my(piv=[]);for(k=1,matsize(A)[2],my(q=concat(piv,k));if(matrank(matrix(matsize(A)[1],#q,i,j,A[i,q[j]]))>#piv,piv=q));piv};
{
my(n=9,p=5,m=47,b=Vec(sqrt(Mod(1,p)+T+O(T^48))),S=[1,2,3,5,6,7,8,10,11,12,13]);
for(c=0,47,
 my(G=select(j->b[j+1]!=0,[0..47]),ks=select(k->k!=c,[0..47]),t=#G,
 W=concat(vector(t-1,i,G[i+1]),vector(#ks,i,ks[i]-26)),order=vecsort(W,,5),
 B=matrix(t,t-1+#ks,i,j,if(j<t,i==j+1,if(ks[j-t+1]>=G[i],b[ks[j-t+1]-G[i]+1],0)))*Mod(1,p),
 sorted=matrix(t,#order,i,j,B[i,order[j]]),pv=greedycols(sorted),
 w=sum(i=1,#pv,W[order[pv[i]]]),count=0,optimal=0,upper=w-sum(i=1,t,G[i])+26*n);
 if(#pv!=t,error("Weighted matrix rank failure"));
 print("BOUND omit=",c," weight=",w," upper=",upper);
 forsubset([11,8],ss,
  my(J=concat([0],vector(8,i,S[ss[i]])),K0=select(k->k!=c,vector(48,i,48-i)),
  A=matrix(n,47,i,j,if(K0[j]>=J[i],b[K0[j]-J[i]+1],Mod(0,p))),piv=greedycols(A),
  K=vecsort(vector(#piv,i,K0[piv[i]])),d=sum(i=1,n,K[i]-J[i]));
  if(#piv!=n,error("Input rank failure"));
  count++;if(d>upper,error("Contradicts certified upper bound"));
  if(d==upper,optimal++;print("omit=",c," J=",J," K=",K," degree=",d," scalar=",lift(matdet(matrix(n,n,i,j,if(K[j]>=J[i],b[K[j]-J[i]+1],Mod(0,p)))))));
 );
 print("omit=",c," inputs_checked=",count," optimal=",optimal);
);
print("OPTIMAL_INPUT_FACE_COMPLETED");
}
quit;
