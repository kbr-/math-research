import json,sys,importlib.util,re
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('dep',R/'tools/claim-dependencies.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
t=(R/'notebook.html').read_text();book=d.notebook_parser(t);p=json.loads((R/'research/results/parallel_index_classify_680_end/packets.json').read_text());out=[]
for i in range(741,780):
 texts=[]
 for region in p[i-680]['passages']:
  anchor=region['target'].split('#')[-1];html=book.excerpt(anchor)
  for match in re.findall(r'<p\b[^>]*>.*?</p>',html,re.S):
   text=re.sub(r'\s+',' ',d.html.unescape(d.strip_markup(match)))
   if 'negative association' in text.lower() or 'negatively associated' in text.lower():texts.append({'anchor':anchor,'text':text})
 out.append({'position':i,'id':p[i-680]['id'],'negative_association_passages':texts})
 print(i,p[i-680]['id'])
 for a in texts:print(a['anchor'],a['text'][:650])
(Path(__file__).parent/'remaining-source-audit.json').write_text(json.dumps(out,indent=2)+'\n')
