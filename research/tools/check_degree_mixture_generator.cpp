// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact degree-mixture generator on the Boolean polynomial quotient, over F2/F3.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using Count=std::int64_t;
void need(bool ok,const std::string& why) {
    if(!ok)throw std::runtime_error(why);
}
int power(int p,int e) {
    int answer=1;
    while(e--){need(answer<=1000000/p,"Finite fixture guard");answer*=p;}
    return answer;
}
template<class T> void array(std::ostream& out,const std::vector<T>& v) {
    out<<'[';for(size_t i=0;i<v.size();++i){if(i)out<<',';out<<int(v[i]);}out<<']';
}
void counts(std::ostream& out,const std::vector<Count>& v) {
    out<<'[';for(size_t i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';
}
void run(std::ostream& out,int p,int v,int t) {
    std::vector<int> features;
    for(int d=0;d<=t;++d)
        for(int mask=0;mask<(1<<v);++mask)
            if(__builtin_popcount(unsigned(mask))==d)features.push_back(mask);
    int m=int(features.size()),space=power(p,m),base=power(p,v*t);
    std::vector<std::vector<unsigned char>> digits(space,std::vector<unsigned char>(m));
    for(int code=0;code<space;++code) {
        int rest=code;
        for(int j=0;j<m;++j){digits[code][j]=rest%p;rest/=p;}
    }
    std::vector<std::vector<Count>> histogram(t+1,std::vector<Count>(space));
    for(int scalar=0;scalar<p;++scalar)histogram[0][scalar]=base/p;
    for(int seed=0;seed<base;++seed) {
        int rest=seed;
        std::vector<int> polynomial(1<<v);polynomial[0]=1;
        for(int degree=1;degree<=t;++degree) {
            std::vector<int> linear(v),next(1<<v);
            for(int i=0;i<v;++i){linear[i]=rest%p;rest/=p;}
            for(int mask=0;mask<(1<<v);++mask)if(polynomial[mask])
                for(int i=0;i<v;++i)
                    next[mask|(1<<i)]=(next[mask|(1<<i)]+polynomial[mask]*linear[i])%p;
            polynomial=std::move(next);
            int index=0,multiplier=1;
            for(int mask:features){index+=multiplier*polynomial[mask];multiplier*=p;}
            ++histogram[degree][index];
        }
    }
    std::vector<int> supported;
    for(int index=0;index<space;++index) {
        bool present=false;
        for(int j=0;j<=t;++j)present|=histogram[j][index]!=0;
        if(present)supported.push_back(index);
    }
    const Count denominator=Count(p-1)*base,mixture_denominator=(t+1)*denominator;
    Count maximum=-1;
    int maximizer=-1;
    std::vector<Count> minimum_degree_counts(t+1);
    out<<"{\"record\":\"case\",\"p\":"<<p<<",\"variables\":"<<v<<",\"t\":"<<t
       <<",\"feature_masks\":";array(out,features);
    out<<",\"per_degree_weight_denominator\":"<<base
       <<",\"mixture_weight_denominator\":"<<(t+1)*base
       <<",\"coefficient_space_size\":"<<space<<"}\n";
    for(int test=0;test<space;++test) {
        std::vector<std::vector<Count>> values(t+1,std::vector<Count>(p));
        for(int index:supported) {
            unsigned value=0;
            for(int j=0;j<m;++j)value+=digits[test][j]*digits[index][j];
            value%=p;
            for(int degree=0;degree<=t;++degree)
                values[degree][value]+=histogram[degree][index];
        }
        std::vector<Count> character(t+1);
        Count mixture=0;
        for(int degree=0;degree<=t;++degree) {
            need(std::accumulate(values[degree].begin(),values[degree].end(),Count(0))==base,
                 "Per-degree mass mismatch");
            for(int value=2;value<p;++value)
                need(values[degree][value]==values[degree][1],"Nonzero values are not equiprobable");
            character[degree]=p*values[degree][0]-base;
            need(character[degree]>=0 && character[degree]<=denominator,"Character average range");
            mixture+=character[degree];
        }
        int least=-1;
        for(int j=0;j<m;++j)if(digits[test][j]) {
            least=__builtin_popcount(unsigned(features[j]));break;
        }
        if(test) {
            need(least>=0,"Nonzero test lacks a degree");
            ++minimum_degree_counts[least];
            if(least==0)need(character[0]==0,"Constant sampler failed");
            else need(character[least]*p*(p-1)<=denominator,
                      "Minimal-degree contraction bound failed");
            need(2*(t+1)*mixture<=(2*(t+1)-1)*mixture_denominator,
                 "Mixture spectral gap failed");
            if(mixture>maximum){maximum=mixture;maximizer=test;}
        }
        std::vector<Count> polynomial_counts(t+1);
        for(int j=0;j<=t;++j)polynomial_counts[j]=histogram[j][test];
        out<<"{\"record\":\"distribution_and_tests\",\"p\":"<<p<<",\"variables\":"<<v
           <<",\"t\":"<<t<<",\"index\":"<<test<<",\"polynomial_weights_by_degree\":";
        counts(out,polynomial_counts);
        out<<",\"least_test_degree\":"<<least<<",\"value_counts_by_degree\":[";
        for(int j=0;j<=t;++j){if(j)out<<',';counts(out,values[j]);}
        out<<"],\"character_numerators_by_degree\":";counts(out,character);
        out<<",\"character_denominator\":"<<denominator
           <<",\"mixture_character_numerator\":"<<mixture
           <<",\"mixture_character_denominator\":"<<mixture_denominator<<"}\n";
        if(test==1)need(character[t]==denominator,"Fixed-positive-degree control should have bias one");
    }
    out<<"{\"record\":\"summary\",\"p\":"<<p<<",\"variables\":"<<v<<",\"t\":"<<t
       <<",\"nonzero_tests\":"<<space-1<<",\"max_mixture_bias_numerator\":"<<maximum
       <<",\"max_mixture_bias_denominator\":"<<mixture_denominator
       <<",\"maximizing_test\":"<<maximizer<<",\"least_degree_counts\":";
    counts(out,minimum_degree_counts);
    out<<",\"bound_numerator\":"<<2*(t+1)-1<<",\"bound_denominator\":"<<2*(t+1)
       <<",\"fixed_degree_control\":{\"test\":1,\"degree\":"<<t<<",\"bias\":1}"
       <<",\"all_passed\":true}\n";
    auto gcd=std::gcd(maximum,mixture_denominator);
    std::cout<<"p="<<p<<", v="<<v<<", t="<<t<<": "<<space-1
             <<" nonzero tests; max mixture bias "<<maximum/gcd<<'/'<<mixture_denominator/gcd
             <<" <= "<<2*(t+1)-1<<'/'<<2*(t+1)
             <<"; minimal-degree bound passed; fixed-degree control rejected.\n";
}
void raw_control(std::ostream& out,int p,int d) {
    int total=power(p,d);
    std::vector<Count> values(p);
    for(int seed=0;seed<total;++seed) {
        int rest=seed,product=1;
        for(int i=0;i<d;++i){product=product*(rest%p)%p;rest/=p;}
        ++values[product];
    }
    Count numerator=p*values[0]-total,denominator=Count(p-1)*total;
    need(numerator*p*(p-1)>denominator,"Raw-power control did not violate the Boolean bound");
    out<<"{\"record\":\"raw_power_control\",\"p\":"<<p<<",\"degree\":"<<d
       <<",\"value_counts\":";counts(out,values);
    out<<",\"character_numerator\":"<<numerator<<",\"character_denominator\":"<<denominator
       <<",\"scope\":\"coefficient of X_1^d before Boolean reduction; not a Boolean-quotient functional\","
         "\"violates_minimal_degree_bound\":true}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","Usage: checker --out PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"Refusing to overwrite prior evidence");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"Cannot create output");
        out<<"{\"record\":\"schema\",\"model\":\"Boolean polynomial quotient over Fp\","
              "\"sampler\":\"uniform degree J in 0..t; J=0 uniform scalar, J>=1 product of J independent uniform homogeneous linear forms\","
              "\"index_rule\":\"base-p coefficients in feature_masks order; same index labels a dual test in test fields\","
              "\"scope\":\"exact base-sampler distributions and every coefficient linear test; no PHP design sampling\"}\n";
        run(out,2,3,3);
        run(out,3,3,2);
        run(out,3,3,3);
        raw_control(out,2,3);
        raw_control(out,3,3);
        out.close();need(bool(out),"Output write failed");
    } catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
