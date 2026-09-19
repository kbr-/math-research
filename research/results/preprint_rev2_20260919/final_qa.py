#!/usr/bin/env python3
"""Capture final PDF metadata, build logs, and source fingerprints."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
p=Path('publications/bit-php-resolution-over-parities')
out=Path('research/results/preprint_rev2_20260919')
log=(p/'whitepaper.log').read_text()
assert not re.search(r'Warning|Overfull|Underfull|Undefined control|Fatal error',log)
for name in ['whitepaper.log','pdflatex-pass-.log']:
 shutil.copyfile(p/name,out/(name+'.txt'))
info=subprocess.check_output(['pdfinfo',str(p/'whitepaper.pdf')],text=True)
(out/'pdfinfo.txt').write_text(info)
assert re.search(r'Pages:\s+37\b',info)
text=subprocess.check_output(['pdftotext','-layout',str(p/'whitepaper.pdf'),'-'],text=True)
assert 'revision 2' in text and '19 September 2026' in text
assert '??' not in text
assert '8904bf09a5376f48a00d1c25d079bf0c6441502a' in text
assert 'A pinned checkout and verification commands' in text
files=sorted(p.glob('*.tex'))+sorted((p/'sections').glob('*.tex'))+[p/'whitepaper.pdf']
report={'review_date':'2026-09-19','revision':2,
 'base_commit':'952844a393b5eed56e82a53465e69d89cf8e995c',
 'formalization_commit':'8904bf09a5376f48a00d1c25d079bf0c6441502a',
 'note':'Final revision-2 TeX/PDF snapshot after clean three-pass LaTeX build and internal visual review. Unchanged theorem sources; prior kernel evidence reused. No new Lean replay or submission package.',
 'files':[{'path':str(f.relative_to(p)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
(p/'reviewed-files.json').write_text(json.dumps(report,indent=2)+'\n')
qa={'status':'PASS','pages':37,'latex_warnings':0,'overfull_underfull_boxes':0,
 'revision_and_date_present':True,'no_unresolved_reference_markers':True,
 'aggregate_commit_in_pdf':True,'visual_review':'Whole-document contact sheets; enlarged parameter/verification pages; corrected final contents, parameter, and verification pages inspected.',
 'scope':'PDF/source editorial QA, not Lean kernel verification.'}
(out/'pdf-qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa,indent=2))
