\\ All exact character states needed for the eight scalar classes and three cubic-period returns.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_witt_jets_20261008.gp");
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,infos=vector(4,g,jw_info(g,one)),base=[670,937,1091,3180,3735,3749,3893,4240],exps=concat([0..5],vector(24,i,base[(i-1)%8+1]+4680*((i-1)\8))),field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),codes=Map(),out="research/results/bmd-exception-cubic-obstruction-20261008/characters.g",count=0,polys=vector(512));
for(i=1,27,mapput(codes,Str(field[i]),i-1));polys[1]=one;
for(S=1,511,my(bit=valuation(S,2));polys[S+1]=polys[S-2^bit+1]*(one+a^bit*T));
write(out,"WITT_EXPONENTS := ",exps,";");write(out,"WITT_CHARACTERS := [");
for(S=1,511,
 my(g=(hammingweight(S)-1)\2);if(g<1,next());
 my(P=polys[S+1],info=infos[g],acc=jw_accelerator(P,g,info,one),D=acc[1],L=acc[2],dp=vector(14),lp=vector(14),initial=jw_initial(P,g,1),states=vector(#exps));
 dp[1]=D;lp[1]=L;for(j=2,14,dp[j]=dp[j-1]^2;lp[j]=lp[j-1]^2);
 jw_assert(D^2*D^4680==D^2&&L^2*L^4680==L^2,"whole character cubic state period");
 my(x=vector(g,i,a^i+one*(i%3))~,v=vector(g,i,a^(2*i)+one)~,st=jw_three([jw_poly(x),0,jw_poly(v)],P,g),want=L*concat(jw_mono(x,info[1]),v),m=#info[1]);
 jw_assert(jw_vector(st[1],g)==D*x&&jw_vector(st[3],g)==want[m+1..m+g],"actual nonprime-field cubic accelerator");
 for(si=1,#exps,my(state=jw_fast(initial,exps[si],P,g,info,dp,lp));states[si]=vector(3,j,vector(g,l,mapget(codes,Str(jw_coeff(state[j],-l))))));
 if(count,write(out,","));
 write(out,"[",S,",",vector(poldegree(P)+1,j,mapget(codes,Str(polcoef(P,j-1,T)))),",",vector(g,i,vector(g,j,mapget(codes,Str(D[i,j])))),",",vector(m+g,i,vector(m+g,j,mapget(codes,Str(L[i,j])))),",",states,"]");
 count++;if(count%50==0,print("WITT_EXPORT_PROGRESS characters=",count," wall_ms=",getwalltime()-start));
);
write(out,"];");jw_assert(count==466,"all positive-genus characters");
print("WITT_CHARACTER_EXPORT_COMPLETED characters=",count," exponents=",#exps," period14040=true wall_ms=",getwalltime()-start);
}
quit;
