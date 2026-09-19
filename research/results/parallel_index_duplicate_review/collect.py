import argparse,functools,importlib.util,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,write_json
spec=importlib.util.spec_from_file_location('deps',R/'tools/claim-dependencies.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.notebook_parser=functools.lru_cache(maxsize=1)(d.notebook_parser)
x=load();base=Path(__file__).parent;c=json.loads((base/'candidates.json').read_text());ids=sorted(set(q[k] for q in c['candidates'] for k in ['left','right']))
p=[d.metadata_packet(x,id,limit=3,width=900) for id in ids];write_json(base/'packets.json',{'packets':p})
for q in p:
 print(q['id'])
 for t in q['passages']:
  print(t['target'].split('#')[-1],':',' | '.join(e['text'][:260] for e in t['excerpts'][:1]))
