// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Complete bounded companion tests over a satisfiable Boolean old domain.
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
using Mask = std::uint64_t;
using Poly = std::vector<Mask>;
constexpr int OLD=6, BLOCKS=3, FAN=5, H=2, U=2, D=8, VARS=36;
constexpr Mask OLD_MASK=(Mask(1)<<OLD)-1;
void need(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
Poly add(const Poly& a,const Poly& b){
    Poly result;std::set_symmetric_difference(a.begin(),a.end(),b.begin(),b.end(),
                                             std::back_inserter(result));return result;
}
Poly multiply(const Poly& a,const Poly& b){
    Poly values,result;
    for(Mask x:a)for(Mask y:b)values.push_back(x|y);
    std::sort(values.begin(),values.end());
    for(std::size_t i=0;i<values.size();){
        std::size_t j=i+1;while(j<values.size()&&values[j]==values[i])++j;
        if((j-i)&1)result.push_back(values[i]);
        i=j;
    }return result;
}
Poly variable(int i){return {Mask(1)<<i};}
int evaluate(const Poly& f,Mask point){
    int value=0;for(Mask term:f)value^=((term&point)==term);return value;
}
template<class T>void array(std::ostream& out,const std::vector<T>& values){
    out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}
Mask diagonal(int block,int input){
    Mask value=0;
    for(int row=0;row<H;++row)value|=Mask(1)<<(OLD+(block*H+row)*FAN+input);
    return value;
}
struct Fixture{
    std::array<std::array<Poly,FAN>,BLOCKS> g,companions;
    std::array<int,3> points{0,1,2};
    std::array<std::array<int,BLOCKS>,3> selected{};
    std::array<std::array<std::array<int,64>,FAN>,BLOCKS> nu{},mu{},plain_mu{};
    std::array<std::array<std::array<std::array<std::array<int,64>,FAN>,FAN>,BLOCKS>,BLOCKS> phi{},plain_phi{};
    Fixture(){
        for(int j=0;j<FAN;++j)g[0][j]=variable(j);
        g[1]={add(Poly{0},variable(0)),variable(1),variable(2),variable(3),variable(5)};
        g[2]=g[0];g[2][0]=add(variable(0),variable(1));
        for(int p=0;p<3;++p)for(int b=0;b<BLOCKS;++b){
            selected[p][b]=-1;
            for(int j=0;j<FAN;++j)if(evaluate(g[b][j],points[p])){
                selected[p][b]=j;break;
            }
        }
        for(int b=0;b<BLOCKS;++b){
            Poly product{0};
            for(int row=0;row<H;++row){
                Poly factor{0};
                for(int j=0;j<FAN;++j)
                    factor=add(factor,multiply(variable(OLD+(b*H+row)*FAN+j),g[b][j]));
                product=multiply(product,factor);
            }
            for(int j=0;j<FAN;++j){
                companions[b][j]=multiply(g[b][j],product);
                for(int mask=0;mask<64;++mask){
                    int raw=weighted_single(b,j,mask);
                    nu[b][j][mask]=raw^(((b+j)&1)&&(mask==63));
                    plain_mu[b][j][mask]=raw;
                }
                for(int mask=0;mask<64;++mask){
                    int value=0;
                    for(Mask term:multiply(g[b][j],Poly{Mask(mask)}))
                        value^=nu[b][j][term];
                    mu[b][j][mask]=value;
                }
            }
        }
        for(int a=0;a<BLOCKS;++a)for(int b=a+1;b<BLOCKS;++b)
            for(int j=0;j<FAN;++j)for(int k=0;k<FAN;++k)for(int mask=0;mask<64;++mask){
                int raw=0;
                for(int p=0;p<3;++p)if(selected[p][a]==j&&selected[p][b]==k)
                    raw^=((mask&points[p])==mask);
                plain_phi[a][b][j][k][mask]=raw;
                phi[a][b][j][k][mask]=raw^(((a+b+j+k)&1)&&(mask==15));
            }
    }
    int root(int mask)const{
        int value=0;for(int point:points)value^=((mask&point)==mask);return value;
    }
    int weighted_single(int b,int j,int mask)const{
        int value=0;
        for(int p=0;p<3;++p)if(selected[p][b]==j)value^=((mask&points[p])==mask);
        return value;
    }
    int moment(Mask monomial,bool perturb=true,bool corrupt_pair=false)const{
        int old=int(monomial&OLD_MASK),count=0;
        std::array<int,BLOCKS> blocks{},inputs{};
        for(int b=0;b<BLOCKS;++b){
            Mask local=monomial&(((Mask(1)<<(H*FAN))-1)<<(OLD+b*H*FAN));
            if(!local)continue;
            int match=-1;for(int j=0;j<FAN;++j)if(local==diagonal(b,j))match=j;
            if(match<0)return 0;
            blocks[count]=b;inputs[count]=match;++count;
        }
        if(count==0)return root(old);
        if(count==1)return perturb?mu[blocks[0]][inputs[0]][old]:
                                          plain_mu[blocks[0]][inputs[0]][old];
        if(count==2){
            int a=blocks[0],b=blocks[1],j=inputs[0],k=inputs[1];
            int result=perturb?phi[a][b][j][k][old]:plain_phi[a][b][j][k][old];
            if(corrupt_pair&&a==0&&b==1&&j==1&&k==0&&old==0)result^=1;
            return result;
        }return 0;
    }
    int check(int b,int i,Mask cofactor,bool perturb=true,bool corrupt_pair=false)const{
        int value=0;
        for(Mask term:companions[b][i])value^=moment(term|cofactor,perturb,corrupt_pair);
        return value;
    }
};
int main(int argc,char** argv){
    try{
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"refusing existing output");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"cannot create output");
        Fixture f;
        out<<"{\"type\":\"schema\",\"version\":1,\"field\":2,\"old_bits\":6,"
               "\"blocks\":3,\"fan_in\":5,\"accuracy\":2,\"u\":2,\"degree\":8,"
               "\"original_companion_degree\":5,\"old_base\":\"BOOL only; not PHP\","
               "\"monomial_encoding\":\"uint64 bit mask; all variables Boolean\","
               "\"root_points\":[0,1,2]}\n";
        std::vector<int> root;for(int m=0;m<64;++m)root.push_back(f.root(m));
        out<<"{\"type\":\"root\",\"moments\":";array(out,root);out<<"}\n";
        int single_changes=0,pair_changes=0;
        for(int b=0;b<BLOCKS;++b)for(int j=0;j<FAN;++j){
            std::vector<int> nu,mu,plain;
            for(int m=0;m<64;++m){
                nu.push_back(f.nu[b][j][m]);mu.push_back(f.mu[b][j][m]);
                plain.push_back(f.plain_mu[b][j][m]);
                single_changes+=f.mu[b][j][m]!=f.plain_mu[b][j][m];
            }
            out<<"{\"type\":\"singleton\",\"block\":"<<b<<",\"input\":"<<j<<",\"g\":";
            array(out,f.g[b][j]);out<<",\"companion\":";array(out,f.companions[b][j]);
            out<<",\"nu\":";array(out,nu);out<<",\"mu\":";array(out,mu);
            out<<",\"unperturbed_mu\":";array(out,plain);out<<"}\n";
        }
        for(int a=0;a<BLOCKS;++a)for(int b=a+1;b<BLOCKS;++b)
            for(int j=0;j<FAN;++j)for(int k=0;k<FAN;++k){
                std::vector<int> masks,values,plain;
                for(int m=0;m<64;++m)if(__builtin_popcount(unsigned(m))<=H+U){
                    masks.push_back(m);values.push_back(f.phi[a][b][j][k][m]);
                    plain.push_back(f.plain_phi[a][b][j][k][m]);
                    pair_changes+=values.back()!=plain.back();
                }
                out<<"{\"type\":\"pair\",\"blocks\":["<<a<<','<<b<<"],\"inputs\":["
                   <<j<<','<<k<<"],\"masks\":";array(out,masks);
                out<<",\"phi\":";array(out,values);out<<",\"unperturbed_phi\":";
                array(out,plain);out<<"}\n";
            }
        need(single_changes>0&&pair_changes>0,"higher-moment perturbations were vacuous");
        std::vector<Mask> cofactors;
        std::function<void(int,int,Mask)> enumerate=[&](int first,int budget,Mask monomial){
            cofactors.push_back(monomial);
            if(!budget)return;
            for(int v=first;v<VARS;++v)enumerate(v+1,budget-1,monomial|(Mask(1)<<v));
        };
        enumerate(0,D-(2*H+1),0);
        need(cofactors.size()==7807,"cofactor count");
        std::uint64_t checks=0;
        bool corruption_found=false;
        for(int b=0;b<BLOCKS;++b)for(int i=0;i<FAN;++i)for(Mask cofactor:cofactors){
            int value=f.check(b,i,cofactor);
            need(value==0,"allowed original-NS companion multiple is not annihilated");
            out<<"{\"type\":\"companion_check\",\"block\":"<<b<<",\"input\":"<<i
               <<",\"cofactor\":"<<cofactor<<",\"moment\":"<<value<<"}\n";++checks;
            if(!corruption_found&&f.check(b,i,cofactor,true,true)){
                out<<"{\"type\":\"incoherent_pair_control\",\"block\":"<<b
                   <<",\"input\":"<<i<<",\"cofactor\":"<<cofactor<<",\"moment\":1,"
                     "\"changed_component\":\"phi[0,1][1,0](1)\"}\n";
                corruption_found=true;
            }
        }
        need(corruption_found,"incoherent pair control was not detected");
        int triple_controls=0,triple_failures=0;
        for(int b=0;b<BLOCKS;++b){
            int a=(b+1)%BLOCKS,c=(b+2)%BLOCKS;
            for(int i=0;i<FAN;++i)for(int j=0;j<FAN;++j)for(int k=0;k<FAN;++k){
                Mask cofactor=diagonal(a,j)|diagonal(c,k);
                int value=f.check(b,i,cofactor,false,false);
                ++triple_controls;triple_failures+=value;
                out<<"{\"type\":\"missing_triple_control\",\"degree\":9,\"block\":"
                   <<b<<",\"input\":"<<i<<",\"cofactor\":"<<cofactor
                   <<",\"moment\":"<<value<<"}\n";
            }
        }
        need(triple_failures>0,"missing-triple boundary control was vacuous");
        out<<"{\"type\":\"summary\",\"companion_checks\":"<<checks
           <<",\"singleton_moment_changes\":"<<single_changes
           <<",\"pair_moment_changes\":"<<pair_changes
           <<",\"triple_controls\":"<<triple_controls
           <<",\"triple_failures\":"<<triple_failures
           <<",\"incoherent_pair_detected\":true,\"passed\":true}\n";
        out.close();need(bool(out),"write failed");
        std::cout<<"Passed "<<checks<<" complete companion checks; "
                 <<single_changes<<" singleton and "<<pair_changes<<" pair high moments changed. "
                 <<triple_failures<<'/'<<triple_controls
                 <<" missing-triple controls fail at degree 9; incoherent pair detected.\n";
    }catch(const std::exception& error){std::cerr<<"ERROR: "<<error.what()<<'\n';return 1;}
}
