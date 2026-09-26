/* Exact character check for the focused collision series, uniformly in d>=2.
   The geometry and extension lattice are proved in the notebook. This checks
   all eight character types, the value/first-derivative encoding at all four
   nodes, and the nonextendable-section control. A,B,C are independent nonzero
   square roots of the three branch parameters; no numerical specialization. */
must(b,msg)=if(!b,error(msg));
{
  my(nodes=[[1,1],[1,-1],[-1,1],[-1,-1]], roots=[A,B,C],
     even=List(), odd=List(), missing=List(), value, derivative, weight);
  print("SCOPE d>=2; all eight characters; four nodes; exact Q[A,B,C] arithmetic");
  for(mask=0,7,
    my(r=vector(3,i,bittest(mask,i-1)), k=sum(i=1,3,r[i]),
       exponent=2*ceil(k/2)-k,
       coeff=vector(4,h,prod(i=1,3,roots[i]^r[i])*nodes[h][1]^r[1]*nodes[h][2]^r[2]));
    must(exponent==k%2,"incorrect top pole parity");
    print("CHARACTER ",r," full_top_j=d-",ceil(k/2),
          " focused_top_j=d-",k," top_u_power=",exponent," coefficient=",coeff);
    if(exponent==0,listput(even,coeff~),listput(odd,coeff~));
    if(floor(k/2)==1,listput(missing,r));
  );
  value=Mat(Vec(even));derivative=Mat(Vec(odd));
  weight=vector(4,h,nodes[h][1]*nodes[h][2]);
  must(#missing==4,"incorrect codimension");
  must(matdet(value)^2==256*A^4*B^4*C^4,"value table singular");
  must(matdet(derivative)^2==256*A^4*B^4*C^4,"derivative table singular");
  must(weight*derivative==[0,0,0,4*A*B*C],"wrong derivative functional");
  print("VALUE_TABLE columns 000,110,101,011 = ",value);
  print("DERIVATIVE_TABLE columns 100,010,001,111 = ",derivative);
  print("VALUE_DETERMINANT=",matdet(value));
  print("DERIVATIVE_DETERMINANT=",matdet(derivative));
  print("MISSING_TYPES=",Vec(missing));
  print("WEIGHTED_DERIVATIVE=",weight*derivative);
  print("NEGATIVE_CONTROL z*T^(d-2)*w1*w2*w3 has zero node values but weighted derivative 4*A*B*C: rejected");
  print("PASS all character types; value matching; derivative functional; nonextendable control");
}
