import sys,json,importlib.util,re,html
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
s=importlib.util.spec_from_file_location('d',R/'tools/claim-dependencies.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=json.load(open(R/'research/claims/index.json'));text=(R/'notebook.html').read_text();book=m.notebook_parser(text)
lo,hi=map(int,sys.argv[1:3])
for i,c in enumerate(d['claims'][lo:hi],lo):
 print('\n###',i,c['id'])
 anchors=re.findall(r'https://[^)]+/#([^ )]+)',c['record'])
 for a in anchors:
  try: excerpt=m.source_excerpt(book,text,a)[0]
  except Exception as e: print(e);continue

  blocks=re.findall(r'<p\b[^>]*>.*?</p>',excerpt,re.S)
  print(a)
  for b in blocks:
   t=m.strip_markup(b)
   if re.search(r'Route assessment|Next bounded|Process assessment|Through final|verification report|reproduction|All checks passed',t,re.I):continue
   print(t)
