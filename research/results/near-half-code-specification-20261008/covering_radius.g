# Verify the short-representative Boolean certificate on a fixed q=5, v=6 code.
# Exactly 5^6=15625 vectors determine all 125 coset leaders. One shared native
# 125x125 finite-field matrix inverse supplies every Fourier coefficient.
# This checks the proposed polynomial identities, not an asymptotic degree bound.
CovWeight:=a->Number(a,x->not IsZero(x));
CovKey:=function(a,q) local t,i; t:=0; for i in [1..Length(a)] do t:=t+IntFFE(a[i])*q^(i-1);od;return t+1;end;
CovBit:=function(a,i) return RemInt(QuoInt(a,2^(i-1)),2);end;
CovMain:=function()
 local q,n,F,E,z,H,A,r,k,Ht,At,elems,words,reps,dist,a,key,c,synd,b,image,
 x0,L,params,points,chars,invchars,vals,coef,j,s,d,shift,phase,lambda,rel,
 polys,supports,mask,S,factors,p,combined,relations,pointChecks,negative,
 firstNonzero,rad,degree,rankpoly,out,coeffs,zero,one,g,shifts,phases;
 q:=5;n:=6;F:=GF(q);E:=GF(16);z:=Z(16)^3;
 if Order(z)<>q then Error("root order");fi;
 H:=List([[1,1,1,1,1,0],[0,1,2,3,4,0],[0,1,4,4,1,1]],row->row*One(F));
 Ht:=TransposedMat(H);A:=NullspaceMat(Ht);At:=TransposedMat(A);
 r:=RankMat(A);k:=n-r;
 if r<>3 or RankMat(H)<>3 then Error("code rank");fi;
 elems:=Elements(F);words:=Tuples(elems,n);
 reps:=List([1..q^k],i->fail);dist:=List([1..q^k],i->n+1);
 for a in words do
  key:=CovKey(a*Ht,q);
  if CovWeight(a)<dist[key] then dist[key]:=CovWeight(a);reps[key]:=a;fi;
 od;
 rad:=Maximum(dist);
 if rad<>2 or ForAny(reps,a->a=fail) then Error("covering-radius calibration");fi;
 image:=Set(List([0..2^n-1],mask->List([1..n],i->CovBit(mask,i)*One(F))*At));
 b:=First(Tuples(elems,r),synd->not synd in image);
 if b=fail then Error("no Boolean-empty syndrome");fi;
 x0:=SolutionMat(At,b);
 L:=List(Tuples(elems,k),params->x0+params*H);
 if Length(Set(L))<>q^k or not ForAll(L,a->a*At=b) then Error("affine coset");fi;
 if ForAny(L,a->ForAll(a,x->x in [Zero(F),One(F)])) then Error("Boolean point");fi;
 chars:=List(reps,a->List(L,x->z^IntFFE(a*x)));
 if RankMat(chars)<>q^k then Error("character basis");fi;
 invchars:=Inverse(chars);
 vals:=List([1..n],j->List([1..q^k],i->Zero(E)));
 for c in [1..q^k] do
  j:=First([1..n],j->not IsZero(z^(2*IntFFE(L[c][j]))-(One(E)+z)*z^IntFFE(L[c][j])+z));
  if j=fail then Error("missing violated Boolean coordinate");fi;
  g:=z^(2*IntFFE(L[c][j]))-(One(E)+z)*z^IntFFE(L[c][j])+z;
  vals[j][c]:=g^-1;
 od;
 coeffs:=List(vals,row->row*invchars);
 if not ForAll([1..n],j->coeffs[j]*chars=vals[j]) then Error("Fourier expansion");fi;
 supports:=List([0..2^n-1],mask->Filtered([1..n],i->CovBit(mask,i)=1));
 polys:=[];
 for a in reps do
  factors:=List(a,x->z^IntFFE(x)-One(E));
  p:=List(supports,S->Product(List(S,i->factors[i]),One(E)));
  Add(polys,p);
 od;
 rankpoly:=RankMat(polys);
 shifts:=List([1..n],j->[]);phases:=List([1..n],j->[]);
 relations:=0;pointChecks:=0;negative:=0;
 combined:=List([1..2^n],i->Zero(E));firstNonzero:=fail;
 for j in [1..n] do
  for c in [1..q^k] do
   shift:=[];phase:=[];
   for s in [1,2] do
    a:=ShallowCopy(reps[c]);a[j]:=a[j]+s*One(F);
    key:=CovKey(a*Ht,q);d:=a-reps[key];
    lambda:=SolutionMat(A,d);
    if lambda=fail or lambda*A<>d then Error("row-space transport");fi;
    if CovWeight(a)>rad+1 or CovWeight(d)>2*rad+1 then Error("support budget");fi;
    Add(shift,key);Add(phase,z^IntFFE(lambda*b));
    if not ForAll([1..q^k],i->chars[c][i]*z^(s*IntFFE(L[i][j]))=phase[s]*chars[key][i]) then Error("transport phase");fi;
    pointChecks:=pointChecks+q^k;relations:=relations+1;
    if chars[c][1]*z^(s*IntFFE(L[1][j]))=z*phase[s]*chars[key][1] then Error("phase negative control");fi;
    negative:=negative+1;
   od;
   rel:=phase[2]*polys[shift[2]]-(One(E)+z)*phase[1]*polys[shift[1]]+z*polys[c];
   combined:=combined+coeffs[j][c]*rel;
   if firstNonzero=fail and not IsZero(coeffs[j][c]) and not IsZero(rel) then firstNonzero:=coeffs[j][c]*rel;fi;
   Add(shifts[j],shift);Add(phases[j],phase);
  od;
 od;
 one:=Concatenation([One(E)],List([1..2^n-1],i->Zero(E)));
 if combined<>one then Error("literal polynomial partition is not one");fi;
 if firstNonzero=fail or combined-firstNonzero=one then Error("omitted-term negative control");fi;
 out:="research/results/near-half-code-specification-20261008/covering-certificate.g";
 PrintTo(out,"# Complete exact certificate data; regenerate with covering_radius.g\n");
 AppendTo(out,"CovA := ",A,";\nCovB := ",b,";\nCovH := ",H,";\nCovRepresentatives := ",reps,";\nCovDistances := ",dist,";\nCovCoefficients := ",coeffs,";\nCovShifts := ",shifts,";\nCovPhases := ",phases,";\nCovLiteralSum := ",combined,";\n");
 Print("q=",q," v=",n," rank=",r," quotient_dimension=",k," vectors=",Length(words)," classes=",Length(reps)," radius=",rad,"\n");
 Print("leader_weight_counts=",List([0..rad],j->Number(dist,x->x=j))," Boolean_image_size=",Length(image)," character_rank=",RankMat(chars)," representative_polynomial_rank=",rankpoly,"\n");
 Print("transport_relations=",relations," phase_point_checks=",pointChecks," perturbed_phase_rejections=",negative," omitted_term_rejection=PASS\n");
 Print("PASS: full short-representative certificate is literally one over F16; no PC degree minimum computed\n");
end;
CovMain();
QUIT;
