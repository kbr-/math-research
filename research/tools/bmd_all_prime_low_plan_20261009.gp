\\ Exhaust the prime divisors of all remaining original low-degree coefficients.
\\ The uniform bulk theorem covers higher degrees; primes<=97 are already complete.
default(parisizemax,500000000);
default(nbthreads,1);
check(c,s)=if(!c,error(s));
N(n,d)=sum(k=0,min(n,d),binomial(n,k)*(1+(d-k)\2));
vfact(n,p)={my(v=0,q=p);while(q<=n,v+=n\q;q*=p);v;};
vH(s,h,p)=sum(i=1,h-1,vfact(2*s+i+h-1,p)-vfact(2*s+2*i-1,p)+vfact(2*i-1,p)-vfact(i+h-1,p));
full_plan()={
 my(byPrime=Map(),primeKeys=List(),degreeRows=List(),total=0,maxRows=0);
 check(vH(2,2,3)==1&&vH(4,4,7)==1,"old nonunit controls");
 for(n=9,10,for(d=2,n-3,
  my(r=N(n-1,d),s=N(n-1,d-1),h=r-s,bound=2*r-2,H=1,back=1,factors=List(),remaining=List());
  for(i=1,h-1,H*=(2*s+i+h-1)!*(2*i-1)!/((2*s+2*i-1)!*(i+h-1)!));
  check(denominator(H)==1,"integral exact coefficient");
  forprime(p=2,bound,my(v=vH(s,h,p));check(v>=0,"nonnegative integer valuation");
   if(v>0,listput(factors,[p,v]);back*=p^v;
    if(p>97,
     listput(remaining,p);total++;maxRows=max(maxRows,N(n,d));
     if(!mapisdefined(byPrime,p),listput(primeKeys,p));
     my(degrees=if(mapisdefined(byPrime,p),mapget(byPrime,p),[[],[]]));
     degrees[n-8]=concat(degrees[n-8],[d]);mapput(byPrime,p,degrees)
    )
   )
  );
  check(H==back,"complete prime factorization multiplied back exactly");
  check(bound<=(n-2)*2^(n-2)-2,"consistent dimension-only bound");
  listput(degreeRows,[n,d,N(n,d),bound,H,Vec(factors),Vec(remaining)]);
  print("DEGREE n=",n," d=",d," rows=",N(n,d)," prime_bound=",bound," remaining_primes=",#remaining," coefficient_bits=",logint(H,2)+1)
 ));
 my(keys=Set(Vec(primeKeys)),plan=vector(#keys,i,[keys[i],mapget(byPrime,keys[i])]));
 write("research/results/bmd-all-prime-complement-20261009/degree-factorizations.json",Vec(degreeRows));
 write("research/results/bmd-all-prime-complement-20261009/plan.json",plan);
 print("COMPLETE original_matrices=",total," distinct_primes=",#keys," field_dimension_jobs=",sum(i=1,#plan,(#plan[i][2][1]>0)+(#plan[i][2][2]>0))," max_rows=",maxRows," exact_factorizations=",#degreeRows)
};
iferr(full_plan(),E,print(E);quit(1));
quit;
