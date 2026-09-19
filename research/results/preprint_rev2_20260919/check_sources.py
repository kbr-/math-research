#!/usr/bin/env python3
"""Focused static correspondence check for the revision-2 editorial changes."""
import json
from pathlib import Path
import re
import subprocess

paper = Path('publications/bit-php-resolution-over-parities')
pin = '8904bf09a5376f48a00d1c25d079bf0c6441502a'
files = sorted(paper.glob('*.tex')) + sorted((paper/'sections').glob('*.tex'))
text = '\n'.join(p.read_text() for p in files)
labels = re.findall(r'\\label\{([^}]+)\}', text)
assert len(labels) == len(set(labels)), 'duplicate LaTeX labels'
refs = set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text))
assert refs <= set(labels), sorted(refs-set(labels))
bib = set(re.findall(r'\\bibitem(?:\[[^]]+\])?\{([^}]+)\}', text))
cites = {key for group in re.findall(r'\\cite\{([^}]+)\}', text) for key in group.split(',')}
assert cites <= bib, sorted(cites-bib)
linked = set(re.findall(r'\\(?:lean|leanref)\{([^}]+\.lean)\}', text))
source = {}
for path in sorted(linked):
 source[path] = subprocess.check_output(['git','show',f'{pin}:formalization/{path}'], text=True)
verification = (paper/'sections/09-verification.tex').read_text()
rows = re.findall(r'\\leanref\{([^}]+)\}.*?\\newline\s*(.*?)(?=\\\\)', verification, re.S)
entries = []
for path, names in rows:
 for name in re.findall(r'\\nolinkurl\{([^}]+)\}', names):
  full = ('MathResearch.PolynomialCalculus.'+name[3:] if name.startswith('PC.') else
          'MathResearch.ThirdParty.'+name[3:] if name.startswith('TP.') else 'MathResearch.'+name)
  header = source[path].split('-/',1)[0]
  assert full in re.search(r'^Declarations: (.*)$', header, re.M).group(1).split(), (path,full)
  entries.append({'file':path,'declaration':full})
assert len(entries) == 15, len(entries)
for path in ['formalization/claims/BitPHPPreprintRevision1.lean','formalization/verify.py',
             'formalization/lean-toolchain','formalization/lakefile.lean','formalization/lake-manifest.json']:
 subprocess.check_output(['git','cat-file','-e',f'{pin}:{path}'])
changed = subprocess.check_output(['git','diff','--name-only','b47e9b1',pin,'--',
 'formalization/claims','formalization/third-party-claims'],text=True).splitlines()
assert changed == ['formalization/claims/BitPHPPreprintRevision1.lean'], changed
assert pin in (paper/'whitepaper.tex').read_text()
report={'status':'PASS','pin':pin,'labels':len(labels),'citations':len(cites),
        'pinned_Lean_files':len(linked),'verification_map':entries,
        'only_claim_directory_change_from_prior_pin':changed,
        'scope':'Static labels, citations, pinned file/declaration existence and pin diff; not a Lean replay.'}
out=Path('research/results/preprint_rev2_20260919/source-check.json')
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
