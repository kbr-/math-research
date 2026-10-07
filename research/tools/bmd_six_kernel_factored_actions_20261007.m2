-- Exact factored rational A-presentation and four actions for H6.
-- Every frame is an explicitly recorded nonsingular rational matrix L_d[R_d,:].
-- No unevaluated unknown solution: its inverse defines the exact coefficient
-- matrices. The full finite source and proved Hilbert dimensions certify each
-- coordinate identity over QQ; a second prime checks the entire implementation.
-- Stages: universal polynomial source; minimal A-generators by certified pivots;
-- rational frame recipes through40; minimal relations through40; four actions
-- through39; small expanded QQ controls; complete two-prime action identities.
faClock=cpuTime();
faCap=value getenv "BMD_ACTION_CAP";assert(member(faCap,{20,40}));
load "research/tools/bmd_six_full_action_source_20261007.m2";
faS=abS;faF=abF;faT=faS_0;faGamma=abGamma;
faRead=(ls,tag)->substring(#tag,first select(ls,l->substring(0,#tag,l)==tag));
faLines=separate("\n",get "research/results/bmd-six-kernel-map-20261007/certificate.txt");
faVW=value faRead(faLines,"PREIMAGE_GENERATOR_WEIGHTS=");
faP=faS^(-faVW);
faV=map(faF,faP,entries matrix value faRead(faLines,"PREIMAGE_MAP="));
faUpper=d->(
    if d<0 then 0 else (
        m:=(d-4)//2;max(d-8,0)+(if d>=4 then (m+1)*(m+2)//2 else 0)
    )
);
faImage=d->(#select({12,13,13,14,14,15},w->d>=w and (d-w)%2==0)
    +(if d==14 then 1 else 0));
faH=d->(
    sum(abFree,b->if d>=b#0 and (d-b#0)%2==0 then b#1 else 0)+
    sum(abTor,row->sum(row#1,b->if d>=b#0 and (d-b#0)%2==0 and d-b#0<2*row#0 then b#1 else 0))
);
faGen=d->sum(abFree,b->if b#0==d then b#1 else 0)+
    sum(abTor,row->sum(row#1,b->if b#0==d then b#1 else 0));
faRel=d->sum(abTor,row->sum(row#1,b->if b#0+2*row#0==d then b#1 else 0));
faQQ=(mat,bas)->(
    if numcols mat==0 then map(QQ^(numcols bas),QQ^0,0) else (
        co:=last coefficients(mat,Monomials=>bas);
        assert(entries(bas*co)==entries mat);sub(co,QQ)
    )
);
faMod=(mat,k)->(assert(all(flatten entries mat,x->denominator(x)%(char k)!=0));sub(mat,k));
faProfile=mat->columnRankProfile mutableMatrix(mat,Dense=>true);
faRows=mat->rowRankProfile mutableMatrix(mat,Dense=>true);
faDesc=bas->apply(toList(0..numcols bas-1),j->(
    row:=first select(toList(0..numrows bas-1),i->bas_(i,j)!=0);
    assert(#terms(bas_(row,j))==1 and leadCoefficient(bas_(row,j))==1);
    {row,first exponents(bas_(row,j))}
));
faG=map(faF,faS^0,0);faWeights={};faFrames=new MutableHashTable;
faRelationRecipes={};faRelationWeights={};
for faPrime in {1000003,1000033} do (
    assert(isPrime faPrime);
    k:=ZZ/faPrime;
    act:=apply(toList(1..4),j->mutableMatrix(k,184,184,Dense=>true));
    relValues:=mutableMatrix(k,184,136,Dense=>true);relCount:=0;
    for d from 15 to faCap do (
        fb:=basis(d,faF);cb:=basis(d,source faGamma);
        gammaQ:=faQQ(faGamma*cb,fb);
        assert(numrows gammaQ*numcols gammaQ<=3500000);
        assert(all(flatten entries gammaQ,x->denominator(x)%faPrime!=0));
        gammaK:=sub(gammaQ,k);
        h:=faH d;grank:=numcols fb-faUpper(d)-faImage(d)-h;
        assert(grank>=0);
        gp:=if faPrime==1000003 then faProfile gammaK else (faFrames#d)#0;
        assert(#gp==grank);
        gbQ:=submatrix(gammaQ,,gp);gbK:=submatrix(gammaK,,gp);
        if faPrime==1000003 and d<=33 then (
            oldIndices:=select(toList(0..#faWeights-1),i->d>=faWeights#i and (d-faWeights#i)%2==0);
            old:=if #oldIndices==0 then map(faF,faS^0,0) else fold((a,b)->a|b,
                apply(oldIndices,i->faT^((d-faWeights#i)//2)*submatrix(faG,,{i})));
            oldQ:=faQQ(old,fb);vb:=basis(d,faP);vcols:=faV*vb;vQ:=faQQ(vcols,fb);
            combined:=gbK|faMod(oldQ,k)|faMod(vQ,k);
            pivots:=faProfile combined;
            assert(#pivots==grank+h);
            prefix:=grank+#oldIndices;
            assert(take(pivots,prefix)==toList(0..prefix-1));
            fresh:=apply(drop(pivots,prefix),i->i-prefix);
            assert(#fresh==faGen d);
            if #fresh>0 then (
                newCols:=map(faF,faS^(apply(fresh,i->-d)),entries submatrix(vcols,,fresh));
                assert(isHomogeneous newCols);faG=faG|newCols;
                faWeights=faWeights|apply(fresh,i->d);
                desc:=faDesc submatrix(vb,,fresh);
                << "A_GENERATOR_SOURCES degree=" << d << " DATA=" << toString desc << endl;
            );
        );
        ai:=select(toList(0..#faWeights-1),i->d>=faWeights#i and (d-faWeights#i)%2==0);
        acol:=if #ai==0 then map(faF,faS^0,0) else fold((a,b)->a|b,
            apply(ai,i->faT^((d-faWeights#i)//2)*submatrix(faG,,{i})));
        aq:=faQQ(acol,fb);ak:=faMod(aq,k);
        hp:=if faPrime==1000003 then (
            pivots:=faProfile(gbK|ak);
            assert(#pivots==grank+h and take(pivots,grank)==toList(0..grank-1));
            apply(drop(pivots,grank),i->i-grank)
        ) else (faFrames#d)#1;
        assert(#hp==h);
        lq:=gbQ|submatrix(aq,,hp);lk:=faMod(lq,k);
        rows:=if faPrime==1000003 then faRows lk else (faFrames#d)#2;
        assert(#rows==grank+h);
        rhsQ:=aq;groups:={};offset:=#ai;
        for j from 3 to 6 do (
            js:=select(toList(0..#faWeights-1),i->faWeights#i+j==d);
            groups=append(groups,{j,js,offset});offset=offset+#js;
            if #js>0 then rhsQ=rhsQ|faQQ(faS_(j-2)*submatrix(faG,,js),fb);
        );
        rhsK:=faMod(rhsQ,k);
        sq:=submatrix(lk,rows,);
        sol:=matrix solve(mutableMatrix(sq,Dense=>true),
            mutableMatrix(submatrix(rhsK,rows,),Dense=>true),Invertible=>true);
        assert(lk*sol==rhsK);
        if faPrime==1000003 and d<=20 then (
            solQ:=submatrix(rhsQ,rows,)//submatrix(lq,rows,);
            assert(lq*solQ==rhsQ);
            << "QQ_FRAME_CONTROL degree=" << d << " columns=" << numcols rhsQ << endl;
        );
        qcoords:=submatrix(sol,toList(grank..grank+h-1),);
        qa:=submatrix(qcoords,,toList(0..#ai-1));
        for group in groups do (
            j:=group#0;js:=group#1;off:=group#2;
            scan(toList(0..#js-1),c->scan(toList(0..h-1),r->
                (act#(j-3))_(ai#(hp#r),js#c)=qcoords_(r,off+c)));
        );
        if d>=34 then (
            nonpivot:=select(toList(0..#ai-1),i->not member(i,hp));
            candidates:=matrix table(#ai,#nonpivot,(r,c)->
                (if r==nonpivot#c then 1_k else 0_k)
                -(if member(r,hp) then qa_(position(hp,i->i==r),nonpivot#c) else 0_k));
            assert(qa*candidates==0);
            oldRelIndices:=select(toList(0..relCount-1),i->(d-faRelationWeights#i)%2==0);
            oldRel:=submatrix(matrix relValues,ai,oldRelIndices);
            if faPrime==1000003 then (
                pivots:=faProfile(oldRel|candidates);
                assert(#pivots==#ai-h and take(pivots,#oldRelIndices)==toList(0..#oldRelIndices-1));
                choices:=apply(drop(pivots,#oldRelIndices),i->i-#oldRelIndices);
                assert(#choices==faRel d);
                scan(choices,c->(
                    scan(toList(0..#ai-1),r->relValues_(ai#r,relCount)=candidates_(r,c));
                    faRelationRecipes=append(faRelationRecipes,{d,ai#(nonpivot#c)});
                    faRelationWeights=append(faRelationWeights,d);relCount=relCount+1;
                ));
            ) else (
                chosen:=select(faRelationRecipes,x->x#0==d);
                selected:=apply(chosen,x->position(nonpivot,c->ai#c==x#1));
                assert(all(selected,x->x=!=null));
                newRel:=submatrix(candidates,,selected);
                assert(#(faProfile(oldRel|newRel))==#ai-h);
                scan(selected,c->(
                    scan(toList(0..#ai-1),r->relValues_(ai#r,relCount)=candidates_(r,c));
                    relCount=relCount+1;
                ));
            );
        );
        if faPrime==1000003 then (
            faFrames#d={gp,hp,rows};
            << "FRAME degree=" << d << " gammaRank=" << grank << " kernelDimension=" << h << endl;
            << "FRAME_F_BASIS=" << toString(faDesc fb) << endl;
            << "FRAME_CYCLIC_BASIS=" << toString(faDesc cb) << endl;
            << "FRAME_GAMMA_COLUMNS=" << toString gp << endl;
            << "FRAME_A_COLUMNS=" << toString ai << endl;
            << "FRAME_H_COLUMNS=" << toString hp << endl;
            << "FRAME_PIVOT_ROWS=" << toString rows << endl;
        );
        << "FRAME_PASS prime=" << faPrime << " degree=" << d << " size=" << #rows
           << " A_generators=" << #faWeights << " A_relations=" << relCount
           << " cpu=" << cpuTime()-faClock << endl << flush;
    );
    if faCap==40 then (
        assert(#faWeights==184 and relCount==136);
        ar:=k[tt,Degrees=>{2}];t:=ar_0;
        pres:=matrix table(184,136,(i,j)->(
            v:=relValues_(i,j);
            if v==0 then 0_ar else (
                power:=faRelationWeights#j-faWeights#i;
                assert(power>=0 and power%2==0);sub(v,ar)*t^(power//2)
            )
        ));
        ops:=apply(toList(3..6),j->matrix table(184,184,(r,c)->(
            v:=(act#(j-3))_(r,c);
            if v==0 then 0_ar else (
                power:=faWeights#c+j-faWeights#r;
                assert(power>=0 and power%2==0);sub(v,ar)*t^(power//2)
            )
        )));
        rp:=gb pres;
        scan(ops,op->assert((op*pres)%rp==0));
        for i from 0 to 3 do for j from i+1 to 3 do assert((ops#i*ops#j-ops#j*ops#i)%rp==0);
        pg:=ar^(-faWeights);rg:=map(pg,ar^(-faRelationWeights),entries pres);
        assert(isHomogeneous rg);
        dr:=degreesRing ar;z:=dr_0;
        wanted:=sum(abFree,b->b#1*z^(b#0))+
            sum(abTor,row->sum(row#1,b->b#1*(z^(b#0)-z^(b#0+2*row#0))));
        assert(poincare coker rg==wanted);
        << "PASS COMPLETE_FIELD_ACTIONS prime=" << faPrime
           << " relationPreservation=4 commutators=6 Hilbert=matched cpu=" << cpuTime()-faClock << endl << flush;
    );
);
<< "A_GENERATOR_WEIGHTS=" << toString faWeights << endl;
<< "A_GENERATOR_IMAGES=" << toString entries faG << endl;
<< "A_RELATION_RECIPES=" << toString faRelationRecipes << endl;
<< "A_RELATION_WEIGHTS=" << toString faRelationWeights << endl;
<< "CYCLIC_COLUMNS=" << toString entries faGamma << endl;
<< "PASS exact factored rational frame certificate cap=" << faCap
   << " complete=" << (faCap==40) << " cpu=" << cpuTime()-faClock << endl << flush;
exit 0;
