# Two complete accuracy-one blocks on (1,x) and (1,y), all constant coefficients.
# Direct-sum kernels over all 16 independent parameter pairs, old cutoffs K=0,1,2.
# Evaluate exact native ranks; assert aggregate intermediate and full-degree controls.
ff := GF(2);; bits := Elements(ff);; pts := Tuples(bits,2);; rows := Tuples(bits,2);;
mons := [[],[1],[2],[1,2]];;
EvalMon := function(s,x) return One(ff)*Product(List(s,j->x[j])); end;;
EvalRow := function(c,x,j) return One(ff)+c[1]+c[2]*x[j]; end;;
KernelDim := function(support,k)
  local basis, mat;
  basis := Filtered(mons,s->Length(s)<=k);
  if Length(support)=0 then return Length(basis); fi;
  mat := List(support,x->List(basis,s->EvalMon(s,x)));
  return Length(basis)-RankMat(mat);
end;;
out := OutputTextFile("research/results/binary_coefficient_locality_20261009/check.txt",false);;
SetPrintFormattingStatus(out,false);
PrintTo(out,"Complete constant-coefficient grids; n=2,r=1,h=1; 16 parameter pairs.\n");
checks := 0;;
for kk in [0..2] do
  ambient := 16*Length(Filtered(mons,s->Length(s)<=kk));
  singleA := 0; singleB := 0; joint := 0;
  for c in rows do
    for d in rows do
      suppA := Filtered(pts,x->EvalRow(c,x,1)=One(ff));
      suppB := Filtered(pts,x->EvalRow(d,x,2)=One(ff));
      singleA := singleA+KernelDim(suppA,kk);
      singleB := singleB+KernelDim(suppB,kk);
      joint := joint+KernelDim(Union(suppA,suppB),kk);
      checks := checks+1;
    od;
  od;
  if singleA<>singleB then Error("asymmetry"); fi;
  if kk=1 and [ambient,singleA,joint]<>[48,20,7] then Error("truncated prediction failed"); fi;
  if kk=2 and joint*ambient<>singleA*singleB then Error("full-degree independence failed"); fi;
  PrintTo(out,"K=",kk,": ambient=",ambient,"; kernels=",singleA,",",singleB,
    "; joint=",joint,"; R_joint=",joint/ambient,
    "; product_R=",singleA*singleB/ambient^2,"\n");
od;
PrintTo(out,"PASS; exact row-pair/cutoff cases=",checks,"\n");
CloseStream(out);
QUIT;
