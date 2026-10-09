\\ Exact symbolic reductions at all large primes excluded by the generic templates.
\\ Each case is over F_p(b), for every positive p-divisible degree parameter.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("tools/saturated_rows.gp");
read("research/tools/bmd_profile_family_core_20261009.gp");
family_field_cases()={
  my(cases=List());
  for(r=3,12,
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,"-minor.gp"));my(first=characteristicPrimes);
    read(Str("research/results/bmd-profile-family-20261009/second-r",r,".gp"));
    my(primes=select(p->p>47,Set(concat(first,characteristicPrimes))));
    for(i=1,#primes,listput(cases,[r,primes[i]]))
  );Vec(cases);
};
run_fields()={
  my(all=family_field_cases(),mode=getenv("BMD_FAMILY_MODE"),pilot=[[3,73],[4,137]],cases,passed=0,failed=0);
  for(i=1,#pilot,family_check(setsearch(Set(all),pilot[i])!=0,"pilot belongs to the exact exclusion domain"));
  if(mode=="pilot",cases=pilot,if(mode=="remaining",cases=select(x->!setsearch(Set(pilot),x),all),error("set BMD_FAMILY_MODE to pilot or remaining")));
  print("CASE_DOMAIN total=",#all," selected=",#cases," mode=",mode);
  for(idx=1,#cases,
    my(r=cases[idx][1],p=cases[idx][2],o=Mod(1,p));print("START residue=",r," characteristic=",p);gettime();
    my(P1=family_first(r,64,ep,b,T,0,p),S1=sat_rows(P1[7],ep,p),L1=family_limit(P1,S1,T),out=Str("research/results/bmd-profile-family-20261009/field-r",r,"-p",p,".gp"),normal,kind);
    write(out,"caseResidue=",r,"; fieldPrime=",p,"; firstParameters=",P1[1..6],"; firstR=",P1[7],"; firstCuts=",P1[10],";");
    write(out,"firstPrimitive=",S1[1],"; firstPoleDepths=",S1[2],"; firstOperations=",S1[3],"; firstRankColumns=",S1[4],"; firstRankMinor=",S1[5],"; firstLowOffset=",L1[1],"; firstHighDegree=",L1[2],"; firstHighCoefficients=",L1[3],";");
    if(matsize(L1[3])[2]==0,
      family_check(L1[1]==2*r+1,"complete conic source dimension");
      my(unit=o*(2*L1[1]+1));family_check(unit!=0,"last ordinary paired minor is a unit");
      normal=1;kind="complete_conic";write(out,"completeConic=1; sufficientUnit=",unit,";");
      print("FIELD residue=",r," p=",p," complete_conic=true unit=",unit," cpu_ms=",gettime()),
      my(P2=family_second(r,L1[1],L1[2],L1[3],64,ep,b,T,0,p),S2=sat_rows(P2[7],ep,p),L2=family_limit(P2,S2,T),E=family_endpoint(L2,p));
      for(i=1,matsize(L2[3])[1],for(j=1,matsize(L2[3])[2],family_check(type(o*L2[3][i,j])=="t_INTMOD","last source coefficients lie in the actual prime field")));
      normal=(E[2]!=0);kind="rational_endpoint";
      write(out,"completeConic=0; secondParameters=",P2[1..6],"; secondR=",P2[7],"; secondCuts=",P2[10],"; secondIndexBound=",P2[11],";");
      write(out,"secondPrimitive=",S2[1],"; secondPoleDepths=",S2[2],"; secondOperations=",S2[3],"; secondRankColumns=",S2[4],"; secondRankMinor=",S2[5],";");
      write(out,"finalLowOffset=",L2[1],"; finalHighDegree=",L2[2],"; finalHighCoefficients=",L2[3],"; endpoint=",E[1],"; endpointDeterminant=",E[2],"; endpointIndexBound=",E[3],";");
      if(!normal,write(out,"endpointKernel=",matker(E[1]),";"));
      print("FIELD residue=",r," p=",p," first_low=",L1[1]," first_high=",L1[2]," first_dim=",matsize(L1[3])[2]," final_low=",L2[1]," final_high=",L2[2]," endpoint_size=",matsize(E[1])[1]," determinant=",E[2]," normal=",normal," cpu_ms=",gettime())
    );
    write(out,"normal=",normal,"; completed=1;");if(normal,passed++,failed++)
  );
  family_check(passed+failed==#cases,"every selected excluded-prime source accounted for");
  print("COMPLETE mode=",mode," passed=",passed," unresolved_boundaries=",failed," total_domain=",#all);
};
iferr(run_fields(),E,print(E);quit(1));
quit;
