\\ Full certificate replay, independent polynomial-division source recovery,
\\ complete exclusion-domain accounting, and Singular determinant export.
default(parisizemax,1000000000);
default(nbthreads,1);
ep='ep;T='T;b='b;
read("tools/saturated_rows.gp");
check(c,s)=if(!c,error(s));
SINGULAR_OUT="research/results/bmd-profile-family-20261009/independent-minors.sing";
CHECKS=0;REPLAYS=0;MAXPOLE=0;GAPS=0;
emit_determinant(M,expected,p,label)={
  my(n=matsize(M)[1],body="");check(n>0&&matsize(M)[2]==n,"square independent check");CHECKS++;
  for(i=1,n,for(j=1,n,body=concat(body,Str(if(i>1||j>1,",",""),liftall(M[i,j])))));
  write(SINGULAR_OUT,"ring R",CHECKS,"=(",p,",b),(z),dp;");
  write(SINGULAR_OUT,"matrix M",CHECKS,"[",n,"][",n,"]=",body,";");
  write(SINGULAR_OUT,"if(det(M",CHECKS,") != (",liftall(expected),")){ nFailed=nFailed+1; print(\"FAIL ",label,"\"); } nChecked=nChecked+1;");
};
verify_rows(R,C,depth,ops,P,unit,p,label,sharp=0)={
  my(S=[C,depth,ops,P,unit,1,0],replay=if(sharp,sat_specialization(R,ep,S),sat_replay(R,ep,S)),n=matsize(C)[1]);
  check(vecmax(depth)<64,"complete omitted-column pole bound");
  MAXPOLE=max(MAXPOLE,vecmax(depth));REPLAYS++;
  emit_determinant(matrix(n,n,i,j,C[i,P[j]]),unit,p,label);
  replay;
};
verify_source(C,top,g,lo,coff,Q,expectedOffset,piv)={
  my(n=matsize(C)[1],tail=0,degree=poldegree(g,T),q=matsize(Q)[2]);
  for(j=1,matsize(C)[2],if(C[,j]!=vector(n)~,tail=j));
  check(lo==top+degree-tail && q==tail-n && lo+1+q==expectedOffset,"full source dimension and low block");
  if(q==0,check(coff==lo,"complete source range");return());
  check(matsize(Q)[1]==coff-lo,"full high window");
  my(K=matrix(tail,q));
  for(j=1,q,
    my(poly=sum(i=1,coff-lo,Q[i,j]*T^(i-1)),quotient=divrem(T^degree*poly,g,T)[1]);
    for(h=0,tail-1,K[h+1,j]=polcoef(quotient,tail-1-h,T))
  );
  my(free=setminus(Set(vector(tail,i,i)),Set(Vec(piv))));
  check(#free==q&&matrix(q,q,i,j,K[free[i],j])==matid(q),"recovered kernel retains its explicit free-coordinate identity");
  check(C[,1..tail]*K==matrix(n,q),"polynomial division independently recovers the full kernel");
};
run_verify()={
  write(SINGULAR_OUT,"// Generated exact independent determinant checks; coefficient parameter b remains generic.");
  write(SINGULAR_OUT,"int nChecked=0; int nFailed=0;");
  my(fieldCases=List());
  for(r=0,12,
    print("VERIFY_GENERIC residue=",r);
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,".gp"));
    my(audit=verify_rows(R,primitive,poleDepths,operations,rankColumns,rankMinor,0,Str("generic-first-",r),1));
    print("STAGE first rows ms=",gettime());
    verify_source(primitive,parameters[6],(1+T)*(1+b*T)^2,limitLowOffset,limitHighDegree,limitHighCoefficients,2*(r+1),rankColumns);
    print("STAGE first source ms=",gettime());
    read(Str("research/results/bmd-profile-family-20261009/first-r",r,"-minor.gp"));
    check(factor(audit[1])[,1]~==characteristicPrimes && audit[2]==canonicalRows,"complete original-minor stratum");
    print("STAGE first audit ms=",gettime());
    my(first=characteristicPrimes);
    read(Str("research/results/bmd-profile-family-20261009/second-r",r,".gp"));
    if(completeConic,
      check(unitResidue==4*r+3 && #select(p->p>47,factor(unitResidue)[,1]~)==0,"complete-conic ordinary transfer"),
      verify_rows(R,primitive,poleDepths,operations,rankColumns,rankMinor,0,Str("generic-second-",r));
      print("STAGE second rows ms=",gettime());
      verify_source(primitive,2*sourceHighDegree,1+T,limitLowOffset,limitHighDegree,limitHighCoefficients,4*(r+1),rankColumns);
      print("STAGE second source ms=",gettime());
      check(max(lowerIndexBound,endpointIndexBound)<53,"generic binomial carries accounted for");
      check(endpointDeterminant!=0,"generic rational endpoint");
      if(matsize(endpoint)[1]>0,emit_determinant(endpoint,endpointDeterminant,0,Str("generic-endpoint-",r)))
    );
    if(r>=3,my(primes=select(p->p>47,Set(concat(first,characteristicPrimes))));for(j=1,#primes,listput(fieldCases,[r,primes[j]])))
  );
  my(pairs=Vec(fieldCases));check(#pairs==22&&#Set(pairs)==22,"complete distinct excluded-prime domain");
  for(i=1,#pairs,
    my(r=pairs[i][1],p=pairs[i][2],o=Mod(1,p));print("VERIFY_FIELD residue=",r," prime=",p);completed=0;
    read(Str("research/results/bmd-profile-family-20261009/field-r",r,"-p",p,".gp"));
    check(completed==1&&normal==1&&caseResidue==r&&fieldPrime==p,"every actual field case is complete and normal");
    verify_rows(firstR,firstPrimitive,firstPoleDepths,firstOperations,firstRankColumns,firstRankMinor,p,Str("field-first-",r,"-",p));
    verify_source(firstPrimitive,firstParameters[6],o*(1+T)*(1+b*T)^2,firstLowOffset,firstHighDegree,firstHighCoefficients,2*(r+1),firstRankColumns);
    if(completeConic,
      check(sufficientUnit!=0&&firstLowOffset==2*r+1,"field complete-conic transfer"),
      verify_rows(secondR,secondPrimitive,secondPoleDepths,secondOperations,secondRankColumns,secondRankMinor,p,Str("field-second-",r,"-",p));
      verify_source(secondPrimitive,secondParameters[6],o*(1+T),finalLowOffset,finalHighDegree,finalHighCoefficients,4*(r+1),secondRankColumns);
      check(max(secondIndexBound,endpointIndexBound)<p,"all field degree coefficients retain the required prime-power data");
      if(matsize(endpoint)[1]>0,
        emit_determinant(endpoint,endpointDeterminant,p,Str("field-endpoint-",r,"-",p));
        check(matsize(finalHighCoefficients)==[2,1],"one complete rational gap");
        my(a=finalLowOffset+1,lambda=finalHighCoefficients[2,1],formula=o*(a+1)^2*(2*a+1)*(2*a+3)/3);
        check(finalHighCoefficients[1,1]==(a+1)*lambda&&endpointDeterminant==lambda^2*formula&&formula!=0,"exact rational-gap criterion with its actual basis scale");
        print("GAP residue=",r," prime=",p," a=",a," scale=",lambda," criterion=",formula);GAPS++
      )
    )
  );
  write(SINGULAR_OUT,"if(nFailed!=0 || nChecked!=",CHECKS,"){ print(\"FAIL independent checks \"+string(nChecked)+\" failures \"+string(nFailed)); } else { print(\"COMPLETE independent determinants=",CHECKS,"\"); } quit;");
  print("COMPLETE full_row_replays=",REPLAYS," max_inverse_pole=",MAXPOLE," excluded_prime_cases=",#pairs," rational_gaps=",GAPS," independent_determinants_exported=",CHECKS);
};
iferr(run_verify(),E,print(E);quit(1));
quit;
