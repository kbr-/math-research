-- Export the verified nine-row connection to Singular for exact local algebra.
-- Reuse only the tangent/encoding construction, not the slow global closure.
src=separate("\n",get "research/tools/bmd_cube_triple_transverse.m2");
cut=first select(toList(0..#src-1),i->substring(0,5,src#i)=="rels=");
value concatenate apply(take(src,cut),line->line|"\n");
-- Multiplication by (Y-X)=2+u-t is a unit at the formal origin.
-- Conjugation changes density to 2*alpha-3*(X+Y)/2 and marker to1.
oldCon=con;
gaugeConnP=f->daP f+vT*diff(t,f)+vU*diff(u,f)+(2*sub(alpha,P)-3*(t+u)/2)*f;
gaugeMat=fold((x,y)->x|y,apply(basisQ,f->encode sub(gaugeConnP lift(f,P),Q)));
gauge=fold((x,y)->x|y,apply(basisQ,f->encode((sub(2+u-t,Q))*f)));
gaugeAug=map(QQ,R,toList(4:0_QQ));assert(det(gaugeAug gauge)!=0);
assert(entries oldCon(gauge)==entries(gauge*gaugeMat));
mat=gaugeMat;v=encode(1_Q);

tripleDirectClock=cpuTime();
coeffs={1_QQ};
for j from 1 to 16 do coeffs=append(coeffs,last(coeffs)*(-3/2-j+1)/j);
columns=apply(toList(0..16),j->encode(sum(toList(0..j),i->coeffs#i*coeffs#(j-i)*sub((t-1)^i*(u+1)^(j-i),Q))));
raw=fold((x,y)->x|y,columns);
<< "DIRECT_COLUMNS=" << numcols raw << " CPU=" << cpuTime()-tripleDirectClock << endl << flush;
out=openOut "research/results/cube-triple-triple-transverse-residual-20260927/direct-columns.sing";
out << "matrix rawColumns[9][17]=" << demark(",",apply(flatten entries raw,toString)) << ";\n";
close out;
<< "DIRECT_EXPORT_COMPLETE" << endl;
exit 0;
