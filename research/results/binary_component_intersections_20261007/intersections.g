# Exact enlarged-intersection formula: 4 codes on 3 disjoint quadratic blocks.
# 64 cube points, 64 monomials, all 7 degree cutoffs; cached prefix echelons.
# Intersection rank = rank(G_L)-rank(CG_L), not rank of the prefix error map.
F:=GF(2);; o:=One(F);; zero:=Zero(F);;
u:=Indeterminate(Rationals,"u");;
m:=3;; r:=2;; v:=m*r;;
if v<>6 then Error("Sizing guard"); fi;
points:=Tuples([zero,o],v);;
monomials:=Concatenation(List([0..v],j->Combinations([1..v],j)));;
vals:=List(points,p->List([1..m],i->Product(p{[(i-1)*r+1..i*r]})));;
cachekeys:=[];; cacheprofiles:=[];;
profile:=function(M)
 local ids,hit,mat,ech,piv;
 ids:=Filtered([1..Length(points)],j->ForAny(M,row->row*vals[j]<>zero));
 hit:=Position(cachekeys,ids);
 if hit<>fail then return cacheprofiles[hit]; fi;
 if Length(ids)=0 then piv:=[]; else
  mat:=List(ids,j->List(monomials,S->Product(List(S,i->points[j][i]),o)));
  ech:=TriangulizedMat(mat);
  piv:=List(Filtered(ech,row->ForAny(row,a->a<>zero)),row->PositionProperty(row,a->a<>zero));
 fi;
 Add(cachekeys,ids);
 Add(cacheprofiles,List([0..v],L->Number(piv,k->k<=Sum([0..L],j->Binomial(v,j)))));
 return cacheprofiles[Length(cacheprofiles)];
end;;
cases:=[ [IdentityMat(m,F),[[1,1,1]]],
 [IdentityMat(m,F),[[1,1,0],[0,1,1]]],
 [IdentityMat(m,F),[[1,0,0],[0,1,0]]],
 [[[1,1,0],[0,1,1]],[[1,1]]] ];;
checks:=0;; H:=(1+u)^r-1-u^r;;
for item in cases do
 A:=List(item[1],row->List(row,x->x*o));;
 C:=List(item[2],row->List(row,x->x*o));; B:=C*A;;
 observed:=profile(A)-profile(B);;
 poly:=Zero(u);;
 for T in Combinations([1..m]) do
  if Length(T)=0 then ar:=0;; cr:=0;; else
   ar:=RankMat(List(A,row->row{T}));; cr:=RankMat(List(B,row->row{T}));;
  fi;
  poly:=poly+H^(m-Length(T))*(u^(r*cr)*(1+u^r)^(Length(T)-cr)
       -u^(r*ar)*(1+u^r)^(Length(T)-ar));
 od;
 co:=CoefficientsOfUnivariatePolynomial(poly);;
 expected:=List([0..v],L->Sum(co{[1..Minimum(L+1,Length(co))]}));;
 if observed<>expected then Error("Intersection formula failed"); fi;
 checks:=checks+7;
 Print("A=",A," C=",C," intersection_prefix_ranks=",observed,"\n");
od;
Print("PASS: ",checks," exact intersection ranks; ",Length(cachekeys),
 " cached support profiles; largest matrix <=64x64.\n");
QUIT;
