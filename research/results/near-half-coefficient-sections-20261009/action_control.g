# Exact degree-two PC witness for three-bit half-integer knapsack, contrasting
# valid truncated actions with invalid global Boolean coefficient actions.
Check:=function(ok,msg) if not ok then Error(msg);fi;end;
mons:=[[],[1],[2],[3],[1,2],[1,3],[2,3]];
Multiply:=function(row,i)
 local out,j,k;
 out:=List(row,x->0*x);
 for j in [1..Length(mons)] do
  if not IsZero(row[j]) then k:=Position(mons,Union(mons[j],[i]));Check(k<>fail,"legal multiplication");out[k]:=out[k]+row[j];fi;
 od;
 return out;
end;
Residual:=function(fld,c)
 local f,base,old,rows,r,i,out,j,submons,unit,piv,counts;
 submons:=[[1,2],[1],[2],[]];f:=[0,1,1,-c]*One(fld);base:=BaseMat([f]);unit:=[0,0,0,1]*One(fld);counts:=0;
 while RankMat(Concatenation(base,[unit]))>Length(base) do
  rows:=ShallowCopy(base);
  for r in base do
   piv:=PositionNonZero(r);
   if Length(submons[piv])<=1 then
    for i in [1..2] do
     out:=List(r,x->Zero(fld));for j in [1..4] do out[Position(submons,Union(submons[j],[i]))]:=out[Position(submons,Union(submons[j],[i]))]+r[j];od;
     Add(rows,out);
    od;
   fi;
  od;
  old:=Length(base);base:=BaseMat(rows);Check(Length(base)>old,"residual must refute");counts:=counts+1;
 od;
 return counts;
end;
Print("SIZING three fields, seven monomials and three state coordinates; six residual spaces of dimension four\n");
actions:=0;kernels:=0;residuals:=0;
for fld in [Rationals,GF(5),GF(7)] do
 one:=One(fld);
 images:=[[1,0,0],[3/2,-1,-1],[0,1,0],[0,0,1],[3/8,0,-1/2],[3/8,-1/2,0],[-3/8,1/2,1/2]]*one;
 tx:=[[3/2,-1,-1],[3/8,0,-1/2],[3/8,-1/2,0]]*one;
 ty:=[[0,1,0],[0,1,0],[-3/8,1/2,1/2]]*one;
 tz:=[[0,0,1],[-3/8,1/2,1/2],[0,0,1]]*one;
 ops:=[tx,ty,tz];e:=images[1];Check(RankMat(images)=3,"proper image dimension");
 for j in [1..4] do for i in [1..3] do
  Check(images[j]*ops[i]=images[Position(mons,Union(mons[j],[i]))],"all legal action identities");actions:=actions+1;
 od;od;
 f:=[-3/2,1,1,1,0,0,0]*one;
 rows:=Concatenation([f],List([1..3],i->Multiply(f,i)));
 Check(RankMat(rows)=4 and rows*images=NullMat(4,3,fld),"full kernel from input and legal multiples");kernels:=kernels+1;
 Check(e*(tx^2-tx)=0*e,"Booleanity valid on unit");
 Check(images[3]*(tx^2-tx)=[0,-1/8,1/8]*one,"global Booleanity failure on degree-one state");
 for i in [1..3] do for j in [1..3] do Check(e*(ops[i]*ops[j]-ops[j]*ops[i])=0*e,"legal commutation on unit");od;od;
 for a in [0,1] do
  rounds:=Residual(fld,(3/2-a)*one);residuals:=residuals+1;
  Print("FIELD=",fld," PIN=",a," RESIDUAL_UNIT_ROUNDS=",rounds,"\n");
 od;
od;
# Characteristic three violates unsatisfiability: all-zero assignment solves it.
Check((3/2)*One(GF(3))=Zero(GF(3)),"excluded characteristic negative control");
Print("LEGAL_ACTIONS=",actions," EXACT_KERNELS=",kernels," RESIDUAL_REFUTATIONS=",residuals,"\n");
Print("ALL FILTERED ACTION CONTROLS PASSED\n");
QUIT;
