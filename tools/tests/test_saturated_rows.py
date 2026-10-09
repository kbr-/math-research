import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
GP = shutil.which('gp')


@unittest.skipUnless(GP, 'PARI/GP is required for this mathematical kernel')
class SaturatedRowsTest(unittest.TestCase):
    def run_gp(self, body):
        program = '\n'.join([
            f'read({json.dumps(str(ROOT / "tools/saturated_rows.gp"))});',
            "ep='ep;b='b;",
            'check(c,s)=if(!c,error(s));',
            'test_run()={', body, '};',
            'iferr(test_run(),E,print(E);quit(1));',
            'print("COMPLETE");quit;'
        ])
        result = subprocess.run([GP, '-q', '-f'], input=program, text=True,
                                capture_output=True, timeout=4)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), 'COMPLETE', result.stdout + result.stderr)
        self.assertNotIn('***', result.stderr)

    def test_saturated_module_poles_and_characteristic_audit(self):
        self.run_gp('''
          my(A=[1,1;1,1+ep],S=sat_rows(A,ep));
          check(S[1]==[1,1;0,1] && S[2]==[0,1],"primitive rows and exact pole bound");
          my(B=[ep,ep^2;ep,ep^2+ep^5],Q=sat_rows(B,ep));
          check(Q[1]==matid(2) && Q[2]==[1,5],"left-transformation poles accumulate");
          my(U=B);
          for(j=1,#Q[3],my(op=Q[3][j]);if(type(op[2])=="t_INT",U[op[1],]*=ep^op[2],my(c=op[2]);check(c[op[1]]==1,"invertible row replacement");U[op[1],]=sum(i=1,2,c[i]*U[i,])));
          check(matrix(2,2,i,j,polcoef(U[i,j],0,ep))==Q[1],"full certificate replay");
          check(sat_rows(A,ep,3)[1]==Mod(1,3)*S[1],"finite-field source");
          check(sat_rows([b/53,0;0,ep*(b+1)/7],ep)[6]==371,"denominator coefficient contents");
          check(sat_rows([13*b,0;0,1],ep)[6]==13,"rank-minor numerator content");
        ''')

    def test_original_minor_removes_spurious_prime_but_keeps_bad_stratum(self):
        self.run_gp('''
          my(A=[5,0,ep;0,1,0;1,1,0],S=sat_rows(A,ep),G=sat_specialization(A,ep,S));
          check(S[6]%5==0 && G[1]==1 && G[2]==matid(3),"intermediate five is not an intrinsic exclusion");
          check(G[3]==1 && G[4]==1,"original minor valuation and inverse pole bound");
          my(S5=sat_rows(A,ep,5));
          check(matrank(S5[1])==3 && sat_replay(Mod(1,5)*A,ep,S5)[1]==S5[1],"direct characteristic-five replay");
          my(B=[5,0;0,1]);
          check(sat_specialization(B,ep,sat_rows(B,ep))[1]%5==0,"genuine vanishing leading minor remains excluded");
          my(C=Mat([b,ep]),K=sat_specialization(C,ep,sat_rows(C,ep)));
          check(K[1]==1 && K[2]==Mat([1,0]),"generic parameter stratum");
          check(sat_rows(subst(C,b,0),ep)[1]==Mat([0,1]),"vanishing parameter minor can change saturation");
          my(D=[1,1;1,1+ep],T=sat_rows(D,ep),caught=0);T[3]=[];
          iferr(sat_specialization(D,ep,T),E,caught=1);
          check(caught,"incomplete row certificate rejected");
        ''')

    def test_invalid_or_dependent_input_fails_closed(self):
        self.run_gp('''
          my(caught=0);
          iferr(sat_rows([1,1;2,2],ep),E,caught++);
          iferr(sat_rows([1/ep,0;0,1],ep),E,caught++);
          iferr(sat_rows([1,0;0,1],ep,9),E,caught++);
          check(caught==3,"all invalid inputs rejected");
        ''')
