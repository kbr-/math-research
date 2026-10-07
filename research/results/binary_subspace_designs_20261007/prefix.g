# Exact filtered-prefix control: F2 Boolean 3-cube, w=1,g=x,K=1,t=2,d=1.
# Satisfiable Boolean algebra, not a Frege lower-bound test. Enumerate 64 matrices.
F:=GF(2);; z:=Zero(F);; o:=One(F);;
bit:=function(b) if b then return 1; else return 0; fi; end;;
pts:=Tuples([z,o],3);; matrices:=Tuples([z,o],6);;
if Length(matrices)<>64 then Error("Enumeration guard"); fi;
mons:=List([0..7],m->Filtered([1..3],i->QuoInt(m,2^(i-1)) mod 2=1));;
Sort(mons,function(a,b)
 if Length(a)<>Length(b) then return Length(a)<Length(b); fi;
 return List([1..3],i->bit(i in a)) < List([1..3],i->bit(i in b));
end);;
W:=List(mons,T->Concatenation(List(mons,S->
 List([1..3],i->bit(Set(Concatenation(T,[i]))=S)*o))));;
# One reverse echelon gives all intersection dimensions with the coefficient flag.
ech:=SemiEchelonMat(List(W,Reversed));;
piv:=Filtered([1..24],j->ech.heads[j]<>0);;
profile:=List([1..8],j->Number(piv,p->QuoInt(24-p,3)+1=j));;
beta:=Sum(profile,r->Minimum(r,(2^r-1)/4));;
domain:=Concatenation([List(pts,x->o)],List([1..3],i->List(pts,x->x[i])));;
counts:=[0,0,0,0,0];; actualsum:=0;;
C:=[];; P:=[];;
for bits in matrices do
 C:=[bits{[1..3]},bits{[4..6]}];;
 P:=List(pts,x->Product(C,row->o+row*x));;
 Err:=List(domain,f->Concatenation(List([1..3],i->
 List([1..8],j->f[j]*P[j]*pts[j][i]))));;
 r:=RankMat(Err);; counts[r+1]:=counts[r+1]+1;; actualsum:=actualsum+r;;
 Print("C=",List(bits,Int)," coefficient_rank=",RankMat(C)," error_rank=",r,"\n");
od;
Print("profile=",profile," beta=",beta," h=4 counts_r0_to_r4=",counts,
 " average_error=",actualsum/64,"\n");
if SortedList(profile)<>[0,0,0,0,1,1,2,3] or beta<>3 or
 counts<>[0,42,0,21,1] or actualsum/64<>109/64 then Error("Prediction failed"); fi;
Print("PASS: exact ranks, profile, strict common-kernel bound.\n");
QUIT;
