# Exhaustive rule check for the extracted coupled Boolean row construction.
# k=1 checks the two-row triple; k=2 checks the sum-of-products cross terms.
field := GF(2);; one := One(field);; zero := Zero(field);;
bb := [];; ee := [];; ff := [];;
total := 0;; negative := 0;;
for k in [1,2] do
  count := 0;
  for bits in Tuples([zero,one],1+3*k) do
    aa := bits[1]; bb := bits{[2..k+1]};
    ee := bits{[k+2..2*k+1]}; ff := bits{[2*k+2..3*k+1]};
    cc := Sum([1..k],i->ee[i]*ff[i]);
    qq := List([1..k],i->ee[i]*aa+bb[i]);
    qzero := (one+Sum(ee))*aa+Sum([1..k],i->(one+ff[i])*bb[i])+cc;
    if qzero+Sum([1..k],i->(one+ff[i])*qq[i])<>aa+cc+aa*cc then Error("triangular identity"); fi;
    prefix := (one+qzero)*Product(qq,q->one+q);
    target := (one+aa)*(one+cc)*Product(bb,b->one+b);
    if prefix<>target then Error("zero indicator"); fi;
    if ForAny(Concatenation([aa],bb,[cc]),g->g*prefix<>zero) then Error("companion"); fi;
    wrong := (one+qzero+Sum(ee)*aa)*Product(qq,q->one+q);
    if wrong<>target then negative := negative+1; fi;
    count := count+1; total := total+1;
    Print("k=",k," values=",List(bits,Int)," rows=",List(Concatenation([qzero],qq),Int),
          " prefix=",Int(prefix)," target=",Int(target),"\n");
  od;
  Print("Completed k=",k,": ",count," assignments\n");
od;
if total<>144 or negative=0 then Error("coverage or negative control"); fi;
Print("PASS: ",total," coupled-row assignments; omitted-term failures: ",negative,"\n");
QUIT;
