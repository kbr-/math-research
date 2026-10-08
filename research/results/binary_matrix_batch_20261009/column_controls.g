# Exact local checks for the strengthened PHP images of the rank-CNF encoding.
# General transfer/degree assertions are proved in the accompanying entry.
out := "research/results/binary_matrix_batch_20261009/control-output.txt";
PrintTo(out,"Binary strengthened-column controls; not a degree-lower-bound enumeration.\n");
badAnd := Filtered(Tuples([0,1],3),t -> t[3]<>t[1]*t[2]);
diagChecks := 0; offChecks := 0;
for u in [0,1] do
 t := [u,u,u];
 for b in badAnd do
  if Product(List([1..3],i -> (1+t[i]+b[i]) mod 2))<>0 then Error("diagonal gate"); fi;
  diagChecks := diagChecks+1;
 od;
od;
for uv in [[0,0],[1,0],[0,1]] do
 t := [uv[1],uv[2],0];
 for b in badAnd do
  if Product(List([1..3],i -> (1+t[i]+b[i]) mod 2))<>0 then Error("offdiagonal gate"); fi;
  offChecks := offChecks+1;
 od;
od;
# Negative control: collision 11 makes exactly the forbidden 110 row violate a clause.
t := [1,1,0];
if Sum(List(badAnd,b -> Product(List([1..3],i -> (1+t[i]+b[i]) mod 2))))<>1 then
 Error("collision negative control");
fi;
states := [[0,0,0],[1,0,0],[0,1,0],[0,0,1]];
compChecks := 0; fieldChecks := 0;
for x in states do
 pref := (1+Sum(List(x,a -> a*a))) mod 2;
 for i in [1..3] do
  if (x[i]*pref) mod 2 <>0 then Error("column companion"); fi;
  if (x[i]*x[i]+x[i]) mod 2 <>0 then Error("coefficient field"); fi;
  compChecks := compChecks+1; fieldChecks := fieldChecks+1;
 od;
od;
AppendTo(out,"diagonal_gate_clause_checks=",diagChecks,
 "\noffdiagonal_gate_clause_checks=",offChecks,
 "\ncollision_negative_controls=1\ncolumn_companion_checks=",compChecks,
 "\ncoefficient_field_checks=",fieldChecks,"\nALL_CHECKS_PASSED\n");
Print("Saved full controls to ",out,"\n");
QUIT_GAP(0);
