\\ Calibrate the common encoder, then classify all remaining first-root source limits.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("tools/saturated_rows.gp");
read("research/tools/bmd_profile_family_core_20261009.gp");
run_family()={
  my(mode=getenv("BMD_FAMILY_MODE"),cases,completed=0);
  if(mode=="pilot",cases=[0,1,2],if(mode=="remaining",cases=vector(10,i,i+2),error("set BMD_FAMILY_MODE to pilot or remaining")));
  for(idx=1,#cases,
    my(r=cases[idx]);print("START residue=",r);gettime();
    my(packet=family_first(r,64,ep,b,T),S=sat_rows(packet[7],ep),limit=family_limit(packet,S,T),bad=factor(S[6])[,1]~);
    if(mode=="pilot",
      my(path=["bmd-elliptic-extreme-profile-20261009","bmd-elliptic-adjacent-profile-20261009","bmd-elliptic-second-residue-20261009"][r+1]);
      read(concat(concat("research/results/",path),"/constraints.gp"));
      my(C=S[1],nr=matsize(C)[1]);
      family_check(matrank(matconcat([C[,1..32]~,primitive~]))==nr&&C[,33..64]==matrix(nr,32),"same complete source row space as prior proof");
      family_check(limit[1]==[-1,0,0][r+1]&&limit[2]==[6,6,7][r+1],"same source low and high bounds");
      my(g=(1+T)*(1+b*T)^2,V=if(r==0,[g,g^2],if(r==1,[g,T*g,T^2*(b*T+b+2)*g],vector(5,i,T^(i-1)*g))),E=matrix(limit[2]-limit[1],#V,i,j,polcoef(V[j],limit[1]+i,T)));
      family_check(matrank(matconcat([limit[3],E]))==#V,"same actual high source span")
    );
    my(out=Str("research/results/bmd-profile-family-20261009/first-r",r,".gp"));
    write(out,"parameters=",packet[1..6],"; lowerIndexBound=",packet[11],";");
    write(out,"R=",packet[7],"; sourceQ=",packet[8],"; sourcePivotRows=",packet[9],"; sourceCuts=",packet[10],";");
    write(out,"primitive=",S[1],"; poleDepths=",S[2],"; operations=",S[3],"; rankColumns=",S[4],"; rankMinor=",S[5],"; excludedPrimes=",bad,";");
    write(out,"limitLowOffset=",limit[1],"; limitHighDegree=",limit[2],"; limitHighCoefficients=",limit[3],"; limitKernel=",limit[4],";");
    print("SOURCE residue=",r," rows=",matsize(packet[7])[1]," max_pole=",vecmax(S[2])," low_offset=",limit[1]," high_degree=",limit[2]," high_dimension=",matsize(limit[3])[2]," excluded_primes=",bad," cpu_ms=",gettime());
    completed++
  );
  family_check(completed==#cases,"complete selected family domain");
  print("COMPLETE mode=",mode," cases=",completed," full_sources=true");
};
iferr(run_family(),E,print(E);quit(1));
quit;
