# Literal ordinary-degree-four certificates for exact star projection.
Deg:=function(p) local e,i,d;
 if IsZero(p) then return 0;fi;e:=ExtRepPolynomialRatFun(p);d:=0;
 for i in [1,3..Length(e)-1] do d:=Maximum(d,Sum(e[i]{[2,4..Length(e[i])]}));od;return d;
end;;
for F in [GF(2),GF(4)] do
 R:=PolynomialRing(F,10);x:=IndeterminatesOfPolynomialRing(R);o:=One(R);
 u:=List([1..4],i->x[2*i-1]);v:=List([1..4],i->x[2*i]);uc:=x[9];vc:=x[10];
 M:=List([1..4],i->[(o+u[i])*(o+v[i]),o+v[i],o+u[i],o]);
 delta:=DeterminantMat(List([1..4],i->[o,u[i],v[i],u[i]*v[i]]));
 if DeterminantMat(M)<>delta then Error("basis determinant");fi;
 cofs:=List([1..4],i->DeterminantMat(List(Filtered([1..4],j->j<>i),j->M[j]{[2..4]})));
 qs:=List([1..4],i->(o+u[i]+uc)*(o+v[i]+vc));
 terms:=List([1..4],i->cofs[i]*qs[i]);
 if not IsZero(Sum(terms)-delta) then Error("literal adjugate certificate");fi;
 if Maximum(List(cofs,Deg))>2 or Maximum(List(terms,Deg))>4 then Error("degree ledger");fi;
 Print("field=",F," coefficients=",cofs," determinant=",delta," max cofactor degree=2 max product degree=4 PASS\n");
od;
Print("ALL ADJUGATE CERTIFICATES PASSED\n");
QUIT;
