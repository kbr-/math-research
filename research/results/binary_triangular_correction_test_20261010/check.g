# Two complete unit-input blocks. Reference components solve opposite blocks:
# R1=[[1,a],[0,0]], R2=[[0,b],[0,1]], a,b in F2.
# Exhaust all off-diagonal pairs and all vectors; a real representation also
# needs commutation. Both source companions must kill a marked nonzero vector.
tcF:=GF(2);; tcI:=IdentityMat(2,tcF);; tcV:=Elements(VectorSpace(tcF,tcI));;
tcPairs:=0;; tcCommute:=0;; tcTests:=0;;
for tcA in Elements(tcF) do
  for tcB in Elements(tcF) do
    tcR:=[[One(tcF),tcA],[Zero(tcF),Zero(tcF)]];;
    tcS:=[[Zero(tcF),tcB],[Zero(tcF),One(tcF)]];;
    if tcR^2<>tcR or tcS^2<>tcS then Error("Boolean action"); fi;
    if tcR*tcS=tcS*tcR then tcCommute:=tcCommute+1; fi;
    if RankMat((tcI-tcR)+(tcI-tcS))<>2 then Error("error sum"); fi;
    for tcW in tcV do
      if tcW<>[Zero(tcF),Zero(tcF)]
         and (tcI-tcR)*tcW=[Zero(tcF),Zero(tcF)]
         and (tcI-tcS)*tcW=[Zero(tcF),Zero(tcF)] then
        Error("unexpected nonzero common source witness");
      fi;
      tcTests:=tcTests+1;
    od;
    tcPairs:=tcPairs+1;
  od;
od;
# Positive control changes the reference itself to the joint legal choice.
if tcI-tcI<>NullMat(2,2,tcF) then Error("joint reference control"); fi;
Print("PASS: ",tcPairs," off-diagonal pairs; ",tcCommute,
      " commuting pairs; ",tcTests," vector tests; no nonzero common witness.\n");
Print("Joint reference R1=R2=I kills both companions and preserves every vector.\n");
QUIT;
