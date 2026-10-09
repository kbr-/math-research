# Falsification test, not an asymptotic source sample.
# Hypothesis: a noncentral odd-width modular row with nonzero coefficients
# distinct up to sign has binary interpolation degree <= (n-3)/2.
# Complete signed/permutation orbits at (n,q)=(9,19),(11,23), all noncentral
# targets. These are nonvacuous: allowed sets can exceed the minimum weight
# 2^(n-(n+1)/2) of the dual Reed-Muller code. No larger series is scheduled.
# Native GAP GF(2) packed rank/nullspace is the numerical kernel.
out := "research/results/near-half-central-slice-filtration-20261009/pair_free_output.txt";
PrintTo(out, "Pair-free odd-row interpolation hypothesis; exact GF(2).\n");
F := GF(2); zz := Zero(F); oo := One(F);
Iv := function(b) if b then return oo; else return zz; fi; end;
found := false;
for n in [9,11] do
  q := 2*n+1; d := QuoInt(n-3,2);
  coeff := [1..n];
  if not ForAll(coeff,a->a mod q<>0) then Error("zero coefficient"); fi;
  if not ForAll(Combinations(coeff,2),p->(p[1]-p[2]) mod q<>0 and (p[1]+p[2]) mod q<>0) then Error("pair collision"); fi;
  pts := Tuples([0,1],n);
  ones := List(pts,p->Filtered([1..n],j->p[j]=1));
  mons := Concatenation(List([0..d],j->Combinations([1..n],j)));
  Print("Preparing n=",n," q=",q," points=",Length(pts)," monomials=",Length(mons),"\n");
  mat := List(ones,on->List(mons,m->Iv(IsSubset(on,m))));
  for row in mat do ConvertToVectorRep(row,2); od;
  vals := List(pts,p->Sum([1..n],j->coeff[j]*p[j]) mod q);
  AppendTo(out,"n=",n," q=",q," d=",d," coefficients=",coeff,"\n");
  for b in [0..q-1] do
    if (2*b-Sum(coeff)) mod q<>0 then
      ids := Filtered([1..Length(pts)],i->vals[i]=b);
      if Length(ids)=0 then rk:=0; else rk:=RankMat(mat{ids}); fi;
      AppendTo(out,"target=",b," allowed=",Length(ids)," rank=",rk,"\n");
      if rk<Length(ids) then
        witness := NullspaceMat(mat{ids})[1];
        if not IsZero(witness*mat{ids}) then Error("dual failed"); fi;
        fvals := List([1..Length(pts)],i->zz);
        for j in [1..Length(ids)] do fvals[ids[j]]:=witness[j]; od;
        anf:=ShallowCopy(fvals);
        for bit in List([0..n-1],j->2^j) do
          for mask in [0..2^n-1] do
            if QuoInt(mask,bit) mod 2=1 then anf[mask+1]:=anf[mask+1]+anf[mask-bit+1]; fi;
          od;
        od;
        support:=Filtered([1..Length(pts)],i->fvals[i]<>zz);
        terms:=Filtered([1..Length(pts)],i->anf[i]<>zz);
        deg:=Maximum(List(terms,i->Length(ones[i])));
        if deg>n-d-1 then Error("ANF degree exceeds dual bound"); fi;
        if not ForAll(support,i->vals[i]=b) then Error("support outside row"); fi;
        AppendTo(out,"COUNTEREXAMPLE support=",pts{support},"\nANF monomials=",ones{terms},"\ndegree=",deg,"\n");
        found:=true; break;
      fi;
    fi;
  od;
  # Independent negative control: the weight-floor(n/2) slice is noncentral
  # modulo q>n and does not interpolate through d.
  b:=QuoInt(n,2);
  ids:=Filtered([1..Length(pts)],i->Sum(pts[i])=b);
  negRank:=RankMat(mat{ids});
  if negRank=Length(ids) then Error("negative control failed"); fi;
  AppendTo(out,"Repeated-coefficient negative control: target=",b," allowed=",Length(ids)," rank=",negRank,"\n");
  Print("Completed n=",n," counterexample=",found,"\n");
  if found then break; fi;
od;
AppendTo(out,"Completed prescribed test; counterexample=",found,". No asymptotic probability inferred.\n");
QUIT;
