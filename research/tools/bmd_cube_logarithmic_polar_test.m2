-- Exhaustive test of a named uniform mechanism, on the already retained n4,d2
-- object: can the corrected polar multiplier Q modulo(F,deltaF) be theta(F)
-- for a homogeneous collision-logarithmic derivation theta of weight two?
-- The proved Vandermonde/Saito basis reduces every such theta to scalar D2
-- modulo(F,deltaF); one ideal membership test therefore covers the entire class.
-- Weight two at arbitrary finite operator order reduces to 1,D1,D2,D1^2:
-- D0 is weighted Euler. Include D1^2F and retain an independent 6x6 minor.
-- Stages: construct D0..D3 from Newton sums; verify determinant and log tangency;
-- test corrected multiplier membership; retain the exact lift or normal form.
needsPackage "Elimination";
B=QQ[e_1,e_2,e_3,e_4,Degrees=>{1,2,3,4}];
cubeRead=(path,key)->(
    sourceLines:=separate("\n",get path);
    hits:=select(sourceLines,l->substring(0,#key,l)==key);
    assert(#hits==1); value substring(#key,hits#0));
cubeMat=rows->matrix apply(rows,row->apply(row,f->sub(f,B)));
cubePath="research/results/cube-hull-uniform-degree-review-20260927/low-polar-colon.txt";
cubePolars=cubeMat cubeRead(cubePath,"POLAR_EQUATIONS=");
cubeF=cubePolars_(0,0); cubeDF=cubePolars_(0,1);
cubeQ=sub(cubeRead(cubePath,"CORRECTED_SECOND_COEFFICIENT="),B);
cubeElem={1_B,e_1,e_2,e_3,e_4};
cubePowers=new MutableHashTable; cubePowers#0=4_B;
for m from 1 to 7 do cubePowers#m=(
    if m<=4 then sum(toList(1..m-1),j->(-1)^(j-1)*cubeElem#j*cubePowers#(m-j))+(-1)^(m-1)*m*cubeElem#m
    else sum(toList(1..4),j->(-1)^(j-1)*cubeElem#j*cubePowers#(m-j)));
cubeDerMatrix=matrix table(4,4,(j,k)->-sum(toList(0..j),l->(-1)^l*cubeElem#(j-l)*cubePowers#(k+1+l)));
cubeApply=(k,f)->sum(toList(0..3),j->cubeDerMatrix_(j,k)*diff(B_j,f));
assert(cubeApply(0,cubeF)==-15*cubeF and cubeApply(1,cubeF)==cubeDF);
cubeBZ=B[z]; cubePolynomial=z^4-e_1*z^3+e_2*z^2-e_3*z+e_4;
cubeDisc=sub(discriminant(cubePolynomial,z),B); cubeCollision=e_4*cubeDisc;
assert((det cubeDerMatrix)==cubeCollision or (det cubeDerMatrix)==-cubeCollision);
for k from 0 to 3 do assert(cubeApply(k,cubeCollision)%cubeCollision==0);
cubeD2F=cubeApply(2,cubeF);
cubeTestRow=matrix{{cubeF,cubeDF,cubeD2F}};
cubeRemainder=cubeQ % ideal cubeTestRow;
<< "COLLISION_LOG_DERIVATION_MATRIX=" << toString entries cubeDerMatrix << endl;
<< "DETERMINANT_SIGN=" << (det cubeDerMatrix)//cubeCollision << endl;
<< "D2F=" << toString cubeD2F << endl;
<< "Q_IN_LOG_DERIVATIVE_CLASS=" << (cubeRemainder==0) << endl;
if cubeRemainder==0 then (
    liftQ:=matrix{{cubeQ}}//cubeTestRow;
    assert(cubeTestRow*liftQ==matrix{{cubeQ}});
    assert(liftQ_(2,0)!=0 and first degree liftQ_(2,0)==0);
    << "EXACT_LIFT_COEFFICIENTS=" << toString entries liftQ << endl;
) else << "CLASS_OBSTRUCTION_REMAINDER=" << toString cubeRemainder << endl;
-- The stronger claim that the entire boundary-coordinate ideal is the
-- collision-logarithmic Jacobian ideal is independently constrained by degrees.
cubeS=cubeMat cubeRead("research/results/cube-four-hull-frame-20260927/frame-and-derivatives.txt","HILBERT_BURCH=");
cubeBoundary=minors(3,cubeS);
cubeLogJac=ideal apply(toList(0..3),k->cubeApply(k,cubeF));
<< "LOG_JACOBIAN_EQUALS_BOUNDARY=" << (cubeLogJac==cubeBoundary) << endl;
assert(diff(e_4,cubeF)!=0 and degree diff(e_4,cubeF)=={11});
<< "NONZERO_E4_PARTIAL=" << toString diff(e_4,cubeF) << endl;
cubeDDF=cubeApply(1,cubeDF);
cubeSecondRow=matrix{{cubeF,cubeDF,cubeD2F,cubeDDF}};
cubeSecondRemainder=cubeQ % ideal cubeSecondRow;
<< "Q_IN_SECOND_ORDER_CLASS=" << (cubeSecondRemainder==0) << endl;
if cubeSecondRemainder==0 then (
    liftSecond:=matrix{{cubeQ}}//cubeSecondRow;
    assert(cubeSecondRow*liftSecond==matrix{{cubeQ}});
    << "SECOND_ORDER_EXACT_LIFT=" << toString entries liftSecond << endl;
) else << "SECOND_ORDER_REMAINDER=" << toString cubeSecondRemainder << endl;
cubeG10=(cubeQ+cubeDDF)/132;
assert(cubeG10%cubeBoundary==0);
<< "G10_IN_FIRST_ORDER_CLASS=" << (cubeG10%ideal cubeTestRow==0) << endl;
if cubeG10%ideal cubeTestRow==0 then (
    liftG:=matrix{{cubeG10}}//cubeTestRow;
    assert(cubeTestRow*liftG==matrix{{cubeG10}});
    << "G10_EXACT_LIFT=" << toString entries liftG << endl;
);
-- Independent coefficient certificate: any weight-17 ideal expression lies
-- in the span of these five forms; a nonzero augmented 6x6 minor refutes it.
cubeForms={e_1^2*cubeF,e_2*cubeF,e_1*cubeDF,cubeD2F,cubeDDF,cubeQ};
cubeMonomials=flatten entries basis(17,B);
cubeCoefficients=matrix apply(cubeMonomials,m->apply(cubeForms,f->lift(coefficient(m,f),QQ)));
assert(rank(cubeCoefficients_{0..4})==5 and rank cubeCoefficients==6);
cubeRows={};
scan(toList(0..numRows cubeCoefficients-1),i->(
    if #cubeRows<6 and rank cubeCoefficients^(cubeRows|{i})>#cubeRows then cubeRows=cubeRows|{i}));
cubeMinor=cubeCoefficients^cubeRows;
assert(det cubeMinor!=0);
<< "WEIGHT17_MONOMIAL_COUNT=" << #cubeMonomials << endl;
<< "CERTIFICATE_MONOMIALS=" << toString apply(cubeRows,i->cubeMonomials#i) << endl;
<< "CERTIFICATE_MATRIX=" << toString entries cubeMinor << endl;
<< "CERTIFICATE_DETERMINANT=" << det cubeMinor << endl;
<< "PASS logarithmic basis audit and exhaustive weight-two operator class tests" << endl;
exit 0;
