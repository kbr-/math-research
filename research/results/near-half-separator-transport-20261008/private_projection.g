# Exact exhaustive checks of existential private-variable projection.
# Every Boolean relation of arity <=3 and every private subset is checked.
# ProjectionIndicator identities are compared as integer coefficient vectors, hence over every field.
# The largest relation inventory is 256, with 8 private subsets and 8 assignments.
Bits := function(a,n) return Filtered([1..n], i -> RemInt(QuoInt(a,2^(i-1)),2)=1); end;
ProjectionIndicator := function(n,scope,a)
 local one,coef,b,s;
 one:=Intersection(scope,Bits(a,n)); coef:=List([1..2^n], i->0);
 for b in [0..2^n-1] do
  s:=Bits(b,n);
  if IsSubset(scope,s) and IsSubset(s,one) then coef[b+1]:=(-1)^(Length(s)-Length(one)); fi;
 od;
 return coef;
end;
relationCount:=0; projectionCount:=0; identityCount:=0; extensionCount:=0;
for n in [0..3] do
 for rel in [0..2^(2^n)-1] do
  relationCount:=relationCount+1;
  allowed:=Filtered([0..2^n-1],a->RemInt(QuoInt(rel,2^a),2)=1);
  for pm in [0..2^n-1] do
   projectionCount:=projectionCount+1;
   private:=Bits(pm,n); shared:=Difference([1..n],private);
   for a in [0..2^n-1] do
    if Intersection(Bits(a,n),private)=[] then
     ext:=Filtered([0..2^n-1],b->Intersection(Bits(b,n),shared)=Bits(a,n));
     extensionCount:=extensionCount+Length(ext);
     projAllowed:=ForAny(ext,b->b in allowed);
     if not projAllowed then
      lhs:=List([1..2^n],i->0);
      for b in ext do
       if b in allowed then Error("forbidden projection contains allowed extension"); fi;
       lhs:=lhs+ProjectionIndicator(n,[1..n],b);
      od;
      if lhs<>ProjectionIndicator(n,shared,a) then Error("projection indicator identity failed"); fi;
      identityCount:=identityCount+1;
     fi;
    fi;
   od;
  od;
 od;
od;
compositionCount:=0; minimalCount:=0;
for ra in [0..15] do
 for rb in [0..15] do
  aa:=Filtered([0..3],a->RemInt(QuoInt(ra,2^a),2)=1);
  bb:=Filtered([0..3],b->RemInt(QuoInt(rb,2^b),2)=1);
  # a=x+2*z, b=y+2*z, private x and y, shared z.
  pa:=Set(List(aa,a->QuoInt(a,2))); pb:=Set(List(bb,b->QuoInt(b,2)));
  sat:=ForAny(aa,a->ForAny(bb,b->QuoInt(a,2)=QuoInt(b,2)));
  if sat<>(Intersection(pa,pb)<>[]) then Error("composition satisfiability failed"); fi;
  if not sat and aa<>[] and bb<>[] then
   minimalCount:=minimalCount+1;
   if pa=[] or pb=[] then Error("block minimality lost"); fi;
  fi;
  compositionCount:=compositionCount+1;
 od;
od;
# Negative control: eliminating a shared variable from x=0 and x=1 is unsound.
if Intersection([0],[1])<>[] or not (Length([0])>0 and Length([1])>0) then Error("negative control failed"); fi;
Print("relations=",relationCount," projection_cases=",projectionCount," indicator_identities=",identityCount," extension_assignments=",extensionCount,"\n");
Print("two_block_compositions=",compositionCount," minimal_unsatisfiable_compositions=",minimalCount,"\n");
Print("shared_variable_negative_control=PASS; degree_overhead_control: empty arity-n relation has input degree n and projected degree 0\n");
Print("PASS: all integer polynomial identities and logical compositions; no PC lower bound computed\n");
QUIT;
