/* Independent brute-force check: delta_S(2,k,l) over GF(8), mod x^3+x+1, S={0,1,2,3}.
   usage: chk k Dmin Dmax ; prints for each D the dims of V_l (order>=l at origin), l=0..k */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int MOD=0xB, Q=8;
static int mul(int x,int y){int r=0;while(y){if(y&1)r^=x;y>>=1;x<<=1;if(x&Q)x^=MOD;}return r;}
static int pw(int x,int e){int r=1;while(e--)r=mul(r,x);return r;}
static int inv(int x){for(int y=1;y<Q;y++)if(mul(x,y)==1)return y;abort();}
static int rankm(int *M,int R,int C){int r=0;for(int c=0;c<C&&r<R;c++){int p=-1;for(int i=r;i<R;i++)if(M[i*C+c]){p=i;break;}if(p<0)continue;
 if(p!=r)for(int j=0;j<C;j++){int t=M[p*C+j];M[p*C+j]=M[r*C+j];M[r*C+j]=t;}
 int iv=inv(M[r*C+c]);for(int j=0;j<C;j++)M[r*C+j]=mul(M[r*C+j],iv);
 for(int i=0;i<R;i++)if(i!=r&&M[i*C+c]){int f=M[i*C+c];for(int j=0;j<C;j++)M[i*C+j]^=mul(f,M[r*C+j]);}
 r++;}return r;}
static int E[5000][2],B[500][2];
int main(int argc,char**argv){int k=atoi(argv[1]),D0=atoi(argv[2]),D1=atoi(argv[3]);
 int S[4]={0,1,2,3};
 for(int D=D0;D<=D1;D++){
  int ne=0;for(int d=0;d<=D;d++)for(int e1=0;e1<=d;e1++){E[ne][0]=e1;E[ne][1]=d-e1;ne++;}
  int nb=0;for(int d=0;d<k;d++)for(int b1=0;b1<=d;b1++){B[nb][0]=b1;B[nb][1]=d-b1;nb++;}
  int R=15*nb; int *M0=malloc(sizeof(int)*R*ne); int row=0;
  for(int i=0;i<4;i++)for(int j=0;j<4;j++){if(!i&&!j)continue;int p1=S[i],p2=S[j];
   for(int b=0;b<nb;b++){for(int c=0;c<ne;c++){int e1=E[c][0],e2=E[c][1],b1=B[b][0],b2=B[b][1];int v=0;
     if(b1<=e1&&b2<=e2&&(b1&~e1)==0&&(b2&~e2)==0)v=mul(pw(p1,e1-b1),pw(p2,e2-b2));M0[row*ne+c]=v;}row++;}}
  printf("D=%d dims:",D);
  for(int l=0;l<=k;l++){
   int cols=0;int *N=malloc(sizeof(int)*R*ne);
   for(int c=0;c<ne;c++)if(E[c][0]+E[c][1]>=l){for(int r=0;r<R;r++)N[r*ne+cols]=M0[r*ne+c];cols++;}
   for(int r=0;r<R;r++)memmove(N+r*cols,N+r*ne,sizeof(int)*cols);
   int rk=rankm(N,R,cols);printf(" %d",cols-rk);free(N);}
  printf("\n");fflush(stdout);free(M0);}
 return 0;
}
