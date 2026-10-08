\\ Export the exact central cohomology frame used in equal-order comparisons.
default(parisize,64000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_root_jets.gp");
read("research/tools/bmd_low_multiplier_core_20261008.gp");
read("research/results/bmd-exception-low-multipliers-20261008/comparison-input.gp");
{
my(a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),I=rootbasis(9,3),products=vector(512),roots=vector(9,i,sqrt(one+a^(i-1)*T+O(T^108))));
products[1]=one+O(T^108);for(S=1,511,my(bit=valuation(S,2));products[S+1]=products[S-2^bit+1]*roots[bit+1]);
my(G=vector(140,i,T^I[i][2]*products[I[i][1]+1]/products[512]),R=matrix(140,108,i,j,polcoef(G[i],108-j,T)),K=lm_decode(LM_MODULES[4][7],field),h=34,kp=matindexrank(K)[1],B=lm_sub(K,kp,[1..h])^-1*matrix(h,140,i,j,(kp[i]==j)*one),S=matrix(142,140,i,j,if(i<=108,R[j,i],B[i-108,j])));
for(i=1,27,mapput(codes,Str(field[i]),i-1));
lm_assert(matrank(S)==140&&B*K==matid(34),"complete dual frame");
write("research/results/bmd-exception-low-multipliers-20261008/dual-frame.g","LOW_DUAL_FRAME := ",lm_encode(S,codes),";");
print("LOW_DUAL_FRAME_COMPLETED full_rank140=true fixed_kernel_normalized=true");
}
quit;
