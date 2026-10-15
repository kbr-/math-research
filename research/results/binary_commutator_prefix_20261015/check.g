# Statement tested: the complete ordered prefixes of the three actual
# commutativity-square blocks square to central 0/I flags on all M2(F2) pairs,
# and each full prefix times the original three-clause input mask squared is zero.
# Stages: free-algebra root checks; exhaustive 16-by-16 matrix pairs for
# each of three fixed graph variants; root-only negative control; full grid.
# Refuted by: any wrong formal root, noncentral squared prefix, or surviving full mask.
# Possible because: intermediate proof lines can contribute noncentral factors
# even though the last line has a central square-commutator value.
# Expected: all formal roots agree, all squared-prefix and whole-mask checks pass,
# and at the order-three matrix paired with zero the root-only mask is nonzero.
# Refuted by: the stated root-only altered mask agreeing with the full zero mask.
# Possible because: the commutator root is zero at that commuting pair while
# an internal Booleanity line has value I and kills the complete prefix.
Read("research/results/binary_commutator_prefix_20261015/words.g");
ncField:=GF(2);; ncOne:=One(ncField);; ncZero:=Zero(ncField);;
ncI:=IdentityMat(2,ncField);; ncZ:=NullMat(2,2,ncField);;
ncAlgebra:=FreeAssociativeAlgebraWithOne(ncField,"x","y");;
ncGenerators:=GeneratorsOfAlgebra(ncAlgebra);;
if Length(ncGenerators)<>3 then Error("unexpected free algebra generators"); fi;
ncLetters:=ncGenerators{[2..3]};;
ncFreeOne:=One(ncAlgebra);; ncFreeZero:=Zero(ncAlgebra);;
ncEval:=function(words,letters,one,zero)
  local total,word,value,letter;
  total:=zero;
  for word in words do
    value:=one;
    for letter in word do value:=value*letters[letter+1]; od;
    total:=total+value;
  od;
  return total;
end;;
ncBits:=function(mat)
  return List(Concatenation(mat),v->IntFFE(v));
end;;
ncMatrices:=List(Tuples([ncZero,ncOne],4),v->[[v[1],v[2]],[v[3],v[4]]]);;
ncVectors:=Filtered(Tuples([ncZero,ncOne],2),v->v<>[ncZero,ncZero]);;
ncHasLine:=function(a,b)
  return ForAny(ncVectors,v->(a*v in [[ncZero,ncZero],v]) and
                             (b*v in [[ncZero,ncZero],v]));
end;;
ncRoot:=(ncLetters[1]*ncLetters[2]+ncLetters[2]*ncLetters[1])^2;;
if ncRoot=ncFreeZero then Error("vacuous formal root control"); fi;
ncStream:=OutputTextFile("research/results/binary_commutator_prefix_20261015/matrix-grid.txt",false);;
SetPrintFormattingStatus(ncStream,false);
PrintTo(ncStream,"variant A B prefix_bits square_bits common_binary_line\n");
ncSummary:=[];; ncTotal:=0;; ncControls:=0;; ncRoots:=0;;
for ncVariant in [1..Length(commutatorBlockWords)] do
  ncRows:=commutatorBlockWords[ncVariant];;
  if ncEval(Last(ncRows),ncLetters,ncFreeOne,ncFreeZero)<>ncRoot then
    Error("wrong free root");
  fi;
  ncRoots:=ncRoots+1;
  ncCounts:=rec(zero:=0,identity:=0,other:=0,square_zero:=0,square_identity:=0,
                common_line:=0,flag_mismatch:=0);;
  for ncAi in [1..16] do
    for ncBi in [1..16] do
      ncA:=ncMatrices[ncAi];; ncB:=ncMatrices[ncBi];; ncPrefix:=ncI;;
      for ncRow in ncRows do
        ncL:=ncEval(ncRow,[ncA,ncB],ncI,ncZ);;
        ncPrefix:=ncPrefix*(ncI+ncL);
      od;
      ncSquare:=ncPrefix^2;;
      if not ncSquare in [ncZ,ncI] then Error("noncentral paired prefix"); fi;
      ncF:=(ncI+ncA)*(ncI+ncB);;
      ncMask:=(ncI+ncF)*(ncI+ncA)*(ncI+ncB);;
      if ncPrefix*ncMask^2<>ncZ then Error("nonzero complete source mask"); fi;
      ncLine:=ncHasLine(ncA,ncB);;
      if ncLine then ncCounts.common_line:=ncCounts.common_line+1; fi;
      if (ncSquare=ncI)<>ncLine then ncCounts.flag_mismatch:=ncCounts.flag_mismatch+1; fi;
      if ncPrefix=ncZ then ncCounts.zero:=ncCounts.zero+1;
      elif ncPrefix=ncI then ncCounts.identity:=ncCounts.identity+1;
      else ncCounts.other:=ncCounts.other+1; fi;
      if ncSquare=ncZ then ncCounts.square_zero:=ncCounts.square_zero+1;
      else ncCounts.square_identity:=ncCounts.square_identity+1; fi;
      PrintTo(ncStream,ncVariant," ",ncAi," ",ncBi," ",ncBits(ncPrefix)," ",
              ncBits(ncSquare)," ",ncLine,"\n");
      ncTotal:=ncTotal+1;
    od;
  od;
  if ncCounts.flag_mismatch<>0 then Error("paired prefix differs from common-line indicator"); fi;
  ncA:=[[ncZero,ncOne],[ncOne,ncOne]];; ncB:=ncZ;;
  ncPrefix:=ncI;;
  for ncRow in ncRows do ncPrefix:=ncPrefix*(ncI+ncEval(ncRow,[ncA,ncB],ncI,ncZ)); od;
  ncMask:=(ncI+(ncI+ncA)*(ncI+ncB))*(ncI+ncA)*(ncI+ncB);;
  ncRootOnly:=(ncI+(ncA*ncB+ncB*ncA)^2)*ncMask^2;;
  if ncPrefix<>ncZ or ncRootOnly=ncZ then Error("root-only negative control failed"); fi;
  ncControls:=ncControls+1;
  Add(ncSummary,ncCounts);
od;
CloseStream(ncStream);
if ncTotal<>768 or ncRoots<>3 or ncControls<>3 then Error("incomplete check"); fi;
Print("Formal roots: ",ncRoots,"\nMatrix pairs: ",ncTotal,"\nRoot-only controls: ",ncControls,"\n");
Print("Per-variant prefix counts: ",ncSummary,"\n");
Print("PASS commutativity-square block prefixes\n");
QUIT;
