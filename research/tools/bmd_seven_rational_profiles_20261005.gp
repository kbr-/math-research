\\ Exact six rational residue templates. The selected minor records excluded primes.
\\ c=8d-17,d>=5 in application. Negative representative j values are evaluated
\\ by the polynomial binomial, not treated as actual small-degree instances.
assert(c,s)={if(!c,error(s));};
tailmatrix(r,kind)={
 my(q=2*r+[1,3,7][kind],cuts=if(kind==1,[],if(kind==2,[1],[5,3,1])),nr=3+#cuts,wid=if(kind==1,6,if(kind==2,8,12)));
 return(matrix(nr,wid,i,j,
  if(i<=3,binomial(q-j+1,[1,3,5][i]),
   if(j-1<=cuts[i-3],binomial(q-j+1,cuts[i-3]-j+1),0))));
};
{
my(res=[0,1,1/2,-1/2,3/2,-3/2],allprimes=List());
for(ri=1,#res,
 for(kind=1,3,
  my(M=tailmatrix(res[ri],kind),P=List(),rank=0);
  for(j=1,matsize(M)[2],
   my(trial=concat(Vec(P),[j]),B=matrix(matsize(M)[1],#trial,i,k,M[i,trial[k]]),r=matrank(B));
   if(r>rank,listput(P,j);rank=r);
   if(rank==matsize(M)[1],break);
  );
  assert(rank==matsize(M)[1],"full tail rank");
  my(B=matrix(rank,rank,i,j,M[i,P[j]]),det=matdet(B),coords=B^-1*M,fac=factor(abs(det))[,1]);
  for(j=1,matsize(M)[2],for(i=1,rank,if(P[i]>j,assert(coords[i,j]==0,"earlier column depends on a later pivot"))));
  for(j=1,#fac,listput(allprimes,fac[j]));
  print("c=",res[ri]," block=",["A","B","C"][kind]," offsets=",vector(rank,j,P[j]-1)," determinant=",det," prime_divisors=",fac~);
 );
);
print("all exceptional determinant primes=",Set(Vec(allprimes)));
print("PASS: all prefix dependencies and exact selected minors checked.");
}
quit;
