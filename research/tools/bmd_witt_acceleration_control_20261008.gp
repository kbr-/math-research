\\ Check acceleration off the prime field and against direct iteration, then prove a whole-state period.
default(parisizemax,1000000000);
default(nbthreads,1);
T='T;
read("research/tools/bmd_witt_jets_20261008.gp");
{
my(start=getwalltime(),a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,masks=[7,83,31,127,511],infos=vector(4,g,jw_info(g,one)),checks=0);
for(ci=1,#masks,
 my(S=masks[ci],P=prod(i=0,8,if(bittest(S,i),one+a^i*T,one)),g=(hammingweight(S)-1)\2,info=infos[g],acc=jw_accelerator(P,g,info,one),D=acc[1],L=acc[2],dp=vector(14),lp=vector(14),initial=jw_initial(P,g,1),state=initial);
 dp[1]=D;lp[1]=L;for(j=2,14,dp[j]=dp[j-1]^2;lp[j]=lp[j-1]^2);
 jw_assert(D^2*D^4680==D^2&&L^2*L^4680==L^2,"whole cubic state has stable 14040-step period");
 for(j=1,4,
  my(x=vector(g,i,a^(i+j)+one*(i%3))~,v=vector(g,i,a^(2*i+j)+one)~,st=jw_three([jw_poly(x),0,jw_poly(v)],P,g),want=L*concat(jw_mono(x,info[1]),v),m=#info[1]);
  jw_assert(jw_vector(st[1],g)==D*x&&jw_vector(st[3],g)==want[m+1..m+g],"nonprime-field accelerator control");checks++;
 );
 for(s=0,17,
  jw_assert(jw_fast(initial,s,P,g,info,dp,lp)==state,"fast versus direct normalized iteration");checks++;
  state=jw_step(state,P,g);
 );
 print("WITT_ACCELERATION mask=",S," genus=",g," dimension=",matsize(L)[1]," period14040=true nonprime_and_direct=true");
);
print("WITT_ACCELERATION_COMPLETED checks=",checks," wall_ms=",getwalltime()-start);
}
quit;
