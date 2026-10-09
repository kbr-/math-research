# Exhaustive local validation of the changed paired source encoding.
# h=1,2,3 and q=3,5; all uniform pair weights (including zero) and signs.
# Exact fixed-assignment density; nonzero rows additionally check every
# retained coordinate set and every pin in either selected variable part.
# This validates local rules, not the asymptotic UNSAT/core theorem.
RunPaired := function()
local out,q,h,k,points,masks,weights,signs,a,eps,coeff,b,allowed,accept,
 p,idx,j,residual,lhs,expected,rows,projectionCount,Y,side,selected,
 pin,full,projected,allowedProj,sideSet,nonzeroRows,totalRows,totalProj;
 out:="research/results/near-half-balanced-paired-source-20261009/local_control_output.txt";
 PrintTo(out,"Paired central source law and projection controls.\n");
 totalRows:=0;totalProj:=0;
 for q in [3,5] do for h in [1,2,3] do
  k:=2*h;points:=Tuples([0,1],k);
  masks:=Concatenation(List([0..k],j->Combinations([1..k],j)));
  weights:=Tuples([0..q-1],h);signs:=Tuples([-1,1],h);
  accept:=List(points,p->0);rows:=0;projectionCount:=0;nonzeroRows:=0;
  for a in weights do for eps in signs do
   rows:=rows+1;coeff:=Concatenation(a,List([1..h],j->eps[j]*a[j]));
   b:=(QuoInt(q+1,2)*Sum(coeff)) mod q;allowed:=[];
   for idx in [1..Length(points)] do
    p:=points[idx];lhs:=(Sum([1..k],j->coeff[j]*p[j])-b) mod q;
    residual:=Sum([1..h],j->a[j]*(p[j]+eps[j]*p[h+j]-QuoInt(1+eps[j],2))) mod q;
    if lhs<>residual then Error("paired residual identity");fi;
    if lhs=0 then Add(allowed,idx);accept[idx]:=accept[idx]+1;fi;
   od;
   AppendTo(out,"q=",q," h=",h," a=",a," signs=",eps," allowed point indices=",allowed,"\n");
   if ForAll(a,t->t<>0) then
    nonzeroRows:=nonzeroRows+1;
    for Y in masks do
     allowedProj:=Set(allowed,i->points[i]{Y});
     for side in [0,1] do
      sideSet:=[1+side*h..h+side*h];selected:=Intersection(Y,sideSet);
      for pin in Tuples([0,1],Length(selected)) do
       full:=List([1..k],j->0);
       for j in [1..Length(selected)] do full[selected[j]]:=pin[j];od;
       for j in [1..h] do
        if side=0 then
         if eps[j]=1 then full[h+j]:=1-full[j];else full[h+j]:=full[j];fi;
        else
         if eps[j]=1 then full[j]:=1-full[h+j];else full[j]:=full[h+j];fi;
        fi;
       od;
       if full{selected}<>pin then Error("selected coordinates changed");fi;
       if not full{Y} in allowedProj then Error("projected affine completion");fi;
       projectionCount:=projectionCount+1;
      od;
     od;
    od;
   fi;
  od;od;
  expected:=q^h+(2^h-1)*q^(h-1);
  if not ForAll(accept,c->c=expected) then Error("fixed assignment density");fi;
  AppendTo(out,"SUMMARY q=",q," h=",h," rows=",rows," nonzero rows=",nonzeroRows," assignments=",Length(points)," accepted parameter choices per assignment=",expected," of ",q^h*2^h," projection completions=",projectionCount,"\n");
  totalRows:=totalRows+rows;totalProj:=totalProj+projectionCount;
  Print("Completed q=",q," h=",h," rows=",rows," projections=",projectionCount,"\n");
 od;od;
 AppendTo(out,"PASS total rows=",totalRows," projected affine completions=",totalProj,"\n");
end;
RunPaired();
QUIT;
