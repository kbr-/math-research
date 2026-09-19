import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'))
from claim_registry import load,validate,write_json
P=Path(__file__).parent;x=load();edges={e['id']:e for e in x['relationships']}
for e in json.loads((P/'relationship-proposals.json').read_text())['relationships']:edges.setdefault(e['id'],e)
x['relationships']=list(edges.values());validate(x)
t=json.loads((P/'topics.json').read_text());assert t['claim_count']==866 and not t['unclassified'];assert sum(z['count'] for z in t['topics'])>=866
v=(P/'resolution-parities.md').read_text();assert v.startswith('> Generated') and '| ID | Summary |' in v and 'thm:publication-Res-parity-bit-PHP' in v
c=json.loads((P/'candidate-decisions.json').read_text());assert c['reviewed_pairs']==22 and c['remaining_pairs']==0 and all(not q['merged'] for q in c['decisions'])
e=json.loads((P/'explicit-decisions.json').read_text());assert e['reviewed_records']==44 and e['remaining_records']==0
write_json(P/'validation.json',{'valid':True,'candidate_pairs_reviewed':22,'explicit_assessments_reviewed':44,'topic_claim_count':866,'topics':len(t['topics']),'unclassified':0,'representative_view_contains_publication_theorem':True,'scope':'Schema validation of proposal union and focused derived-view acceptance. No semantic equivalence certified by the validator.'})
print('22 candidate decisions,44 explicit assessment dispositions, topic map and representative view passed focused acceptance checks.')
