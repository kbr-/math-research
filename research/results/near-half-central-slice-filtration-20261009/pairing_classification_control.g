# New test of the exact central pairing classification, not another size sweep.
# q=17 is the first tested prime where sign classes outnumber the binary
# dimension of z^a+z^-a, so one primitive root can miss an unpaired row.
# All 1716 signed/permutation coefficient orbits at k=6, q=17 are checked.
# Native GAP packed GF(2) evaluation ranks; GF(256) character comparisons.
RunPairing := function()
local out,k,q,h,F,E,zeta,pts,ones,monsLow,monsHigh,low,high,row,coeffSets,
 a,b,ids,pairable,oneZero,allZero,vals,rk,rankHigh,count,pairedCount,
 missedCount,emptyCount,nonpairedCount,lamb,moment,one,zero;
 out:="research/results/near-half-central-slice-filtration-20261009/pairing_classification_output.txt";
 PrintTo(out,"Exact central pairing classification; q=17 k=6.\n");
 k:=6; q:=17; h:=OrderMod(2,q); F:=GF(2); E:=GF(2^h);
 zeta:=Z(2^h)^QuoInt(2^h-1,q); one:=One(F); zero:=Zero(F);
 pts:=Tuples([0,1],k); ones:=List(pts,p->Filtered([1..k],j->p[j]=1));
 monsLow:=Concatenation(List([0..2],j->Combinations([1..k],j)));
 monsHigh:=Concatenation(List([0..3],j->Combinations([1..k],j)));
 low:=List(ones,on->List(monsLow,function(m) if IsSubset(on,m) then return one; else return zero; fi; end));
 high:=List(ones,on->List(monsHigh,function(m) if IsSubset(on,m) then return one; else return zero; fi; end));
 for row in low do ConvertToVectorRep(row,2); od;
 for row in high do ConvertToVectorRep(row,2); od;
 coeffSets:=Filtered(Tuples([1..8],k),a->ForAll([1..k-1],i->a[i]<=a[i+1]));
 if Length(coeffSets)<>Binomial(13,6) then Error("orbit count"); fi;
 count:=0; pairedCount:=0; missedCount:=0; emptyCount:=0; nonpairedCount:=0;
 for a in coeffSets do
  count:=count+1; b:=(9*Sum(a)) mod q;
  ids:=Filtered([1..Length(pts)],i->(Sum([1..k],j->a[j]*pts[i][j])-b) mod q=0);
  pairable:=ForAll([1..8],j->Number(a,x->x=j) mod 2=0);
  oneZero:=Sum(a,t->zeta^t+zeta^(-t))=Zero(E);
  allZero:=ForAll([1..16],lamb->Sum(a,t->zeta^(lamb*t)+zeta^(-lamb*t))=Zero(E));
  if allZero<>pairable then Error("all-character pairing identity"); fi;
  if IsEmpty(ids) then rk:=0; rankHigh:=0; emptyCount:=emptyCount+1;
  else rk:=RankMat(low{ids}); rankHigh:=RankMat(high{ids}); fi;
  if rankHigh<>Length(ids) then Error("baseline half interpolation"); fi;
  if pairable then
   pairedCount:=pairedCount+1;
   if IsEmpty(ids) or rk=Length(ids) then Error("paired sharpness"); fi;
  else
   nonpairedCount:=nonpairedCount+1;
   if rk<>Length(ids) then Error("unpaired interpolation"); fi;
   if oneZero then missedCount:=missedCount+1; fi;
  fi;
  AppendTo(out,"a=",a," allowed=",Length(ids)," low rank=",rk," half rank=",rankHigh," pairable=",pairable," single-root zero=",oneZero,"\n");
 od;
 AppendTo(out,"PASS orbits=",count," paired=",pairedCount," unpaired=",nonpairedCount," empty=",emptyCount," single-root misses on unpaired=",missedCount,"\n");
end;
RunPairing();
QUIT;
