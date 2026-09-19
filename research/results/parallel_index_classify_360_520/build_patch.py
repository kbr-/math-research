#!/usr/bin/env python3
"""Build isolated field patch from reviewed per-claim specifications; no registry mutation."""
import argparse,copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load,write_json,validate
from claim_reviews import Evidence,make_review,claim_digest
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
data=load();packets=json.loads((Path(__file__).parent/'packets.json').read_text())['packets'];rev=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
groups={'F':['finite-certificates'],'S':['ens','substitution','degree-accounting'],'C':['ens','frege-simulation','degree-accounting'],'M':['matching-php','moment-designs','polynomial-calculus'],'A':['affine-linear-algebra','ens'],'D':['ens','moment-designs','nullstellensatz'],'B':['bit-php','polynomial-calculus','degree-accounting'],'N':['ens','nullstellensatz','degree-accounting'],'R':['affine-linear-algebra','polynomial-calculus','bit-php'],'W':['algebraic-branching-programs','ens','degree-accounting']}
topic={'id':'algebraic-branching-programs','title':'Algebraic branching programs','description':'Read-once oblivious algebraic branching programs, matrix representations and evaluation or coefficient cut-rank bounds.'}
if not any(t['id']==topic['id'] for t in data['topic_definitions']):data['topic_definitions'].append(topic)
finite={360,365,369,375,381,386,390,394,397,402,407,410,414,420,426,430,431,442,448,455,460,469,488,494,503,510,515}
context={376,447,454,464,465,474,479,480,493,504,511,516}
established={382,481,482,484,485,486,489,490,491,492}
rows=[];evidence=Evidence()
lines=(Path(__file__).parent/'specs.tsv').read_text().splitlines();assert len(lines)==160
for position,line,packet in zip(range(360,520),lines,packets):
 n,group,category,rationale=line.split(' ',3);assert int(n)==position
 c=copy.deepcopy(data['claims'][position]);assert c['id']==packet['id'] and c['summary']==packet['summary'] and c['assessment']==packet['assessment']
 targets=list(dict.fromkeys(p['target'] for p in packet['passages']));assert targets
 c['mathematical_status']='finite_check' if position in finite else 'context' if position in context else 'established' if position in established else 'working_proof'
 c['topics']=groups[group].copy()
 if category=='negative_result':c['topics'].append('method-obstructions')
 if position in range(480,489) or position==493:c['topics'].append('resolution-parities')
 if category=='independent_result':c['topics'].append('publication')
 c['significance']={'category':category,'rationale':rationale,'novelty':'unknown' if category=='independent_result' else 'not_claimed','publication_status':'candidate' if category=='independent_result' else 'not_applicable','references':targets,'next_action':None}
 action=None
 if category=='independent_result':
  action='Compare the exact rule conventions and encoding against primary lower-bound literature before assigning independent novelty; for the earlier binary corollary inherit the publication theorem audit rather than counting it separately.'
  c['significance']['next_action']=action
 reviews={}
 for field in ('mathematical_status','topics','significance'):
  reviews[field]=make_review(data,c,field,targets,revision=rev,date='2026-09-19',reviewer='Codex parallel index worker 360-520',note='Reviewed indexed scope and compact source evidence. '+rationale+' This is source-relative metadata, not a new proof or literature audit.',state='pending' if field=='significance' and action else 'reviewed',next_action=action if field=='significance' else None,evidence=evidence)
 rows.append({'position':position,'id':c['id'],'baseline_claim_sha256':claim_digest(c),'fields':{f:c[f] for f in reviews},'reviews':reviews,'evidence_targets':targets})
 data['claims'][position]=c
 c['reviews'].update(reviews)
validate(data)
write_json(a.out,{'schema_version':1,'baseline_revision':rev,'scope':'Isolated source-relative classification patch for positions [360,520); no canonical registry mutation, no formalization or relationship changes.','topic_definitions':[topic],'claims':rows,'counts':{'claims':160,'reviewed_status':160,'reviewed_topics':160,'reviewed_significance':158,'pending_significance':2}})
print('Patch: 160 claims; 158 reviewed significance, 2 pending literature-audit dispositions; local schema validated.')
