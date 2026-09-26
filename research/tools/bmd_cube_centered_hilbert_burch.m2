-- Full S5 invariant presentation of the actual d=2 first-step ideal.
-- Average the four retained S4-invariant generators over the five branch-label
-- cosets, express them in centered invariants of weights 2,3,4,5, and certify
-- equality after extension back to the original symmetric ring.
-- Test whether ANY graded Hankel Hilbert--Burch form is compatible with the
-- linear part: diagonal rescalings/graded basis changes preserve its six-cycle.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
certificateLines=separate("\n",get "research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt");
key="TOP_GENERATORS=";
hits=select(certificateLines,l -> substring(0,#key,l)==key);
assert(#hits==1);
gi=matrix value substring(#key,hits#0);
R=QQ[a_1..a_4];
branchRoots=toList gens R;
toR=map(R,B,apply(toList(1..4),k -> sum(subsets(4,k),I -> product(I,i -> R_i))));
mu=sum branchRoots/5;
centeredRoots={-mu}|apply(branchRoots,a -> a-mu);
centeredValues=apply(toList(2..5),k -> sum(subsets(5,k),I -> product(I,i -> centeredRoots#i)));
C=QQ[c2,c3,c4,c5,Degrees=>{2,3,4,5}];
centerMap=map(R,C,centeredValues);
es={1_B,e_1,e_2,e_3,e_4,0_B};
centerB=map(B,C,apply(toList(2..5),k -> sum(toList(0..k),j -> binomial(5-j,k-j)*(-e_1/5)^(k-j)*es#j)));
cosetMaps={map(R,R,branchRoots)}|apply(toList(0..3),i -> map(R,R,apply(toList(0..3),j -> (if j==i then 0_R else R_j)-R_i)));
cg=apply(first entries gi,f -> (
    av:=sum(cosetMaps,sigma -> sigma(toR f))/5;
    wt:=first degree f;
    cb:=basis(wt,C); rb:=basis(wt,R);
    lhs:=sub(last coefficients(centerMap cb,Monomials=>rb),QQ);
    rhs:=sub(last coefficients(matrix{{av}},Monomials=>rb),QQ);
    sol:=rhs//lhs;
    assert(lhs*sol==rhs);
    cf:=(cb*sub(sol,C))_(0,0);
    assert(centerMap cf==av);
    << "CENTERED_GENERATOR_" << wt << "=" << toString cf << endl << flush;
    cf));
J=ideal cg;
assert(centerB J==ideal gi);
<< "PASS full invariant generators extend to the actual weighted top ideal" << endl << flush;
RC=res coker gens J;
assert(length RC==2);
d1=RC.dd_1; M=RC.dd_2;
assert(minors(3,M)==J and dim(C/J)==2);
gdeg=apply(toList(0..3),i -> first degree d1_(0,i));
bdeg=apply(toList(0..2),j -> (
    i:=first select(toList(0..3),i -> M_(i,j)!=0);
    first degree M_(i,j)+gdeg#i));
rs=apply(reverse sort apply(toList(0..3),i -> {gdeg#i,i}),x -> x#1);
cs=apply(sort apply(toList(0..2),j -> {bdeg#j,j}),x -> x#1);
M=submatrix(M,rs,cs);
assert(apply(rs,i -> gdeg#i)=={15,14,13,12} and apply(cs,j -> bdeg#j)=={17,18,19});
lcMat=matrix table(4,3,(i,j) -> (
    wt:=2+i+j;
    if wt>5 then 0_QQ else sub(coefficient(C_(wt-2),M_(i,j)),QQ)));
cycA=lcMat_(0,2)*lcMat_(1,0)*lcMat_(2,1);
cycB=lcMat_(0,1)*lcMat_(1,2)*lcMat_(2,0);
<< "CENTERED_RELATION_MATRIX=" << toString entries M << endl;
<< "LINEAR_PART_COEFFICIENT_MATRIX=" << toString entries lcMat << endl;
<< "HANKEL_SIX_CYCLE_LEFT=" << cycA << " RIGHT=" << cycB << " RATIO=" << cycA/cycB << endl;
if cycA!=cycB then (<< "FALSIFIED: no graded Hankel form with weights 2..7 under graded basis and coordinate changes" << endl) else (<< "PASSED NECESSARY SIX-CYCLE CONDITION; nonlinear entries still require a test" << endl);
<< "PASS actual ideal equality, full invariant Hilbert--Burch certificate, and six-cycle audit" << endl;
exit 0;
