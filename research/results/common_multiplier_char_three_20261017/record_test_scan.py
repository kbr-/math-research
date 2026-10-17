"""List the record's paragraphs and sentences that offer recorded figures as a test of a claim.

No statement tested: a partial check for the queued build record-test-scope, listing each sentence holding
"against the record" or "as (a) requires"-style test wording, with its notebook and entry, so the forms the build
must read are counted before it is written.
"""
import glob
import html
import re

PATTERN = re.compile(r'against the record|tests? (?:the|this) (?:corollary|proposition|statement)|as \(\w\) requires',
                     re.I)
total = 0
for path in sorted(glob.glob('research/branches/*/notebook.html') + ['notebook.html']):
    body = open(path).read()
    for m in re.finditer(r'<article id="(entry-[^"]+)"', body):
        text = body[m.start():body.find('</article>', m.start())]
        plain = html.unescape(re.sub('<[^>]+>', ' ', text))
        for s in re.split(r'(?<=[.;])\s+', plain):
            if PATTERN.search(s):
                total += 1
                print(f'{path} {m.group(1)}: {" ".join(s.split())[:160]}')
print(f'{total} sentences')
