-- Complete transverse residual and its embedding in one cached CAS session.
-- Reloading printed generators discards cached Groebner data and timed out.
-- Keep that data in memory; no different size or collision pattern is tested.
-- Orders0..2 must match the independent Artin cross lengths3,11,24.
-- Order3 tests whether the entire length-three residual is detected.
transVerifySource=separate("\n",get "research/tools/bmd_cube_quadruple_transverse.m2");
value concatenate apply(select(transVerifySource,l->l!="exit 0;"),l->l|"\n");
<< "VERIFY_START" << endl << flush;
assert(dim K==0 and degree K==3);
assert(annihilator K==ideal(D,C,B,A^2));
-- Its nonzero A action has rank1 by length3 and A^2=0.
for jetOrder in {0,1,2,3} do (
    artinRelations:=gens((ideal gens R)^(jetOrder+1)*R^8);
    cj:=coker(rels|artinRelations);ej:=coker(gens sat|artinRelations);
    fullLength:=degree cj;upperLength:=degree ej;
    if jetOrder<3 then assert(fullLength==({3,11,24}#jetOrder));
    assert(fullLength-upperLength==({0,0,2,3}#jetOrder));
    << "JET=" << jetOrder << " CROSS_LENGTH=" << fullLength << " UPPER_LENGTH=" << upperLength
       << " RESIDUAL_IMAGE=" << fullLength-upperLength << endl << flush;
);
<< "VERIFY_PASS cpu=" << cpuTime()-transClock << endl << flush;
exit 0;
