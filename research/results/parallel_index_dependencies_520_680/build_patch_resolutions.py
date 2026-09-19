import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'tools'))
from claim_reviews import claim_digest
x=json.loads((root/'research/claims/index.json').read_text());cs={c['id']:c for c in x['claims']};rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();web='https://kbr.is-a.dev/math-research/#';rows=[];edges=[]
def add(i,anchors,relations,note):
 c=x['claims'][i];ev=[web+a for a in anchors.split()];rows.append({'id':c['id'],'position':i,'claim_sha256':claim_digest(c),'state':'reviewed','evidence':ev,'note':note,'next_action':None})
 for typ,target,scope in relations:
  assert target in cs,target
  edges.append({'id':c['id']+'::'+typ+'::'+target,'source':{'namespace':'current','id':c['id'],'locator':None},'target':{'namespace':'current','id':target,'locator':None},'type':typ,'scope':scope,'evidence':ev,'review_status':'reviewed','review':{'revision':rev,'date':'2026-09-19','reviewer':'Codex parallel dependency reviewer','note':'Owning proof/application passage reviewed, including implicit intra-entry references; no new mathematical or kernel audit.'}})
def rel(kind,index,scope):return (kind,x['claims'][index]['id'] if isinstance(index,int) else index,scope)
def put(i,relations,note):
 c=x['claims'][i];import re
 anchors=re.findall(r'https://[^)]+/#([^ )]+)',c['record']);add(i,' '.join(anchors),relations,note)
put(532,[rel('depends_on','ex:cube-dual-complete-marginal-checks','Reuses the explicit residual degree-two design concentrated at q and three pair cells (q,a),(b,a),(b,q).'),rel('depends_on','ex:odd-prime-affine-complete-checks','Reuses signed residual path coefficients (1,-1,1) in the F3 extension.'),rel('applies',528,'Tests signed multi-axis residual detector.'),rel('applies',529,'Checks separated target-cube and multiplier-edge accounting.')], 'Resolved by exact earlier finite passages and check_cube_dual_design.cpp lines69–93. This is explicit finite residual data, not an invocation of Razborov lower-bound existence for the fixture.')
rows[-1]['evidence']+=['https://kbr.is-a.dev/math-research/#cube-dual-complete-marginal-checks','https://kbr.is-a.dev/math-research/#odd-prime-affine-complete-checks','../research/tools/check_cube_dual_design.cpp']
put(555,[rel('depends_on','thm:all-prime-affine-family-exclusion','Reuses its ordinary affine-coordinate literal ideal-witness argument f=sum a_i g_i with degree(a_i)<=k-1; domain multiplier dimension is replaced here.')], 'Resolved by the all-prime source literal-coordinate paragraph, whose field-independent proof is the earlier ordinary-restriction audit: monomials vanishing on the coordinate zero flat each contain a constrained coordinate. The union-bound and changed binomial dimension estimate are proved locally.')
rows[-1]['evidence']+=['https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit']
put(610,[rel('depends_on',608,'Supplies actual original input span and affine intersection.'),rel('depends_on',555,'Supplies high-affine ordinary restriction estimate.'),rel('depends_on','audit:ordinary-restriction-affine-family','Supplies exact ordinary affine-coordinate literal ideal representation in the binary case.')], 'Resolved the unnamed affine witness source to the explicit ordinary-restriction audit. Pulling back to quadratic original inputs keeps coefficient degree but may cost k+1 in NS; the separate low-rank basis-prefix map is proved directly.')
rows[-1]['evidence']+=['https://kbr.is-a.dev/math-research/#ordinary-restriction-affine-family-audit']
out={'schema_version':1,'base_revision':rev,'supersedes_pending_positions':[532,555,610],'claims':rows,'relationships':edges,'scope':'Replaces the three provisional pending inventory dispositions after targeted provenance resolution. Apply after other worker patches; retain all prior reviewed edges.'}
(root/'research/results/parallel_index_dependencies_520_680/patch_resolutions.json').write_text(json.dumps(out,indent=2)+'\n');print('3 pending inventories resolved')
