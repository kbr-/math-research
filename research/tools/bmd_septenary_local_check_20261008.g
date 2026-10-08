Read("research/results/bmd-nine-septenary-period-20261008/local-certificates.g");
for curve in [1..2] do
 recd:=LOCAL_CERTIFICATES[curve];;period:=recd[6];;deg:=recd[1];;fq:=GF(7^deg);;oneq:=One(fq);;zeroq:=Zero(fq);;xq:=Indeterminate(fq,"xq");;
 b:=RootsOfPolynomial(fq,Sum([0..deg],j->recd[2][j+1]*xq^j))[1];;
 decodeq:=c->Sum([0..deg-1],j->(QuoInt(c,7^j) mod 7)*b^j);;
 y:=Indeterminate(fq,"y");;iy:=IndeterminateNumberOfUnivariateRationalFunction(y);;
 polq:=v->UnivariatePolynomialByCoefficients(FamilyObj(oneq),v,iy);;
 off:=0;;for L in [15,15,15,15,4] do for point in [1..8] do
  v:=List(recd[4]{[off+1..off+L]},decodeq);;h:=polq(v);;
  if PowerMod(h,period,y^L)<>oneq*y^0 then Error("complete geometric local period");fi;
  off:=off+L;
 od;od;
 if off<>512 then Error("all geometric charts");fi;
 Print("GAP_PERIOD curve=",curve-1," local_period=",period," all512=true\n");
od;
Print("GAP_SEPTENARY_LOCAL_PERIODS_COMPLETED two_inputs_all_local_periods\n");
QUIT;
