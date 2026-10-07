\\ Test character Kodaira-Spencer pairings for f_t=x^9+x^8+x^5+x-t at t=1.
\\ Pairing matrix: 2 sum_i v_i*b_i^(a+b-2)/R_S'(b_i), v_i=1/f_t'(b_i).
\\ Controls: affine root velocities are coordinate changes and have zero pairing.
default(parisizemax,1000000000);
default(nbthreads,1); setrand(20261007);
check(c,s)={if(!c,print("FAIL: ",s);quit(1));};
{
f=Mod(1,3)*(x^9+x^8+x^5+x-1);a=ffgen(ffinit(3,10,'a),'a);roots=polrootsmod(f,a);check(#roots==9,"distinct roots");
print("FIELD_POLYNOMIAL=",a.mod," ROOTS=",roots);
v=vector(9,i,1/subst(deriv(f),x,roots[i]));
ranks=matrix(9,5);witness=vector(9);totalrank=0;genus=0;controls=0;
for(mask=1,511,my(m=hammingweight(mask));if(m>=3,
 my(g=(m-1)\2,I=select(i->bittest(mask,i-1),[1..9]),R=prod(j=1,m,x-roots[I[j]]),rp=deriv(R));
 my(weights=vector(m,j,2/subst(rp,x,roots[I[j]])));
 my(H=matrix(g,g,i,j,sum(k=1,m,weights[k]*v[I[k]]*roots[I[k]]^(i+j-2))),r=matrank(H));
 ranks[m,r+1]++;totalrank+=r;genus+=g;if(r==g && witness[m]==0,witness[m]=mask;print("WITNESS size=",m," mask=",mask," matrix=",H," determinant=",matdet(H)));
 for(e=0,if(m%2,1,2),my(C=matrix(g,g,i,j,sum(k=1,m,weights[k]*roots[I[k]]^(i+j-2+e))));check(C==matrix(g,g),"coordinate-change control failed");controls++);
 if(m==9,print("FULL_QUOTIENT_KS=",H," determinant=",matdet(H)))
));
print("RANK_COUNTS_BY_SIZE_AND_RANK=",ranks);print("FULL_RANK_WITNESS_MASKS=",witness);
print("TOTAL_KS_RANK=",totalrank," GENUS=",genus," COORDINATE_CHANGE_CONTROLS=",controls);
print("PARAMETER_RANK_CONTROL_COMPLETED; no theta coverage asserted");
}
quit;
