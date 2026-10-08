# Exact expectation check for paths to nonzero row-space targets.
# Fixed two-row ternary coset; all 9 intermediate choices, four scaled
# pivot targets and five states per path. This is not an asymptotic test.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
rows:=[[1,0,1],[0,1,1]];; sums:=[];; states:=0;; active:=[];; coeff:=[];;
for target in [[1,0],[2,0],[0,1],[0,2]] do
 totals:=[0,0,0,0,0];
 for middle in Tuples([0,1,2],2) do
  path:=[[0,0],[middle[1],0],middle,[target[1],middle[2]],target];
  widths:=[];
  for pos in [1..5] do
   coeff:=path[pos];
   word:=List([1..3],j->Sum([1..2],i->coeff[i]*rows[i][j]) mod 3);
   width:=Number(word,a->a<>0); Add(widths,width);
   totals[pos]:=totals[pos]+width; states:=states+1;
  od;
  PrintTo(out,"target ",target," middle ",middle," widths ",widths,"\n");
 od;
 if not ForAll(totals,a->a<=24) then Error("nonzero-target expectation bound failed"); fi;
 Add(sums,totals);
od;
PrintTo(out,"SUMMARY states=",states," targets=4 random_choices=9 summed_widths=",sums,
 " bound_per_position=24\nPASS\n");
CloseStream(out); Print("PASS; exact output at ",OUT,"\n"); QUIT;
