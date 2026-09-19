import sys,json,importlib.util,re,html
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import references
s=importlib.util.spec_from_file_location('d',R/'tools/claim-dependencies.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=json.load(open(R/'research/claims/index.json'));text=(R/'notebook.html').read_text();book=m.notebook_parser(text);owners={}
for c in d['claims']:
 for r in references(c):
  if '#' in r['target']:owners.setdefault(r['target'].split('#')[-1],[]).append(c['id'])
lo,hi=map(int,sys.argv[1:3])
for i,c in enumerate(d['claims'][lo:hi],lo):
 print('\n',i,c['id'])
 for ref in references(c):
  if 'math-research/#' not in ref['target']:continue
  a=ref['target'].split('#')[-1];ex=m.source_excerpt(book,text,a)[0]
  for target,label in re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',ex,re.S):
   an=target.split('#')[-1];print(m.strip_markup(label),'->',','.join(owners.get(an,[])) or target)
