-- Test the general hypothesis Supp(K2) subset the quintuple closure.
-- Work at N=6, where the (4,2) and (3,3) strata first occur. A positive
-- full-defect/rigid-upper-quotient dimension difference on the first-order
-- Artin neighbourhood proves residual survival. Zero is NOT vanishing of K2.
-- Stop once a positive residual is detected; do not add a dimension series.
-- Stages: import the reviewed extension cocycle; verify its cocycle identity;
-- form the full pair connection over the first-order coefficient algebra;
-- exact finite QQ invariant-span closure; compare with the pushout quotient.
-- Central-fibre controls check dimension4 and reject the split extension.
-- Maximum QQ sizes: full ambient90, upper ambient72, upper relations72.
-- Full stdout is the certificate and must be retained with save-run-output.py.

resClock=cpuTime();
resCert="research/results/cube-six-root-extension-test-20260927/extension-certificate.txt";
resLines=separate("\n",get resCert);
resStart=first select(toList(0..#resLines-1),i->substring(0,4,resLines#i)=="N=6 ");
resData=drop(resLines,resStart);
resLine=tag->substring(#tag,first select(resData,l->substring(0,#tag,l)==tag));
resS=QQ[c_2..c_6,Degrees=>{2,3,4,5,6}];
resD1=matrix value resLine "D1=";
resD2=matrix value resLine "D2=";
assert(numrows resD1==6 and numcols resD1==12 and numcols resD2==6);
assert(resD1*resD2==0);
resB=QQ[b,c];
resCV=value first separate(" DRIFT=",resLine "LOWER_COEFFICIENT_MAP=");
resSB=map(resB,resS,resCV);
resCoords=value first separate(" CROSS_COORDINATES=",resLine "PHI_COORDINATES=");
resSol=flatten value resLine "JOINT_KERNEL=";
assert(#resCoords==42 and #resSol==43 and last resSol==1);
resPhi=matrix{apply(toList(0..11),j->sum(select(toList(0..41),i->(resCoords#i)#0==j),i->resSol#i*(resCoords#i)#1))};
assert(resPhi*(resSB resD2)==0);
assert(resPhi_(0,0)==-28/43);
<< "CERTIFICATE_SOURCE=" << resCert << endl;
<< "IMPORTED_PHI=" << toString entries resPhi << endl;

resPairs=flatten apply(toList(0..5),i->apply(toList(i+1..5),j->{i,j}));
assert(#resPairs==15 and first resPairs=={0,1});
resWeights=apply(resPairs,p->p#0+p#1+1);
resFound=false;
resCases={{{-1_QQ,-1_QQ,-1_QQ,-1_QQ,2_QQ,2_QQ},1_QQ,"42"},
          {{-1_QQ,-1_QQ,-1_QQ,1_QQ,1_QQ,1_QQ},0_QQ,"33"}};
for testCase in resCases do if not resFound then (
    roots:=testCase#0;lam:=testCase#1;label:=testCase#2;
    pp:={1_QQ};
    for rr in roots do pp=apply(toList(0..#pp),i->
        (if i<#pp then pp#i else 0_QQ)-rr*(if i>0 then pp#(i-1) else 0_QQ));
    assert(pp#1==0);
    base:=apply(toList(2..6),i->(-1)^i*pp#i);
    for order in {0,1} do (
        amb:=QQ[ee_2..ee_6];ee:=gens amb;
        art:=amb/((ideal ee)^(order+1));
        artMons:=if order==0 then {1_art} else prepend(1_art,gens art);
        artLiftMons:=apply(artMons,m->lift(m,amb));
        aa:=#artMons;
        assert(aa==(if order==0 then 1 else 6));
        cv:=apply(toList(0..4),i->sub(base#i,art)+art_i);
        intoArt:=map(art,resS,cv);
        cap:=cv#0/3;
        drift:=apply(toList(2..6),j->
            (if j<6 then (j+1)*cv#(j-1) else 0_art)-
            cap*(7-j)*(if j>2 then cv#(j-3) else 0_art)+lam*j*cv#(j-2));
        assert(all(drift,f->sub(lift(f,amb),apply(ee,e->e=>0_QQ))==0));
        da:=f->sum(toList(0..4),i->drift#i*sub(diff(ee#i,lift(f,amb)),art));
        assert(all(ee,e->da((sub(e,art))^2)==0));
        enc:=mat->matrix table(aa*numrows mat,numcols mat,(i,j)->
            lift(coefficient(artLiftMons#(i//numrows mat),lift(mat_(i%numrows mat,j),amb)),QQ));
        -- Root connection - (i+1/2) Z^(i+1) - i*kappa Z^(i-1), reduced by p.
        zPowers:=apply(toList(0..5),j->submatrix(id_(art^6),,{j}));
        z6:=matrix{apply(toList(0..5),i->-(if 6-i>=2 then (-1)^(6-i)*cv#(4-i) else 0_art))};
        z6=transpose z6;
        rootConn:=fold((u,v)->u|v,apply(toList(0..5),j->
            -(j+1/2)*(if j<5 then zPowers#(j+1) else z6)-
            (if j>0 then j*cap*zPowers#(j-1) else map(art^6,art^1,0))));
        pairConn:=matrix table(15,15,(row,col)->(
            ab:=resPairs#row;ij:=resPairs#col;
            (if ab#1==ij#1 then rootConn_(ab#0,ij#0) else 0_art)-
            (if ab#0==ij#1 then rootConn_(ab#1,ij#0) else 0_art)+
            (if ab#0==ij#0 then rootConn_(ab#1,ij#1) else 0_art)-
            (if ab#1==ij#0 then rootConn_(ab#0,ij#1) else 0_art)+
            (if row==col then lam*resWeights#row else 0_art)
        ));
        con:=vv->matrix apply(entries vv,row->apply(row,f->da f))+pairConn*vv;
        artBasisVectors:=flatten apply(artMons,m->apply(toList(0..14),j->m*submatrix(id_(art^15),,{j})));
        connQQ:=fold((u,v)->u|v,apply(artBasisVectors,vv->enc con vv));
        start:=fold((u,v)->u|v,apply(artMons,m->enc(m*submatrix(id_(art^15),,{0}))));
        span:=map(QQ^(15*aa),QQ^0,0);block:=start;stable:=false;steps:=0;rrank:=0;
        while not stable do (
            newer:=span|block;newrank:=rank newer;
            if newrank==rrank then stable=true else (
                span=newer;rrank=newrank;block=connQQ*block;
            );
            steps=steps+1;assert(steps<=15*aa+1);
        );
        assert(rank(span|connQQ*span)==rrank);
        for em in gens art do (
            mult:=fold((u,v)->u|v,apply(artBasisVectors,vv->enc(em*vv)));
            assert(rank(span|mult*span)==rrank);
        );
        cdim:=15*aa-rrank;
        -- The retained nonzero cocycle defines the rigid upper quotient.
        bAmb:=QQ[bb,cc,zz_2..zz_6];zz:=drop(gens bAmb,2);
        bInto:=map(bAmb,resB,{bAmb_0,bAmb_1});
        eqs:=join(apply(toList(0..4),i->bInto(resCV#i)-base#i-zz#i),
            flatten entries gens((ideal zz)^(order+1)));
        bArt:=bAmb/ideal eqs;
        assert(dim bArt==0);
        bBasis:=flatten entries basis bArt;
        bBasisLift:=apply(bBasis,m->lift(m,bAmb));
        nb:=#bBasis;assert(nb<=6*aa);
        artIntoB:=map(bArt,art,drop(gens bArt,2));
        phiB:=(map(bArt,resB,{bArt_0,bArt_1})) resPhi;
        d1a:=intoArt resD1;
        encB:=f->matrix table(nb,1,(i,j)->lift(coefficient(bBasisLift#i,lift(f,bAmb)),QQ));
        for f in flatten entries phiB do (
            co:=encB f;
            assert(sum(toList(0..nb-1),i->sub(co_(i,0),bArt)*bBasis#i)==f);
        );
        relCols:=flatten apply(artMons,m->apply(toList(0..11),j->
            encB(-artIntoB(m)*phiB_(0,j))||enc(m*submatrix(d1a,,{j}))));
        relations:=fold((u,v)->u|v,relCols);
        erank:=rank relations;edim:=nb+6*aa-erank;
        assert(numrows relations<=72 and numcols relations<=72);
        normRank:=rank fold((u,v)->u|v,apply(artMons,m->enc(m*d1a)));
        ddim:=6*aa-normRank;splitdim:=nb+ddim;
        assert(cdim>=edim and edim>=ddim);
        if order==0 then assert(cdim==4 and edim==4 and splitdim>edim);
        << "CASE=" << label << " ORDER=" << order << " ROOTS=" << roots << " LAMBDA=" << lam << " COEFFICIENTS=" << base << endl;
        << "ARTIN_DRIFT=" << toString drift << " ARTIN_BASIS=" << toString artMons << endl;
        << "PAIR_CONNECTION_QQ=" << toString entries connQQ << endl;
        << "CYCLIC_SPAN_QQ=" << toString entries span << endl;
        << "LOWER_ARTIN_IDEAL=" << toString eqs << " LOWER_BASIS=" << toString bBasis << endl;
        << "UPPER_RELATIONS_QQ=" << toString entries relations << endl;
        << "RESULT case=" << label << " order=" << order << " artinLength=" << aa
           << " fullAmbient=" << 15*aa << " fullRank=" << rrank << " fullDefect=" << cdim
           << " upperAmbient=" << nb+6*aa << " upperRank=" << erank << " upperDefect=" << edim
           << " normalization=" << ddim << " lower=" << nb << " split=" << splitdim
           << " residualImage=" << cdim-edim << " closureSteps=" << steps << endl << flush;
        if order==1 and cdim>edim then resFound=true;
    );
);
<< "TEST_FINISHED residualDetected=" << resFound << " cpu=" << cpuTime()-resClock << endl << flush;
exit 0;
