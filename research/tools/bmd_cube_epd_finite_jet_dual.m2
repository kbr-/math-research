-- Decide finite-jet realizability for one functional on the actual transverse
-- Artin defect. This is a finite adjoint test for ALL possible jet powers.
-- Stages: retain a functional detecting eta; encode pair multiplication over
-- QQ; separate its three support points; verify jet bounds10,8,6; test the
-- transpose of EPD on orders at most8,6,4. Largest rational solve is66x45.
cubeInput=separate("\n",get "research/tools/bmd_cube_first_obstruction.m2");
cubeStop=first select(toList(0..#cubeInput-1),j->substring(0,14,cubeInput#j)=="cubeRelations=");
value concatenate apply(take(cubeInput,cubeStop),l->l|"\n");
cubeLocal=QQ[uu,vv,ww];cubeArtin=cubeLocal/((ideal(uu,vv,ww))^2);
cubeSpec=map(cubeArtin,S,{-15_cubeArtin,10+uu,60+vv,-72+ww});
cubeMons={1_cubeArtin,uu,vv,ww};cubeMonsLift={1_cubeLocal,uu,vv,ww};
cubeExpand=M->matrix table(4*numrows M,numcols M,(i,j)->
    lift(coefficient(cubeMonsLift#(i//numrows M),lift(M_(i%numrows M,j),cubeLocal)),QQ));
cubeLinear=M->fold((a,b)->a|b,apply(cubeMons,mon->cubeExpand(mon*M)));
cubeImage=cubeLinear(cubeSpec cubePhi);cubeClass=cubeExpand(cubeSpec cubeEta);
cubeDual=gens kernel transpose cubeImage;
cubeDetect=transpose(cubeClass)*cubeDual;
cubePick=first select(toList(0..numcols cubeDual-1),j->cubeDetect_(0,j)!=0);
cubeEll=transpose(submatrix(cubeDual,,{cubePick}))/cubeDetect_(0,cubePick);
assert(cubeEll*cubeImage==0 and cubeEll*cubeClass==matrix{{1_QQ}});
<< "TRANSVERSE_DEFECT_DIMENSION=" << 12-rank cubeImage << " ETA_DETECTOR=" << toString entries cubeEll << endl;
cubeProj=submatrix(cubeRowChange,cubeOtherRows,);
cubePsi=cubeEll*cubeLinear(cubeSpec cubeProj);
assert(cubePsi*cubeLinear(cubeSpec cubeA)==0);
<< "PAIR_FUNCTIONAL=" << toString entries cubePsi << endl;
cubePsiAll=transpose(cubeDual)*cubeLinear(cubeSpec cubeProj);
assert(cubePsiAll*cubeLinear(cubeSpec cubeA)==0);
<< "COMPLETE_DEFECT_DUAL=" << toString entries transpose cubeDual << endl;
<< "COMPLETE_PAIR_FUNCTIONALS=" << toString entries cubePsiAll << endl;
cubeJetRing=QQ[js,jv];
cubeA3Base=js^3-2*js*jv-15*js-10;
cubeA4Base=js^4-3*js^2*jv+jv^2-15*(js^2-jv)-10*js+60;
cubeA5Base=js*cubeA4Base-jv*cubeA3Base+72;
cubeAtPoint=map(QQ,cubeJetRing,{1_QQ,-6_QQ});
assert(all({cubeA4Base,cubeA5Base},f->cubeAtPoint(f)==0 and cubeAtPoint(diff(js,f))==0 and cubeAtPoint(diff(jv,f))==0));
cubeSM=matrix table(10,10,(i,j)->(
    u:=(cubePairs#i)#0;v:=(cubePairs#i)#1;r:=(cubePairs#j)#0;s:=(cubePairs#j)#1;
    (cubeZ_(u,r)*(if v==s then 1_S else 0_S)+(if u==r then 1_S else 0_S)*cubeZ_(v,s)
    -cubeZ_(v,r)*(if u==s then 1_S else 0_S)-(if v==r then 1_S else 0_S)*cubeZ_(u,s))
));
cubeVM=exteriorPower(2,cubeZ);
assert(entries(cubeSM*cubeVM)==entries(cubeVM*cubeSM));
cubeSM=cubeLinear(cubeSpec cubeSM);cubeVM=cubeLinear(cubeSpec cubeVM);
cubeRoot=cubeLinear(cubeSpec cubeZ);
cubeP0=matrix{{0_QQ}};
cubeRootP0=(cubeRoot+2*id_(QQ^20))^3*(cubeRoot-3*id_(QQ^20))^2;
assert(cubeRootP0^2==0);
cubePoints={{-4_QQ,4_QQ,10},{1_QQ,-6_QQ,8},{6_QQ,9_QQ,6}};
cubeEig=apply(cubePoints,p->gens kernel((cubeSM-p#0*id_(QQ^40))^(p#2+1)));
cubeFrame=fold((a,b)->a|b,cubeEig);assert(numcols cubeFrame==40 and rank cubeFrame==40);
cubeInverse=inverse cubeFrame;
cubeInputs=matrix table(40,4,(i,j)->if i==10*j then 1_QQ else 0_QQ);
cubeOffset=0;cubeAllPass=true;
for point from 0 to 2 do (
    p:=cubePoints#point;m:=p#2;n:=numcols(cubeEig#point);
    projection:=cubeFrame*diagonalMatrix apply(toList(0..39),i->if i>=cubeOffset and i<cubeOffset+n then 1_QQ else 0_QQ)*cubeInverse;
    cubeOffset=cubeOffset+n;
    assert(projection^2==projection and projection*cubeSM==cubeSM*projection and projection*cubeVM==cubeVM*projection);
    X:=cubeSM-p#0*id_(QQ^40);Y:=cubeVM-p#1*id_(QQ^40);
    start:=projection*cubeInputs;
    xp:=apply(toList(0..m+1),a->X^a);yp:=apply(toList(0..m+1),b->Y^b);
    assert(all(toList(0..m+1),a->xp#a*yp#(m+1-a)*start==0));
    rows:=flatten apply(toList(0..m),d->apply(toList(0..d),a->{a,d-a}));
    cols:=flatten apply(toList(0..m-2),d->apply(toList(0..d),a->{a,d-a}));
    moments:=matrix table(#rows,4*numcols cubeDual,(i,j)->(cubePsiAll*xp#((rows#i)#0)*yp#((rows#i)#1)*start)_(j//4,j%4));
    adjoint:=matrix table(#rows,#cols,(i,j)->(
        a:=(rows#i)#0;b:=(rows#i)#1;c:=(cols#j)#0;d:=(cols#j)#1;
        ((if c==a-2 and d==b then a*(a-1) else 0)
        +(if c==a-1 and d==b-1 then p#0*a*b else 0)
        +(if c==a and d==b-2 then p#1*b*(b-1) else 0)
        +(if c==a and d==b-1 then b*(a+b+3/2) else 0))
    ));
    symbolicL=apply(rows,ab->(
        f:=js^(ab#0)*jv^(ab#1);
        (diff(js,diff(js,f))+(js+p#0)*diff(js,diff(jv,f))
          +(jv+p#1)*diff(jv,diff(jv,f))+(5/2)*diff(jv,f))
    ));
    assert(adjoint==matrix table(#rows,#cols,(i,j)->lift(coefficient(js^((cols#j)#0)*jv^((cols#j)#1),symbolicL#i),QQ)));
    rr:=rank adjoint;ra:=rank(adjoint|moments);
    << "POINT=" << point << " LOCATION=" << take(p,2) << " PAIR_LOCAL_DIMENSION=" << n
       << " PSI_JET_BOUND=" << m << " LAMBDA_BOUND=" << m-2
       << " ADJOINT_RANK=" << rr << " AUGMENTED_RANK=" << ra << endl;
    << "LOCAL_PSI_MOMENTS=" << toString entries moments << endl;
    if rr==ra then (
        solution:=moments//adjoint;assert(adjoint*solution==moments);
        << "FINITE_JET_SOLUTION=" << toString entries solution << endl;
        bounds:=apply(toList(0..3),j->(
            nz:=select(toList(0..#cols-1),i->any(toList(0..numcols cubeDual-1),k->solution_(i,4*k+j)!=0));
            if #nz==0 then -1 else max apply(nz,i->sum(cols#i))
        ));
        << "ALL_FUNCTIONALS_JET_ORDERS_by_parameter_component=" << bounds << endl;
        assert(if point==1 then bounds=={3,1,1,1} else bounds=={-1,-1,-1,-1});
    ) else (
        cubeAllPass=false;
        left:=gens kernel transpose adjoint;values:=transpose(left)*moments;
        row:=first select(toList(0..numrows values-1),i->any(toList(0..numcols values-1),j->values_(i,j)!=0));
        witness:=transpose(submatrix(left,,{row}));
        assert(witness*adjoint==0 and witness*moments!=0);
        << "ADJOINT_SEPARATING_FUNCTIONAL=" << toString entries witness << endl;
        << "NONZERO_MOMENT_PAIRING=" << toString entries(witness*moments) << endl;
    );
);
<< "ALL_SUPPORT_POINTS_ADMIT_FINITE_JETS=" << cubeAllPass << endl;
assert cubeAllPass;
<< "PASS all defect functionals kill J_T squared: constant order4 and linear-parameter order2 vanish" << endl;
<< "PASS J_T itself does not vanish: normalized eta detector equals1" << endl;
<< "FINITE_JET_DUAL_COMPLETED cpu=" << cpuTime()-cubeClock << endl << flush;
exit 0;
