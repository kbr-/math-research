-- Test the uniform codimension-two stabilization prediction at its first
-- unsettled case N=6, in characteristic zero via exact modular injectivity.
-- The proposed bound is alpha6=43.  At excess41 and42 the original first-step
-- kernel must vanish; multiplication by c2 then excludes every excess<=42.
-- Stages: construct universal pair columns once, remove the nine constant
-- pivots, retain the full polynomial core, build the two graded coefficient
-- maps, and compute exact ranks over GF(1000003). No parameter is specialized.
-- A rank defect modulo this prime alone would not refute the QQ prediction.
kk=ZZ/1000003;
S=kk[c_2..c_6,Degrees=>{2,3,4,5,6}];
bmdClock=cpuTime();
bmdN=6;bmdLast=16;
bmdWeights=toList(2..6);
bmdPairs=select(subsets(toList(0..5),2),p->p#0<p#1);
bmdPairWeights=apply(bmdPairs,p->sum(p)+1);
bmdW=apply(toList(0..5),i->apply(toList(0..5),j->if i==j then 1_S else 0_S));
for i from 6 to 17 do bmdW=append(bmdW,apply(toList(0..5),j->sum(toList(2..6),k->(-1)^(k+1)*c_k*(bmdW#(i-k))#j)));
bmdGamma={1_S};
for i from 0 to 15 do bmdGamma=append(bmdGamma,-(2*i+3)/(2*i+2)*last bmdGamma);
bmdCols=apply(toList(0..16),j->apply(bmdPairs,p->sum(toList(0..j),a->(
 b:=j-a;bmdGamma#a*bmdGamma#b*((bmdW#a)#(p#0)*(bmdW#(b+1))#(p#1)-(bmdW#a)#(p#1)*(bmdW#(b+1))#(p#0))
))));
bmdAll=map(S^(-bmdPairWeights),S^(-toList(2..18)),transpose matrix bmdCols);
assert(isHomogeneous bmdAll);
bmdPivotPairs={{0,1},{0,2},{0,3},{0,4},{0,5},{1,5},{2,5},{3,5},{4,5}};
bmdPiv=apply(bmdPivotPairs,p->position(bmdPairs,q->p==q));
bmdRest=select(toList(0..14),i->not member(i,bmdPiv));
assert(apply(bmdRest,i->bmdPairWeights#i)=={4,5,6,6,7,8});
bmdP=submatrix(bmdAll,bmdPiv,toList(0..8));
bmdDet=det bmdP;assert(bmdDet!=0 and degree bmdDet=={0});
bmdInv=inverse bmdP;assert(bmdP*bmdInv==id_(target bmdP));
bmdCore=submatrix(bmdAll,bmdRest,toList(9..16))-submatrix(bmdAll,bmdRest,toList(0..8))*bmdInv*submatrix(bmdAll,bmdPiv,toList(9..16));
assert(isHomogeneous bmdCore);
<< "PRIME=1000003 ROOT_COUNT=6 ORIGINAL_ORDER=18" << endl;
<< "PIVOT_DETERMINANT=" << bmdDet << endl;
<< "CORE_SOURCE_WEIGHTS=" << toString degrees source bmdCore << endl;
<< "CORE_TARGET_WEIGHTS=" << toString degrees target bmdCore << endl;
<< "CORE_MATRIX=" << toString entries bmdCore << endl << flush;
for ell in {41,42} do (
 t:=18+ell;
 srcBasis:=basis(t,source bmdCore);tgtBasis:=basis(t,target bmdCore);
 ncols:=numcols srcBasis;nrows:=numcols tgtBasis;
 assert(ncols*nrows<26000000);
 assert({nrows,ncols}==(if ell==41 then {5401,4068} else {5797,4372}));
 << "BEGIN excess=" << ell << " rows=" << nrows << " columns=" << ncols << " cpu=" << cpuTime()-bmdClock << endl << flush;
 products:=bmdCore*srcBasis;
 coeffs:=last coefficients(products,Monomials=>tgtBasis);
 assert(tgtBasis*coeffs==products);
 coeffs=sub(coeffs,kk);
 assert(numrows coeffs==nrows and numcols coeffs==ncols);
 actualRank:=rank coeffs;
 << "RANK excess=" << ell << " value=" << actualRank << " nullity=" << ncols-actualRank << " cpu=" << cpuTime()-bmdClock << endl << flush;
);
<< "COMPLETED cpu=" << cpuTime()-bmdClock << endl << flush;
exit 0;
