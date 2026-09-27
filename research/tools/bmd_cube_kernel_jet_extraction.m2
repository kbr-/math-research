-- Universal local-symbol test, not a dimension series.
-- At an ordered triple/double pair x=0,y=1, seek an S-linear functional
-- on I/L(J) using pair jets <=3 and three coefficient variations <=1.
-- Independent polynomial jets give a stronger test than any fixed N.
-- Stages: build the complete 20x14 symbol matrix; solve over its exact
-- rational function field; detect a_(N-1); check a quintic specialization.
-- Complete output is preserved with tools/save-run-output.py.
A=QQ[P3,P4,P5,Q2,Q3,Q4,Q5];
F=frac A;
R=F[x,z];
invGap=sum(toList(0..5),j->(x-z)^j);
epd=f->(diff(x,diff(z,f))+(3/2)*invGap*(diff(x,f)-diff(z,f)));
pX=P3*x^3+P4*x^4+P5*x^5;
pY=Q2*z^2+Q3*z^3+Q4*z^4+Q5*z^5;
exps=flatten apply(toList(0..3),d->apply(toList(0..d),a->{a,d-a}));
mons=apply(exps,ab->x^(ab#0)*z^(ab#1));
baseExps=select(exps,ab->ab!={0,0} and ab!={1,0});
baseMons=apply(baseExps,ab->x^(ab#0)*z^(ab#1));
coeff=(f,m)->lift(coefficient(m,f),F);
jet=f->apply(baseMons,m->coeff(f,m));
shortJet=f->{coeff(f,1_R),coeff(f,x)};
symbolRow=(which,u)->(
    p:=if which==0 then pX else pY;
    join(jet(epd(p*u)),
        flatten apply(toList(0..2),r->shortJet(epd((if which==0 then x^r else (1+z)^r)*u))))
);
rows=flatten apply(toList(0..1),i->apply(mons,u->symbolRow(i,u)));
M=matrix rows;
assert(numrows M==20 and numcols M==14);
assert(all(flatten entries M,a->all({2,6},j->
    diff(A_j,numerator(a))==0 and diff(A_j,denominator(a))==0)));
K=gens kernel M;
assert(M*K==0);
<< "BASE_JET_EXPONENTS=" << baseExps << endl;
<< "COEFFICIENT_JETS=delta_0(eval,dx),delta_1(eval,dx),delta_2(eval,dx)" << endl;
<< "MATRIX_SIZE=" << (numrows M,numcols M) << " RANK=" << rank M << " NULLITY=" << numcols K << endl;
<< "UNIVERSAL_SYMBOL_MATRIX=" << toString entries M << endl;
<< "KERNEL=" << toString entries K << endl;
-- a_(N-1)=(p(y)-p(x))/(y-x); each delta_r changes p by X^r.
aValue=(pY-pX)*invGap;
aRow=matrix{join(jet(aValue),
    flatten apply(toList(0..2),r->shortJet(((1+z)^r-x^r)*invGap)))};
detected=aRow*K;
<< "FIRST_CLASS_ROW=" << toString entries aRow << endl;
<< "FIRST_CLASS_VALUES=" << toString entries detected << endl;
assert(any(flatten entries detected,t->t!=0));
pick=first select(toList(0..numcols K-1),j->detected_(0,j)!=0);
witness=submatrix(K,,{pick})/detected_(0,pick);
assert(M*witness==0 and aRow*witness==matrix{{1_F}});
<< "NORMALIZED_DETECTOR=" << toString entries witness << endl;
-- A simpler linear combination eliminates all triple-root jet denominators.
-- Entries use Taylor coefficients; zz and xzz include factorial 2.
polyWitness=transpose matrix{{-21*(2*Q2-Q3),-14*Q2,6*(3*Q2-Q3),0_F,
    0_F,4*Q2,0_F,0_F,0_F,0_F,24*Q2^2,0_F,18*Q2^2,-12*Q2^2}};
assert(M*polyWitness==0);
assert((aRow*polyWitness)_(0,0)==20*Q2^2);
<< "POLYNOMIAL_DETECTOR=" << toString entries polyWitness << endl;
<< "POLYNOMIAL_DETECTION=" << toString entries(aRow*polyWitness) << endl;
-- Degree four source monomials are a direct negative control for truncation.
four=apply(toList(0..4),a->x^a*z^(4-a));
M4=matrix flatten apply(toList(0..1),i->apply(four,u->symbolRow(i,u)));
assert(M4==0);
<< "SOURCE_DEGREE_FOUR_ZERO=" << true << endl;
-- Independent exact calibration at p=X^3(X-1)^2, using derivatives
-- rather than coefficient extraction and the untruncated rational operator.
spec=map(QQ,A,{1,-2,1,1,3,3,1});
toQQ=a->spec numerator a/spec denominator a;
wq=matrix apply(entries witness,row->apply(row,toQQ));
Rq=QQ[t,w]; Frq=frac Rq;
at0=map(QQ,Rq,{0_QQ,0_QQ});
ratAt0=f->at0 numerator f/at0 denominator f;
dRat=(i,f)->(
    g:=promote(f,Frq);a:=numerator g;b:=denominator g;
    (diff(Rq_i,a)*b-a*diff(Rq_i,b))/b^2
);
epdQ=f->(dRat(0,dRat(1,f))+(3/2)/(1-t+w)*(dRat(0,f)-dRat(1,f)));
djet=(f,ab)->(
    g:=f;
    for j from 1 to ab#0 do g=dRat(0,g);
    for j from 1 to ab#1 do g=dRat(1,g);
    ratAt0(g)/(({1,1,2,6}#(ab#0))*({1,1,2,6}#(ab#1)))
);
rowQ=(i,ab)->(
    u:=t^(ab#0)*w^(ab#1);
    p:=if i==0 then t^3*(t-1)^2 else (1+w)^3*w^2;
    join(apply(baseExps,cd->djet(epdQ(p*u),cd)),
      flatten apply(toList(0..2),r->apply({{0,0},{1,0}},cd->
        djet(epdQ((if i==0 then t^r else (1+w)^r)*u),cd))))
);
Mq=matrix flatten apply(toList(0..1),i->apply(exps,ab->rowQ(i,ab)));
Ms=matrix apply(entries M,row->apply(row,toQQ));
assert(Mq==Ms and Mq*wq==0);
<< "QUINTIC_INDEPENDENT_DERIVATIVE_AUDIT=" << true << " RANK=" << rank Mq << endl;
<< "QUINTIC_DETECTOR=" << toString entries wq << endl;
-- Coordinate-restoration control: centered p=(Z-2)^3(Z-5)^2(Z+16).
-- This tests gap 3 and nonconstant spectator, not a new threshold case.
gap=3_QQ;q2=567_QQ;q3=594_QQ;
epdGap=f->(dRat(0,dRat(1,f))+(3/2)/(gap-t+w)*(dRat(0,f)-dRat(1,f)));
theta=(f,g1,g2)->(
    ((-42*gap*q2+21*gap^2*q3)*djet(f,{0,1})
     -14*gap^2*q2*djet(f,{0,2})
     +gap^2*(18*q2-6*gap*q3)*djet(f,{1,1})
     +4*gap^3*q2*djet(f,{1,2})
     +24*gap*q2^2*djet(g1,{0,0})
     +18*q2^2*djet(g2,{0,0})
     -12*gap*q2^2*djet(g2,{1,0}))
);
px6=t^3*(t-3)^2*(t+18);py6=(3+w)^3*w^2*(21+w);
assert(djet(py6,{0,2})==q2 and djet(py6,{0,3})==q3);
restored=flatten apply(toList(0..1),i->apply(exps,ab->(
    u:=t^(ab#0)*w^(ab#1);
    zc:=if i==0 then t else gap+w;
    pp:=if i==0 then px6 else py6;
    theta(epdGap(pp*u),epdGap(zc*u),epdGap(zc^2*u))
)));
assert(all(restored,a->a==0));
detectGap=theta((py6-px6)/(gap+w-t),1_Frq,gap+w+t);
assert(detectGap==20*gap*q2^2);
<< "RESTORED_GAP=" << gap << " SPECTATOR_AT_DOUBLE=21"
   << " ANNIHILATION_CONTROL=" << true << " FIRST_CLASS_VALUE=" << detectGap << endl;
