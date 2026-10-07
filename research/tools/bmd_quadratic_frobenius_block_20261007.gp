\\ q=9 nonlinear branch mechanism: does the complete raw H_81 block still have
\\ a left kernel? If yes, the proved raw-Mobius-block theorem transports that
\\ row defect to every finite unramified mark. If no, no such conclusion follows.
\\ Reuse columns 0..35 of the saved F9(t) matrix; extend only to 78, the end of
\\ the smallest full Frobenius block Q-3 with Q=81 >= original D=38.
\\ Independent square-root recursion checks the 1548 newly added entries.
default(parisizemax,2000000000);
default(parisize,128000000);
t='t;b=ffgen(ffinit(3,2,'b),'b);
{
my(lines=readstr("research/results/bmd-effective-recursion-20261007/quadratic-fixed.txt"),M=0);
for(i=1,#lines,my(parts=strsplit(lines[i],"="));if(#parts>=2&&parts[1]=="SYMBOLIC_MATRIX ",M=eval(parts[2])));
if(type(M)!="t_MAT"||matsize(M)!=[36,36],error("saved matrix missing"));
my(o=b^0,base=vector(9,i,((i-1)%3)*o+((i-1)\3)*b),a=vector(9,i,base[i]+t*base[i]^2),cap=79,C=matrix(36,cap,i,j,if(j<=36,M[i,j],0*o)),row=0,checks=0);
for(i=1,9,for(j=i+1,9,
 row++;my(s=a[i]+a[j],v=a[i]*a[j],delta=(a[i]-a[j])^2,Q=vector(cap,k,if(k<=36,M[row,k],0*o)),G=vector(cap+2,k,0*o));
 G[1]=o;G[2]=s/2;for(l=0,35,G[l+3]=delta*Q[l+1]);
 for(l=36,cap-1,Q[l+1]=s*Q[l]+delta*sum(h=0,l-2,Q[h+1]*Q[l-1-h]));
 for(l=38,cap+1,G[l+1]=-sum(h=1,l-1,G[h+1]*G[l-h+1])/2);
 for(l=36,cap-1,if(G[l+3]!=delta*Q[l+1],error("new original coefficient mismatch"));checks++;C[row,l+1]=Q[l+1]);
));
print("RAW_BLOCK Q=81 COLUMNS 0..78 ROWS36; reused columns0..35");
print("NEW_SOURCE_IDENTITIES = ",checks);
print("RAW_BLOCK_MATRIX = ",C);
print("LEFT_KERNEL_STARTED");
my(K=matker(C~));
if(C~*K!=matrix(cap,matsize(K)[2],i,j,0*o),error("left kernel reconstruction"));
print("RAW_BLOCK_ROW_RANK = ",36-matsize(K)[2]);
print("RAW_BLOCK_LEFT_KERNEL = ",K);
print("QUADRATIC_FROBENIUS_BLOCK_COMPLETED")
}
quit;
