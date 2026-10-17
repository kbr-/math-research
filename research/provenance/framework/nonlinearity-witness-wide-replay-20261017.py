"""No statement tested: replay of a proposed notebook-append check over every article of every notebook: sentences
saying a rule or flow is nonlinear (not linear) in the counts, and whether the same sentence gives an additivity
witness (additivity, a sum of inputs, superposition)."""
import glob
import re
CLAIM = re.compile(r'\b(?:nonlinear|non-linear|not linear) in the counts\b', re.I)
WITNESS = re.compile(r'additiv|their sum|the sum of|superposition|sum of the inputs|\bsum\b.{0,40}\bgives?\b', re.I)
books = ['notebook.html'] + sorted(glob.glob('research/branches/*/notebook.html'))
tot = bare = 0
for b in books:
    t = open(b, encoding='utf-8').read()
    for m in re.finditer(r'<article id="([^"]+)".*?</article>', t, re.S):
        text = re.sub(r'<[^>]+>', ' ', m.group(0))
        for s in re.split(r'(?<=[.;])\s+', ' '.join(text.split())):
            if CLAIM.search(s):
                tot += 1
                if not WITNESS.search(s):
                    bare += 1
                    print('-', m.group(1), '|', s[:240])
print(f'Replay, 17 October 2026: {tot} sentences say nonlinear in the counts; {bare} give no additivity witness.')
