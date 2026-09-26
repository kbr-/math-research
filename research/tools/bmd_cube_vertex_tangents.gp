\\ Test the proposed repair: reduced tangent cones at quadrangle vertices.
\\ The first nonvacuous equal-coordinate vertex is d=3: residual side order 2.
\\ Three generic directions determine a homogeneous quadratic tangent cone.
\\ Compute the 20 by 20 jet determinant exactly over Q[e], strip the proved
\\ collision factors a=26,b=21, and interpolate its epsilon^2 coefficient.
\\ This is one bounded falsification test, not an additional squarefree sweep.
DS=[];
read("research/tools/bmd_cube_limit_sides.gp");
{
  my(d=3,a=4*d^2-4*d+2,b=4*d^2-6*d+3,values=List(),dirs=[2,3,4]);
  for(j=1,#dirs,
    my(c=dirs[j],v=[1+'e*c,1+'e,1],D=deltaU(d,v),collision,R,ord);
    collision=prod(i=1,3,v[i]^a)*prod(i=1,2,prod(k=i+1,3,(v[i]-v[k])^b));
    R=D/collision;
    if(type(R)!="t_POL",error("collision quotient is not a polynomial"));
    ord=valuation(R,'e);
    if(ord<2,error("unexpected smaller residual vertex order"));
    listput(values,polcoeff(R,2,'e));
    print("d=3 direction (",c,",1,0): residual order=",ord,
          "; epsilon^2 coefficient=",values[#values]);
  );
  my(H=polinterpolate(dirs,Vec(values),'x));
  if(H==0,error("all three directions have zero quadratic coefficient"));
  print("Quadratic tangent at (1:1:1), affine direction (x,1,0): ",H);
  print("Factorization: ",factor(H));
  print("Squarefree quadratic: ",poldegree(H)==2 && poldegree(gcd(H,deriv(H)))==0);
}
quit;
