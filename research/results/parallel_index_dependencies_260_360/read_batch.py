import sys,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
sp=importlib.util.spec_from_file_location('deps',R/'tools/claim-dependencies.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
d=json.loads((R/'research/claims/index.json').read_text())
lo,hi=map(int,sys.argv[1:3]);rows=[]
scan=json.loads((R/'research/results/index_dependency_review_20260919/candidates.json').read_text())
for i,c in enumerate(d['claims'][lo:hi],lo):
 p=m.metadata_packet(d,c['id'],limit=8,width=950)
 candidates=[x for x in scan['candidates'] if x['source']==c['id']]
 rows.append({'position':i,'packet':p,'candidates':candidates})
 print('\nPOSITION',i,m.packet_text(p))
 for x in candidates:print('CANDIDATE',x['method'],x['targets'],[(o.get('context') or o.get('text')) for o in x['occurrences']])
(Path(__file__).parent/f'packets-{lo}-{hi}.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
