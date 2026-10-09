\\ Exact finite original complement after the uniform n9/n10 bulk theorem.
\\ Reuses the integral joint-leading valuation formula; tests it once before the series.
\\ The entire requested remaining prime interval is53..97, not a sampled subset.
default(nbthreads,1);
check(c,s)=if(!c,error(s));
N(n,d)=sum(k=0,min(n,d),binomial(n,k)*(1+(d-k)\2));
vfact(n,p)={my(v=0,q=p);while(q<=n,v+=n\q;q*=p);v;};
vH(s,h,p)=sum(i=1,h-1,vfact(2*s+i+h-1,p)-vfact(2*s+2*i-1,p)+vfact(2*i-1,p)-vfact(i+h-1,p));
plan_grid()={
 my(control=0,primes=primes([53,97]),all=List(),direct=0,largest=0,candidates=0);
 for(s=0,4,for(h=0,8,my(H=1);for(i=1,h-1,for(j=i,h-1,H*=(2*s+i+j)/(i+j)));check(denominator(H)==1,"integer coefficient");forprime(p=3,31,check(vH(s,h,p)==valuation(H,p),"exact product valuation control");control++)));
 check(vH(2,2,3)==1&&vH(4,4,7)==1,"nonunit negative controls");
 for(k=1,#primes,my(p=primes[k],needed=vector(2));
  for(n=9,10,my(top=n-3,degrees=List());
   check(p>2*(n-1)-2,"both finite degree-one parent bounds");
   for(d=2,top,my(r=N(n-1,d),s=N(n-1,d-1),h=r-s,v=vH(s,h,p));
    check(v>=0,"integral leading scalar");candidates++;
    if(v!=0,listput(degrees,d);direct++;largest=max(largest,N(n,d)));
    print("FILTER n=",n," p=",p," d=",d," N=",N(n,d)," valuation=",v," sufficient=",v==0)
   );needed[n-8]=Vec(degrees)
  );
  listput(all,[p,needed]);
  write(Str("research/results/bmd-original-low-complement-20261009/filter-p",p,".gp"),"FILTER_PRIME=",p,";DIRECT_DEGREES=",needed,";ASSUMES_N9_COMPLETE=1;")
 );
 write("research/results/bmd-original-low-complement-20261009/plan.json",Vec(all));
 print("COMPLETE primes=",#primes," original_candidates=",candidates," direct=",direct," coefficient_skips=",candidates-direct," max_rows=",largest," exact_controls=",control)
};
iferr(plan_grid(),E,print(E);quit(1));
quit;
