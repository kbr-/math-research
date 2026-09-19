import json,re,sys,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'));from claim_registry import load,references,write_json
s=importlib.util.spec_from_file_location('d',R/'tools/claim-dependencies.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
x=load();text=(R/'notebook.html').read_text();book=d.notebook_parser(text);owners={}
for c in x['claims']:
 for r in references(c):
  if '#' in r['target']:owners.setdefault(r['target'].split('#')[-1],[]).append(c['id'])
rows=[]
for c in x['claims']:
 if not re.search(r'rediscover|refin',c['assessment'],re.I):continue
 row={'id':c['id'],'assessment':c['assessment'],'source_evidence':[]};print(c['id'])
 for r in references(c):
  if 'math-research/#' not in r['target']:continue
  ex=d.source_excerpt(book,text,r['target'].split('#')[-1])[0];links=[]
  for target,label in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',ex,re.S):
   ids=owners.get(target.split('#')[-1],[])
   if ids:links.append({'label':d.strip_markup(label),'targets':ids,'locator':target})
  selected=[d.strip_markup(q) for q in re.findall(r'<p\b[^>]*>.*?</p>',ex,re.S) if re.search(r'rediscover|refin|earlier|previous|same proof',q,re.I)]
  row['source_evidence'].append({'target':r['target'],'links':links,'passages':selected})
  print(' links:',[(l['label'],l['targets']) for l in links])
  if selected:print(' note:',selected[0][:300])
 rows.append(row)
write_json(Path(__file__).parent/'explicit-refinement-inventory.json',{'records':rows,'scope':'Lexical assessment census, evidence extraction only; classifications supplied separately.'})
