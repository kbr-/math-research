// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kamil Braun
// Exact old matching moments and a conditioning-commutation control.
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

void need(bool ok,const char* message) {
    if(!ok) throw std::runtime_error(message);
}
int residue(int x,int p) { return (x%p+p)%p; }
struct Design {
    int rows,columns=3,prime;
    bool point;
    int variables() const { return rows*columns; }
    int first(int x) const {
        return point ? int(x%columns==x/columns) : int(x%columns==0);
    }
    int second(int x,int y,bool unsigned_control=false) const {
        if(point)return first(x)*first(y);
        if(x==y)return first(x);
        if(x/columns==y/columns)return 0;
        if(x/columns>y/columns)std::swap(x,y);
        const int a=x%columns,b=y%columns;
        if((a==0&&b==1)||(a==2&&b==0))return 1;
        if(a==2&&b==1)return unsigned_control?1:residue(-1,prime);
        return 0;
    }
    int moment(int x,int y=-1,bool unsigned_control=false) const {
        if(x<0)return 1;
        return y<0?first(x):second(x,y,unsigned_control);
    }
};
int check(std::ostream& out,const Design& d,const std::string& key) {
    int checks=0;
    auto save=[&](const char* type,int a,int b,int multiplier,int value) {
        value=residue(value,d.prime);
        out<<"{\"record\":\"constraint\",\"case\":\""<<key<<"\",\"kind\":\""<<type
           <<"\",\"a\":"<<a<<",\"b\":"<<b<<",\"multiplier_variable\":"<<multiplier
           <<",\"moment\":"<<value<<"}\n";
        need(value==0,"all ordinary degree-two generator multiples vanish");
        ++checks;
    };
    for(int row=0;row<d.rows;++row)for(int q=-1;q<d.variables();++q) {
        int value=-(q<0?1:d.first(q));
        for(int col=0;col<d.columns;++col)
            value+=q<0?d.first(row*d.columns+col):d.second(q,row*d.columns+col);
        save("row_equation",row,-1,q,value);
    }
    for(int x=0;x<d.variables();++x)
        save("boolean",x,-1,-1,d.second(x,x)-d.first(x));
    for(int row=0;row<d.rows;++row)
        for(int a=0;a<d.columns;++a)for(int b=a+1;b<d.columns;++b)
            save("same_row",row*d.columns+a,row*d.columns+b,-1,
                 d.second(row*d.columns+a,row*d.columns+b));
    for(int a=0;a<d.rows;++a)for(int b=a+1;b<d.rows;++b)
        for(int col=0;col<d.columns;++col)
            save("same_column",a*d.columns+col,b*d.columns+col,-1,
                 d.second(a*d.columns+col,b*d.columns+col));
    return checks;
}
void write_design(std::ostream& out,const Design& d,const std::string& key) {
    out<<"{\"record\":\"design\",\"case\":\""<<key<<"\",\"prime\":"<<d.prime
       <<",\"rows\":"<<d.rows<<",\"columns\":3,\"normalization\":1,\"first\":[";
    for(int x=0;x<d.variables();++x) { if(x)out<<',';out<<d.first(x); }
    out<<"],\"second\":[";
    for(int x=0;x<d.variables();++x) {
        if(x)out<<',';
        out<<'[';
        for(int y=0;y<d.variables();++y) { if(y)out<<',';out<<d.second(x,y); }
        out<<']';
    }
    out<<"]}\n";
}
int main(int argc,char** argv) {
    try {
        need(argc==3&&std::string(argv[1])=="--out","usage: --out NEW_PATH");
        std::filesystem::path path=argv[2];
        need(!std::filesystem::exists(path),"output already exists");
        if(path.has_parent_path())std::filesystem::create_directories(path.parent_path());
        std::ofstream out(path);need(bool(out),"output open");
        out<<"{\"record\":\"schema\",\"version\":1,\"variables\":\"row-major, zero-based; constant multiplier is -1\","
             "\"degree\":2,\"encoding\":\"ordinary residues; complete first and second moments\"}\n";
        int total=0,cases=0;
        for(int p:{2,3,5}) {
            Design d{4,3,p,false};
            std::string key="nonpoint_F"+std::to_string(p);
            write_design(out,d,key);
            int count=check(out,d,key);
            need(count==94,"complete 4-by-3 constraint count");
            total+=count;++cases;
            int actual=d.second(0,3),factorized=d.first(0)*d.first(3);
            need(actual==0&&factorized==1,"same-column covariance obstructs point factorization");
            int unsigned_row=0;
            for(int j=0;j<3;++j)unsigned_row+=d.second(2,3+j,true);
            unsigned_row=residue(unsigned_row-d.first(2),p);
            need((unsigned_row==0)==(p==2),"unsigned control distinguishes characteristic two");
            out<<"{\"record\":\"conditioning_control\",\"case\":\""<<key
               <<"\",\"x\":0,\"y\":3,\"joint\":"<<actual
               <<",\"product_of_means\":"<<factorized
               <<",\"unsigned_row_residual\":"<<unsigned_row<<",\"passed\":true}\n";

            Design point{3,3,p,true};
            key="injection_F"+std::to_string(p);
            write_design(out,point,key);
            count=check(out,point,key);
            need(count==57,"complete 3-by-3 constraint count");
            for(int x=0;x<point.variables();++x)
                for(int y=0;y<point.variables();++y)
                    need(point.second(x,y)==point.first(x)*point.first(y),
                         "satisfiable injection has factorized moments");
            total+=count;++cases;
        }
        need(total==453&&cases==6,"complete run count");
        out<<"{\"record\":\"summary\",\"field_cases\":6,\"constraint_checks\":453,"
             "\"nonpoint_controls\":3,\"injection_controls\":3,\"passed\":true}\n";
        need(bool(out),"output write");
        std::cout<<"Six exact moment systems and 453 degree-two constraints passed.\n";
    }catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n';return 1;
    }
}
