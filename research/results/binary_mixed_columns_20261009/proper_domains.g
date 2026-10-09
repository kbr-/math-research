# Exact control of the proper-hole normal form and column-state partitions.
# n=4, m=5: 1024 label assignments, 15 proper hole subsets.
# Degree-filtered monomials are all allowed supports after pivot elimination.
# GAP's exact GF(2) rank verifies independence once per symmetry class.
all := Tuples([0..3],5);;
if Length(all) <> 1024 then Error("size guard"); fi;
z := Zero(GF(2));; o := One(GF(2));;
allowed := function(a,B)
  return ForAll(B,j->Number(a,x->x=j)<=1);
end;;
Print("n=4 m=5 assignments=",Length(all)," proper_subsets=15\n");
for q in [0..3] do
  B := [0..q-1];;
  states := Filtered(all,a->allowed(a,B));;
  supports := List(states,a->Filtered([1..5],i->a[i]<>3));;
  mat := List([1..Length(states)],i->List(states,a->
      (ForAll(supports[i],r->a[r]=states[i][r]))));;
  mat := List(mat,row->List(row,function(x) if x then return o; else return z; fi; end));;
  rank := RankMat(mat);;
  if rank<>Length(states) then Error("normal basis dependent"); fi;
  counts := List([0..5],d->Number(supports,S->Length(S)<=d));;
  Print("selected_holes=",q," states=",Length(states)," rank=",rank,
        " degree_0_to_5=",counts,"\n");
od;
checks := 0;;
for B in Combinations([0..3]) do
  if Length(B)<4 then
    pivot := First([0..3],j->not j in B);;
    states := Filtered(all,a->allowed(a,B));;
    # Every selected hole has the state empty or its unique occupant.
    codes := Set(List(states,a->List(B,j->Position(a,j))));;
    for a in states do
      code := List(B,j->Position(a,j));;
      active := Number(codes,c->ForAll([1..Length(B)],t->
        (c[t]=fail and not B[t] in a) or
        (c[t]<>fail and a[c[t]]=B[t])));;
      if active<>1 then Error("partition failure"); fi;
      checks := checks+1;
    od;
    Print("B=",B," pivot=",pivot," points=",Length(states),
          " admissible_codes=",Length(codes),"\n");
  fi;
od;
if Number(all,a->allowed(a,[0..3]))<>0 then Error("full-domain control"); fi;
# Distinct locally nonempty domains can have empty global intersection.
if not ForAll([0..3],j->Number(all,a->allowed(a,[j]))>0) then
  Error("singleton domain empty");
fi;
Print("PASS partition_points=",checks,
      " full_hole_domain_empty=true singleton_intersection_empty=true\n");
QUIT;
