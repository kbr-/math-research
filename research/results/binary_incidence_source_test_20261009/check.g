# Exhaust the weighted affine-coefficient quotient over F4 on two Boolean bits.
# Prediction: for every nonzero weight W, legal classes form precisely the
# binary-image set of size 2^r, where all affine images have size 4^r.
# Homogeneous t=0 field solutions must have zero quotient class.
# Scope: finite function-algebra identity check, not hard-quotient evidence.
fld := GF(4);;
elts := Elements(fld);;
bits := [Zero(fld),One(fld)];;
pts := Tuples(bits,2);;
aff := List(Tuples(elts,3),c->List(pts,x->c[1]+c[2]*x[1]+c[3]*x[2]));;
binaff := List(Tuples(bits,3),c->List(pts,x->c[1]+c[2]*x[1]+c[3]*x[2]));;
weights := Tuples(elts,4);;
Mul := function(a,b) return List([1..4],j->a[j]*b[j]); end;;
sq := a->List(a,z->z^2);;
zero := List([1..4],j->Zero(fld));;
hist := [0,0,0];;
weightCount := 0;; fieldChecks := 0;; boundaryChecks := 0;; homogeneousChecks := 0;;
for w in weights do
  if w<>zero then
    weightCount := weightCount+1;
    images := Set(List(aff,a->Mul(w,a)));
    rr := Position([4,16,64],Length(images));
    if rr=fail then Error("bad quotient dimension"); fi;
    hist[rr] := hist[rr]+1;
    legal := Set(List(Filtered(aff,a->Mul(w,sq(a)-a)=zero),a->Mul(w,a)));
    binaryImages := Set(List(binaff,a->Mul(w,a)));
    if legal<>binaryImages or Length(legal)<>2^rr then Error("legal fiber mismatch"); fi;
    fieldChecks := fieldChecks+Length(aff);
    for a in aff do
      if Mul(w,sq(a))=zero and Mul(w,a)<>zero then Error("boundary class survives"); fi;
      boundaryChecks := boundaryChecks+1;
    od;
    for tt in elts do
      fiber := Set(List(Filtered(aff,a->Mul(w,sq(a)-tt*a)=zero),a->Mul(w,a)));
      if tt=Zero(fld) then
        if fiber<>[zero] then Error("nonzero boundary fiber"); fi;
      elif Length(fiber)<>2^rr then Error("homogeneous nonzero fiber mismatch");
      fi;
      homogeneousChecks := homogeneousChecks+Length(aff);
    od;
  fi;
od;
PrintTo("research/results/binary_incidence_source_test_20261009/check.txt",
  "PASS\nfield=F4; old Boolean bits=2; coefficient degree=1; weight degree<=2; D>=4\n",
  "nonzero weights=",weightCount,"\nquotient dimension histogram r=1,2,3: ",hist,"\n",
  "affine maps per weight=",Length(aff),"\nfield comparisons=",fieldChecks,
  "\nboundary comparisons=",boundaryChecks,"\nhomogeneous comparisons=",homogeneousChecks,"\n",
  "Every legal quotient fiber equals its binary representative image.\n");
QUIT;
