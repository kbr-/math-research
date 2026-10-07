# Exact filtered kernels on the charge-zero ternary three-edge star over F4.
# Predict h=[1,7,9], and common kernels [0,4,6], [0,2,4], [0,1,2]
# for one, two and three zero-label errors. One echelon per support, 9x19 max.
F:=GF(4);; om:=Z(4);; zero:=Zero(F);; one:=One(F);;
points:=Filtered(Tuples([0,1,2],3),a->Sum(a) mod 3=0);;
mons:=Filtered(Tuples([0,1,2],3),a->Number(a,t->t<>0)<=2);;
SortBy(mons,a->Number(a,t->t<>0));;
cuts:=List([0..2],k->Number(mons,a->Number(a,t->t<>0)<=k));;
if Length(points)<>9 or cuts<>[1,7,19] then Error("Sizing"); fi;
profile:=function(pts)
 local mat,ech,piv;
 if Length(pts)=0 then return [0,0,0]; fi;
 mat:=List(pts,a->List(mons,b->om^(Sum([1..3],i->a[i]*b[i]) mod 3)));
 ech:=TriangulizedMat(mat);
 piv:=List(Filtered(ech,row->ForAny(row,x->x<>zero)),row->PositionProperty(row,x->x<>zero));
 return List(cuts,c->Number(piv,i->i<=c));
end;;
h:=profile(points);;
if h<>[1,7,9] then Error("Domain"); fi;
Print("domain=",h,"\n");
expected:=[[1,7,9],[0,4,6],[0,2,4],[0,1,2]];;
for S in Combinations([1..3]) do
 forbidden:=Filtered(points,a->ForAny(S,i->a[i]=0));;
 ker:=h-profile(forbidden);;
 if ker<>expected[Length(S)+1] then Error("Kernel profile"); fi;
 Print("S=",S," kernel=",ker,"\n");
od;
z:=1/2;; H:=1+6*z+2*z^2;; single:=4*z+2*z^2;;
pair:=2*z+2*z^2;; triple:=z+z^2;;
conditional:=[(H-single)/H,(single-pair)/single,(pair-triple)/pair];;
if conditional<>[4/9,2/5,1/2] then Error("Weighted activities"); fi;
bound:=H/8;; tail:=2*z^2;;
if not bound>tail then Error("Tail test"); fi;
Print("z=",z," H=",H," conditional=",conditional,
 " bound=",bound," tail_above_degree_one=",tail,"\n");
for a in points do
 fval:=one+Sum(List([1..3],i->(1+om^a[i]+om^(-a[i]))));;
 if (ForAny(a,x->x=0) and fval<>zero) or
    (ForAll(a,x->x<>0) and fval<>one) then Error("Explicit survivor"); fi;
od;
Print("PASS: 24 kernel-prefix dimensions, weighted activities and explicit degree-one survivor.\n");
QUIT;
