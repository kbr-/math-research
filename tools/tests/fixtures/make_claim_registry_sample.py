"""Write fixed shape and search fixtures from the live registry (run from the repository root).

The sample holds the registry's first three claims, the relationships among them, and its other top-level keys,
small ones in full and large lists cut to their first five entries, so test_claim_shape compares the compiled and
interpreted shape checkers on the same input on every branch, whatever its registry holds (softeng's has none).
The search sample keeps the leading competitors for the two retrieval regressions,
using only the fields scored by search; unit tests must not parse the growing corpus.
Usage: python3 tools/tests/fixtures/make_claim_registry_sample.py"""
import importlib.util
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path('tools').resolve()))

registry = json.loads(Path('research/claims/index.json').read_text())
claims = registry['claims'][:3]
ids = {c['id'] for c in claims}
sample = dict(registry, claims=claims,
              relationships=[r for r in registry['relationships']
                             if r['source'].get('id') in ids and r['target'].get('id') in ids],
              dependency_decisions=registry.get('dependency_decisions', [])[:5])
out = Path('tools/tests/fixtures/claim-registry-sample.json')
out.write_text(json.dumps(sample, ensure_ascii=False, indent=1) + '\n')
print(out, len(out.read_text()), 'bytes;', [c['id'] for c in claims], len(sample['relationships']), 'relationships')

spec = importlib.util.spec_from_file_location('fixture_claim_search', 'tools/search-claims.py')
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)
queries = [('point support lower bound', 'lem:Boolean-design-point-support-lower-bound'),
           ('two form no fall criterion', 'thm:two-form-no-fall-criterion')]
selected = set()
for query, expected in queries:
    hits = search.search(registry, query.split())[:12]
    assert expected in {c['id'] for _, c in hits}, (query, expected)
    selected.update(c['id'] for _, c in hits)
sample = {'claims': [{key: c[key] for key in ('id', 'summary', 'assessment')}
                     for c in registry['claims'] if c['id'] in selected]}
for query, expected in queries:
    assert expected in {c['id'] for _, c in search.search(sample, query.split())[:5]}
out = Path('tools/tests/fixtures/claim-search-sample.json')
out.write_text(json.dumps(sample, ensure_ascii=False, indent=1) + '\n')
print(out, len(out.read_text()), 'bytes;', len(sample['claims']), 'search competitors')
