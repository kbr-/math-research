-- Exact H6/c2^e H6 Hilbert functions, using the complete parameter fibre.
-- The known A-generator bound33 gives end <=33+2(e-1), a proved cutoff.
-- Stages: universal low-weight lifts; actual harmonic columns modulo t^e;
-- graded QQ ranks; one faithful Tor correction at14+2e; PID length increments.
-- Stop when the increment equals rank48: every torsion exponent is then <e.
-- A finite requested stage cap is only a sizing guard, never a completeness claim.
-- Previously completed stages may be imported from a retained full output.
thClock=cpuTime();
thMax=value getenv "BMD_THICKENING_MAX";assert(thMax>=1 and thMax<=8);
thPriorPath=getenv "BMD_THICKENING_PRIOR";
thPrelude=separate("\n",get "research/tools/bmd_six_faithful_fibre_20261007.m2");
thStop=first select(toList(0..#thPrelude-1),i->substring(0,7,thPrelude#i)=="fibR=QQ");
thCode=concatenate apply(take(thPrelude,thStop),l->l|"\n");
thCode=replace("bmdBuildKernelSource\\(6,14\\)","bmdBuildKernelSource(6,"|toString(12+2*thMax)|")",thCode);
thCode=replace("from 9 to 14","from 9 to "|toString(12+2*thMax),thCode);
value thCode;
thSaved=separate("\n",get "research/results/bmd-six-faithful-fibre-20261007/certificate.txt");
thFibreLine=first select(thSaved,l->substring(0,11,l)=="FIBRE_STOP=");
thSavedDims=value last separate(" FIBRE_DIMENSIONS=",thFibreLine);
thPrior={};
if #thPriorPath>0 then (
    ls:=select(separate("\n",get thPriorPath),l->substring(0,16,l)=="THICKENING_DATA=");
    thPrior=apply(ls,l->value substring(16,l));
    assert(all(toList(0..#thPrior-1),i->(thPrior#i)#0==i+1));
);
thUpper=d->(
    if d<0 then 0 else (
        a:=max(d-8,0);m:=(d-4)//2;
        a+(if d>=4 then (m+1)*(m+2)//2 else 0)
    )
);
thImage=(e,d)->(
    #(select({12,13,13,14,14,15},w->d>=w and (d-w)%2==0 and d-w<2*e))
    +(if d==14 then 1 else 0)
);
thLength=if #thPrior==0 then 0 else sum((last thPrior)#1,x->x#1);
thPreviousIncrement=if #thPrior==0 then 184 else (
    thLength-(if #thPrior==1 then 0 else sum((thPrior#(#thPrior-2))#1,x->x#1))
);
for data in thPrior do << "THICKENING_DATA=" << toString data << endl;
thComplete=false;
for e from #thPrior+1 to thMax do (
    r:=fibS/ideal(fibS_0^e);cc:=gens r;sp:=map(r,fibS,cc);
    f:=r^(-fibFW);p:=r^(-fibVW);
    jj:=map(f,p,entries(sp fibJ));
    rr:=map(p,r^(-fibRW),entries(sp fibRel));
    low:=map(p,r^(-toList(11..14+2*thMax)),entries(sp fibLowLift));
    proj:=sp(fibData#"projection");pairs:=fibData#"pairs";
    powers:=apply(toList(0..5),j->submatrix(id_(r^6),,{j}));
    gam:={1_QQ};columns:=map(f,r^0,0);dims:={};
    for d from 11 to 31+2*e do (
        order:=d-2;
        while #powers<=order+1 do (
            n:=#powers;powers=append(powers,sum(toList(2..6),i->
                (-1)^(i+1)*cc#(i-2)*powers#(n-i)));
        );
        while #gam<=order do (
            n:=#gam;gam=append(gam,last(gam)*(-3/2-n+1)/n);
        );
        pair:=matrix table(15,1,(a,b)->(
            uv:=pairs#a;sum(toList(0..order),i->gam#i*gam#(order-i)*
                ((powers#i)_(uv#0,0)*(powers#(order-i+1))_(uv#1,0)
                 -(powers#i)_(uv#1,0)*(powers#(order-i+1))_(uv#0,0)))
        ));
        col:=map(f,r^{-d},entries(proj*pair));assert(isHomogeneous col);
        if order<=12+2*thMax then
            assert(entries col==entries(sp((fibData#"columns")#order)));
        columns=columns|col;
        fb:=basis(d,f);gbas:=basis(d,source columns);
        aa:=fibQQ(columns*gbas,fb);
        assert(numrows aa*numcols aa<=3000000);
        rk:=numcols gens gb aa;
        upper:=thUpper(d)-thUpper(d-2*e)+thImage(e,d);
        raw:=numcols fb-upper-rk;hidden:=0;
        if d==14+2*e then (
            pb:=basis(d,p);
            relq:=fibQQ(rr*basis(d,source rr),pb);
            lowq:=fibQQ(low*basis(d,source low),pb);
            jq:=fibQQ(jj*pb,fb);
            assert(jq*lowq==aa);
            assert(jq*relq==0);
            assert(numcols pb-numcols gens gb relq==numcols fb-upper+1);
            h:=numcols pb-numcols gens gb(relq|lowq);
            hidden=h-raw;assert(member(hidden,{0,1}));
        );
        h:=raw+hidden;assert(h>=0);
        if e==1 then (
            saved:=first select(thSavedDims,x->x#0==d);assert(h==saved#1);
        );
        dims=append(dims,{d,h});
        << "THICKENING e=" << e << " weight=" << d << " rows=" << numrows aa
           << " cols=" << numcols aa << " gammaRank=" << rk << " hidden=" << hidden
           << " quotient=" << h << " cpu=" << cpuTime()-thClock << endl << flush;
    );
    len:=sum(dims,x->x#1);increment:=len-thLength;
    assert(increment>=48 and increment<=thPreviousIncrement);
    << "THICKENING_DATA=" << toString {e,dims} << endl;
    << "THICKENING_LENGTH e=" << e << " length=" << len << " increment=" << increment
       << " torsionExponentsAtLeast=" << e << " count=" << increment-48
       << " cpu=" << cpuTime()-thClock << endl << flush;
    thLength=len;thPreviousIncrement=increment;
    if increment==48 then (
        thComplete=true;<< "TORSION_EXPONENT_BOUND=" << e-1 << endl << flush;break
    );
);
<< "PASS exact completed thickenings; torsion cutoff completed=" << thComplete
   << " cpu=" << cpuTime()-thClock << endl << flush;
exit 0;
