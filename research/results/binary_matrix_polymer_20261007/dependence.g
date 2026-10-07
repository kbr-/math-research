# Exact degree-truncation dependence of two disjoint cubic conjunctions on six bits.
# Three support matrices, at most 15x64, one echelon per matrix supplies all cutoffs.
# K=3: each rank8 in dimension42, joint rank15, conditional loss7/34>4/21.
# K=6: full tensor-algebra independence is restored.
F:=GF(2);; o:=One(F);; zero:=Zero(F);;
n:=6;; r:=3;;
mons:=Concatenation(List([0..n],j->Combinations([1..n],j)));;
points:=Tuples([zero,o],n);;
supports:=[Filtered(points,p->Product(p{[1..r]})=o),
 Filtered(points,p->Product(p{[r+1..n]})=o)];;
Add(supports,Union(supports[1],supports[2]));;
if List(supports,Length)<>[8,8,15] then Error("Sizing/support guard"); fi;
rankprofiles:=[];;
for pts in supports do
 mat:=List(pts,p->List(mons,S->Product(List(S,j->p[j]),o)));;
 ech:=TriangulizedMat(mat);;
 piv:=List(Filtered(ech,row->ForAny(row,a->a<>zero)),row->PositionProperty(row,a->a<>zero));;
 Add(rankprofiles,List([0..n],K->Number(piv,j->j<=Sum([0..K],d->Binomial(n,d)))));
od;
count:=function(m,K) return Sum([0..Minimum(m,K)],j->Binomial(m,j)); end;;
for K in [0..n] do
 h:=count(n,K);; single:=count(n-r,K);; both:=2*single-count(n-2*r,K);;
 if List(rankprofiles,row->row[K+1])<>[single,single,both] then Error("Rank formula"); fi;
 good:=1-single/h;; joint:=1-both/h;;
 if K>0 and K<n and not joint<good^2 then Error("Strict dependence"); fi;
 if K=n and joint<>good^2 then Error("Full-degree control"); fi;
 Print("K=",K," h=",h," single_error_rank=",single," stacked_rank=",both,
 " common_kernel=",h-both," relative_joint=",joint," product=",good^2,"\n");
 if K=3 then
  conditional:=(both-single)/(h-single);;
  if conditional<>7/34 or single/h<>4/21 then Error("Nonvacuous prediction"); fi;
  Print("conditional_error_fraction=",conditional," initial_error_fraction=",single/h,"\n");
 fi;
od;
Print("PASS: 21 exact prefix ranks, strict intermediate dependence, full-degree independence.\n");
QUIT;
