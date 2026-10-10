# Native matrix control for the tuple-valued eigenvector lift.
# A core character on error images need not make the old weight an eigenvector.
mcF:=GF(2);;
mcCheck:=function(ok,msg)
  if not ok then Print("FAIL ",msg,"\n"); QUIT_GAP(1); fi;
end;
mcOne:=List([1..4],i->One(mcF));;
mcX:=List([0,1,0,1],a->a*One(mcF));;
mcY:=List([0,0,1,1],a->a*One(mcF));;
mcDX:=DiagonalMat(mcX);; mcDY:=DiagonalMat(mcY);;
mcT:=Concatenation(TransposedMat(mcDX),TransposedMat(mcDY));;
mcT:=TransposedMat(mcT);;
mcMX:=DiagonalMat(Concatenation(mcX,mcX));;
mcMY:=DiagonalMat(Concatenation(mcY,mcY));;
mcZero:=Zero(mcF)*mcOne;;
mcRows:=Tuples([Zero(mcF),One(mcF)],4);;
for mcFrow in mcRows do
  mcCheck((mcFrow*mcT)*mcMX=(mcFrow*mcDX)*mcT,"x action intertwines");
  mcCheck((mcFrow*mcT)*mcMY=(mcFrow*mcDY)*mcT,"y action intertwines");
od;
mcWeight:=mcOne+mcX;;
mcZ:=mcWeight*mcT;;
mcCheck(not IsZero(mcZ),"nonzero joint error image");
mcCheck(IsZero(mcZ*mcMX) and mcZ*mcMY=mcZ,"joint character x0 y1");
mcCheck(mcWeight*mcDY<>mcWeight,"old lift is not a scalar y eigenvector");
mcCheck(IsZero(mcWeight*mcDX),"zero character recovers weighted input");
# First source input x has zero core value, use zero coefficients.
# Second source input y has character one, select it in the first row.
mcCheck(IsZero(mcWeight*mcDX),"first complete companion");
mcCheck(IsZero((mcWeight*mcDY)*(IdentityMat(4,mcF)+mcDY)),"second complete companion");
Print("PASS old_functions=16 intertwining_checks=32 source_blocks=2 ",
      "nonzero_tuple_weight=1 scalar_eigenvector_negative_control=1\n");
QUIT_GAP(0);
