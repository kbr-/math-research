# Test the named reduced-buffer shortening assertion, not a hardness instance.
# k=5, N=2 gives25 variables,326 squarefree monomials through degree2,
# full affine domain26,90 relation rows, and32 legal coefficient rows.
# Native GAP ranks compare raw quotient matrices with an explicit normal form.
dbOut:="research/results/binary_design_buffer_test_20261010/check.txt";;
dbF:=GF(2);; dbO:=One(dbF);; dbZ:=Zero(dbF);;
dbK:=5;; dbCopies:=2;; dbPairs:=Combinations([1..dbK],2);;
dbN:=dbK+dbCopies*Length(dbPairs);;
dbMons:=Concatenation([[]],List([1..dbN],i->[i]),Combinations([1..dbN],2));;
dbDim:=Length(dbMons);;
dbY:=function(c,a,b)
  return dbK+(c-1)*Length(dbPairs)+Position(dbPairs,Set([a,b]));
end;;
dbInfo:=List([1..dbK],i->[]);;
for dbC in [1..dbCopies] do
  for dbPair in dbPairs do Add(dbInfo,[dbC,dbPair[1],dbPair[2]]); od;
od;
dbTindex:=function(c,b)
  local a;
  a:=1; if b=1 then a:=2; fi;
  return Position(dbMons,[a,dbY(c,a,b)]);
end;;
dbRaw:=function(i,j)
  local v;
  v:=ListWithIdenticalEntries(dbDim,dbZ);
  if j=0 then v[1+i]:=dbO;
  else v[Position(dbMons,Set([i,j]))]:=dbO; fi;
  return v;
end;;
dbNF:=function(i,j,d)
  local v,info,b;
  if j<=dbK then return dbRaw(i,j); fi;
  v:=ListWithIdenticalEntries(dbDim,dbZ);
  if d=3 then return v; fi;
  info:=dbInfo[j]; b:=0;
  if i=info[2] then b:=info[3]; fi;
  if i=info[3] then b:=info[2]; fi;
  if b<>0 then v[dbTindex(info[1],b)]:=dbO; fi;
  return v;
end;;
dbRelations:=[];;
for dbI in [1..dbK] do
  for dbJ in [dbK+1..dbN] do
    dbRow:=dbRaw(dbI,dbJ)+dbNF(dbI,dbJ,2);
    if not IsZero(dbRow) then Add(dbRelations,dbRow); fi;
  od;
od;
dbRelRank:=RankMat(dbRelations);;
Assert(0,dbRelRank=90);
dbRawT:=List([0..dbN],j->Concatenation(List([1..dbK],i->dbRaw(i,j))));;
dbT2:=List([0..dbN],j->Concatenation(List([1..dbK],i->dbNF(i,j,2))));;
dbT3:=List([0..dbN],j->Concatenation(List([1..dbK],i->dbNF(i,j,3))));;
dbBlockRelations:=[];;
for dbI in [1..dbK] do
  for dbRow in dbRelations do
    dbBlocks:=List([1..dbK],j->ListWithIdenticalEntries(dbDim,dbZ));
    dbBlocks[dbI]:=dbRow; Add(dbBlockRelations,Concatenation(dbBlocks));
  od;
od;
dbC2:=RankMat(dbT2);; dbC3:=RankMat(dbT3);;
Assert(0,dbC2=26 and dbC3=6);
Assert(0,RankMat(Concatenation(dbBlockRelations,dbRawT))-dbK*dbRelRank=dbC2);
PrintTo(dbOut,"variables=",dbN," monomials<=2=",dbDim,
 " relation_rank=",dbRelRank," quotient_dimension=",dbDim-dbRelRank,
 " affine_domain=",dbN+1," c2=",dbC2," c3=",dbC3,"\n");
dbLoss2:=0;; dbLoss3:=0;; dbRows:=0;;
for dbCoeff in Tuples([0,1],dbK) do
  dbMraw:=List([0..dbN],j->Sum([1..dbK],i->dbCoeff[i]*dbRaw(i,j)));
  dbM2:=List([0..dbN],j->Sum([1..dbK],i->dbCoeff[i]*dbNF(i,j,2)));
  dbM3:=List([0..dbN],j->Sum([1..dbK],i->dbCoeff[i]*dbNF(i,j,3)));
  dbR2:=RankMat(dbM2); dbR3:=RankMat(dbM3);
  Assert(0,RankMat(Concatenation(dbRelations,dbMraw))-dbRelRank=dbR2);
  if Sum(dbCoeff)=0 then Assert(0,dbR2=0 and dbR3=0);
  else Assert(0,dbR2=13 and dbR3=5); fi;
  dbLoss2:=dbLoss2+dbC2-dbR2; dbLoss3:=dbLoss3+dbC3-dbR3;
  dbRows:=dbRows+1;
  AppendTo(dbOut,"row=",dbCoeff," rank2=",dbR2," kernel2=",dbC2-dbR2,
    " rank3=",dbR3," kernel3=",dbC3-dbR3,"\n");
od;
Assert(0,dbRows=32 and dbLoss2/32=429/32 and dbLoss3/32=37/32);
Assert(0,dbLoss2/32>dbC2/2 and 13>(15/31)*dbC2);
Assert(0,dbLoss3/32<=dbC3/2 and 1<=(15/31)*dbC3);
# Verify all ten exact degree-three PC certificate identities before using
# the displayed D=3 quotient. Every axiom multiplier is affine or a variable.
dbVars:=List([1..dbN],i->Indeterminate(dbF,i));;
dbCerts:=0;;
for dbC in [1..dbCopies] do
  for dbB in [1..dbK] do
    dbOthers:=Filtered([1..dbK],i->i<>dbB);
    dbA:=dbOthers[1]; dbCidx:=dbOthers[2];
    dbBase:=1; if dbB=1 then dbBase:=2; fi;
    dbTarget:=dbVars[dbBase]*dbVars[dbY(dbC,dbBase,dbB)];
    dbXa:=dbVars[dbA]; dbXc:=dbVars[dbCidx];
    dbYab:=dbVars[dbY(dbC,dbA,dbB)];
    dbYcb:=dbVars[dbY(dbC,dbCidx,dbB)];
    dbRab:=dbXa*dbYab+dbTarget;
    dbRcb:=dbXc*dbYcb+dbTarget;
    dbZeroRel:=dbXa*dbYcb;
    dbCert:=(dbXa+dbO)*dbRab+dbYab*(dbXa^2+dbXa)
             +dbXa*dbRcb+dbXc*dbZeroRel;
    Assert(0,dbCert=dbTarget); dbCerts:=dbCerts+1;
  od;
od;
Assert(0,dbCerts=10);
AppendTo(dbOut,"PASS: 32 legal rows; raw/normal quotient ranks agree; ",
 "10 exact degree3 certificates. Mean kernel atD2=",dbLoss2/32,
 "; atD3=",dbLoss3/32,".\n");
QUIT;
