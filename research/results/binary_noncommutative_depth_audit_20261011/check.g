# Exact local identities in GAP's free associative algebra, not a commutative quotient.
# Covers every nontrivial local rule schema used in the draft and its prefix identity.
ncA := FreeAssociativeAlgebraWithOne(GF(2), "a", "b", "h", "u", "v", "l", "c");;
ncG := GeneratorsOfAlgebra(ncA);;
ncOne := One(ncA);; ncZero := Zero(ncA);;
ncA1 := ncG[2];; ncB := ncG[3];; ncH := ncG[4];;
ncU := ncG[5];; ncV := ncG[6];; ncL := ncG[7];; ncC := ncG[8];;
ncCount := 0;; ncNegative := 0;; ncTruth := 0;; ncParity := 0;;
ncCheck := function(x,y)
  if x <> y then Print("FAIL free-algebra identity\n"); QUIT_GAP(1); fi;
  ncCount := ncCount+1;
end;;
ncCom := function(x,y) return x*y-y*x; end;;
ncBool := function(x) return x*x-x; end;;
ncCheck(ncCom(ncA1*ncB,ncH), ncA1*ncCom(ncB,ncH)+ncCom(ncA1,ncH)*ncB);
ncCheck(ncCom(ncA1,ncB*ncH), ncCom(ncA1,ncB)*ncH+ncB*ncCom(ncA1,ncH));
ncCheck(ncBool(ncA1+ncB),ncBool(ncA1)+ncBool(ncB)+ncCom(ncA1,ncB));
ncCheck(ncBool(ncA1*ncB),ncA1*ncCom(ncB,ncA1)*ncB+ncBool(ncA1)*ncB*ncB+ncA1*ncBool(ncB));
ncCheck((ncOne-ncA1)*ncH+ncA1*ncH,ncH);
ncCheck((ncOne-ncA1)*ncH+ncA1*(ncOne-ncB)*ncH,(ncOne-ncA1*ncB)*ncH);
ncCheck((ncOne-ncA1)*ncB*ncH+ncA1*(ncOne-ncB)*ncH,(ncA1+ncB)*ncH);
ncCheck((ncOne-ncA1)*(ncOne-ncB)*ncH+ncA1*ncB*ncH,(ncOne+ncA1+ncB)*ncH);
ncCheck(ncH*ncA1,ncA1*ncH+ncCom(ncH,ncA1));
ncCheck(ncA1*ncA1*ncH-ncA1*ncH,ncBool(ncA1)*ncH);
ncCheck(ncU*(ncOne-ncL)*ncV*ncA1*ncL*ncB,
  -ncU*ncBool(ncL)*ncV*ncA1*ncB+ncU*(ncOne-ncL)*ncCom(ncV*ncA1,ncL)*ncB);
ncCheck(ncOne-(ncOne-ncA1)*(ncOne-ncB)*(ncOne-ncC),
  ncA1+(ncOne-ncA1)*ncB+(ncOne-ncA1)*(ncOne-ncB)*ncC);
for ncBad in [ncBool(ncA1+ncB)-ncBool(ncA1)-ncBool(ncB),
  ncU*(ncOne-ncL)*ncV*ncA1*ncL*ncB+ncU*ncBool(ncL)*ncV*ncA1*ncB] do
  if ncBad=ncZero then Print("FAIL negative control\n"); QUIT_GAP(1); fi;
  ncNegative := ncNegative+1;
od;
# Independent ordinary Boolean truth evaluation of the four two-premise rules and weakening.
for ncVals in Tuples([0,1],3) do
  ncX := ncVals[1]; ncY := ncVals[2]; ncZ := ncVals[3];
  ncRules := [ [[(1-ncX)*ncZ,ncX*ncZ],ncZ],
    [[(1-ncX)*ncZ,(1-ncY)*ncZ],(1-ncX*ncY)*ncZ],
    [[(1-ncX)*ncY*ncZ,ncX*(1-ncY)*ncZ],((ncX+ncY) mod 2)*ncZ],
    [[(1-ncX)*(1-ncY)*ncZ,ncX*ncY*ncZ],((1+ncX+ncY) mod 2)*ncZ],
    [[ncZ],ncZ*ncX] ];
  for ncRule in ncRules do
    if ForAll(ncRule[1],x->x=0) and ncRule[2]<>0 then
      Print("FAIL Boolean rule\n"); QUIT_GAP(1);
    fi;
    ncTruth := ncTruth+1;
  od;
od;
for ncArity in [0..4] do
  for ncBits in Tuples([0,1],ncArity) do
    ncTranslated := (1+ncArity+Sum(List(ncBits,x->1-x))) mod 2;
    if ncTranslated <> 1-(Sum(ncBits) mod 2) then
      Print("FAIL parity convention\n"); QUIT_GAP(1);
    fi;
    ncParity := ncParity+1;
  od;
od;
Print("PASS: ",ncCount," free-algebra identities; ",ncTruth," Boolean rule cases; ",
  ncParity," parity assignments; ",ncNegative," negative controls.\n");
QUIT_GAP(0);
