# Exact controls for the general rectangular-inverse substitution, invertibility
# weight degree, and failure of support-only relative-dimension independence.
# GAP native matrix multiplication, determinant and nullspace over GF(2).
# Fixed bounded cases: n<=2. No larger parameter series is requested.
fld := GF(2);;
bits := function(mask, count)
  return List([0..count-1], j -> QuoInt(mask,2^j) mod 2);
end;;
mat := function(mask, rows, cols)
  local bb;
  bb := bits(mask,rows*cols);
  return List([1..rows], i -> List([1..cols],j -> bb[(i-1)*cols+j]*One(fld)));
end;;
degree := function(vals, count)
  local cc, j, mask, supp;
  cc := ShallowCopy(vals);
  for j in [0..count-1] do
    for mask in [0..2^count-1] do
      if QuoInt(mask,2^j) mod 2 = 1 then
        cc[mask+1] := (cc[mask+1]+cc[mask-2^j+1]) mod 2;
      fi;
    od;
  od;
  supp := Filtered([0..2^count-1],mask -> cc[mask+1]=1);
  if IsEmpty(supp) then return -1; fi;
  return Maximum(List(supp,mask -> Sum(bits(mask,count))));
end;;
Print("Stages: rectangular/square pairs <=4096; substitution <=64 Boolean inputs; invertibility weights <=63; two-variable kernel control.\n");
subchecks:=0;;
for nn in [1,2] do
  mm:=nn+1;; ident:=IdentityMat(mm,fld);; hits:=0;; pairs:=0;;
  for amask in [0..2^(mm*nn)-1] do
    amat:=mat(amask,mm,nn);;
    for bmask in [0..2^(mm*nn)-1] do
      bmat:=mat(bmask,nn,mm);; pairs:=pairs+1;;
      if amat*bmat=ident then hits:=hits+1; fi;
    od;
    prodmat:=amat*TransposedMat(amat);;
    for ii in [1..mm] do
      for jj in [1..mm] do
        if ii=jj then
          expected:=Sum(amat[ii]);
        else
          expected:=Sum([1..nn],kk->amat[ii][kk]*amat[jj][kk]);
        fi;
        Assert(0,prodmat[ii][jj]=expected);
        subchecks:=subchecks+1;
      od;
    od;
  od;
  Assert(0,hits=0);
  Print("rectangular n=",nn," pairs=",pairs," inverse pairs=",hits,"\n");
  sqhits:=0;; sqpairs:=0;;
  for amask in [0..2^(nn*nn)-1] do
    amat:=mat(amask,nn,nn);;
    for bmask in [0..2^(nn*nn)-1] do
      sqpairs:=sqpairs+1;;
      if amat*mat(bmask,nn,nn)=IdentityMat(nn,fld) then sqhits:=sqhits+1; fi;
    od;
  od;
  Assert(0,sqhits=Size(GL(nn,2)));
  Print("square n=",nn," pairs=",sqpairs," inverse pairs=",sqhits,"\n");
od;
Print("substitution coordinate checks=",subchecks,"\n");
for kk in [1,2] do
  nv:=kk*kk;; npoints:=2^nv;;
  glpoints:=Filtered([0..npoints-1],u -> DeterminantMat(mat(u,kk,kk))<>Zero(fld));;
  Assert(0,Length(glpoints)<=6);
  hist:=List([0..nv],i->0);;
  for wmask in [1..2^Length(glpoints)-1] do
    vals:=List([1..npoints],i->0);; wb:=bits(wmask,Length(glpoints));;
    for ii in [1..Length(glpoints)] do vals[glpoints[ii]+1]:=wb[ii]; od;
    deg:=degree(vals,nv);;
    Assert(0,deg>=kk);
    hist[deg+1]:=hist[deg+1]+1;
  od;
  detvals:=List([0..npoints-1],u -> Int(DeterminantMat(mat(u,kk,kk))));;
  Assert(0,degree(detvals,nv)=kk);
  Print("pivot k=",kk," invertible points=",Length(glpoints)," nonzero supported weights=",2^Length(glpoints)-1," degree histogram=",hist,"\n");
od;
mx:=List([[0,1,0,0],[0,1,0,0],[0,0,0,1]],r->r*One(fld));;
my:=List([[0,0,1,0],[0,0,0,1],[0,0,1,0]],r->r*One(fld));;
joint:=List([1..3],i->Concatenation(mx[i],my[i]));;
kdims:=[Length(NullspaceMat(mx)),Length(NullspaceMat(my)),Length(NullspaceMat(joint))];;
Assert(0,kdims=[1,1,0]);
Print("truncated disjoint-variable kernel dimensions=",kdims," in domain dimension3\n");
Print("All assertions passed.\n");
QUIT;
