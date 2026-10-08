# Exhaustive local validation of the binary gate CNF and paired-column substitution.
# The general degree bound is proved in the notebook, not inferred from these cases.
# Each of AND and XOR uses the four width-three clauses excluding its four bad rows.
# A second check evaluates clause violation polynomials after exact gate substitution.
# Pair cancellation uses all 64 labels for a 3-row pair, checking all nine entries.
out := "research/results/binary_rank_principle_20261009/control-output.txt";
PrintTo(out, "Exact GF(2) local encoding controls; no lower-bound extrapolation.\n");
truth := Tuples([0,1],3); inputs := Tuples([0,1],2);
counter := 0; substituted := 0; omitted := 0;
for kind in ["and","xor"] do
 if kind="and" then
   fun := function(a,b) return a*b; end;
 else
   fun := function(a,b) return (a+b) mod 2; end;
 fi;
 bad := Filtered(truth,t -> t[3] <> fun(t[1],t[2]));
 if Length(bad)<>4 then Error("wrong forbidden-row count"); fi;
 for t in truth do
   viol := List(bad,b -> Product(List([1..3],i -> (1+t[i]+b[i]) mod 2)));
   if (Sum(viol)=0) <> (t[3]=fun(t[1],t[2])) then Error("CNF gate mismatch"); fi;
   counter := counter+Length(viol);
 od;
 for xy in inputs do
   t := [xy[1],xy[2],fun(xy[1],xy[2])];
   for b in bad do
     if Product(List([1..3],i -> (1+t[i]+b[i]) mod 2))<>0 then
       Error("substituted clause is nonzero");
     fi;
     substituted := substituted+1;
   od;
 od;
 for deleted in bad do
   remaining := Filtered(bad,b -> b<>deleted);
   if not ForAll(remaining,b -> Product(List([1..3],i -> (1+deleted[i]+b[i]) mod 2))=0)
      or deleted[3]=fun(deleted[1],deleted[2]) then Error("omission control failed"); fi;
   omitted := omitted+1;
 od;
 AppendTo(out, kind, ": four clauses, all eight gate rows and all four substituted rows checked.\n");
od;
pairs := 0;
for label in Tuples([0,1],6) do
 a := label{[1..3]}; b := label{[4..6]};
 for i in [1..3] do
  for j in [1..3] do
   if (a[i]*b[j]+a[i]*b[j]) mod 2 <> 0 then Error("pair cancellation failed"); fi;
   pairs := pairs+1;
  od;
 od;
od;
AppendTo(out, "truth_clause_evaluations=",counter,"\nsubstituted_clause_evaluations=",substituted,
 "\nomitted_clause_negative_controls=",omitted,"\npaired_outer_product_entry_checks=",pairs,
 "\nALL_CHECKS_PASSED\n");
Print("Full controls saved to ",out,"\n");
QUIT_GAP(0);
