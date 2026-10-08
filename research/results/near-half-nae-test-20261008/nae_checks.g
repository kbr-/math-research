# Exact ordinary-PC identities, not a truncated Groebner degree estimate.
# All 25 width-two resolution patterns on a pivot and two other variables;
# all eight branches on a Fano line, with every derived clause verified.
# Fano has seven variables and an independent four-set; the predicted degree
# ceiling is six, strictly below the variable count. Enumerations are bounded.
if not IsBound(OUT) then Error("Set OUT"); fi;
out:=OutputTextFile(OUT,false);; SetPrintFormattingStatus(out,false);;
Check:=function(ok,msg) if not ok then Error(msg); fi; end;;
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0; fi;
 e:=ExtRepPolynomialRatFun(p); d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]})); od;
 return d;
end;;
vars:=[];; one:=0;; ring:=0;;
FalseLit:=function(l) if l>0 then return one-vars[l]; else return vars[-l]; fi; end;;
ClausePoly:=function(c) return one*Product(c,FalseLit); end;;
Taut:=function(c) return ForAny(c,l->-l in c); end;;
Resolve:=function(a,b,j,weight,cap)
 local aa,bb,ra,rb,r,product,p1,p2,correction,t;
 Check(j in a and -j in b,"resolution pivot");
 aa:=Difference(a,[j]); bb:=Difference(b,[-j]);
 Check(Length(aa)<=1 and Length(bb)<=1,"not width two");
 ra:=ClausePoly(aa); rb:=ClausePoly(bb);
 p1:=rb*weight*ClausePoly(a); p2:=ra*weight*ClausePoly(b);
 product:=weight*ra*rb;
 Check(IsZero(p1+p2-product),"literal resolution identity");
 Check(Maximum(Deg(p1),Deg(p2))<=cap,"resolution degree");
 r:=Set(Concatenation(aa,bb));
 if Taut(r) then
  t:=AbsInt(r[1]); correction:=-weight*(vars[t]^2-vars[t]);
  Check(IsZero(product-correction),"tautology correction"); return fail;
 fi;
 if Length(aa)=1 and aa=bb then
  t:=AbsInt(aa[1]); correction:=weight*(vars[t]^2-vars[t]);
 else correction:=Zero(ring); fi;
 Check(IsZero(product-correction-weight*ClausePoly(r)),"duplicate literal correction");
 Check(Deg(correction)<=cap,"Boolean correction degree");
 return r;
