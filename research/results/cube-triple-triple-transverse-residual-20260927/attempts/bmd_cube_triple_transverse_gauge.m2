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
dest="research/results/cube-triple-triple-transverse-residual-20260927/gauged-connection.sing";
out=openOut dest;
out << "// Exact QQ connection exported after both factor tangent checks.\n";
out << "ring R=0,(A,B,C,D),(ds,C);\n";
out << "matrix conn[9][9]=" << demark(",",apply(flatten entries mat,toString)) << ";\n";
out << "ideal drift=" << demark(",",apply(dr,toString)) << ";\n";
out << "matrix marker[9][1]=" << demark(",",apply(flatten entries v,toString)) << ";\n";
close out;
<< "EXPORTED=" << dest << " FACTOR_CHECKS=passed ROWS=9 COEFFICIENTS=4" << endl;
exit 0;
