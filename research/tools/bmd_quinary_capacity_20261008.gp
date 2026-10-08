\\ Exact dimension of pth-root subspaces in the full paired boundary, no jet sampling.
\\ Question: can source dimension alone force a marked kernel larger than the first-lift rank bound?
\\ Full Y_m has N=2^m*(c+1), c=2^m*(d-m+1)-1; character divisors are the proved recursion.
\\ The output is a lower bound on marked corank, never an equality or an original normality verdict.
default(nbthreads,1);
capacity(m,c,q)={
 my(t=2^m-m-1,w=0);
 for(mask=0,2^m-1,
  my(s=hammingweight(mask),cut=0,cap=(c+t-(q-1)*s/2)\q);
  for(i=1,m,
   my(e=bittest(mask,i-1),bi=(2^(i-1)-1)*e+2^(i-1)*sum(j=i+1,m,1-bittest(mask,j-1)));
   cut+=max(0,ceil((bi-(q-1)*e/2)/q));
  );
  w+=max(0,cap-cut+1);
 );
 return(w);
};
{for(i=1,2,my(d=[125,856][i],c=16*d-49,N=256*(d-3));for(j=1,8,my(q=5^j,w=capacity(4,c,q));print("d=",d," q=",q," root_dim=",w," required_jets=",ceil(N/q)," forced_corank=",max(0,w-ceil(N/q)))));}
print("COMPLETE named Frobenius capacity test; zero lower bound is inconclusive.");
quit;
