\\ Leading coefficient of the neck window minors against the theorem's formula (reviewer's check,
\\ promoted). Builds the rescaled rows u_m = T^m + sum_(n>=M) G_(m,n) e^(n-m) T^n and
\\ w_m = tau(1/T) u_m (tau = -tanh(3/2 artanh y), truncated; T^J offset for the negative powers),
\\ takes the window W_k and reports val det, and the ratio of its leading coefficient to
\\ t_1^k H_(M-k) det Gamma_k with Gamma_k = [G_(m,D+1) - G_(m-1,D) - G_(m,M) G_(M-1,D)] (r2),
\\ and to the uncorrected [G_(m,D+1) - G_(m-1,D)] (r1). Theorem prediction: val = k(k+1), r2 = +-1.
lam=3/2; N=30; J=29;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta(j)=binomial(-lam,j);
Gp(b,m,n)={my(P=prod(i=1,#b,x-b[i]));polcoeff(lift(Mod(x^n,P)),m,x)};
G(b,m,n)=if(m<0,0,if(n<#b,m==n,beta(n)/beta(m)*Gp(b,m,n)));
tv=vector(J,j,polcoeff(truncate(-tanh(lam*atanh(y+O(y^(J+2))))),j,y));
test(b,k)={my(M=#b,rows=List(),S);for(m=0,M-1,my(u=T^m+sum(n=M,N,G(b,m,n)*e^(n-m)*T^n));my(w=sum(j=1,J,tv[j]*T^(J-j))*u);listput(rows,[vector(3*M,c,polcoeff(u,c-1-M,T)),vector(3*M,c,polcoeff(w,c-1-M+J,T))]));S=vector(2*M,i,i-(M-k)-1);my(A=matrix(2*M,2*M,r,c,my(m=(r-1)%M,typ=(r-1)\M);rows[m+1][typ+1][S[c]+M+1]));my(d=matdet(A),v=valuation(d,e));my(g1=matdet(matrix(k,k,i,j,my(m=M-k+i-1,D=M+j-1);G(b,m,D+1)-G(b,m-1,D))));my(g2=matdet(matrix(k,k,i,j,my(m=M-k+i-1,D=M+j-1);G(b,m,D+1)-G(b,m-1,D)-G(b,m,M)*G(b,M-1,D))));my(H=if(M-k==0,1,matdet(matrix(M-k,M-k,i,j,tv[i-1+j]))));my(lc=polcoeff(d,v,e));emit(Str("M=",M," k=",k," val=",v," predicted=",k*(k+1)," r1=",lc/(tv[1]^k*H*g1)," r2=",if(g2,lc/(tv[1]^k*H*g2),"g2=0")));}
test([2,-3],1);test([2,-3],2);test([2,5,-7],1);test([2,5,-7],2);test([2,5,-7],3);test([1,3,-2,5],2);test([1,3,-2,5],3);test([1,3,-2,5],4);
