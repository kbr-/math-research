\\ Test the derivative of the remaining relative pairing on its actual one-dimensional radical.
\\ The signed-family dual section f+w*f1 satisfies Phi4*f1=-lambda162*f.
default(parisizemax,1000000000);
default(nbthreads,1);
read("research/tools/bmd_root_jets.gp");
read("research/results/bmd-exception-return-multipliers-20261008/relative-input.gp");
read("research/results/bmd-exception-return-multipliers-20261008/failure-export/failed-tangent.gp");
rr_assert(c,s)={if(!c,error(s));};
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),decode=x->field[x+1],h=140,Q=81,I=rootbasis(9,3),roots=vector(9,i,sqrt(one+a^(i-1)*T+O(T^(2*Q)))),products=vector(512));
products[1]=one+O(T^(2*Q));
for(S=1,511,my(b=valuation(S,2));products[S+1]=products[S-2^b+1]*roots[b+1]);
my(FC=matrix(2*Q,h,i,j,polcoef(T^I[j][2]*products[I[j][1]+1],i-1,T)),GC=matrix(2*Q,h,i,j,polcoef(T^I[j][2]*products[I[j][1]+1]/products[512],i-1,T)));
my(C=matrix(h,h,i,j,decode(LIFT_C[i][j])),K=matrix(h,61,i,j,decode(LIFT_K[i][j])),Cnu=matrix(h,h,i,j,decode(MIXED_TANGENT[i][j])),C2=matrix(h,2*Q,i,j,GC[2*Q+1-j,i])*FC,A=mattranspose(K)*Cnu*K,u=matker(A),f0=K*u);
rr_assert(MIXED_K==18 && MIXED_SIGN==1 && matrank(A)==60 && matsize(u)==[61,1],"single correct radical");
rr_assert(C2==mattranspose(C2) && mattranspose(K)*C2*K==matrix(61,61),"exact second cup compatibility");
my(piv=matindexrank(C),rows=piv[1],cols=piv[2],rhs=-C2*f0,small=matrix(#rows,#cols,i,j,C[rows[i],cols[j]]),sol=matsolve(small,matrix(#rows,1,i,j,rhs[rows[i],j])),f1=matrix(h,1));
for(i=1,#cols,f1[cols[i],1]=sol[i,1]);
rr_assert(C*f1==rhs && C*f0==matrix(h,1),"full first-correction equation");
my(value=(mattranspose(f0)*Cnu*f1)[1,1],gauge=(mattranspose(f0)*Cnu*(f1+f0))[1,1],codes=Map(),out="research/results/bmd-exception-return-multipliers-20261008/relative-data.g");
rr_assert(value==gauge,"kernel-gauge invariance");
for(i=1,27,mapput(codes,Str(field[i]),i-1));
write(out,"REL_CNU := ",vector(h,i,vector(h,j,mapget(codes,Str(Cnu[i,j])))),";");
write(out,"REL_C2 := ",vector(h,i,vector(h,j,mapget(codes,Str(C2[i,j])))),";");
write(out,"REL_F0 := ",vector(h,i,[mapget(codes,Str(f0[i,1]))]),";");
write(out,"REL_F1 := ",vector(h,i,[mapget(codes,Str(f1[i,1]))]),";");
write(out,"REL_DERIVATIVE := ",mapget(codes,Str(value)),";");
print("RELATIVE_RETURN_DERIVATIVE mixed_rank=",matrank(A)," radical=1 derivative=",value," code=",mapget(codes,Str(value))," gauge_invariant=true wall_ms=",getwalltime()-start);
print("RELATIVE_RETURN_DERIVATIVE_COMPLETED");
}
quit;
