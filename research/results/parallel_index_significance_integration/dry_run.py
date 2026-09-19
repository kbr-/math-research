#!/usr/bin/env python3
"""Normalize the nine reviewed significance proposals; never write canonical state."""
import argparse,copy,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,validate,write_json,local_target
from claim_reviews import claim_digest,digest,Evidence,make_review
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
source_paths=[ROOT/'research/results/parallel_index_significance_normalizers/proposals.json',ROOT/'research/results/parallel_index_significance_calculi/patch.json',ROOT/'research/results/parallel_index_significance_query_obstructions/proposals.json']
data=load();before=copy.deepcopy(data);claims={c['id']:c for c in data['claims']};ev=Evidence();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();rows=[];checks=[];inputs=[];baseline_books={}
spec=importlib.util.spec_from_file_location('excerpts',ROOT/'tools/notebook-excerpt.py');ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
for path in source_paths:
 raw=path.read_bytes();blob=json.loads(raw);items=blob if isinstance(blob,list) else blob['claims'];base=None if isinstance(blob,list) else blob.get('base_revision',blob.get('baseline_revision'))
 inputs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'records':len(items)})
 for row in items:
  c=claims[row['id']];claimed=row.get('baseline_claim_sha256',row.get('source_fields_sha256',row.get('claim_sha256')))
  assert claimed==claim_digest(c),('source text changed',c['id'])
  value=row.get('fields',{}).get('significance',row.get('significance'));review=row.get('reviews',{}).get('significance',row.get('review'));assert value is not None and review['state']=='reviewed'
  assert value['novelty'] in {'unknown','candidate'}
  assert value['next_action'],'Residual publication uncertainty needs specific next action'
  base=review.get('revision',base)
  for item in review.get('evidence',[]):
   actual=ev.sha256(item['target']);assert actual==item['sha256'],('stale evidence',c['id'],item['target']);checks.append({'claim':c['id'],'target':item['target'],'sha256':actual,'check':'supplied evidence hash matches'})
  targets=review.get('evidence_targets',[e['target'] for e in review.get('evidence',[])])
  # Calculi proposals have locator lists but not source hashes: compare notebook
  # slices to their immutable declared baseline and freeze all evidence now.
  if not review.get('evidence'):
   if base not in baseline_books:
    old=subprocess.check_output(['git','show',base+':notebook.html'],cwd=ROOT,text=True);baseline_books[base]=ex.Notebook(old)
   for target in targets:
    local=local_target(target,ROOT)
    if local and local[0].name=='notebook.html' and local[1]:
     prior=hashlib.sha256(baseline_books[base].excerpt(local[1]).encode()).hexdigest();actual=ev.sha256(target);assert prior==actual,('baseline notebook changed',target)
     checks.append({'claim':c['id'],'target':target,'sha256':actual,'check':'immutable baseline excerpt matches'})
    else:checks.append({'claim':c['id'],'target':target,'sha256':ev.sha256(target),'check':'audit report fingerprint recorded at integration'})
  c['significance']=copy.deepcopy(value)
  c['reviews']['significance']=make_review(data,c,'significance',targets,revision=head,date='2026-09-19',reviewer='Codex significance integration review',state='reviewed',next_action=None,note=review['note']+' Integration verified source fingerprints and preserved every unrelated claim field.',evidence=ev)
  rows.append({'id':c['id'],'baseline_claim_sha256':claimed,'fields':{'significance':copy.deepcopy(c['significance'])},'reviews':{'significance':copy.deepcopy(c['reviews']['significance'])},'source_proposal':str(path.relative_to(ROOT))})
assert len(rows)==9 and len({r['id'] for r in rows})==9
validate(data)
# Erase precisely the allowed changes; equality proves all other metadata/text/edges survive.
restored=copy.deepcopy(data);original={c['id']:c for c in before['claims']}
for c in restored['claims']:
 if c['id'] in {r['id'] for r in rows}:
  c['significance']=original[c['id']]['significance']
  if 'significance' in original[c['id']]['reviews']:c['reviews']['significance']=original[c['id']]['reviews']['significance']
  else:c['reviews'].pop('significance',None)
assert restored==before
write_json(a.out,{'schema_version':1,'base_revision':head,'baseline_registry_sha256':digest(before),'source_proposals':inputs,'claims':rows,'scope':'Nine significance-only fields/reviews; unknown novelty remains a completed bounded-audit disposition, not certified originality. No canonical edits.'})
write_json(a.out.parent/'report.json',{'schema_valid':True,'claims':9,'field_reviews':9,'unrelated_state_identical':True,'canonical_unchanged':True,'source_checks':checks,'novelty_counts':{'unknown':sum(r['fields']['significance']['novelty']=='unknown' for r in rows),'candidate':sum(r['fields']['significance']['novelty']=='candidate' for r in rows)},'scope':'Current source and supplied audit evidence hashes checked; two locator-only proposals compared to their immutable notebook baseline. No independent re-search or proof audit.'})
print('Nine reviewed significance proposals normalized; all source checks pass; unrelated state identical.')
