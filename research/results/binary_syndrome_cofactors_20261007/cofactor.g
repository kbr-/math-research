# Twisted, satisfiable F4 character quotient U1=omega U2, with an independent spectator.
# Nine characters; three code vectors. Raw two-error span rank6 excludes the code;
# adding one permitted degree-one cofactor gives rank9 and returns every codeword.
# Heterogeneous budgets: a1=(1+U1), cofactors span{1,U2}; a2=V2, constants only.
F:=GF(4);; o:=One(F);; z:=Zero(F);; omega:=Z(4);;
bit:=function(b) if b then return 1; else return 0; fi; end;;
labels:=Tuples([0,1,2],2);;
if Length(labels)<>9 then Error("Sizing guard"); fi;
shift:=function(b)
 return List(labels,a->List(labels,c->o*bit(c=List([1,2],i->(a[i]+b[i]) mod 3))));
end;;
I:=IdentityMat(9,F);; U:=shift([1,0]);; V:=shift([2,0]);;
Uone:=omega*U;;
code:=List([0,1,2],j->List(labels,a->o*bit(a=[0,j])));;
aone:=I+Uone;; atwo:=V;;
raw:=Concatenation(code*aone,code*atwo);;
closed:=Concatenation(code*aone,code*U*aone,code*atwo);;
rawsyn:=[[o,omega,z],[z,z,o]];;
closedsyn:=[[o,omega,z],[z,o,omega],[z,z,o]];;
if RankMat(raw)<>3*RankMat(rawsyn) or RankMat(closed)<>3*RankMat(closedsyn)
 or RankMat(raw)<>6 or RankMat(Concatenation(raw,code))<>9 or RankMat(closed)<>9
 then Error("Factorization or target test"); fi;
if (I+omega*U)*aone+omega^2*atwo<>I then Error("Degree-two return identity"); fi;
Print("raw_syndrome_rank=",RankMat(rawsyn)," raw_code_rank=",RankMat(raw),
 " with_target_rank=",RankMat(Concatenation(raw,code)),"\n");
Print("closed_syndrome_rank=",RankMat(closedsyn)," closed_code_rank=",RankMat(closed),"\n");
Print("PASS: twisted phase, heterogeneous cofactor budgets, tensor factorization and target return.\n");
QUIT;
