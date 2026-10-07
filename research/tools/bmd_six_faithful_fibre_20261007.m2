-- Faithful H6/c2 H6 over QQ[c3,c4,c5,c6], retaining the hidden Tor class.
-- General mechanism: a module generated through g over a positively weighted
-- polynomial ring with variable weights at most w has no later components once
-- w consecutive components above g vanish. Here g=19,w=6. Thus six zeros certify
-- the full cyclic quotient, not rank stability or a guessed orbit endpoint.
-- Stages: import full preimage; universal low-weight lifts before specialization;
-- direct specialized universal harmonic formula (never a specialized derivation);
-- exact homogeneous quotient spaces and representatives; stop at six zeros;
-- four commuting coefficient actions on the complete parameter fibre.
-- Guard d<=50 and coefficient matrices<=3 million entries: failure is no theorem.
fibClock=cpuTime();
load "research/tools/bmd_six_kernel_model_20261007.m2";
fibData=bmdBuildKernelSource(6,14);
fibS=fibData#"ring";fibFW=fibData#"weights";fibF=fibData#"module";
fibRead=(lines,tag)->(
    hits:=select(lines,l->substring(0,#tag,l)==tag);assert(#hits==1);
    substring(#tag,first hits)
);
fibLines=separate("\n",get "research/results/bmd-six-kernel-map-20261007/certificate.txt");
fibVW=value fibRead(fibLines,"PREIMAGE_GENERATOR_WEIGHTS=");
fibRW=value fibRead(fibLines,"PREIMAGE_RELATION_WEIGHTS=");
fibP=fibS^(-fibVW);
fibJ=map(fibF,fibP,entries matrix value fibRead(fibLines,"PREIMAGE_MAP="));
fibRel=map(fibP,fibS^(-fibRW),entries matrix value fibRead(fibLines,"PREIMAGE_RELATIONS="));
assert(fibJ*fibRel==0 and isHomogeneous fibJ and isHomogeneous fibRel);
fibQQ=(mat,bas)->(
    if numcols mat==0 then map(QQ^(numcols bas),QQ^0,0) else (
        co:=last coefficients(mat,Monomials=>bas);
        assert(entries(bas*co)==entries mat);sub(co,QQ)
    )
);
-- All orbit columns that could interact with hidden weight16 are lifted over S.
fibLowLift=map(fibP,fibS^0,0);
for j from 9 to 14 do (
    d:=j+2;pb:=basis(d,fibP);fb:=basis(d,fibF);
    aa:=fibQQ(fibJ*pb,fb);bb:=fibQQ((fibData#"columns")#j,fb);
    sol:=bb//aa;assert(aa*sol==bb);
    col:=map(fibP,fibS^{-d},entries(pb*sub(sol,fibS)));
    assert(entries(fibJ*col)==entries((fibData#"columns")#j));
    fibLowLift=fibLowLift|col;
);
fibR=QQ[z_3..z_6,Degrees=>{3,4,5,6}];fibC=prepend(0_fibR,gens fibR);
fibSpec=map(fibR,fibS,fibC);
fibF0=fibR^(-fibFW);fibP0=fibR^(-fibVW);
fibJ0=map(fibF0,fibP0,entries(fibSpec fibJ));
fibRel0=map(fibP0,fibR^(-fibRW),entries(fibSpec fibRel));
fibLow0=map(fibP0,fibR^(-toList(11..16)),entries(fibSpec fibLowLift));
fibProjection=fibSpec(fibData#"projection");
fibPairs=fibData#"pairs";
fibPowers=apply(toList(0..5),j->submatrix(id_(fibR^6),,{j}));
fibGamma={1_QQ};
fibColumns=map(fibF0,fibR^0,0);
fibMakeColumn=j->(
    while #fibPowers<=j+1 do (
        n:=#fibPowers;
        fibPowers=append(fibPowers,sum(toList(2..6),i->
            (-1)^(i+1)*fibC#(i-2)*fibPowers#(n-i)));
    );
    while #fibGamma<=j do (
        n:=#fibGamma;fibGamma=append(fibGamma,last(fibGamma)*(-3/2-n+1)/n);
    );
    pair:=matrix table(15,1,(r,col)->(
        ab:=fibPairs#r;
        sum(toList(0..j),i->fibGamma#i*fibGamma#(j-i)*
            ((fibPowers#i)_(ab#0,0)*(fibPowers#(j-i+1))_(ab#1,0)
             -(fibPowers#i)_(ab#1,0)*(fibPowers#(j-i+1))_(ab#0,0)))
    ));
    ans:=map(fibF0,fibR^{-j-2},entries(fibProjection*pair));
    assert(isHomogeneous ans);
    if j<=14 then assert(entries ans==entries(fibSpec((fibData#"columns")#j)));
    ans
);
fibSpaces=new MutableHashTable;
fibRepresentatives=map(fibP0,fibR^0,0);
fibZero=0;fibStop=0;fibDims={};
for d from 11 to 50 do (
    col:=fibMakeColumn(d-2);fibColumns=fibColumns|col;
    pb:=basis(d,fibP0);fb:=basis(d,fibF0);
    aa:=fibQQ(fibJ0*pb,fb);
    gg:=fibQQ(fibColumns*basis(d,source fibColumns),fb);
    assert(numrows aa*numcols aa<=3000000 and numrows gg*numcols gg<=3000000);
    aBasis:=gens gb aa;gBasis:=gens gb gg;
    assert(gg%gb aBasis==0);
    reps:=map(fibP0,fibR^0,0);
    normal:=map(QQ^0,QQ^0,0);
    if d<=16 then (
        rr:=fibQQ(fibRel0*basis(d,source fibRel0),pb);
        gl:=fibQQ(fibLow0*basis(d,source fibLow0),pb);
        assert(aa*gl==gg);
        normal=gens gb(id_(QQ^(numcols pb))%gb(rr|gl));
        reps=map(fibP0,fibR^(apply(toList(1..numcols normal),i->-d)),
            entries(pb*sub(normal,fibR)));
        fibSpaces#d={pb,rr|gl,normal,true};
    ) else (
        reduced:=aa%gb gBasis;normal=gens gb reduced;
        lift:=normal//reduced;assert(reduced*lift==normal);
        reps=map(fibP0,fibR^(apply(toList(1..numcols normal),i->-d)),
            entries(pb*sub(lift,fibR)));
        assert((fibQQ(fibJ0*reps,fb)-normal)%gb gBasis==0);
        fibSpaces#d={fb,gBasis,normal,false};
    );
    h:=numcols reps;fibDims=append(fibDims,{d,h});
    fibRepresentatives=fibRepresentatives|reps;
    << "FAITHFUL_FIBRE weight=" << d << " ambient=" << numcols fb
       << " cover=" << numcols pb << " gammaRank=" << numcols gBasis
       << " quotient=" << h << " total=" << numcols fibRepresentatives
       << " cpu=" << cpuTime()-fibClock << endl << flush;
    if d>=20 and h==0 then fibZero=fibZero+1 else fibZero=0;
    if fibZero==6 then (fibStop=d;break);
);
assert(fibStop>0);
fibWeights=flatten degrees source fibRepresentatives;
assert(numcols fibRepresentatives>=49);
<< "FIBRE_STOP=" << fibStop << " FIBRE_DIMENSIONS=" << toString fibDims << endl;
<< "FIBRE_BASIS_WEIGHTS=" << toString fibWeights << endl;
<< "FIBRE_REPRESENTATIVES=" << toString entries fibRepresentatives << endl << flush;
-- Complete actions, using the domain presentation precisely where Tor can occur.
fibActions={};
for j from 3 to 6 do (
    action:=matrix table(#fibWeights,#fibWeights,(i,l)->0_QQ);
    for d in sort unique apply(fibWeights,w->w+j) do (
        cols:=select(toList(0..#fibWeights-1),l->fibWeights#l+j==d);
        if d<=fibStop then (
            data:=fibSpaces#d;
            values:=fibR_(j-3)*submatrix(fibRepresentatives,,cols);
            if not data#3 then values=fibJ0*values;
            qq:=fibQQ(values,data#0)%gb(data#1);
            coords:=qq//(data#2);assert((data#2)*coords==qq);
            rows:=select(toList(0..#fibWeights-1),i->fibWeights#i==d);
            assert(#rows==numrows coords);
            action=matrix table(#fibWeights,#fibWeights,(i,l)->
                if member(i,rows) and member(l,cols) then
                    coords_(position(rows,x->x==i),position(cols,x->x==l)) else action_(i,l));
        );
    );
    fibActions=append(fibActions,action);
    << "FIBRE_COEFFICIENT_ACTION=" << j << " MATRIX=" << toString entries action << endl << flush;
);
for i from 0 to 3 do for j from i+1 to 3 do assert(fibActions#i*fibActions#j==fibActions#j*fibActions#i);
<< "PASS complete faithful parameter fibre and four commuting original coefficient actions; cpu="
   << cpuTime()-fibClock << endl << flush;
exit 0;
