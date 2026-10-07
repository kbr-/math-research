\\ Exact moving-mark controls for the intrinsic degree obstruction.
\\ n3 elliptic curve; d1..3 includes Hasse orders crossing characteristic3.
\\ These check the normalized state map, not a new normality range.
default(parisizemax,2000000000);
default(nbthreads,1);
read("research/tools/bmd_branch_state_core_20261007.gp");
projective_degree(v)={
 my(den=Pol(OO,XPAR),g=Pol(0*OO,XPAR));
 for(i=1,#v,den=lcm(den,denominator(v[i])));
 my(pol=vector(#v,i,den*v[i]));
 for(i=1,#pol,assert(denominator(pol[i])==1,"uncleared denominator");if(pol[i]!=0,g=gcd(g,pol[i])));
 assert(g!=0,"zero projective vector");
 my(primitive=apply(t->t/g,pol),height=0);
 for(i=1,#primitive,if(primitive[i]!=0,height=max(height,poldegree(primitive[i],XPAR))));
 [height,primitive]
};
{
T='x;XPAR='u;NN=3;PP=3;BB=4;CC=12;HH=1;
my(modulus=ffinit(3,2,'a),a=ffgen(modulus,'a),aa=[2,a+2,2*a+1]);OO=a^0;
AA=vector(3,i,aa[i]/(OO+aa[i]*XPAR));
my(coords=List());for(S=0,7,for(i=1,3,if(!bittest(S,i-1),listput(coords,[S,i]))));COORD=Vec(coords);
ZZ=vector(CC,c,-OO/AA[COORD[c][2]]);
my(ell=vector(3,i,OO+AA[i]*T+O(T^12)),roots=apply(sqrt,ell));for(i=1,3,assert(valuation(roots[i]^2-ell[i],T)>=12,"normalized square roots"));
CH=vector(8,S,prod(i=1,3,if(bittest(S-1,i-1),roots[i],OO)));
print("FIELD = ",modulus,"; FIXED_CURVE_SLOPES = ",aa,"; moving slopes a_i/(1+a_i*u)");
for(d=1,3,
 my(M=4*d,L=M-1,K=matker(source_jet(d,L)),v=source_eval(d)*K);
 assert(matsize(K)[2]==1 && matrank(v)==1,"elliptic line state");
 my(h=projective_degree(v[,1]),scaled=projective_degree(v[,1]*(XPAR^3+XPAR+OO)/(XPAR^2+OO)),raw=M*(M-1),pullback=8*h[1]);
 assert(h[1]==scaled[1],"projective degree changed under basis scaling");
 assert(raw-12<=pullback && pullback<=raw+8,"gauge degree bounds");
 print("d=",d," jet_length=",L," raw_Pluecker_degree=",raw," normalized_base_degree=",h[1]," pullback_degree=",pullback);
 print("PRIMITIVE_PROJECTIVE_COORDINATES = ",h[2])
);
print("PROJECTIVE_DEGREE_CONTROLS_COMPLETED")
}
quit;
