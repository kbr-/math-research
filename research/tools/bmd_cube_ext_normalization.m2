-- Interpret the retained exact Ext3 presentation, without rerunning resolution.
-- Normalize its two basis scalars; verify the map to the (3,2) curve's
-- normalization. Equal Hilbert series is checked independently by GP.
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];
cubeLines=separate("\n",get "research/results/cube-filtered-syzygy-route-review-20260927/centered-ext.txt");
cubeRead=label->(
    hits:=select(cubeLines,l->substring(0,#label,l)==label);
    assert(#hits==1);
    matrix value substring(#label,hits#0)
);
cubeOriginal=cubeRead "CENTERED_DEFECT_PRESENTATION=";
cubeFirstMap=cubeRead "DEFECT_DIFFERENTIAL 1=";
assert(image cubeOriginal==image cubeFirstMap);
<< "PASS resolution first differential has exactly the original presentation image" << endl;
cubeStart=first select(toList(0..#cubeLines-1),i->substring(0,11,cubeLines#i)=="EXT_INDEX=3");
cubeKey="EXT_PRESENTATION=";
cubeFound=first select(toList(cubeStart..#cubeLines-1),i->substring(0,#cubeKey,cubeLines#i)==cubeKey);
cubeP=matrix value substring(#cubeKey,cubeLines#cubeFound);
assert(numrows cubeP==2 and numcols cubeP==6);
cubeA=lift(coefficient(c_3,cubeP_(0,0)),QQ);cubeB=lift(coefficient(c_2,cubeP_(1,0)),QQ);
assert(cubeA!=0 and cubeB!=0);
cubeQ=matrix table(2,6,(i,j)->cubeP_(i,j)*(if j>=4 then cubeB else 1_QQ)/
    (if i==0 then cubeA else cubeB));
cubeU=QQ[u];cubeMap=map(cubeU,S,{-15*u^2,10*u^3,60*u^4,-72*u^5});
cubeImages=matrix{{1_cubeU,(2/3)*u}};
assert(all(flatten entries(cubeImages*(cubeMap cubeQ)),f->f==0));
cubeJ=ideal(4*c_2^2-15*c_4,12*c_2*c_3-25*c_5,9*c_3^2+c_2*c_4);
assert(cubeMap cubeJ==ideal(0_cubeU));
<< "NORMALIZED_EXT3_PRESENTATION=" << toString entries cubeQ << endl;
<< "NORMALIZATION_MAP={c2:-15u²,c3:10u³,c4:60u4,c5:-72u5}; generators map to1,(2/3)u" << endl;
<< "PASS all6 relations and all3 annihilator equations; surjectivity follows from u²=-c2/15" << endl;
exit 0;
