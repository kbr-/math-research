-- Interpret the retained small coefficient actions; no cyclic/image series rerun.
-- Check exact squared-cubic equations, doubled cusp annihilator, and minimal
-- two-variable presentation. Derive original-S Betti data only from that
-- presentation, the three monic graph relations, and the verified vertex split.
stClock=cpuTime();stR=QQ[baseT,Degrees=>{2}];
stLines=separate("\n",get "research/results/cube-six-root-coefficient-image-20260927/actions-certificate.txt");
stGet=tag->value substring(#tag,first select(stLines,l->substring(0,#tag,l)==tag));
stOps=apply(stGet "FREE_COEFFICIENT_ACTIONS=",a->matrix a);
stWeights=stGet "FREE_GENERATOR_WEIGHTS=";
stEq=(a,b)->entries a==entries b;
stU=stOps#0;stId=id_(stR^6);stDelta=stU^2+(2/27)*baseT^3*stId;
<< "GRAPH_C4=" << (stEq(stOps#1,(1/4)*baseT^2*stId))
   << " GRAPH_C5=" << (stEq(stOps#2,(baseT/2)*stU))
   << " GRAPH_C6=" << (stEq(stOps#3,(1/4)*stU^2))
   << " DELTA_NONZERO=" << (stDelta!=0) << " DELTA_SQUARE_ZERO=" << (stDelta^2==0)
   << " DELTA_RANK=" << rank stDelta << endl << flush;
assert(stEq(stOps#1,(1/4)*baseT^2*stId) and stEq(stOps#2,(baseT/2)*stU) and stEq(stOps#3,(1/4)*stU^2));
assert(stDelta!=0 and stDelta^2==0 and rank stDelta==2);
stP=QQ[coefT,coefU,Degrees=>{2,3}];stMap=map(stP,stR,{coefT});
stMatrix=coefU*id_(stP^6)-stMap stU;stD=coefU^2+(2/27)*coefT^3;
assert(det stMatrix==stD^3);
stF=coker map(stP^(apply(stWeights,w->-w)),stP^(apply(stWeights,w->-w-3)),entries stMatrix);
stMin=prune stF;stPres=presentation stMin;
assert(numrows stPres==5 and numcols stPres==5);
assert(all(flatten entries stPres,f->f%ideal(coefT,coefU)==0));
assert(det stPres!=0);
stGens=flatten degrees target stPres;stRels=flatten degrees source stPres;
<< "MINIMAL_GENERATOR_WEIGHTS=" << toString stGens << " MINIMAL_RELATION_WEIGHTS=" << toString stRels << endl;
<< "MINIMAL_TWO_VARIABLE_PRESENTATION=" << toString entries stPres << endl;
-- Use only homogeneous invertible basis changes to make the presentation readable.
stPairRows={0,2};
stLead=matrix table(2,2,(i,j)->lift(coefficient(coefT,stPres_(stPairRows#i,j)),QQ));
stInv=(id_(QQ^2))//stLead;assert(stInv*stLead==id_(QQ^2));
stDiag={0_QQ,1/lift(coefficient(coefU,stPres_(1,0)),QQ),0_QQ,
    1/lift(coefficient(coefT^2,stPres_(3,1)),QQ),1/lift(coefficient(coefU,stPres_(4,1)),QQ)};
stRowChange=matrix table(5,5,(i,j)->if member(i,stPairRows) and member(j,stPairRows) then
    stInv_(position(stPairRows,k->k==i),position(stPairRows,k->k==j)) else if i==j then stDiag#i else 0_QQ);
assert(det stRowChange!=0);
stReadable=sub(stRowChange,stP)*stPres;
<< "READABLE_ROW_CHANGE=" << toString entries stRowChange << endl;
<< "READABLE_PRESENTATION=" << toString entries stReadable << endl;
stCross=lift(coefficient(coefU,stReadable_(2,2)),QQ);assert(stCross!=0);
stScaleRows=diagonalMatrix matrix{{stCross,stCross,1_QQ,1_QQ,1_QQ}};
stScaleCols=diagonalMatrix matrix{{1/stCross,1_QQ,1/stCross,1_QQ,1_QQ}};
stCompact=sub(stScaleRows,stP)*stReadable*sub(stScaleCols,stP);
<< "COMPACT_SCALE=" << stCross << " COMPACT_PRESENTATION=" << toString entries stCompact << endl;

<< "DOUBLED_CUSP_POLYNOMIAL=" << toString stD << " CHARACTERISTIC_DETERMINANT=" << toString det stMatrix << endl;
stH=QQ[h];stB0=sum(stGens,w->h^w);stB1=sum(stRels,w->h^w);
stI0=stB0+h^14;
stI1=stB1+stB0*(h^4+h^5+h^6)+h^14*(h^2+h^3+h^4+h^5+h^6);
<< "IMAGE_BETTI0=" << toString stI0 << " IMAGE_BETTI1=" << toString stI1
   << " FIRST_RELATION_MAX=" << first degree stI1 << endl;
<< "PASS cpu=" << cpuTime()-stClock << endl << flush;
exit 0;
