-- Exact rational ranks from modular lower certificates and proved upper bounds.
-- Image Gamma_e lies in ker(F_e -> E'_e), so rank <= dim F_e-dim E'_e,
-- as well as the column count. Equality with a modular rank proves QQ rank.
-- No modular deficiency is used as a rational rank upper bound.
-- Validate the sharpened stage3 window against archived QQ ranks, then continue the
-- same thickenings. Prior graded PID increments bound every next degree window.
-- Nonsaturated individual bounds remain upper Hilbert bounds. They become exact
-- collectively only if their length increment equals the known rank48 lower bound.
-- Otherwise abort without accepting the incomplete stage.
mbClock=cpuTime();
load "research/tools/bmd_six_kernel_model_20261007.m2";
mbData=bmdBuildKernelSource(6,14);mbS=mbData#"ring";mbFW=mbData#"weights";
mbPrior=getenv "BMD_THICKENING_PRIOR";
mbReference=separate("\n",get "research/results/bmd-six-torsion-thickenings-20261007/through-three.txt");
mbLines=if #mbPrior==0 then mbReference else separate("\n",get mbPrior);
mbStages=new MutableHashTable;
scan(mbLines,l->if substring(0,16,l)=="THICKENING_DATA=" then (
    v:=value substring(16,l);mbStages#(v#0)=v#1;
));
mbLast=max keys mbStages;
assert(sort keys mbStages==toList(1..mbLast));
if #mbPrior>0 then assert(any(mbLines,l->substring(0,17,l)=="PASS QQ_REFERENCE"));
mbOldRanks=new MutableHashTable;
scan(mbReference,l->if substring(0,#"THICKENING e=3 ",l)=="THICKENING e=3 " then (
    tok:=separate(" ",l);
    val:=i->value last separate("=",tok#i);
    mbOldRanks#(val 2)={val 3,val 4,val 5,val 6,val 7};
));
mbCoeff=(ls,d)->(
    hit:=select(ls,x->x#0==d);if #hit==0 then 0 else (first hit)#1
);
mbBirths=e->(
    prev:=if e==1 then {} else mbStages#(e-1);cur:=mbStages#e;
    vals:=apply(toList(0..60),d->{d-2*(e-1),mbCoeff(cur,d)-mbCoeff(prev,d)});
    assert(all(vals,x->x#1>=0));select(vals,x->x#1>0)
);
mbUpper=d->(
    if d<0 then 0 else (
        m:=(d-4)//2;max(d-8,0)+(if d>=4 then (m+1)*(m+2)//2 else 0)
    )
);
mbImage=(e,d)->(
    #(select({12,13,13,14,14,15},w->d>=w and (d-w)%2==0 and d-w<2*e))
    +(if d==14 then 1 else 0)
);
mbQQ=(mat,bas)->(
    co:=last coefficients(mat,Monomials=>bas);
    assert(entries(bas*co)==entries mat);sub(co,QQ)
);
mbPrime=1000003;mbField=ZZ/mbPrime;
mbDone=false;
mbFirst=if #mbPrior==0 then 3 else mbLast+1;
for e from 1 to mbFirst-1 do << "THICKENING_DATA=" << toString {e,mbStages#e} << endl;
for e from mbFirst to 12 do (
    uncertain:=false;
    prev:=mbStages#(e-1);birth:=mbBirths(e-1);
    previousEnd:=max apply(select(prev,x->x#1>0),x->x#0);
    bound:=max(previousEnd,max(apply(birth,x->x#0))+2*(e-1));
    assert(bound<=33+2*(e-1) and bound<=55);
    << "STAGE_BEGIN e=" << e << " degreeBound=" << bound << endl << flush;
    r:=mbS/ideal(mbS_0^e);cc:=gens r;sp:=map(r,mbS,cc);
    f:=r^(-mbFW);proj:=sp(mbData#"projection");pairs:=mbData#"pairs";
    powers:=apply(toList(0..5),j->submatrix(id_(r^6),,{j}));
    gam:={1_QQ};cols:=map(f,r^0,0);dims:={};
    for d from 11 to bound do (
        ord:=d-2;
        while #powers<=ord+1 do (
            q:=#powers;powers=append(powers,sum(toList(2..6),i->
                (-1)^(i+1)*cc#(i-2)*powers#(q-i)));
        );
        while #gam<=ord do (
            q:=#gam;gam=append(gam,last(gam)*(-3/2-q+1)/q);
        );
        pair:=matrix table(15,1,(a,b)->(
            uv:=pairs#a;sum(toList(0..ord),i->gam#i*gam#(ord-i)*
                ((powers#i)_(uv#0,0)*(powers#(ord-i+1))_(uv#1,0)
                 -(powers#i)_(uv#1,0)*(powers#(ord-i+1))_(uv#0,0)))
        ));
        col:=map(f,r^{-d},entries(proj*pair));assert(isHomogeneous col);
        if ord<=14 then assert(entries col==entries(sp((mbData#"columns")#ord)));
        cols=cols|col;fb:=basis(d,f);
        aa:=mbQQ(cols*basis(d,source cols),fb);
        assert(numrows aa*numcols aa<=3000000);
        upper:=mbUpper(d)-mbUpper(d-2*e)+mbImage(e,d);
        rankBound:=min(numcols aa,numrows aa-upper);
        assert(rankBound>=0);
        assert(all(flatten entries aa,x->denominator(x)%mbPrime!=0));
        lower:=rank sub(aa,mbField);
        assert(lower<=rankBound);
        if lower!=rankBound then (
            uncertain=true;
            << "RANK_INTERVAL e=" << e << " degree=" << d << " modularLower=" << lower
               << " rationalUpper=" << rankBound << endl << flush;
        );
        hidden:=0;
        if d==14+2*e then (
            -- Injectivity of this whole free column space also excludes a
            -- hidden kernel in its image in V_e. The Tor class therefore survives.
            if lower!=numcols aa then uncertain=true;
            hidden=1;
        );
        h:=numrows aa-upper-lower+hidden;assert(h>=0);
        if e==3 then (
            assert(mbOldRanks#d=={numrows aa,numcols aa,lower,hidden,h});
            assert(h==mbCoeff(mbStages#3,d));
        );
        dims=append(dims,{d,h});
        << "RANK_DATA e=" << e << " degree=" << d << " rows=" << numrows aa
           << " cols=" << numcols aa << " rank=" << lower << " upper=" << rankBound
           << " hidden=" << hidden << " quotient=" << h
           << " cpu=" << cpuTime()-mbClock << endl << flush;
    );
    if e==3 then (
        assert(all(mbStages#3,x->x#1==mbCoeff(dims,x#0)));
        dims=mbStages#3;
        << "PASS QQ_REFERENCE all repeated stage3 ranks and hidden correction matched" << endl << flush;
    );
    mbStages#e=dims;
    b:=mbBirths e;oldBirth:=mbBirths(e-1);
    assert(all(b,x->x#1<=mbCoeff(oldBirth,x#0)));
    len:=sum(dims,x->x#1);increment:=len-sum(prev,x->x#1);
    assert(increment==sum(b,x->x#1) and increment>=48);
    if uncertain then (
        assert(increment==48);
        << "PASS GLOBAL_RANK_SQUEEZE upper increment48 equals the rank lower bound; all degree bounds exact" << endl << flush;
    );
    << "THICKENING_DATA=" << toString {e,dims} << endl;
    << "SURVIVING_BIRTHS e=" << e << " DATA=" << toString b << endl;
    << "THICKENING_LENGTH e=" << e << " length=" << len << " increment=" << increment
       << " remainingTorsion=" << increment-48 << " cpu=" << cpuTime()-mbClock << endl << flush;
    if increment==48 then (
        mbDone=true;<< "FREE_BIRTHS=" << toString b << endl;
        for j from 1 to e-1 do (
            bj:=mbBirths j;bn:=mbBirths(j+1);
            tj:=select(apply(bj,x->{x#0,x#1-mbCoeff(bn,x#0)}),x->x#1>0);
            << "TORSION_EXPONENT=" << j << " BIRTHS=" << toString tj << endl;
        );
        << "TORSION_EXPONENT_BOUND=" << e-1 << endl << flush;break;
    );
);
assert(mbDone);
<< "PASS complete graded Smith data from exact rank bounds; prime=" << mbPrime
   << " cpu=" << cpuTime()-mbClock << endl << flush;
exit 0;
