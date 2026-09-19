#!/usr/bin/env python3
"""Compare restoration outputs against a pinned Git revision, without copying snapshots."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from notebook_context import budgets,excerpt

BASE='33047a41d10f2c1f01735ffbb23320293cc183ad'
FILES=['AGENTS.md','COMPUTATION_RULES.md','research/AGENTS.md','research/notes/RESUME.md']

def at_base(path):
    return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)

def metrics(text):
    return {'utf8_bytes':len(text.encode()),'whitespace_words':len(text.split()),
            'sha256':hashlib.sha256(text.encode()).hexdigest()}

def current(source):
    return source[:excerpt.Notebook(source).anchor('research-record')['start']].rstrip()+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    old=at_base('notebook.html');new=(ROOT/'notebook.html').read_text()
    config=json.loads((ROOT/'research/context-budgets.json').read_text())
    old_current,new_current=current(old),current(new)
    before={p:metrics(at_base(p)) for p in FILES};after={p:metrics((ROOT/p).read_text()) for p in FILES}
    before['notebook --current']=metrics(old_current);after['notebook --current']=metrics(new_current)
    # Reproduce the previous bounded grep output, not its unbounded variant.
    import re
    old_toc='\n'.join(f'{i}:{line}' for i,line in enumerate(old.splitlines(),1)
                      if re.search(r'<article|<h3>|class="entry-meta"',line))
    old_toc='\n'.join(old_toc.splitlines()[-30:])+'\n'
    new_toc,_=excerpt.Notebook(new).toc()
    before['title scan']=metrics(old_toc);after['title scan']=metrics(new_toc)
    # Record actual bounded retrieval sizes and IDs, not duplicate source outputs.
    labels=['lem:mp-telescoping','thm:publication-Res-parity-bit-PHP','audit:permutation-NA-source-error']
    lookups=[]
    for label in labels:
        command=[sys.executable,'tools/search-claims.py','--show',label]
        result=subprocess.check_output(command,cwd=ROOT,text=True)
        lookups.append({'command':command[1:],'output':metrics(result)})
    # Paused-task recovery audit: these exact links and distinguishing conditions
    # must remain in the overview. Full statements/proofs are still read by anchor.
    cases={
      'source_module_review': {'anchors':['full-costed-source-coupled-marginals','active-window-old-extension-reduction','bit-affine-coherent-band-extension','faithful-pair-NS-PC-transfer','flat-module-four-h-rank-corollary'], 'phrases':['3h&lt;D\\le4h','E=D-L','general-step']},
      'profile_endpoint': {'anchors':['accuracy-dependent-affine-exclusion','costed-ns-value-profile','source-profile-rank-inflation'], 'phrases':['h=3\\ell','n\\ge2B_*-1','D_*=c_{\\rm fr}']},
      'probability_repair': {'anchors':['entry-2026-09-19-permutation-probability-audit'], 'phrases':['replacement probability','does not refute all stronger']},
      'formalization_gap': {'anchors':['entry-2026-09-14-lean-mp-telescoping','entry-2026-09-14-bounded-companion-degree-audit'], 'phrases':['loose input-degree ceiling','downstream audit remains partial']},
      'publication_scope': {'anchors':['lean-publication-bit-PHP-superpolynomial','lean-bit-PHP-exponential'], 'phrases':['both recorded rule conventions','\\ell\\ge32','awaits external review']},
      'parked_routes': {'anchors':['route-review-conjecture','parity-concentration-decision','parity-two-obstruction'], 'phrases':['relative rank count','parked']}}
    ids=set(re.findall(r'\bid="([^"]+)"',new))
    for case in cases.values():
        case['passed']=all(f'href="#{a}"' in new_current and a in ids for a in case['anchors']) and all(p in new_current for p in case['phrases'])
        assert case['passed'],case
    links=re.findall(r'href="#([^"]+)"',new_current)
    assert all(a in ids for a in links),'Broken living-section link'
    # The old record is preserved byte-for-byte as a prefix before any new entry.
    old_record=old[old.index('<section id="research-record">'):old.rfind('</section>')].rstrip()
    new_record=new[new.index('<section id="research-record">'):]
    assert new_record.startswith(old_record),'Historical record changed'
    totals={name:sum(item['utf8_bytes'] for item in rows.values()) for name,rows in [('before',before),('after',after)]}
    report={'baseline_revision':BASE,'before':before,'after':after,'total_restoration_bytes':totals,
            'reduction_percent':round(100*(1-totals['after']/totals['before']),2),
            'budgets_before':budgets(old,config),'budgets_after':budgets(new,config),
            'representative_lookup_outputs':lookups,'recovery_cases':cases,
            'historical_record_preserved':True,'living_links_checked':len(links),
            'scope':'Actual selected-file/command output sizes, not model token accounting. Harness prompts, optional agent-specific instructions and follow-up proof reads are excluded. No tokenizer or token estimate claimed.'}
    with args.out.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'bytes':totals,'reduction_percent':report['reduction_percent'],'recovery_cases':len(cases),'budget_passed':report['budgets_after']['passed']},indent=2))

if __name__=='__main__':main()
