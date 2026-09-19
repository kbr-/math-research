import sys,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load
s=importlib.util.spec_from_file_location('dep',R/'tools/claim-dependencies.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
book=d.notebook_parser((R/'notebook.html').read_text());d.notebook_parser=lambda text:book
x=load();packets=[d.metadata_packet(x,c['id'],limit=2,width=500) for c in x['claims'][680:]]
(Path(__file__).parent/'packets.json').write_text(json.dumps(packets,indent=2,ensure_ascii=False)+'\n')
for i,p in enumerate(packets,680):
 print(i,p['id']);print(p['assessment']);print(p['summary'])
 for passage in p['passages'][:1]:
  for e in passage['excerpts'][:1]:print(e['text'])
