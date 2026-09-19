#!/usr/bin/env python3
"""Integrate reviewed, disjoint worker proposals; never replace original claim text."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,REGISTRY
from claim_reviews import claim_digest,make_review,Evidence
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
paths=[ROOT/'research/results'/name/'patch.json' for name in ('parallel_index_classify_360_520','parallel_index_classify_520_680','parallel_index_classify_680_end')]
data=load();claims={c['id']:c for c in data['claims']};evidence=Evidence();seen=set();manifest=[];applied=[]
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
for path in paths:
 raw=path.read_bytes();patch=json.loads(raw);manifest.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'baseline':patch.get('baseline_revision',patch.get('baseline'))})
 for topic in patch.get('topic_definitions',patch.get('proposed_topic_definitions',[])):
  old=next((t for t in data['topic_definitions'] if t['id']==topic['id']),None)
  if old:assert old==topic,(topic['id'],'conflicting topic definition')
  else:data['topic_definitions'].append(topic)
 for row in patch['claims']:
  label=row['id'];assert label not in seen,('overlapping classification proposal',label);seen.add(label)
  c=claims[label];expected=row.get('baseline_claim_sha256',row.get('claim_sha256'))
  assert expected==claim_digest(c),(label,'source text changed')
  values=row.get('fields',row.get('values'));assert set(values)=={'mathematical_status','topics','significance'}
  for field,value in values.items():
   assert field not in c['reviews'],(label,field,'would overwrite existing reviewed seed')
   rv=row['reviews'][field];targets=rv.get('evidence_targets') or [e['target'] for e in rv.get('evidence',[])]
   assert targets,(label,field,'missing source evidence')
   for item in rv.get('evidence',[]):assert evidence.sha256(item['target'])==item['sha256'],(label,'stale worker evidence')
   c[field]=value
   c['reviews'][field]=make_review(data,c,field,targets,revision=revision,date=rv.get('date',patch.get('date','2026-09-19')),
    reviewer=rv.get('reviewer',patch.get('reviewer','Codex parallel classification worker')),state=rv['state'],
    note=rv['note']+' Integrated after source-digest/evidence validation; original text and other fields preserved.',next_action=rv.get('next_action'),evidence=evidence)
  applied.append(label)
 assert path.read_bytes()==raw,('worker patch changed during integration',str(path))
validate(data);write_json(REGISTRY,data);write_json(args.out,{'base_revision':revision,'inputs':manifest,'claims_applied':applied,'count':len(applied),'scope':'Field-level worker integration; original claim fields, formalization, relationships and reviewed seeds retained.'})
print(f'Integrated {len(applied)} claims / {len(applied)*3} field dispositions from three disjoint workers.')
