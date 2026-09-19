#!/usr/bin/env python3
"""Inventory existing formalization mappings; this does not certify proof scope."""
import argparse
import hashlib
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from claim_registry import load, references, local_target, write_json

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
data=load();mapped={};claim_rows=[]
for claim in data['claims']:
    paths=set()
    for reference in references(claim):
        local=local_target(reference['target'])
        if local and local[0].suffix=='.lean':
            paths.add(local[0].resolve())
    if paths:
        claim_rows.append({'id':claim['id'],'summary':claim['summary'],'assessment':claim['assessment'],
                           'files':[str(p.relative_to(ROOT)) for p in sorted(paths)]})
    for path in paths: mapped.setdefault(path,[]).append(claim['id'])
files=[]
for directory in ('claims','third-party-claims'):
    for path in sorted((ROOT/'formalization'/directory).glob('*.lean')):
        text=path.read_text()
        header=re.match(r'\s*/-\s*(.*?)\s*-/',text,re.S)
        header=header.group(1) if header else ''
        claim_header=re.search(r'^Claims?:\s*(.*)$',header,re.M)
        scope=re.search(r'^Scope:\s*(.*?)(?=\n[A-Z][A-Za-z ]*:|\Z)',header,re.M|re.S)
        files.append({'path':str(path.relative_to(ROOT)),
                      'sha256':hashlib.sha256(text.encode()).hexdigest(),
                      'indexed_claims':mapped.get(path.resolve(),[]),
                      'claim_header':claim_header.group(1) if claim_header else None,
                      'scope_header':scope.group(1).strip() if scope else None,
                      'header':header,
                      'imports':re.findall(r'^import\s+(\S+)',text,re.M),
                      'declaration_names':re.findall(r'^\s*(?:noncomputable\s+)?(?:theorem|lemma|def|abbrev|structure|class)\s+([^\s({:]+)',text,re.M)})
write_json(args.out,{'claims_with_lean_links':len(claim_rows),'files':files,'claims':claim_rows,
                     'unmapped_files':[f['path'] for f in files if not f['indexed_claims']],
                     'scope':'Existing source inventory only; no compilation or completeness inference.'})
print(f'{len(files)} Lean files; {len(claim_rows)} linked claims; {sum(not f["indexed_claims"] for f in files)} files without an index link.')
for f in files:
    print(f['path']+'\t'+','.join(f['indexed_claims'])+'\t'+str(f['scope_header'] or 'NO SCOPE HEADER'))
