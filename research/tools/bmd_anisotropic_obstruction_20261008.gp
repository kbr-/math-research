\\ Actual binary second restrictions: test anisotropy and every compatible skew part.
{
my(a=ffgen(Mod(1,3)*(a^3+2*a+2),'a),one=a^0,field=vector(27,i,one*((i-1)%3)+a*(((i-1)\3)%3)+a^2*((i-1)\9)),forms=[[2,0;0,18],[24,11;11,25]],exps=[2809,3745],codes=Map());
for(i=1,27,mapput(codes,Str(field[i]),i-1));
for(ci=1,2,
 my(C=matrix(2,2,i,j,field[forms[ci][i,j]+1]),zeros=0,singular=0,disc=-matdet(C));
 for(i=1,27,for(j=1,27,if(i==1&&j==1,next());my(v=[field[i],field[j]]~);if((mattranspose(v)*C*v)==0,zeros++)));
 for(N=1,2,for(i=1,27,my(skew=[0,field[i];-field[i],0],B=N*C/2+skew);if(matdet(B)==0,singular++)));
 print("ANISOTROPIC_TEST exponent=",exps[ci]," negative_det_code=",mapget(codes,Str(disc))," square_character=",disc^13," nonzero_isotropic_vectors=",zeros," singular_compatible_matrices=",singular);
);
my(control=[one,0;0,-one],found=0);
for(i=1,27,if(matdet(control+[0,field[i];-field[i],0])==0,found++));
if(found!=2,error("isotropic control must permit singular skew completion"));
print("ANISOTROPIC_TEST_COMPLETED vectors=1456 compatible_matrices=108 isotropic_control_singular=",found);
}
quit;
