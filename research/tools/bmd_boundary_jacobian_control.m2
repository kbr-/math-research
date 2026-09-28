-- Test the all-N generic-reducedness mechanism on the retained first nontrivial
-- N=5 centered core. No new kernel or dimension row is computed.
-- Stages: load the certified rational marker, reconstruct four core columns,
-- compare the first determinant with the retained boundary form, reduce at a
-- denominator-safe prime, and compute the singular-locus codimension.
-- Sizes: 3x4 core, four maximal minors of weights15..18, 4x4 Jacobian,
-- at most36 two-minors of weights at most30 in four weighted variables.
-- Codimension>=3 for J+I_2(Jac J) modulo p implies the same bound over QQ.
-- Codimension2 modulo p would only be a warning requiring a rational witness.
S=QQ[c_2..c_5,Degrees=>{2,3,4,5}];
c2=c_2;c3=c_3;c4=c_4;c5=c_5;
bmdClock=cpuTime();
bmdLines=separate("\n",get "research/results/cube-centered-curvature-recurrence-20260927/centered-block-certificate.txt");
bmdRead=(data,label)->(
 hit:=select(data,l->substring(0,#label,l)==label);assert(#hit==1);
 value substring(#label,first hit)
);
bmdBoundary=sub(matrix bmdRead(bmdLines,"BLOCK_BOUNDARY_COORDINATES="),S);
bmdMarker=submatrix(bmdBoundary,{7,8,9},{0});
bmdKappa=2*c_2/5;
bmdDV={3*c_3,4*c_4-3*bmdKappa*c_2,5*c_5-2*bmdKappa*c_3,-bmdKappa*c_4};
bmdDelta=f->sum(toList(0..3),j->bmdDV#j*diff(S_j,f));
bmdDer=M->matrix apply(entries M,row->apply(row,f->bmdDelta f));
bmdConnection=matrix{{0_S,0_S,-(21/8)*c_3},{1_S,0_S,-(23/20)*c_2},{0_S,1_S,0_S}};
bmdIters={bmdMarker};
for j from 1 to 3 do bmdIters=append(bmdIters,bmdDer(last bmdIters)+bmdConnection*last bmdIters);
bmdA=map(S^(-{4,5,6}),S^(-{9,10,11,12}),fold((A,B)->A|B,bmdIters));
assert(isHomogeneous bmdA);
bmdSaved=separate("\n",get "research/results/cube-first-post-boundary-alln-20260928/c3-derivative-test.txt");
bmdSavedF=bmdRead(bmdSaved,"CENTERED_BOUNDARY=");
bmdF=det submatrix(bmdA,,{0,1,2});
assert(bmdF!=0 and degree bmdF=={15} and bmdF % ideal bmdSavedF==0);
bmdConstants=flatten apply(flatten entries bmdA,f->flatten entries last coefficients f);
bmdDen=lcm apply(bmdConstants,x->denominator lift(x,QQ));
assert(bmdDen%32003!=0);
<< "RATIONAL_CORE=" << toString entries bmdA << endl;
<< "BOUNDARY_COMPARISON=proportional to retained centered boundary" << endl;
<< "DENOMINATOR_LCM=" << bmdDen << endl;
kk=ZZ/32003;
K=kk[c_2..c_5,Degrees=>{2,3,4,5}];
bmdMod=map(K,S,gens K);
bmdAm=bmdMod bmdA;
bmdJ=minors(3,bmdAm);
assert(sort apply(flatten entries gens bmdJ,f->first degree f)=={15,16,17,18});
assert(codim bmdJ==2);
bmdJac=jacobian gens bmdJ;
assert(numrows bmdJac==4 and numcols bmdJac==4);
bmdJacIdeal=bmdJ+minors(2,bmdJac);
<< "PRIME=32003 ROOT_COUNT=5 BOUNDARY_IDEAL_CODIM=2" << endl;
<< "BOUNDARY_GENERATORS=" << toString entries gens bmdJ << endl;
<< "BEGIN_SINGULAR_LOCUS four variables, at most40 generators, max weight30 cpu=" << cpuTime()-bmdClock << endl << flush;
bmdGB=gens gb bmdJacIdeal;
bmdHeight=codim bmdJacIdeal;
<< "SINGULAR_LOCUS_CODIM=" << bmdHeight << endl;
<< "SINGULAR_LOCUS_GROEBNER_BASIS=" << toString entries bmdGB << endl << flush;
B=kk[x,z,y,Degrees=>{2,3,6}];
bmdBad=ideal(x^3+y,3*z*x^2);
bmdBadSing=bmdBad+minors(2,jacobian gens bmdBad);
assert(codim bmdBad==2 and codim bmdBadSing==2);
<< "NEGATIVE_CONTROL=nonreduced boundary (x^3+y,3zx^2), singular codimension2 detected" << endl;
<< "COMPLETED cpu=" << cpuTime()-bmdClock << endl << flush;
exit 0;
