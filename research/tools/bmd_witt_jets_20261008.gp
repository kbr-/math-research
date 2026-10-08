\\ Truncated multiplicative cocycles through z^3 in characteristic3.
\\ E(X)=1+X+2X^2+2X^3; E(xz)E(yz^2)E(vz^3).
\\ All polynomial/rational arithmetic and matrix kernels are PARI operations.
jw_assert(c,s)={if(!c,error(s));};
jw_coeff(f,j)={if(f==0,return(0));polcoef(numerator(f),j+poldegree(denominator(f),T),T)/pollead(denominator(f),T);};
jw_proj(f,g)={sum(j=1,g,jw_coeff(f,-j)*T^-j);};
jw_pos(f)={if(f==0,return(0));my(d=poldegree(numerator(f),T)-poldegree(denominator(f),T));if(d<0,0,sum(j=0,d,jw_coeff(f,j)*T^j));};
jw_mul(a,b,P)={[a[1]*b[1]+P*a[2]*b[2],a[1]*b[2]+a[2]*b[1]];};
jw_step(state,P,g)={
 my(raw=P*state[1]^3,h=jw_proj(raw,g),plus=jw_pos(raw),minus=raw-h-plus);
 [h,jw_proj(P*state[2]^3,g),jw_proj(P*state[3]^3+P*(plus+h)*(h+minus)*(plus+minus),g)];
};
jw_initial(P,g,q)={
 my(r=truncate(1/sqrt(P+O(T^(3*q)))),A=[1/(2*T^q),r/(2*T^q)],h=[0,jw_proj(A[2],g)],plus=[0,jw_pos(A[2])],minus=A-h-plus,carry=jw_mul(jw_mul(plus+h,h+minus,P),plus+minus,P));
 [h[2],jw_proj(-r/(2*T^(2*q)),g),jw_proj(carry[2],g)];
};
jw_vector(f,g)={vector(g,j,jw_coeff(f,-j))~;};
jw_poly(v)={sum(j=1,#v,v[j]*T^-j);};
jw_mono(v,monos)={vector(#monos,i,v[monos[i][1]]*v[monos[i][2]]*v[monos[i][3]])~;};
jw_info(g,one)={
 my(m=List());for(i=1,g,for(j=i,g,for(k=j,g,listput(m,[i,j,k]))));m=Vec(m);
 my(points=vector(3^g-1,i,vector(g,j,one*((i\3^(j-1))%3))~),E=matrix(#points,#m,i,j,jw_mono(points[i],m)[j]),rr=matindexrank(E)[1]);
 jw_assert(#rr==#m,"homogeneous cubic interpolation is unisolvent");
 points=vector(#m,i,points[rr[i]]);E=matrix(#m,#m,i,j,jw_mono(points[i],m)[j]);[m,points,E^-1];
};
jw_three(state,P,g)={for(j=1,3,state=jw_step(state,P,g));state;};
jw_accelerator(P,g,info,one)={
 my(monos=info[1],points=info[2],inv=info[3],m=#monos,D=matrix(g,g),values=matrix(m,g));
 for(j=1,g,my(st=jw_three([T^-j*one,0,0],P,g));for(i=1,g,D[i,j]=jw_coeff(st[1],-i)));
 for(j=1,m,my(st=jw_three([jw_poly(points[j]),0,0],P,g));jw_assert(jw_vector(st[1],g)==D*points[j],"linear first coordinate");for(i=1,g,values[j,i]=jw_coeff(st[3],-i)));
 my(force=mattranspose(inv*values),MV=matrix(m,m,i,j,jw_mono(D*points[i],monos)[j]),sym=mattranspose(inv*MV),L=matrix(m+g,m+g,i,j,if(i<=m,if(j<=m,sym[i,j],0*one),if(j<=m,force[i-m,j],D[i-m,j-m]))));
 [D,L];
};
jw_power_vector(powers,k,v)={my(bit=1);while(k,if(k%2,v=powers[bit]*v);k=k\2;bit++);v;};
jw_fast(initial,s,P,g,info,dp,lp)={
 my(k=s\3,x=jw_power_vector(dp,k,jw_vector(initial[1],g)),y=jw_power_vector(dp,k,jw_vector(initial[2],g)),state=jw_power_vector(lp,k,concat(jw_mono(jw_vector(initial[1],g),info[1]),jw_vector(initial[3],g))),m=#info[1]);
 jw_assert(state[1..m]==jw_mono(x,info[1]),"cubic monomial state remains exact");
 state=[jw_poly(x),jw_poly(y),jw_poly(state[m+1..m+g])];for(j=1,s%3,state=jw_step(state,P,g));state;
};
