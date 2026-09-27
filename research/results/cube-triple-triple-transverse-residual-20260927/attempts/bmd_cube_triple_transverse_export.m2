-- Export the verified nine-row connection to Singular for exact local algebra.
-- Reuse only the tangent/encoding construction, not the slow global closure.
src=separate("\n",get "research/tools/bmd_cube_triple_transverse.m2");
cut=first select(toList(0..#src-1),i->substring(0,5,src#i)=="rels=");
value concatenate apply(take(src,cut),line->line|"\n");
dest="research/results/cube-triple-triple-transverse-residual-20260927/connection.sing";
out=openOut dest;
out << "// Exact QQ connection exported after both factor tangent checks.\n";
out << "ring R=0,(A,B,C,D),(ds,C);\n";
out << "matrix conn[9][9]=" << demark(",",apply(flatten entries mat,toString)) << ";\n";
out << "ideal drift=" << demark(",",apply(dr,toString)) << ";\n";
out << "matrix marker[9][1]=" << demark(",",apply(flatten entries v,toString)) << ";\n";
close out;
<< "EXPORTED=" << dest << " FACTOR_CHECKS=passed ROWS=9 COEFFICIENTS=4" << endl;
exit 0;
