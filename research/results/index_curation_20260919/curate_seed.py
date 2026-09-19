#!/usr/bin/env python3
"""Apply the first manually source-reviewed curation batch; no proof execution."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from claim_registry import load, write_json, validate, REGISTRY
from claim_reviews import make_review, Evidence

REVISION = 'c289a353136c262e04fe754846ef063144f9acf9'
DATE = '2026-09-19'
WEB = 'https://kbr.is-a.dev/math-research/#'
data = load()
assert data['schema_version'] == 2
claims = {c['id']: c for c in data['claims']}
topics = [
    ('ens', 'ENS approximation', 'Extension blocks, products, coefficients and source interfaces.'),
    ('degree-accounting', 'Degree accounting', 'Original polynomial degrees, budgets and degree discrepancies.'),
    ('bit-php', 'Bit pigeonhole principle', 'Bit encodings, their transfers and proof bounds.'),
    ('resolution-parities', 'Resolution over parities', 'Affine/parity clause calculi and proof size.'),
    ('publication', 'Publication results', 'Statements prepared for independent dissemination and review.')]
existing = {t['id'] for t in data['topic_definitions']}
for key, title, description in topics:
    if key not in existing:
        data['topic_definitions'].append(dict(id=key, title=title, description=description))

specs = {
 'lem:mp-telescoping': {
  'mathematical_status': 'working_proof', 'topics': ['ens', 'degree-accounting'],
  'formalization': {
   'status': 'partial',
   'scope': 'Identity and ordinary product/coefficient/companion upper bounds verified. The original loose-bound exact companion-degree equality is refuted, not verified; downstream audit remains bounded.',
   'references': ['../formalization/claims/MpTelescoping.lean', WEB+'entry-2026-09-14-lean-mp-telescoping'],
   'artifacts': [
    {'scope': 'Finite-product telescoping identity and joint degree upper bounds, including zero accuracy and empty inputs.',
     'status': 'complete', 'references': ['../formalization/claims/MpTelescoping.lean'],
     'declarations': ['MathResearch.mp_telescoping', 'MathResearch.mp_coefficient_degree', 'MathResearch.mp_companion_degree'],
     'verification': 'results/lean_mp_telescoping_20260914_02/verification-final.txt'},
    {'scope': 'Counterexample to exact companion-degree equality for a loose ceiling, over every nontrivial commutative coefficient ring.',
     'status': 'counterexample', 'references': ['../formalization/claims/MpTelescoping.lean'],
     'declarations': ['MathResearch.mp_companion_equality_counterexample'],
     'verification': 'results/lean_mp_telescoping_20260914_02/verification-final.txt'}]},
  'significance': {'category': 'general_tool', 'rationale': 'A reusable source identity with precise degree conventions; its formal audit exposes a scope error that matters to downstream uses.',
    'novelty': 'not_claimed', 'publication_status': 'not_applicable',
    'references': [WEB+'entry-2026-09-14-lean-mp-telescoping'], 'next_action': None},
  'evidence': [WEB+'entry-2026-09-14-lean-mp-telescoping', '../formalization/claims/MpTelescoping.lean',
               'results/lean_mp_telescoping_20260914_02/verification-final.txt']},
 'thm:publication-Res-parity-bit-PHP': {
  'mathematical_status': 'established', 'topics': ['bit-php', 'resolution-parities', 'publication'],
  'formalization': {'status': 'complete',
   'scope': 'Usual-CNF bit-PHP superpolynomial node lower bound for every real exponent eventually in bit length, with both recorded affine-DAG rule conventions, actual initials and empty conclusion, no height bound.',
   'references': ['../formalization/claims/BitPHPSuperpolynomial.lean', WEB+'lean-publication-bit-PHP-superpolynomial'],
   'artifacts': [{'scope': 'Complete indexed superpolynomial theorem and transitive proof chain.',
    'status': 'complete', 'references': ['../formalization/claims/BitPHPSuperpolynomial.lean'],
    'declarations': ['MathResearch.bitPHP_superpolynomial'],
    'verification': 'results/r25_publication_20260915/verification-final.txt'}]},
  'significance': {'category': 'independent_result',
   'rationale': 'Publication-side lower bound for unrestricted Res(parity) bit PHP; the recorded focused literature audit identifies an open benchmark. Distinct from the main Frege goal.',
   'novelty': 'candidate', 'publication_status': 'preprint',
   'references': [WEB+'bit-PHP-publication-audit-verdict', WEB+'entry-2026-09-19-preprint-revision-2'],
   'next_action': 'Obtain independent expert review and resolve novelty against the exact literature scope; this curation does not perform a new literature search.'},
  'evidence': [WEB+'lean-publication-bit-PHP-superpolynomial', '../formalization/claims/BitPHPSuperpolynomial.lean',
               'results/r25_publication_20260915/verification-final.txt', WEB+'bit-PHP-publication-audit-verdict', WEB+'entry-2026-09-19-preprint-revision-2']},
 'cor:bit-PHP-exponential-parameter-bound': {
  'mathematical_status': 'established', 'topics': ['bit-php', 'resolution-parities', 'publication'],
  'formalization': {'status': 'complete',
   'scope': 'For every bit length ell >= 32, usual-CNF bit-PHP affine-DAG refutations need more than exp(2^ell/(32768 ell^2)) nodes, and the stated base-two consequence, under both recorded conventions.',
   'references': ['../formalization/claims/BitPHPExponential.lean', WEB+'entry-2026-09-17-lean-bit-PHP-exponential'],
   'artifacts': [{'scope': 'Complete exponential bound with explicit threshold 32 and base-two corollary.',
    'status': 'complete', 'references': ['../formalization/claims/BitPHPExponential.lean'],
    'declarations': ['MathResearch.bitPHP_exponential_room', 'MathResearch.bitPHP_exponential', 'MathResearch.bitPHP_exponential_base_two'],
    'verification': 'results/lean_bitphp_exponential_20260917/lean-verification.txt'}]},
  'significance': {'category': 'independent_result',
   'rationale': 'Quantitative publication headline strengthening the earlier superpolynomial conclusion via the same finite exclusion and clause-transfer mechanism, not independent confirmation of that mechanism.',
   'novelty': 'candidate', 'publication_status': 'preprint',
   'references': [WEB+'entry-2026-09-17-lean-bit-PHP-exponential', WEB+'entry-2026-09-19-preprint-revision-2'],
   'next_action': 'External review of the common proof and quantitative publication statement remains outstanding.'},
  'evidence': [WEB+'entry-2026-09-17-lean-bit-PHP-exponential', '../formalization/claims/BitPHPExponential.lean',
               'results/lean_bitphp_exponential_20260917/lean-verification.txt', WEB+'entry-2026-09-19-preprint-revision-2']}}

parents = ['audit:ordinary-restriction-affine-family', 'thm:bit-PHP-affine-clause-PC-transfer']
edges = []
for child, anchor in [('thm:publication-Res-parity-bit-PHP', 'lean-publication-bit-PHP-superpolynomial'),
                      ('cor:bit-PHP-exponential-parameter-bound', 'lean-bit-PHP-exponential-proof')]:
    for parent in parents:
        edges.append((child, parent, 'depends_on', WEB+anchor,
                      'Direct exclusion/transfer step of the recorded full proof.'))
edges.append(('cor:bit-PHP-exponential-parameter-bound','thm:publication-Res-parity-bit-PHP','refines',
              WEB+'entry-2026-09-17-lean-bit-PHP-exponential',
              'Quantitatively stronger bound on the same calculus; not a claim that the Lean proof depends on the superpolynomial theorem.'))
for child, parent, kind, evidence, scope in edges:
    key = child+'::'+kind+'::'+parent
    edge = {'id':key,'source':{'namespace':'current','id':child,'locator':None},
            'target':{'namespace':'current','id':parent,'locator':None},'type':kind,
            'evidence':[evidence],'review_status':'reviewed','scope':scope,
            'review':{'revision':REVISION,'date':DATE,'reviewer':'Codex GPT-6 Astra',
                      'note':'Read the recorded proof and corresponding Lean imports/declarations; no fresh kernel replay.'}}
    prior = next((e for e in data['relationships'] if e['id']==key),None)
    if prior is None: data['relationships'].append(edge)
    else: assert prior == edge

evidence = Evidence()
for label, spec in specs.items():
    claim=claims[label]
    for field in ('mathematical_status','formalization','topics','significance'):
        claim[field]=spec[field]
    for field in ('mathematical_status','formalization','topics','significance','relationships'):
        note='Source-reviewed metadata only; original summary and assessment retained, no new proof or kernel replay.'
        if label=='lem:mp-telescoping' and field=='relationships':
            note='Recorded Lean proof imports Mathlib directly and names no other continued-research theorem as a mathematical prerequisite. Library internals are outside the claim-level edge scope.'
        claim['reviews'][field]=make_review(data,claim,field,spec['evidence'],revision=REVISION,
            date=DATE,note=note,reviewer='Codex GPT-6 Astra',evidence=evidence)
validate(data)
write_json(REGISTRY,data)
print('Curated 3 claims across 5 fields; recorded 5 evidence-backed relationships and 5 initial topics.')
