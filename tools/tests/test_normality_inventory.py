import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normality_inventory import inventory, summary_hash, markdown


class NormalityInventoryTest(unittest.TestCase):
    def setUp(self):
        self.claims = {'claims': [dict(id='thm:base', summary='Explicit all-degree base range',
                                      record='[Proof](proof)', mathematical_status='working_proof'),
                                 dict(id='cor:partial', summary='Specified degrees only',
                                      record='[Partial](partial)', mathematical_status='working_proof')]}
        self.spec = dict(version=1, n_max=10, p_max=97,
                         complete_empty=[dict(claim='thm:base', dimension_min=1, dimension_max=8,
                                              summary_sha256=summary_hash(self.claims['claims'][0]))],
                         partial=[dict(claim='cor:partial', n=9, p=3,
                                       summary_sha256=summary_hash(self.claims['claims'][1]),
                                       normal_degrees={'intervals': [[2, 6]]})])

    def test_partial_and_unexamined_pairs_are_not_empty_sets(self):
        result = inventory(self.claims, self.spec, 10, 97)
        self.assertEqual((len(result['pairs']), result['complete_pairs'], result['unresolved_pairs']),
                         (240, 192, 48))
        for row in result['pairs']:
            if row['n'] <= 8:
                self.assertEqual(row['exception_set'], [])
            else:
                self.assertIsNone(row['exception_set'])
                self.assertEqual(row['status'], 'unresolved')
        partial = next(r for r in result['pairs'] if (r['n'],r['p']) == (9,3))
        self.assertEqual(partial['certified_normal_degrees'], [{'intervals': [[2,6]]}])
        self.assertIn('not', markdown(result))

    def test_changed_or_withdrawn_proof_fails_closed(self):
        for field,value in [('summary','Stronger hypotheses now required'),
                            ('mathematical_status','refuted')]:
            altered = copy.deepcopy(self.claims)
            altered['claims'][0][field] = value
            with self.assertRaisesRegex(ValueError, 're-review scope'):
                inventory(altered, self.spec, 10, 97)

    def test_reduced_bounds_and_scope_guard(self):
        result = inventory(self.claims, self.spec, 9, 7)
        self.assertEqual(result['odd_primes'], [3,5,7])
        self.assertEqual((result['complete_pairs'],result['unresolved_pairs']), (24,3))
        for n,p in [(11,97),(10,101),(0,7),(9,2)]:
            with self.assertRaises(ValueError): inventory(self.claims,self.spec,n,p)
