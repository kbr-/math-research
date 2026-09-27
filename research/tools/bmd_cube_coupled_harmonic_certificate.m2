-- Test whether the full EPD pair-ideal encoding retains the already known
-- first bounded original relation (n4,d2,total19,order17). No new parameter
-- or dimension is searched; read the saved first resolution syzygy.
-- Stages: recover actual centered columns/unit pivots, lift retained syzygy,
-- form its harmonic polynomial, divide in the two-generator pair ideal,
-- verify the full polynomial certificate and original order/degree.
cubeDriverLines=separate("\n",get "research/tools/bmd_cube_full_cyclic_ext.m2");
cubeDriverStop=first select(toList(0..#cubeDriverLines-1),j->
    substring(0,19,cubeDriverLines#j)=="cubeResolution=res(");
value concatenate apply(take(cubeDriverLines,cubeDriverStop),l->l|"\n");
cubeSaved=separate("\n",get "research/results/cube-filtered-syzygy-route-review-20260927/centered-ext.txt");
cubeLabel="DEFECT_DIFFERENTIAL 2=";
cubeSavedLine=first select(cubeSaved,l->substring(0,#cubeLabel,l)==cubeLabel);
cubeSavedK=matrix value substring(#cubeLabel,cubeSavedLine);
cubeLastK=submatrix(cubeSavedK,,{0});
assert(cubePhi*cubeLastK==0);
cubeFirstK=-submatrix(cubeReduced,cubePivotRows,toList(7..16))*cubeLastK;
cubeOriginalK=cubeFirstK||cubeLastK;
cubeLeading=max select(toList(0..16),j->cubeOriginalK_(j,0)!=0);
assert(cubeLeading==15);
cubeScale=lift(coefficient(c_2,cubeOriginalK_(15,0)),QQ);
assert(cubeScale!=0);
cubeOriginalK=cubeOriginalK/cubeScale;
assert(cubeOriginalK_(15,0)==c_2);
assert(all(flatten entries(cubeA*cubeOriginalK),f->f==0));
<< "ORIGINAL_CENTERED_RELATION=" << toString entries cubeOriginalK << endl << flush;
P=QQ[c_2..c_5,ss,vv,Degrees=>{2,3,4,5,1,2}];
cubeParameterMap=map(P,S,{c_2,c_3,c_4,c_5});
cubeG={1_P,-(3/2)*ss};
for j from 1 to 15 do cubeG=append(cubeG,(-(j+3/2)*ss*cubeG#j-(j+2)*vv*cubeG#(j-1))/(j+1));
cubeH=sum(toList(0..16),j->(cubeParameterMap cubeOriginalK_(j,0))*cubeG#j);
cubeLH=diff(ss,diff(ss,cubeH))+ss*diff(ss,diff(vv,cubeH))+vv*diff(vv,diff(vv,cubeH))+(5/2)*diff(vv,cubeH);
assert(cubeLH==0 and first degree cubeH==17);
cubeOrdinary={1_P,ss};
for j from 2 to 5 do cubeOrdinary=append(cubeOrdinary,ss*cubeOrdinary#(j-1)-vv*cubeOrdinary#(j-2));
cubeAA=cubeOrdinary#4+c_2*cubeOrdinary#2-c_3*ss+c_4;
cubeBB=cubeOrdinary#5+c_2*cubeOrdinary#3-c_3*cubeOrdinary#2+c_4*ss-c_5;
cubeIdealMap=map(P^1,P^{-4,-5},{{cubeAA,cubeBB}});
cubeHMap=map(P^1,P^{-17},{{cubeH}});
cubeFG=cubeHMap//cubeIdealMap;
assert(cubeIdealMap*cubeFG==cubeHMap);
assert(isHomogeneous cubeFG and first degree cubeFG_(0,0)==13 and first degree cubeFG_(1,0)==12);
cubeFNormal=cubeFG_(0,0);cubeGNormal=cubeFG_(1,0);
while cubeGNormal!=0 and max(apply(exponents cubeGNormal,e->last e))>=2 do (
    d:=max apply(exponents cubeGNormal,e->last e);
    leading:=sum(select(terms cubeGNormal,t->last first exponents t==d));
    multiple:=leading//vv^2;
    assert(multiple*vv^2==leading);
    cubeGNormal=cubeGNormal-multiple*cubeAA;
    cubeFNormal=cubeFNormal+multiple*cubeBB;
);
assert(cubeAA*cubeFNormal+cubeBB*cubeGNormal==cubeH);
assert(first degree cubeFNormal==13 and first degree cubeGNormal==12);
cubeFG=map(target cubeFG,source cubeFG,{{cubeFNormal},{cubeGNormal}});
cubeDiagonal=sub(cubeH,{vv=>0_P});
cubeOrder=max apply(exponents cubeDiagonal,e->e#4);
assert(cubeOrder==15);
<< "HARMONIC_POLYNOMIAL=" << toString cubeH << endl;
<< "PAIR_IDEAL_GENERATORS=" << toString entries cubeIdealMap << endl;
<< "COUPLED_CERTIFICATE_F_G=" << toString entries cubeFG << endl;
<< "CERTIFICATE_WEIGHTS={13,12}; harmonic_weight17; original_total19; original_order17; top=c2" << endl;
<< "CERTIFICATE_MONOMIAL_COUNTS=" << apply(flatten entries cubeFG,f->#terms f) << endl;
<< "CERTIFICATE_MAX_V_DEGREES=" << apply(flatten entries cubeFG,f->max apply(exponents f,e->last e)) << endl;
<< "PASS full coupled polynomial identity, EPD equation, original column relation and order/degree" << endl;
<< "COUPLED_HARMONIC_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
