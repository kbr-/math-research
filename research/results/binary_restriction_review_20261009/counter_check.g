# All 8192 Boolean assignments to two old/new one-hot3 counters and one input.
# Verify the fixed local Boolean implication used in the counter-depth control.
out:=OutputTextFile("research/results/binary_restriction_review_20261009/counter-checks.txt",false);;
SetPrintFormattingStatus(out,false);;
onehot:=a->Sum(a)=1;;
step:=function(a,b,x)
local s,j;
if not onehot(a) or not onehot(b) then return false;fi;
for s in [1..3] do
 j:=((s-1+x) mod 3)+1;
 if a[s]=1 and b[j]<>1 then return false;fi;
od;
return true;
end;;
rows:=Tuples([0,1],13);;
checks:=0;;hyp:=0;;bad:=0;;negative:=0;;
for v in rows do
 a:=v{[1..3]};; b:=v{[4..6]};; aa:=v{[7..9]};; bb:=v{[10..12]};; x:=v[13];;
checks:=checks+1;
 if step(a,aa,x) and step(b,bb,x) then
  if a=b then hyp:=hyp+1;if aa<>bb then bad:=bad+1;fi;
  elif aa<>bb then negative:=negative+1;fi;
 fi;
od;
AppendTo(out,"assignments=",checks,"; premise_models=",hyp,"; violations=",bad,"; omitted_equality_failures=",negative,"\n");
if checks=8192 and hyp=6 and bad=0 and negative=12 then AppendTo(out,"PASS\n");else AppendTo(out,"FAIL\n");fi;
CloseStream(out);
QUIT;
