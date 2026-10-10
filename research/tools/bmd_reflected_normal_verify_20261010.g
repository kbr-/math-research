# Independent GAP linear algebra on the complete original derivative matrices.
Read("research/results/bmd-reflected-normal-20261010/matrices.g");;
for item in Cases do
  M:=item[3];; ders:=item[4];;
  if item[1]=2 then
    M:=List(M,r->List(r,Decode));;
    ders:=List(ders,A->List(A,r->List(r,Decode)));;
  fi;
  left:=NullspaceMat(M);;
  right:=NullspaceMat(TransposedMat(M));;
  Q:=List(ders,A->Concatenation(List(left,l->List(right,u->(l*A)*u))));;
  Print("GAP_CASE ",item[1]," source_rank=",RankMat(M)," left=",Length(left),
        " right=",Length(right)," normal_rank=",RankMat(Q),"\n");
od;
Print("REFLECTED_NORMAL_INDEPENDENT_COMPLETED\n");
QUIT_GAP(0);
