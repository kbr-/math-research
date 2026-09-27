-- Same seventh/sixth-power detector test, encoded once as finite QQ linear
-- algebra. Max ambient840; use bulk coefficient extraction and shared spans.
-- Quadratic dimensions36/32 are an independent established encoder control.
-- If all16 classes survive, retain separating duals for a basis of actual
-- polynomial source classes, and the sixth-power kernel as a minimality control.
linearClock=cpuTime();
R=QQ[A,B,C,D];
dlSource=separate("\n",get "research/results/cube-triple-triple-source-relations-20260927/source-certificate.txt");
dlCore=separate("\n",get "research/results/cube-triple-triple-transverse-residual-20260927/deflation-certificate.txt");
dlRead=(ls,tag)->matrix value substring(#tag,first select(ls,l->substring(0,#tag,l)==tag));
dlRel=dlRead(dlCore,"CORE_RAW=");dlSel=dlRead(dlSource,"SELECTED_LIFTS=");
dlMons=flatten apply(toList(0..6),d->flatten entries basis(d,R));
assert(#dlMons==210);
dlArt=R/((ideal gens R)^7);
dlTMons=apply(dlMons,m->sub(m,dlArt));
dlEncode=mm->fold((a,b)->a||b,apply(entries mm,row->
    sub(last coefficients(matrix{apply(row,f->lift(f,R))},
        Variables=>gens R,Monomials=>dlMons),QQ)));
dlRpoly=fold((a,b)->a|b,apply(dlTMons,m->m*sub(dlRel,dlArt)));
dlSpoly=fold((a,b)->a|b,apply(dlTMons,m->m*sub(dlSel,dlArt)));
dlRQ=dlEncode dlRpoly;dlSQ=dlEncode dlSpoly;
assert(numrows dlRQ==840 and numcols dlRQ==2520 and numcols dlSQ==840);
dlDecoder=id_(dlArt^4)**matrix{dlTMons};
assert(entries(dlDecoder*sub(dlEncode sub(dlSel,dlArt),dlArt))==entries sub(dlSel,dlArt));
<< "ENCODED rows=840 relationColumns=2520 sourceColumns=840 CPU="
   << cpuTime()-linearClock << endl << flush;
dlRB=gens gb dlRQ;
dlRem=dlSQ%gb dlRB;dlIB=gens gb dlRem;
dlImage=rank dlIB;
assert(dlImage<=16);
<< "POWER=7 FULL=" << 840-numcols dlRB << " UPPER=" << 840-numcols dlRB-dlImage
   << " RESIDUAL_IMAGE=" << dlImage << " CPU=" << cpuTime()-linearClock << endl << flush;
for power in {3,6} do (
    count:=binomial(4+power-1,4);
    rows:=flatten apply(toList(0..3),i->apply(toList(0..count-1),j->210*i+j));
    rb:=gens gb submatrix(dlRB,rows,);
    ib:=submatrix(dlIB,rows,)%gb rb;
    imageDim:=rank ib;fullDim:=4*count-numcols rb;
    if power==3 then assert(fullDim==36 and imageDim==4);
    if power==6 then (
        dlRows6=rows;dlRB6=rb;dlImage6=imageDim;
    );
    << "POWER=" << power << " FULL=" << fullDim << " UPPER=" << fullDim-imageDim
       << " RESIDUAL_IMAGE=" << imageDim << endl << flush;
);
if dlImage==16 then (
    dlChosen={};dlSpan=map(QQ^840,QQ^0,0);
    for j from 0 to numcols dlRem-1 do if #dlChosen<16 then (
        rem:=submatrix(dlRem,,{j})%gb dlSpan;
        if rem!=0 then (dlChosen=append(dlChosen,j);dlSpan=gens gb(dlSpan|rem););
    );
    assert(#dlChosen==16);
    dlActual=submatrix(dlSQ,,dlChosen);
    dlDual=transpose gens ker transpose dlRB;
    dlEval=dlDual*dlActual;
    dlSep=transpose((id_(QQ^16))//transpose dlEval)*dlDual;
    assert(dlSep*dlRQ==0 and dlSep*dlActual==id_(QQ^16));
    dlMiss=gens ker(submatrix(dlActual,dlRows6,)%gb dlRB6);
    assert(numcols dlMiss==16-dlImage6);
    << "SOURCE_BASIS_COLUMNS=" << toString dlChosen << endl;
    << "SOURCE_BASIS_MONOMIALS_AND_GENERATORS="
       << toString apply(dlChosen,j->{dlMons#(j//4),j%4}) << endl;
    << "SEPARATING_DUALS=" << toString entries dlSep << endl;
    << "SIXTH_POWER_KERNEL=" << toString entries dlMiss << endl;
);
<< "COMPLETE cpu=" << cpuTime()-linearClock << endl << flush;
exit 0;
