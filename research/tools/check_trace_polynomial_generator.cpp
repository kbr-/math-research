// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exhaustive small-field checks of coefficient-wise trace and small bias.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

void need(bool ok,const std::string& why) {
    if(!ok)throw std::runtime_error(why);
}
struct Field {
    int k,q,modulus;
    int mul(int a,int b) const {
        int result=0;
        while(b) {
            if(b&1)result^=a;
            b>>=1;a<<=1;
            if(a&q)a^=modulus;
        }
        return result;
    }
    int power(int a,int exponent) const {
        int result=1;
        while(exponent) {
            if(exponent&1)result=mul(result,a);
            a=mul(a,a);exponent>>=1;
        }
        return result;
    }
    int trace(int a) const {
        int answer=0;
        for(int i=0;i<k;++i){answer^=a;a=mul(a,a);}
        need(answer==0 || answer==1,"Trace is not in the base field");
        return answer;
    }
    void check() const {
        need(q==(1<<k),"Field dimension mismatch");
        for(int a=1;a<q;++a)need(power(a,q-1)==1,"A nonzero field element is not a unit");
        for(int a=0;a<q;++a) {
            int ones=0;
            for(int b=0;b<q;++b) {
                need(trace(a^b)==(trace(a)^trace(b)),"Trace linearity");
                ones+=trace(mul(a,b));
            }
            need(ones==(a?q/2:0),"Trace pairing is degenerate");
        }
    }
};
void integers(std::ostream& out,const std::vector<int>& v) {
    out<<'[';for(size_t i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';
}
std::vector<std::int64_t> walsh(std::vector<std::int64_t> a) {
    for(size_t stride=1;stride<a.size();stride*=2)
        for(size_t start=0;start<a.size();start+=2*stride)
            for(size_t j=0;j<stride;++j) {
                auto x=a[start+j],y=a[start+stride+j];
                a[start+j]=x+y;a[start+stride+j]=x-y;
            }
    return a;
}
void run(std::ostream& out,Field field,int variables,int degree) {
    field.check();
    std::vector<int> monomials;
    for(int d=0;d<=degree;++d)
        for(int mask=0;mask<(1<<variables);++mask)
            if(__builtin_popcount(unsigned(mask))==d)monomials.push_back(mask);
    const int width=int(monomials.size());
    need(width<=16 && degree<field.q,"Exhaustive fixture size guard");
    const int space_size=1<<width;
    std::vector<std::int64_t> histogram(space_size),fixed_z_histogram(space_size);
    std::int64_t assignments=1,dp_checks=0;
    for(int i=0;i<variables;++i)assignments*=field.q;
    const std::int64_t seeds=assignments*field.q;
    for(std::int64_t code=0;code<assignments;++code) {
        std::vector<int> a(variables);
        auto digits=code;
        for(int i=0;i<variables;++i){a[i]=int(digits%field.q);digits/=field.q;}
        std::vector<int> products(1<<variables,1);
        for(int mask=1;mask<(1<<variables);++mask) {
            const int bit=__builtin_ctz(unsigned(mask));
            products[mask]=field.mul(products[mask^(1<<bit)],a[bit]);
        }
        for(int z=0;z<field.q;++z) {
            int coefficients=0;
            for(int j=0;j<width;++j)
                coefficients|=field.trace(field.mul(z,products[monomials[j]]))<<j;
            ++histogram[coefficients];
            if(z==1)++fixed_z_histogram[coefficients];
            for(int x=0;x<(1<<variables);++x) {
                std::vector<int> dp(degree+1);dp[0]=1;
                for(int i=0;i<variables;++i)
                    for(int d=std::min(degree,i+1);d>=1;--d)
                        if((x>>i)&1)dp[d]^=field.mul(a[i],dp[d-1]);
                int sum=0;for(int value:dp)sum^=value;
                int recurrence_value=field.trace(field.mul(z,sum));
                int coefficient_value=0;
                for(int j=0;j<width;++j)
                    if((monomials[j]&x)==monomials[j])
                        coefficient_value^=(coefficients>>j)&1;
                need(recurrence_value==coefficient_value,"Truncated-product recurrence disagrees");
                ++dp_checks;
            }
        }
    }
    const auto spectrum=walsh(histogram),control_spectrum=walsh(fixed_z_histogram);
    need(spectrum[0]==seeds && control_spectrum[0]==assignments,"Mass mismatch");
    std::int64_t largest=0,smallest=seeds,control_abs=0;
    int largest_test=-1;
    for(int test=1;test<space_size;++test) {
        need(spectrum[test]>=0,"Unexpected negative trace-character average");
        need(spectrum[test]*field.q<=degree*seeds,"Degree/field-size bias bound failed");
        if(spectrum[test]>largest){largest=spectrum[test];largest_test=test;}
        smallest=std::min(smallest,spectrum[test]);
        control_abs=std::max(control_abs,std::int64_t(
            control_spectrum[test]<0?-control_spectrum[test]:control_spectrum[test]));
    }
    need(control_abs==assignments && control_abs*field.q>degree*assignments,
         "Fixed trace multiplier must fail the promised bias bound");
    out<<"{\"record\":\"case\",\"variables\":"<<variables<<",\"degree\":"<<degree
       <<",\"extension_degree\":"<<field.k<<",\"field_size\":"<<field.q
       <<",\"modulus_bits\":"<<field.modulus<<",\"feature_masks\":";
    integers(out,monomials);
    out<<",\"seed_count\":"<<seeds<<",\"fixed_z_seed_count\":"<<assignments<<"}\n";
    for(int index=0;index<space_size;++index)
        out<<"{\"record\":\"distribution_and_fourier\",\"variables\":"<<variables
           <<",\"degree\":"<<degree<<",\"field_size\":"<<field.q
           <<",\"index\":"<<index<<",\"polynomial_count\":"<<histogram[index]
           <<",\"dual_character_sum\":"<<spectrum[index]
           <<",\"fixed_z_polynomial_count\":"<<fixed_z_histogram[index]
           <<",\"fixed_z_dual_character_sum\":"<<control_spectrum[index]<<"}\n";
    out<<"{\"record\":\"summary\",\"variables\":"<<variables<<",\"degree\":"<<degree
       <<",\"field_size\":"<<field.q<<",\"seed_count\":"<<seeds
       <<",\"nonzero_dual_tests\":"<<space_size-1
       <<",\"max_bias_numerator\":"<<largest<<",\"min_bias_numerator\":"<<smallest
       <<",\"bias_denominator\":"<<seeds<<",\"maximizing_dual_test\":"<<largest_test
       <<",\"bound_numerator\":"<<degree<<",\"bound_denominator\":"<<field.q
       <<",\"DP_evaluation_checks\":"<<dp_checks
       <<",\"fixed_z_control_abs_bias_numerator\":"<<control_abs
       <<",\"fixed_z_control_denominator\":"<<assignments<<",\"all_passed\":true}\n";
    std::cout<<"v="<<variables<<", t="<<degree<<", Q="<<field.q<<": "<<seeds
             <<" seeds, "<<space_size-1<<" nonzero tests, max bias "<<largest<<'/'<<seeds
             <<" <= "<<degree<<'/'<<field.q<<"; "<<dp_checks
             <<" DP evaluations; fixed-z control fails as expected.\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3 && std::string(argv[1])=="--out","Usage: checker --out PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"Refusing to overwrite earlier evidence");
        if(!path.parent_path().empty())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"Cannot create output");
        out<<"{\"record\":\"schema\",\"base_field\":2,"
              "\"coefficient_rule\":\"c_A=Tr(z*product_{i in A} a_i), |A|<=t\","
              "\"index_rule\":\"bit j denotes feature_masks[j]; histogram index is a polynomial, "
              "Fourier index is a dual linear test\","
              "\"scope\":\"exhaustive generator distributions and characters on small formal polynomial spaces; not PHP design sampling\"}\n";
        run(out,{2,4,7},2,1);
        run(out,{3,8,11},3,2);
        run(out,{3,8,11},3,3);
        run(out,{2,4,7},4,2);
        out.close();need(bool(out),"Output write failed");
    } catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
