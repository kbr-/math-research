#!/usr/bin/env python3
"""Extract an archived degree-three fall witness; does not rerun elimination."""
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():p.error('output exists')
 base=ROOT/'research/results/hw_unary_design_20260918_228';runs={};sources=[]
 for degree in (1,2,3):
  path=base/f'ns_l8_d{degree}_h1_label_seed1.jsonl';raw=path.read_bytes();data=[json.loads(line) for line in raw.splitlines()]
  runs[degree]={'header':next(x for x in data if 'rank_I' in x),'pivots':{x['clause']:x['pivots_by_leading_degree'] for x in data if 'clause' in x and 'pivots_by_leading_degree' in x},'rows':{x['clause']:x for x in data if 'dim_V_mod_I' in x}}
  sources.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
 out=[];N=8;v=N*N-1;k=(N+1)*(2*N*N-3*N+2)//2
 for M in (14,15):
  g1=sum(runs[1]['pivots'][M]);g2=runs[2]['header']['rank_I']+runs[2]['rows'][M]['dim_V_mod_I'];low2=sum(runs[2]['pivots'][M][:2]);low3=sum(runs[3]['pivots'][M][:3]);d=v-M
  qrank=1+d+math.comb(d,2)-runs[2]['rows'][M]['quotient_left']
  assert g1==9+M and low2==g1 and qrank==k
  out.append({'clauses':M,'v':v,'d':d,'dim_K':k,'dim_G1':g1,'dim_G2':g2,'dim_G2_cap_degree1':low2,'dim_G3_cap_degree2':low3,'quadratic_image_rank':qrank,'quadratic_faithful':True,'degree3_fall_dimension':low3-g2,'one_in_G3':runs[3]['rows'][M]['one_in_span']})
 assert out[0]['degree3_fall_dimension']==0 and out[1]['degree3_fall_dimension']==179
 report={'scope':'Reuses archived exact ranks for eight holes, label forms, seed 1. No fresh elimination and no extracted polynomial certificate.','sources':sources,'witnesses':out}
 a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
