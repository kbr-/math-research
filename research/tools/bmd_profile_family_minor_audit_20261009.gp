\\ Replace elimination-prime lists by the original minimal-minor open stratum.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("tools/saturated_rows.gp");
check(c,s)=if(!c,error(s));
run_audit()={
  my(count=0,oldTotal=0,newTotal=0);
  for(r=0,12,
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,".gp"));
    my(S=[primitive,poleDepths,operations,rankColumns,rankMinor,1,0],A=sat_specialization(R,ep,S),primes=factor(A[1])[,1]~);
    check(A[4]<64,"full tail bound survives on the minimal-minor stratum");
    for(i=1,matsize(limitHighCoefficients)[1],for(j=1,matsize(limitHighCoefficients)[2],my(d=sat_contents(limitHighCoefficients[i,j])[2],g=gcd(d,A[1]));while(g>1,d/=g;g=gcd(d,A[1]));check(d==1,"source basis has no extra characteristic denominator")));
    write(Str("research/results/bmd-profile-family-20261009/first-r",r,"-minor.gp"),"characteristicPrimes=",primes,"; canonicalRows=",A[2],"; originalMinorOrder=",A[3],"; inversePoleBound=",A[4],";");
    my(before=select(p->p>47,excludedPrimes),after=select(p->p>47,primes));
    print("MINOR_AUDIT residue=",r," order=",A[3]," inverse_pole=",A[4]," primes=",primes," large_prime_checks=",#before,"->",#after);
    if(r>=3,oldTotal+=#before;newTotal+=#after);count++
  );
  check(count==13,"all thirteen complete source audits");
  print("COMPLETE remaining_large_prime_checks=",oldTotal,"->",newTotal," original_minors_and_full_replays=true");
};
iferr(run_audit(),E,print(E);quit(1));
quit;
