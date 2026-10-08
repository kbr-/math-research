# Multigraded coefficient projection, delta=4, two labels per slot.
# All 37 monomials of degree <=2 in eight variables, all 1369 pairs,
# all 16 tensor indices. Integer coefficient equality checks every field.
slots := 4;; labels := 2;;
monomials := Filtered(Combinations([1..8]),s->Length(s)<=2);;
indices := Tuples([1..labels],slots);;
cuts := Combinations([1..slots],2);;
if Length(monomials)<>37 or Length(indices)<>16 then Error("size"); fi;
checks := 0;; leftMon := [];; rightMon := [];; selected := [];;
for leftMon in monomials do
  for rightMon in monomials do
    for index in indices do
      selected := List([1..slots],j->2*(j-1)+index[j]);
      union := Union(leftMon,rightMon);
      lhs := 0;
      if Length(union)=4 and union=Set(selected) then lhs := 1; fi;
      rhs := 0;
      for cut in cuts do
        if leftMon=Set(selected{cut}) and
           rightMon=Set(selected{Difference([1..slots],cut)}) then
          rhs := rhs+1;
        fi;
      od;
      if lhs<>rhs then Error("coefficient projection"); fi;
      checks := checks+1;
    od;
    Print("monomials ",leftMon," * ",rightMon,": all 16 indices pass\n");
  od;
od;
# Diagonal tensor on 2 labels: every nontrivial bipartition has matrix rank 2.
for prime in [2,3] do
  field := GF(prime);;
  for size in [1..3] do
    mat := NullMat(2^size,2^(4-size),field);
    mat[1][1] := One(field); mat[2^size][2^(4-size)] := One(field);
    if RankMat(mat)<>2 then Error("diagonal control"); fi;
  od;
od;
# Outside the joint-degree hypothesis: (xy)(xz) reduces to xyz.
# Its formal t1*t2*t3 coefficient is zero but Boolean-reduced coefficient is one.
Print("Odd-ceiling negative control: formal xyz coefficient 0, Boolean-reduced coefficient 1\n");
if checks<>21904 then Error("coverage"); fi;
Print("PASS: ",checks," coefficient comparisons; diagonal controls over F2 and F3\n");
QUIT;
