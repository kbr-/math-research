-- Exact falsifying test of the proposed all-M exterior-pair repair assertion:
-- after inverting exterior axes and pair differences, do the corrections
-- u^r L(u) P(u), deg P<=3, span all three exterior-pair rows?
-- M=3 is the smallest allowed internal size. This is one mechanism test,
-- not a threshold row or parameter series. The matrix is 3-by-4 over QQ[t,z],
-- with s=1 (allowed because s is inverted), entries of degree at most nine.
-- Stages: build the map by the proved binary finite-difference identity;
-- independently reconstruct all entries from the original pair functional;
-- compute its maximal minors and saturate away precisely the excluded divisors.
-- Unit saturation supports this one case; proper saturation refutes the
-- universal assertion. Neither result decides the actual forcing vector.
kk=QQ;
R=kk[tt,zz];
bmdM=3;bmdR=3;bmdAlpha=3/2;bmdBeta=bmdAlpha-bmdM+1;
bmdRise=(a,n)->if n==0 then 1_kk else product(toList(0..n-1),i->a+i);
bmdGamma=(j)->(-1)^j*bmdRise(bmdAlpha,j)/(j!);
bmdH=(j,x,y)->sum(toList(0..j),a->bmdGamma(a)*bmdGamma(j-a)*x^a*y^(j-a));
bmdSmallD=(j)->(-1)^j*(j!)/bmdRise(bmdBeta,j+2*bmdM);
bmdFactor=(-1)^bmdM*bmdRise(1-bmdAlpha,bmdM)*bmdRise(bmdAlpha,bmdM);
bmdTriples={{1_R,tt,zz},{1_R,zz,tt},{tt,zz,1_R}};
bmdPhi=(j,x,y,z)->sum(toList(0..bmdM),a->
 binomial(bmdM,a)*(-z)^(bmdM-a)*bmdSmallD(j+a)*bmdH(j+a,x,y));
bmdMap=matrix apply(bmdTriples,p->apply(toList(0..3),j->
 bmdPhi(bmdR+j,p#0,p#1,p#2)));
assert({numrows bmdMap,numcols bmdMap}=={3,4});
T=R[uu];
bmdL=(uu-1_T)^bmdM*(uu-sub(tt,T))^bmdM*(uu-sub(zz,T))^bmdM;
bmdLC=apply(toList(0..3*bmdM),a->sub(coefficient(uu^a,bmdL),R));
bmdF=(j,x,y)->(-1)^j*(j!)/bmdRise(bmdBeta,j)*bmdH(j,x,y);
for i from 0 to 2 do for j from 0 to 3 do (
 p:=bmdTriples#i;
 raw:=sum(toList(0..3*bmdM),a->bmdLC#a*bmdF(bmdR+j+a,p#0,p#1));
 assert(raw==(p#0*p#1)^bmdM*bmdFactor*bmdMap_(i,j));
 );
<< "M=3 r=3 s=1 MATRIX_SHAPE=3x4" << endl;
<< "DIRECT_FUNCTIONAL_RECONSTRUCTION=PASS" << endl;
<< "EXTERIOR_MAP=" << toString entries bmdMap << endl;
bmdMinors=flatten entries gens minors(3,bmdMap);
assert(#bmdMinors==4);
assert(any(bmdMinors,f->f!=0));
<< "MAXIMAL_MINORS=" << toString bmdMinors << endl;
bmdG=first bmdMinors;
scan(drop(bmdMinors,1),f->bmdG=gcd(bmdG,f));
<< "MINOR_GCD=" << toString factor bmdG << endl;
bmdPrimitive=apply(bmdMinors,f->(q:=f//bmdG;assert(q*bmdG==f);q));
<< "PRIMITIVE_MINORS=" << toString bmdPrimitive << endl;
bmdExcluded=tt*zz*(1-tt)*(1-zz)*(tt-zz);
-- The gcd may itself have a non-excluded factor; retain it in the ideal.
bmdIdeal=ideal bmdMinors;
bmdSat=saturate(bmdIdeal,ideal bmdExcluded);
<< "SATURATED_GROEBNER_BASIS=" << toString entries gens gb bmdSat << endl;
<< "SURJECTIVE_OFF_AXES_AND_COLLISIONS=" << (bmdSat==ideal(1_R)) << endl;
<< "SATURATED_QUOTIENT_DIMENSION=" << dim(R/bmdSat) << endl;
if bmdSat!=ideal(1_R) then << "SATURATED_QUOTIENT_DEGREE=" << degree(R/bmdSat) << endl;
<< "COMPLETED_EXACT_EXTERIOR_IMAGE_TEST" << endl;
exit 0;
