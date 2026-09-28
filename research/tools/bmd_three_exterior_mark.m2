-- Follow-up on the same M=3 exterior map, not another parameter.
-- Does adding the marked last column make the map onto away from axes and
-- pair collisions? If so, the previously computed nonempty obstruction
-- scheme forces every zeroth-order highest coefficient to vanish there.
-- Reuse the saved map and all four old minors; compute only the new column
-- and six new minors, then work in the saved finite obstruction quotient.
-- Repeating saturation in an added variable timed out; this reuses the known
-- saturated basis and removes the common collision factor before reduction.
-- No old kernel or saturation is rerun.
kk=QQ;R=kk[tt,zz];
bmdText=get "research/results/cube-exterior-pair-image-20260928/exterior-image.txt";
bmdRead=(prefix)->(
 linesFound:=select(lines bmdText,l->substring(0,#prefix,l)==prefix);
 assert(#linesFound==1);
 value substring(#prefix,first linesFound));
bmdMap=matrix bmdRead("EXTERIOR_MAP=");
bmdOldMinors=bmdRead("MAXIMAL_MINORS=");
bmdBase=ideal matrix bmdRead("SATURATED_GROEBNER_BASIS=");
assert({numrows bmdMap,numcols bmdMap}=={3,4} and #bmdOldMinors==4);
bmdM=3;bmdR=3;bmdAlpha=3/2;bmdBeta=bmdAlpha-bmdM+1;
bmdRise=(a,n)->if n==0 then 1_kk else product(toList(0..n-1),i->a+i);
bmdGamma=(j)->(-1)^j*bmdRise(bmdAlpha,j)/(j!);
bmdH=(j,x,y)->sum(toList(0..j),a->bmdGamma(a)*bmdGamma(j-a)*x^a*y^(j-a));
bmdSmallD=(j)->(-1)^j*(j!)/bmdRise(bmdBeta,j+2*bmdM);
bmdTriples={{1_R,tt,zz},{1_R,zz,tt},{tt,zz,1_R}};
bmdPhi=(j,x,y,z)->sum(toList(0..bmdM),a->
 binomial(bmdM,a)*(-z)^(bmdM-a)*bmdSmallD(j+a)*bmdH(j+a,x,y));
bmdLast=matrix apply(bmdTriples,p->{bmdPhi(bmdR+4,p#0,p#1,p#2)});
bmdAug=bmdMap|bmdLast;
bmdNewMinors=apply(subsets(toList(0..3),2),p->
 det submatrix(bmdAug,toList(0..2),append(p,4)));
assert(#bmdNewMinors==6);
<< "M=3 REUSED_MAP=exterior-image.txt ADDED_MARKED_COLUMN=4" << endl;
<< "MARKED_COLUMN=" << toString entries bmdLast << endl;
bmdExcluded=tt*zz*(1-tt)*(1-zz)*(tt-zz);
bmdV=(tt-1)*(zz-1)*(tt-zz);
bmdNewPrimitive=apply(bmdNewMinors,f->(q:=f//bmdV;assert(q*bmdV==f);q));
bmdBaseGB=gb bmdBase;
bmdReduced=apply(bmdNewPrimitive,f->f%bmdBaseGB);
<< "NEW_MINORS_MOD_FINITE_OBSTRUCTION=" << toString bmdReduced << endl;
bmdAugIdeal=bmdBase+ideal bmdReduced;
bmdAugGB=gb bmdAugIdeal;
<< "AUGMENTED_OBSTRUCTION_GROEBNER_BASIS=" << toString entries gens bmdAugGB << endl;
<< "AUGMENTED_SURJECTIVE_OFF_EXCLUDED_DIVISORS=" << (1_R%bmdAugGB==0) << endl;
<< "AUGMENTED_QUOTIENT_DIMENSION=" << dim(R/bmdAugIdeal) << endl;
<< "COMPLETED_EXACT_MARKED_COLUMN_TEST" << endl;
exit 0;
