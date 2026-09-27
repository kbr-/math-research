\\ Exact interpretation of the retained weighted Hilbert series.
\\ M2 degree in this weighted presentation is not the vector-space length.
T='T;
{
my(lines=readstr("research/results/cube-filtered-syzygy-route-review-20260927/centered-ext.txt"),hs=List());
for(i=1,#lines,my(parts=strsplit(lines[i],"="));
  if(#parts==2&&parts[1]=="EXT_HILBERT_SERIES",listput(hs,eval(parts[2]))));
if(#hs!=2,error("Hilbert inventory"));
my(P=1+T+3*T^2+2*T^3+3*T^4+2*T^5+2*T^6+T^7+T^8);
if(hs[1]!=T^(-21)/(1-T),error("normalization Hilbert identity"));
if(hs[2]!=T^(-32)*P,error("finite Ext Hilbert identity"));
my(H0=T^(-14)*subst(hs[2],T,1/T));
if(denominator(H0)!=1||subst(H0,T,1)!=16,error("weighted local duality length"));
print("EXT3_HILBERT = T^(-21)/(1-T)");
print("EXT4_HILBERT = T^(-32)*(",P,")");
print("VERTEX_TORSION_HILBERT_CENTERED = ",H0);
print("VERTEX_TORSION_LENGTH_CENTERED = ",subst(H0,T,1));
print("VERTEX_TORSION_LENGTH_ANCHORED = ",5*subst(H0,T,1));
print("EXT_INTERPRETATION_COMPLETED");
}
quit;
