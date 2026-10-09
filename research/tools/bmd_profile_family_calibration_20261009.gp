\\ Real-source calibration of the shared saturation kernel against six completed certificates.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;b='b;
read("tools/saturated_rows.gp");
check(c,s)=if(!c,error(s));
run_calibration()={
  my(paths=["bmd-elliptic-extreme-profile-20261009","bmd-elliptic-adjacent-profile-20261009","bmd-elliptic-second-residue-20261009"],count=0);
  for(caseId=1,3,for(stage=1,2,
    read(concat(concat("research/results/",paths[caseId]),if(stage==1,"/constraints.gp","/second-constraints.gp")));
    my(S=sat_rows(R,ep));
    check(S[1]==primitive,"same full primitive source rows");
    check(S[2]==poleDepths,"same complete left-transformation pole bounds");
    check(factor(S[6])[,1]~==excludedPrimes,"same exact prime exclusions");
    check(S[3]==Vec(operations),"same replayable row-operation certificate");
    print("CALIBRATED case=",caseId," stage=",stage," rows=",matsize(R)[1]," cols=",matsize(R)[2]," max_pole=",vecmax(S[2]));
    count++
  ));
  check(count==6,"all real-source calibrations complete");
};
iferr(run_calibration(),E,print(E);quit(1));
print("COMPLETE six real-source certificates matched exactly.");
quit;
