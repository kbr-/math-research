\\ The support-adjusted initial cofactor degree upper bound and its extremal scalar.
T='T;
{
for(ci=1,2,
 my(n=if(ci==1,4,9),p=if(ci==1,101,5),m=n*(n+1)/2+2,r=m-n,
 b=Vec(sqrt(Mod(1,p)+T+O(T^(m+1)))),allowed=select(j->b[j+1]!=0,[0..m-1]),J=vector(n,i,allowed[i]),
 K=vector(n,i,r+i-1),M=matrix(n,n,i,j,if(K[j]>=J[i],b[K[j]-J[i]+1],Mod(0,p))),
 upper=r*n+n*(n-1)/2-sum(i=1,n,J[i]));
 print("n=",n," p=",p," J=",J," K=",K," transfer_det=",matdet(M)," original_bound=",upper," reduced_bound=",upper-n*(n+1));
);
print("AXIS_BOUND_COMPLETED");
}
quit;
