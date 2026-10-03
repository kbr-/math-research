"""Write tools/tests/fixtures/claim-registry-sample.json from the live registry (run from the repository root).

The sample holds the registry's first three claims, the relationships among them, and its other top-level keys,
small ones in full and large lists cut to their first five entries, so test_claim_shape compares the compiled and
interpreted shape checkers on the same input on every branch, whatever its registry holds (softeng's has none).
Usage: python3 tools/tests/fixtures/make_claim_registry_sample.py"""
import json
from pathlib import Path

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
