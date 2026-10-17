"""Count sentences of Process assessment and Prevention paragraphs that hold a figure and no research/ path.

No statement tested: a partial check for the queued build count-beside-output, measuring how many such sentences the
record holds before a finisher check is written, so its refusals can be judged against them.
"""
import glob
import html
import re

FIGURE = re.compile(r'\b\d{2,}\b')
total = bare = 0
for path in sorted(glob.glob('research/branches/*/notebook.html')):
    body = open(path).read()
    for para in re.findall(r'<p><strong>Process assessment\.</strong>(.*?)</p>', body, re.S):
        plain = html.unescape(re.sub('<[^>]+>', ' ', para))
        for s in re.split(r'(?<=[.;])\s+', plain):
            if FIGURE.search(re.sub(r'\d{1,2} October 2026|\\\(.*?\\\)', '', s)):
                total += 1
                if 'research/' not in s:
                    bare += 1
print(f'{total} figure sentences in Process assessment paragraphs; {bare} without a research/ path beside them')
