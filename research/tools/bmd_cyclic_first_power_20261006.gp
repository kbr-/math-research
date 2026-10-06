\\ Test the odd-cyclic-branch degree-two certificate for p>=M.
\\ Stages: negative control; at most23 candidates through47x47;
\\ exact root/series checks; determinant/rank; stop on first failure.
default(parisizemax, 500000000);
setrand(20261006);
bmd_assert(x,s)=if(!x,error(s));
bmd_run()={
  my(bmd_one=Mod(1,7),bmd_C,bmd_total=0,bmd_tested=0,bmd_failed=0,bmd_m,bmd_bound,bmd_L,bmd_e,bmd_pol,bmd_z,bmd_primitive,bmd_cycroot,bmd_roots,bmd_shift,bmd_beta,bmd_series,bmd_J,bmd_row,bmd_g,bmd_det,bmd_rank,bmd_ker);
  bmd_C=matrix(6,6,i,j,if(i==1,bmd_one*(j==1),binomial(1/2,j-1)*(i-1)^(j-1)*bmd_one));
  bmd_assert(matrank(bmd_C)==5,"degree-one negative control");
  print("negative_control p=7 n=5 d=1 M=6 rank=",matrank(bmd_C));
  for(N=3,10,bmd_m=binomial(N,2)+2;bmd_bound=(N-1)*(N-2)+2;forprime(p=bmd_m,max(bmd_bound,nextprime(bmd_m)),bmd_total++));
  print("maximum_candidates=",bmd_total," largest_matrix=47x47; stop_first_failure=true");
  for(N=3,10,
    if(bmd_failed,break);
    bmd_m=binomial(N,2)+2;bmd_bound=(N-1)*(N-2)+2;bmd_L=if(N%2,N,N-1);
    forprime(p=bmd_m,max(bmd_bound,nextprime(bmd_m)),
      bmd_e=znorder(Mod(p,bmd_L));bmd_pol=ffinit(p,bmd_e);bmd_z=ffgen(bmd_pol,'z);
      bmd_primitive=ffprimroot(bmd_z);bmd_cycroot=bmd_primitive^((p^bmd_e-1)/bmd_L);bmd_one=bmd_cycroot^0;
      bmd_assert(bmd_cycroot^bmd_L==bmd_one,"root unity order");
      bmd_roots=if(N%2,vector(N,i,bmd_cycroot^(i-1)),concat([0*bmd_one],vector(bmd_L,i,bmd_cycroot^(i-1))));
      bmd_shift=bmd_roots[1];bmd_roots=vector(N,i,bmd_roots[i]-bmd_shift);
      bmd_assert(#Set(bmd_roots)==N,"branch collisions");
      bmd_beta=vector(bmd_m,j,bmd_one*binomial(1/2,j-1));
      bmd_series=vector(N,i,Polrev(vector(bmd_m,j,bmd_beta[j]*bmd_roots[i]^(j-1)),'T));
      for(i=1,N,bmd_assert((bmd_series[i]^2-1-bmd_roots[i]*T)%T^bmd_m==0,"square-root normalization"));
      bmd_J=matrix(bmd_m,bmd_m,i,j,0*bmd_one);bmd_J[1,1]=bmd_one;bmd_J[2,2]=bmd_one;bmd_row=2;
      for(i=1,N-1,for(j=i+1,N,bmd_row++;bmd_g=bmd_series[i]*bmd_series[j];for(c=0,bmd_m-1,bmd_J[bmd_row,c+1]=polcoef(bmd_g,c))));
      bmd_assert(bmd_row==bmd_m,"source count");
      bmd_det=matdet(bmd_J);bmd_rank=matrank(bmd_J);bmd_tested++;
      bmd_assert((bmd_det!=0)==(bmd_rank==bmd_m),"determinant/rank mismatch");
      print("CASE N=",N," p=",p," L=",bmd_L," e=",bmd_e," M=",bmd_m," rank=",bmd_rank," determinant=",bmd_det);
      print("field_polynomial=",bmd_pol," root_of_unity=",bmd_cycroot);
      if(bmd_rank<bmd_m,
        bmd_ker=matker(bmd_J);bmd_assert(bmd_J*bmd_ker==matrix(bmd_m,bmd_m-bmd_rank),"kernel residual");
        print("FAILED_CERTIFICATE slopes=",bmd_roots);
        print("right_kernel=",bmd_ker);
        bmd_failed=1;break
      )
    )
  );
  print("tested=",bmd_tested," failure=",bmd_failed);
  print("PASS: source checks completed; candidate verdict=",if(bmd_failed,"FALSIFIED","PASSED_BOUNDED_CONTROLS_ONLY"));
};
bmd_run();
quit;
