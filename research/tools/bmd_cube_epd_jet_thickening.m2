-- Calibrate infinitesimal support tests: a closed collision fibre can lose the
-- known first EPD extension class. Keep the existing N5 presentation and eta.
-- Test the specified velocity and one transverse negative control only.
cubeInput=separate("\n",get "research/tools/bmd_cube_first_obstruction.m2");
cubeStop=first select(toList(0..#cubeInput-1),j->substring(0,14,cubeInput#j)=="cubeRelations=");
value concatenate apply(take(cubeInput,cubeStop),l->l|"\n");
cubeArtinRing=QQ[eps];cubeArtin=cubeArtinRing/ideal(eps^2);
cubeBase={-15_QQ,10_QQ,60_QQ,-72_QQ};
cubeDirections={{-3_QQ,-12_QQ,9_QQ,54_QQ},{0_QQ,0_QQ,0_QQ,1_QQ}};
cubeExpand=M->matrix table(2*numrows M,numcols M,(i,j)->
    lift(coefficient(eps^(i//numrows M),lift(M_(i%numrows M,j),cubeArtinRing)),QQ));
for direction from 0 to 1 do (
    values:=apply(toList(0..3),i->cubeBase#i+(cubeDirections#direction)#i*eps);
    spec:=map(cubeArtin,S,values);
    phi:=spec cubePhi;eta:=spec cubeEta;
    imageMat:=cubeExpand(phi|(eps*phi));
    classMat:=cubeExpand eta;
    rr:=rank imageMat;ra:=rank(imageMat|classMat);
    << "DIRECTION=" << direction << " PARAMETER_VELOCITY=" << cubeDirections#direction
       << " DEFECT_DIMENSION=" << 6-rr << " ETA_SURVIVES=" << (ra>rr) << endl;
    << "SPECIALIZED_PRESENTATION=" << toString entries phi << endl;
    << "SPECIALIZED_ETA=" << toString entries eta << endl << flush;
);
-- Three transverse parameters: c2=-15 is an etale slice to the smooth
-- triple-double curve at z=1, since d(c2)/dz=-30. Stop as soon as eta survives.
-- The bounded fallback q<=6 has length<=56 and target dimension<=168 over QQ.
cubeLocal=QQ[uu,vv,ww];cubeDetected=false;
for q from 2 to 6 do if not cubeDetected then (
    artin:=cubeLocal/((ideal(uu,vv,ww))^q);
    spec:=map(artin,S,{-15_artin,10+uu,60+vv,-72+ww});
    phi:=matrix entries(spec cubePhi);eta:=matrix entries(spec cubeEta);
    remainder:=eta % (gens gb image phi);
    cubeDetected=(remainder!=0);
    << "FULL_TRANSVERSE_POWER=" << q << " ARTIN_LENGTH=" << binomial(q+2,3)
       << " ETA_SURVIVES=" << cubeDetected << endl;
    << "ETA_NORMAL_FORM=" << toString entries remainder << endl << flush;
    if cubeDetected then (
        << "TRANSVERSE_PRESENTATION=" << toString entries phi << endl;
        << "TRANSVERSE_ETA=" << toString entries eta << endl;
    );
);
assert cubeDetected;
<< "EPD_JET_THICKENING_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
