# Test relative-intersection specialization for every U <= F2^(F2^3\{0}).
# Hypotheses: g_i(y)=y_i; multiplication is coordinatewise. With c=dim U,
# e=rank((L U+U)/U) over F2(lambda), test max gain >= (c-e)/2 and
# mean gain over the seven nonzero legal rows >= (c-e)/2.
# Gain for a is c-rank(U restricted to a.y=0). This is an exact Boolean
# calibration, not an unsatisfiable source or a proof of a universal claim.
# Enumeration has 29212 spaces and at most 233696 tiny native rank calls.
# Extension-field evaluation is exact: every escape minor has size <=3;
# lambda=(1,z,z^4) injects homogeneous monomials of each such degree into
# polynomials of degree <=12, while z has minimal polynomial degree 13.
F:=GF(2);; extField:=GF(2^13);; z:=Z(2^13);;
if Order(z)<>8191 or DegreeOverPrimeField(extField)<>13 then Error("field control"); fi;
bits:=List([1..7],y->List([0..2],i->QuoInt(y,2^i) mod 2));;
values:=List(bits,b->b[1]*One(extField)+b[2]*z+b[3]*z^4);;
zeros:=List(bits,a->Filtered([1..7],j->Sum([1..3],i->a[i]*bits[j][i]) mod 2=0));;
if not ForAll(zeros,h->Length(h)=3) then Error("hyperplane control"); fi;
out:=OutputTextFile("research/results/binary_joint_escape_20261008/spaces.txt",false);;
SetPrintFormattingStatus(out,false);;
AppendTo(out,"basis_bitmasks;generic_escape;gains_for_rows_1_to_7;existence_pass;average_pass\n");
counts:=List([0..7],i->0);; expected:=[1,127,2667,11811,11811,2667,127,1];;
averageFailures:=0;; existenceFailure:=false;; firstAverage:=fail;;
start:=Runtime();;
Print("planned spaces=29212, native ranks at most=233696\n");
for c in [0..7] do
 for piv in Combinations([1..7],c) do
  free:=Difference([1..7],piv);
  positions:=[];
  for i in [1..c] do
   for j in free do
    if j>piv[i] then Add(positions,[i,j]); fi;
   od;
  od;
  for assignment in Tuples([0,1],Length(positions)) do
   B:=NullMat(c,7,F);
   for i in [1..c] do B[i][piv[i]]:=One(F); od;
   for t in [1..Length(positions)] do
    B[positions[t][1]][positions[t][2]]:=assignment[t]*One(F);
   od;
   if c=0 or c=7 then escape:=0;
   else
    escape:=RankMat(List([1..c],i->List(free,j->
      Int(B[i][j])*(values[j]-values[piv[i]]))));
   fi;
   if c=0 then gains:=List([1..7],a->0);
   else gains:=List(zeros,h->c-RankMat(List(B,row->row{h}))); fi;
   masks:=List(B,row->Sum([1..7],j->Int(row[j])*2^(j-1)));
   existsPass:=2*Maximum(gains)>=c-escape;
   averagePass:=2*Sum(gains)>=7*(c-escape);
   AppendTo(out,masks,";",escape,";",gains,";",existsPass,";",averagePass,"\n");
   counts[c+1]:=counts[c+1]+1;
   if not averagePass then
    averageFailures:=averageFailures+1;
    if firstAverage=fail then
     firstAverage:=[masks,escape,gains]; Print("first average failure: ",firstAverage,"\n");
    fi;
   fi;
   if not existsPass then
    existenceFailure:=true;
    Print("existence failure: ",[masks,escape,gains],"\n"); break;
   fi;
  od;
  if existenceFailure then break; fi;
 od;
 Print("dimension ",c,": ",counts[c+1]," tested; elapsed_ms=",Runtime()-start,"\n");
 if existenceFailure then break; fi;
od;
CloseStream(out);
if not existenceFailure and counts<>expected then Error("enumeration count"); fi;
Print("counts=",counts," total=",Sum(counts)," average_failures=",averageFailures,
      " existence_failure=",existenceFailure," elapsed_ms=",Runtime()-start,"\n");
QUIT;
