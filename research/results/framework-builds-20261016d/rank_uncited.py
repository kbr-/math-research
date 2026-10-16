"""No statement tested: where the motivating claims rank, and the cost of each search stage."""
import importlib.util, sys, time, math, collections
from pathlib import Path
sys.path.insert(0, 'tools')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
ft = load('ft', 'tools/finish-turn.py'); sc = load('sc', 'tools/search-claims.py')
t = time.monotonic(); data = sc.read_json(sc.REGISTRY); print(f'read {time.monotonic()-t:.2f} s')
t = time.monotonic(); toks = [sc.stems(c['id'] + ' ' + c['summary'] + ' ' + c['assessment']) for c in data['claims']]; print(f'stems {time.monotonic()-t:.2f} s')
body = Path('notebook.html').read_text()
at = body.index('<article id="entry-2026-10-16-matched-image-goal-review"'); entry = body[at:body.index('</article>', at)]
(label, text), = ft.planned_test_texts(entry)
print(label, len(text.split()), 'words:', text[:300])
q = sc.stems(text); print('query stems', len(q))
t = time.monotonic(); res = sc.search(data, [text]); print(f'search {time.monotonic()-t:.2f} s')
ids = [c['id'] for _, c in res]
for want in ('cor:growing-expansion-flat-removal', 'thm:growing-rank-gap-exclusion'):
    print(want, 'rank', ids.index(want) + 1 if want in ids else None, 'of', len(ids))
# exact-stem inverted index with idf
t = time.monotonic()
index = collections.defaultdict(set)
for i, s in enumerate(toks):
    for w in s: index[w].add(i)
n = len(toks); score = collections.Counter()
for w in set(q):
    for i in index.get(w, ()): score[i] += math.log((n + 1) / (len(index[w]) + 1))
order = [data['claims'][i]['id'] for i, _ in score.most_common()]
print(f'exact index {time.monotonic()-t:.2f} s')
for want in ('cor:growing-expansion-flat-removal', 'thm:growing-rank-gap-exclusion'):
    print(want, 'exact rank', order.index(want) + 1 if want in order else None)
