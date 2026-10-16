"""No statement tested: do registry neighbours of the claims an entry cites reach the claims it missed?"""
import importlib.util, sys, re, collections, html, subprocess
from pathlib import Path
sys.path.insert(0, 'tools')
spec = importlib.util.spec_from_file_location('sc', 'tools/search-claims.py'); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
spec = importlib.util.spec_from_file_location('ft', 'tools/finish-turn.py'); ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
data = sc.read_json(sc.REGISTRY)
r0 = data['relationships'][0]; print({k: (v if k != 'source' else v) for k, v in r0.items() if k in ('type', 'kind', 'target', 'relation')})
rel = collections.defaultdict(set)
for r in data['relationships']:
    s = r['source']['id']; t = r['target']['id'] if isinstance(r['target'], dict) else r['target']
    rel[s].add(t); rel[t].add(s)
by_record = collections.defaultdict(set)
for c in data['claims']:
    by_record[re.sub(r'^\[.*?\]\(|\)$', '', c['record'] or '')].add(c['id'])
rec_of = {c['id']: re.sub(r'^\[.*?\]\(|\)$', '', c['record'] or '') for c in data['claims']}
def neighbours(cited):
    out = set()
    for c in cited:
        out |= rel.get(c, set()); out |= by_record.get(rec_of.get(c, ''), set())
    return out - set(cited)
# the spread defect entry as committed (before it named its next attempt the record-search missed)
body = subprocess.run(['git', 'show', '85aa78616:notebook.html'], capture_output=True, text=True).stdout
at = body.index('<article id="entry-2026-10-16-spread-defect-cover"'); entry = body[at:body.index('</article>', at)]
plain = html.unescape(ft.strip_tags(entry)); cited = set(ft.CLAIM_ID_RE.findall(plain))
nb = neighbours(cited)
print('spread: cited', len(cited), 'neighbours', len(nb), 'weighted-chain-cells in', 'lem:weighted-chain-cells' in nb)
# second-order: neighbours of claims cited in its Follow-up only
follow = html.unescape(ft.strip_tags(ft.report_paragraph(entry + '</article>', 'Follow-up'))); fc = set(ft.CLAIM_ID_RE.findall(follow))
print('follow cited', fc, 'neighbours', len(neighbours(fc)), 'lem:weighted-chain-cells' in neighbours(fc))
# matched image review, decisive test cited claims (original as committed)
body2 = subprocess.run(['git', 'show', '33696f91a:notebook.html'], capture_output=True, text=True).stdout
at = body2.index('<article id="entry-2026-10-16-matched-image-goal-review"'); e2 = body2[at:body2.index('</article>', at)]
dt = html.unescape(ft.strip_tags(ft.report_paragraph(e2 + '</article>', 'Decisive test'))); dc = set(ft.CLAIM_ID_RE.findall(dt))
n2 = neighbours(dc); print('review test cited', dc, 'neighbours', len(n2), 'flat-removal in', 'cor:growing-expansion-flat-removal' in n2)
def two_hop(cited):
    first = neighbours(cited)
    return (first | neighbours(first)) - set(cited)
docs = {c['id']: set(sc.stems(c['id'] + ' ' + c['summary'])) for c in data['claims']}
def ranked(pool, text):
    q = set(sc.stems(re.sub(r'\\\(.*?\\\)', ' ', text)))
    return sorted(pool, key=lambda c: -len(q & docs.get(c, set())))
na = ft.planned_test_texts(entry)
for label, cited_set, want, text in (('spread follow', fc, 'lem:weighted-chain-cells', follow),
                                       ('review test', dc, 'cor:growing-expansion-flat-removal', dt)):
    pool = two_hop(cited_set); order = ranked(pool, text)
    print(label, 'two-hop pool', len(pool), want, 'rank', order.index(want) + 1 if want in order else None)
