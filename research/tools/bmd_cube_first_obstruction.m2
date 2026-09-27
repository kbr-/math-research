-- Test the universal EPD primitive of the divided difference on the first
-- nonzero extension class (N5). The retained centered driver supplies the
-- exact target and unit elimination; its resolution stage is not rerun.
-- Stages: build the existing 10x17 column map, verify the EPD primitive,
-- form its marked class, compute its scalar annihilator, then lift every
-- minimal annihilator generator through the original centered columns.
-- This is a relation-lifting test, not a new dimension/threshold sweep.
cubeDriverLines=separate("\n",get "research/tools/bmd_cube_full_cyclic_ext.m2");
cubeDriverStop=first select(toList(0..#cubeDriverLines-1),j->
    substring(0,19,cubeDriverLines#j)=="cubeResolution=res(");
value concatenate apply(take(cubeDriverLines,cubeDriverStop),l->l|"\n");
cubeWork=S[ss,zz,Degrees=>{1,2}];
cubePrimitive=(-5*ss^4*zz/128-35*ss^2*zz^2/768-59*zz^3/18432
    -3*c_2*ss^2*zz/32-7*c_2*zz^2/384+c_3*ss*zz/8-c_4*zz/8);
cubeDivided=(5*ss^4+10*ss^2*zz+zz^2)/16+c_2*(3*ss^2+zz)/4-c_3*ss+c_4;
cubeL=diff(ss,diff(ss,cubePrimitive))-4*zz*diff(zz,diff(zz,cubePrimitive))-8*diff(zz,cubePrimitive);
<< "EPD_RESIDUAL=" << cubeL-cubeDivided << endl;
assert(cubeL==cubeDivided);
<< "PASS EPD primitive of the degree4 divided difference" << endl << flush;
cubeXY=S[xx,yy];
cubeSub=map(cubeXY,cubeWork,{xx+yy,(xx-yy)^2});
cubePX=xx^5+c_2*xx^3-c_3*xx^2+c_4*xx-c_5;
cubePY=yy^5+c_2*yy^3-c_3*yy^2+c_4*yy-c_5;
assert((yy-xx)*(cubeSub cubeDivided)==cubePY-cubePX);
cubeFinite=cubeXY/ideal(cubePX,cubePY);
cubeAlternant=lift(sub((yy-xx)*(cubeSub cubePrimitive),cubeFinite),cubeXY);
cubeHullClass=matrix table(10,1,(i,j)->sub(coefficient(xx^((cubePairs#i)#0)*yy^((cubePairs#i)#1),cubeAlternant),S));
cubeEtaRaw=submatrix(cubeRowChange*cubeHullClass,cubeOtherRows,);
cubeEta=map(target cubePhi,S^{-8},entries cubeEtaRaw);
assert isHomogeneous cubeEta;
assert(image(cubePhi|cubeEta)!=image cubePhi);
<< "FIRST_CLASS_IN_MINIMAL_COVER=" << toString entries cubeEta << endl << flush;
cubeRelations=syz(cubePhi|(-cubeEta));
cubeScalarIdeal=ideal submatrix(cubeRelations,{10},);
cubeScalarGens=mingens cubeScalarIdeal;
<< "SCALAR_ANNIHILATOR_GENERATORS=" << toString entries cubeScalarGens << endl;
<< "SCALAR_ANNIHILATOR_DEGREES=" << degrees source cubeScalarGens << endl;
<< "SCALAR_ANNIHILATOR_RADICAL=" << toString entries gens radical cubeScalarIdeal << endl << flush;
cubeLastLift=(cubeEta*cubeScalarGens)//cubePhi;
assert(cubePhi*cubeLastLift==cubeEta*cubeScalarGens);
cubeFullRhs=cubeHullClass*cubeScalarGens-submatrix(cubeA,,toList(7..16))*cubeLastLift;
cubeChangedRhs=cubeRowChange*cubeFullRhs;
assert(submatrix(cubeChangedRhs,cubeOtherRows,)==0);
cubeFirstLift=submatrix(cubeChangedRhs,cubePivotRows,);
cubeLift=cubeFirstLift||cubeLastLift;
assert(cubeA*cubeLift==cubeHullClass*cubeScalarGens);
<< "ORIGINAL_PAIR_HULL_CLASS=" << toString entries cubeHullClass << endl;
<< "ORIGINAL_CENTERED_COLUMN_LIFTS=" << toString entries cubeLift << endl;
<< "LIFT_PAIR_HIGHEST_ORDERS=" << apply(toList(0..numcols cubeLift-1),j->max select(toList(0..16),i->cubeLift_(i,j)!=0)) << endl;
<< "PASS all scalar generators lift through actual centered pair columns0..16" << endl;
cubeScalarRelations=syz cubeScalarGens;
assert(cubeScalarGens*cubeScalarRelations==0);
assert isHomogeneous cubeScalarRelations;
<< "SCALAR_SYZYGY_MATRIX=" << toString entries cubeScalarRelations << endl;
cubeRelationWeights=apply(degrees source cubeScalarRelations,d->first d+8);
cubeFromClass=map(S^(-toList(2..18)),S^(-cubeRelationWeights),entries(cubeLift*cubeScalarRelations));
assert isHomogeneous cubeFromClass;
assert(entries(cubeA*cubeFromClass)==entries map(S^10,source cubeFromClass,0));
cubeClassKernel=mingens image cubeFromClass;
<< "SCALAR_SYZYGY_TOTAL_DEGREES=" << degrees source cubeScalarRelations << endl;
<< "DERIVED_OPERATOR_RELATION_TOTAL_DEGREES=" << degrees source cubeClassKernel << endl;
<< "DERIVED_OPERATOR_RELATION_HIGHEST_ORDERS=" << apply(toList(0..numcols cubeClassKernel-1),j->2+max select(toList(0..16),i->cubeClassKernel_(i,j)!=0)) << endl;
<< "DERIVED_OPERATOR_RELATIONS=" << toString entries cubeClassKernel << endl;
<< "PASS every derived column is an actual centered operator relation" << endl;
<< "FIRST_OBSTRUCTION_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
