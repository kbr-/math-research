-- Diagnostic after complete polynomial/local closures exceeded bounded runs.
-- Reuse the reviewed full-coefficient Artin model and actual upper extension.
-- Only the triple-triple core is tested. Orders0,1 are controls; continue only
-- through the first unchecked two orders, stopping immediately on a positive
-- residual image. A positive result proves support in every N by spectators;
-- zero remains inconclusive and no full transverse length is inferred.
-- Maximum four-row QQ ambient224, upper matrices672. No new root count.
resSource=separate("\n",get "research/tools/bmd_cube_residual_first_order.m2");
resEnd=first select(toList(0..#resSource-1),i->substring(0,9,resSource#i)=="resPairs=");
value concatenate apply(take(resSource,resEnd),s->s|"\n");
resPairs=flatten apply(toList(0..5),i->apply(toList(i+1..5),j->{i,j}));
resWeights=apply(resPairs,p->p#0+p#1+1);
resCases={{{-1_QQ,-1_QQ,-1_QQ,1_QQ,1_QQ,1_QQ},0_QQ,"33",20}};
resFound=false;
for testCase in resCases do if not resFound then (
    roots:=testCase#0;lam:=testCase#1;label:=testCase#2;
    pp:={1_QQ};
    for rr in roots do pp=apply(toList(0..#pp),i->
        (if i<#pp then pp#i else 0_QQ)-rr*(if i>0 then pp#(i-1) else 0_QQ));
    base:=apply(toList(2..6),i->(-1)^i*pp#i);
    for jetOrder in {0,1,2,3} do if not resFound then (
        amb:=QQ[ee_2..ee_6];ee:=gens amb;art:=amb/((ideal ee)^(jetOrder+1));
        artMons:=flatten entries basis art;aa:=#artMons;
        artLiftMons:=apply(artMons,m->lift(m,amb));
        assert(aa==binomial(5+jetOrder,5));
        cv:=apply(toList(0..4),i->sub(base#i,art)+art_i);
        intoArt:=map(art,resS,cv);cap:=cv#0/3;
        aug:=map(QQ,art,toList(5:0_QQ));
        drift:=apply(toList(2..6),j->
            (if j<6 then (j+1)*cv#(j-1) else 0_art)-
            cap*(7-j)*(if j>2 then cv#(j-3) else 0_art)+lam*j*cv#(j-2));
        assert(all(drift,f->aug(f)==0));
        da:=f->sum(toList(0..4),i->drift#i*sub(diff(ee#i,lift(f,amb)),art));
        enc:=mat->matrix table(aa*numrows mat,numcols mat,(i,j)->
            lift(coefficient(artLiftMons#(i//numrows mat),lift(mat_(i%numrows mat,j),amb)),QQ));
        zPowers:=apply(toList(0..5),j->submatrix(id_(art^6),,{j}));
        z6:=transpose matrix{apply(toList(0..5),i->-(if 6-i>=2 then (-1)^(6-i)*cv#(4-i) else 0_art))};
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
        vv:=submatrix(id_(art^15),,{0});cycCols:={};
        for j from 0 to 10 do (cycCols=append(cycCols,vv);vv=con vv;);
        cyc:=fold((u,v)->u|v,cycCols);constantCyc:=aug cyc;
        assert(rank constantCyc==11);
        completion:=constantCyc;
        for j from 0 to 14 do if numcols completion<15 then (
            trial:=completion|submatrix(id_(QQ^15),,{j});
            if rank trial>numcols completion then completion=trial;
        );
        assert(numcols completion==15 and rank completion==15);
        invCompletion:=(id_(QQ^15))//completion;
        assert(invCompletion*completion==id_(QQ^15));
        change:=sub(invCompletion,art);liftCore:=sub(submatrix(completion,,toList(11..14)),art);
        transformed:=change*cyc;unitBlock:=submatrix(transformed,toList(0..10),);
        bottom:=submatrix(transformed,toList(11..14),);
        nn:=unitBlock-id_(art^11);unitInv:=id_(art^11);term:=id_(art^11);
        for j from 1 to jetOrder do (term=-term*nn;unitInv=unitInv+term;);
        assert(unitBlock*unitInv==id_(art^11));
        project:=((-bottom*unitInv)|id_(art^4))*change;
        assert(project*cyc==0 and project*liftCore==id_(art^4));
        coreMarker:=project*vv;
        projectedConn:=project*con(cyc);expectedConn:=map(art^4,art^10,0)|coreMarker;
        if entries projectedConn!=entries expectedConn then (
            << "PROJECTION_CONNECTION_RESIDUAL=" << toString entries(matrix entries projectedConn-matrix entries expectedConn) << endl << flush;
        );
        assert(entries projectedConn==entries expectedConn);
        coreConn:=project*pairConn*liftCore;
        coreCon:=v->matrix apply(entries v,row->apply(row,f->da f))+coreConn*v;
        artBasisVectors:=flatten apply(artMons,m->apply(toList(0..3),j->m*submatrix(id_(art^4),,{j})));
        connQQ:=fold((u,v)->u|v,apply(artBasisVectors,v->enc coreCon v));
        block:=fold((u,v)->u|v,apply(artMons,m->enc(m*coreMarker)));
        span:=map(QQ^(4*aa),QQ^0,0);stable:=false;steps:=0;rrank:=0;
        while not stable do (
            newer:=span|block;newrank:=rank newer;
            if newrank==rrank then stable=true else (span=newer;rrank=newrank;block=connQQ*block;);
            steps=steps+1;assert(steps<=4*aa+1);
        );
        assert(rank(span|connQQ*span)==rrank);
        for em in gens art do (
            mult:=fold((u,v)->u|v,apply(artBasisVectors,v->enc(em*v)));
            assert(rank(span|mult*span)==rrank);
        );
        cdim:=4*aa-rrank;
        -- Eliminate the Artin epsilon variables from the lower algebra first.
        changes:=apply(toList(0..4),i->resCV#i-base#i);
        bArt:=resB/((ideal changes)^(jetOrder+1));
        assert(dim bArt==0);
        bBasis:=flatten entries basis bArt;bLift:=apply(bBasis,m->lift(m,resB));
        nb:=#bBasis;assert(nb<=6*aa);
        artIntoB:=map(bArt,art,apply(changes,f->sub(f,bArt)));
        phiB:=sub(resPhi,bArt);d1a:=intoArt resD1;
        encB:=f->matrix table(nb,1,(i,j)->lift(coefficient(bLift#i,lift(f,resB)),QQ));
        for f in flatten entries phiB do (
            co:=encB f;assert(sum(toList(0..nb-1),i->sub(co_(i,0),bArt)*bBasis#i)==f);
        );
        relCols:=flatten apply(artMons,m->apply(toList(0..11),j->
            encB(-artIntoB(m)*phiB_(0,j))||enc(m*submatrix(d1a,,{j}))));
        relations:=fold((u,v)->u|v,relCols);erank:=rank relations;edim:=nb+6*aa-erank;
        assert(numrows connQQ<=224 and numrows relations<=672 and numcols relations<=672);
        normRank:=rank fold((u,v)->u|v,apply(artMons,m->enc(m*d1a)));
        ddim:=6*aa-normRank;splitdim:=nb+ddim;
        assert(cdim>=edim and edim>=ddim);
        if jetOrder==0 then assert(cdim==4 and edim==4 and splitdim>edim);
        if jetOrder==1 then assert(cdim==testCase#3 and edim==testCase#3);
        << "CASE=" << label << " ORDER=" << jetOrder << " ROOTS=" << roots << " COEFFICIENTS=" << base << endl;
        << "ARTIN_BASIS=" << toString artMons << " DRIFT=" << toString drift << endl;
        << "LOCAL_PROJECTION=" << toString entries project << " LOCAL_MARKER=" << toString entries coreMarker << endl;
        << "CORE_CONNECTION_QQ=" << toString entries connQQ << endl;
        << "CORE_CYCLIC_SPAN_QQ=" << toString entries span << endl;
        << "LOWER_BASE_IDEAL=" << toString changes << " POWER=" << jetOrder+1 << " LOWER_BASIS=" << toString bBasis << endl;
        << "UPPER_RELATIONS_QQ=" << toString entries relations << endl;
        << "RESULT case=" << label << " order=" << jetOrder << " artinLength=" << aa
           << " coreAmbient=" << 4*aa << " coreRank=" << rrank << " fullDefect=" << cdim
           << " upperAmbient=" << nb+6*aa << " upperRank=" << erank << " upperDefect=" << edim
           << " normalization=" << ddim << " lower=" << nb << " split=" << splitdim
           << " residualImage=" << cdim-edim << " closureSteps=" << steps << endl << flush;
        if jetOrder>=2 and cdim>edim then resFound=true;
    );
);
<< "SECOND_ORDER_FINISHED residualDetected=" << resFound << " cpu=" << cpuTime()-resClock << endl << flush;
exit 0;
