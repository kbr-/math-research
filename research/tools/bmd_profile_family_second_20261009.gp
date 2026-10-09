\\ Complete characteristic-zero templates for the last root and marked endpoints.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;T='T;
read("tools/saturated_rows.gp");
read("research/tools/bmd_profile_family_core_20261009.gp");
run_second()={
  my(completed=0);
  for(r=0,12,
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,".gp"));
    my(lo=limitLowOffset,coff=limitHighDegree,Q=limitHighCoefficients,q=matsize(Q)[2],out=Str("research/results/bmd-profile-family-20261009/second-r",r,".gp"));
    if(q==0,
      my(unit=2*lo+1,bad=factor(abs(unit))[,1]~);
      family_check(lo==2*r+1 && #select(p->p>47,bad)==0,"complete conic source has a unit ordinary minor above47");
      write(out,"completeConic=1; unitResidue=",unit,"; characteristicPrimes=[];");
      print("ENDPOINT residue=",r," complete_conic=true ordinary_unit=",unit),
      my(packet=family_second(r,lo,coff,Q,64,ep,b,T),S=sat_rows(packet[7],ep),A=sat_specialization(packet[7],ep,S),limit=family_limit(packet,S,T),E=family_endpoint(limit));
      family_check(E[2]!=0,"generic rational endpoint is normal");
      family_check(max(packet[11],E[3])<53,"all degree coefficients are determined modulo every prime above47");
      my(contents=sat_contents(E[2]),bad=lcm(A[1],contents[1]*contents[2]));bad=lcm(bad,abs(2*coff+1));
      if(r<=2,
        my(path=["bmd-elliptic-extreme-profile-20261009","bmd-elliptic-adjacent-profile-20261009","bmd-elliptic-second-residue-20261009"][r+1]);
        read(concat(concat("research/results/",path),"/second-constraints.gp"));
        my(C=S[1],nr=matsize(C)[1]);
        family_check(matrank(matconcat([C[,1..32]~,primitive~]))==nr&&C[,33..64]==matrix(nr,32),"same complete second source as the prior proof");
        family_check(limit[1]==[-1,7,11][r+1]&&limit[2]==[4,7,11][r+1],"same complete rational source bounds")
      );
      write(out,"completeConic=0; sourceLowOffset=",lo,"; sourceHighDegree=",coff,"; lowerIndexBound=",packet[11],"; R=",packet[7],"; sourceCuts=",packet[10],";");
      write(out,"primitive=",S[1],"; poleDepths=",S[2],"; operations=",S[3],"; rankColumns=",S[4],"; rankMinor=",S[5],"; canonicalRows=",A[2],"; originalMinorOrder=",A[3],";");
      write(out,"limitLowOffset=",limit[1],"; limitHighDegree=",limit[2],"; limitHighCoefficients=",limit[3],"; limitKernel=",limit[4],"; endpoint=",E[1],"; endpointDeterminant=",E[2],"; endpointIndexBound=",E[3],"; characteristicPrimes=",factor(bad)[,1]~,";");
      print("ENDPOINT residue=",r," rows=",matsize(packet[7])[1]," max_pole=",A[4]," final_low=",limit[1]," final_high=",limit[2]," endpoint_size=",matsize(E[1])[1]," determinant=",E[2]," large_primes=",select(p->p>47,factor(bad)[,1]~))
    );
    completed++
  );
  family_check(completed==13,"all thirteen generic endpoint cases complete");
  print("COMPLETE thirteen generic endpoints and all three prior-source calibrations.");
};
iferr(run_second(),E,print(E);quit(1));
quit;
