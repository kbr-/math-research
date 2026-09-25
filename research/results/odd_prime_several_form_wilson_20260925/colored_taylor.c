/* Several-form Wilson test on the colored algebra C_{N,M} = tensor_{c=1..N} (F_3 + F_3^M), e_{ic}e_{jc}=0,
   with forms l_i = sum_c e_{ic} (i=1..M).  This is the weak base's monomial algebra for M dense forms whose column
   parts are independent in every column (after a per-column change of basis); blocked columns give smaller N.
   Tested statement (Taylor generation for the squares): for target degree s, the kernel of
     Phi_s : (+)_i C_{s-2} -> C_s,  (g_i) -> sum_i g_i l_i^2
   equals the span of the Frobenius syzygies (l_i m) e_i, m in C_{s-3}, and the Koszul syzygies
   (l_j^2 m) e_i - (l_i^2 m) e_j, m in C_{s-4}.  Both sides split by color multidegree a (sum a = s); per multidegree
   we report dim ker Phi and the rank of the Taylor span; excess = dim ker - Taylor rank (0 means Taylor-generated).
   Usage: colored_taylor M N_min N_max s_max out.json */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int M,N;
typedef struct { uint32_t *code; long n; } Basis;   /* monomials of a multidegree, sorted codes (base M+1, 2 bits/col) */
static void enum_rec(int c,int *cnt,uint32_t code,Basis*B,long cap){ if(c==N){ for(int i=0;i<M;i++) if(cnt[i]) return; B->code[B->n++]=code; return; }
  int rem=0; for(int i=0;i<M;i++) rem+=cnt[i]; if(rem>N-c) return;
  enum_rec(c+1,cnt,code,B,cap);
  for(int i=0;i<M;i++) if(cnt[i]){ cnt[i]--; enum_rec(c+1,cnt,code|((uint32_t)(i+1)<<(2*c)),B,cap); cnt[i]++; } }
static long multinom(int *a){ int s=0; for(int i=0;i<M;i++) s+=a[i]; if(s>N) return 0; double r=1; int k=N; for(int i=0;i<M;i++) for(int t=1;t<=a[i];t++){ r=r*k/t; k--; } return (long)(r+0.5); }
static int cmpu(const void*x,const void*y){ uint32_t a=*(uint32_t*)x,b=*(uint32_t*)y; return a<b?-1:a>b; }
static Basis mk(int *a){ Basis B; for(int i=0;i<M;i++) if(a[i]<0){B.n=0;B.code=NULL;return B;} long cap=multinom(a); B.code=malloc(sizeof(uint32_t)*(cap+1)); B.n=0; int cnt[8]; memcpy(cnt,a,sizeof(int)*M); enum_rec(0,cnt,0,&B,cap); qsort(B.code,B.n,sizeof(uint32_t),cmpu); return B; }
static long find(Basis*B,uint32_t c){ long lo=0,hi=B->n-1; while(lo<=hi){ long mid=(lo+hi)/2; if(B->code[mid]==c) return mid; if(B->code[mid]<c) lo=mid+1; else hi=mid-1;} return -1; }
/* multiply monomial by l_i (coef 1 per empty column) -> add into row; by l_i^2 (coef 2 per unordered pair of empty columns) */
static void add_li(uint32_t m,int i,int coef,Basis*T,unsigned char*row){ for(int c=0;c<N;c++) if(!((m>>(2*c))&3)){ long j=find(T,m|((uint32_t)(i+1)<<(2*c))); row[j]=(row[j]+coef)%3; } }
static void add_li2(uint32_t m,int i,int coef,Basis*T,unsigned char*row){ for(int c=0;c<N;c++) if(!((m>>(2*c))&3)) for(int d=c+1;d<N;d++) if(!((m>>(2*d))&3)){ long j=find(T,m|((uint32_t)(i+1)<<(2*c))|((uint32_t)(i+1)<<(2*d))); row[j]=(row[j]+2*coef)%3; } }
static long rank3(unsigned char*A,long r,long c){ long rk=0; for(long col=0;col<c&&rk<r;col++){ long p=-1; for(long i=rk;i<r;i++) if(A[i*c+col]){p=i;break;} if(p<0) continue;
    if(p!=rk) for(long j=0;j<c;j++){unsigned char t=A[p*c+j];A[p*c+j]=A[rk*c+j];A[rk*c+j]=t;}
    unsigned char inv=A[rk*c+col]; for(long j=col;j<c;j++) A[rk*c+j]=(A[rk*c+j]*inv)%3;
    #pragma omp parallel for schedule(static)
    for(long i=0;i<r;i++) if(i!=rk&&A[i*c+col]){ unsigned char f=A[i*c+col]; for(long j=col;j<c;j++) A[i*c+j]=(A[i*c+j]+3*3-f*A[rk*c+j])%3; }
    rk++; } return rk; }
