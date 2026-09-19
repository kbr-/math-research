#!/usr/bin/env python3
"""Real finalizer integration in isolated repos, before and after proposed patch."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
from propose_integration import ROOT,proposed_sources
BASELINE='4747534a8c0b68d3eeb7d4e8f199c9d355febd1f'

FIXTURE=r'''
import json,sys
sys.path.insert(0,'tools')
from claim_registry import import_markdown,upgrade,HEADER,render
from claim_reviews import FIELDS,Evidence,make_review,coverage
from pathlib import Path
root=Path.cwd();p=root/'research/claims/index.json'
if sys.argv[1]=='baseline':
 d=upgrade(import_markdown('# Index\n\n'+HEADER+'| `lem:fixture` | Fixture | Working proof | [Proof](../notebook.html#entry-fixture) |\n'))
 d['claims']=[];d['topic_definitions']=[{'id':'fixture','title':'Fixture','description':'Isolated test'}]
 (root/'notebook.html').write_text('<section id="research-record"></section>\n')
elif sys.argv[1]=='new':
 d=json.loads(p.read_text());c=upgrade(import_markdown('# Index\n\n'+HEADER+'| `lem:fixture` | Fixture | Working proof | [Proof](../notebook.html#entry-fixture) |\n'))['claims'][0]
 c.update(mathematical_status='working_proof',topics=['fixture'],formalization={'status':'not_started','scope':'Fixture only; no formalization assigned.','references':[],'artifacts':[]},significance={'category':'context','rationale':'Isolated software fixture.','novelty':'not_claimed','publication_status':'not_applicable','references':[],'next_action':None})
 d['claims']=[c]
 (root/'notebook.html').write_text('<section id="research-record">\n<article id="entry-fixture" data-kind="research" data-route="side-test" data-claims="lem:fixture">\n<p class="entry-meta">Status: working fixture.</p>\n<p>Mathematical statement unchanged.</p>\n<!-- TIMING fixture_turn -->\n</article>\n</section>\n')
 e=Evidence(root)
 for f in FIELDS:c['reviews'][f]=make_review(d,c,f,['https://kbr.is-a.dev/math-research/#entry-fixture'],revision='a'*40,date='2026-09-19',reviewer='Fixture',note='Inspected isolated fixture.',evidence=e)
else:
 d=json.loads(p.read_text());print(json.dumps(coverage(d,root)));raise SystemExit
p.write_text(json.dumps(d));(root/'research/CLAIM_INDEX.md').write_text(render(d))
'''
# Raw string above needs actual line separators in the small Markdown strings.
FIXTURE=FIXTURE.replace('\\\\n','\\n')
results=[]
with tempfile.TemporaryDirectory(prefix='claim-finalizer-regression-') as temp:
 for fixed in (False,True):
  root=Path(temp)/('fixed' if fixed else 'legacy');(root/'tools').mkdir(parents=True);(root/'research/claims').mkdir(parents=True)
  for file in (ROOT/'tools').glob('*.py'):shutil.copy2(file,root/'tools'/file.name)
  shutil.copy2(ROOT/'compute.sh',root/'compute.sh')
  for name in ('schema.json','schema-v1.json'):shutil.copy2(ROOT/'research/claims'/name,root/'research/claims'/name)
  if not fixed:
   for path in ('tools/claim_reviews.py','tools/finish-turn.py','research/claims/schema.json'):
    (root/path).write_text(subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT,text=True))
  (root/'fixture.py').write_text(FIXTURE)
  def run(args):
   x=subprocess.run(args,cwd=root,capture_output=True,text=True)
   if x.returncode:raise RuntimeError(str(args)+'\n'+x.stdout+'\n'+x.stderr)
   return x.stdout
  run([sys.executable,'fixture.py','baseline']);run(['git','init','-q']);run(['git','add','research','notebook.html'])
  run(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Baseline'])
  run([sys.executable,'fixture.py','new']);before=json.loads(run([sys.executable,'fixture.py','coverage']))
  run([sys.executable,'compute.sh','start','fixture_turn','--agent','Fixture','--model','Fixture model'])
  finish=run([sys.executable,'tools/finish-turn.py','fixture_turn'])
  after=json.loads(run([sys.executable,'fixture.py','coverage']))
  expected='reviewed' if fixed else 'stale'
  assert all(after['counts'][field]=={expected:1} for field in after['counts']),after['counts']
  # The old evidence hash itself is never rewritten by the real finalizer.
  data=json.loads((root/'research/claims/index.json').read_text())
  item=data['claims'][0]['reviews']['mathematical_status']['evidence'][0]
  results.append({'fixed':fixed,'before':before['counts'],'after':after['counts'],'evidence':item,'finalizer_stdout':finish})
  if fixed:
   text=(root/'notebook.html').read_text();(root/'notebook.html').write_text(text.replace('Status: working fixture.','Status: refuted fixture.'))
   changed=json.loads(run([sys.executable,'fixture.py','coverage']))
   assert all(v=={'stale':1} for v in changed['counts'].values())
   results[-1]['status_change_after_finalization']=changed['counts']
   (root/'notebook.html').write_text(text.replace('Mathematical statement unchanged.','Mathematical statement changed.'))
   changed=json.loads(run([sys.executable,'fixture.py','coverage']))
   assert all(v=={'stale':1} for v in changed['counts'].values())
   results[-1]['mathematics_change_after_finalization']=changed['counts']
p=Path(__file__).parent/'reproduction.json';p.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
