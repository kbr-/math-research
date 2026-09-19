import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate
x=load();edges={e['id']:e for e in x['relationships']};count=0
for p in Path(__file__).parent.glob('patch_*.json'):
 d=json.loads(p.read_text())
 for e in d['relationships']:
  count+=1
  if e['id'] not in edges:edges[e['id']]=e
x['relationships']=list(edges.values());validate(x)
(Path(__file__).parent/'validation.json').write_text(json.dumps({'schema_valid':True,'edge_proposals':count,'scope':'Structural validation of proposal union in memory; root refreshes endpoint reviews and reconciles existing edges.'},indent=2)+'\n')
print(count,'edge proposals pass structural validation')
