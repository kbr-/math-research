"""Audit queue migration against the inventoried commit and current notebook files.

No statement tested: this is framework data-integrity verification, not mathematics.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import framework_queue as fq
import lead_queue as q
from notebooks import catalogue

spec = json.loads(Path(__file__).with_name('migration.json').read_text())
requested = {(r['notebook'], r['qualified_id']) for r in spec['items']}
central_body = (ROOT / 'notebook.html').read_text()
central = {fq.key(n): n for n in fq.parse(central_body)}
assert len(central) == len(requested)
outside = re.compile(r'<section id="(?:lead|framework)-queue"[^>]*>.*?</section>\s*', re.S)
rows = []
total_math = 0
for name, meta in catalogue(ROOT).items():
    path = ROOT / meta['source']
    old = subprocess.check_output(['git', 'show', spec['source_commit'] + ':' + meta['source']], cwd=ROOT, text=True)
    new = path.read_text()
    assert outside.sub('', old) == outside.sub('', new), ('outside queues changed', name)
    before, after = q.parse_tree(old), q.parse_tree(new)
    if not before:
        assert after is None
        rows.append(dict(notebook=name, moved=0, mathematical=0))
        continue
    expected = []
    moved = 0
    for top in before[1]:
        keep = top.copy()
        keep.children = []
        for node in [top, *top.children]:
            if (name, q.qualified(node)) in requested:
                exact = fq.transferred(node, name, meta['source'], q.qualified(top) if node is not top else None)
                saved = central[fq.key(exact)]
                assert (saved.text, saved.attrs) == (exact.text, exact.attrs), ('payload changed', fq.key(exact))
                moved += 1
            elif node is not top:
                keep.children.append(node)
        expected.extend(keep.children if (name, q.qualified(top)) in requested else [keep])
    assert q.render_nodes(expected) == q.render_nodes(after[1]), ('math queue changed', name)
    assert not fq.SECTION.search(new) or name == 'main'
    q.check(old, new, path, ROOT, central_body)
    remaining = len(q.every_item(after[1]))
    total_math += remaining
    rows.append(dict(notebook=name, moved=moved, mathematical=remaining))
report = dict(framework=len(central), mathematical=total_math, total=len(central)+total_math,
              notebooks=rows, checks='Exact framework payloads and provenance; exact remaining math nodes and order; '
              'outside-queue content unchanged; single main ownership; queue transition checks passed.')
out = Path(__file__).with_name('audit.json')
out.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
