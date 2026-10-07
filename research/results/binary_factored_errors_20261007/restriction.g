# Exact image checker for ternary vertex restrictions and positive-accuracy
# binary ENS constant specializations. Local degree3 controls only; no graph
# degree barrier or arbitrary-source claim is inferred from enumeration.
labels := Tuples([0,1,2],3);
signs := Tuples([1,-1],3);
masks := Combinations([1,2,3]);
total := 0; nonzero := 0; zeros := 0;
for sig in signs do
 for charge in [0,1,2] do
  for mask in masks do
   keep := Difference([1,2,3],mask);
   for vals in Tuples([0,1,2],Length(mask)) do
    residual := (charge-Sum([1..Length(mask)],j->sig[mask[j]]*vals[j])) mod 3;
    for lab in labels do
     if Sum([1..3],j->sig[j]*lab[j]) mod 3 <> charge then
      total := total+1;
      agrees := ForAll([1..Length(mask)],j->lab[mask[j]]=vals[j]);
      if agrees then
       nonzero := nonzero+1;
       if Sum(keep,j->sig[j]*lab[j]) mod 3 = residual then
        Error("nonzero image is not a forbidden residual tuple");
       fi;
      else
       zeros := zeros+1;
      fi;
     fi;
    od;
   od;
  od;
 od;
od;
checks := 0;
for len in [0..3] do
 for vals in Tuples([0,1],len) do
  for h in [1,2] do
   rows := List([1..h],j->List([1..len],i->0));
   pos := Position(vals,1);
   if pos <> fail then rows[1][pos] := 1; fi;
   prod := Product(rows,row->(1-Sum([1..len],i->row[i]*vals[i])) mod 2);
   if not ForAll(vals,v->(v*prod) mod 2=0) then Error("companion survives"); fi;
   if not ForAll(Concatenation(rows),r->r*r-r=0) then Error("domain"); fi;
   checks := checks+1;
  od;
 od;
od;
if total<>27648 or nonzero<>3456 or zeros<>24192 or checks<>30 then Error("case counts"); fi;
Print("vertex_images=",total," nonzero_residual_clauses=",nonzero," zero_images=",zeros,"\n");
Print("binary_constant_blocks=",checks," includes empty and zero input tuples; accuracies1,2\n");
Print("PASS local restriction and complete-block images; no graph closure computed\n");
QUIT;
