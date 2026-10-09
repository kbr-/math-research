// One native prime-field factorization supplies a quadratic-field torsion function and nested RR frames.
// Existing FLINT root products are reused; all extracted frames get independent FLINT polynomial checks.
#define main original_complement_main
#include "bmd_nineteen_low_check_20261009.cpp"
#undef main
#include <givaro/modular.h>
using Prime=Givaro::Modular<double>;
std::vector<std::pair<int,int>> polecols(int M){auto c=columns(M,4);std::sort(c.begin(),c.end(),[](auto a,auto b){return std::make_tuple(2*a.second+__builtin_popcount((unsigned)a.first),a.first,a.second)<std::make_tuple(2*b.second+__builtin_popcount((unsigned)b.first),b.first,b.second);});return c;}
int main(int argc,char**argv){try{
 ck(argc==5,"input out max-pole threads");std::ifstream in(argv[1]);int p,k,nref;in>>p>>k>>nref;std::vector<int>degrees(nref),labels(4);for(auto&d:degrees)in>>d;for(auto&v:labels)in>>v;int cap=std::stoi(argv[3]);ck(p>=17&&p<=97&&k>=32&&k<=672&&k%32==0&&k<=cap,"bounded measured pole");int threads=std::stoi(argv[4]);ck(threads>=1&&threads<=8,"shared threads");
 Job job;job.n=4;job.p=p;job.f=2;job.mod={36,1,1};if(in>>job.mod[0]){ck(bool(in>>job.mod[1]>>job.mod[2]),"explicit field modulus");}else ck(p==37,"nondefault prime requires explicit modulus");ck(job.mod[2]==1,"monic quadratic");Field F(p,2,job.mod);Prime K(p);int N=8*k,prec=N+1;auto begun=std::chrono::steady_clock::now();auto co=prefixes(job,F,labels,prec,4);auto cols=polecols(k);int U=cols.size(),R=2*N,C=2*U;ck(U==8*k-4,"source dimension");ck(8.0*R*C<1200000000.0,"matrix below1.2GB");
 std::vector<double>A((size_t)R*C,0);for(int j=0;j<U;j++){auto[s,q]=cols[j];for(int i=q;i<N;i++){int c=F.zech2padic(co[s*prec+i-q]),x=c%p,y=c/p;A[(size_t)(2*i)*C+2*j]=x;A[(size_t)(2*i)*C+2*j+1]=((p-job.mod[0])*y)%p;A[(size_t)(2*i+1)*C+2*j]=y;A[(size_t)(2*i+1)*C+2*j+1]=(x-job.mod[1]*y+p*p)%p;}}
 std::cout<<"PREP rows="<<R<<" columns="<<C<<" matrix_bytes="<<A.size()*8<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count()<<std::endl;
 auto fact=std::chrono::steady_clock::now();std::vector<size_t>P(C),Q(R);std::iota(P.begin(),P.end(),0);std::iota(Q.begin(),Q.end(),0);
 size_t rank=FFPACK::LUdivine(K,FFLAS::FflasNonUnit,FFLAS::FflasNoTrans,R,C,A.data(),C,P.data(),Q.data());
 ck(rank==C-2,"one-dimensional quadratic torsion kernel");std::vector<int>perm(C);std::iota(perm.begin(),perm.end(),0);for(size_t i=0;i<rank;i++){ck(P[i]>=i&&P[i]<(size_t)C,"swap convention");std::swap(perm[i],perm[P[i]]);}std::vector<int>pos(C);for(int i=0;i<C;i++)pos[perm[i]]=i;
 std::cout<<"FACTORIZATION prime_rank="<<rank<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-fact).count()<<std::endl;
 nmod_poly_t mod,el;nmod_poly_init(mod,p);nmod_poly_init(el,p);nmod_poly_set_coeff_ui(mod,0,job.mod[0]);nmod_poly_set_coeff_ui(mod,1,job.mod[1]);nmod_poly_set_coeff_ui(mod,2,1);fq_nmod_ctx_t ctx;fq_nmod_ctx_init_modulus(ctx,mod,"a");fq_nmod_t e;fq_nmod_init(e,ctx);
 auto set=[&](int c){nmod_poly_zero(el);nmod_poly_set_coeff_ui(el,0,c%p);nmod_poly_set_coeff_ui(el,1,c/p);fq_nmod_set_nmod_poly(e,el,ctx);};
 std::vector<fq_nmod_poly_struct>sp(16);for(auto&v:sp)fq_nmod_poly_init(&v,ctx);for(int s=0;s<16;s++)for(int i=0;i<prec;i++){set(F.zech2padic(co[s*prec+i]));fq_nmod_poly_set_coeff(&sp[s],i,e,ctx);}
 fq_nmod_poly_t sum,poly,tmp;fq_nmod_poly_init(sum,ctx);fq_nmod_poly_init(poly,ctx);fq_nmod_poly_init(tmp,ctx);
 std::ofstream out(argv[2]);ck(out.good(),"output");out<<p<<' '<<k<<' '<<nref<<'\n';for(int l:labels)out<<l<<' ';out<<'\n';for(auto v:job.mod)out<<v<<' ';out<<'\n';
 auto extract=[&](int M,int jets,int want,bool torsion){auto bc=polecols(M);int u=bc.size(),r=torsion?rank:2*jets,dim=2*u-r;ck(dim==2*want,"expected prime kernel dimension");for(int i=0;i<r;i++){if(!torsion)ck(Q[i]==(size_t)i,"all leading jet rows independent");ck(perm[i]<2*u,"prefix pivots inside original pole bound");}
 std::vector<int>free;std::vector<bool>pivot(2*u,false);for(int i=0;i<r;i++)pivot[perm[i]]=true;for(int j=0;j<2*u;j++)if(!pivot[j])free.push_back(j);ck((int)free.size()==dim,"free columns");
 std::vector<double>X((size_t)r*dim);for(int i=0;i<r;i++)for(int j=0;j<dim;j++)X[(size_t)i*dim+j]=A[(size_t)i*C+pos[free[j]]];
 if(r)FFLAS::ftrsm(K,FFLAS::FflasLeft,FFLAS::FflasUpper,FFLAS::FflasNoTrans,FFLAS::FflasNonUnit,r,dim,K.mOne,A.data(),C,X.data(),dim);
 std::vector<double>B((size_t)2*u*dim,0);for(int i=0;i<r;i++)std::copy_n(X.data()+(size_t)i*dim,dim,B.data()+(size_t)perm[i]*dim);for(int j=0;j<dim;j++)B[(size_t)free[j]*dim+j]=1;
 std::vector<E>BT((size_t)dim*u);for(int j=0;j<dim;j++)for(int i=0;i<u;i++){int x=std::lround(B[(size_t)2*i*dim+j]),y=std::lround(B[(size_t)(2*i+1)*dim+j]);x=(x%p+p)%p;y=(y%p+p)%p;BT[(size_t)j*u+i]=F.padic2zech(x+p*y);}
 int ld=std::max(u,dim);std::vector<E>rankcopy((size_t)dim*ld,F.zero);for(int j=0;j<dim;j++)std::copy_n(BT.data()+(size_t)j*u,u,rankcopy.data()+(size_t)j*ld);std::vector<size_t>pv(ld),qr(dim);size_t fqrank=FFPACK::LUdivine_gauss(F,FFLAS::FflasNonUnit,dim,ld,rankcopy.data(),ld,pv.data(),qr.data());std::cout<<"BASIS_RANK pole="<<M<<" got="<<fqrank<<" expected="<<want<<std::endl;ck((int)fqrank==want,"quadratic basis rank");out<<M<<' '<<jets<<' '<<u<<' '<<want<<'\n';for(auto[s,q]:bc)out<<s<<' '<<q<<' ';out<<'\n';
 for(int j=0;j<want;j++){ck(qr[j]<(size_t)dim,"basis row profile");auto v=BT.data()+qr[j]*u;fq_nmod_poly_zero(sum,ctx);for(int s=0;s<16;s++){fq_nmod_poly_zero(poly,ctx);for(int i=0;i<u;i++)if(bc[i].first==s){set(F.zech2padic(v[i]));fq_nmod_poly_set_coeff(poly,bc[i].second,e,ctx);}fq_nmod_poly_mullow(tmp,poly,&sp[s],jets+1,ctx);fq_nmod_poly_add(sum,sum,tmp,ctx);}for(int i=0;i<jets;i++){fq_nmod_poly_get_coeff(e,sum,i,ctx);ck(fq_nmod_is_zero(e,ctx),"independent FLINT marked equation");}if(torsion){fq_nmod_poly_get_coeff(e,sum,jets,ctx);ck(!fq_nmod_is_zero(e,ctx),"exact torsion zero order");}for(int i=0;i<u;i++)out<<F.zech2padic(v[i])<<' ';out<<'\n';}
 out.flush();std::cout<<"FRAME pole="<<M<<" jets="<<jets<<" columns="<<want<<" independent_FLINT_jets=true elapsed="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count()<<std::endl;};
 extract(k,N,1,true);for(int d:degrees){int M=32*d-72,jets=256*d-768;ck(d>=3&&M<=k&&jets<=N,"reference range");extract(M,jets,188,false);}
 std::cout<<"COMPLETE one_large_factorization=true seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count()<<std::endl;
 }catch(const std::exception&e){std::cerr<<e.what()<<std::endl;return 1;}return 0;}
