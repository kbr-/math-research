\\ Exact check of thm:cube-boundary-abel-identity at N = 2, 3, 4 over Q (written by the fresh-context reviewer of
\\ cycle kbz, 9 October 2026, promoted to the record).  Rows 1, T, sqrt((1+a_iT)(1+a_jT)), a_0 = 0; checks the flow
\\ identity delta Delta = ((N-1)/2) e_1 Delta - m Delta' and the reduced identity m G' = -delta Phi - (N-1)(N-1/2) e_1 Phi.
tt=T;
dl(f)=sum(i=2,N,a[i]^2*deriv(f,a[i]))
a=[0,x1]; N=2; m=3; rows=List(); listput(rows,vector(m+1,c,c==1)); listput(rows,vector(m+1,c,c==2));
for(i=1,N,for(j=i+1,N,s=sqrt(1+a[i]*T+O(T^(m+1)))*sqrt(1+a[j]*T+O(T^(m+1))); listput(rows,vector(m+1,c,polcoef(s,c-1,T)))));
M=matrix(m,m+1,r,c,rows[r][c]); D=matdet(matrix(m,m,r,c,M[r,c])); Dp=matdet(matrix(m,m,r,c,if(c<m,M[r,c],M[r,m+1])));
e1=vecsum(a); V=prod(i=1,N,prod(j=i+1,N,a[j]-a[i]));
print("N=",N," D nonzero: ",D!=0," flow identity: ",dl(D)-((N-1)/2*e1*D-m*Dp)==0);
Phi=D/V^N; Gp=Dp/V^N; print("  types ",type(Phi)," ",type(Gp)," deg Phi ",poldegree(substvec(Phi,variables(Phi),vector(#variables(Phi),k,variables(Phi)[k]*yy)),yy)," reduced identity: ",m*Gp+dl(Phi)+(N-1)*(N-1/2)*e1*Phi==0);
a=[0,x1,x2]; N=3; m=5; rows=List(); listput(rows,vector(m+1,c,c==1)); listput(rows,vector(m+1,c,c==2));
for(i=1,N,for(j=i+1,N,s=sqrt(1+a[i]*T+O(T^(m+1)))*sqrt(1+a[j]*T+O(T^(m+1))); listput(rows,vector(m+1,c,polcoef(s,c-1,T)))));
M=matrix(m,m+1,r,c,rows[r][c]); D=matdet(matrix(m,m,r,c,M[r,c])); Dp=matdet(matrix(m,m,r,c,if(c<m,M[r,c],M[r,m+1])));
e1=vecsum(a); V=prod(i=1,N,prod(j=i+1,N,a[j]-a[i]));
print("N=",N," D nonzero: ",D!=0," flow identity: ",dl(D)-((N-1)/2*e1*D-m*Dp)==0);
Phi=D/V^N; Gp=Dp/V^N; print("  types ",type(Phi)," ",type(Gp)," deg Phi ",poldegree(substvec(Phi,variables(Phi),vector(#variables(Phi),k,variables(Phi)[k]*yy)),yy)," reduced identity: ",m*Gp+dl(Phi)+(N-1)*(N-1/2)*e1*Phi==0);
a=[0,x1,x2,x3]; N=4; m=8; rows=List(); listput(rows,vector(m+1,c,c==1)); listput(rows,vector(m+1,c,c==2));
for(i=1,N,for(j=i+1,N,s=sqrt(1+a[i]*T+O(T^(m+1)))*sqrt(1+a[j]*T+O(T^(m+1))); listput(rows,vector(m+1,c,polcoef(s,c-1,T)))));
M=matrix(m,m+1,r,c,rows[r][c]); D=matdet(matrix(m,m,r,c,M[r,c])); Dp=matdet(matrix(m,m,r,c,if(c<m,M[r,c],M[r,m+1])));
e1=vecsum(a); V=prod(i=1,N,prod(j=i+1,N,a[j]-a[i]));
print("N=",N," D nonzero: ",D!=0," flow identity: ",dl(D)-((N-1)/2*e1*D-m*Dp)==0);
Phi=D/V^N; Gp=Dp/V^N; print("  types ",type(Phi)," ",type(Gp)," deg Phi ",poldegree(substvec(Phi,variables(Phi),vector(#variables(Phi),k,variables(Phi)[k]*yy)),yy)," reduced identity: ",m*Gp+dl(Phi)+(N-1)*(N-1/2)*e1*Phi==0);