int main(int argc,char**argv){ M=atoi(argv[1]); int Nmin=atoi(argv[2]),Nmax=atoi(argv[3]),smax=atoi(argv[4]); FILE*out=fopen(argv[5],"w"); fprintf(out,"["); int first=1;
  for(N=Nmin;N<=Nmax;N++) for(int s=2;s<=smax&&s<=N;s++){
    /* multidegrees a with sum s, sorted nonincreasing (S_M symmetry) */
    int a[8]={0}; 
    void rec(int i,int rem,int maxv){ if(i==M){ if(rem) return;
        /* source space: components i with a_i>=2 */
        Basis src[8]; long off[9]; off[0]=0; for(int t=0;t<M;t++){ int b[8]; memcpy(b,a,sizeof b); b[t]-=2; src[t]=mk(b); off[t+1]=off[t]+src[t].n; }
        long dimS=off[M]; if(dimS==0){ for(int t=0;t<M;t++) free(src[t].code); return; }
        Basis T=mk(a);
        unsigned char*Phi=calloc((size_t)dimS*T.n,1);
        for(int t=0;t<M;t++) for(long r=0;r<src[t].n;r++) add_li2(src[t].code[r],t,1,&T,Phi+(off[t]+r)*T.n);
        long rk=rank3(Phi,dimS,T.n); free(Phi); long ker=dimS-rk;
        /* Taylor vectors in source space */
        long nF=0,nK=0; Basis fb[8]; Basis kb[8][8];
        for(int t=0;t<M;t++){ int b[8]; memcpy(b,a,sizeof b); b[t]-=3; fb[t]=mk(b); nF+=fb[t].n; }
        for(int t=0;t<M;t++) for(int u=t+1;u<M;u++){ int b[8]; memcpy(b,a,sizeof b); b[t]-=2; b[u]-=2; kb[t][u]=mk(b); nK+=kb[t][u].n; }
        long nT=nF+nK; long trk=0;
        if(nT>0){ unsigned char*Tay=calloc((size_t)nT*dimS,1); long row=0;
          for(int t=0;t<M;t++) for(long r=0;r<fb[t].n;r++,row++) add_li(fb[t].code[r],t,1,&src[t],Tay+row*dimS+off[t]);
          for(int t=0;t<M;t++) for(int u=t+1;u<M;u++) for(long r=0;r<kb[t][u].n;r++,row++){ uint32_t m=kb[t][u].code[r];
              add_li2(m,u,1,&src[t],Tay+row*dimS+off[t]); add_li2(m,t,2,&src[u],Tay+row*dimS+off[u]); }
          trk=rank3(Tay,nT,dimS); free(Tay); }
        fprintf(out,"%s{\"M\":%d,\"N\":%d,\"s\":%d,\"a\":[",first?"":",",M,N,s); first=0; for(int t=0;t<M;t++) fprintf(out,"%s%d",t?",":"",a[t]);
        fprintf(out,"],\"src\":%ld,\"tgt\":%ld,\"ker\":%ld,\"taylor\":%ld,\"excess\":%ld}\n",dimS,T.n,ker,trk,ker-trk);
        if(ker!=trk) printf("M=%d N=%d s=%d a=(%d,%d,%d) ker=%ld taylor=%ld excess=%ld\n",M,N,s,a[0],M>1?a[1]:0,M>2?a[2]:0,ker,trk,ker-trk);
        fflush(stdout); fflush(out);
        free(T.code); for(int t=0;t<M;t++){ free(src[t].code); free(fb[t].code); for(int u=t+1;u<M;u++) free(kb[t][u].code);} return; }
      for(int v=(rem<maxv?rem:maxv); v>=0; v--){ a[i]=v; rec(i+1,rem-v,v); } a[i]=0; }
    rec(0,s,s);
    printf("done N=%d s=%d\n",N,s); fflush(stdout); }
  fprintf(out,"]\n"); fclose(out); return 0; }
