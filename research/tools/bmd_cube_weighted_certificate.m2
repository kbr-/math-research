-- Verify the retained d=2 rational Hilbert--Burch certificate without recomputing
-- its expensive cube kernel.  The source generator/resolution file is complete.
-- This checks the maximal-minor ideal, codimension, homogeneity/minimality and
-- degree/arithmetic-genus accounting for its extension to four degree-one roots.
B=QQ[e_1..e_4,Degrees=>{1,2,3,4}];
certificateLines=separate("\n",get "research/results/cube-weighted-first-step-resolution-20260926/resolution-qq.txt");
readEntries=key -> (
    hits:=select(certificateLines,l -> substring(0,#key,l)==key);
    assert(#hits==1);
    value substring(#key,hits#0));
gensI=matrix readEntries "TOP_GENERATORS=";
d1=matrix readEntries "QUOTIENT_DIFFERENTIAL_1=";
d2=matrix readEntries "QUOTIENT_DIFFERENTIAL_2=";
I=ideal gensI;
assert(ideal d1==I);
assert(d1*d2==0);
assert(numrows d2==4 and numcols d2==3);
assert(minors(3,d2)==I);
assert(dim(B/I)==2);
assert(all(flatten entries d2, x -> x==0 or first degree x>0));
gd=sort apply(first entries gensI,x -> first degree x);
assert(gd=={12,13,14,15});
relDegrees=apply(toList(0..2),j -> unique apply(toList(0..3),i -> if d2_(i,j)==0 then null else first degree d2_(i,j)+first degree d1_(0,i)));
relDegrees=apply(relDegrees,L -> (L=select(L,x -> x=!=null); assert(#L==1); L#0));
assert(sort relDegrees=={17,18,19});
degCurve=(sum(relDegrees,b -> b^2)-sum(gd,a -> a^2))/2;
arithGenus=1-degCurve+(sum(relDegrees,b -> b*(b-1)*(b-2))-sum(gd,a -> a*(a-1)*(a-2)))/6;
assert(degCurve==120 and arithGenus==1021);
<< "PASS QQ Hilbert--Burch maximal minors equal complete top ideal; height=2" << endl;
<< "MINIMAL_GENERATOR_DEGREES=" << gd << " RELATION_DEGREES=" << sort relDegrees << endl;
<< "ORDINARY_ROOT_RING_CURVE_DEGREE=" << degCurve << " ARITHMETIC_GENUS=" << arithGenus << endl;
<< "PASS exactness by Hilbert--Burch and minimality by positive-degree entries" << endl;
exit 0;
