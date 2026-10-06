\\ Alternative merge's actual two domain rows at p7,D5mod7; seven local coefficients suffice.
default(parisizemax,1000000000);
default(nbthreads,1);
assert(c,s)={if(!c,error(s));};
{
my(D=103,c=D+1,q=2*c+1,top=q-1,P=7,o=Mod(1,7),xp=(o+ep+O(ep^(P+2)))^25,Y=-xp-1,tail=vector(P,j,top-P+j),R=matrix(2,P),zt=o+ep+O(ep^(P+2)),beta=Mod(8/3,7),zp=vector(c+1));
zp[1]=o;for(k=2,c+1,zp[k]=zp[k-1]*zt);
for(j=1,P,
 my(e=tail[j],fp0=(X-1)^e+if(e==top,(X-1)^q/Mod(q,7),0*o),fpoly=o*2^e*fp0);
 assert(polcoef(fpoly,2*c,X)==0,"actual missing even monomial");
 my(Ae=sum(k=0,c-1,polcoef(fpoly,2*k,X)*zp[k+1]),Be=sum(k=0,c,polcoef(fpoly,2*k+1,X)*zp[k+1]),dBe=sum(k=1,c,if(k%7 && polcoef(fpoly,2*k+1,X)!=0,polcoef(fpoly,2*k+1,X)*k*ep*zp[k],0*o)),lambda=1/xp+2*xp*beta/ep);
 my(ref1=ep^(top-e)*2*Ae,ref2=ep^(top-e)*(4*xp^2/ep*(dBe-beta*Be)-2*lambda*Ae));
 R[1,j]=ep^(top-e)*subst(fpoly,X,-xp);R[2,j]=ep^(top-e)*subst(deriv(fpoly,X),X,-xp);
 assert(valuation(ref1-R[1,j],ep)>=P && valuation(ref2-R[2,j],ep)>=P,"exact original coordinate-domain constraints");
);
my(j1=P,pivot=R[1,j1]);assert(valuation(pivot,ep)==0,"first primitive row unit");for(j=1,P,R[1,j]/=pivot);
my(mult=R[2,j1]);for(j=1,P,R[2,j]-=mult*R[1,j]);
my(val=vecmin(vector(P,j,valuation(R[2,j],ep))));assert(val==1,"second primitive row order");for(j=1,P,R[2,j]/=ep);
my(LC=matrix(2,P,i,j,polcoef(R[i,j],0,ep)));assert(matrank(LC)==2 && LC[1,P]!=0 && LC[2,P-1]!=0,"top two core coordinates removed");
for(j=1,P-2,assert(LC[,j]==[0,0]~, "all lower core coordinates retained"));
print("D=",D," qmod7=",q%7," tail_offsets=",tail-vector(P,j,2*D)," row_orders=[0,1] constraints=",LC);
print("PASS direct original-domain identities; top-two unit minor gives full F_(2D+1) alternative limit.");
}
quit;