end;;
edges:=[[1,2,3],[1,4,5],[1,6,7],[2,4,6],[2,5,7],[3,4,7],[3,5,6]];;
fixed:=[1,2,3];; free:=[4,5,6,7];;
Check(ForAll(edges,e->not IsSubset(free,e)),"independent four-set");;
allpoints:=Tuples([0,1],7);; Check(Length(allpoints)=128,"truth enumeration cap");;
Check(ForAll(allpoints,a->ForAny(edges,e->Length(Set(a{e}))=1)),"Fano unsatisfiability");;
axioms:=Concatenation(edges,List(edges,e->List(e,x->-x)));;
localcases:=0;; branchcount:=0;; liftcount:=0;; resolutions:=0;; controls:=0;; transfercount:=0;;
PrintTo(out,"planned: 4 fields; 25 local resolution patterns and 8 Fano branches per field; 128 truth points\n");;
for fld in [Rationals,GF(2),GF(3),GF(4)] do
 ring:=PolynomialRing(fld,7); vars:=IndeterminatesOfPolynomialRing(ring); one:=One(ring);
 for la in [0,2,-2,3,-3] do for lb in [0,2,-2,3,-3] do
  a:=[1]; b:=[-1]; if la<>0 then Add(a,la); fi; if lb<>0 then Add(b,lb); fi;
  r:=Resolve(Set(a),Set(b),1,one,3); localcases:=localcases+1;
 od; od;
 if Characteristic(fld)=2 then
  x:=vars[1]; y:=vars[2]; z:=vars[3];
  q:=one+x+y+z+x*y+x*z+y*z;
  c0:=(one-x)*(one-y)*(one-z); c1:=x*y*z;
  Check(IsZero(q-c0-c1),"NAE clause sum");
  Check(IsZero(x*q-c1-(x^2-x)*(one+y+z)),"NAE reverse cubic certificate");
  Check(IsZero(q-(one+x+y)*(one+x+z)-(x^2-x)),"NAE affine factorization");
  transfercount:=transfercount+3;
 fi;
 partition:=Zero(ring); first:=fail;
 for alpha in Tuples([0,1],3) do
  weight:=one*Product(fixed,function(i) if alpha[i]=1 then return vars[i]; else return one-vars[i]; fi; end);
  if first=fail then first:=weight; fi; partition:=partition+weight;
  clauses:=[];
  for c in axioms do
   sat:=ForAny(c,l->AbsInt(l) in fixed and ((l>0 and alpha[AbsInt(l)]=1) or (l<0 and alpha[AbsInt(l)]=0)));
   if not sat then
    r:=Filtered(c,l->not AbsInt(l) in fixed); r:=Set(r);
    Check(Length(r)<=2,"residual is not 2-CNF");
    extra:=Difference(fixed,List(c,AbsInt));
    mult:=one*Product(extra,function(i) if alpha[i]=1 then return vars[i]; else return one-vars[i]; fi; end);
    Check(IsZero(ClausePoly(c)*mult-weight*ClausePoly(r)),"literal clause lifting");
    Check(Deg(ClausePoly(c)*mult)<=5,"lifted axiom degree");
    AddSet(clauses,r); liftcount:=liftcount+1;
   fi;
  od;
  count:=0;
  for j in free do
   if [] in clauses then break; fi;
   pos:=Filtered(clauses,c->j in c); neg:=Filtered(clauses,c->-j in c);
   remaining:=Filtered(clauses,c->not j in c and not -j in c);
   for a in pos do
    if [] in remaining then break; fi;
    for b in neg do
     r:=Resolve(a,b,j,weight,6); count:=count+1; resolutions:=resolutions+1;
     PrintTo(out,"resolve field=",fld," branch=",alpha," pivot=",j," parents=",a,";",b," result=",r,"\n");
     if r<>fail then AddSet(remaining,r); fi;
     if [] in remaining then break; fi;
    od;
   od;
   clauses:=remaining;
  od;
  Check([] in clauses,"branch has no derived empty clause");
  branchcount:=branchcount+1;
  PrintTo(out,"branch field=",fld," assignment=",alpha," resolution_steps=",count," degree<=6 PASS\n");
 od;
 Check(IsZero(partition-one),"branch partition");
 Check(not IsZero(partition-first-one),"omitted branch control"); controls:=controls+1;
 # Omitting either parent from a nondegenerate width-two inference must fail.
 a:=[1,2]; b:=[-1,3];
 Check(not IsZero(FalseLit(3)*ClausePoly(a)-FalseLit(2)*FalseLit(3)),"omitted resolution parent control");
 controls:=controls+1;
od;
Check(3*(19/20)^2>5/2,"density slack");;
Check(4*(3/4)^5=243/256 and 243/256<1,"first moment slack");;
Check((19/20)/(2*(49/50))=95/196 and 95/196<1/2,"actual-variable coefficient");;
PrintTo(out,"SUMMARY local_resolution_cases=",localcases," Fano_branches=",branchcount,
 " lifted_axioms=",liftcount," weighted_resolution_steps=",resolutions," negative_controls=",controls,
 " binary_transfer_identities=",transfercount," max_Fano_degree=6\n",
 "exact probability constants: 3*(19/20)^2=",3*(19/20)^2,"; 4*(3/4)^5=243/256; degree_ratio=95/196\nALL CHECKS PASSED\n");;
CloseStream(out);; QUIT;
