import json,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import validate,check_targets
from claim_reviews import Evidence,claim_digest
HERE=Path(__file__).parent
for lo in range(260,360,10):
 subprocess.run([sys.executable,str(HERE/'build_patch.py'),str(lo),str(lo+10)],check=True)
d=json.loads((R/'research/claims/index.json').read_text());claims={c['id']:c for c in d['claims']};evidence=Evidence();reviews=[];edges=[]
for lo in range(260,360,10):
 p=json.loads((HERE/f'patch-{lo}-{lo+10}.json').read_text());reviews+=p['reviews'];edges+=p['relationships']
for r in reviews:
 assert claim_digest(claims[r['id']])==r['claim_sha256'],r['id']
 for e in r['evidence']:assert evidence.sha256(e['target'])==e['sha256'],e['target']
assert len(reviews)==len({r['id'] for r in reviews})==100
assert len(edges)==len({e['id'] for e in edges})
old={e['id']:e for e in d['relationships']}
conflicts=[e['id'] for e in edges if e['id'] in old and old[e['id']]!=e]
d['relationships'] += [e for e in edges if e['id'] not in old]
validate(d)
target_report=check_targets(d)
assert target_report['passed'],target_report['errors']
report={'reviewed_inventories':len(reviews),'proposed_relationships':len(edges),'existing_edge_scope_comparisons_required':conflicts,'new_edge_count':sum(e['id'] not in old for e in edges),'source_hashes_checked':True,'schema_and_targets':target_report,'scope':'Proposal-only validation; existing edge scope differences require coordinator reconciliation, not automatic replacement.'}
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='schema_and_targets'},indent=2))
