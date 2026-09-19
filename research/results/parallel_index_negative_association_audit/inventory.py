#!/usr/bin/env python3
import hashlib,html,importlib.util,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('d',R/'tools/claim-dependencies.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
t=(R/'notebook.html').read_text();book=d.notebook_parser(t);claims=json.loads((R/'research/claims/index.json').read_text())['claims'];byanchor={}
for c in claims:
 for a in re.findall(r'https://[^)]+/#([^ )]+)',c['record']):byanchor.setdefault(a,[]).append(c['id'])
records=[]
for match in re.finditer(r'<p\b[^>]*>.*?</p>',t,re.S):
 raw=match.group()
 if not re.search(r'negative(?:ly)? associa|Joag.Dev|Proschan',raw,re.I):continue
 pos=match.start(); prior=[n for n in book.nodes if n.get('anchor') and n['start']<=pos]
 article=next((n['anchor'] for n in reversed(prior) if n['tag']=='article'),'')
 heading=next((n['anchor'] for n in reversed(prior) if n['tag'].startswith('h')),'')
 records.append({'line':t.count('\n',0,pos)+1,'article':article,'anchor':heading,'claim_ids':byanchor.get(heading,[]),'text':d.strip_markup(raw),'raw_html':raw})
out={'notebook_sha256':hashlib.sha256(t.encode()).hexdigest(),'search':'negative/negatively associated/association or Joag-Dev/Proschan, all notebook paragraphs','occurrences':records,'scope':'Text-use inventory, not proof that all usages are invalid. Uniform-subset membership indicators differ from full bijection matrix indicators.'}
P=Path(__file__).parent;(P/'direct-use-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
for r in records:print(r['line'],r['anchor'],','.join(r['claim_ids']),r['text'][:110])
for a in ['unary-reader-setup','dense-labels-satisfied','pinned-class-reduction']:
 raw=book.excerpt(a);(P/(a+'.html')).write_text(raw)
print('Paragraphs:',len(records))
