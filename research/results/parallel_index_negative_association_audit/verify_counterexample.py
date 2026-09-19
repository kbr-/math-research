import json
from fractions import Fraction
from pathlib import Path
rows=[{'bijection':[1,2],'probability':'1/2','X11':1,'X22':1},{'bijection':[2,1],'probability':'1/2','X11':0,'X22':0}]
a=b=Fraction(1,2);both=none=Fraction(1,2)
assert both>a*b and none>(1-a)*(1-b)
m=4;s=t=2;intersection=0
joint=Fraction(s*t-intersection,m*(m-1));cov=joint-Fraction(s*t,m*m)
assert joint==Fraction(1,3) and cov==Fraction(1,12)
out={'two_by_two_outcomes':rows,'joint':'1/2','product_of_marginals':'1/4','avoidance':'1/2','strict_positive_covariance':'1/4','four_by_four_disjoint_two_row_sets_joint':str(joint),'four_by_four_covariance':str(cov),'exponential_bound_refutation':'Avoidance 1/2 > exp(-1), since e > 1+1 = 2. Exact symbolic argument; no floating-point estimate.','scope':'Checks the elementary premise/generic-lemma counterexamples, not the dense-label theorem under its full thresholds.'}
p=Path(__file__).parent/'counterexample.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
