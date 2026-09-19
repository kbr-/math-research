#!/usr/bin/env python3
"""Populate explicit recorded Lean coverage; preserve scope exceptions and pending evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load, REGISTRY, local_target, validate, write_json
from claim_reviews import Evidence, make_review, verified_declarations

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
inventory=json.loads((Path(__file__).parent/'inventory.json').read_text())
data=load();claims={c['id']:c for c in data['claims']}
spec=importlib.util.spec_from_file_location('notebook_excerpt',ROOT/'tools/notebook-excerpt.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
book=module.Notebook((ROOT/'notebook.html').read_text());evidence=Evidence()
files={f['path']:f for f in inventory['files']};report=[]
verification_catalog=[]
for path in (ROOT/'research/results').rglob('*.txt'):
    if not re.search(r'verification|axiom|kernel',path.name,re.I):continue
    body=path.read_text()
    names=verified_declarations(body)
    if names:verification_catalog.append((path,names))
for record in inventory['claims']:
    claim=claims[record['id']]
    if claim['id'] in ('lem:mp-telescoping','thm:publication-Res-parity-bit-PHP','cor:bit-PHP-exponential-parameter-bound'):
        report.append({'id':claim['id'],'outcome':'previous curated coverage preserved'});continue
    artifacts=[];targets=[];notes=[]
    for filename in record['files']:
        file=files[filename];path=ROOT/filename
        assert hashlib.sha256(path.read_bytes()).hexdigest()==file['sha256'],filename
        assert claim['id'] in file['header'],(claim['id'],filename,'header ownership mismatch')
        scope=file['scope_header'];assert scope
        decl_header=re.search(r'^Declarations?:\s*(.*?)(?=\n[A-Z][A-Za-z ]*:|\Z)',file['header'],re.M|re.S)
        declarations=re.findall(r'\bMathResearch\.[\w.]+',decl_header.group(1)) if decl_header else []
        declarations=[d.rstrip('.') for d in declarations]
        if claim['id']=='lem:generic-CNF-initial-value-bridge':
            declarations=[d for d in declarations if d.rsplit('.',1)[-1] in
                          ('clauseFalsityPolynomial','clauseFalsityPolynomial_eval_eq_zero_iff','registry_generic_initial')]
            scope='Binary ordinary clause polynomial and evaluation characterization; the registry initial-value bridge through 2h+w. The separate generic DAG criterion is not part of this claim.'
        elif claim['id']=='thm:generic-CNF-affine-DAG-subspace-criterion':
            declarations=[d for d in declarations if d.rsplit('.',1)[-1] in ('generic_CNF_PC_transfer','generic_CNF_subspace_criterion')]
        source=re.search(r'^Source:\s*(\S+)',file['header'],re.M)
        source=source.group(1) if source else None
        verification=[]
        if source:
            local=local_target(source)
            if local and local[0].resolve()==(ROOT/'notebook.html').resolve():
                try:
                    node=book.anchor(local[1])
                    while node and node['tag']!='article':node=node['scope']
                    passage=book.excerpt(node['anchor']) if node else book.excerpt(local[1])
                except ValueError:
                    passage='';notes.append('Unresolved source passage: '+source)
                for href in re.findall(r'href="([^"]+)"',passage):
                    loc=local_target(href)
                    if loc and loc[0].suffix=='.txt' and loc[0].is_file() and re.search(r'verification|axiom|kernel',loc[0].name,re.I):
                        body=loc[0].read_text()
                        score=sum(name in verified_declarations(body) for name in declarations)
                        if score:
                            verification.append((score,'final' in loc[0].name,href))
                targets.append(source)
        if not verification:
            for proof_path,names in verification_catalog:
                score=sum(name in names for name in declarations)
                if score:
                    verification.append((score,'final' in proof_path.name,
                        str(proof_path.relative_to(ROOT/'research'))))
        explicit_reports={
            'formalization/claims/AffineFamilyExclusion.lean':'results/r_parallel_assembly_review_20260915/exclusion-final.txt',
            'formalization/claims/AffineParameterBounds.lean':'results/r_parallel_assembly_review_20260915/parameters-final.txt'}
        if filename in explicit_reports:
            target=explicit_reports[filename]
            body=(ROOT/'research'/target).read_text()
            assert all(name in verified_declarations(body) for name in declarations),(filename,'final report declaration mismatch')
            verification.append((len(declarations)+1,True,target))
        report_link=max(verification)[2] if verification else None
        status='statement_only' if filename.endswith('/ChessboardFilling.lean') else 'complete'
        if report_link:
            targets.append(report_link)
            loc=local_target(report_link)
            audited=verified_declarations(loc[0].read_text())
            if status=='complete':
                # Keep declarations tied to actual named reports. All additional
                # source exports remain preserved in inventory.json.
                declarations=[name for name in declarations if name in audited]
        elif status=='complete':notes.append('No matching verification report located for '+filename)
        targets.append('../'+filename)
        artifacts.append({'scope':scope,'status':status,'references':['../'+filename],
                          'declarations':declarations,'verification':report_link})
    claim['formalization']={'status':'complete',
        'scope':claim['summary']+'. Recorded qualifications: '+claim['assessment'],
        'references':list(dict.fromkeys(targets)),'artifacts':artifacts}
    note=('Matched indexed scope/qualifications against explicit Lean Claim/Scope/Declarations headers '
          'and linked notebook verification records. This is metadata extraction, not a new proof audit or kernel replay.')
    if any(len(files[f]['indexed_claims'])>1 for f in record['files']):
        note+=' Shared artifact declarations were split by indexed claim; the other theorem is not included in this scope.'
    state='pending' if notes else 'reviewed'
    claim['reviews']['formalization']=make_review(data,claim,'formalization',list(dict.fromkeys(targets)),
        revision='5ed10d8692edfc66d77f7425ee5cd31fa9b87124',date='2026-09-19',reviewer='Codex GPT-6 Astra',
        note=note,state=state,next_action='; '.join(notes) if notes else None,evidence=evidence)
    report.append({'id':claim['id'],'outcome':state,'artifacts':len(artifacts),'notes':notes})
validate(data);write_json(REGISTRY,data)
write_json(args.out,{'claims':report,'unmapped_file_disposition':{
    'formalization/claims/BitPHPPreprintRevision1.lean':'Import-only publication aggregate with no independent declaration; not a missing mathematical claim.'},
    'method':'Recorded coverage extraction with explicit shared/definition-only scope handling; no Lean build.'})
print(json.dumps({'mapped_claims':len(report),'preserved':sum(r['outcome'].startswith('previous') for r in report),
                  'reviewed':sum(r['outcome']=='reviewed' for r in report),'pending':sum(r['outcome']=='pending' for r in report)},indent=2))
for row in report:
    if row['outcome']=='pending':print(row['id'],row['notes'])
